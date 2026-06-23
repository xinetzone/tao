# Task 3: Add Issue Patterns And Project Integration Pages

**Files:**
- Create: `.agents/docs/issue-patterns/python-errors.md`
- Create: `.agents/docs/issue-patterns/podman-errors.md`
- Create: `.agents/docs/integrations/python-in-agentforge.md`
- Create: `.agents/docs/integrations/podman-in-agentforge.md`

- [ ] **Step 1: Write `python-errors.md`**

Create `.agents/docs/issue-patterns/python-errors.md`:
```md
# Python Error Patterns

## Pattern 1: Optional Dependency Not Installed

- 现象：运行时出现 `ModuleNotFoundError` 或导入失败。
- 常见原因：可选依赖未安装、依赖组未同步、环境切换后锁文件未生效。
- 排查步骤：
  1. 检查 `pyproject.toml` 中对应依赖组。
  2. 检查 `uv.lock` 是否包含目标依赖。
  3. 使用 `uv run` 在项目环境内复现。
- 优先检查文件：`pyproject.toml`、`uv.lock`

## Pattern 2: Python Version Compatibility Regression

- 现象：升级 Python 版本后测试失败或 API 行为变化。
- 常见原因：标准库行为调整、第三方包兼容性不足、类型检查假设失效。
- 排查步骤：
  1. 阅读 `.agents/docs/version-tracking.md`
  2. 运行 `.agents/scripts/check_python_compat.py`
  3. 运行 `.agents/scripts/check_python_deprecations.py`
- 优先检查文件：`.agents/docs/version-tracking.md`、`.agents/scripts/`
```

- [ ] **Step 2: Write `podman-errors.md`**

Create `.agents/docs/issue-patterns/podman-errors.md`:
```md
# Podman Error Patterns

## Pattern 1: Mount Or Path Mapping Failure

- 现象：容器内看不到预期文件，或启动时报路径不存在。
- 常见原因：宿主机路径错误、Windows 路径格式不匹配、权限或标签设置问题。
- 排查步骤：
  1. 核对宿主机实际路径。
  2. 重新检查 `podman run -v` 参数。
  3. 查看容器日志并进入容器内确认挂载结果。
- 优先命令：`podman run`, `podman exec`, `podman inspect`

## Pattern 2: Container Exits Immediately

- 现象：容器创建成功但立刻退出。
- 常见原因：入口命令错误、依赖服务缺失、环境变量未传入。
- 排查步骤：
  1. 执行 `podman logs <container>`
  2. 检查入口命令和参数
  3. 验证环境变量与挂载目录
- 优先命令：`podman logs`, `podman inspect`
```

- [ ] **Step 3: Write `python-in-agentforge.md`**

Create `.agents/docs/integrations/python-in-agentforge.md`:
```md
# Python In AgentForge

## Goal

说明 Python 相关外部知识在 AgentForge 仓库中的主要落点，帮助 agent 快速从问题跳到代码和配置。

## Primary Files

- `pyproject.toml`：依赖组、Python 版本范围和工具配置入口。
- `src/taolib/`：核心 Python 代码。
- `tests/`：行为验证与回归测试。
- `.agents/docs/version-tracking.md`：Python 版本适配知识沉淀。

## Common Navigation Paths

- 依赖问题：先看 `pyproject.toml` 与 `uv.lock`
- GitHub App 认证问题：先看 `src/taolib/github_app/`
- 测试失败：先看 `tests/github_app/` 和对应模块
- 版本兼容问题：先看 `.agents/docs/version-tracking.md` 与 `.agents/scripts/`

## Related References

- `../references/python/package-index.md`
- `../issue-patterns/python-errors.md`
```

- [ ] **Step 4: Write `podman-in-agentforge.md`**

Create `.agents/docs/integrations/podman-in-agentforge.md`:
```md
# Podman In AgentForge

## Goal

说明 Podman 相关知识在 AgentForge 中的当前和潜在落点，帮助 agent 判断何时需要参考容器文档。

## Current Assessment

- 当前仓库中尚未形成明显的 Podman 专用脚本或完整容器工作流。
- Podman 相关知识目前更适合作为通用运行环境与排障能力储备。

## Suggested Future Mapping

- 若后续引入本地容器开发脚本，优先记录到 `scripts/`
- 若后续引入 CI 容器构建流程，优先记录到 `.github/workflows/`
- 若后续引入开发文档，再同步到面向人类的 `docs/`

## Related References

- `../references/podman/command-cheatsheet.md`
- `../issue-patterns/podman-errors.md`
```

- [ ] **Step 5: Run a structure check**

Run:
```bash
Get-ChildItem c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\issue-patterns, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\integrations `
  | Select-Object FullName
```

Expected: the four new Markdown files are listed.

- [ ] **Step 6: Commit**

```bash
git add .agents/docs/issue-patterns .agents/docs/integrations
git commit -m "docs: add issue patterns and integration maps for AI wiki"
```
