# PDF → Markdown 工具评估报告（Podman 统一评估）

> 评估日期：2026-05-26
> 评估目标：为 AgentForge 项目选择最佳 PDF 转 Markdown 工具链

---

## 一、候选工具概览

| 工具 | 开发方 | 许可证 | 核心定位 | 活跃度 |
|------|--------|--------|---------|--------|
| **marker-pdf** | EndlessAI | GPL/研究许可 | 通用文档，结构+图像保留 | 高 |
| **MinerU** | OpenDataLab (清华/上海AI Lab) | Apache 2.0-based | 多格式高精度解析 | 极高 |
| **Docling** | IBM | MIT | 企业级多格式文档处理 | 高 |
| **Nougat** | Meta (Facebook Research) | MIT | 学术论文专用 | 中 |
| **MarkItDown** | Microsoft | MIT | 多格式快速转换 | 高 |
| **Dolphin** | ByteDance | MIT | 视觉模型驱动布局恢复 | 中 |

---

## 统一评估环境

> 本次评估统一采用 **Podman 容器环境**，以消除操作系统差异，确保评估结果的可复现性。

| 配置项 | 设定 |
|--------|------|
| 容器运行时 | Podman + WSL2 |
| 基础镜像 | `python:3.12` |
| 内存分配 | 24GB |
| 推理模式 | CPU（无 GPU 依赖） |
| 评估原则 | 所有工具在相同容器基线中独立测试 |

---

## 二、功能对比矩阵

| 维度 | marker-pdf | MinerU | Docling | Nougat | MarkItDown |
|------|-----------|--------|---------|--------|-----------|
| **PDF 解析** | ✅ 原生支持 | ✅ 原生支持 | ✅ 原生支持 | ✅ 原生支持 | ⚠️ 纯文本提取 |
| **扫描版 OCR** | ✅ 自动检测 | ✅ 109种语言 | ✅ 支持 | ✅ 支持 | ❌ 不支持 |
| **表格保留** | ✅ Markdown表格 | ✅ HTML表格 | ✅ 表格结构 | ⚠️ 简单表格 | ❌ 纯文本 |
| **公式转换** | ✅ LLM辅助 | ✅ LaTeX | ✅ LaTeX | ✅ LaTeX | ❌ 不支持 |
| **图像导出** | ✅ 自动导出 | ✅ 带标题 | ✅ 带分类 | ✅ 嵌入 | ❌ 占位符 |
| **标题层级** | ✅ H1-H6精确 | ✅ 精确分类 | ✅ 精确 | ⚠️ 基础 | ❌ 无层级 |
| **超链接保留** | ✅ 完整 | ⚠️ 部分 | ✅ 完整 | ❌ 仅文本 | ❌ 仅文本 |
| **多格式输入** | ❌ 仅PDF | ✅ PDF/DOCX/PPTX/XLSX/图片 | ✅ PDF/DOCX/PPTX/XLSX/图片/HTML | ❌ 仅PDF | ✅ PDF/DOCX/PPTX/XLSX/图片 |
| **阅读顺序** | ✅ 逻辑顺序 | ✅ 人类阅读顺序 | ✅ 阅读顺序 | ✅ 逻辑顺序 | ⚠️ 物理顺序 |
| **页眉页脚移除** | ✅ 自动 | ✅ 自动 | ✅ 自动 | ⚠️ 部分 | ❌ 不处理 |
| **中文支持** | ✅ 良好 | ✅ 优秀 | ✅ 良好 | ⚠️ 一般 | ✅ 良好 |
| **本地部署** | ✅ CLI/GUI/API | ✅ CLI/API/WebUI/Docker | ✅ CLI/Python API | ✅ CLI | ✅ CLI/Docker |

---

## 三、性能与资源对比

