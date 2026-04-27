# 第四章：扩展之道 - Sphinx 插件系统

> 知其雄，守其雌，为天下溪。为天下溪，常德不离，复归于婴儿。知其白，守其黑，为天下式。为天下式，常德不忒，复归于无极。知其荣，守其辱，为天下谷。为天下谷，常德乃足，复归于朴。

## 4.1 扩展之妙

Sphinx 的强大之处，在于其**可扩展性**。扩展系统如天下谷，容纳百川，常德乃足，复归于朴。

## 4.2 扩展的基本结构

一个典型的 Sphinx 扩展：

```python
def setup(app):
    """扩展入口函数"""
    # 注册构建器
    app.add_builder(MyBuilder)
    
    # 注册指令
    app.add_directive('mydirective', MyDirective)
    
    # 注册角色
    app.add_role('myrole', myrole_fn)
    
    # 注册域名
    app.add_domain(MyDomain)
    
    # 连接事件
    app.connect('doctree-resolved', on_doctree_resolved)
    
    # 返回扩展元数据
    return {
        'version': '1.0',
        'env_version': 1,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

## 4.3 扩展类型

### 4.3.1 内置扩展

Sphinx 内置了丰富的扩展：

- `sphinx.ext.autodoc` - 自动文档生成
- `sphinx.ext.autosummary` - 自动摘要生成
- `sphinx.ext.doctest` - 文档测试
- `sphinx.ext.intersphinx` - 跨项目引用
- `sphinx.ext.todo` - TODO 列表
- `sphinx.ext.coverage` - 文档覆盖率
- `sphinx.ext.viewcode` - 代码查看
- `sphinx.ext.graphviz` - 图表生成
- `sphinx.ext.imgmath` - 数学公式
- `sphinx.ext.ifconfig` - 条件内容

### 4.3.2 第三方扩展

社区贡献了大量第三方扩展：

- `sphinxcontrib` 系列
- 主题扩展
- 语言支持扩展
- 集成扩展

## 4.4 事件系统

Sphinx 采用事件驱动架构，在构建流程的关键节点触发事件：

```python
# 配置初始化完成
app.connect('config-inited', on_config_inited)

# 构建器初始化
app.connect('builder-inited', on_builder_inited)

# 源文件读取
app.connect('source-read', on_source_read)

# doctree 读取完成
app.connect('doctree-read', on_doctree_read)

# doctree 解析完成
app.connect('doctree-resolved', on_doctree_resolved)

# 构建完成
app.connect('build-finished', on_build_finished)
```

> 圣人恒无心，以百姓之心为心。

扩展系统如圣人，无固定之心，以用户（开发者）之心为心。

---

**本章要义**：扩展系统是 Sphinx 的活力之源，开放包容，海纳百川。
