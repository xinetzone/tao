"""``taolib-github-app`` 命令行入口。

本模块提供两个子命令：

- ``profile``：查询当前运行环境画像，无需有效私钥即可执行。
- ``token``：获取安装令牌并以脱敏后的 JSON 输出。

详细环境变量与输出示例请参阅 :class:`taolib.github_app.config.GitHubAppSettings`。
"""

import asyncio
import json
import sys

from taolib.github_app.errors import GitHubAppClientError, GitHubAppConfigurationError

from ._builders import build_manager, build_request
from ._formatters import _build_profile_payload, _build_token_payload, _emit_json
from ._parsers import build_parser

# 保持向后兼容：测试通过 taolib.cli.github_app.build_manager 做 monkeypatch
__all__ = ["main", "build_manager", "build_request", "build_parser"]


def main(argv: list[str] | None = None) -> int:
    """CLI 主入口。

    Args:
        argv: 可选参数列表，为 ``None`` 时默认使用 :data:`sys.argv`。

    Returns:
        进程退出码：``0`` 表示成功，``1`` 表示配置错误，``2`` 表示客户端错误。
    """
    try:
        args = build_parser().parse_args(argv)
        if args.command == "profile":
            _emit_json(_build_profile_payload(args))
            return 0
        manager = build_manager(args)
        result = asyncio.run(manager.get_token(build_request(args)))
        _emit_json(_build_token_payload(result))
        return 0
    except GitHubAppConfigurationError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    except GitHubAppClientError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
