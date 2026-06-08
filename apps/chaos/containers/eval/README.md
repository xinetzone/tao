# Containerfile 评估模板库

本目录包含用于大型评估选品测试的 Podman 容器模板，主要用于 PDF 处理工具的对比测试。

## 模板列表

| 模板 | 用途 | 工具 |
|------|------|------|
| `Containerfile.base` | 通用评估基础镜像 | Python 3.13 + uv + 基础系统依赖 |
| `Containerfile.marker` | marker-pdf 评估环境 | marker-pdf |
| `Containerfile.docling` | Docling 评估环境 | docling |
| `Containerfile.mineru` | MinerU 评估环境 | magic-pdf (MinerU) |

## 构建命令

```bash
# 构建基础镜像
podman build -t eval-base -f containers/eval/Containerfile.base .

# 构建 marker-pdf 评估镜像
podman build -t eval-marker -f containers/eval/Containerfile.marker .

# 构建 Docling 评估镜像
podman build -t eval-docling -f containers/eval/Containerfile.docling .

# 构建 MinerU 评估镜像
podman build -t eval-mineru -f containers/eval/Containerfile.mineru .
```

## 运行方式

```bash
# 运行交互式评估环境（挂载本地 data 目录）
podman run --rm -it -v ./data:/eval/data eval-marker

# MinerU 需要更多内存
podman run --rm -it -m 24g -v ./data:/eval/data eval-mineru
```

## 评估基线

- **基础镜像**: `python:3.13-slim`
- **包管理**: `uv`
- **资源建议**: CPU 推理模式，建议 24GB+ 内存

## 目录结构约定

```
containers/eval/
├── Containerfile.base      # 基础模板
├── Containerfile.marker    # marker-pdf 专用
├── Containerfile.docling   # Docling 专用
├── Containerfile.mineru    # MinerU 专用
└── README.md              # 本说明文件
```

## 构建优化建议

1. **缓存层优化**: 先复制依赖定义文件，再复制源码，以利用 Docker/Podman 缓存
2. **多阶段构建**: 对于生产环境，使用多阶段构建减小镜像体积
3. **镜像清理**: 定期清理未使用的镜像和容器

## 注意事项

- MinerU 的 detectron2 依赖需要从 GitHub 源码编译，构建时间较长
- 建议使用 rootless Podman 运行以提高安全性
- 评估数据建议通过 volume 挂载，避免复制到镜像中
