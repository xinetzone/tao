# Task 2: Add Python And Podman Reference Entry Points

**Files:**
- Create: `.agents/docs/references/python/README.md`
- Create: `.agents/docs/references/python/package-index.md`
- Create: `.agents/docs/references/podman/README.md`
- Create: `.agents/docs/references/podman/command-cheatsheet.md`

- [ ] **Step 1: Create the topic directories**

Run:
```bash
New-Item -ItemType Directory -Force `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\references\python, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\references\podman
```

- [ ] **Step 2: Write `references/python/README.md`**

Create `.agents/docs/references/python/README.md`:
```md
# Python References

该目录存放与 AgentForge 排障和实现相关的 Python 参考知识。

## 建议收录范围

- 常用依赖包，如 `pytest`、`httpx`、`pydantic`
- Python 版本兼容与类型系统要点
- 测试、异步、打包和依赖管理相关知识

## 当前页面

- [Package Index](./package-index.md)
```

- [ ] **Step 3: Write `references/python/package-index.md`**

Create `.agents/docs/references/python/package-index.md`:
```md
# Python Package Index

## Goal

记录 AgentForge 中值得为 agent 建立专门参考页的 Python 包与主题。

## Relevance In AgentForge

- 关联模块：`src/taolib/`、`tests/`、`pyproject.toml`
- 常见触发场景：依赖升级、测试失败、类型问题、网络请求行为变化
- 优先检查文件：`pyproject.toml`、`src/taolib/github_app/`、`tests/github_app/`

## Current Candidates

- `pytest`：测试组织、夹具、异步测试。
- `httpx`：GitHub App HTTP 客户端相关请求行为。
- `PyJWT`：GitHub App JWT 签发与认证链路。
- `PyGithub`：对象化 GitHub API 访问适配层。

## Next Suggested Pages

- `pytest.md`
- `httpx.md`
- `pyjwt.md`
- `pygithub.md`

## Sources

- 官方文档：待补充
- 版本：按仓库依赖锁定版本补充
- 抓取时间：待补充
```

- [ ] **Step 4: Write `references/podman/README.md`**

Create `.agents/docs/references/podman/README.md`:
```md
# Podman References

该目录存放与容器构建、运行、挂载、网络和权限相关的 Podman 参考知识。

## 建议收录范围

- 常用命令速查
- 与 Docker 的差异点
- Rootless、挂载、网络和排障要点

## 当前页面

- [Command Cheatsheet](./command-cheatsheet.md)
```

- [ ] **Step 5: Write `references/podman/command-cheatsheet.md`**

Create `.agents/docs/references/podman/command-cheatsheet.md`:
```md
# Podman Command Cheatsheet

## Goal

为 agent 提供最常用的 Podman 命令入口，减少在排障时反复查找基础命令的成本。

## Relevance In AgentForge

- 关联模块：容器化工作流、开发环境脚本、后续可能引入的本地运行说明
- 常见触发场景：镜像构建失败、容器未启动、日志查看、挂载路径错误
- 优先检查文件：相关脚本、工作流配置、后续补充的集成说明页

## Common Commands

```bash
podman build -t my-image .
podman run --rm -it my-image
podman ps -a
podman logs <container>
podman exec -it <container> /bin/sh
podman rm -f <container>
podman image ls
```

## Common Problems

### 问题：容器存在但没有按预期启动

- 现象：`podman ps -a` 可以看到容器，但状态异常或快速退出。
- 原因：入口命令错误、环境变量缺失、挂载失败或权限不足。
- 排查步骤：先看 `podman logs`，再检查挂载参数和启动命令。
- 相关命令或代码位置：`podman logs <container>`、启动脚本或工作流文件。

## Sources

- 官方文档：待补充
- 版本：按本地或 CI 使用版本补充
- 抓取时间：待补充
```

- [ ] **Step 6: Run a quick file check**

Run:
```bash
Get-ChildItem c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\references -Recurse `
  | Select-Object FullName
```

Expected: `python/README.md`, `python/package-index.md`, `podman/README.md`, and `podman/command-cheatsheet.md` are present.

- [ ] **Step 7: Commit**

```bash
git add .agents/docs/references/python .agents/docs/references/podman
git commit -m "docs: add Python and Podman reference entry pages"
```