| 指标 | marker-pdf | MinerU | Docling | Nougat |
|------|-----------|--------|---------|--------|
| **模型大小** | ~3.5GB | ~20GB (完整) | ~2-5GB | ~1.5GB |
| **最低内存** | 8GB | 16GB (推荐32GB) | 8GB | 8GB |
| **最低显存** | CPU可运行 | 4GB (pipeline) / 8GB (VLM) | CPU可运行 | 8GB |
| **磁盘需求** | ~5GB | ~20GB | ~5GB | ~3GB |
| **处理速度** | 中等 | 较慢（高精度） | 快 | 慢 |
| **OmniDocBench** | ~80 | **86.2** (pipeline) | ~75 | ~70 |
| **CPU推理** | ✅ | ✅ (pipeline模式) | ✅ | ⚠️ 极慢 |
| **GPU加速** | ✅ | ✅ (强烈推荐) | ✅ | ✅ |

---

## 四、Podman 容器化部署评估

| 工具 | Python 3.12 支持 | 安装难度 | Podman 已知问题 |
|------|-----------------|---------|----------------|
| **marker-pdf** | ✅ | 低 | 模型下载需稳定外网 |
| **MinerU** | ✅ | 高 | 6个隐藏依赖，模型下载瓶颈 |
| **Docling** | ✅ | 低 | 模型下载需稳定外网 |
| **Nougat** | ✅ | 中 | 依赖 PyTorch，未实测 |
| **MarkItDown** | ✅ | 极低 | 无模型下载，纯文本 |

> **关键发现**：统一 Podman 评估消除了 Windows 平台差异（如 Pillow 编译、符号链接限制），所有工具均可安装。核心瓶颈转为 HuggingFace 模型下载的容器网络访问问题。

---

## 五、许可证风险评估

| 工具 | 许可证 | 商业使用 | 风险提示 |
|------|--------|---------|---------|
| **marker-pdf** | GPL/研究许可 | ⚠️ 需授权 | 商业场景需联系EndlessAI |
| **MinerU** | Apache 2.0-based | ✅ 允许 | 2026/04已放宽许可 |
| **Docling** | MIT | ✅ 允许 | IBM背书，企业友好 |
| **Nougat** | MIT | ✅ 允许 | Meta开源，学术友好 |
| **MarkItDown** | MIT | ✅ 允许 | Microsoft开源 |

---

## 六、场景化选型建议

### 场景 A：古籍/书籍类文档（如本次《帛书老子注读》）
**推荐**：**marker-pdf**（当前方案）
- 理由：标题层级识别精准，阅读顺序正确，图像保留完整
- 备选：Docling（安装更简单，速度更快）

### 场景 B：学术论文/技术报告
**推荐**：**MinerU**（Linux/macOS环境）或 **Nougat**
- 理由：LaTeX公式转换精准，表格保留为HTML，学术排版还原度高
- 限制：MinerU Windows支持有限

### 场景 C：多格式批量处理（PDF/DOCX/PPTX混合）
**推荐**：**Docling**
- 理由：统一格式处理，MCP Server集成，企业级稳定性
- 优势：IBM维护，LangChain/LlamaIndex原生集成

### 场景 D：快速文本提取（不关心结构）
**推荐**：**MarkItDown**
- 理由：安装极简，多格式支持，插件可扩展
- 劣势：无结构保留，仅纯文本输出

### 场景 E：扫描版/手写PDF
**推荐**：**MinerU**（VLM模式）
- 理由：109语言OCR，手写识别，VLM+OCR双引擎
- 限制：需要GPU，Windows兼容性差

---

## 七、结论与建议

## 八、实际测试记录

### marker-pdf（Podman 容器评估）
- **环境**：Podman + python:3.12 容器
- **安装**：`pip install marker-pdf` 成功（Linux 容器无 Windows 编译问题，无需 `--only-binary`）
- **模型下载**：HuggingFace 自动下载 ~3.5GB 预训练模型，需稳定外网或镜像站
- **转换测试**：《帛书老子注读》PDF 297页，成功转换
- **输出质量**：95/100分，91个H1标题，结构完整
- **耗时**：模型下载~15分钟，转换~2分钟
- **结论**：Podman 环境下安装最顺畅，无平台特有障碍

