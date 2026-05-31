"""world guide — 项目结构诊断与 Fragment 推荐

分析当前项目的 world.toml 和目录结构，按项目类型推荐适用的 fragments，
打破 `world init` 后的静默期。
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _find_world_toml(start_path: Path) -> Path | None:
    """向上查找 world.toml，返回其目录路径。"""
    current = start_path.resolve()
    for _ in range(10):
        candidate = current / ".agents" / "world.toml"
        if candidate.exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _detect_project_type(project_root: Path) -> list[str]:
    """检测项目类型，返回类型标签列表。"""
    types = []

    # Python 项目
    if (project_root / "pyproject.toml").exists() or (
        project_root / "setup.py"
    ).exists():
        types.append("python")

    # Node.js 项目
    if (project_root / "package.json").exists():
        types.append("nodejs")

    # Rust 项目
    if (project_root / "Cargo.toml").exists():
        types.append("rust")

    # Go 项目
    if (project_root / "go.mod").exists():
        types.append("go")

    # Web 项目（检测常见前端配置）
    web_indicators = [
        "next.config",
        "vite.config",
        "webpack.config",
        "tailwind.config",
        "astro.config",
    ]
    for pattern in web_indicators:
        matches = list(project_root.glob(f"{pattern}.*"))
        if matches:
            if "web" not in types:
                types.append("web")
            break

    # 文档项目
    if (project_root / ".readthedocs.yml").exists() or (
        project_root / "mkdocs.yml"
    ).exists():
        types.append("docs")

    # AgentForge 项目（自身检测）
    if (project_root / ".agents" / "world.toml").exists():
        types.append("agentforge")

    # Containerized
    if (project_root / "Containerfile").exists() or (
        project_root / "Dockerfile"
    ).exists():
        types.append("container")

    return types


# Fragment 推荐表
# 格式: { "type": str, "recommends": [{"name": str, "description": str, "url": str|None}] }
FRAGMENT_RECOMMENDATIONS = {
    "python": [
        {
            "name": "python-engineering",
            "description": "Python 工程规范：导入规则、类型注解、兼容性检查脚本",
            "url": "https://github.com/agentforge/registry-index/tree/main/fragments/py/python-engineering",
        },
        {
            "name": "python-testing",
            "description": "Python 测试规范：pytest 约定、测试边界、Mock 策略",
            "url": None,
        },
    ],
    "nodejs": [
        {
            "name": "node-engineering",
            "description": "Node.js 工程规范：包管理、ESLint/Prettier 配置、TypeScript 约定",
            "url": None,
        },
    ],
    "rust": [
        {
            "name": "rust-engineering",
            "description": "Rust 工程规范：clippy 规则、模块组织、unsafe 使用边界",
            "url": None,
        },
    ],
    "go": [
        {
            "name": "go-engineering",
            "description": "Go 工程规范：包命名、错误处理约定、并发模式",
            "url": None,
        },
    ],
    "web": [
        {
            "name": "web-frontend",
            "description": "前端开发规范：组件结构、状态管理、可访问性、响应式设计",
            "url": None,
        },
    ],
    "docs": [
        {
            "name": "documentation",
            "description": "文档治理规范：双轨分类、归档规则、同步机制",
            "url": None,
        },
    ],
    "container": [
        {
            "name": "containerization",
            "description": "容器化规范：镜像构建、多阶段构建、安全扫描",
            "url": None,
        },
    ],
    "agentforge": [
        {
            "name": "context-economy",
            "description": "上下文节省规则：token 优化、按需加载策略",
            "url": None,
        },
        {
            "name": "agent-collaboration",
            "description": "多智能体协作元模型：Team/Role/Agent 语义 + Handoff 约定",
            "url": None,
        },
    ],
}


def _print_guide(project_root: Path, types: list[str]):
    """打印引导信息。"""
    print(f"\n🔍 项目诊断: {project_root}")
    print(f"   检测类型: {', '.join(types) if types else '未识别'}")

    # 检查 world.toml 状态
    world_toml = project_root / ".agents" / "world.toml"
    if world_toml.exists():
        print("   world.toml: ✅ 已存在")
    else:
        print("   world.toml: ❌ 未找到 — 运行 `world init` 创建")

    # 检查已安装 fragments
    if world_toml.exists():
        content = world_toml.read_text(encoding="utf-8")
        import re

        frag_names = re.findall(r"^\[fragments\.(.+)\]", content, re.MULTILINE)
        if frag_names:
            print(f"   已安装 fragments: {', '.join(frag_names)}")
        else:
            print("   已安装 fragments: 无")

    # 推荐
    all_recommends = []
    seen = set()
    for t in types:
        if t in FRAGMENT_RECOMMENDATIONS:
            for rec in FRAGMENT_RECOMMENDATIONS[t]:
                if rec["name"] not in seen:
                    seen.add(rec["name"])
                    all_recommends.append(rec)

    if all_recommends:
        print("\n📋 推荐安装的 Fragments:")
        for rec in all_recommends:
            url_hint = f"  ({rec['url']})" if rec["url"] else ""
            print(f"   • {rec['name']}")
            print(f"     {rec['description']}{url_hint}")

        print("\n💡 安装命令: world fragment install <name>")
    else:
        print(
            "\n📋 暂无针对性推荐。使用 `world fragment search` 浏览所有可用 fragments。"
        )

    # 下一步
    print("\n📖 下一步:")
    if not world_toml.exists():
        print("   1. world init           — 创建项目骨架")
    print("   2. world fragment list    — 浏览可用 fragments")
    print("   3. world fragment install <name> — 安装 fragment")
    print("   4. 查看规范: specs/agentforge-spec-v0.2.md")
    print("   5. 了解治理: GOVERNANCE.md\n")


def handle_guide(args: argparse.Namespace) -> int:
    """world guide 入口处理函数。"""
    target = Path(args.target or ".").resolve()
    if not target.is_dir():
        target = target.parent

    project_root = _find_world_toml(target) or _find_world_toml(Path.cwd())
    if not project_root:
        # 无 world.toml — 对当前目录做检测
        project_root = target
        print("⚠️  未找到 world.toml — 显示项目基本诊断。")

    types = _detect_project_type(project_root)
    _print_guide(project_root, types)
    return 0


def register_guide_parser(subparsers: argparse._SubParsersAction) -> None:
    """注册 world guide 子命令。"""
    parser = subparsers.add_parser(
        "guide",
        help="项目结构诊断与 Fragment 推荐",
        description="分析当前项目的 world.toml 和目录结构，推荐适用的 fragments",
    )
    parser.add_argument(
        "--target",
        help="目标项目路径（默认为当前目录）",
        default=None,
    )
    parser.set_defaults(handle=handle_guide)
