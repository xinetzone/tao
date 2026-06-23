# Task 3: 收口当前推荐入口文档口径

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Optional Modify: `docs/quickstart.md`
- Verify: repository text search

- [ ] **Step 1: 搜索历史入口残留**

Run:

```bash
Select-String -Path README.md,AGENTS.md,docs\quickstart.md,.agents\scripts\check_env.py -Pattern "scripts/init.ps1|init.ps1|pipx|conda" -CaseSensitive
```

Expected: 当前态入口文档不应推荐 `scripts/init.ps1`、`pipx` 或 `conda` 作为项目依赖安装路径。若命中历史说明，需要判断是否属于禁止路径或历史记录。

- [ ] **Step 2: 更新 README 当前入口表达**

Ensure `README.md` environment section keeps this recommended path:

```markdown
如需一键完成信任、安装、依赖同步与首次环境校验，请直接运行：

```bash
mise run init
```
```

Ensure validation section includes:

```markdown
建议至少完成以下验证：

```bash
mise run check-env
mise run test
```
```

Do not add direct `pip install`、`conda install` or `pipx install` instructions.

- [ ] **Step 3: 更新 AGENTS 当前入口表达**

Ensure `AGENTS.md` contains an environment rule equivalent to:

```markdown
- **外部工具初始化**：运行 `mise run init` 安装项目所需的外部工具依赖。使用 `mise run init-check` 可仅检查依赖状态，使用 `mise run check-env` 可直接校验工具链版本。
```

Ensure it also retains the rule that Python dependencies are managed by `uv` and direct `pip` or `conda` installation is forbidden.

- [ ] **Step 4: 必要时更新 quickstart**

If `docs/quickstart.md` recommends a historical init path, replace it with:

```markdown
mise run init
```

If it only mentions `mise trust` / `mise install` / `mise run sync` as expanded manual steps, keep those steps.

- [ ] **Step 5: 再次搜索确认当前态口径一致**

Run:

```bash
Select-String -Path README.md,AGENTS.md,docs\quickstart.md,.agents\scripts\check_env.py -Pattern "scripts/init.ps1|init.ps1|pipx|conda" -CaseSensitive
```

Expected: No matches in current recommended-path sections. If matches remain only in explicit historical context, document that in the implementation summary before continuing.

- [ ] **Step 6: 提交文档口径收口**

Run:

```bash
git add README.md AGENTS.md docs/quickstart.md .agents/scripts/check_env.py
git commit -m "docs: align mise environment entrypoints"
```

Expected: Git 创建一个文档口径收口提交；若 `docs/quickstart.md` 未变更，Git 只提交实际变更文件。
