"""GitHub App 集成的异常体系。

本模块定义了 GitHub App 子模块中所有可预期错误的公共基类，
调用方可通过捕获 :class:`GitHubAppError` 一次性处理本集成报出的异常。
"""


class GitHubAppError(Exception):
    """GitHub App 集成的异常基类。

    所有本模块主动抛出的异常都以本类为根，便于上层统一捕获。
    """


class GitHubAppConfigurationError(ValueError, GitHubAppError):
    """必需的 GitHub App 配置缺失或非法时抛出。

    常见触发场景：

    - ``GITHUB_APP_ID`` / ``GITHUB_APP_INSTALLATION_ID`` 环境变量未设置。
    - 私钥既未通过 ``GITHUB_APP_PRIVATE_KEY`` 传入，也未通过
      ``GITHUB_APP_PRIVATE_KEY_FILE`` 指定。

    同时继承自 :class:`ValueError`，便于兼容常规参数校验逻辑。
    """


class GitHubAppClientError(GitHubAppError):
    """GitHub App 客户端未能获取安装令牌时抛出。

    常见触发场景：

    - 网络超时或连接失败。
    - GitHub API 返回非 2xx 状态码。
    - JWT 签名无效导致认证失败。
    """
