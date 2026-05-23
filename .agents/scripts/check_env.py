from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


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


def _tool_version(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("version"), str):
        return value["version"]
    return "未声明"


def load_mise_tool_versions(project_root: Path) -> dict[str, str]:
    mise_path = project_root / "mise.toml"
    with mise_path.open("rb") as file:
        data = tomllib.load(file)

    tools = data.get("tools", {})
    if not isinstance(tools, dict):
        return {}

    return {
        "python": _tool_version(tools.get("python")),
        "uv": _tool_version(tools.get("uv")),
        "node": _tool_version(tools.get("node")),
        "defuddle": _tool_version(tools.get("npm:defuddle")),
    }


def build_tool_specs(project_root: Path) -> tuple[ToolSpec, ...]:
    versions = load_mise_tool_versions(project_root)
    python_version = versions.get("python", "未声明")
    uv_version = versions.get("uv", "未声明")
    node_version = versions.get("node", "未声明")
    defuddle_version = versions.get("defuddle", "未声明")

    return (
        ToolSpec(
            name="mise",
            command=["mise", "--version"],
            expected="已安装",
            fix="先安装 mise，再重新运行 mise run init",
            version_pattern=None,
            match_mode="available",
        ),
        ToolSpec(
            name="python",
            command=["python", "--version"],
            expected=python_version,
            fix=f"mise install python@{python_version}",
        ),
        ToolSpec(
            name="uv",
            command=["uv", "--version"],
            expected=uv_version,
            fix=f"mise install uv@{uv_version}",
        ),
        ToolSpec(
            name="node",
            command=["node", "--version"],
            expected=node_version,
            fix=f"mise install node@{node_version}",
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
            expected=defuddle_version,
            fix=f'mise install "npm:defuddle@{defuddle_version}"',
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


def check_config_consistency(project_root: Path) -> list[dict]:
    issues = []

    mise_path = project_root / "mise.toml"
    pyproject_path = project_root / "pyproject.toml"

    if not mise_path.exists() or not pyproject_path.exists():
        return issues

    mise_content = mise_path.read_text(encoding="utf-8")
    mise_match = re.search(r'python\s*=\s*"(\d+)\.(\d+)', mise_content)
    if not mise_match:
        return issues
    mise_major, mise_minor = int(mise_match[1]), int(mise_match[2])

    pyproject = pyproject_path.read_text(encoding="utf-8")

    ruff_match = re.search(r'target-version\s*=\s*"py(\d)(\d+)"', pyproject)
    if ruff_match:
        ruff_major, ruff_minor = int(ruff_match[1]), int(ruff_match[2])
        expected_ruff = f"py{mise_major}{mise_minor}"
        current_ruff = f"py{ruff_major}{ruff_minor}"
        if ruff_major != mise_major or ruff_minor != mise_minor:
            issues.append(
                {
                    "item": "Ruff target-version vs Python version",
                    "expected": expected_ruff,
                    "current": current_ruff,
                    "fix": f'更新 pyproject.toml 中 tool.ruff.target-version 为 "{expected_ruff}"',
                }
            )

    req_match = re.search(r'requires-python\s*=\s*">=\s*(\d+)\.(\d+)"', pyproject)
    if req_match:
        req_major, req_minor = int(req_match[1]), int(req_match[2])
        if req_major > mise_major or (
            req_major == mise_major and req_minor > mise_minor
        ):
            issues.append(
                {
                    "item": "requires-python 约束 vs mise Python 版本",
                    "expected": f">={mise_major}.{mise_minor}",
                    "current": f">={req_major}.{req_minor}",
                    "fix": f"降低 requires-python 约束或升级 mise Python 版本至 >={req_major}.{req_minor}",
                }
            )

    return issues


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    results = [check_tool(spec) for spec in build_tool_specs(project_root)]
    print("AgentForge 环境校验")
    print_table(results)

    consistency_issues = check_config_consistency(project_root)

    if consistency_issues:
        print("\n配置一致性校验:")
        headers_c = ("检查项", "期望值", "当前值", "修复建议")
        widths_c = [
            max(
                len(headers_c[idx]),
                *(len(str(i.get(k, ""))) for i in consistency_issues),
            )
            for idx, k in enumerate(["item", "expected", "current", "fix"])
        ]
        print(
            " | ".join(
                h.ljust(widths_c[idx]) for idx, h in enumerate(headers_c)
            )
        )
        print("-+-".join("-" * w for w in widths_c))
        for issue in consistency_issues:
            row = (
                issue["item"].ljust(widths_c[0]),
                issue["expected"].ljust(widths_c[1]),
                issue["current"].ljust(widths_c[2]),
                issue["fix"].ljust(widths_c[3]),
            )
            print(" | ".join(row))

    failed = [result for result in results if not result.ok]
    if failed or consistency_issues:
        if failed:
            print('\n存在工具版本或可用性不一致，请按"修复命令"列处理。')
        if consistency_issues:
            print('存在配置文件一致性不一致，请按"修复建议"列处理。')
        return 1

    print("\n环境满足项目基线。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
