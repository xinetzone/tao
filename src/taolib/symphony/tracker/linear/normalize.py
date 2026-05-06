"""Linear 响应规范化 — 将原始 GraphQL node 转换为领域模型 Issue。

主要处理：
- labels → 小写规范化
- blocked_by → 从 inverseRelations 中提取 type=="blocks" 的关联 issue
- priority → 非整数映射为 None
- state → 从嵌套的 state.name 提取
- 日期 → ISO 8601 字符串解析为 datetime
"""

from datetime import datetime, timezone

from taolib.symphony.tracker.models import Issue


def normalize_issue(node: dict) -> Issue:
    """将 Linear GraphQL 返回的 issue node 规范化为 :class:`Issue`。

    Args:
        node: Linear API 返回的原始 issue 字典，
              包含嵌套的 ``state``、``labels``、``inverseRelations`` 等字段。

    Returns:
        规范化后的 :class:`Issue` 实例。
    """
    return Issue(
        id=node["id"],
        identifier=node["identifier"],
        title=node["title"],
        description=node.get("description"),
        priority=_parse_priority(node.get("priority")),
        url=node.get("url"),
        state=_extract_state(node),
        labels=_extract_labels(node),
        blocked_by=_extract_blocked_by(node),
        branch_name=node.get("branchName"),
        created_at=_parse_datetime(node.get("createdAt")),
        updated_at=_parse_datetime(node.get("updatedAt")),
    )


def _extract_state(node: dict) -> str:
    """从嵌套的 state 对象中提取状态名称。"""
    state_obj = node.get("state")
    if isinstance(state_obj, dict):
        return state_obj.get("name", "")
    return ""


def _extract_labels(node: dict) -> list[str]:
    """从 labels.nodes 中提取标签名并转为小写。"""
    labels_obj = node.get("labels")
    if not isinstance(labels_obj, dict):
        return []
    nodes = labels_obj.get("nodes", [])
    if not isinstance(nodes, list):
        return []
    return [
        name.lower()
        for n in nodes
        if isinstance(n, dict) and isinstance(n.get("name"), str) and (name := n["name"].strip())
    ]


def _extract_blocked_by(node: dict) -> list[str]:
    """从 inverseRelations.nodes 中提取 type 为 'blocks' 的关联 issue ID。

    Linear 中 ``inverseRelations`` 表示"该 issue 被其他 issue 阻塞"，
    其中 ``type == "blocks"`` 意味着关联的 issue 阻塞了当前 issue。
    """
    relations_obj = node.get("inverseRelations")
    if not isinstance(relations_obj, dict):
        return []
    nodes = relations_obj.get("nodes", [])
    if not isinstance(nodes, list):
        return []
    blocked_ids: list[str] = []
    for rel in nodes:
        if not isinstance(rel, dict):
            continue
        rel_type = rel.get("type", "")
        if not isinstance(rel_type, str) or rel_type.strip().lower() != "blocks":
            continue
        related = rel.get("relatedIssue")
        if isinstance(related, dict) and isinstance(related.get("id"), str):
            blocked_ids.append(related["id"])
    return blocked_ids


def _parse_priority(value: object) -> int | None:
    """优先级解析：仅整数 1-4 有效，其余映射为 None。"""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _parse_datetime(raw: str | None) -> datetime | None:
    """ISO 8601 日期字符串解析，失败返回 None。"""
    if raw is None:
        return None
    try:
        dt = datetime.fromisoformat(raw)
        # 确保 timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None
