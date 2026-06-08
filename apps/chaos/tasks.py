"""Invoke tasks for project environment initialization."""

from __future__ import annotations

import locale
import os
import shutil
import subprocess
import sys
from pathlib import Path

from invoke import Exit, task

REPO_ROOT = Path(__file__).resolve().parent
PLATFORM = sys.platform

_STDOUT_FD = sys.stdout.fileno()


def _console_encoding() -> str:
    if sys.platform == "win32":
        import ctypes

        cp = ctypes.windll.kernel32.GetConsoleOutputCP()
        return f"cp{cp}"
    return sys.stdout.encoding or locale.getpreferredencoding() or "utf-8"


_STDOUT_ENC = _console_encoding()


def _write(msg: str) -> None:
    os.write(_STDOUT_FD, (msg + "\n").encode(_STDOUT_ENC, errors="replace"))


def _check_mise() -> str:
    mise = shutil.which("mise")
    if mise is None:
        raise Exit(
            "[ERROR] 未检测到 mise，无法继续初始化。\n"
            "[WHY]   AgentForge 使用 mise 统一管理 Python、uv、Node 与外部工具版本。\n"
            "[FIX]   请先安装 mise: https://mise.jdx.dev/getting-started.html\n"
            "[NEXT]  安装完成后重新打开终端，并运行: mise run init",
            code=1,
        )
    return mise


def _child_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = _STDOUT_ENC
    return env


def _print_plan(title: str, steps: list[str]) -> None:
    _write(f"[INFO] {title}")
    _write(f"[INFO] 平台: {PLATFORM}")
    _write(f"[INFO] 仓库根目录: {REPO_ROOT}")
    _write("[INFO] 将依次执行:")
    for index, step in enumerate(steps, start=1):
        _write(f"[INFO]   {index}. {step}")


def _print_success_next_steps(message: str, next_steps: list[str]) -> None:
    _write("")
    _write(f"[OK] {message}")
    for next_step in next_steps:
        _write(f"[NEXT] {next_step}")


def _print_failure(
    label: str,
    fix_hint: str = "",
    why_hint: str = "",
    next_hint: str = "",
) -> None:
    _write(f"[FAIL] {label}")
    if why_hint:
        _write(f"[WHY]  {why_hint}")
    if fix_hint:
        _write(f"[FIX]  {fix_hint}")
    if next_hint:
        _write(f"[NEXT] {next_hint}")


def _run_step(
    label: str,
    command: list[str],
    fix_hint: str = "",
    why_hint: str = "",
    next_hint: str = "",
) -> None:
    _write(f"[STEP] {label}")
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=_child_env(),
            check=False,
            capture_output=False,
        )
    except FileNotFoundError:
        _print_failure(label, fix_hint, why_hint, next_hint)
        raise Exit(code=1)

    if completed.returncode != 0:
        _print_failure(label, fix_hint, why_hint, next_hint)
        raise Exit(code=completed.returncode)

    _write(f"[OK]   {label}")


@task
def init(ctx):
    """一键环境初始化：信任配置 → 安装工具链 → 同步依赖 → 校验环境"""
    _check_mise()
    _print_plan(
        "AgentForge 新手接入初始化",
        [
            "信任 mise 配置",
            "安装 mise 工具链",
            "同步 Python 依赖组",
            "执行环境一致性校验",
        ],
    )

    _run_step(
        "信任仓库 mise 配置",
        ["mise", "trust"],
        "可手动运行: mise trust",
        "mise 需要先信任当前仓库配置，才能使用项目声明的工具链与任务。",
        "修复后重新运行: mise run init",
    )
    _run_step(
        "安装 mise 工具链 (Python 3.13 / uv 0.11.16 / Node 22.22.3 等)",
        ["mise", "install"],
        "可手动运行: mise install",
        "工具链安装失败，常见原因包括网络不可用、mise 配置未信任或本机缺少系统依赖。",
        "修复后重新运行: mise run init",
    )
    _run_step(
        "同步 Python 依赖组",
        ["mise", "run", "sync"],
        "可手动运行: mise run sync",
        "依赖同步失败，常见原因包括网络不可用、uv 未正确安装或 lock 文件与当前环境不匹配。",
        "修复后重新运行: mise run init",
    )
    _run_step(
        "执行环境一致性校验",
        ["mise", "run", "check-env"],
        "可手动运行: mise run check-env",
        "环境校验失败，说明本机工具版本或依赖状态仍未达到项目基线。",
        "根据上方校验结果修复后重新运行: mise run init-check",
    )

    _print_success_next_steps(
        "初始化完成",
        [
            "建议运行: mise run test",
            "可选检查: mise run lint",
            "构建文档: mise run docs-html",
        ],
    )


@task
def init_check(ctx):
    """仅检查环境（不安装/同步）：信任配置 → 校验环境"""
    _check_mise()
    _print_plan(
        "AgentForge 环境检查",
        [
            "信任 mise 配置",
            "校验环境一致性",
        ],
    )

    _run_step(
        "信任仓库 mise 配置",
        ["mise", "trust"],
        "可手动运行: mise trust",
        "mise 需要先信任当前仓库配置，才能读取项目声明的工具链与任务。",
        "修复后重新运行: mise run init-check",
    )
    _run_step(
        "校验当前工具链与版本基线",
        ["mise", "run", "check-env"],
        "可手动运行: mise install ; mise run check-env",
        "环境校验失败，说明本机工具版本或依赖状态未达到项目基线。",
        "如需完整修复流程，可运行: mise run init",
    )

    _print_success_next_steps(
        "环境检查完成",
        [
            "如需完整初始化: mise run init",
            "如需运行测试: mise run test",
        ],
    )
