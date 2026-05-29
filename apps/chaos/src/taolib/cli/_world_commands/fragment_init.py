"""world fragment init — 创建新 Fragment 或从已有规则打包

支持两种模式：
1. ``world fragment init <name>`` — 从零创建 Fragment 骨架
2. ``world fragment init <name> --from-rules path/...`` — 将已有规则目录打包为 Fragment
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional


def _find_agents_dir(start_path: Path) -> Optional[Path]:
    """向上查找 .agents/ 目录。"""
    current = start_path.resolve()
    for _ in range(10):
        candidate = current / ".agents"
        if candidate.is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _init_from_scratch(project_root: Path, name: str, target_dir: Optional[str]) -> int:
    """从零创建 Fragment 骨架。"""
    agents_dir = project_root / ".agents"
    if not agents_dir.is_dir():
        print("❌ 未找到 .agents/ 目录。请先运行 world init。")
        return 1

    # 确定 fragment 目录
    if target_dir:
        frag_dir = Path(target_dir).resolve()
    else:
        frag_dir = agents_dir / "fragments" / name

    frag_dir.mkdir(parents=True, exist_ok=True)

    # 创建 fragment.toml
    fragment_toml = frag_dir / "fragment.toml"
    if fragment_toml.exists():
        print(f"⚠️  {fragment_toml} 已存在，跳过创建。")
    else:
        fragment_toml.write_text(
            f"""# {name} — AgentForge Fragment

[fragment]
name = "{name}"
version = "0.1.0"
description = "TODO: 描述此 Fragment 的用途"
type = "extension"   # extension | meta | reference

[distribution]
homepage = ""
registry = ""

[includes]
rules = []
skills = []
scripts = []
references = []

[requires]
# 依赖的其他 fragments
# example = ">=1.0.0"
""",
            encoding="utf-8",
        )
        print(f"✅ 已创建 {fragment_toml}")

    # 创建 rules/ 目录
    rules_dir = frag_dir / "rules"
    rules_dir.mkdir(exist_ok=True)
    (rules_dir / ".gitkeep").touch()

    # 创建 skills/ 目录
    skills_dir = frag_dir / "skills"
    skills_dir.mkdir(exist_ok=True)
    (skills_dir / ".gitkeep").touch()

    print(f"✅ Fragment `{name}` 骨架已创建: {frag_dir}")
    print(f"\n💡 下一步:")
    print(f"   1. 编辑 {fragment_toml} 完善描述和依赖")
    print(f"   2. 将规则放入 {rules_dir}/")
    print(f"   3. world fragment publish {name}")
    return 0


def _init_from_rules(project_root: Path, name: str, rules_path: str) -> int:
    """从已有规则目录打包为 Fragment。"""
    agents_dir = project_root / ".agents"
    if not agents_dir.is_dir():
        print("❌ 未找到 .agents/ 目录。")
        return 1

    # 解析规则路径
    source_dir = Path(rules_path).resolve()
    if not source_dir.is_dir():
        print(f"❌ 路径不存在或不是目录: {source_dir}")
        return 1

    # 收集规则文件
    rule_files = []
    for pattern in ["*.md", "*.toml", "*.yaml", "*.json"]:
        rule_files.extend(source_dir.glob(pattern))

    if not rule_files:
        print(f"❌ {source_dir} 中未找到规则文件（*.md/*.toml/*.yaml/*.json）")
        return 1

    print(f"📦 从 {source_dir} 发现 {len(rule_files)} 个文件")

    # 确定 fragment 目录
    frag_dir = agents_dir / "fragments" / name
    frag_dir.mkdir(parents=True, exist_ok=True)

    # 计算相对路径
    rules_rel_dir = frag_dir / "rules"
    rules_rel_dir.mkdir(exist_ok=True)

    # 读取第一个规则文件尝试提取描述
    description = "从已有规则打包生成"
    for f in rule_files[:1]:
        content = f.read_text(encoding="utf-8")
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                description = line[:100]
                break

    # 收集文件列表
    relative_files = []
    try:
        for f in rule_files:
            rel = f.relative_to(project_root)
            target = rules_rel_dir / f.name
            content = f.read_text(encoding="utf-8")
            target.write_text(content, encoding="utf-8")
            relative_files.append(str(rel))
    except ValueError:
        # 文件不在 project_root 下
        for f in rule_files:
            target = rules_rel_dir / f.name
            content = f.read_text(encoding="utf-8")
            target.write_text(content, encoding="utf-8")
            relative_files.append(f"rules/{f.name}")

    # 创建 fragment.toml
    fragment_toml = frag_dir / "fragment.toml"
    file_list = "\n".join(f'    "{fn}",' for fn in relative_files)
    fragment_toml.write_text(
        f"""# {name} — AgentForge Fragment（从已有规则打包）

[fragment]
name = "{name}"
version = "0.1.0"
description = "{description}"
type = "extension"

[distribution]
homepage = ""
registry = ""

[includes]
rules = [
{file_list}
]
skills = []
scripts = []
references = []

[requires]
# 依赖的其他 fragments
""",
        encoding="utf-8",
    )

    print(f"\n✅ Fragment `{name}` 已打包: {frag_dir}")
    print(f"   包含 {len(rule_files)} 个规则文件:")
    for f in rule_files:
        print(f"   • {f.name}")
    print(f"\n💡 下一步: world fragment publish {name}")
    return 0


def handle_fragment_init(args: argparse.Namespace) -> int:
    """world fragment init 入口处理函数。"""
    name = args.name
    if not name:
        print("❌ 必须指定 Fragment 名称。")
        print("   用法: world fragment init <name> [--from-rules <path>]")
        return 1

    # 验证名称格式
    import re
    if not re.match(r"^[a-z0-9]([a-z0-9._-]*[a-z0-9])?$", name):
        print(f"❌ 无效的 Fragment 名称: {name}")
        print("   名称必须为 kebab-case，如 python-engineering")
        return 1

    target = Path(args.target or ".").resolve()
    if not target.is_dir():
        target = target.parent

    project_root = _find_agents_dir(target)
    if not project_root:
        print("❌ 未找到 .agents/ 目录。请先运行 world init。")
        return 1

    if args.from_rules:
        return _init_from_rules(project_root, name, args.from_rules)
    else:
        return _init_from_scratch(project_root, name, args.target)


def register_fragment_init_parser(subparsers: argparse._SubParsersAction) -> None:
    """注册 world fragment init 子命令。"""
    parser = subparsers.add_parser(
        "init",
        help="创建新 Fragment 或从已有规则打包",
        description="创建新 Fragment 骨架，或从已有规则目录打包为可发布 Fragment",
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="Fragment 名称（kebab-case）",
        default=None,
    )
    parser.add_argument(
        "--from-rules",
        help="从指定目录的规则文件打包（而非从零创建）",
        default=None,
        metavar="PATH",
    )
    parser.add_argument(
        "--target",
        help="目标项目路径（默认为当前目录）",
        default=None,
    )
    parser.set_defaults(handle=handle_fragment_init)
