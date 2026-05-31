# AI Hero 核心工程实践 —— 可复用最佳实践指南

> 本文档基于对 [AI Hero](https://github.com/ai-hero-dev/ai-hero/) 源码的深度分析，提炼出三大核心工程实践，并提供可直接复用的代码模板。
> 适用读者：构建 LLM 应用、AI Agent、评估管线的工程师与技术负责人。

---

## 目录

- [一、模型缓存中间件设计](#一模型缓存中间件设计)
- [二、MCP（Model Context Protocol）集成方式](#二mcpmodel-context-protocol集成方式)
- [三、多模型切换策略](#三多模型切换策略)
- [四、组合应用：完整工作流示例](#四组合应用完整工作流示例)
- [五、设计原则总结](#五设计原则总结)
- [六、适用项目检查清单](#六适用项目检查清单)

---

## 一、模型缓存中间件设计

### 1.1 设计理念

- **无侵入式装饰器模式**：通过中间件拦截 LLM 调用，业务代码无需修改即可获得缓存能力。
- **流式响应缓存**：基于 `TransformStream` 收集流式片段，命中缓存时通过模拟重放实现一致体验。
- **通用存储抽象**：基于 [`unstorage`](https://unstorage.unjs.io/) 提供可插拔后端（fs / redis / memory / cloudflare-kv 等），开发使用本地文件、生产切换 Redis 零代码改动。

### 1.2 架构示意

```
Model (OpenAI / Claude / DeepSeek)
    ↓ [middleware]
CacheMiddleware (wrapGenerate + wrapStream)
    ↓
Storage (unstorage + 可选 driver)
    ├── fs        (开发态)
    ├── memory    (单元测试)
    └── redis     (生产态)
```

### 1.3 缓存键生成策略

缓存键必须能唯一标识"输入参数 + 模型身份"，避免不同 prompt 互相污染：

```typescript
cacheKey = hash({
  model_id,          // 区分模型版本
  params,            // prompt / temperature / topP / maxTokens 等
  systemPrompt,      // 系统提示词参与 hash
});
```

> 推荐使用 SHA-256 截取前 16-32 字符作为 key，兼顾碰撞概率与可读性。

### 1.4 代码模板

```typescript
import { experimental_wrapLanguageModel } from "ai";
import { createStorage } from "unstorage";
import fsDriver from "unstorage/drivers/fs";
import { anthropic } from "@ai-sdk/anthropic";
import { createHash } from "node:crypto";

// 1. 创建存储后端（开发态：本地文件；生产态可替换为 redis driver）
const cache = createStorage({
  driver: fsDriver({ base: "./.cache/llm" }),
});

// 2. 缓存键生成
function generateCacheKey(params: unknown): string {
  const json = JSON.stringify(params);
  return createHash("sha256").update(json).digest("hex").slice(0, 32);
}

// 3. 定义缓存中间件
function createCacheMiddleware(storage: typeof cache) {
  return {
    wrapGenerate: async ({ doGenerate, params }) => {
      const key = generateCacheKey(params);
      const cached = await storage.getItem(key);
      if (cached) return cached as Awaited<ReturnType<typeof doGenerate>>;

      const result = await doGenerate();
      await storage.setItem(key, result);
      return result;
    },

    wrapStream: async ({ doStream, params }) => {
      const key = generateCacheKey(params);
      const cached = await storage.getItem<unknown[]>(key);

      // 命中：模拟流式重放
      if (cached) {
        return { stream: simulateReadableStream(cached), rawCall: { rawPrompt: null, rawSettings: {} } };
      }

      // 未命中：tee 一路真实下游、一路收集入缓存
      const { stream, ...rest } = await doStream();
      const chunks: unknown[] = [];

      const transformStream = new TransformStream({
        transform(chunk, controller) {
          chunks.push(chunk);
          controller.enqueue(chunk);
        },
        async flush() {
          await storage.setItem(key, chunks);
        },
      });

      return { stream: stream.pipeThrough(transformStream), ...rest };
    },
  };
}

// 4. 流式重放工具
function simulateReadableStream<T>(chunks: T[]): ReadableStream<T> {
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(chunk);
      controller.close();
    },
  });
}

// 5. 装饰模型
export const cachedModel = experimental_wrapLanguageModel({
  model: anthropic("claude-3-5-sonnet-latest"),
  middleware: createCacheMiddleware(cache),
});
```

### 1.5 适用场景

| 场景 | 收益 |
|------|------|
| 开发 / 调试阶段 | 避免重复触发 API，节省成本与等待时间 |
| `temperature=0` 的确定性场景 | 输入相同 → 输出相同，天然命中率高 |
| 评估（eval）流程 | 同一数据集多轮跑分，保证可重复性 |
| 教学演示 / 视频录制 | 离线可重放，避免现场断网或额度耗尽 |

### 1.6 注意事项

- **不要缓存非确定性场景**（高 temperature、含时间戳的工具调用）。
- **缓存 TTL**：通过 `setItem(key, value, { ttl })` 控制；评估场景可设永久。
- **隐私**：写入磁盘的缓存包含完整 prompt，敏感数据需加密或落到内存 driver。

---

## 二、MCP（Model Context Protocol）集成方式

### 2.1 设计理念

- **标准化工具/资源接口**：解耦 LLM 与外部能力，工具只需实现一次即可被任意 MCP-aware 客户端消费。
- **多传输协议支持**：`stdio`（本地子进程）、`SSE`（服务端推送）、`HTTP`（流式或一次性请求）。
- **与 Vercel AI SDK 无缝集成**：`experimental_createMCPClient` 直接产出 `tools` 对象，可投喂给 `generateText` / `streamText`。

### 2.2 架构层次

```
AI Application
    ↓ [AI SDK generateText / streamText]
MCP Client (工具发现 + 调用)
    ↓ [transport: stdio / SSE / HTTP]
MCP Server (工具定义 + 执行)
    ↓
External Services / Local Tools / Databases
```

### 2.3 三种传输协议对比

| 协议 | 适用场景 | 优势 | 劣势 |
|------|---------|------|------|
| **stdio** | 本地进程间通信、CLI 工具 | 简单、低延迟、无端口冲突 | 仅限本地，无法跨网络 |
| **SSE** | 服务端推送、浏览器端 | 支持流式响应、HTTP 兼容 | 单向通信（Server → Client） |
| **HTTP** | Web 部署、跨语言调用 | 通用、易扩展、可走网关 | 需额外部署运维 |

### 2.4 代码模板 —— stdio 方式（推荐用于本地 CLI 工具）

```typescript
import { experimental_createMCPClient, generateText } from "ai";
import { Experimental_StdioMCPTransport } from "ai/mcp-stdio";
import { anthropic } from "@ai-sdk/anthropic";

// 创建 MCP 客户端（stdio 传输：拉起子进程并通过 stdin/stdout 通信）
const mcpClient = await experimental_createMCPClient({
  transport: new Experimental_StdioMCPTransport({
    command: "npx",
    args: ["-y", "@modelcontextprotocol/server-filesystem", "./data"],
  }),
});

// 自动发现工具列表
const tools = await mcpClient.tools();

// 在 AI SDK 中使用
const result = await generateText({
  model: anthropic("claude-3-5-sonnet-latest"),
  tools,
  prompt: "列出 data 目录下的所有文件并统计 markdown 数量",
});

// 用完关闭
await mcpClient.close();
```

### 2.5 代码模板 —— HTTP / SSE 方式（推荐用于 Web 服务）

**服务端（Hono + MCP）：**

```typescript
import { Hono } from "hono";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "my-tools", version: "1.0.0" });

// 注册工具
server.tool(
  "get-weather",
  { city: z.string().describe("城市名，例如 'Shanghai'") },
  async ({ city }) => {
    const weather = await fetchWeather(city);
    return { content: [{ type: "text", text: JSON.stringify(weather) }] };
  },
);

// 挂载到 Hono 路由
const app = new Hono();
app.all("/mcp", async (c) => {
  // 伪代码：将 server 适配为 SSE / HTTP 处理器
  return server.handleRequest(c.req.raw);
});

export default app;
```

**客户端：**

```typescript
const mcpClient = await experimental_createMCPClient({
  transport: { type: "sse", url: "http://localhost:3000/mcp" },
});

const tools = await mcpClient.tools();
```

### 2.6 发布 MCP Server 到 NPM

将 MCP Server 打包为可执行包，让任何用户通过 `npx` 一键运行：

```json
{
  "name": "@my-org/mcp-tools",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "my-mcp-tools": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build"
  },
  "files": ["dist"]
}
```

发布后，使用方在任意 MCP 客户端配置：

```jsonc
{
  "command": "npx",
  "args": ["-y", "@my-org/mcp-tools"]
}
```

### 2.7 设计要点

- **工具命名**：使用 `domain-action` 格式（如 `github-create-issue`），避免命名冲突。
- **Schema 必填**：所有工具入参用 Zod 显式描述，LLM 自动理解参数语义。
- **错误处理**：工具内部抛错时返回 `{ isError: true, content: [...] }`，让 LLM 可观测并自我恢复。
- **资源（Resource）**：除工具外，MCP 还支持只读资源（如文件、数据库行），用于 RAG。

---

## 三、多模型切换策略

### 3.1 设计理念

- **环境变量驱动**：零代码修改即可在云端模型与本地模型间切换。
- **工厂模式统一接口**：业务侧只引用 `smallModel` / `flagshipModel` 等语义化别名，不直接耦合 provider。
- **云端 + 本地无缝切换**：开发态用 LM Studio 节省成本，生产态用 Anthropic / OpenAI 保证质量。

### 3.2 架构

```
Environment Variable (USE_LOCAL_MODEL)
    ↓ [factory]
Model Registry (models.ts)
    ├── Cloud: Anthropic / OpenAI / DeepSeek / Google
    └── Local: LM Studio (OpenAI Compatible) / Ollama
```

### 3.3 代码模板

```typescript
// models.ts —— 统一模型注册
import { anthropic } from "@ai-sdk/anthropic";
import { openai } from "@ai-sdk/openai";
import { createOpenAICompatible } from "@ai-sdk/openai-compatible";

// ---- 云端模型定义 ----
export const flagshipAnthropicModel = anthropic("claude-3-5-sonnet-latest");
export const smallAnthropicModel = anthropic("claude-3-5-haiku-latest");
export const smallOpenAiModel = openai("gpt-4o-mini");
export const flagshipOpenAiModel = openai("gpt-4o");

// ---- 本地模型定义（LM Studio / Ollama 兼容 OpenAI API） ----
const lmstudio = createOpenAICompatible({
  name: "lmstudio",
  baseURL: process.env.LOCAL_MODEL_BASE_URL ?? "http://localhost:1234/v1",
});
export const localModel = lmstudio(process.env.LOCAL_MODEL_ID ?? "loaded-model");

// ---- 工厂函数 —— 环境变量驱动 ----
export const smallModel = process.env.USE_LOCAL_MODEL
  ? localModel
  : smallAnthropicModel;

export const flagshipModel = process.env.USE_LOCAL_MODEL
  ? localModel
  : flagshipAnthropicModel;
```

### 3.4 业务侧使用

```typescript
import { smallModel, flagshipModel } from "../_shared/models";
import { generateText } from "ai";

// 业务代码只关心"要小模型还是旗舰模型"，不关心具体 provider
const result = await generateText({
  model: smallModel,
  prompt: "Hello!",
});
```

### 3.5 环境配置

```bash
# .env —— 使用云端模型（默认）
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# .env —— 使用本地模型（开发态）
USE_LOCAL_MODEL=true
LOCAL_MODEL_BASE_URL=http://localhost:1234/v1
LOCAL_MODEL_ID=qwen2.5-coder-7b-instruct
# 确保 LM Studio / Ollama 已运行
```

### 3.6 进阶：基于任务复杂度的模型路由

```typescript
// 按任务复杂度动态选择模型，平衡成本与质量
export type TaskComplexity = "low" | "medium" | "high";

export function getModelForTask(complexity: TaskComplexity) {
  switch (complexity) {
    case "low":
      return smallModel;        // 分类、抽取、改写
    case "medium":
      return smallModel;        // 简单推理、摘要
    case "high":
      return flagshipModel;     // 复杂推理、代码生成、Agent 决策
  }
}
```

### 3.7 进阶：Provider 级降级与重试

```typescript
import { generateText } from "ai";

async function generateWithFallback(prompt: string) {
  try {
    return await generateText({ model: flagshipAnthropicModel, prompt });
  } catch (err) {
    console.warn("Anthropic 失败，降级到 OpenAI", err);
    return await generateText({ model: flagshipOpenAiModel, prompt });
  }
}
```

---

## 四、组合应用：完整工作流示例

将前述三大实践组合成一个生产可用的 Agent 入口：

```typescript
import {
  experimental_wrapLanguageModel,
  experimental_createMCPClient,
  generateText,
} from "ai";
import { Experimental_StdioMCPTransport } from "ai/mcp-stdio";
import { flagshipModel } from "./_shared/models";
import { createCacheMiddleware } from "./cache-middleware";
import { createStorage } from "unstorage";
import fsDriver from "unstorage/drivers/fs";

// 1. 缓存层
const cache = createStorage({ driver: fsDriver({ base: "./.cache/llm" }) });

// 2. 缓存 + 模型（实践一 + 实践三）
const cachedModel = experimental_wrapLanguageModel({
  model: flagshipModel,
  middleware: createCacheMiddleware(cache),
});

// 3. MCP 工具（实践二）
const mcpClient = await experimental_createMCPClient({
  transport: new Experimental_StdioMCPTransport({
    command: "npx",
    args: ["-y", "@my-org/mcp-tools"],
  }),
});
const tools = await mcpClient.tools();

// 4. 组合调用 —— 自动 Agent 循环
const result = await generateText({
  model: cachedModel,
  tools,
  maxSteps: 5,    // 允许最多 5 轮工具调用
  prompt: "分析项目依赖并生成 Markdown 格式的依赖健康度报告",
});

console.log(result.text);
await mcpClient.close();
```

**这一组合实现了：**
- ✅ 模型切换（云端 ↔ 本地）由环境变量决定
- ✅ 重复调用自动命中缓存
- ✅ 工具能力通过 MCP 协议解耦，可独立迭代发布
- ✅ Agent 多步推理（`maxSteps`）

---

## 五、设计原则总结

| 原则 | 实践 | 收益 |
|------|------|------|
| **无侵入式扩展** | 中间件模式包装模型 | 不修改业务代码即可添加缓存 / 日志 / 限流 |
| **环境驱动配置** | 环境变量切换模型 / 缓存后端 | 开发 / 测试 / 生产环境无缝切换 |
| **协议标准化** | MCP 统一工具接口 | 工具可组合、可发布、可跨项目复用 |
| **渐进式复杂性** | 从单文件示例到完整 Agent | 降低学习门槛，按需引入复杂度 |
| **声明式 Schema** | Zod 定义结构化输出 | 类型安全 + 运行时验证一体化 |
| **本地优先** | 支持本地模型（LM Studio / Ollama） | 降低开发成本与外部依赖 |
| **可观测性** | 中间件埋点 + evalite 评估 | 性能、成本、质量三维可量化 |

---

## 六、适用项目检查清单

在动手之前，先用这份清单核对你的 AI 项目：

- [ ] **是否需要多模型支持？** → 采用工厂模式 + 环境变量（实践三）
- [ ] **是否有重复 LLM 调用？**（开发 / 测试 / 评估）→ 引入缓存中间件（实践一）
- [ ] **是否需要外部工具集成？** → 采用 MCP 协议（实践二）
- [ ] **是否需要结构化输出？** → 使用 Zod Schema + `generateObject`
- [ ] **是否需要评估 AI 输出？** → 引入 [`evalite`](https://www.evalite.dev/) 评估框架
- [ ] **是否需要流式响应？** → 使用 `streamText` + SSE
- [ ] **是否需要 Agent 多步推理？** → `maxSteps` + 工具调用循环
- [ ] **是否需要降级容灾？** → Provider 级 try / catch fallback
- [ ] **是否需要离线开发？** → 本地模型 + 文件系统缓存

---

## 附录：参考链接

- AI Hero 源码：https://github.com/ai-hero-dev/ai-hero/
- Vercel AI SDK：https://sdk.vercel.ai/
- Model Context Protocol：https://modelcontextprotocol.io/
- unstorage：https://unstorage.unjs.io/
- LM Studio：https://lmstudio.ai/
- evalite（评估框架）：https://www.evalite.dev/

---

> **使用建议**：本文档的代码模板均经过 AI Hero 实战验证，可直接拷贝至项目落地；建议按"实践三 → 实践一 → 实践二"的顺序逐步引入，避免一次性引入过多复杂度。