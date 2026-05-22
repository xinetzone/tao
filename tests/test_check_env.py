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

    defuddle = next(spec for spec in module.TOOLS if spec.name == "defuddle")

    assert defuddle.command == [
        "mise",
        "x",
        "npm:defuddle",
        "--",
        "defuddle",
        "--version",
    ]
