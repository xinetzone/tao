"""验证 .agents/scripts/validate_roles.py 的角色扫描与字段兼容行为。"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tomllib


def _load_validate_roles_module():
    """从脚本路径加载 validate_roles 模块。"""

    script_path = (
        Path(__file__).resolve().parent.parent
        / ".agents"
        / "scripts"
        / "validate_roles.py"
    )
    spec = spec_from_file_location("validate_roles", script_path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validate_accepts_governance_role_frontmatter_in_nested_directory(tmp_path):
    """治理层角色在子目录中出现扩展 frontmatter 时也应通过校验。"""

    agents_root = tmp_path / ".agents"
    governance_dir = agents_root / "roles" / "governance"
    rules_dir = agents_root / "rules"
    docs_dir = agents_root / "docs" / "references"
    governance_dir.mkdir(parents=True)
    rules_dir.mkdir(parents=True)
    docs_dir.mkdir(parents=True)

    (rules_dir / "documentation.md").write_text("# documentation\n", encoding="utf-8")
    (rules_dir / "context-economy.md").write_text("# context\n", encoding="utf-8")
    (docs_dir / "agent-collaboration-metamodel.md").write_text(
        "# metamodel\n",
        encoding="utf-8",
    )
    (governance_dir / "collaboration-architect.md").write_text(
        """+++
id = "collaboration-architect"
domain = "governance+knowledge"
layer = "governance"

[bindings]
rules = ["rules/documentation.md", "rules/context-economy.md"]
references = ["docs/references/agent-collaboration-metamodel.md"]
skills = ["brainstorming", "writing-plans"]

[constraints]
rules_must_exist = true
non_goals_enforced = true

[non_goals]
items = ["不直接修改 skills/ 实现代码"]
+++

# Collaboration Architect

## Description

治理角色示例。

## Responsibilities

- 维护协作元模型。

## Non-Goals

- 不直接修改 `skills/` 实现代码
""",
        encoding="utf-8",
    )

    validate_roles = _load_validate_roles_module()

    errors, warnings, role_ids = validate_roles.validate(agents_root)

    assert errors == []
    assert warnings == []
    assert role_ids == ["collaboration-architect"]


def test_all_repository_role_files_declare_layer():
    """仓库中的每个角色文件都应显式声明 layer。"""

    roles_dir = Path(__file__).resolve().parent.parent / ".agents" / "roles"
    role_files = sorted(
        path for path in roles_dir.rglob("*.md") if path.is_file() and path.name != "README.md"
    )

    missing_layer = []
    for role_file in role_files:
        text = role_file.read_text(encoding="utf-8")
        frontmatter = text.split("+++", 2)[1]
        data = tomllib.loads(frontmatter)
        if "layer" not in data:
            missing_layer.append(role_file.relative_to(roles_dir).as_posix())

    assert missing_layer == []


def test_validate_rejects_role_when_layer_does_not_match_parent_directory(tmp_path):
    """角色所在目录与声明的 layer 不一致时应报错。"""

    agents_root = tmp_path / ".agents"
    engineering_dir = agents_root / "roles" / "engineering"
    rules_dir = agents_root / "rules"
    engineering_dir.mkdir(parents=True)
    rules_dir.mkdir(parents=True)

    (rules_dir / "backend.md").write_text("# backend\n", encoding="utf-8")
    (engineering_dir / "backend-dev.md").write_text(
        """+++
id = "backend-dev"
domain = "engineering"
layer = "governance"

[bindings]
rules = ["rules/backend.md"]
references = []
skills = []
+++

# Backend Dev

## Description

示例角色。

## Responsibilities

- 提供后端实现。

## Non-Goals

- 不负责前端实现。
""",
        encoding="utf-8",
    )

    validate_roles = _load_validate_roles_module()

    errors, warnings, role_ids = validate_roles.validate(agents_root)

    assert warnings == []
    assert role_ids == ["backend-dev"]
    assert errors == [
        "ERROR: role 'backend-dev' layer 'governance' does not match parent "
        "directory 'engineering'"
    ]


def test_validate_requires_non_goals_enforced_for_governance_roles(tmp_path):
    """governance/ 角色必须声明 constraints.non_goals_enforced = true。"""

    agents_root = tmp_path / ".agents"
    governance_dir = agents_root / "roles" / "governance"
    rules_dir = agents_root / "rules"
    docs_dir = agents_root / "docs" / "references"
    governance_dir.mkdir(parents=True)
    rules_dir.mkdir(parents=True)
    docs_dir.mkdir(parents=True)

    (rules_dir / "documentation.md").write_text("# doc\n", encoding="utf-8")
    (docs_dir / "metamodel.md").write_text("# meta\n", encoding="utf-8")
    (governance_dir / "loose-governor.md").write_text(
        """+++
id = "loose-governor"
domain = "governance"
layer = "governance"

[bindings]
rules = ["rules/documentation.md"]
references = ["docs/references/metamodel.md"]
skills = []
+++

# Loose Governor

## Description