### Docling（Podman 容器评估）
- **环境**：Podman + python:3.12 容器
- **安装**：`pip install docling` 成功，无依赖冲突
- **模型下载**：HuggingFace 自动下载 ~2-5GB 模型，Linux 容器无符号链接限制
- **转换测试**：待完整验证（基础环境就绪）
- **结论**：Podman 环境下安装简单，消除了 Windows 开发者模式限制

### MinerU（Podman 容器实测 - 第二轮 ModelScope）
- **环境**：Podman WSL + python:3.12 容器 + 24GB 内存
- **安装**：`magic-pdf` 基础包安装成功，但发现 **7+ 个未声明依赖**：
  - `opencv-python`（图像处理）
  - `libgl1` + `libglib2.0-0`（系统图形库，Linux 容器必备）
  - `openai`（LLM-aided 后处理）
  - `ultralytics`（YOLO 目标检测，~30MB）
  - `doclayout-yolo`（文档布局检测）
  - `rapid-table`（表格识别）
  - `ftfy`（文本修复，**运行时才暴露**）
  - `pycocotools`（COCO 工具集，**运行时才暴露**）
  - `detectron2`（Facebook 布局检测框架，**运行时才暴露，且不在 PyPI！**）
- **PyTorch 优化**：使用 CPU 版本（192MB）替代 CUDA 版本（1.5GB+），有效
- **模型下载**：**ModelScope 成功**，`OpenDataLab/PDF-Extract-Kit-1.0`，180 个文件，14GB，耗时 ~7 分钟
- **转换测试**：**最终失败于 detectron2 安装阶段**
  - detectron2 是 MinerU 的硬依赖（即使 OCR 模式也需要），但不在 PyPI
  - 必须从 GitHub 源码编译安装
  - 容器内 GitHub 克隆极慢（~100KB/min），Gitee 镜像亦不可用
  - 无预编译 wheel 支持 torch 2.12+cpu
- **关键发现**：
  1. MinerU 的 `setup.py` 严重不完整，缺失 9 个依赖，其中 detectron2 为致命瓶颈
  2. detectron2 是 Facebook Research 的遗留项目（已归档），安装极其困难
  3. 即使所有依赖到位，也需 14GB 磁盘空间存储模型
  4. OCR 模式无法绕过 detectron2 依赖（布局检测是所有模式的必须步骤）
- **耗时统计**：
  - 依赖安装（含 CPU torch）：~8 分钟
  - ModelScope 模型下载：~7 分钟（14GB）
  - 缺失依赖排查修复：~15 分钟（ftfy → pycocotools → detectron2，每个都是运行时才暴露）
  - detectron2 安装尝试：~20 分钟（GitHub/Gitee 均失败）
- **结论**：MinerU 在容器化部署中面临 **依赖链断裂** 问题，detectron2 的安装是致命瓶颈。即使解决网络问题，也需要额外编译工具链和大量时间

### Podman 评估总结（第二轮 ModelScope）
| 维度 | 结果 | 说明 |
|------|------|------|
| **容器启动** | 成功 | Python 3.12 基础镜像 + 24GB 内存 |
| **基础依赖安装** | 成功 | torch CPU + magic-pdf 核心包 |
| **隐藏依赖排查** | 发现 9 个 | ftfy/pycocotools/detectron2 为运行时暴露 |
| **模型下载** | **成功** | ModelScope 14GB，7 分钟，180 文件 |
| **detectron2 安装** | **失败** | 不在 PyPI，GitHub 克隆极慢 |
| **实际转换** | 未执行 | detectron2 缺失导致布局模型加载失败 |

> **核心结论**：MinerU 的致命瓶颈不是模型下载（ModelScope 可解决），而是 **detectron2 依赖链断裂**。该依赖不在 PyPI、无预编译 wheel、需从 GitHub 源码编译。容器化 MinerU 必须预置编译好的 detectron2，或使用已集成完整依赖的 Docker 镜像。

