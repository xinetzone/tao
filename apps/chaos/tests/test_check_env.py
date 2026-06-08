import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_check_env_module():
    script_path = (
        Path(__file__).resolve().parents[1] / ".agents" / "scripts" / "check_env.py"
    )
    spec = spec_from_file_location("check_env", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_defuddle_check_uses_mise_managed_tool_entry():
    module = _load_check_env_module()

    defuddle = next(
        spec
        for spec in module.build_tool_specs(Path(__file__).resolve().parents[1])
        if spec.name == "defuddle"
    )

    assert defuddle.command == [
        "mise",
        "x",
        "npm:defuddle",
        "--",
        "defuddle",
        "--version",
    ]


def test_environment_check_main_resolves_project_root(monkeypatch):
    module = _load_check_env_module()

    monkeypatch.setattr(
        module,
        "check_tool",
        lambda spec: module.ToolResult(
            name=spec.name,
            expected=spec.expected,
            current=spec.expected,
            ok=True,
            fix=spec.fix,
        ),
    )
    monkeypatch.setattr(module, "print_table", lambda results: None)
    monkeypatch.setattr(module, "check_config_consistency", lambda project_root: [])

    assert module.main() == 0


def test_build_tool_specs_reads_tool_versions_from_mise_config(tmp_path):
    module = _load_check_env_module()
    mise_config = tmp_path / "mise.toml"
    mise_config.write_text(
        """
[tools]
python = "3.15.1"
uv = "0.12.0"
node = { version = "24.1.0" }
"npm:defuddle" = { version = "0.20.0" }
""".strip(),
        encoding="utf-8",
    )

    specs = {spec.name: spec for spec in module.build_tool_specs(tmp_path)}

    assert specs["python"].expected == "3.15.1"
    assert specs["uv"].expected == "0.12.0"
    assert specs["node"].expected == "24.1.0"
    assert specs["defuddle"].expected == "0.20.0"
    assert specs["mise"].fix == "先安装 mise，再重新运行 mise run init"


def test_config_consistency_accepts_ruff_supported_target_floor(tmp_path):
    module = _load_check_env_module()
    (tmp_path / "mise.toml").write_text(
        """
[tools]
python = "3.13.5"
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        """
requires-python = ">=3.13"

[tool.ruff]
target-version = "py313"
""".strip(),
        encoding="utf-8",
    )

    assert module.check_config_consistency(tmp_path) == []
