"""CLI 输出格式化工具。

本模块负责对令牌等敏感信息进行脱敏处理，并将业务结果转换为
标准化的 JSON 可序列化字典后输出到 stdout。
"""

import argparse
import json

from taolib.github_app.models import InstallationTokenResult

from ._parsers import _detect_environment, _resolve_api_url, _resolve_strategy


def _mask_secret(secret: str) -> str:
    """对密钥字符串进行脱敏处理。

    Args:
        secret: 待脱敏的原始密钥字符串。

    Returns:
        脱敏后的字符串，保留首尾若干字符，中间以 ``...`` 替代。
    """
    if len(secret) <= 11:
        return f"{secret[:4]}...{secret[-2:]}"
    return f"{secret[:7]}...{secret[-4:]}"


def _build_profile_payload(args: argparse.Namespace) -> dict[str, str]:
    """构建 profile 子命令的输出数据。

    Args:
        args: 已解析的命令行参数。

    Returns:
        包含 ``api_url``、``default_strategy`` 与 ``environment`` 的字典。
    """
    api_url = _resolve_api_url(args)
    return {
        "api_url": api_url,
        "default_strategy": _resolve_strategy(args).value,
        "environment": _detect_environment(api_url).value,
    }


def _build_token_payload(result: InstallationTokenResult) -> dict[str, object]:
    """构建 token 子命令的输出数据。

    Args:
        result: 令牌管理器返回的安装令牌结果。

    Returns:
        包含令牌元信息与脱敏预览的字典。
    """
    return {
        "degraded": result.degraded,
        "effective_strategy": result.effective_strategy,
        "expires_at": result.expires_at.isoformat(),
        "requested_strategy": result.requested_strategy,
        "token_kind": result.token_kind.value,
        "token_preview": _mask_secret(result.token),
    }


def _emit_json(payload: dict[str, object]) -> None:
    """将字典以 JSON 格式输出到 stdout。

    Args:
        payload: 待输出的数据字典。
    """
    print(json.dumps(payload, sort_keys=True))
