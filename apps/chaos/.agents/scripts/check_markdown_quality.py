"""
PDF→Markdown 转换结果质量检查脚本

功能：
    - 基础属性检查（大小、行数、字符数）
    - Markdown 结构检查（标题层级、空文件检测）
    - 内容完整性检查（关键章节存在性）
    - 与原始 PDF 页数映射对比
    - 生成质量评分报告

用法:
    python check_markdown_quality.py <markdown.md> [--pdf original.pdf] [--verbose]

示例:
    python check_markdown_quality.py book.md --pdf book.pdf
"""

import argparse
import json
import os
import re
import sys


def analyze_markdown(md_path: str) -> dict:
    """分析 Markdown 文件结构和内容"""
    stats = {
        "file_size": os.path.getsize(md_path),
        "line_count": 0,
        "char_count": 0,
        "empty_lines": 0,
        "headers": {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0},
        "code_blocks": 0,
        "tables": 0,
        "images": 0,
        "links": 0,
        "chinese_chars": 0,
        "sections": [],
    }

    in_code_block = False

    with open(md_path, encoding="utf-8") as f:
        for line in f:
            stats["line_count"] += 1
            stats["char_count"] += len(line)
            stripped = line.strip()

            if not stripped:
                stats["empty_lines"] += 1
                continue

            # 代码块检测
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                if in_code_block:
                    stats["code_blocks"] += 1
                continue

            if in_code_block:
                continue

            # 标题检测
            header_match = re.match(r"^(#{1,6})\s+(.+)", stripped)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2)
                key = f"h{level}"
                stats["headers"][key] = stats["headers"].get(key, 0) + 1
                if level <= 2:
                    stats["sections"].append({"level": level, "title": title})
                continue

            # 表格检测
            if "|" in stripped and stripped.startswith("|"):
                stats["tables"] += 1

            # 图片检测
            if re.search(r"!\[.*?\]\(.*?\)", stripped):
                stats["images"] += 1

            # 链接检测
            if re.search(r"\[.*?\]\(.*?\)", stripped):
                stats["links"] += 1

            # 中文字符统计
            stats["chinese_chars"] += len(re.findall(r"[\u4e00-\u9fff]", line))

    return stats


def check_quality_rules(stats: dict, md_path: str) -> list:
    """基于统计信息执行质量规则检查"""
    issues = []
    warnings = []
    info = []

    # P0: 致命问题
    if stats["file_size"] < 1000:
        issues.append({"level": "P0", "msg": "文件过小 (< 1KB)，可能内容严重缺失"})

    if stats["char_count"] < 500:
        issues.append({"level": "P0", "msg": "字符数过少 (< 500)，可能转换失败"})

    if stats["headers"]["h1"] == 0 and stats["headers"]["h2"] == 0:
        issues.append({"level": "P0", "msg": "未检测到任何标题，结构完全损坏"})

    # P1: 严重问题
    empty_ratio = stats["empty_lines"] / max(stats["line_count"], 1)
    if empty_ratio > 0.5:
        warnings.append({"level": "P1", "msg": f"空行比例过高 ({empty_ratio:.1%})"})

    if stats["chinese_chars"] == 0:
        warnings.append({"level": "P1", "msg": "未检测到中文字符，可能 OCR 失败"})

    # P2: 一般问题
    if stats["headers"]["h1"] < 3:
        warnings.append(
            {
                "level": "P2",
                "msg": f"一级标题过少 ({stats['headers']['h1']} 个)，章节可能遗漏",
            }
        )

    # P3: 提示信息
    if stats["images"] > 0:
        info.append({"level": "P3", "msg": f"包含 {stats['images']} 张图片引用"})

    if stats["tables"] > 0:
        info.append({"level": "P3", "msg": f"包含 {stats['tables']} 个表格"})

    return issues + warnings + info


