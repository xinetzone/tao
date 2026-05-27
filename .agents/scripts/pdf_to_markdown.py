"""
PDF → Markdown 全流程转换脚本

功能：
    - 环境自动检测与安装
    - 支持单文件/分批转换
    - 自动合并输出
    - 转换质量检查

用法:
    python pdf_to_markdown.py <input.pdf> [options]

示例:
    # 基础转换（自动判断是否需要分批）
    python pdf_to_markdown.py book.pdf

    # 强制分批转换
    python pdf_to_markdown.py book.pdf --batch-size 20

    # 指定输出
    python pdf_to_markdown.py book.pdf --output ./output/book.md
"""

import argparse
import importlib.util
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --- 配置区 ---
DEFAULT_BATCH_SIZE = 30
MARKER_CMD = "marker_single"


# --- 工具函数 ---

def check_marker_installed() -> bool:
    """检查 marker-pdf 是否已安装"""
    return shutil.which(MARKER_CMD) is not None


def install_marker_pdf() -> bool:
    """安装 marker-pdf（Windows 使用 --only-binary 策略）"""
    print("[安装] marker-pdf 未安装，开始安装...")
    cmd = [sys.executable, "-m", "pip", "install", "marker-pdf", "--only-binary", ":all:"]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        print("[安装] marker-pdf 安装成功")
        return True
    else:
        print(f"[安装错误] {result.stderr[:500]}")
        return False


def get_pdf_page_count(pdf_path: str) -> int:
    """获取 PDF 总页数"""
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except ImportError:
        print("[错误] 需要 pypdfium2 来获取页数")
        sys.exit(1)


def convert_all_pages(pdf_path: str, output_dir: str) -> bool:
    """一次性转换全部页码"""
    print("[转换] 执行全页转换...")
    cmd = [
        MARKER_CMD,
        pdf_path,
        "--output_dir", output_dir,
        "--output_format", "markdown",
        "--disable_tqdm",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"[转换错误] {result.stderr[:500]}")
        return False
    return True


