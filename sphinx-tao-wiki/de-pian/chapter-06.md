# 第六章：构建之德 - Builders 详解

> 大成若缺，其用不弊。大盈若冲，其用不穷。大直若诎，大巧若拙，大赢若绌。躁胜寒，静胜热，清静可以为天下正。

## 6.1 Builder 之德

Builder 是 Sphinx 的输出引擎，如天下神器，不可为也，不可执也。不同的 Builder，适应不同的输出需求。

## 6.2 主要 Builder 详解

### 6.2.1 HTMLBuilder - 网页之德

```python
from sphinx.builders.html import HTMLBuilder
```

HTML Builder 将文档转换为美观的网页：

```python
# conf.py 配置
html_theme = 'alabaster'
html_static_path = ['_static']
html_css_files = ['custom.css']
```

特点：
- 交互式阅读
- 搜索功能
- 响应式设计
- 主题定制

### 6.2.2 LaTeXBuilder - 印刷之德

```python
from sphinx.builders.latex import LaTeXBuilder
```

LaTeX Builder 将文档转换为专业的印刷文档：

```python
# conf.py 配置
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
}
```

特点：
- 专业排版
- PDF 输出
- 打印质量
- 书籍格式

### 6.2.3 其他常用 Builder

| Builder | 输出格式 | 用途 |
|---------|---------|------|
| `SingleFileHTMLBuilder` | 单页 HTML | 简单文档 |
| `DirHTMLBuilder` | 目录 HTML | 大型文档 |
| `EPUB3Builder` | EPUB | 电子书籍 |
| `ManpageBuilder` | man 手册 | Unix 手册 |
| `TextBuilder` | 纯文本 | 简单文本 |
| `LinkCheckBuilder` | 链接检查 | 验证链接 |

## 6.3 自定义 Builder

创建自定义 Builder：

```python
from sphinx.builders import Builder

class MyBuilder(Builder):
    name = 'mybuilder'
    format = 'myformat'
    epilog = '构建完成！'
    
    def init(self):
        """初始化"""
        pass
        
    def get_outdated_docs(self):
        """获取需要更新的文档"""
        return self.env.found_docs
        
    def prepare_writing(self, docnames):
        """准备写入"""
        pass
        
    def write_doc(self, docname, doctree):
        """写入单个文档"""
        # 处理文档树
        pass
        
    def finish(self):
        """完成构建"""
        pass
```

> 天下万物生于有，有生于无。

Builder 从无到有，生成各种格式的文档。

---

**本章要义**：根据输出需求选择合适的 Builder，善用其德，方能得到满意的文档。
