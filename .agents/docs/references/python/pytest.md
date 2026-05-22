# pytest

## Search Keywords

- 主关键词：pytest
- 英文术语：pytest, test fixtures, mocks, code coverage
- 常见别名：测试框架, 单元测试
- 错误短语：fixture not found, test collection failed, ModuleNotFoundError in tests, assert failed

## Goal

说明 pytest 在项目中的使用规范、常见 Fixture 模式以及异步测试的处理方法，帮助解决测试失败 (test failures) 问题。

## Relevance In AgentForge

- 关联模块：所有模块的单元测试与集成测试，尤其是 `tests/github_app/` 和 `flexloop/tests/` 目录。
- 常见触发场景：运行测试套件失败、编写新测试时不知道如何 Mock 异步客户端。
- 优先检查文件：`tests/conftest.py`, `pyproject.toml` (pytest 配置区)

## Trigger Phrases

- 为什么 pytest 没收集到测试？
- 怎么在 pytest 里测试 asyncio 异步函数？
- 找不到对应的 fixture 报错怎么办？
- 怎么生成 pytest 覆盖率报告？

## Key Concepts

- **Fixture**: pytest 中用于提供测试上下文和依赖注入的机制（如提供 mock 配置、临时目录等）。
- **Asyncio Testing**: 使用 `pytest.mark.asyncio` 装饰器或在配置中开启自动处理，来测试 `async def` 函数。
- **Mocking**: 隔离外部依赖（如 `httpx.AsyncClient` 或 GitHub API），常用 `unittest.mock.AsyncMock`。

## Common Problems

### 问题：异步测试未被执行或报 RuntimeWarning

- 现象：测试函数没有运行，或者抛出 `RuntimeWarning: coroutine '...' was never awaited`。
- 原因：测试函数是 `async def`，但没有使用 `pytest-asyncio` 的标记，导致 pytest 将其作为普通函数处理。
- 排查步骤：
  1. 确保安装了 `pytest-asyncio`。
  2. 检查测试函数上是否有 `@pytest.mark.asyncio` 装饰器，或者在 `pytest.ini`/`pyproject.toml` 中设置了 `asyncio_mode = "auto"`。
- 相关命令或代码位置：`tests/github_app/test_client.py`

### 问题：找不到 Fixture

- 现象：`fixture 'mock_settings' not found`
- 原因：Fixture 未定义，或者定义 Fixture 的 `conftest.py` 作用域没有覆盖到当前测试文件。
- 排查步骤：
  1. 确认 fixture 名称拼写正确。
  2. 检查最近的 `conftest.py` 是否包含了该 fixture，或在当前文件中显式定义。

## Commands Or Snippets

```bash
# 运行特定模块的测试并输出详细信息
pytest tests/github_app/ -v

# 运行特定测试函数
pytest tests/github_app/test_client.py::test_client_sends_override_header_for_enabled_strategy -v

# 运行并生成覆盖率报告
pytest tests/ -v --cov=taolib --cov-report=html
```

```python
# 异步测试示例
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_function(mock_settings):
    # Arrange
    client = AsyncMock()
    # Act
    result = await do_something_async(client, mock_settings)
    # Assert
    assert result is True
```

## Sources

- 官方文档：[pytest documentation](https://docs.pytest.org/en/latest/)
- 版本：基于项目中使用的当前版本
- 抓取时间：N/A
