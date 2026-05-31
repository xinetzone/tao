from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

# 严格模式（strict）下与必填同等的最小集
REQUIRED_SECTIONS_MIN = [
    ("Skill ID/Name", r"(?:Skill\s*(?:ID|Name|唯一标识)|Name)"),
    ("Description", r"(?:Description|功能描述|功能|用途|Summary)"),
]

# 推荐章节：strict 模式下视为必填，relaxed 模式下仅产生 WARN
RECOMMENDED_REQUIRED_SECTIONS = [
    ("I/O Parameters", r"(?:I/?O\s*Parameters?|Input|Output|输入|输出|Parameters?)"),
    ("Dependencies", r"(?:Dependencies?|依赖|依赖项|Requirements?)"),
    ("Deployment", r"(?:Deployment|部署|Install|安装|Setup|配置)"),
    ("Error Handling", r"(?:Error\s*Handling|错误|异常|handling)"),
    ("Changelog", r"(?:Changelog|版本|Version|History|变更|更新记录)"),
]

# 向后兼容：strict 模式下的全量必填章节（老调用点可能仍引用此常量）
REQUIRED_SECTIONS = REQUIRED_SECTIONS_MIN + RECOMMENDED_REQUIRED_SECTIONS

# 建议章节（两种模式均不强制，仅 WARN）
RECOMMENDED_SECTIONS = [
    ("快速开始", r"(?:Quick\s*Start|快速开始|入门|使用方法)"),
    ("执行流程", r"(?:Execution\s*Flow|执行流程|工作流程|调用流程)"),
    ("最佳实践", r"(?:Best\s*Practices?|最佳实践|注意事项|FAQ)"),
]

VALID_MODES = ("strict", "relaxed")

# 技能目录预期文件结构
# tests/ 与 evals/ 为等价关系：evals/ 遵循 agentskills.io 标准命名
EXPECTED_STRUCTURE = {
    "scripts": ["*.py"],
    "tests": ["*.py"],
    "evals": ["*.py", "*.json"],
}


def load_config(
    project_root: Path,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], str]:
    """从 .validate-config.toml 加载校验配置。

    返回:
        (required_sections, recommended_required_sections, default_mode)
        - required_sections: 两种模式均强制的章节
        - recommended_required_sections: strict 模式下必填、relaxed 模式下推荐的章节
        - default_mode: 配置中的默认模式（strict / relaxed）
    """
    config_file = project_root / ".agents" / "skills" / ".validate-config.toml"
    if not config_file.exists():
        return REQUIRED_SECTIONS_MIN, RECOMMENDED_REQUIRED_SECTIONS, "strict"

    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    required_raw = config.get("required_sections", {})
    recommended_raw = config.get("recommended_sections", {})
    mode_cfg = config.get("mode", {})
    default_mode = str(mode_cfg.get("default", "strict")).lower()
    if default_mode not in VALID_MODES:
        default_mode = "strict"

    if required_raw or recommended_raw:
        required = (
            [(n, p) for n, p in required_raw.items()]
            if required_raw
            else list(REQUIRED_SECTIONS_MIN)
        )
        recommended = (
            [(n, p) for n, p in recommended_raw.items()] if recommended_raw else []
        )
        return required, recommended, default_mode

    # 旧版配置兼容：仅提供 required_sections 且包含全部 7 项时作为 strict 源
    return REQUIRED_SECTIONS_MIN, RECOMMENDED_REQUIRED_SECTIONS, default_mode


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


