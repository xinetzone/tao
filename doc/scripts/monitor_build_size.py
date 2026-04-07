#!/usr/bin/env python3
"""
监控 Sphinx 文档构建输出大小的脚本

功能：
1. 检查构建输出目录的大小
2. 与基准值比较，设置阈值警报
3. 生成报告并记录历史数据
"""

import os
import json
import datetime
from pathlib import Path
import argparse

# 配置
DEFAULT_BUILD_DIR = "doc/_build/html"
DEFAULT_METRICS_FILE = "doc/scripts/build_metrics.json"
DEFAULT_BASELINE = 100  # 默认基准值（MB）
DEFAULT_THRESHOLD = 15  # 默认阈值（MB）

def get_directory_size(directory):
    """计算目录大小（MB）"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # 转换为 MB

def load_metrics(metrics_file):
    """加载历史指标数据"""
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "baseline": DEFAULT_BASELINE,
        "threshold": DEFAULT_THRESHOLD,
        "history": []
    }

def save_metrics(metrics_file, metrics):
    """保存指标数据"""
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

def generate_report(current_size, metrics):
    """生成报告"""
    timestamp = datetime.datetime.now().isoformat()
    
    # 计算与基准值的差异
    baseline = metrics["baseline"]
    threshold = metrics["threshold"]
    difference = current_size - baseline
    
    # 检查是否超过阈值
    alert = abs(difference) > threshold
    
    # 构建报告
    report = {
        "timestamp": timestamp,
        "size": round(current_size, 2),
        "baseline": baseline,
        "difference": round(difference, 2),
        "threshold": threshold,
        "alert": alert
    }
    
    # 添加到历史记录
    metrics["history"].append(report)
    
    # 只保留最近 100 条记录
    if len(metrics["history"]) > 100:
        metrics["history"] = metrics["history"][-100:]
    
    return report

def main():
    parser = argparse.ArgumentParser(description="监控 Sphinx 文档构建输出大小")
    parser.add_argument(
        "--build-dir",
        default=DEFAULT_BUILD_DIR,
        help=f"构建输出目录（默认：{DEFAULT_BUILD_DIR}"
    )
    parser.add_argument(
        "--metrics-file",
        default=DEFAULT_METRICS_FILE,
        help=f"指标数据文件（默认：{DEFAULT_METRICS_FILE}"
    )
    parser.add_argument(
        "--set-baseline",
        action="store_true",
        help="将当前大小设置为新的基准值"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help=f"设置警报阈值（默认：{DEFAULT_THRESHOLD} MB）"
    )
    
    args = parser.parse_args()
    
    # 检查构建目录是否存在
    build_dir = Path(args.build_dir)
    if not build_dir.exists():
        print(f"错误：构建目录 {build_dir} 不存在")
        return 1
    
    # 计算当前大小
    current_size = get_directory_size(build_dir)
    print(f"当前构建目录大小：{current_size:.2f} MB")
    
    # 加载指标数据
    metrics_file = Path(args.metrics_file)
    metrics_file.parent.mkdir(exist_ok=True)
    metrics = load_metrics(metrics_file)
    
    # 设置新的基准值
    if args.set_baseline:
        metrics["baseline"] = round(current_size, 2)
        print(f"已将基准值设置为：{metrics['baseline']} MB")
    
    # 设置新的阈值
    if args.threshold is not None:
        metrics["threshold"] = args.threshold
        print(f"已将警报阈值设置为：{metrics['threshold']} MB")
    
    # 生成报告
    report = generate_report(current_size, metrics)
    
    # 保存指标数据
    save_metrics(metrics_file, metrics)
    
    # 打印报告
    print("\n=== 构建大小报告 ===")
    print(f"时间：{report['timestamp']}")
    print(f"当前大小：{report['size']} MB")
    print(f"基准值：{report['baseline']} MB")
    print(f"差异：{report['difference']} MB")
    print(f"阈值：{report['threshold']} MB")
    
    if report['alert']:
        print("\033[91m警告：构建大小超出阈值！\033[0m")
        return 1
    else:
        print("\033[92m构建大小在正常范围内。\033[0m")
        return 0

if __name__ == "__main__":
    exit(main())
