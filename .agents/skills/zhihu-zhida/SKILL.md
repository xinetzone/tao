---
name: zhida
version: 1.0.2
description: 调用知乎开放平台的 zhida 接口，返回结构化回答结果
homepage: ../../docs/zhida_openai.md
metadata: {"openclaw":{"emoji":"💬","requires":{"bins":["python3"]}}}
---

# Zhida Skill

## 概述
本 Skill 用于调用知乎开放平台的 `zhida` API。
完整的 API 文档请参考：https://developer.zhihu.com/docs

该 Skill 使用 Chat Completions 风格输入，适合 agent 场景调用。

## 认证
使用环境变量 `ZHIHU_ACCESS_SECRET` 进行认证
用户可以在知乎开放平台控制台获取 Access Secret

可选配置：

- `ZHIHU_OPENAPI_BASE_URL`（默认：`https://developer.zhihu.com`）
- `ZHIHU_ZHIDA_URL`（完整 endpoint 覆盖；设置后优先）

## 快速开始

`{baseDir}` 是 agent 框架在运行时自动替换的变量，指向当前 skill 目录的绝对路径（即 `skills/zhida/`）。

```bash
python3 {baseDir}/scripts/zhida.py '{"model":"zhida-thinking-1p5","messages":[{"role":"user","content":"如何理解 rave 文化"}]}'
```

## 输入约定

传入 OpenAI 风格 body：

```json
{"model":"zhida-agent","messages":[{"role":"user","content":"..."}]}
```

规则：

- `model` 为必填；脚本只检查是否为空，具体模型合法性由服务端校验
- `messages` 为必填，且必须为非空数组

## 可选模型

- `zhida-fast-1p5`
- `zhida-thinking-1p5`
- `zhida-agent`

## 输出约定

返回 JSON，包含：

- `code`
- `id`, `model`
- `content`
- `reasoning_content`
- `finish_reason`

### 失败

`error` 字段为动态错误描述，常见情况：

```json
{"error":"messages is required","exit_code":1}
{"error":"model is required","exit_code":1}
{"error":"Invalid JSON payload","exit_code":1}
{"error":"Set ZHIHU_ACCESS_SECRET first (Bearer auth only)","exit_code":1}
{"error":"HTTP request failed (timeout or network error)","exit_code":1}
{"error":"HTTP 400","body":{"error":{"message":"invalid model","type":"invalid_request_error","param":"model","code":"model_not_found"}},"exit_code":1}
```

HTTP 非 2xx 时额外携带 `body`：

```json
{"error":"HTTP 403","body":"Forbidden","exit_code":1}
```
