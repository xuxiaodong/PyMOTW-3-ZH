import configparser
import http.server
import os
import subprocess

from paver.easy import options, Bunch, task, consume_args, sh, info, error, cmdopts, dry
from paver.path import path
from paver.setuputils import setup

import pyquery

from sphinxcontrib import paverutils  # noqa
from sphinxcontrib.paverutils import cog, run_script

import wordpress_xmlrpc
import wordpress_xmlrpc.exceptions


# Set PYTHONHASHSEED so ensure the "randomness" for mapping-related
# items is always the same between runs to avoid unnecessary cog
# updates.
os.environ['PYTHONHASHSEED'] = '19710329'


setup(
    name="PyMOTW-3",
    packages=[],
    version="0.0",
    url="https://pymotw.com/3/",
    author="Doug Hellmann",
    author_email="doug@doughellmann.com"
)

options(

    sphinx=Bunch(
        docroot='.',
        builddir='build',
        sourcedir='source',
        warnerror=True,
    ),

    spelling=Bunch(
        builder='spelling',
    ),

    # Some of the files include [[[ as part of a nested list data
    # structure, so change the tags cog looks for to something
    # less likely to appear.
    cog=Bunch(
        beginspec='{{{cog',
        endspec='}}}',
        endoutput='{{{end}}}',
    ),

    pdf=Bunch(
        builder='latex',
        docroot='.',
        builddir='build',
        sourcedir='source',
    ),

    website=Bunch(
        # What server hosts the website?
        server='pymotw.com',
        server_path='/home/douhel3shell/pymotw.com/3/',
    ),

    testsite=Bunch(
        # Where do we put the files for local testing?
        local_path='/Users/dhellmann/Sites/pymotw.com/3',
    ),

    sitemap_gen=Bunch(
        # Where is the config file for sitemap_gen.py?
        config='sitemap_gen_config.xml',
    ),

    migrate=Bunch(
        old_loc='../../Python2/book-git/PyMOTW/',
    ),

    blog=Bunch(
        outdir='blog_posts',
        in_file='index.html',
        out_file='blog.html',
        no_edit=False,
        url_base='https://pymotw.com/3/',
    ),

)


# Replace run_script with local wrapper
def run_script(input_file, script_name, break_lines_at=64, **kwds):
    return paverutils.run_script(input_file, script_name,
                                 break_lines_at=break_lines_at,
                                 **kwds)

# Stuff commonly used symbols into the builtins so we don't have to
# import them in all of the cog blocks where we want to use them.
__builtins__['run_script'] = run_script
__builtins__['path'] = path
__builtins__['sh'] = sh


def remake_directories(*dirnames):
    """Remove the directories and recreate them.
    """
    for d in dirnames:
        d = path(d)
        if d.exists():
            d.rmtree()
        d.mkdir()
    return


@task
def clean(options):
    remake_directories(options.sphinx.builddir)


@task
def css(options):
    "Generate CSS from less"
    src_path = 'source/_themes/pymotw/static/'
    file_base = 'pymotw'
    outfile = path(src_path + file_base + '.css')
    rebuild = False
    if not outfile.exists() or path(src_path + file_base + '.less').mtime > outfile.mtime:
        rebuild = True
    elif path(src_path + 'vars.less').mtime > outfile.mtime:
        rebuild = True
    if rebuild:
        sh('lessc %(file_base)s.less > %(file_base)s.css' % {
            'file_base': src_path + file_base,
        })
        path(src_path + file_base + '.css').copy(
            options.sphinx.builddir + '/html/_static/pymotw.css')


@task
def html(options):
    "Generate HTML files."
    paverutils.html(options)
    css(options)
    return


@task
def spelling(options):
    "Check spelling."
    rc = paverutils.run_sphinx(options, 'spelling')
    if rc:
        raise ValueError('Found spelling mistake')


@task
def html_clean(options):
    """Remove sphinx output directories before building the HTML.
    """
    clean(options)
    html(options)
    return


def _get_branch_name():
    """Look at git for our branch name."""
    out = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
    )
    out = out.strip()
    return out.decode('utf-8')


def _get_module(options):
    """Return the name of module passed as arg or the default.
    """
    module = None
    args = getattr(options, 'args', [])
    if args:
        module = args[0]
        info('using argument for module: %s' % module)
    branch = _get_branch_name()
    if branch.startswith('module/'):
        module = branch.partition('/')[-1]
        info('using git branch for module: %s' % module)
    if not module:
        try:
            module = path('module').text().rstrip()
        except:
            pass
        else:
            info('read module from file: %s' % module)
    if not module:
        error('could not determine the module')
    return module


def _flake8(infile):
    """Run flake8 against the input file"""
    return sh('flake8 %s' % infile)


@task
def flake8(options):
    """Run flake8 against all of the input files"""
    options.order('flake8', 'sphinx', add_rest=True)
    module = _get_module(options)
    if module:
        module_dir = os.path.join(options.sphinx.sourcedir, module)
        _flake8(module_dir)
    else:
        _flake8(options.sphinx.sourcedir)


@task
@consume_args
def update(options):
    """Run cog against the named module, then re-build the HTML.

    Examples::

      $ paver update atexit
    """
    options.order('update', 'sphinx', add_rest=True)
    module = _get_module(options)
    module_dir = os.path.join(options.sphinx.sourcedir, module)
    if path(module_dir).isdir():
        _flake8(module_dir)
    options.order('cog', 'sphinx', add_rest=True)
    options.args = [module_dir]
    cog(options)
    html(options)
    return