def check_markdown_quality(content: str) -> list[dict]:
    """检查 Markdown 质量问题"""
    issues = []

    # 检查中文标题是否有显式锚点
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#") and any(
            chinese_char in line for chinese_char in "一-龥"
        ):
            if not re.match(r"^\(#.*\)=\s*#", line):
                # 检查前一行是否有锚点定义
                if i == 0 or not lines[i - 1].strip().startswith("("):
                    issues.append(
                        {
                            "severity": "WARN",
                            "item": "Markdown 质量",
                            "detail": f"中文标题建议添加显式锚点: {line.strip()}",
                        }
                    )

    # 检查链接有效性（简单检查格式）
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for match in link_pattern.finditer(content):
        link_text, link_url = match.groups()
        if not link_url.startswith(("http://", "https://", "/", "./", "../")):
            # 相对路径但不在 docs 树内
            if not link_url.startswith("references/") and not link_url.startswith(
                "evals/"
            ):
                issues.append(
                    {
                        "severity": "WARN",
                        "item": "链接格式",
                        "detail": f"潜在无效链接: [{link_text}]({link_url})",
                    }
                )

    # 检查 H1 数量（应该只有一个）
    h1_count = sum(
        1
        for line in lines
        if line.startswith("# ") and len(line.lstrip("#").strip()) > 0
    )
    if h1_count != 1:
        issues.append(
            {
                "severity": "WARN",
                "item": "标题结构",
                "detail": f"发现 {h1_count} 个 H1 标题，建议只有一个主标题",
            }
        )

    return issues


def check_skill_directory(skill_dir: Path) -> list[dict]:
    """检查技能目录结构"""
    issues = []

    # 检查 scripts 目录
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        py_files = list(scripts_dir.glob("*.py"))
        if not py_files:
            issues.append(
                {
                    "severity": "WARN",
                    "item": "脚本文件",
                    "detail": "scripts/ 目录为空，建议添加技能实现脚本",
                }
            )

    # 检查是否有测试文件：tests/ 与 evals/ 等价（agentskills.io 标准使用 evals/）
    has_tests = (
        any((skill_dir / "tests").glob("*.py"))
        or any((skill_dir / "evals").glob("*.py"))
        or any((skill_dir / "evals").glob("*.json"))
        or any(skill_dir.glob("test_*.py"))
    )
    if not has_tests:
        issues.append(
            {
                "severity": "WARN",
                "item": "测试覆盖",
                "detail": "建议添加测试文件以保障技能质量（tests/ 或 evals/ 均可）",
            }
        )

    return issues


def check_skill_md(
    skill_name: str,
    skill_dir: Path,
    required_sections: list[tuple[str, str]] | None = None,
    recommended_required_sections: list[tuple[str, str]] | None = None,
    mode: str = "strict",
) -> list[dict]:
    """校验单个 SKILL.md。

    Args:
        required_sections: 两种模式均强制的最小集。
        recommended_required_sections: strict 模式必填、relaxed 模式仅 WARN 的章节。
            为保持向后兼容，若未传入：
              - 当 required_sections 长度 == REQUIRED_SECTIONS（老版合并调用）时，以空列表处理；
              - 否则默认采用 RECOMMENDED_REQUIRED_SECTIONS。
        mode: "strict" 或 "relaxed"。
    """
    if required_sections is None:
        required_sections = REQUIRED_SECTIONS_MIN
    if recommended_required_sections is None:
        # 老调用点传入合并后的 REQUIRED_SECTIONS（含 7 项）时，避免重复计算
        if len(required_sections) >= len(REQUIRED_SECTIONS):
            recommended_required_sections = []
        else:
            recommended_required_sections = list(RECOMMENDED_REQUIRED_SECTIONS)

    if mode not in VALID_MODES:
        mode = "strict"

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

    content = skill_md.read_text(encoding="utf-8")
    headers = parse_skill_md_headers(skill_md)

    # 检查必填章节（两种模式均 MISSING）
    missing_required = 0
    for section_name, pattern in required_sections:
        found = any(re.search(pattern, h) for h in headers)
        if not found:
            missing_required += 1
            issues.append(
                {
                    "severity": "MISSING",
                    "item": "必填章节",
                    "detail": f"缺少「{section_name}」章节",
                }
            )

    # 检查推荐必填章节：strict → MISSING，relaxed → WARN
    rec_missing = 0
    rec_severity = "MISSING" if mode == "strict" else "WARN"
    rec_item = "必填章节" if mode == "strict" else "推荐章节"
    for section_name, pattern in recommended_required_sections:
        found = any(re.search(pattern, h) for h in headers)
        if not found:
            rec_missing += 1
            issues.append(
                {
                    "severity": rec_severity,
                    "item": rec_item,
                    "detail": f"缺少「{section_name}」章节"
                    + ("" if mode == "strict" else "（relaxed 模式仅提示）"),
                }
            )

    # 检查建议章节（只警告，两种模式一致）
    recommended_found = 0
    for _section_name, pattern in RECOMMENDED_SECTIONS:
        if any(re.search(pattern, h) for h in headers):
            recommended_found += 1

    if recommended_found < len(RECOMMENDED_SECTIONS):
        issues.append(
            {
                "severity": "WARN",
                "item": "建议章节",
                "detail": f"建议补充 {len(RECOMMENDED_SECTIONS) - recommended_found} 个建议章节（快速开始、执行流程、最佳实践）",
            }
        )

    # 检查 Markdown 质量
    quality_issues = check_markdown_quality(content)
    issues.extend(quality_issues)

    # 检查目录结构
    structure_issues = check_skill_directory(skill_dir)
    issues.extend(structure_issues)

    # 统计合规情况
    total_required = len(required_sections) + (
        len(recommended_required_sections) if mode == "strict" else 0
    )
    total_missing = missing_required + (rec_missing if mode == "strict" else 0)

    if not any(i["severity"] == "MISSING" for i in issues):
        issues.insert(
            0,
            {
                "severity": "PASS",
                "item": "SKILL.md 合规性",
                "detail": f"{skill_name} 通过全部 {total_required} 个必填章节校验（mode={mode}）",
            },
        )
    else:
        remaining = total_required - total_missing
        issues.insert(
            0,
            {
                "severity": "WARN",
                "item": "SKILL.md 合规性",
                "detail": f"{skill_name} 的 SKILL.md 包含 {remaining}/{total_required} 个必填章节（mode={mode}）",
            },
        )

    return issues


