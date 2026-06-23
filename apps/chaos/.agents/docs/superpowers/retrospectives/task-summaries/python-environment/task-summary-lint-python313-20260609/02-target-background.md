# 2. 目标背景

## 2.1 初始背景

用户要求针对 `d:\spaces\AgentForge\.temp\error.log` 中 `#problems_and_diagnostics` 报告的问题进行修复。该日志反映 `apps/chaos` 项目中存在 Ruff lint、格式化和 Python 版本目标相关问题。

## 2.2 项目约束

本次工作遵循以下约束：

- 工作目录：`d:\spaces\AgentForge\apps\chaos`
- Python 项目命令优先使用 `uv`
- 遵循项目内 `AGENTS.md` 与 `.agents/rules/python.md` 规则
- 尽量只修改与 diagnostics 和用户明确反馈相关的文件
- 不主动格式化或重构无关文件
- 不提交 Git commit，除非用户明确要求

## 2.3 后续需求调整

初始 lint 修复完成后，用户提出两项追加要求：

1. 将 `podman_win.py` 中运行环境说明改为 Python 3.13+。
2. 移除 `from __future__ import annotations`。

随后用户进一步明确：

> `from __future__ import annotations 要全部移除，以匹配python3.13+`

因此任务范围从单文件修复扩展为：确保 `apps/chaos` 下 Python 文件中不再存在该 future import。