# @task
# def pdf():
#     """Generate the PDF book.
#     """
#     options.order('pdf', 'sphinx', add_rest=True)
#     paverutils.pdf(options)
#     return

@task
def rsyncwebsite(options):
    # Copy to the server
    os.environ['RSYNC_RSH'] = '/usr/bin/ssh'
    src_path = path(options.sphinx.builddir) / 'html'
    sh('(cd %s; rsync --archive --delete --verbose . %s:%s)' %
        (src_path, options.website.server,
         options.website.server_path))
    return


@task
def test(options):
    # Copy to the local site
    src_path = path(options.sphinx.builddir) / 'html'
    os.chdir(src_path)
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address,
                                   http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()
    return


@task
def buildsitemap(options):
    sh('python2 ./bin/sitemap_gen.py --testing --config=%s' %
       options.sitemap_gen.config)
    return


@task
def notify_google(options):
    # Tell Google there is a new sitemap. This is sort of hacky,
    # since we regenerate the sitemap locally but Google fetches
    # the one we just copied to the remote site.
    # sh('python2 ./bin/sitemap_gen.py --config=%s'
    #    % options.sitemap_gen.config)
    return


@task
def deploy(options):
    """Rebuild and copy website files to the remote server.
    """
    # Rebuild
    html_clean(options)
    # Rebuild the site-map
    buildsitemap(options)
    # Install
    rsyncwebsite(options)
    # Update Google
    notify_google(options)
    return


@task
def push(options):
    """Push changes to remote git repository.
    """
    sh('git push')


@task
def publish(options):
    # spelling(options)
    deploy(options)
    push(options)


@task
@consume_args
def migrate(options):
    "Copy old content into place to prepare for updating"
    args = getattr(options, 'args', [])
    options.order('update', 'sphinx', add_rest=True)
    module = _get_module(options)
    # The source module name might be different from the destination
    # module name, so look for an explicit argument for the source.
    source = module
    args = getattr(options, 'args', [])
    if args:
        source = args[0]
    dest = path('source/' + module)
    if dest.exists():
        raise ValueError('%s already exists' % dest)
    path(options.migrate.old_loc + '/' + source).copytree(dest)
    (dest + '/__init__.py').remove()
    if source != module:
        # Rename any modules that have the old source module name to
        # use the new source module name.
        for srcfile in dest.glob(source + '_*.py'):
            newname = srcfile.name.replace(source + '_', module + '_')
            srcfile.rename(dest + '/' + newname)


def get_post_title(filename):
    with open(filename, 'r') as f:
        body = f.read()

    doc = pyquery.PyQuery(body)
    h1 = doc('h1')
    return h1.text


def gen_blog_post_from_page(input_file, module, url_base):
    """Generate the blog post body and title
    """
    canonical_url = url_base.rstrip('/') + '/' + module + '/'
    if not input_file.endswith("index.html"):
        canonical_url += input_base

    print('reading from {}'.format(input_file))
    raw_body = input_file.text().strip()
    doc = pyquery.PyQuery(raw_body)

    # Get the title, removing any anchors for the header in the
    # process
    title = doc('h1').remove('a').text()
    if module not in title:
        title = '{} - {}'.format(module, title)
    if 'PyMOTW 3' not in title:
        title = '{} — PyMOTW 3'.format(title)

    # Get the intro paragraph
    intro = doc('p').eq(0)

    # Convert the paragraph to simple text, removing all formatting.
    intro = intro.text().replace('\n', ' ')

    output_body = '''<p>{intro}</p>
<p><a href="{canonical_url}">Read more...</a></p>
<p><small>This post is part of the Python Module of the Week series for Python 3. See <a href="https://pymotw.com/3/">PyMOTW.com</a> for more articles from the series.</small></p>
'''.format(intro=intro, canonical_url=canonical_url)

    return (title, output_body)

def post_draft(title, body):
    cfg_filename = path('~/.wphelper').expanduser()
    cfg = configparser.ConfigParser()
    if not cfg.read(cfg_filename):
        raise RuntimeError('Did not find configuration file {}'.format(cfg_filename))
    site_url = cfg['site']['url']
    xmlrpc_url = site_url + '/xmlrpc.php'
    username = cfg['site']['username']
    password = cfg['site']['password']
    wp = wordpress_xmlrpc.Client(xmlrpc_url, username, password)
    post = wordpress_xmlrpc.WordPressPost()
    post.title = title
    post.content = body
    post.post_status = 'draft'
    post.terms_names = {
        'post_tag': ['PyMOTW', 'python'],
    }
    wp.call(wordpress_xmlrpc.methods.posts.NewPost(post))


@task
@consume_args
@cmdopts([
    ('in-file=', 'b', 'Blog input filename (e.g., "-b index.html")'),
])
def blog(options):
    """Generate the blog post version of the HTML for the current module.

    The default behavior generates the post for the current module using
    its index.html file as input.

    To use a different file within the module directory, use the
    --in-file or -b option::

      paver blog -b communication.html

    To run against a directory other than a module, use the
    -s or --sourcedir option::

      paver blog -s PyMOTW/articles -b text_processing.html
    """
    options.order('blog', 'sphinx', add_rest=True)
    module = _get_module(options)

    # Create output directory
    out = path(options.outdir)
    if not out.exists():
        out.mkdir()

    blog_file = path(options.outdir) / module + '.html'
    title, body = dry(
        'building blog post body',
        gen_blog_post_from_page,
        input_file=path(options.builddir) / 'html' / module / options.in_file,
        module=module,
        url_base=options.url_base,
    )
    print('title {!r}'.format(title))
    post_draft(title, body)
    return
