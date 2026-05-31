"""``world init`` 子命令：脚手架生成器。

从模板生成 AGENTS.md + .agents/ 最小骨架，让新项目零配置启动。
这是 AgentForge 的 "npm init" 等价物——用户接触的第一个命令。

示例::

    $ world init --name my-awesome-project
    已创建: AGENTS.md
    已创建: .agents/world.toml
    已创建: .agents/rules/
    已创建: .agents/skills/
    已创建: .agents/docs/

    ✨ 项目已就绪！下一步：
      - 编辑 AGENTS.md 定制你的全局契约
      - 编辑 .agents/world.toml 声明项目元信息
      - 运行 world status 查看当前状态
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def _find_starter_template() -> Path | None:
    """从当前目录向上逐级查找 ``.agents/templates/starter/``。

    优先使用项目内的模板（保证模板内容与当前 AgentForge 版本一致）。

    Returns:
        找到时返回模板目录的绝对路径，否则返回 ``None``。
    """
    current = Path.cwd().resolve()
    for directory in [current, *current.parents]:
        candidate = directory / ".agents" / "templates" / "starter"
        if candidate.is_dir():
            # 确认关键文件存在
            ag_md = candidate / "AGENTS.md"
            world_toml = candidate / "world.toml"
            if ag_md.is_file() and world_toml.is_file():
                return candidate
    return None


_EMBEDDED_AGENTS_MD = """\
# 🤖 智能体全局契约 (AGENTS Manifest)

> 本文件兼容 AGENTS.md 开放标准——OpenAI Codex、Cursor、Copilot 等 30+ 工具原生支持。
> AgentForge 扩展（.agents/ 目录、world.toml）完全可选，零依赖即可使用本文件。

## 全局核心规则

- **沟通语言**：使用中文与用户交流。
- **按需读取**：执行特定领域任务前，只读取与当前任务直接相关的 `.agents/` 规范。
- **代码修改**：遵循"约定优于配置"，优先参考现有代码风格和项目架构。

## 上下文路由

遇到以下任务时，先读取对应规范，再执行任务。

| 任务类型 | 必读入口 |
|---|---|
| Python 开发 | `.agents/rules/python.md` |
| 前端开发 | `.agents/rules/frontend.md` |
| 后端开发 | `.agents/rules/backend.md` |
| 文档治理 | `.agents/rules/documentation.md` |
"""

_EMBEDDED_WORLD_TOML_TEMPLATE = """\
# world.toml — AgentForge 世界声明式描述
# Spec v0.2 Layer 1: Project Protocol (最小格式)

[world]
name = "{name}"
version = "0.1.0"
description = "项目简介"
"""


def _generate(
    target: Path,
    name: str,
    template_dir: Path | None,
) -> int:
    """在目标目录生成 AGENTS.md + .agents/ 骨架。

    Args:
        target: 目标项目根目录（将在此创建文件）。
        name: 项目名称（kebab-case），写入 world.toml 的 ``name`` 字段。
        template_dir: 模板目录路径，为 ``None`` 时使用内嵌最小模板。

    Returns:
        退出码：``0`` 表示成功。
    """
    agents_dir = target / ".agents"

    # 防止覆盖已有项目
    existing = []
    if (target / "AGENTS.md").exists():
        existing.append("AGENTS.md")
    if agents_dir.exists():
        existing.append(".agents/")
    if existing:
        print(
            f"错误：目标目录已存在 {' 和 '.join(existing)}，"
            f"请选择空目录或使用 --force 强制覆盖",
            file=sys.stderr,
        )
        return 1

    # 确保目标目录存在
    target.mkdir(parents=True, exist_ok=True)

    created: list[str] = []

    # 1. 生成 AGENTS.md
    if template_dir is not None:
        shutil.copy2(template_dir / "AGENTS.md", target / "AGENTS.md")
    else:
        (target / "AGENTS.md").write_text(_EMBEDDED_AGENTS_MD, encoding="utf-8")
    created.append("AGENTS.md")

    # 2. 生成 .agents/ 目录及其内容
    agents_dir.mkdir(exist_ok=True)

    # world.toml
    if template_dir is not None:
        shutil.copy2(template_dir / "world.toml", agents_dir / "world.toml")
        # 替换项目名称
        wt_path = agents_dir / "world.toml"
        content = wt_path.read_text(encoding="utf-8")
        content = content.replace('name = "my-project"', f'name = "{name}"')
        wt_path.write_text(content, encoding="utf-8")
    else:
        (agents_dir / "world.toml").write_text(
            _EMBEDDED_WORLD_TOML_TEMPLATE.format(name=name),
            encoding="utf-8",
        )
    created.append(".agents/world.toml")

    # rules/
    rules_dir = agents_dir / "rules"
    rules_dir.mkdir(exist_ok=True)
    (rules_dir / ".gitkeep").touch()
    created.append(".agents/rules/")

    # skills/
    skills_dir = agents_dir / "skills"
    skills_dir.mkdir(exist_ok=True)
    (skills_dir / ".gitkeep").touch()
    created.append(".agents/skills/")

    # docs/
    docs_dir = agents_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / ".gitkeep").touch()
    created.append(".agents/docs/")

    # 输出结果
    for item in created:
        print(f"  已创建: {item}")

    print()
    print(f"  ✨ 项目 '{name}' 已就绪！下一步：")
    print("    - 编辑 AGENTS.md 定制你的全局契约")
    print("    - 编辑 .agents/world.toml 声明项目元信息")
    print("    - 运行 world guide 获取 Fragment 推荐")
    print(
        "    - 运行 world fragment init <name> --from-rules .agents/rules/ 将规则打包为 Fragment"
    )
    print("    - 运行 world status 查看当前状态")
    print("    - 查看规范: specs/agentforge-spec-v0.2.md 了解三层架构")
    print("    - 查看治理: GOVERNANCE.md 了解如何参与标准制定")
    return 0


def register_init_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """注册 ``init`` 子命令到给定的 subparsers。

    Args:
        subparsers: argparse 的子命令注册器。
    """
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "init",
        help="生成 AGENTS.md + .agents/ 项目骨架",
        description=(
            "从模板生成 AGENTS.md + .agents/ 最小骨架。新项目零配置启动的唯一命令。"
        ),
    )
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        default=None,
        help="项目名称（kebab-case），默认使用目标目录名",
    )
    parser.add_argument(
        "--target",
        "-t",
        type=str,
        default=".",
        help="目标项目目录（默认当前目录）",
    )
    parser.set_defaults(handler=handle_init)


def handle_init(args: argparse.Namespace) -> int:
    """执行 ``world init`` 命令逻辑。

    Args:
        args: 由 argparse 解析的命名空间。

    Returns:
        退出码：``0`` 表示成功，``1`` 表示错误。
    """
    target = Path(args.target).resolve()
    name = args.name or target.name

    # 校验项目名称
    if not name or name == ".":
        print(
            "错误：无法推断项目名称，请使用 --name 显式指定",
            file=sys.stderr,
        )
        return 1

    template_dir = _find_starter_template()
    if template_dir is not None:
        print(f"  使用模板: {template_dir}")
    else:
        print("  使用内嵌最小模板（未找到 .agents/templates/starter/）")

    return _generate(target, name, template_dir)
