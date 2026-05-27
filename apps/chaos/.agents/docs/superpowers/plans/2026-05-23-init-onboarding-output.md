# Init Onboarding Output Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 增强现有 `mise run init` / `mise run init-check` 的命令内新手接入闭环。

**Architecture:** 低侵入式修改 `tasks.py`，保留现有 mise 与 Invoke 入口不变。将流程概览、失败输出、成功下一步建议拆成小函数。

**Tech Stack:** Python 3.14、Invoke、标准库 subprocess/shutil/pathlib、pytest、mise、uv。

## File Structure

- Modify: `tasks.py` — 初始化任务、流程概览、失败提示、成功建议
- Modify: `tests/test_tasks.py` — 验证辅助函数与错误路径
- No modify: `mise.toml` — 入口已满足目标

## Key Design Decisions

1. 不新增命令入口（mise run init / init-check 不变）
2. 输出函数拆分为可测试小粒度：`_print_plan`、`_print_success_next_steps`、`_print_failure`
3. `_run_step` 新增 why_hint/next_hint 默认参数，向后兼容
4. `_check_mise` 缺失提示升级为 ERROR/WHY/FIX/NEXT 四段式
