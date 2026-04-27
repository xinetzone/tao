# 第八章：主题之德 - 外观定制

> 五色令人目盲，五音令人耳聋，五味令人口爽，驰骋田猎令人心发狂，难得之货令人行妨。是以圣人为腹不为目，故去彼取此。

## 8.1 主题之德

主题决定了文档的外观，如衣饰之于人，需内外兼修。Sphinx 提供了丰富的主题系统，使文档美观实用。

## 8.2 内置主题

Sphinx 内置了多个主题：

- **alabaster** - 简洁美观的默认主题
- **sphinx_rtd_theme** - Read the Docs 风格
- **sphinxdoc** - 官方文档风格
- **nature** - 自然风格
- **classic** - 经典风格
- **basic** - 基础风格

## 8.3 主题配置

在 `conf.py` 中配置主题：

```python
html_theme = 'alabaster'

html_theme_options = {
    'github_user': 'username',
    'github_repo': 'project',
    'github_banner': True,
    'travis_button': True,
    'fixed_sidebar': True,
}
```

## 8.4 自定义主题

### 8.4.1 基本结构

```
mytheme/
├── theme.conf
├── layout.html
└── static/
    └── mystyle.css
```

### 8.4.2 theme.conf

```ini
[theme]
inherit = basic
stylesheet = mystyle.css
```

### 8.4.3 模板定制

使用 Jinja2 模板定制布局：

```html
{% extends "layout.html" %}

{% block extrahead %}
<style>
/* 自定义样式 */
</style>
{% endblock %}

{% block content %}
<div class="my-content">
    {{ super() }}
</div>
{% endblock %}
```

## 8.5 主题之道

好的主题，应该：

- **以内容为主** - 不喧宾夺主
- **简洁实用** - 易于阅读和导航
- **响应式设计** - 适应不同设备
- **可定制性** - 满足不同需求

> 是以圣人方而不割，廉而不刿，直而不肆，光而不耀。

---

**本章要义**：主题是文档的外衣，应简洁实用，不掩盖内容的光芒。