def run(project_root: Path, mode: str | None = None) -> dict[str, list[dict]]:
    """执行全量技能校验。

    Args:
        project_root: 项目根目录。
        mode: 校验模式（"strict" / "relaxed"）。None 时使用配置文件中的默认值。
    """
    skill_dirs = find_skill_dirs(project_root)
    required_sections, recommended_required_sections, default_mode = load_config(
        project_root
    )
    effective_mode = (mode or default_mode).lower()
    if effective_mode not in VALID_MODES:
        effective_mode = "strict"

    results: dict[str, list[dict]] = {}
    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        results[skill_name] = check_skill_md(
            skill_name,
            skill_dir,
            required_sections,
            recommended_required_sections,
            mode=effective_mode,
        )

    return results


def print_report(results: dict[str, list[dict]]) -> None:
    severity_order = {"MISSING": 0, "WARN": 1, "PASS": 2}

    for skill_name, issues in sorted(results.items()):
        print(f"\n## {skill_name}")
        sorted_issues = sorted(
            issues, key=lambda i: severity_order.get(i["severity"], 3)
        )
        for issue in sorted_issues:
            tag = issue["severity"]
            print(f"  [{tag}] {issue['item']}: {issue['detail']}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="技能 SKILL.md 合规性校验器（支持 strict / relaxed 双模式）",
    )
    parser.add_argument(
        "--mode",
        choices=list(VALID_MODES),
        default=None,
        help=(
            "校验模式：strict = 全部 7 章节必填（项目自有 Skills 默认）；"
            "relaxed = 仅 Name + Description 必填（与 agentskills.io 对齐）。"
            "未指定时使用 .validate-config.toml 中的默认值。"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project_root = Path(__file__).resolve().parents[3]
    results = run(project_root, mode=args.mode)

    if not results:
        print("未找到任何 .agents/skills/ 下的技能目录。")
        return 0

    _, _, default_mode = load_config(project_root)
    effective_mode = (args.mode or default_mode).lower()
    print(f"技能 SKILL.md 合规性校验报告（mode={effective_mode}）")
    print("=" * 40)
    print_report(results)

    skip_names = load_skip_names(project_root)
    if skip_names:
        print("\n跳过的技能（见 .agents/skills/.validate-skip）：")
        for name in sorted(skip_names):
            print(f"  - {name}")

    exit_code = 0
    for _skill_name, issues in results.items():
        if any(i["severity"] == "MISSING" for i in issues):
            exit_code = 1
            break

    print(f"\n校验完成，退出码 {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
