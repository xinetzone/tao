from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    name: str
    command: list[str]
    expected: str
    fix: str
    required: bool = True
    version_pattern: str | None = r"(\d+(?:\.\d+)+)"
    match_mode: str = "prefix"


@dataclass(frozen=True)
class ToolResult:
    name: str
    expected: str
    current: str
    ok: bool
    fix: str


TOOLS: tuple[ToolSpec, ...] = (
    ToolSpec(
        name="mise",
        command=["mise", "--version"],
        expected="已安装",
        fix="先安装 mise，再重新运行 scripts/init.ps1",
        version_pattern=None,
        match_mode="available",
    ),
    ToolSpec(
        name="python",
        command=["python", "--version"],
        expected="3.14.5",
        fix="mise install python@3.14.5",
    ),
    ToolSpec(
        name="uv",
        command=["uv", "--version"],
        expected="0.11.16",
        fix="mise install uv@0.11.16",
    ),
    ToolSpec(
        name="node",
        command=["node", "--version"],
        expected="22.22.3",
        fix="mise install node@22.22.3",
        version_pattern=r"v?(\d+(?:\.\d+)+)",
    ),
    ToolSpec(
        name="ruff",
        command=["uv", "run", "ruff", "--version"],
        expected="0.15.14",
        fix="mise run sync",
    ),
    ToolSpec(
        name="pre-commit",
        command=["uv", "run", "pre-commit", "--version"],
        expected="4.6.0",
        fix="mise run sync",
    ),
    ToolSpec(
        name="defuddle",
        command=["mise", "x", "npm:defuddle", "--", "defuddle", "--version"],
        expected="0.18.1",
        fix='mise install "npm:defuddle@0.18.1"',
    ),
)


def run_command(command: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return False, "未安装"

    output = (completed.stdout or completed.stderr).strip()
    line = output.splitlines()[0].strip() if output else ""

    if completed.returncode != 0:
        return False, line or f"命令失败 (exit {completed.returncode})"

    return True, line or "可用"


def extract_version(text: str, pattern: str | None) -> str:
    if pattern is None:
        return text
    match = re.search(pattern, text)
    return match.group(1) if match else text


def is_match(spec: ToolSpec, current: str) -> bool:
    if spec.match_mode == "available":
        return current not in {"未安装", ""}

    version = extract_version(current, spec.version_pattern)
    if spec.match_mode == "prefix":
        return version.startswith(spec.expected)

    return version == spec.expected


def check_tool(spec: ToolSpec) -> ToolResult:
    ok, current = run_command(spec.command)
    if not ok:
        return ToolResult(
            name=spec.name,
            expected=spec.expected,
            current=current,
            ok=False,
            fix=spec.fix,
        )

    return ToolResult(
        name=spec.name,
        expected=spec.expected,
        current=current,
        ok=is_match(spec, current),
        fix=spec.fix,
    )


def print_table(results: list[ToolResult]) -> None:
    headers = ("工具", "期望值", "当前值", "状态", "修复命令")
    rows = [
        (
            result.name,
            result.expected,
            result.current,
            "OK" if result.ok else "FAIL",
            result.fix if not result.ok else "-",
        )
        for result in results
    ]

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]

    def format_row(values: tuple[str, ...]) -> str:
        return " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(values)
        )

    print(format_row(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(format_row(row))


def main() -> int:
    results = [check_tool(spec) for spec in TOOLS]
    print("AgentForge 环境校验")
    print_table(results)

    failed = [result for result in results if not result.ok]
    if failed:
        print("\n存在工具版本或可用性不一致，请按“修复命令”列处理。")
        return 1

    print("\n环境满足项目基线。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
