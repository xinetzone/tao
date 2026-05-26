"""Linear API 客户端 — 基于 gql+httpx 的异步 GraphQL 实现。

实现 :class:`TrackerClient` 接口，提供三个核心查询方法：

- :meth:`fetch_candidate_issues`  — 分页获取候选 issue
- :meth:`fetch_issues_by_states`  — 按状态集合过滤 issue
- :meth:`fetch_issue_states_by_ids` — 根据 ID 批量获取 issue 状态

每次查询通过 ``async with self._client as session`` 创建新会话，
确保连接生命周期隔离。
"""

import logging

from gql import Client

from taolib.symphony.tracker.base import TrackerClient
from taolib.symphony.tracker.errors import (
    LinearAPIRequestError,
    LinearGraphQLError,
    LinearMissingCursorError,
)
from taolib.symphony.tracker.linear.normalize import normalize_issue
from taolib.symphony.tracker.linear.queries import (
    FETCH_BY_STATES,
    FETCH_CANDIDATES,
    FETCH_STATES_BY_IDS,
)
from taolib.symphony.tracker.linear.transport import create_transport
from taolib.symphony.tracker.models import Issue, TrackerConfig

logger = logging.getLogger(__name__)

_PAGE_SIZE = 50
_RELATION_PAGE_SIZE = 50


class LinearClient(TrackerClient):
    """Linear API 客户端，基于 gql + httpx 异步传输。

    Args:
        config: Tracker 配置，包含 endpoint、api_key、project_slug 等。
    """

    def __init__(self, config: TrackerConfig) -> None:
        transport = create_transport(config)
        self._client = Client(
            transport=transport,
            fetch_schema_from_transport=False,
        )
        self._config = config

    # ------------------------------------------------------------------
    # TrackerClient 接口实现
    # ------------------------------------------------------------------

    async def fetch_candidate_issues(self) -> list[Issue]:
        """获取候选 issue 列表（分页）。

        按 project slug + 配置中的 active_states 过滤，
        每页取 :data:`_PAGE_SIZE` 条，自动翻页直到遍历完成。
        """
        all_nodes = await self._paginated_query(
            query=FETCH_CANDIDATES,
            variables={
                "projectSlug": self._config.project_slug,
                "stateNames": self._config.active_states,
                "first": _PAGE_SIZE,
                "relationFirst": _RELATION_PAGE_SIZE,
            },
            field_name="issues",
        )
        return [normalize_issue(node) for node in all_nodes]

    async def fetch_issues_by_states(self, states: list[str]) -> list[Issue]:
        """按指定状态集合过滤 issue（分页）。

        主要用于终态清理：启动时扫描 Done / Cancelled 等终态
        的工作区残留。

        Args:
            states: 状态名称列表。
        """
        if not states:
            return []

        all_nodes = await self._paginated_query(
            query=FETCH_BY_STATES,
            variables={
                "projectSlug": self._config.project_slug,
                "stateNames": states,
                "first": _PAGE_SIZE,
                "relationFirst": _RELATION_PAGE_SIZE,
            },
            field_name="issues",
        )
        return [normalize_issue(node) for node in all_nodes]

    async def fetch_issue_states_by_ids(self, issue_ids: list[str]) -> list[Issue]:
        """根据 ID 列表批量获取 issue 的当前状态（分批）。

        将 ID 列表按 :data:`_PAGE_SIZE` 分批查询，每批独立发起请求，
        最终按原始请求顺序排列返回结果。

        Args:
            issue_ids: Issue UUID 列表。
        """
        if not issue_ids:
            return []

        # 去重并保持原始顺序
        unique_ids = list(dict.fromkeys(issue_ids))
        order_index = {iid: idx for idx, iid in enumerate(unique_ids)}

        all_nodes: list[dict] = []
        for start in range(0, len(unique_ids), _PAGE_SIZE):
            batch = unique_ids[start : start + _PAGE_SIZE]
            batch_nodes = await self._execute_query(
                query=FETCH_STATES_BY_IDS,
                variables={
                    "ids": batch,
                    "first": len(batch),
                    "relationFirst": _RELATION_PAGE_SIZE,
                },
                field_name="issues",
                paginated=False,
            )
            all_nodes.extend(batch_nodes)

        issues = [normalize_issue(node) for node in all_nodes]
        # 按原始请求顺序排列
        fallback = len(order_index)
        issues.sort(key=lambda issue: order_index.get(issue.id, fallback))
        return issues

    # ------------------------------------------------------------------
    # 内部分页与查询逻辑
    # ------------------------------------------------------------------

    async def _paginated_query(
        self,
        query: object,
        variables: dict,
        field_name: str,
    ) -> list[dict]:
        """通用分页查询逻辑。

        自动跟踪 ``endCursor``，循环翻页直到 ``hasNextPage`` 为 False。

        Args:
            query: gql 编译后的 AST 查询文档。
            variables: GraphQL 变量字典。
            field_name: 响应 ``data`` 中对应的字段名（如 ``"issues"``）。

        Returns:
            所有页的 node 字典合并列表。

        Raises:
            LinearMissingCursorError: hasNextPage=True 但 endCursor 缺失。
        """
        all_nodes: list[dict] = []
        after_cursor: str | None = None

        while True:
            if after_cursor is not None:
                variables["after"] = after_cursor
            else:
                variables.pop("after", None)

            page_nodes, page_info = await self._execute_query(
                query=query,
                variables=variables,
                field_name=field_name,
                paginated=True,
            )
            all_nodes.extend(page_nodes)

            if not page_info.get("hasNextPage", False):
                break

            end_cursor = page_info.get("endCursor")
            if not end_cursor:
                raise LinearMissingCursorError(
                    "分页响应中 hasNextPage=True 但缺少 endCursor"
                )
            after_cursor = end_cursor

        return all_nodes

    async def _execute_query(
        self,
        query: object,
        variables: dict,
        field_name: str,
        *,
        paginated: bool,
    ) -> tuple[list[dict], dict]:
        """执行单次 GraphQL 查询并提取结果。

        Args:
            query: gql AST 查询文档。
            variables: GraphQL 变量。
            field_name: 响应 data 中的字段名。
            paginated: 是否为分页查询（需要提取 pageInfo）。

        Returns:
            ``(nodes, page_info)`` 元组。
            非分页查询的 ``page_info`` 为空字典。

        Raises:
            LinearAPIRequestError: 网络/传输错误。
            LinearAPIStatusError: 非 200 响应。
            LinearGraphQLError: GraphQL errors 字段非空。
        """
        try:
            async with self._client as session:
                result = await session.execute(
                    query,
                    variable_values=variables,
                )
        except Exception as exc:
            # gql 会在传输错误时抛出异常
            raise LinearAPIRequestError(
                f"Linear API 请求失败: {exc}"
            ) from exc

        # 检查 GraphQL errors
        if isinstance(result, dict) and "errors" in result:
            errors = result["errors"]
            raise LinearGraphQLError(
                "Linear GraphQL 响应包含错误",
                errors=errors,
            )

        # 提取 data[field_name]
        field_data = result.get(field_name, {})
        if not isinstance(field_data, dict):
            field_data = {}

        nodes = field_data.get("nodes", [])
        if not isinstance(nodes, list):
            nodes = []

        page_info: dict = {}
        if paginated:
            page_info = field_data.get("pageInfo", {})
            if not isinstance(page_info, dict):
                page_info = {}

        return nodes, page_info
