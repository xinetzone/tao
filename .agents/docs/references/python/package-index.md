# Python Package Index

## Search Keywords

- 主关键词：Python Packages
- 英文术语：Dependencies, Packages
- 常见别名：依赖, 包管理, 第三方库
- 错误短语：ModuleNotFoundError, ImportError, No module named

## Goal

本页作为项目中关键 Python 第三方依赖 (Python Packages) 的导航索引，说明各个包的用途及阅读顺序。

## Relevance In AgentForge

- 关联模块：全局项目依赖，特别是 `pyproject.toml` 中的定义。
- 常见触发场景：安装依赖失败、导入报错、或者需要查阅某个特定第三方库的用法时。
- 优先检查文件：`pyproject.toml`, `uv.lock`

## Trigger Phrases

- 项目用了哪些测试框架？
- HTTP 请求是用 requests 还是 httpx？
- 找不到对应的 Python 包文档在哪里？

## Key Concepts

- **核心依赖 (Core Dependencies)**：项目运行必不可少的包。
- **开发依赖 (Development Dependencies)**：仅在测试、格式化、构建文档时使用的包（如 `pytest`, `ruff`）。

## Packages

### 网络与异步
- **[httpx](./httpx.md)**: 现代的、支持异步的 HTTP 客户端。替代 `requests`。

### 测试与质量
- **[pytest](./pytest.md)**: 核心测试框架，配合 `pytest-asyncio` 进行异步测试。

### Web 框架与工具 (待补充详细页)
- **FastAPI**: 用于构建 API 的高性能 Web 框架。
- **Pydantic**: 数据验证和设置管理。

## Common Problems

### 问题：未记录的依赖包

- 现象：在查阅本索引时，发现某个代码中用到的包没有记录。
- 原因：包索引未及时更新。
- 排查步骤：
  1. 检查 `pyproject.toml` 中是否声明了该包。
  2. 考虑在 `references/python/` 下为该包创建一个新的参考页。
- 相关命令或代码位置：`pyproject.toml`

## Commands Or Snippets

```bash
# 查看当前环境安装的包
uv pip list
```

## Sources

- 官方文档：无
- 版本：N/A
- 抓取时间：N/A