def compare_with_pdf(md_stats: dict, pdf_path: str) -> dict:
    """将 Markdown 结果与原始 PDF 进行对比"""
    try:
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(pdf_path)
        pdf_pages = len(doc)
        doc.close()

        # 估算预期章节数（假设每 3-5 页一个章节）
        expected_sections_min = max(1, pdf_pages // 5)
        expected_sections_max = max(1, pdf_pages // 2)
        actual_sections = md_stats["headers"]["h1"]

        comparison = {
            "pdf_pages": pdf_pages,
            "md_h1_count": actual_sections,
            "expected_sections_range": f"{expected_sections_min}-{expected_sections_max}",
            "page_coverage": "未知",  # marker-pdf 的 page_range 信息可从元数据获取
        }

        if actual_sections < expected_sections_min:
            comparison["status"] = "可能遗漏"
            comparison["note"] = (
                f"章节数 ({actual_sections}) 明显低于预期 ({expected_sections_min}+)"
            )
        elif actual_sections > expected_sections_max:
            comparison["status"] = "可能过细"
            comparison["note"] = (
                f"章节数 ({actual_sections}) 高于预期，可能拆分了过细的标题"
            )
        else:
            comparison["status"] = "正常"
            comparison["note"] = "章节数在合理范围内"

        return comparison

    except ImportError:
        return {"error": "需要 pypdfium2 进行 PDF 对比"}
    except Exception as e:
        return {"error": str(e)}


def calculate_score(stats: dict, issues: list) -> int:
    """计算质量评分 (0-100)"""
    score = 100

    for issue in issues:
        level = issue["level"]
        if level == "P0":
            score -= 30
        elif level == "P1":
            score -= 15
        elif level == "P2":
            score -= 5
        elif level == "P3":
            score -= 0  # 信息级别不扣分

    # 基于结构完整性加分/减分
    if stats["headers"]["h1"] >= 5:
        score += 5
    if stats["chinese_chars"] > 10000:
        score += 5

    return max(0, min(100, score))


def print_report(md_path: str, stats: dict, issues: list, comparison: dict, score: int):
    """打印质量检查报告"""
    print("=" * 60)
    print("Markdown 转换质量检查报告")
    print("=" * 60)
    print(f"检查文件: {md_path}")
    print(f"文件大小: {stats['file_size']:,} 字节")
    print()

    # 基础统计
    print("--- 基础统计 ---")
    print(f"  总行数: {stats['line_count']:,}")
    print(f"  总字符: {stats['char_count']:,}")
    print(f"  中文字符: {stats['chinese_chars']:,}")
    print(f"  空行数: {stats['empty_lines']:,}")
    print()

    # 结构统计
    print("--- 结构统计 ---")
    for level, count in stats["headers"].items():
        if count > 0:
            print(f"  {level.upper()}: {count} 个")
    print(f"  代码块: {stats['code_blocks']} 个")
    print(f"  表格: {stats['tables']} 个")
    print(f"  图片: {stats['images']} 张")
    print(f"  链接: {stats['links']} 个")
    print()

    # PDF 对比
    if "error" not in comparison:
        print("--- PDF 对比 ---")
        print(f"  PDF 页数: {comparison['pdf_pages']}")
        print(f"  Markdown H1: {comparison['md_h1_count']} 个")
        print(f"  预期章节: {comparison['expected_sections_range']}")
        print(f"  状态: {comparison['status']}")
        if comparison.get("note"):
            print(f"  备注: {comparison['note']}")
        print()

    # 问题列表
    if issues:
        print("--- 检查项 ---")
        for issue in issues:
            icon = (
                "🔴"
                if issue["level"] == "P0"
                else "🟡"
                if issue["level"].startswith("P")
                else "🟢"
            )
            print(f"  {icon} [{issue['level']}] {issue['msg']}")
        print()

    # 评分
    print("=" * 60)
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D"
    print(f"质量评分: {score}/100 (等级: {grade})")
    print("=" * 60)

    if score >= 90:
        print("✅ 质量优秀，内容完整")
    elif score >= 75:
        print("⚠️ 质量良好，存在 minor 问题")
    elif score >= 60:
        print("⚠️ 质量一般，建议人工复核")
    else:
        print("❌ 质量不合格，需要重新转换")


def main():
    parser = argparse.ArgumentParser(description="Markdown 转换质量检查")
    parser.add_argument("md_path", help="Markdown 文件路径")
    parser.add_argument("--pdf", default=None, help="原始 PDF 文件路径（用于对比）")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细章节列表")
    args = parser.parse_args()

    if not os.path.exists(args.md_path):
        print(f"[错误] 文件不存在: {args.md_path}")
        sys.exit(1)

    # 分析
    stats = analyze_markdown(args.md_path)
    issues = check_quality_rules(stats, args.md_path)

    # PDF 对比
    comparison = {}
    if args.pdf and os.path.exists(args.pdf):
        comparison = compare_with_pdf(stats, args.pdf)

    # 评分
    score = calculate_score(stats, issues)

    # 输出
    if args.json:
        result = {
            "file": args.md_path,
            "score": score,
            "stats": stats,
            "issues": issues,
            "comparison": comparison,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(args.md_path, stats, issues, comparison, score)

        if args.verbose and stats["sections"]:
            print("\n--- 章节列表 ---")
            for sec in stats["sections"]:
                indent = "  " * (sec["level"] - 1)
                print(f"{indent}{'#' * sec['level']} {sec['title']}")

    # 退出码：P0 问题返回 1
    has_critical = any(i["level"] == "P0" for i in issues)
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
