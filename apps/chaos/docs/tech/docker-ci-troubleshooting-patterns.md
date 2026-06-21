# Docker CI 故障排查模式 — 萃取自 Containerfile.test 构建修复

> **来源**：`task-summary-docker-ci-build-fix-20260609.md`  
> **场景**：Docker 构建失败、CI 流水线报错、Python 项目容器化

---

## 1. 调用链追踪法

**通用流程**：

```
错误签名 → 追踪调用链至配置源头 → 理解时序 → 最小修复
```

**实战数据**（TRAE 仓库 Containerfile.test）：

```
FileNotFoundError: src/taolib/_version.py
       ↓ 追踪
uv sync → scikit_build_core 构建 → setuptools_scm 写入 _version.py
       ↓ 定位
Step 12: RUN sync-test-deps.sh  ← 需要 src/taolib/ 存在
Step 13: COPY . .                ← 源码在此之后才拷贝
       ↓ 结论
Step 12 ↔ Step 13 之间存在数据依赖断裂
```

**可复用规则**：
- Docker 构建失败 → 第一检查项永远是 `COPY` 与 `RUN` 的顺序
- `FileNotFoundError` 在容器内 → 检查目标目录是否已在构建上下文中
- 追踪到构建工具（scikit-build-core / setuptools_scm）→ 检查其写入路径的目录是否存在

---

## 2. 最小影响修复决策三角

**场景**：发现根因后，有多个可能的修复方案。

**决策模型**：

```
方案 A：调整顺序（改动大，破坏缓存）
方案 B：跳过触发（改动多文件，需补后续步骤）
方案 C：预创建占位（1 行代码，不破坏任何既有流程）← 选中
```

**评估矩阵**：

| 维度 | 方案 A | 方案 B | 方案 C |
|------|--------|--------|--------|
| 改动行数 | 多行重排 | 2 文件 | **1 行** |
| 破坏缓存 | 是 | 否 | **否** |
| 需额外步骤 | 否 | 是 | **否** |
| 语义变更 | 有 | 有 | **无** |

**可复用规则**：
- 修复 Docker 构建问题时，优先选择不改变层缓存策略的方案
- 如果修复需要重排 `COPY/RUN` 顺序，检查是否有更轻量的替代方案
- 占位文件 + 后续覆盖 是 Docker 多阶段构建中成本最低的时序修复手段

---

## 3. setuptools_scm 容器化反向模式

**问题**：`setuptools_scm` 在容器内运行，无 `.git` 目录时行为与本地不同。

**TRAE 实践**：

| 环境 | `.git` | `setuptools_scm` 行为 |
|------|--------|----------------------|
| 本地开发 | 存在 | 从 git tag 推导版本号 |
| CI 容器 | **不存在** | `fallback_version = "0.0.0"` |

**结论**：对测试环境无影响（测试容器不需要精确版本号），但需要确保 `src/taolib/` 目录在构建时存在。

**可复用规则**：
- Python 项目容器化时，确认 `setuptools_scm` 的 `fallback_version` 是否已显式配置
- 如果 CI 容器不需要 `.git`，确保构建工具的写入路径在 `COPY` 源码之前已创建
- 生产镜像与测试镜像的 `setuptools_scm` 行为可能不同，建议在 `pyproject.toml` 中显式声明 `fallback_version`

---

## 4. Docker 构建时序依赖自检

**适用于**：任何涉及 `COPY` + `RUN` 的 Dockerfile/Containerfile 审查。

- [ ] 每个 `RUN` 步骤所需文件是否在之前的 `COPY` 中已引入？
- [ ] 是否存在 `RUN` 依赖 `COPY . .` 之后才有的文件？
- [ ] 如果存在时序依赖，是否可以用「预创建占位 + 后续覆盖」绕过？
- [ ] 修复是否保持了 Docker 层缓存的有效性？
- [ ] 修复后的构建流程语义是否与原设计一致？

---

*萃取完毕 | 2026-06-21 | 来源：06-09 Docker CI 构建修复任务*
