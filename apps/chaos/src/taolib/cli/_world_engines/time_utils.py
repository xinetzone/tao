"""时间处理工具函数。"""

from datetime import UTC, datetime, timedelta


def now_iso() -> str:
    """返回当前时间的 ISO 8601 with offset 字符串。"""
    return datetime.now(UTC).astimezone().isoformat()


def parse_iso(ts: str) -> datetime:
    """将 ISO 8601 with offset 字符串解析为 datetime（带时区）。"""
    return datetime.fromisoformat(ts)


def lease_until_iso(lease_minutes: int) -> str:
    """计算从现在起 lease_minutes 分钟后的 ISO 8601 时间戳。"""
    dt = datetime.now(UTC).astimezone() + timedelta(minutes=lease_minutes)
    return dt.isoformat()
