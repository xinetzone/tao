# 知乎开发者平台 API 参考

> 来源：https://developer.zhihu.com/docs
> 归档日期：2026-05-26

## 概述

知乎开发者平台提供四大能力，每个能力有 API / Skill / MCP 三种接入形式。

| 能力 | 说明 | API 端点 |
|------|------|---------|
| 知乎搜索 | 站内内容搜索 | `/api/v1/content/zhihu_search` |
| 全网搜索 | 基于知乎的全网搜索 | `/api/v1/content/global_search` |
| 直答 | AI 问答能力（三档模型） | `/v1/chat/completions` |
| 热榜 | 实时热榜 | `/api/v1/content/hot_list` |

## 鉴权

所有接口统一使用 Bearer Token 认证。

**请求头**：

```
Authorization: Bearer <your_access_secret>
X-Request-Timestamp: 秒级 Unix 时间戳
Content-Type: application/json
```

Access Secret 在知乎开放平台个人中心获取。

---

## 知乎搜索

### API

- **端点**：`GET https://developer.zhihu.com/api/v1/content/zhihu_search`
- **参数**：
  - `Query` (String, 必填): 查询关键词
  - `Count` (Int32, 可选): 请求数量，默认10，最大10

- **响应 Data 字段**：
  - `HasMore` (Bool): 是否有下一页（当前固定 false）
  - `SearchHashId` (String): 搜索请求标识
  - `Items` (Array[Item]): 搜索结果列表
  - `EmptyReason` (String, 可选): 无结果原因

- **Item 字段**：
  - `Title` (String): 内容标题
  - `ContentType` (String): 类型（Article/Answer/Question）
  - `ContentID` (String): 内容标识
  - `ContentText` (String): 内容摘要
  - `Url` (String): 内容链接
  - `CommentCount` (Int32): 评论数
  - `VoteUpCount` (Int32): 赞同数
  - `AuthorName` (String): 作者昵称
  - `AuthorAvatar` (String): 作者头像
  - `AuthorBadge` (String): 认证图标
  - `AuthorBadgeText` (String): 认证文案
  - `EditTime` (Int32): 发布/更新时间戳
  - `CommentInfoList` (Array, 可选): 精选评论
  - `AuthorityLevel` (String): 权威等级
  - `RankingScore` (Float32): 排序分数

- **Curl 示例**：

```bash
curl -G 'https://developer.zhihu.com/api/v1/content/zhihu_search' \
  --data-urlencode 'Query=怎么理解rave文化' \
  -H 'Authorization: Bearer <your_access_secret>' \
  -H "X-Request-Timestamp: $(date +%s)" \
  -H 'Content-Type: application/json'
```

### Skill

- **下载**：https://developer.zhihu.com/download/zhihu_search_skills.zip
- **输入**：`query` (String, 必填), `count` (Int, 可选, 默认10, 最大10)
- **输出**：`code`, `message`, `item_count`, `items`
- **Item**: `title`, `summary`, `url`, `author_name`, `vote_up_count`, `comment_count`, `edit_time`

### MCP

- **SSE URL**：`https://developer.zhihu.com/api/mcp/zhihu_search/v1/sse`
- **Message URL**：`https://developer.zhihu.com/api/mcp/zhihu_search/v1/message`
- **工具名**：`zhihu_search`
- **参数**：`query` (String, 2-100字符), `count` (Number, 1-10, 默认10)
- **返回格式**：XML 结构化文本

---

## 全网搜索

### API

- **端点**：`GET https://developer.zhihu.com/api/v1/content/global_search`
- **参数**：
  - `Query` (String, 必填): 查询关键词
  - `Count` (Int32, 可选): 请求数量，默认10，最大20
  - `Filter` (String, 可选): 高级筛选表达式
  - `SearchDB` (String, 可选): 索引库，all/realtime/static，默认all

- **Filter 语法**：
  - 支持字段：`host`（域名）、`publish_time`（时间戳）
  - 操作符：`==`, `!=`, `>`, `>=`, `<`, `<=`
  - 逻辑：`AND`（高优先级）、`OR`，支持括号
  - 示例：`host=="example.com" AND publish_time>=1778494631`

- **响应 Item 字段**：与知乎搜索相同，额外有：
  - `AuthorityLevel`: 权威等级（1低/2中/3高/4超高）

### Skill

- **下载**：https://developer.zhihu.com/download/global_search_skills.zip
- **输入**：`query`, `count`(默认10), `filter`, `search_db`
- **使用建议**：对开放性问题使用完整关键词组合以提高覆盖质量

### MCP

