---
name: hot-list
version: 1.0.2
description: 获取知乎热榜列表，返回脚本整理后的结构化结果（标题、链接、缩略图、摘要）
homepage: ../../docs/hot_list.md
metadata: {"openclaw":{"emoji":"🔥","requires":{"bins":["python3"]}}}
---

# Hot List Skill

## 概述
本 Skill 用于调用知乎开放平台的 `hot_list` API。
完整的 API 文档请参考：https://developer.zhihu.com/docs

通过 OpenAPI Platform `GET /api/v1/content/hot_list` 获取热榜内容，并整理为含标题、链接、缩略图与摘要的列表。

## 认证
使用环境变量 `ZHIHU_ACCESS_SECRET` 进行认证
用户可以在知乎开放平台控制台获取 Access Secret

可选配置：

- `ZHIHU_OPENAPI_BASE_URL`（默认：`https://developer.zhihu.com`）
- `ZHIHU_HOT_LIST_URL`（完整 endpoint 覆盖；设置后优先）

## 快速开始

`{baseDir}` 是 agent 框架在运行时自动替换的变量，指向当前 skill 目录的绝对路径（即 `skills/hot-list/`）。

```bash
python3 {baseDir}/scripts/hot-list.py '{"limit":10}'
```

## 输入约定

```json
{"limit":10}
```

规则：

- `limit` 可选，默认 `30`
- 脚本会把 `limit` 规范到 `1-30`

## 输出约定

返回 JSON，包含：

- `code`, `message`
- `total`, `item_count`
- `items[]`，包含 `title`, `url`, `thumbnail_url`, `summary`

说明：

- `thumbnail_url` 和 `summary` 始终返回，无数据时为空字符串
- 若服务端返回的条目不是对象，脚本会跳过

### 失败

`error` 字段为动态错误描述，常见情况：

```json
{"error":"Invalid JSON payload","exit_code":1}
{"error":"Set ZHIHU_ACCESS_SECRET first (Bearer auth only)","exit_code":1}
{"error":"HTTP request failed (timeout or network error)","exit_code":1}
```

HTTP 非 2xx 时额外携带 `body`：

```json
{"error":"HTTP 403","body":"Forbidden","exit_code":1}
```
