from __future__ import annotations

import re
import sys
from pathlib import Path

CHECK_RULES = [
    {
        "source": ".agents/docs/references/knowledge-driven-exploration-protocol.md",
        "description": "协议页引用完整性",
        "must_contain": [
            "dao-scenario-card-template",
            "knowledge-driven-exploration-spec-template",
            "knowledge-driven-exploration-workbench-template",
            "knowledge-driven-exploration-retrospective-template",
            "dao-scenario-catalog",
            "exploration-knowledge-loop-pilot",
        ],
    },
    {
        "source": ".agents/docs/references/dao-scenario-catalog.md",
        "description": "场景目录引用完整性",
        "must_contain": [
            "knowledge-driven-exploration-protocol",
            "dao-business-mapping-framework",
            "dao-scenario-card-template",
        ],
    },
    {
        "source": ".agents/docs/templates/knowledge-driven-exploration-workbench-template.md",
        "description": "工作台模板引用完整性",
        "must_contain": [
            "spec.md",
            "tasks.md",
            "checklist.md",
            "Expected Evidence",
            "复盘包含至少一个可执行回流动作",
        ],
    },
    {
        "source": ".agents/docs/templates/knowledge-driven-exploration-retrospective-template.md",
        "description": "复盘模板引用完整性",
        "must_contain": [
            "Reused Foundation",
            "Friction Points",
            "Upgrade Recommendations",
            "Next Action",
        ],
    },
]


def check_file_references(project_root: Path, rule: dict) -> list[dict]:
    issues: list[dict] = []
    source_path = project_root / rule["source"]

    if not source_path.exists():
        issues.append(
            {
                "severity": "MISSING",
                "item": rule["description"],
                "detail": f"源文件不存在：{rule['source']}",
            }
        )
        return issues

    content = source_path.read_text(encoding="utf-8")

    for keyword in rule["must_contain"]:
        if keyword not in content:
            issues.append(
                {
                    "severity": "WARN",
                    "item": rule["description"],
                    "detail": f"未找到关键词「{keyword}」",
                }
            )

    if not issues:
        issues.append(
            {
                "severity": "PASS",
                "item": rule["description"],
                "detail": "所有关键词引用均存在",
            }
        )

    return issues


def check_cross_refs(project_root: Path) -> list[dict]:
    issues: list[dict] = []
    protocol_path = (
        project_root
        / ".agents"
        / "docs"
        / "references"
        / "knowledge-driven-exploration-protocol.md"
    )

    if not protocol_path.exists():
        issues.append(
            {
                "severity": "MISSING",
                "item": "交叉引用",
                "detail": "协议页不存在，无法检查交叉引用",
            }
        )
        return issues

    content = protocol_path.read_text(encoding="utf-8")
    protocol_dir = protocol_path.parent

    template_refs = re.findall(r"\[`([^`]+)`\]\(([^)]+)\)", content)
    resolved_count = 0
    failed_count = 0
    for name, path_ref in template_refs:
        if path_ref.startswith("http://") or path_ref.startswith("https://"):
            continue
        absolute = _resolve_relative(project_root, protocol_dir, path_ref)
        if not absolute.exists():
            failed_count += 1
            issues.append(
                {
                    "severity": "WARN",
                    "item": "交叉引用失效",
                    "detail": f"引用「{name}」→ {path_ref} 不存在",
                }
            )
        else:
            resolved_count += 1

    total = resolved_count + failed_count
    if not issues:
        issues.append(
            {
                "severity": "PASS",
                "item": "交叉引用",
                "detail": f"协议页中 {total} 个相对引用全部有效",
            }
        )

    return issues


def _resolve_relative(project_root: Path, source_dir: Path, ref: str) -> Path:
    normalized = ref.replace("\\", "/")
    if normalized.startswith("/"):
        return project_root / normalized.lstrip("/")
    return (source_dir / normalized).resolve()


def run(project_root: Path) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}

    for rule in CHECK_RULES:
        source = rule["source"]
        results[source] = check_file_references(project_root, rule)

    results["协议页交叉引用有效性"] = check_cross_refs(project_root)

    return results


def print_report(results: dict[str, list[dict]]) -> None:
    severity_order = {"MISSING": 0, "WARN": 1, "PASS": 2}

    for source, issues in sorted(results.items()):
        print(f"\n## {source}")
        sorted_issues = sorted(issues, key=lambda i: severity_order.get(i["severity"], 3))
        for issue in sorted_issues:
            tag = issue["severity"]
            print(f"  [{tag}] {issue['item']}: {issue['detail']}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[3]
    results = run(project_root)
    print("引用完整性校验报告")
    print("=" * 40)
    print_report(results)

    exit_code = 0
    for source, issues in results.items():
        if any(i["severity"] == "MISSING" for i in issues):
            exit_code = 1
            break

    print(f"\n校验完成，退出码 {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
