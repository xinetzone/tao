"""OAuth Redis 缓存键定义模块。

定义 OAuth 系统中使用的所有 Redis 缓存键。
"""


def oauth_state_key(state: str) -> str:
    """生成 CSRF state 缓存键。

    Args:
        state: state token

    Returns:
        Redis key
    """
    return f"oauth:state:{state}"


def oauth_session_key(session_id: str) -> str:
    """生成会话缓存键。

    Args:
        session_id: 会话 ID

    Returns:
        Redis key
    """
    return f"oauth:session:{session_id}"


def oauth_user_sessions_key(user_id: str) -> str:
    """生成用户会话列表缓存键。

    Args:
        user_id: 用户 ID

    Returns:
        Redis key
    """
    return f"oauth:user_sessions:{user_id}"
