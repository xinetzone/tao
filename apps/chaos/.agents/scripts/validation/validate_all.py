"""统一验证入口 - 运行所有验证脚本并生成汇总报告"""

from __future__ import annotations

import sys
from pathlib import Path

# 添加父目录到 sys.path 以支持模块导入
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

from validate_references import run as validate_references  # noqa: E402
from validate_retro_feedback import run as validate_retro_feedback  # noqa: E402
from validate_skill_md import run as validate_skill_md  # noqa: E402
from validate_workbench import run as validate_workbench  # noqa: E402


def print_summary_report(results: dict[str, dict[str, list[dict]]]) -> int:
    """打印汇总报告并返回退出码"""
    severity_order = {"MISSING": 0, "WARN": 1, "PASS": 2}
    exit_code = 0
    total_issues = 0
    total_pass = 0

    print("=" * 60)
    print("🎯 AgentForge 技能验证体系 - 综合校验报告")
    print("=" * 60)

    for validator_name, validator_results in results.items():
        print(f"\n📋 {validator_name}")
        print("-" * 40)

        if not validator_results:
            print("  (无数据)")
            continue

        for item_name, issues in sorted(validator_results.items()):
            sorted_issues = sorted(
                issues, key=lambda i: severity_order.get(i["severity"], 3)
            )

            has_issue = any(i["severity"] in ("MISSING", "WARN") for i in sorted_issues)
            status = (
                "❌"
                if any(i["severity"] == "MISSING" for i in sorted_issues)
                else "⚠️"
                if has_issue
                else "✅"
            )

            print(f"\n  {status} {item_name}")
            for issue in sorted_issues:
                tag = issue["severity"]
                if tag == "MISSING":
                    exit_code = 1
                    total_issues += 1
                    print(f"    ❌ [{tag}] {issue['item']}: {issue['detail']}")
                elif tag == "WARN":
                    exit_code = max(exit_code, 1)
                    total_issues += 1
                    print(f"    ⚠️ [{tag}] {issue['item']}: {issue['detail']}")
                else:
                    total_pass += 1
                    print(f"    ✓ [{tag}] {issue['item']}: {issue['detail']}")

    print("\n" + "=" * 60)
    print(f"📊 汇总结果: {total_pass} 项通过, {total_issues} 项问题")
    print("=" * 60)

    return exit_code


def main() -> int:
    project_root = Path(__file__).resolve().parents[3]

    print("🚀 正在运行技能验证体系综合校验...\n")

    results = {
        "技能 SKILL.md 合规性": validate_skill_md(project_root),
        "探索工作台完整性": validate_workbench(project_root),
        "复盘回流动作校验": validate_retro_feedback(project_root),
        "引用完整性": validate_references(project_root),
    }

    return print_summary_report(results)


if __name__ == "__main__":
    sys.exit(main())
