"""客户端侧工具定义。

定义可供 Codex 智能体在工作区内调用的工具，
当前实现为 Linear GraphQL 查询工具。
"""

from dataclasses import dataclass, field

__all__ = ["DynamicTool", "LinearGraphQLTool", "ToolResult"]


@dataclass
class ToolResult:
    """工具执行结果。"""

    success: bool
    """是否成功。"""

    output: str = ""
    """工具输出的文本内容。"""

    error: str | None = None
    """错误信息。"""


class DynamicTool:
    """动态工具基类。

    所有客户端侧工具的抽象基类，
    定义工具名称和调用接口。
    """

    @property
    def name(self) -> str:
        """工具名称。"""
        raise NotImplementedError

    @property
    def description(self) -> str:
        """工具描述。"""
        raise NotImplementedError

    async def handle(self, arguments: dict) -> ToolResult:
        """处理工具调用。

        Args:
            arguments: 工具调用参数。

        Returns:
            工具执行结果。
        """
        raise NotImplementedError

    def to_tool_definition(self) -> dict:
        """生成 Codex 工具定义字典。"""
        return {
            "name": self.name,
            "description": self.description,
        }


class LinearGraphQLTool(DynamicTool):
    """Linear GraphQL 查询工具。

    允许 Codex 智能体在工作区内查询 Linear API，
    复用 Symphony 的 Linear 认证信息。
    """

    def __init__(self, api_key: str, endpoint: str = "https://api.linear.app/graphql") -> None:
        self._api_key = api_key
        self._endpoint = endpoint

    @property
    def name(self) -> str:
        return "linear_graphql"

    @property
    def description(self) -> str:
        return "查询 Linear GraphQL API，获取 Issue、项目等信息"

    async def handle(self, arguments: dict) -> ToolResult:
        """执行 Linear GraphQL 查询。

        Args:
            arguments: 包含 ``query`` 和可选 ``variables`` 的字典。

        Returns:
            GraphQL 查询结果。
        """
        import json

        import httpx

        query = arguments.get("query", "")
        variables = arguments.get("variables", {})

        if not query:
            return ToolResult(success=False, error="缺少 query 参数")

        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }
        payload = {"query": query, "variables": variables}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    self._endpoint,
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()

            if "errors" in data:
                errors = data["errors"]
                first_msg = errors[0].get("message", "未知 GraphQL 错误")
                return ToolResult(
                    success=False,
                    error=f"GraphQL 错误: {first_msg}",
                    output=json.dumps(data, ensure_ascii=False),
                )

            return ToolResult(
                success=True,
                output=json.dumps(data.get("data", {}), ensure_ascii=False),
            )
        except httpx.HTTPStatusError as e:
            return ToolResult(success=False, error=f"HTTP {e.response.status_code}: {e}")
        except httpx.RequestError as e:
            return ToolResult(success=False, error=f"请求失败: {e}")

    def to_tool_definition(self) -> dict:
        """生成包含参数 schema 的工具定义。"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "GraphQL 查询字符串",
                    },
                    "variables": {
                        "type": "object",
                        "description": "GraphQL 查询变量",
                    },
                },
                "required": ["query"],
            },
        }
