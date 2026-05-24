from __future__ import annotations

import re
import sys
from pathlib import Path

EXPECTED_WORKBENCH_FILES = ("spec.md", "tasks.md", "checklist.md")

REQUIRED_CHECKLIST_ITEMS = [
    "场景卡已完成并字段完整",
    "spec 已完成并边界清晰",
    "plan 已完成并可执行",
    "至少完成一次最小验证",
    "已输出复盘并指定回流动作",
    "复盘包含至少一个可执行回流动作",
    "预期证据已完整指向协议、场景、工作台、复盘与回流动作",
]

REQUIRED_TASK_SECTIONS = [
    "校验场景卡",
    "确认 spec",
    "生成 checklist",
    "验证",
    "复盘",
    "回流",
]


def find_spec_dirs(project_root: Path) -> list[Path]:
    specs_root = project_root / ".trae" / "specs"
    if not specs_root.exists():
        return []
    return sorted(
        d for d in specs_root.iterdir() if d.is_dir() and not d.name.startswith(".")
    )


def check_files_exist(spec_dir: Path) -> list[str]:
    missing = []
    for filename in EXPECTED_WORKBENCH_FILES:
        if not (spec_dir / filename).exists():
            missing.append(filename)
    return missing


def parse_checklist_statuses(spec_dir: Path) -> dict[str, str]:
    path = spec_dir / "checklist.md"
    if not path.exists():
        return {}
    statuses = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- [x]"):
            item = stripped[5:].strip()
            statuses[item] = "x"
        elif stripped.startswith("- [ ]"):
            item = stripped[5:].strip()
            statuses[item] = " "
    return statuses


def parse_tasks_statuses(spec_dir: Path) -> dict[str, str]:
    path = spec_dir / "tasks.md"
    if not path.exists():
        return {}
    statuses = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        match = re.match(r"- \[(.)\]\s+(Task\s*\d+:?.+)", stripped)
        if match:
            statuses[match.group(2).strip()] = match.group(1)
    return statuses


def check_checklist_completeness(statuses: dict[str, str]) -> list[str]:
    warnings = []
    for item in REQUIRED_CHECKLIST_ITEMS:
        found = None
        for checklist_item in statuses:
            if item in checklist_item:
                found = checklist_item
                break
        if found is None:
            warnings.append(f"MISSING: checklist 缺少必要项「{item}」")
        elif statuses[found] == " ":
            warnings.append(f"WARN: checklist 项「{found}」未勾选")
    return warnings


def check_tasks_consistency(
    tasks_statuses: dict[str, str], checklist_statuses: dict[str, str]
) -> list[str]:
    warnings = []
    for task, ts in tasks_statuses.items():
        if ts == "x" and "以上为已验证" in task:
            continue
        task_keywords = _extract_keywords(task)
        matched = False
        for ci in checklist_statuses:
            if any(kw in ci for kw in task_keywords if len(kw) >= 3):
                matched = True
                break
        if not matched and len(task_keywords) > 0:
            pass
    return warnings


def _extract_keywords(task: str) -> list[str]:
    cleaned = re.sub(r"[：:].*", "", task)
    cleaned = re.sub(r"Task\s*\d+\s*[:-]?\s*", "", cleaned)
    return [w for w in re.split(r"[^\w\u4e00-\u9fff]+", cleaned) if w]


def run(project_root: Path) -> dict[str, list[dict]]:
    spec_dirs = find_spec_dirs(project_root)
    results: dict[str, list[dict]] = {}

    for spec_dir in spec_dirs:
        topic = spec_dir.name
        issues: list[dict] = []

        missing_files = check_files_exist(spec_dir)
        for mf in missing_files:
            issues.append(
                {"severity": "MISSING", "item": f"工作台文件缺失", "detail": mf}
            )

        checklist_statuses = parse_checklist_statuses(spec_dir)
        checklist_warnings = check_checklist_completeness(checklist_statuses)
        for w in checklist_warnings:
            severity = "MISSING" if w.startswith("MISSING:") else "WARN"
            detail = w.split(": ", 1)[1] if ": " in w else w
            issues.append({"severity": severity, "item": "checklist 完整性", "detail": detail})

        tasks_statuses = parse_tasks_statuses(spec_dir)
        tasks_done = sum(1 for v in tasks_statuses.values() if v == "x")
        tasks_total = len(tasks_statuses)

        if tasks_total > 0:
            open_tasks = [t for t, s in tasks_statuses.items() if s == " "]
            if open_tasks:
                issues.append(
                    {
                        "severity": "WARN",
                        "item": "tasks 进度",
                        "detail": f"{tasks_done}/{tasks_total} 已完成，未完成：{', '.join(open_tasks[:3])}",
                    }
                )
            else:
                issues.append(
                    {
                        "severity": "PASS",
                        "item": "tasks 进度",
                        "detail": f"{tasks_done}/{tasks_total} 全部完成",
                    }
                )

        if not issues:
            issues.append(
                {"severity": "PASS", "item": "工作台整体", "detail": "所有检查通过"}
            )

        results[topic] = issues

    return results


def print_report(results: dict[str, list[dict]]) -> None:
    severity_order = {"MISSING": 0, "WARN": 1, "PASS": 2}

    for topic, issues in sorted(results.items()):
        print(f"\n## {topic}")
        sorted_issues = sorted(issues, key=lambda i: severity_order.get(i["severity"], 3))
        for issue in sorted_issues:
            tag = issue["severity"]
            print(f"  [{tag}] {issue['item']}: {issue['detail']}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[3]
    results = run(project_root)

    if not results:
        print("未找到任何 .trae/specs/ 下的探索工作台目录。")
        return 0

    print("探索工作台完整性校验报告")
    print("=" * 40)
    print_report(results)

    exit_code = 0
    for topic, issues in results.items():
        if any(i["severity"] == "MISSING" for i in issues):
            exit_code = 1
            break

    print(f"\n校验完成，退出码 {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
