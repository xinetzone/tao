"""Linear GraphQL 查询定义。

使用 :func:`gql.gql` 将查询字符串编译为 AST，获得编译时校验。
查询结构参照 Linear API 文档与 Elixir 参考实现。
"""

from gql import gql

# ---------------------------------------------------------------------------
# FETCH_CANDIDATES — 按 project slug + 活跃状态过滤，分页获取候选 issue
# ---------------------------------------------------------------------------
FETCH_CANDIDATES = gql(
    """
query FetchCandidates(
    $projectSlug: String!,
    $stateNames: [String!]!,
    $first: Int!,
    $relationFirst: Int!,
    $after: String
) {
  issues(
    filter: {
      project: { slugId: { eq: $projectSlug } },
      state: { name: { in: $stateNames } }
    },
    first: $first,
    after: $after
  ) {
    nodes {
      id
      identifier
      title
      description
      priority
      state { name }
      branchName
      url
      labels {
        nodes { name }
      }
      inverseRelations(first: $relationFirst) {
        nodes {
          type
          relatedIssue {
            id
            identifier
            state { name }
          }
        }
      }
      createdAt
      updatedAt
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""
)

# ---------------------------------------------------------------------------
# FETCH_STATES_BY_IDS — 通过 ID 列表批量获取 issue 当前状态
# ---------------------------------------------------------------------------
FETCH_STATES_BY_IDS = gql(
    """
query FetchStatesByIds(
    $ids: [ID!]!,
    $first: Int!,
    $relationFirst: Int!
) {
  issues(filter: { id: { in: $ids } }, first: $first) {
    nodes {
      id
      identifier
      title
      description
      priority
      state { name }
      branchName
      url
      labels {
        nodes { name }
      }
      inverseRelations(first: $relationFirst) {
        nodes {
          type
          relatedIssue {
            id
            identifier
            state { name }
          }
        }
      }
      createdAt
      updatedAt
    }
  }
}
"""
)

# ---------------------------------------------------------------------------
# FETCH_BY_STATES — 按指定状态集合过滤（用于终态清理）
# ---------------------------------------------------------------------------
FETCH_BY_STATES = gql(
    """
query FetchByStates(
    $projectSlug: String!,
    $stateNames: [String!]!,
    $first: Int!,
    $relationFirst: Int!,
    $after: String
) {
  issues(
    filter: {
      project: { slugId: { eq: $projectSlug } },
      state: { name: { in: $stateNames } }
    },
    first: $first,
    after: $after
  ) {
    nodes {
      id
      identifier
      title
      description
      priority
      state { name }
      branchName
      url
      labels {
        nodes { name }
      }
      inverseRelations(first: $relationFirst) {
        nodes {
          type
          relatedIssue {
            id
            identifier
            state { name }
          }
        }
      }
      createdAt
      updatedAt
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""
)
