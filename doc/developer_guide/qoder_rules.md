# Qoder 规范

## Python 环境
执行 Python 测试和代码运行时，默认使用 `${PYTHON_ENV_DIR:-C:\Users\XMICUser\.conda\envs\py314}` 环境。

## 记忆管理
- **禁止重复存储**：`AGENTS.md`、`.qoder/rules/*.md`、`pyproject.toml` 每次会话自动加载为上下文，不得复制为记忆
- **创建前搜索**：使用 `search_memory` 确认无重复或需更新的记忆
- **合并优先**：找到相关内容优先 `update` 而非新建
- **一主题一条**：同一主题选最匹配单一类别存储
- **同步演进**：项目重大变化时更新已有记忆，而非保留过时内容