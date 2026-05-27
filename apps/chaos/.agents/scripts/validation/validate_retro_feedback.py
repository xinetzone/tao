from __future__ import annotations

import re
import sys
from pathlib import Path

NEXT_ACTION_HEADING = re.compile(r"Next\s*Action|下一步", re.IGNORECASE)
NEXT_ACTION_FALLBACK = re.compile(
    r"后续\s*(?:动作|步骤|行动|计划)|follow.?up\s*actions?", re.IGNORECASE
)

ACTION_PATTERNS = [
    (r"更新\S*(?:模板|规则|协议|场景目录|参考)", "回流动作: 资产更新"),
    (r"升级\S*(?:模板|规则|规范)", "回流动作: 资产升级"),
    (r"(?:新增|创建|建立)\S*(?:检查|校验|脚本|工具)", "回流动作: 工具建设"),
    (r"(?:进入|启动|开始)\S*(?:plan|探索|试点|任务)", "回流动作: 启动下一轮"),
    (r"(?:执行|完成)\S*(?:回溯|回写|同步)", "回流动作: 数据同步"),
]


def is_empty_action(text: str) -> bool:
    cleaned = re.sub(r"[#\-*>\s]", "", text)
    return len(cleaned) < 10


def find_next_actions(content: str) -> list[str]:
    lines = content.splitlines()
    in_section = False
    actions: list[str] = []
    buffer: list[str] = []

    for _i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") and NEXT_ACTION_HEADING.search(stripped):
            in_section = True
            buffer = []
            continue

        if in_section:
            if stripped.startswith("#") and len(stripped.lstrip("#").strip()) > 0:
                if not NEXT_ACTION_HEADING.search(stripped):
                    in_section = False
                    combined = "\n".join(buffer).strip()
                    if combined and not is_empty_action(combined):
                        actions.append(combined)
                    continue

            if stripped.startswith("-"):
                action = stripped[1:].strip()
                if action and not is_empty_action(action):
                    actions.append(action)
            elif stripped and not is_empty_action(stripped):
                buffer.append(stripped)

    if in_section and buffer:
        combined = "\n".join(buffer).strip()
        if combined and not is_empty_action(combined):
            actions.append(combined)

    return actions


def check_retro(project_root: Path, retro_path: Path) -> list[dict]:
    issues: list[dict] = []
    retro_name = retro_path.stem

    content = retro_path.read_text(encoding="utf-8")
    has_next_action_section = bool(
        NEXT_ACTION_HEADING.search(content) or NEXT_ACTION_FALLBACK.search(content)
    )

    if not has_next_action_section:
        issues.append(
            {
                "severity": "MISSING",
                "item": "复盘结构",
                "detail": f"{retro_name} 缺少「Next Action / 下一步」章节",
            }
        )
        return issues

    actions = find_next_actions(content)

    if not actions:
        issues.append(
            {
                "severity": "WARN",
                "item": "回流动作",
                "detail": f"{retro_name} 的 Next Action 章节未找到可执行的动作描述",
            }
        )
        return issues

    categorized = {}
    for action in actions:
        matched = False
        for pattern, category in ACTION_PATTERNS:
            if re.search(pattern, action):
                categorized.setdefault(category, []).append(action)
                matched = True
                break
        if not matched:
            categorized.setdefault("回流动作: 其他", []).append(action)

    report = ", ".join(
        f"{cat}: {len(acts)}条" for cat, acts in sorted(categorized.items())
    )
    issues.append(
        {
            "severity": "PASS",
            "item": "回流动作",
            "detail": f"{retro_name} 包含 {len(actions)} 个回流动作（{report}）",
        }
    )

    return issues


def run(project_root: Path) -> dict[str, list[dict]]:
    retro_dir = project_root / ".agents" / "docs" / "superpowers" / "retrospectives"
    retros: dict[str, list[dict]] = {}

    if not retro_dir.exists():
        return retros

    for retro_path in sorted(retro_dir.glob("*.md")):
        retros[retro_path.name] = check_retro(project_root, retro_path)

    return retros


def print_report(retros: dict[str, list[dict]]) -> None:
    severity_order = {"MISSING": 0, "WARN": 1, "PASS": 2}
    total = len(retros)
    with_action = sum(
        1
        for issues in retros.values()
        if any(i["item"] == "回流动作" and i["severity"] == "PASS" for i in issues)
    )

    print(f"复盘回流动作存在性校验报告 ({with_action}/{total} 含回流动作)")
    print("=" * 60)

    for filename, issues in sorted(retros.items()):
        sorted_issues = sorted(
            issues, key=lambda i: severity_order.get(i["severity"], 3)
        )
        status = (
            "PASS" if all(i["severity"] == "PASS" for i in sorted_issues) else "ISSUE"
        )
        print(f"\n[{status}] {filename}")
        for issue in sorted_issues:
            tag = issue["severity"]
            print(f"    [{tag}] {issue['item']}: {issue['detail']}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[3]
    results = run(project_root)

    if not results:
        print("未找到任何复盘文件。")
        return 0

    print_report(results)

    exit_code = 0
    for _filename, issues in results.items():
        if any(i["severity"] == "MISSING" for i in issues):
            exit_code = 1
            break

    print(f"\n校验完成，退出码 {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
