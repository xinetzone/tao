# PDF → Markdown 工具评估报告（P4）

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

## 四、Windows 兼容性评估

| 工具 | Python 3.13 | 安装难度 | Windows 已知问题 |
|------|------------|---------|-----------------|
| **marker-pdf** | ⚠️ 需 `--only-binary` | 中等 | Pillow编译问题 |
| **MinerU** | ❌ 不支持 (ray限制) | 高 | 仅支持 3.10-3.12 |
| **Docling** | ✅ 支持 | 低 | 无明显问题 |
| **Nougat** | ⚠️ 未验证 | 中等 | 依赖PyTorch |
| **MarkItDown** | ✅ 支持 | 极低 | 无 |

> **关键发现**：MinerU 在 Windows + Python 3.13 环境下**无法安装**，这是当前环境的重要限制。

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

### marker-pdf（当前方案）
- **安装**：`pip install marker-pdf --only-binary :all:` 成功
- **转换测试**：《帛书老子注读》PDF 297页，成功转换
- **输出质量**：95/100分，91个H1标题，结构完整
- **耗时**：模型下载~15分钟，转换~2分钟

### Docling
- **安装**：`pip install docling` 成功，无依赖冲突
- **转换测试**：失败于 HuggingFace 模型下载阶段
- **失败原因**：`huggingface_hub` 在 Windows 非管理员/非开发者模式下无法创建符号链接
- **修复方案**：启用 Windows 开发者模式 或 以管理员身份运行
- **结论**：安装简单但 Windows 首次运行需要额外系统配置

### MinerU（Podman 容器实测）
- **环境**：Podman WSL + python:3.12 容器 + 24GB 内存
- **安装**：`magic-pdf` 基础包安装成功，但发现大量未声明依赖：
  - `opencv-python`（图像处理）
  - `libgl1` + `libglib2.0-0`（系统图形库，Linux 容器必备）
  - `openai`（LLM-aided 后处理）
  - `ultralytics`（YOLO 目标检测）
  - `doclayout-yolo`（文档布局检测）
  - `rapid-table`（表格识别）
- **PyTorch 优化**：使用 CPU 版本（192MB）替代 CUDA 版本（1.5GB+），安装时间从~30分钟缩短到~2分钟
- **转换测试**：**失败于模型加载阶段**
- **失败原因**：MinerU 依赖 HuggingFace 下载 ~2GB+ 预训练模型（YOLO、LayoutLMv3 等），Podman WSL 容器内无法稳定访问 HuggingFace/镜像站
- **关键发现**：即使使用 `hf-mirror.com` 镜像站，容器内网络仍受限，模型下载无法完成
- **耗时统计**：
  - 环境准备（容器启动、依赖安装）：~10分钟
  - 模型下载尝试：~20分钟（失败）
  - 缺失依赖逐个排查修复：~15分钟
- **结论**：MinerU 容器化部署可行，但模型下载是核心瓶颈。建议在具备稳定 HuggingFace/ModelScope 访问的环境中预先下载模型后打包镜像

### Podman 评估总结
| 维度 | 结果 | 说明 |
|------|------|------|
| **容器启动** | 成功 | Python 3.12 基础镜像运行正常 |
| **依赖安装** | 成功（有波折） | 发现 6 个隐藏依赖，需手动补齐 |
| **CPU 优化** | 显著有效 | torch CPU 版减少 ~1.3GB 下载 |
| **模型下载** | **失败** | 容器网络受限，无法访问模型仓库 |
| **实际转换** | 未执行 | 模型缺失导致无法进入推理阶段 |

> **核心教训**：MinerU 的容器化部署必须解决模型预置问题。推荐方案：在具备外网访问的环境中预先执行 `huggingface-cli download`，将模型打包进镜像或使用 Volume 挂载。

---

## 九、综合排名（AgentForge项目视角）

| 排名 | 工具 | 综合评分 | 推荐场景 | Windows 兼容性 |
|------|------|---------|---------|---------------|
| 1 | **marker-pdf** | 8.5/10 | 当前方案，古籍/书籍专用 | 良好（需--only-binary） |
| 2 | **Docling** | 7.5/10 | 通用首选，企业级稳定性 | 一般（需开发者模式） |
| 3 | **MinerU** | 6.5/10 | 高精度需求（Linux/Podman） | 差（容器内需预置模型） |
| 4 | **Nougat** | 6.5/10 | 学术论文专用 | 未验证 |
| 5 | **MarkItDown** | 5.0/10 | 快速文本提取 | 优秀 |

> **排名调整说明**：实际测试后 marker-pdf 上升至第一位，原因是其在当前 Windows + Python 3.13 环境下是唯一"即装即用"的高质量方案。Docling 降至第二位，因 Windows 符号链接问题增加了部署复杂度。

---

## 十、关键建议

### 短期（当前项目）
继续使用 **marker-pdf**，理由：
- 已在当前环境验证通过
- 已建立完整工具链（6个脚本）
- 古籍类文档转换质量优秀（95/100分）

### 中期（扩展场景）
1. **多格式处理需求**：评估 Docling（需解决 Windows 开发者模式问题）
2. **学术/公式密集文档**：评估 Nougat（需单独 Python 环境）
3. **扫描版/手写文档**：关注 MinerU Windows 兼容性进展

### 长期（架构层面）
1. ✅ **已完成**：在 Podman 容器中评估 MinerU（见下方结果）
   - 结论：容器化可行，但模型预置是关键前提
   - 方案：预下载模型打包镜像，或使用外部 Volume 挂载
2. 封装 **统一转换接口**，底层可切换不同引擎
3. **合规注意**：marker-pdf 的 GPL/研究许可在商业场景需额外授权

### Podman/MinerU 实操要点
| 步骤 | 关键操作 | 踩坑记录 |
|------|---------|---------|
| **容器创建** | `podman run -it -v /host:/data python:3.12 bash` | 基础镜像选择 `python:3.12` 而非 `python:3.12-slim`（避免缺少编译工具） |
| **PyTorch** | `pip install torch --index-url https://download.pytorch.org/whl/cpu` | **必须**指定 CPU 版本，否则自动安装 CUDA（+1.5GB） |
| **系统依赖** | `apt-get install -y libgl1 libglib2.0-0` | OpenCV 需要系统级图形库 |
| **隐藏依赖** | `pip install opencv-python openai ultralytics doclayout-yolo rapid-table` | `magic-pdf` 的 `setup.py` 未声明这些依赖 |
| **模型预置** | 预先下载到 `/tmp/models` 或挂载 Volume | 容器内 HuggingFace/镜像站访问不稳定 |
| **配置文件** | `echo '{"device-mode":"cpu"}' > /root/magic-pdf.json` | 缺少配置会报错 |

### 行动清单
- [x] 在 Linux/Docker 环境中评估 MinerU（Podman 完成，模型下载失败）
- [ ] 启用 Windows 开发者模式后重试 Docling 完整测试
- [ ] 调研 marker-pdf 商业授权流程（如需要）
- [ ] 设计统一转换接口抽象层
- [ ] 在具备外网的环境中预先下载 MinerU 模型，验证完整转换流程

---

*数据来源：GitHub官方仓库、OmniDocBench评测、实际安装测试*
