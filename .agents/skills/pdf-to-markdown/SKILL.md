---
name: pdf-to-markdown
version: 1.0.0
description: 将中文学术/古籍类PDF无损转换为结构化Markdown文件集，支持章节识别、跨页标题合并、并行转换
metadata: {"openclaw":{"requires":{"bins":["python3"],"packages":["pdfplumber","pypdfium2"]}}}
---

# PDF → Markdown 转换技能 (PDF to Markdown)

## 1. 技能唯一标识 (Skill ID)

`pdf-to-markdown`

## 2. 功能描述 (Description)

PDF 全文提取 + 章节结构分析 + Markdown 拆分转换。适用于中文学术/古籍类 PDF（含多级标题、注释、双栏排版）。

核心能力：

- **逐页文本提取**：基于 `pdfplumber` 全文抽取，区分扫描页（无文本）/文本页；
- **跨页标题合并**：消除 PDF 分页截断造成的章节标题碎片（如 `「五十一、不自生...其私（今」 + 「7章）」`）；
- **章节结构自动识别**：通过中文数字编号、篇章/章节/附录/前置内容四级层次正则匹配；
- **并行化 Markdown 生成**：`ThreadPoolExecutor` 并行写入多组章节，加速大批量转换；
- **JSON Schema 验证**：中间产物 `pdf_page_meta.json` 通过 schema 校验，及早暴露结构异常；
- **封面渲染**：基于 `pypdfium2`（不依赖 poppler）渲染首页为 PNG。

适用场景：

- 古籍/学术著作 PDF 数字化转录（如《帛书老子注读》81 章本）；
- 含「篇/章/节/附录」多级层次的中文文档结构化；
- 需要保留原始排版语义但输出可被 MkDocs/Sphinx 处理的 Markdown。

## 3. 输入输出参数定义 (I/O Parameters)

### 3.1 输入参数 (Input)

`pdf_extract.py`：

| 参数名称 | 类型 | 是否必填 | 默认值 | 说明 |
|----------|------|----------|--------|------|
| `pdf_path` | string (positional) | 是 | 无 | 待提取的 PDF 文件路径 |
| `--output-dir`, `-o` | string | 否 | PDF 同目录 | 中间产物输出目录 |
| `--page-range` | string | 否 | 全文 | 页码范围，形如 `1-100` |

`pdf_to_markdown.py`：

| 参数名称 | 类型 | 是否必填 | 默认值 | 说明 |
|----------|------|----------|--------|------|
| `meta_json` | string (positional) | 是 | 无 | `pdf_page_meta.json` 路径 |
| `raw_txt` | string (positional) | 是 | 无 | `pdf_raw_text.txt` 路径 |
| `--output-dir`, `-o` | string | 是 | 无 | Markdown 输出目录 |
| `--cover` | string | 否 | 无 | 封面图片路径（可选） |

### 3.2 输出参数 (Output)

`pdf_extract.py` 在 `output_dir` 下产出：

```text
<output_dir>/
├── pdf_raw_text.txt          # 全文逐页文本（含 ===== PAGE N ===== 分隔符）
├── pdf_structure_analysis.md # 结构分析报告（Mermaid 图 + 章节表）
├── pdf_page_meta.json        # 结构化元数据（符合 page-meta.schema.json）
└── <pdf_stem>-cover.png      # 封面图片
```

`pdf_to_markdown.py` 在 `output_dir` 下产出基于章节结构拆分的 Markdown 文件集（具体目录布局由调用方的章节模型决定）。

## 4. 依赖项说明 (Dependencies)

- **Python**: `>=3.10`
- **第三方包**:
  - `pdfplumber>=0.11`
  - `pypdfium2>=5.0`
  - `jsonschema`（可选，缺失时自动退回轻量断言验证）

## 5. 部署要求 (Deployment)

```bash
pip install pdfplumber pypdfium2
# 可选：pip install jsonschema
```

无需任何外部服务。`pypdfium2` 自带原生库，不依赖 poppler/Ghostscript。

### 快速开始

`{baseDir}` 是 agent 框架在运行时自动替换的变量，指向当前 skill 目录的绝对路径（即 `skills/pdf-to-markdown/`）。

```bash
# 步骤1：提取 PDF 文本并分析结构
python3 {baseDir}/scripts/pdf_extract.py <pdf_path> --output-dir <dir>

# 步骤2：将提取结果转换为 Markdown 文件集
python3 {baseDir}/scripts/pdf_to_markdown.py <meta_json_path> <raw_txt_path> --output-dir <dir>
```

## 6. 错误处理规范 (Error Handling)

| 错误码/场景 | 异常场景 | 应对策略 |
|--------|----------|----------|
| `FontBBox` 警告 | pdfminer 内部无害 warning | 已通过 `warnings.filterwarnings("ignore")` 自动抑制 |
| 扫描页（无可提取文本） | PDF 中嵌入图像而非文字 | 标记为 `[SCAN_PAGE_NO_TEXT]`，并在 `page-meta.json.scan_pages` 中列出 |
| 单页提取异常 | 字体损坏、加密区段 | 写入 `[EXTRACT_ERROR]` 占位，不中断整体流程 |
| 编码异常 | 非 UTF-8 字符 | 强制 UTF-8 写入，无法解码字符以占位符替代 |
| Schema 验证失败 | meta JSON 结构缺失字段 | 报告具体字段错误，退出码非零 |
| 缺失 `jsonschema` 库 | 环境未安装可选依赖 | 自动退回基本断言验证，打印 `[INFO] jsonschema 不可用` |
| PDF 文件不存在 | 路径错误 | 写入 stderr 并返回退出码 `1` |

## 7. 版本记录 (Changelog)

- **v1.0.0** (2026-05-27): 初始版本，从《帛书老子注读》PDF 转 Markdown 任务沉淀，提供参数化 CLI、跨页标题合并、JSON Schema 验证与并行写入能力。