- **SSE URL**：`https://developer.zhihu.com/api/mcp/global_search/v1/sse`
- **Message URL**：`https://developer.zhihu.com/api/mcp/global_search/v1/message`
- **工具名**：`global_search`
- **参数**：`query`, `count`(1-20), `filter`, `search_db`

---

## 直答

### API

- **端点**：`POST https://developer.zhihu.com/v1/chat/completions`
- **兼容 OpenAI 格式**

- **请求 Body**：
  - `model` (String, 必填): 模型档位
    - `zhida-fast-1p5`: 快速回答
    - `zhida-thinking-1p5`: 深度思考（含 reasoning_content）
    - `zhida-agent`: 智能检索+回答
  - `messages` (Array[Message], 必填): 对话消息列表
    - `role` (String): user/assistant
    - `content` (String): 内容
  - `stream` (Bool, 可选): 流式返回，默认 false

- **非流式响应**：

```json
{
  "id": "chatcmpl-xxxx",
  "object": "chat.completion",
  "created": 1740470400,
  "model": "zhida-thinking-1p5",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "reasoning_content": "分析过程...",
      "content": "最终回答"
    },
    "finish_reason": "stop"
  }]
}
```

- **流式响应**：SSE 格式，`data: {...}\n\n`，结束标记 `data: [DONE]`

- **Curl 示例**：

```bash
curl -X POST 'https://developer.zhihu.com/v1/chat/completions' \
  -H 'Authorization: Bearer <your_access_secret>' \
  -H "X-Request-Timestamp: $(date +%s)" \
  -H 'Content-Type: application/json' \
  -d '{"model":"zhida-thinking-1p5","messages":[{"role":"user","content":"什么是RAG？"}],"stream":false}'
```

### Skill

- **下载**：https://developer.zhihu.com/download/zhida_skills.zip
- **输入方式1（简化）**：`query`, `model`, `stream`
- **输入方式2（对话式）**：`model`, `messages`, `stream`
- **输出**：`code`, `id`, `model`, `stream`, `content`, `reasoning_content`, `finish_reason`
- **使用建议**：通用问答用 fast，强推理用 thinking，复杂任务用 agent

### MCP

- **端点**：`POST https://developer.zhihu.com/api/mcp/zhida/v1/stream`
- **传输方式**：MCP Streamable HTTP
- **工具名**：`zhida`
- **参数**：`query` (String, 必填), `model` (String, 必填), `member_id` (Number, 可选，预留)

---

## 热榜

### API

- **端点**：`GET https://developer.zhihu.com/api/v1/content/hot_list`
- **参数**：`Limit` (Int32, 可选, 默认30, 最大30)

- **响应 Data 字段**：
  - `Total` (Int64): 返回条数
  - `Items` (Array[Item]): 热榜列表

- **Item 字段**：
  - `Title` (String): 标题
  - `Url` (String): 链接
  - `ThumbnailUrl` (String): 缩略图，无时为空
  - `Summary` (String): 摘要，无时为空

- **说明**：仅返回问题和文章两类

### Skill

- **下载**：https://developer.zhihu.com/download/hot_list_skills.zip
- **输入**：`limit` (Int, 可选, 默认30, 最大30)
- **输出**：`code`, `message`, `total`, `item_count`, `items`

### MCP

- **SSE URL**：`https://developer.zhihu.com/api/mcp/hot_list/v1/sse`
- **Message URL**：`https://developer.zhihu.com/api/mcp/hot_list/v1/message`
- **工具名**：`hot_list`
- **参数**：`limit` (Number, 1-30, 默认30)
- **返回格式**：XML

---

## 通用错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 10001 | 参数错误 |
| 20001 | 鉴权失败 |
| 30001 | 频率限制 |
| 90001 | 内部错误 |

---

## Skill 下载汇总

| 能力 | 下载地址 |
|------|---------|
| 知乎搜索 | https://developer.zhihu.com/download/zhihu_search_skills.zip |
| 全网搜索 | https://developer.zhihu.com/download/global_search_skills.zip |
| 直答 | https://developer.zhihu.com/download/zhida_skills.zip |
| 热榜 | https://developer.zhihu.com/download/hot_list_skills.zip |

## MCP 端点汇总

| 能力 | SSE/Stream URL | 工具名 |
|------|---------------|--------|
| 知乎搜索 | `https://developer.zhihu.com/api/mcp/zhihu_search/v1/sse` | zhihu_search |
| 全网搜索 | `https://developer.zhihu.com/api/mcp/global_search/v1/sse` | global_search |
| 直答 | `https://developer.zhihu.com/api/mcp/zhida/v1/stream` | zhida |
| 热榜 | `https://developer.zhihu.com/api/mcp/hot_list/v1/sse` | hot_list |
