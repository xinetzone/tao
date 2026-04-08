"""Redis 缓存 key 前缀统一常量。

所有模块的 Redis key 命名规范，避免跨模块 key 冲突。
每个模块使用独立的顶层前缀。

命名规则::

    {module_prefix}:{component}:{identifier}

分隔符统一使用 ``:``（冒号）。

使用示例::

    from taolib.testing._base.cache_keys import CONFIG_PREFIX, PUSH_BUFFER_PREFIX

    key = f"{CONFIG_PREFIX}{environment}:{service}:{config_key}"
"""

# ==================== 配置中心 ====================
# 配置值缓存: config:{env}:{svc}:{key}
CONFIG_PREFIX = "config:"
# 配置元数据缓存: config:meta:{env}:{svc}:{key}
CONFIG_META_PREFIX = "config:meta:"
# 服务配置列表缓存: config:list:{env}:{svc}
CONFIG_LIST_PREFIX = "config:list:"
# 用户角色缓存: user:roles:{user_id}
USER_ROLES_PREFIX = "user:roles:"

# ==================== 推送服务 ====================
# 用户离线消息缓冲: push:buffer:{user_id}      TTL 86400s
PUSH_BUFFER_PREFIX = "push:buffer:"
# 频道消息缓冲（HTTP 轮询）: push:channel_buf:{channel}  TTL 3600s
PUSH_CHANNEL_BUF_PREFIX = "push:channel_buf:"
# 在线状态: push:presence:{user_id}             TTL 120s/600s
PUSH_PRESENCE_PREFIX = "push:presence:"
# 广播频道: push:broadcast:{channel}
PUSH_BROADCAST_PREFIX = "push:broadcast:"
# 实例心跳: push:instance:{instance_id}         TTL 60s
PUSH_INSTANCE_PREFIX = "push:instance:"

# ==================== 认证授权 ====================
# Token 黑名单: taolib:auth:blacklist:{jti}      TTL = token 剩余有效期
AUTH_BLACKLIST_PREFIX = "taolib:auth:blacklist:"

# ==================== 任务队列 ====================
# 任务队列根前缀（队列/运行中/已完成/失败/重试/任务/统计）
TASK_QUEUE_PREFIX = "tq:"

# ==================== 限流器 ====================
# 滑动窗口: ratelimit:window:{identifier}:{path}:{method}
RATELIMIT_WINDOW_PREFIX = "ratelimit:window:"
# 违规计数: ratelimit:violations:{identifier}
RATELIMIT_VIOLATIONS_PREFIX = "ratelimit:violations:"
# 统计: ratelimit:stats:*
RATELIMIT_STATS_PREFIX = "ratelimit:stats:"

# ==================== OAuth ====================
# CSRF state: oauth:state:{state_token}           TTL 600s
OAUTH_STATE_PREFIX = "oauth:state:"
# 会话: oauth:session:{session_id}
OAUTH_SESSION_PREFIX = "oauth:session:"
# 用户会话集合: oauth:user_sessions:{user_id}
OAUTH_USER_SESSIONS_PREFIX = "oauth:user_sessions:"

# ==================== 邮件服务 ====================
# 邮件发送队列: email:queue:{priority}
EMAIL_QUEUE_PREFIX = "email:queue:"


