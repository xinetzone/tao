from __future__ import annotations

import re
import sys
from pathlib import Path
import tomllib

REQUIRED_SECTIONS = [
    ("Skill ID/Name", r"(?:Skill\s*(?:ID|Name|唯一标识)|Name)" ),
    ("Description", r"(?:Description|功能描述|功能|用途|Summary)"),
    ("I/O Parameters", r"(?:I/?O\s*Parameters?|Input|Output|输入|输出|Parameters?)"),
    ("Dependencies", r"(?:Dependencies?|依赖|依赖项|Requirements?)"),
    ("Deployment", r"(?:Deployment|部署|Install|安装|Setup|配置)"),
    ("Error Handling", r"(?:Error\s*Handling|错误|异常|handling)"),
    ("Changelog", r"(?:Changelog|版本|Version|History|变更|更新记录)"),
]


def load_config(project_root: Path) -> list[tuple[str, str]]:
    """从 .validate-config.toml 加载必填章节配置，不存在则使用默认值。"""
    config_file = project_root / ".agents" / "skills" / ".validate-config.toml"
    if not config_file.exists():
        return REQUIRED_SECTIONS

    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    sections = config.get("required_sections", {})
    if not sections:
        return REQUIRED_SECTIONS

    return [(name, pattern) for name, pattern in sections.items()]


def load_skip_names(project_root: Path) -> set[str]:
    skip_file = project_root / ".agents" / "skills" / ".validate-skip"
    skip_names: set[str] = set()
    if skip_file.exists():
        for line in skip_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                skip_names.add(line)
    return skip_names


def find_skill_dirs(project_root: Path) -> list[Path]:
    skills_root = project_root / ".agents" / "skills"
    if not skills_root.exists():
        return []

    skip_names = load_skip_names(project_root)

    return sorted(
        d
        for d in skills_root.iterdir()
        if d.is_dir()
        and not d.name.startswith(".")
        and d.name != "templates"
        and d.name not in skip_names
    )


def parse_skill_md_headers(skill_md_path: Path) -> set[str]:
    if not skill_md_path.exists():
        return set()
    content = skill_md_path.read_text(encoding="utf-8")
    headers = set()
    for line in content.splitlines():
        stripped = line.strip()
        match = re.match(r"^#{1,4}\s+(.+)", stripped)
        if match:
            headers.add(match.group(1).strip())
    return headers


def check_skill_md(skill_name: str, skill_dir: Path, required_sections: list[tuple[str, str]] | None = None) -> list[dict]:
    if required_sections is None:
        required_sections = REQUIRED_SECTIONS
    issues: list[dict] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        issues.append(
            {
                "severity": "MISSING",
                "item": "SKILL.md 存在性",
                "detail": f"{skill_name} 缺少 SKILL.md 文件",
            }
        )
        return issues

    headers = parse_skill_md_headers(skill_md)

    for section_name, pattern in required_sections:
        found = any(re.search(pattern, h) for h in headers)
        if not found:
            issues.append(
                {
                    "severity": "MISSING",
                    "item": "必填章节",
                    "detail": f"缺少「{section_name}」章节",
                }
            )

    if not issues:
        issues.append(
            {
                "severity": "PASS",
                "item": "SKILL.md 合规性",
                "detail": f"{skill_name} 的 SKILL.md 包含全部 {len(required_sections)} 个必填章节",
            }
        )
    else:
        remaining = len(required_sections) - sum(
            1
            for i in issues
            if i["severity"] == "MISSING" and i["item"] == "必填章节"
        )
        issues.insert(
            0,
            {
                "severity": "WARN",
                "item": "SKILL.md 合规性",
                "detail": f"{skill_name} 的 SKILL.md 包含 {remaining}/{len(required_sections)} 个必填章节",
            },
        )

    return issues


def run(project_root: Path) -> dict[str, list[dict]]:
    skill_dirs = find_skill_dirs(project_root)
    required_sections = load_config(project_root)
    results: dict[str, list[dict]] = {}

    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        results[skill_name] = check_skill_md(skill_name, skill_dir, required_sections)

    return results


def print_report(results: dict[str, list[dict]]) -> None:
    severity_order = {"MISSING": 0, "WARN": 1, "PASS": 2}

    for skill_name, issues in sorted(results.items()):
        print(f"\n## {skill_name}")
        sorted_issues = sorted(issues, key=lambda i: severity_order.get(i["severity"], 3))
        for issue in sorted_issues:
            tag = issue["severity"]
            print(f"  [{tag}] {issue['item']}: {issue['detail']}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[3]
    results = run(project_root)

    if not results:
        print("未找到任何 .agents/skills/ 下的技能目录。")
        return 0

    print("技能 SKILL.md 合规性校验报告")
    print("=" * 40)
    print_report(results)

    skip_names = load_skip_names(project_root)
    if skip_names:
        print("\n跳过的技能（见 .agents/skills/.validate-skip）：")
        for name in sorted(skip_names):
            print(f"  - {name}")

    exit_code = 0
    for skill_name, issues in results.items():
        if any(i["severity"] == "MISSING" for i in issues):
            exit_code = 1
            break

    print(f"\n校验完成，退出码 {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