def convert_page_range(pdf_path: str, start: int, end: int, output_dir: str) -> bool:
    """转换指定页码范围"""
    range_str = f"{start}-{end - 1}"
    cmd = [
        MARKER_CMD,
        pdf_path,
        "--output_dir", output_dir,
        "--output_format", "markdown",
        "--page_range", range_str,
        "--disable_tqdm",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return result.returncode == 0


def merge_outputs(source_dirs: list, final_output: str) -> int:
    """合并多个目录的 Markdown 文件到单一文件"""
    total_files = 0
    with open(final_output, "w", encoding="utf-8") as out:
        out.write(f"# {Path(final_output).stem}\n\n")
        out.write("> 由 marker-pdf 自动转换生成\n\n---\n\n")

        for source_dir in source_dirs:
            md_files = sorted(Path(source_dir).rglob("*.md"))
            for md_file in md_files:
                content = md_file.read_text(encoding="utf-8")
                out.write(content)
                out.write("\n\n---\n\n")
                total_files += 1

    return total_files


def quality_check(md_file: str, original_pdf: str) -> dict:
    """对转换结果进行基础质量检查"""
    stats = {
        "file_size": os.path.getsize(md_file),
        "line_count": 0,
        "char_count": 0,
        "h1_count": 0,
        "h2_count": 0,
        "empty_lines": 0,
        "warnings": [],
    }

    with open(md_file, "r", encoding="utf-8") as f:
        for line in f:
            stats["line_count"] += 1
            stats["char_count"] += len(line)
            stripped = line.strip()
            if not stripped:
                stats["empty_lines"] += 1
            elif stripped.startswith("# ") and not stripped.startswith("## "):
                stats["h1_count"] += 1
            elif stripped.startswith("## "):
                stats["h2_count"] += 1

    # 质量阈值检查
    if stats["file_size"] < 1000:
        stats["warnings"].append("输出文件过小，可能内容缺失")
    if stats["h1_count"] == 0:
        stats["warnings"].append("未检测到一级标题，结构可能损坏")
    if stats["char_count"] < 500:
        stats["warnings"].append("字符数过少，可能转换失败")

    return stats


def main():
    parser = argparse.ArgumentParser(description="PDF → Markdown 全流程转换")
    parser.add_argument("pdf_path", help="输入 PDF 文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出 Markdown 文件路径")
    parser.add_argument("--batch-size", type=int, default=0,
                        help="分批大小（0=自动判断，默认>100页自动分批）")
    parser.add_argument("--work-dir", default=None, help="临时工作目录")
    parser.add_argument("--skip-check", action="store_true", help="跳过环境检查")
    parser.add_argument("--keep-temp", action="store_true", help="保留临时文件")
    args = parser.parse_args()

    # 1. 检查输入文件
    if not os.path.exists(args.pdf_path):
        print(f"[错误] 文件不存在: {args.pdf_path}")
        sys.exit(1)

    pdf_path = os.path.abspath(args.pdf_path)
    pdf_name = Path(pdf_path).stem

    # 2. 检查/安装环境
    if not args.skip_check:
        if not check_marker_installed():
            if not install_marker_pdf():
                print("[错误] marker-pdf 安装失败，请手动安装")
                sys.exit(1)

    # 3. 获取 PDF 页数，决定转换策略
    total_pages = get_pdf_page_count(pdf_path)
    print(f"[信息] PDF 总页数: {total_pages}")

    batch_size = args.batch_size
    if batch_size == 0:
        batch_size = 30 if total_pages > 100 else total_pages

    use_batch = batch_size < total_pages

    # 4. 准备输出路径
    if args.output:
        final_output = os.path.abspath(args.output)
    else:
        final_output = os.path.join(os.path.dirname(pdf_path), f"{pdf_name}.md")

    if args.work_dir:
        work_dir = args.work_dir
    else:
        work_dir = tempfile.mkdtemp(prefix="pdf2md_")

    os.makedirs(work_dir, exist_ok=True)
    print(f"[信息] 工作目录: {work_dir}")
    print(f"[信息] 输出文件: {final_output}")

    # 5. 执行转换
    source_dirs = []
    if use_batch:
        num_batches = math.ceil(total_pages / batch_size)
        print(f"[信息] 分批转换: {num_batches} 批，每批 {batch_size} 页")

        for i in range(num_batches):
            start = i * batch_size
            end = min(start + batch_size, total_pages)
            batch_dir = os.path.join(work_dir, f"batch_{i + 1:03d}")
            os.makedirs(batch_dir, exist_ok=True)

            print(f"[{i + 1}/{num_batches}] 转换页码 {start}-{end - 1}...")
            success = convert_page_range(pdf_path, start, end, batch_dir)
            if success:
                source_dirs.append(batch_dir)
            else:
                print(f"  [警告] 批次 {i + 1} 转换失败，已跳过")
    else:
        print("[信息] 执行全页转换...")
        success = convert_all_pages(pdf_path, work_dir)
        if success:
            source_dirs.append(work_dir)
        else:
            print("[错误] 转换失败")
            sys.exit(1)

    if not source_dirs:
        print("[错误] 所有批次转换均失败")
        sys.exit(1)

    # 6. 合并输出
    print("[合并] 合并所有输出...")
    total_files = merge_outputs(source_dirs, final_output)
    print(f"[合并] 已合并 {total_files} 个文件")

    # 7. 质量检查
    print("[质检] 执行质量检查...")
    stats = quality_check(final_output, pdf_path)

    print(f"\n{'=' * 40}")
    print("转换完成报告")
    print(f"{'=' * 40}")
    print(f"输出文件: {final_output}")
    print(f"文件大小: {stats['file_size']:,} 字节")
    print(f"总行数: {stats['line_count']:,}")
    print(f"总字符: {stats['char_count']:,}")
    print(f"一级标题: {stats['h1_count']}")
    print(f"二级标题: {stats['h2_count']}")

    if stats["warnings"]:
        print(f"\n⚠️ 质量警告:")
        for w in stats["warnings"]:
            print(f"  - {w}")
    else:
        print("\n✅ 质量检查通过")

    # 8. 清理临时文件
    if not args.keep_temp and not args.work_dir:
        shutil.rmtree(work_dir)
        print(f"\n[清理] 已删除临时目录: {work_dir}")

    print(f"\n✅ 转换完成: {final_output}")


if __name__ == "__main__":
    main()
