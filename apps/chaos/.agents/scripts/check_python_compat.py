#!/usr/bin/env python
"""Python 版本合规性扫描脚本。

基于已知的 Python 版本弃用/移除清单，扫描项目代码中可能的不兼容模式。
支持 --target-version 参数指定目标 Python 版本（默认 3.15）。

用法:
    python check_python_compat.py [--target-version 3.15]
"""

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEPRECATION_RULES = {
    "3.15": {
        "removed": [],
        "deprecated": [],
        "behavior_changes": [
            {
                "pattern": r"(?:open|read_text|write_text)\(",
                "check": lambda path, line: (
                    ("open(" in line or "read_text(" in line or "write_text(" in line)
                    and "encoding=" not in line
                    and "encoding =" not in line
                ),
                "severity": "info",
                "message": "open()/read_text()/write_text() 未指定 encoding 参数。Python 3.15 默认 UTF-8，建议显式声明 encoding='utf-8'。",
                "fix": "添加 encoding='utf-8' 参数",
            },
        ],
        "soft_deprecated": [
            {
                "pattern": r"re\.match\(",
                "check": lambda path, line: "re.match(" in line,
                "severity": "info",
                "message": "re.match() 在 Python 3.15+ 被标记为软弃用 (soft-deprecated)。优先使用 re.prefixmatch() 或 re.fullmatch()。",
                "fix": "若语义为全匹配则用 re.fullmatch()；若语义为前缀匹配则用 re.prefixmatch()(需 Python ≥ 3.15)",
            },
        ],
    },
}


def scan_file(file_path: Path, target_version: str) -> list[dict]:
    results = []
    rules = DEPRECATION_RULES.get(target_version, {})
    if not rules:
        return results

    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return results

    lines = content.split("\n")
    for i, line in enumerate(lines, start=1):
        for category, items in rules.items():
            for rule in items:
                if rule["check"](file_path, line):
                    results.append(
                        {
                            "file": str(file_path.relative_to(PROJECT_ROOT)),
                            "line": i,
                            "line_content": line.strip(),
                            "severity": rule["severity"],
                            "category": category,
                            "message": rule["message"],
                            "fix": rule.get("fix", ""),
                        }
                    )

    return results


def main():
    target_version = "3.15"
    if "--target-version" in sys.argv:
        idx = sys.argv.index("--target-version")
        if idx + 1 < len(sys.argv):
            target_version = sys.argv[idx + 1]

    print(f"🔍 Python {target_version} 合规性扫描")
    print(f"   扫描目录: {PROJECT_ROOT}")
    print()

    exclude_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".tox"}
    total_files = 0
    all_results = []

    for py_file in PROJECT_ROOT.rglob("*.py"):
        parts = set(py_file.parts)
        if parts & exclude_dirs:
            continue
        total_files += 1
        results = scan_file(py_file, target_version)
        all_results.extend(results)

    severity_counts = {}
    for r in all_results:
        severity_counts[r["severity"]] = severity_counts.get(r["severity"], 0) + 1

    print(f"   扫描文件: {total_files}")
    print(f"   发现问题: {len(all_results)}")
    for sev, count in sorted(severity_counts.items()):
        label = {"critical": "Critical", "warning": "Warning", "info": "Info"}.get(
            sev, sev
        )
        print(f"     {label}: {count}")
    print()

    if all_results:
        for r in sorted(all_results, key=lambda x: (x["file"], x["line"])):
            print(f"  [{r['file']}:L{r['line']}] [{r['category']}] [{r['severity']}]")
            print(f"    {r['message']}")
            if r["fix"]:
                print(f"    修复: {r['fix']}")
            print()

    exit_code = 1 if any(r["severity"] == "critical" for r in all_results) else 0
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
