=============================
 textwrap --- 格式化文本段落 
=============================

.. module:: textwrap
    :synopsis: 格式化文本段落

:用途: 通过调整换行符在段落中出现的位置来格式化文本。

:mod:`textwrap` 模块用于将输出的文本格式化为期望的漂亮打印场合。它提供可在很多文本编辑器及文字处理器中找到的类似于换行或填充段落这样的程序功能。

样例数据
========

本节中的样例使用包含字符串 ``sample_text`` 的模块 ``textwrap_example.py`` 。

.. literalinclude:: textwrap_example.py
    :caption:
    :start-after: #end_pymotw_header


填充段落
========

:func:`fill` 函数将文本作为输入，并产生输出格式化的文本。

.. literalinclude:: textwrap_fill.py
    :caption:
    :start-after: #end_pymotw_header

结果有点小于期望。虽然文本现在左对齐，但是首行保留了缩进，而且每个序列行前面的空格都被嵌入到了段落中。

.. {{{cog
.. cog.out(run_script(cog.inFile, 'textwrap_fill.py'))
.. }}}

::

	$ python3 textwrap_fill.py
	
	No dedent:
	
	     The textwrap module can be used to format
	text for output in     situations where pretty-
	printing is desired.  It offers     programmatic
	functionality similar to the paragraph wrapping
	or filling features found in many text editors.

.. {{{end}}}


移除现有的缩进
==============

因为先前的样例嵌入了制表符和额外的空格混合到输出中间，所以格式化得很不齐整。利用 :func:`dedent` 移除样例文本中所有行的常见空白将产生更好的结果。同时，当移除 Python 代码的格式时，可以直接使用文档字符串或嵌入的多行字符串。为了说明该功能，样例字符串引入了人造的缩进层次。

.. literalinclude:: textwrap_dedent.py
    :caption:
    :start-after: #end_pymotw_header

结果看起来更好。

.. {{{cog
.. cog.out(run_script(cog.inFile, 'textwrap_dedent.py'))
.. }}}

::

	$ python3 textwrap_dedent.py
	
	Dedented:
	
	The textwrap module can be used to format text for output in
	situations where pretty-printing is desired.  It offers
	programmatic functionality similar to the paragraph wrapping
	or filling features found in many text editors.
	

.. {{{end}}}

由于“dedent”是“indent”的反面，所以结果移除了文本块每行开头共同的空白。如果一行已经缩进了多次，那么不会移除某些空白。

像这样的输入

::

  ␣Line one.
  ␣␣␣Line two.
  ␣Line three.

将变成

::

  Line one.
  ␣␣Line two.
  Line three.

组合取消缩进和填充
==================

下面，利用几个不同的 *宽度* 值将取消缩进的文本传到 :func:`fill` 。

.. literalinclude:: textwrap_fill_width.py
    :caption:
    :start-after: #end_pymotw_header


这将使用指定的宽度产生输出。

.. {{{cog
.. cog.out(run_script(cog.inFile, 'textwrap_fill_width.py'))
.. }}}

::

	$ python3 textwrap_fill_width.py
	
	45 Columns:
	
	The textwrap module can be used to format
	text for output in situations where pretty-
	printing is desired.  It offers programmatic
	functionality similar to the paragraph
	wrapping or filling features found in many
	text editors.
	
	60 Columns:
	
	The textwrap module can be used to format text for output in
	situations where pretty-printing is desired.  It offers
	programmatic functionality similar to the paragraph wrapping
	or filling features found in many text editors.
	

.. {{{end}}}

缩进块
======

使用 :func:`indent` 函数将前缀文本一致地添加到字符串的所有行。本例利用 ``>`` 作为每行的前缀，将同样的示例文本格式化成引用回复邮件消息的一部分。

.. literalinclude:: textwrap_indent.py
   :caption:
   :start-after: #end_pymotw_header

文本块在换行时分割，添加前缀到包含文本的每一行，然后这些行被合并成新的字符串并返回。

.. {{{cog
.. cog.out(run_script(cog.inFile, 'textwrap_indent.py'))
.. }}}

::

	$ python3 textwrap_indent.py
	
	Quoted block:
	
	>  The textwrap module can be used to format text
	> for output in situations where pretty-printing is
	> desired.  It offers programmatic functionality
	> similar to the paragraph wrapping or filling
	> features found in many text editors.
	
	> Second paragraph after a blank line.

.. {{{end}}}

要控制哪行得到新的前缀，将可调函数作为断言参数传递给 :func:`indent` 。可调函数将在每个文本行被调用，并将前缀添加到返回值为真的行。

.. literalinclude:: textwrap_indent_predicate.py
   :caption:
   :start-after: #end_pymotw_header

本例将前缀 ``EVEN`` 添加到有偶数字符的行。

.. {{{cog
.. cog.out(run_script(cog.inFile, 'textwrap_indent_predicate.py'))
.. }}}

::

	$ python3 textwrap_indent_predicate.py
	
	Indent ' The textwrap module can be used to format text\n'?
	Indent 'for output in situations where pretty-printing is\n'?
	Indent 'desired.  It offers programmatic functionality\n'?
	Indent 'similar to the paragraph wrapping or filling\n'?
	Indent 'features found in many text editors.'?
	
	Quoted block:
	
	EVEN  The textwrap module can be used to format text
	for output in situations where pretty-printing is
	EVEN desired.  It offers programmatic functionality
	EVEN similar to the paragraph wrapping or filling
	EVEN features found in many text editors.

.. {{{end}}}

悬挂缩进
========

正如可以设置输出宽度一样，序列行跟首行缩进也能被独立控制。

.. literalinclude:: textwrap_hanging_indent.py
    :caption:
    :start-after: #end_pymotw_header

这将产生悬挂缩进，首行缩进比其他行小。

.. {{{cog
.. cog.out(run_script(cog.inFile, 'textwrap_hanging_indent.py'))
.. }}}

::

	$ python3 textwrap_hanging_indent.py
	
	The textwrap module can be used to format text for
	    output in situations where pretty-printing is
	    desired.  It offers programmatic functionality
	    similar to the paragraph wrapping or filling
	    features found in many text editors.

.. {{{end}}}

缩进值也可以包含非空白字符。悬挂缩进可以利用前缀 ``*`` 产生项目符号。

截断长文本
==========

要截断文本来创建摘要或预览，可以使用 :func:`shorten` 。诸如制表符、换行符、以及连续的多个空格等所有现存的空白都将被标准化为单一的空格。然后，文本被截断成小于或等于请求的长度，单词边界之间不会含有部分的单词。

.. literalinclude:: textwrap_shorten.py
   :caption:
   :start-after: #end_pymotw_header

如果非空白文本从原文移除，那么它将使用占位符替换。可以通过提供 :func:`shorten` ``placeholder`` 参数来替换默认值 ``[...]``。

.. {{{cog
.. cog.out(run_script(cog.inFile, 'textwrap_shorten.py'))
.. }}}

::

	$ python3 textwrap_shorten.py
	
	Original:
	
	 The textwrap module can be used to format text
	for output in situations where pretty-printing is
	desired.  It offers programmatic functionality
	similar to the paragraph wrapping or filling
	features found in many text editors.
	
	Shortened:
	
	The textwrap module can be used to format text for
	output in situations where pretty-printing [...]

.. {{{end}}}



.. seealso::

    * :pydoc:`textwrap`