治理型角色示例，但缺失硬约束。
""",
        encoding="utf-8",
    )

    validate_roles = _load_validate_roles_module()

    errors, warnings, role_ids = validate_roles.validate(agents_root)

    assert warnings == []
    assert role_ids == ["loose-governor"]
    assert any(
        "non_goals_enforced" in msg and "governance" in msg for msg in errors
    ), errors


def test_all_repository_governance_roles_have_non_goals_enforced_true():
    """仓库内 governance 角色必须显式开启 non_goals_enforced 硬约束。"""

    import tomllib
    from importlib.util import module_from_spec, spec_from_file_location

    repo_root = Path(__file__).resolve().parent.parent
    governance_dir = repo_root / ".agents" / "roles" / "governance"
    assert governance_dir.is_dir(), f"governance 目录不存在：{governance_dir}"

    spec = spec_from_file_location(
        "_validate_roles_for_repo",
        repo_root / ".agents" / "scripts" / "validate_roles.py",
    )
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    offenders: list[str] = []
    for role_file in sorted(governance_dir.glob("*.md")):
        if role_file.name == "README.md":
            continue
        text = role_file.read_text(encoding="utf-8")
        toml_text, _fm_err = module._extract_frontmatter(text)
        assert toml_text is not None
        data = tomllib.loads(toml_text)
        constraints = data.get("constraints", {})
        if not isinstance(constraints, dict):
            offenders.append(role_file.name)
            continue
        if constraints.get("non_goals_enforced") is not True:
            offenders.append(role_file.name)

    assert offenders == [], (
        "以下 governance 角色未开启 non_goals_enforced 硬约束："
        + ", ".join(offenders)
    )


def test_validate_requires_non_goals_items_when_non_goals_enforced(tmp_path):
    """开启 non_goals_enforced 时，non_goals.items 必须至少含一条记录。"""

    agents_root = tmp_path / ".agents"
    governance_dir = agents_root / "roles" / "governance"
    rules_dir = agents_root / "rules"
    docs_dir = agents_root / "docs" / "references"
    governance_dir.mkdir(parents=True)
    rules_dir.mkdir(parents=True)
    docs_dir.mkdir(parents=True)

    (rules_dir / "documentation.md").write_text("# doc\n", encoding="utf-8")
    (docs_dir / "metamodel.md").write_text("# meta\n", encoding="utf-8")
    (governance_dir / "shell-governor.md").write_text(
        """+++
id = "shell-governor"
domain = "governance"
layer = "governance"

[bindings]
rules = ["rules/documentation.md"]
references = ["docs/references/metamodel.md"]
skills = []

[constraints]
rules_must_exist = true
non_goals_enforced = true
+++

# Shell Governor

## Description

声明了硬约束但未声明任何非目标的治理角色。
""",
        encoding="utf-8",
    )

    validate_roles = _load_validate_roles_module()

    errors, warnings, role_ids = validate_roles.validate(agents_root)

    assert warnings == []
    assert role_ids == ["shell-governor"]
    assert any(
        "non_goals.items" in msg and "shell-governor" in msg for msg in errors
    ), errors


def test_validate_rejects_drift_between_non_goals_items_and_body(tmp_path):
    """non_goals.items 与 Markdown ## Non-Goals 节内容不一致时必须报错。"""

    agents_root = tmp_path / ".agents"
    governance_dir = agents_root / "roles" / "governance"
    rules_dir = agents_root / "rules"
    docs_dir = agents_root / "docs" / "references"
    governance_dir.mkdir(parents=True)
    rules_dir.mkdir(parents=True)
    docs_dir.mkdir(parents=True)

    (rules_dir / "documentation.md").write_text("# doc\n", encoding="utf-8")
    (docs_dir / "metamodel.md").write_text("# meta\n", encoding="utf-8")
    (governance_dir / "drifted-governor.md").write_text(
        """+++
id = "drifted-governor"
domain = "governance"
layer = "governance"

[bindings]
rules = ["rules/documentation.md"]
references = ["docs/references/metamodel.md"]
skills = []

[constraints]
rules_must_exist = true
non_goals_enforced = true

[non_goals]
items = [
    "不直接修改 skills/ 实现代码",
    "不在第一版引入自动化合规扫描",
]
+++

# Drifted Governor

## Description

frontmatter 与正文 Non-Goals 不一致示例。

## Non-Goals

- 不直接修改 `skills/` 实现代码
- 不直接修改 `skills/` 实现代码
""",
        encoding="utf-8",
    )

    validate_roles = _load_validate_roles_module()

    errors, warnings, role_ids = validate_roles.validate(agents_root)

    assert warnings == []
    assert role_ids == ["drifted-governor"]
    assert any(
        "drifted-governor" in msg and "Non-Goals" in msg for msg in errors
    ), errors


def test_all_repository_governance_role_bodies_match_non_goals_items():
    """仓库内 governance 角色的 Markdown ## Non-Goals 必须与 non_goals.items 一致。"""

    from importlib.util import module_from_spec, spec_from_file_location

    repo_root = Path(__file__).resolve().parent.parent
    governance_dir = repo_root / ".agents" / "roles" / "governance"
    assert governance_dir.is_dir(), f"governance 目录不存在：{governance_dir}"

    spec = spec_from_file_location(
        "_validate_roles_for_repo",
        repo_root / ".agents" / "scripts" / "validate_roles.py",
    )
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    errors, _, _ = module.validate(repo_root / ".agents")

    body_drift = [
        msg for msg in errors
        if "Non-Goals" in msg and msg.startswith("ERROR:")
    ]
    assert body_drift == [], (
        "以下 governance 角色 body 与 non_goals.items 不一致：\n"
        + "\n".join(body_drift)
    )
