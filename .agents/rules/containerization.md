# 容器化规则

## 核心约束

- **大型评估选品测试（large-scale evaluation / product selection testing）场景**，必须优先使用 Podman 容器化方案。
- 禁止在此类场景中默认选用 Docker 或其他容器运行时，除非有明确的技术不可行证据。

## 适用场景

- PDF 处理工具评估（如 MinerU、marker-pdf 等）
- 依赖复杂 Linux 原生环境的工具链对比测试
- 需要隔离环境的批量性能基准测试

## 技术依据

- 项目已采用 Podman 原生格式（`Containerfile`、`Containerfile.test`、`.containerignore`）
- Podman 无守护进程、rootless 运行、OCI 标准兼容
- Windows 环境下通过 `podman machine` 提供 Linux 容器能力

## 命令参考

| 操作 | 命令 |
|------|------|
| 构建镜像 | `podman build -t <name> -f Containerfile .` |
| 构建测试镜像 | `podman build -t <name>-test -f Containerfile.test .` |
| 运行容器 | `podman run --rm -it <name>` |

## 评估模板库

项目根目录提供预置的评估容器模板，覆盖主要 PDF 工具：

| 模板 | 用途 | 构建命令 |
|------|------|----------|
| `containers/eval/Containerfile.base` | 通用评估基础镜像 | `podman build -t eval-base -f containers/eval/Containerfile.base .` |
| `containers/eval/Containerfile.marker` | marker-pdf 评估 | `podman build -t eval-marker -f containers/eval/Containerfile.marker .` |
| `containers/eval/Containerfile.docling` | Docling 评估 | `podman build -t eval-docling -f containers/eval/Containerfile.docling .` |
| `containers/eval/Containerfile.mineru` | MinerU 评估（含踩坑注释） | `podman build -t eval-mineru -f containers/eval/Containerfile.mineru .` |

评估统一基线：`python:3.12` + CPU 推理 + 24GB 内存建议。
