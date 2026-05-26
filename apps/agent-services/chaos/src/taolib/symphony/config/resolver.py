"""Symphony 配置合并与解析。

实现配置的深度合并、环境变量替换、路径解析以及最终配置组装。
合并优先级：CLI > env $VAR > WORKFLOW.md YAML > symphony.toml [defaults] > Pydantic 默认值。
"""

import os
import re
from pathlib import Path

from taolib.symphony.config.loader import load_workflow
from taolib.symphony.config.schema import SymphonyConfig
from taolib.symphony.config.toml_config import load_toml

# 匹配 $VAR_NAME 形式的环境变量引用
_ENV_VAR_RE = re.compile(r"^\$([A-Za-z_][A-Za-z0-9_]*)$")


def deep_merge(base: dict, override: dict) -> dict:
    """深度合并两个字典。

    override 中的值覆盖 base 中的同名键。如果两边的值都是字典，
    则递归合并。base 和 override 均不被修改。

    Args:
        base: 基础配置字典。
        override: 覆盖配置字典。

    Returns:
        合并后的新字典。

    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def resolve_env_vars(config: dict) -> dict:
    """替换配置中的 $VAR_NAME 环境变量引用。

    仅对值为 ``$VAR_NAME`` 形式的字符串进行替换。
    如果环境变量不存在或为空字符串，则保留原始 ``$VAR_NAME`` 引用。

    Args:
        config: 原始配置字典。

    Returns:
        替换环境变量后的配置字典。

    """
    return _resolve_env_vars_recursive(config)


def _resolve_env_vars_recursive(value: object) -> object:
    """递归替换环境变量引用。"""
    if isinstance(value, dict):
        return {k: _resolve_env_vars_recursive(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars_recursive(item) for item in value]
    if isinstance(value, str):
        m = _ENV_VAR_RE.match(value)
        if m:
            env_name = m.group(1)
            env_value = os.environ.get(env_name, "")
            if env_value:
                return env_value
        return value
    return value


def resolve_paths(config: dict, base_dir: Path) -> dict:
    """解析配置中的路径值。

    对已知的路径字段进行 ``~`` 展开和相对路径解析：
    - ``~`` 展开为用户主目录。
    - 相对路径基于 base_dir 解析为绝对路径。
    - 仅处理已知的路径字段，不重写 URI 或任意命令字符串。

    Args:
        config: 配置字典。
        base_dir: 相对路径的基准目录（通常为 WORKFLOW.md 所在目录）。

    Returns:
        路径解析后的配置字典。

    """
    config = dict(config)

    # 解析 workspace.root
    workspace = config.get("workspace")
    if isinstance(workspace, dict) and "root" in workspace:
        workspace = dict(workspace)
        workspace["root"] = _resolve_path_value(workspace["root"], base_dir)
        config["workspace"] = workspace

    return config


def _resolve_path_value(value: object, base_dir: Path) -> object:
    """解析单个路径值。"""
    if not isinstance(value, str):
        return value

    # 先展开环境变量引用
    m = _ENV_VAR_RE.match(value)
    if m:
        env_name = m.group(1)
        env_value = os.environ.get(env_name, "")
        if env_value:
            value = env_value
        else:
            return value

    # 展开 ~ 为用户主目录
    expanded = Path(value).expanduser()

    # 如果不是绝对路径，基于 base_dir 解析
    if not expanded.is_absolute():
        expanded = (base_dir / expanded).resolve()
    else:
        expanded = expanded.resolve()

    return str(expanded)


def resolve_config(
    cli_args: dict,
    toml_path: Path | None,
    workflow_path: Path,
) -> SymphonyConfig:
    """组装最终配置。

    按优先级从低到高合并配置源：
    1. Pydantic 默认值
    2. symphony.toml [defaults] 段
    3. WORKFLOW.md YAML 前置数据
    4. 环境 $VAR 替换
    5. 路径解析
    6. CLI 参数覆盖

    Args:
        cli_args: CLI 参数字典，例如 ``{"port": 8080, "logs_root": Path("./log")}``。
        toml_path: symphony.toml 文件路径，为 None 则跳过。
        workflow_path: WORKFLOW.md 文件路径。

    Returns:
        校验后的 SymphonyConfig 实例。

    Raises:
        WorkflowLoadError: WORKFLOW.md 无法加载。
        ConfigError: TOML 配置无法加载。
        ValueError: 配置校验失败。

    """
    # 1. 从 WORKFLOW.md 加载原始配置
    wf = load_workflow(workflow_path)
    workflow_config = wf.config

    # 2. 从 symphony.toml 加载 [defaults] 段
    toml_defaults: dict = {}
    if toml_path is not None:
        toml_defaults = load_toml(toml_path)

    # 3. 合并：TOML defaults 为 base，WORKFLOW.md YAML 覆盖
    merged = deep_merge(toml_defaults, workflow_config)

    # 4. 环境变量替换
    merged = resolve_env_vars(merged)

    # 5. 路径解析（基于 WORKFLOW.md 所在目录）
    workflow_dir = workflow_path.resolve().parent
    merged = resolve_paths(merged, workflow_dir)

    # 6. CLI 参数覆盖
    merged = _apply_cli_overrides(merged, cli_args)

    # 7. 构造 Pydantic 模型（包含默认值填充和校验）
    try:
        return SymphonyConfig.model_validate(merged)
    except Exception as exc:
        msg = f"配置校验失败: {exc}"
        raise ValueError(msg) from exc


def _apply_cli_overrides(config: dict, cli_args: dict) -> dict:
    """将 CLI 参数应用到配置字典。

    仅在 CLI 参数非 None 时覆盖对应配置项。
    """
    config = dict(config)

    # --port 覆盖 server.port
    port = cli_args.get("port")
    if port is not None:
        server = dict(config.get("server", {}))
        server["port"] = port
        config["server"] = server

    return config
