# Task 6: 补齐学习笔记、CI 验证与测试报告

**Files:**
- Create: `docs/github-app-token-override.md`
- Create: `.agents/docs/superpowers/retrospectives/2026-05-22-github-app-installation-token-override-testing.md`
- Modify: `docs/index.md`
- Modify: `README.md`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/project_changelogs/CHANGELOG_2026-05.md`

- [ ] **Step 1: 写文档与报告内容**

```md
# GitHub App 安装令牌请求级覆盖头学习笔记

GitHub 在 2026-05-15 公布了 `X-GitHub-Stateless-S2S-Token` 请求头，用于 `POST /app/installations/{installation_id}/access_tokens` 的逐请求覆盖。`enabled` 会返回新的 stateless token，`disabled` 会返回 classic stateful token，而默认不带头时继续遵循平台 rollout。对接方最重要的准备工作不是解析 JWT，而是消除长度、正则、数据库字段与日志格式上对旧 token 的假设。
```

```md
# 2026-05-22 GitHub App Token Override Testing

- 功能测试：通过
- 并发测试：25 并发 -> 1 次上游请求
- 压测：100 并发 -> 1 次上游请求，失败率 0%
- 风险：当前缓存仅为单进程实现，多实例部署仍需外部缓存
```

- [ ] **Step 2: 更新索引、README、CI 与项目变更日志**

~~~~md
```{toctree}
:maxdepth: 2
:caption: 目录
:hidden:

intro
quickstart
features
github-app-token-override
api
deploy
contributing
changelog
```
~~~~

```yaml
- name: Run GitHub App token tests
  run: uv run pytest tests/github_app -v
```

```md
### Added
- 新增 GitHub App 安装令牌管理层设计与实现计划，支持请求级覆盖头、自动降级、CLI、并发测试与学习笔记。
```

- [ ] **Step 3: 运行完整验证**

Run: `uv run pytest tests/github_app -v`
Expected: PASS with all GitHub App tests green

Run: `uv run pytest tests/ -v`
Expected: PASS with existing tests still green

Run: `uv run --group docs invoke build --target html`
Expected: PASS with generated docs including `github-app-token-override.html`

- [ ] **Step 4: 自查指标并写入报告**

将以下指标对比写入测试报告（指标表已抽取为独立原子单元，详见 [metrics-comparison.md](metrics-comparison.md)）：

```md
## 指标对比

| 指标 | 改造前 | 改造后 |
|------|--------|--------|
| 同 key 25 并发上游请求数 | 25 | 1 |
| 同 key 100 并发失败率 | 未定义 | 0% |
| 覆盖头控制能力 | 无 | `auto/enabled/disabled` |
| 日志脱敏 | 无统一约束 | 默认脱敏 |
```

- [ ] **Step 5: 提交本任务**

```bash
git add docs/github-app-token-override.md docs/index.md README.md .github/workflows/ci.yml tests/project_changelogs/CHANGELOG_2026-05.md .agents/docs/superpowers/retrospectives/2026-05-22-github-app-installation-token-override-testing.md
git commit -m "docs: add github app token override notes and reports"
```
