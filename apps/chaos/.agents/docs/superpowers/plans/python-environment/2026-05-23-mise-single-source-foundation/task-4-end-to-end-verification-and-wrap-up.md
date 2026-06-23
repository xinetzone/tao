# Task 4: 端到端验证与收尾

**Files:**
- Verify: `.agents/scripts/check_env.py`
- Verify: `mise.toml`
- Verify: `README.md`
- Verify: `AGENTS.md`

- [ ] **Step 1: 运行环境校验入口**

Run:

```bash
mise run check-env
```

Expected: 输出 `AgentForge 环境校验`，并展示工具表格。若某些工具未安装或版本不一致，应显示修复命令；脚本不应出现 Python 异常。

- [ ] **Step 2: 运行只检查初始化入口**

Run:

```bash
mise run init-check
```

Expected: 执行 `mise trust` 与 `mise run check-env`；若环境满足基线，应以 `[OK] 环境检查完成` 结束。

- [ ] **Step 3: 运行 lint**

Run:

```bash
mise run lint
```

Expected: pre-commit 全量检查通过。若由于环境缺失失败，先按 `check-env` 修复建议处理；若仍无法运行，记录具体失败原因。

- [ ] **Step 4: 运行 Python 语法检查兜底**

Run:

```bash
python -m py_compile .agents/scripts/check_env.py tasks.py
```

Expected: 命令无输出且退出码为 0。

- [ ] **Step 5: 检查未完成标记和旧入口残留**

Run:

```bash
Select-String -Path .agents\scripts\check_env.py,README.md,AGENTS.md,docs\quickstart.md -Pattern "[T]BD|[T]ODO|[待]补|[占]位|[未]定|scripts/init.ps1|init.ps1" -CaseSensitive
```

Expected: No matches. If historical context intentionally保留旧入口，应在最终总结中说明具体位置和原因。

- [ ] **Step 6: 提交验证收尾变更**

If Task 4 required file changes, run:

```bash
git add .agents/scripts/check_env.py README.md AGENTS.md docs/quickstart.md
git commit -m "chore: verify mise foundation hardening"
```

Expected: 如有变更则创建收尾提交；如无变更则跳过提交，并在最终总结中说明验证结果。
