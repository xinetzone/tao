"""
PDF 分批转 Markdown 脚本（解决大 PDF 内存占用问题）

用法:
    python pdf_to_markdown_batch.py <input.pdf> [--batch-size N] [--output-dir DIR]

示例:
    python pdf_to_markdown_batch.py book.pdf --batch-size 20 --output-dir ./output
"""

import argparse
import math
import os
import subprocess
import sys
from pathlib import Path


def get_pdf_page_count(pdf_path: str) -> int:
    """获取 PDF 总页数（使用 pypdfium2，marker-pdf 已依赖）"""
    try:
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except ImportError:
        print("错误：需要 pypdfium2 来获取页数。请运行 pip install pypdfium2")
        sys.exit(1)


def convert_page_range(pdf_path: str, start: int, end: int, output_dir: str) -> str:
    """转换指定页码范围"""
    range_str = f"{start}-{end - 1}"  # marker_single 使用 0-based 索引
    cmd = [
        "marker_single",
        pdf_path,
        "--output_dir",
        output_dir,
        "--output_format",
        "markdown",
        "--page_range",
        range_str,
        "--disable_tqdm",
    ]
    print(f"  转换页码 {range_str} -> {output_dir}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"  警告：页码 {range_str} 转换出现错误")
        print(result.stderr[:500])
    return output_dir


def merge_batch_outputs(batch_dirs: list, final_output: str) -> None:
    """合并所有分批输出为一个 Markdown 文件"""
    print(f"\n合并 {len(batch_dirs)} 个批次到最终文件...")
    with open(final_output, "w", encoding="utf-8") as out:
        out.write("# PDF 转换结果\n\n")
        out.write("> 由 marker-pdf 分批转换合并生成\n\n---\n\n")

        for i, batch_dir in enumerate(batch_dirs, 1):
            md_files = sorted(Path(batch_dir).rglob("*.md"))
            for md_file in md_files:
                content = md_file.read_text(encoding="utf-8")
                out.write(content)
                out.write("\n\n---\n\n")
            print(f"  批次 {i}: 合并 {len(md_files)} 个文件")

    print(f"\n最终输出: {final_output}")


def main():
    parser = argparse.ArgumentParser(description="分批转换 PDF 为 Markdown")
    parser.add_argument("pdf_path", help="输入 PDF 文件路径")
    parser.add_argument(
        "--batch-size", type=int, default=30, help="每批处理的页数（默认 30）"
    )
    parser.add_argument("--output-dir", default=".", help="输出目录")
    parser.add_argument("--output-name", default=None, help="最终合并文件名")
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"错误：文件不存在 {args.pdf_path}")
        sys.exit(1)

    pdf_path = os.path.abspath(args.pdf_path)
    total_pages = get_pdf_page_count(pdf_path)
    batch_size = args.batch_size
    num_batches = math.ceil(total_pages / batch_size)

    print(f"PDF 文件: {pdf_path}")
    print(f"总页数: {total_pages}")
    print(f"批次大小: {batch_size} 页")
    print(f"预计批次: {num_batches}\n")

    # 创建临时目录存放各批次输出
    base_dir = os.path.join(args.output_dir, "pdf_batch_output")
    os.makedirs(base_dir, exist_ok=True)

    batch_dirs = []
    for i in range(num_batches):
        start = i * batch_size
        end = min(start + batch_size, total_pages)
        batch_dir = os.path.join(base_dir, f"batch_{i + 1:03d}")
        os.makedirs(batch_dir, exist_ok=True)

        print(f"[{i + 1}/{num_batches}] 处理页码 {start}-{end - 1}...")
        convert_page_range(pdf_path, start, end, batch_dir)
        batch_dirs.append(batch_dir)

    # 合并所有批次
    output_name = args.output_name or f"{Path(pdf_path).stem}.md"
    final_output = os.path.join(args.output_dir, output_name)
    merge_batch_outputs(batch_dirs, final_output)

    # 可选：清理临时批次目录
    # import shutil
    # shutil.rmtree(base_dir)
    # print(f"已清理临时目录: {base_dir}")


if __name__ == "__main__":
    main()
