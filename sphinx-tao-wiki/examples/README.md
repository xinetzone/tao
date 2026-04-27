# Sphinx 道德经 - 示例项目

这是《Sphinx 道德经》教程的示例项目，演示如何使用 Sphinx 创建美观的文档。

## 项目结构

```
examples/
├── source/
│   ├── conf.py           # Sphinx 配置文件
│   ├── index.rst         # 首页
│   ├── dao-pian.rst      # 道篇
│   ├── de-pian.rst       # 德篇
│   ├── appendix.rst      # 附录
│   └── _static/
│       └── custom.css    # 自定义样式
└── build/                # 构建输出（生成后）
```

## 快速开始

### 1. 安装依赖

```bash
pip install sphinx
```

### 2. 构建文档

```bash
cd examples
sphinx-build -b html source build/html
```

或者如果你有 Makefile：

```bash
make html
```

### 3. 查看结果

在浏览器中打开 `build/html/index.html`。

## 功能演示

本示例项目演示了以下 Sphinx 功能：

- [x] 基本的 reStructuredText 语法
- [x] 文档树结构（toctree）
- [x] 代码高亮
- [x] 数学公式支持
- [x] 表格
- [x] 警告和提示框
- [x] 自定义主题样式
- [x] 交叉引用
- [x] 内置扩展使用

## 扩展配置

在 `conf.py` 中我们启用了以下扩展：

```python
extensions = [
    'sphinx.ext.autodoc',      # 自动文档生成
    'sphinx.ext.doctest',      # 文档测试
    'sphinx.ext.intersphinx',  # 跨项目引用
    'sphinx.ext.todo',         # TODO 列表
    'sphinx.ext.coverage',     # 文档覆盖
    'sphinx.ext.viewcode',     # 代码查看
    'sphinx.ext.mathjax',      # 数学公式
]
```

## 学习建议

1. 先查看 `index.rst` 了解基本结构
2. 阅读 `conf.py` 了解配置选项
3. 运行构建命令查看输出结果
4. 修改内容并重新构建，观察变化
5. 参考《Sphinx 道德经》教程深入理解

## 更多资源

- 教程文档：`../README.md`
- Sphinx 官网：https://www.sphinx-doc.org/
- reStructuredText 入门：https://docutils.readthedocs.io/

---

> 道生一，一生二，二生三，三生万物。
