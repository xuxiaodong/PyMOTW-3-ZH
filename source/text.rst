======
 文本 
======

对 Python 程序员而言，:class:`string` 类是最为明显可用的文本处理工具。不过，在标准库中有很多其它的工具使高级的文本处理更简单。

Python 2.0 以前编写的老旧代码不是使用 :class:`string` 对象的方法而是使用 :mod:`string` 模块中的函数。模块中的每一个函数都有等效的方法，不赞成在新代码中使用函数。

使用 Python 2.4 或更新版本的程序可以在 :class:`string` 或 :class:`unicode` 类的功能之外将 :class:`string.Template` 作为一种简单的参数化字符串方法使用。虽然没有很多 web 框架或 Python Package Index 上的扩展模块定义的模板功能丰富，但是对于需要将动态值插到静态文本外的用户可修改模板来说，:class:`string.Template` 是一种不错的妥协。

:mod:`textwrap` 模块包含用于从限制段落的输出宽度、增加缩进、插入换行符到一致地换行等格式化文本工具。

标准库在字符串对象所支持的内置相等性及排序比较外包含两个与比较文本值相关的模块。:mod:`re` 提供完整的正则表达式库，为了效率使用 C 实现。对于在大的数据集中查找子字符串、靠比固定字符串更复杂的模式比较字符串、以及平和的解析，正则表达式很便利。

另一方面，:mod:`difflib` 使用添加、移除、或更改部分项来计算文本序列之间的实际差异。:mod:`difflib` 中的比较函数输出能被用于提供更详尽的反馈，以便用户了解两方输入中的更改产生位置、文档如何随时间的流逝而更改等。

.. toctree::
   :maxdepth: 1

   textwrap/index
   difflib/index

..
   string/index
   re/index
   difflib/index