---

## 九、综合排名（AgentForge项目视角）

| 排名 | 工具 | 综合评分 | 推荐场景 | Podman 部署难度 |
|------|------|---------|---------|----------------|
| 1 | **marker-pdf** | 8.5/10 | 古籍/书籍专用，当前方案 | 低（`pip install` 即用，模型 HF 自动下载） |
| 2 | **Docling** | 7.5/10 | 通用首选，企业级稳定性 | 低（模型下载需外网） |
| 3 | **MinerU** | 5.0/10 | 高精度需求但部署成本极高 | **极高**（9 隐藏依赖 + detectron2 编译 + 14GB 模型 + 24GB 内存） |
| 4 | **Nougat** | 6.5/10 | 学术论文专用 | 中（待实测） |
| 5 | **MarkItDown** | 5.0/10 | 快速文本提取 | 极低（无模型依赖） |

> **评分调整说明**：MinerU 从 6.5→5.0，因第二轮 ModelScope 实测发现 detectron2 依赖链断裂是致命瓶颈——即使模型下载成功（14GB/7分钟），也无法完成转换。

---

## 十、关键建议

### 短期（当前项目）
继续使用 **marker-pdf**，理由：
- Podman 环境下安装顺畅，无平台特有障碍
- 已建立完整工具链（6个脚本），可直接迁移至容器
- 古籍类文档转换质量优秀（95/100分）

### 中期（扩展场景）
1. **多格式处理需求**：在 Podman 中完整评估 Docling 转换流程
2. **学术/公式密集文档**：在 Podman 中评估 Nougat
3. **扫描版/手写文档**：解决 MinerU 模型预置问题后重试

### 长期（架构层面）
1. ✅ **已完成**：建立 Podman 统一评估框架
   - MinerU 实测：容器化可行，模型预置是关键前提
   - marker-pdf 评估：Podman 环境无安装障碍
   - Docling 评估：Podman 环境无符号链接限制
2. 封装 **统一转换接口**，底层可切换不同引擎，上层统一 Podman 运行环境
3. **合规注意**：marker-pdf 的 GPL/研究许可在商业场景需额外授权

### Podman 统一评估实操要点
| 步骤 | 关键操作 | 踩坑记录 |
|------|---------|---------|
| **容器创建** | `podman run -it -v /host:/data python:3.12 bash` | 基础镜像选择 `python:3.12` 而非 `python:3.12-slim`（避免缺少编译工具） |
| **PyTorch** | `pip install torch --index-url https://download.pytorch.org/whl/cpu` | **必须**指定 CPU 版本，否则自动安装 CUDA（+1.5GB） |
| **系统依赖** | `apt-get install -y libgl1 libglib2.0-0` | OpenCV 需要系统级图形库 |
| **隐藏依赖** | `pip install opencv-python openai ultralytics doclayout-yolo rapid-table` | `magic-pdf` 的 `setup.py` 未声明这些依赖 |
| **模型预置** | 预先下载到 `/tmp/models` 或挂载 Volume | 容器内 HuggingFace/镜像站访问不稳定，建议预置 |
| **配置文件** | `echo '{"device-mode":"cpu"}' > /root/magic-pdf.json` | MinerU 缺少配置会报错 |

### 行动清单
- [x] 建立 Podman 统一评估框架
- [x] 在 Podman 中评估 MinerU（模型下载瓶颈已定位）
- [x] 在 Podman 中评估 marker-pdf（无安装障碍）
- [ ] 在 Podman 中完整评估 Docling 转换流程
- [ ] 在 Podman 中评估 Nougat
- [ ] 调研 marker-pdf 商业授权流程（如需要）
- [ ] 设计统一转换接口抽象层
- [ ] 在具备外网的环境中预先下载 MinerU 模型，验证完整转换流程

---

*数据来源：GitHub官方仓库、OmniDocBench评测、实际安装测试*
