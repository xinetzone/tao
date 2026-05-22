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
            "[ERROR] 未检测到 mise，请先安装后再初始化项目环境。\n"
            "[FIX]   参考安装说明: https://mise.jdx.dev/getting-started.html",
            code=1,
        )
    return mise


def _child_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = _STDOUT_ENC
    return env


def _run_step(label: str, command: list[str], fix_hint: str = "") -> None:
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
        _write(f"[FAIL] {label}")
        if fix_hint:
            _write(f"[FIX]  {fix_hint}")
        raise Exit(code=1)

    if completed.returncode != 0:
        _write(f"[FAIL] {label}")
        if fix_hint:
            _write(f"[FIX]  {fix_hint}")
        raise Exit(code=completed.returncode)

    _write(f"[OK]   {label}")


@task
def init(ctx):
    """一键环境初始化：信任配置 → 安装工具链 → 同步依赖 → 校验环境"""
    _check_mise()
    _write(f"[INFO] 平台: {PLATFORM}")
    _write(f"[INFO] 仓库根目录: {REPO_ROOT}")

    _run_step("信任仓库 mise 配置", ["mise", "trust"], "可手动运行: mise trust")
    _run_step(
        "安装 mise 工具链 (Python 3.14.5 / uv 0.11.16 / Node 22.22.3 等)",
        ["mise", "install"],
        "可手动运行: mise install",
    )
    _run_step(
        "同步 Python 依赖组",
        ["mise", "run", "sync"],
        "可手动运行: mise run sync",
    )
    _run_step(
        "执行环境一致性校验",
        ["mise", "run", "check-env"],
        "可手动运行: mise run check-env",
    )

    _write("")
    _write("[OK] 初始化完成")
    _write("常用入口: mise run test / mise run lint / mise run docs-html")


@task
def init_check(ctx):
    """仅检查环境（不安装/同步）：信任配置 → 校验环境"""
    _check_mise()
    _write(f"[INFO] 平台: {PLATFORM}")
    _write(f"[INFO] 仓库根目录: {REPO_ROOT}")

    _run_step("信任仓库 mise 配置", ["mise", "trust"], "可手动运行: mise trust")
    _run_step(
        "校验当前工具链与版本基线",
        ["mise", "run", "check-env"],
        "可手动运行: mise install ; mise run check-env",
    )

    _write("")
    _write("[OK] 环境检查完成")
    _write("建议后续命令: mise run test / mise run lint / mise run docs-html")
