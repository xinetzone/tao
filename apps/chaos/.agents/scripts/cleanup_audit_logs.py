"""审计日志清理脚本 — EU AI Act Article 12 合规实现

定期清理过期审计日志，满足 EU AI Act 记录留存要求：
- 默认保留 365 天
- 自动压缩旧日志
- 提供清理统计报告

用法：
    # 手动清理
    uv run python .agents/scripts/cleanup_audit_logs.py

    # 指定保留天数
    uv run python .agents/scripts/cleanup_audit_logs.py --retention-days 365

    # 干运行（不实际删除）
    uv run python .agents/scripts/cleanup_audit_logs.py --dry-run

    # 集成到 cron
    # 0 2 * * * cd /path/to/project && uv run python .agents/scripts/cleanup_audit_logs.py
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from audit_logger import AuditLogger, create_audit_logger


def cleanup_logs(
    log_dir: Path | None = None,
    retention_days: int = 365,
    compress_after_days: int = 30,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict[str, int]:
    """清理过期审计日志。

    Args:
        log_dir: 日志目录路径
        retention_days: 日志保留天数
        compress_after_days: 多少天后压缩日志
        dry_run: 干运行模式（不实际删除）
        verbose: 详细输出

    Returns:
        清理统计信息
    """
    if log_dir is None:
        audit = create_audit_logger(retention_days=retention_days)
    else:
        audit = AuditLogger(
            log_dir=log_dir,
            retention_days=retention_days,
            compress_after_days=compress_after_days,
        )

    if verbose:
        print(f"[INFO] 日志目录: {audit.log_dir}")
        print(f"[INFO] 保留天数: {retention_days}")
        print(f"[INFO] 压缩阈值: {compress_after_days} 天")
        print(f"[INFO] 干运行模式: {dry_run}")
        print()

    if dry_run:
        # 干运行模式：只统计，不实际清理
        stats = _dry_run_cleanup(audit, verbose)
    else:
        # 实际清理
        stats = audit.cleanup_old_logs()

    return stats


def _dry_run_cleanup(audit: AuditLogger, verbose: bool) -> dict[str, int]:
    """干运行清理（只统计，不实际删除）。"""
    from datetime import timedelta
    import os

    cutoff_date = datetime.now() - timedelta(days=audit.retention_days)
    compress_date = datetime.now() - timedelta(days=audit.compress_after_days)

    stats = {
        "deleted_files": 0,
        "compressed_files": 0,
        "freed_bytes": 0,
    }

    for log_file in audit.log_dir.glob("audit_*.log*"):
        try:
            # 提取文件日期
            file_name = log_file.stem
            if log_file.suffix == '.gz':
                file_name = log_file.stem.replace('.log', '')

            parts = file_name.split('_')
            if len(parts) >= 2:
                date_str = parts[1][:6]
                file_date = datetime.strptime(date_str, "%Y%m")
                file_size = log_file.stat().st_size

                # 检查是否需要删除
                if file_date < cutoff_date:
                    stats["deleted_files"] += 1
                    stats["freed_bytes"] += file_size

                    if verbose:
                        print(f"[DELETE] {log_file.name} ({file_size / 1024:.1f} KB)")

                # 检查是否需要压缩
                elif file_date < compress_date and log_file.suffix != '.gz':
                    stats["compressed_files"] += 1

                    if verbose:
                        print(f"[COMPRESS] {log_file.name} ({file_size / 1024:.1f} KB)")

        except (ValueError, IndexError, OSError) as e:
            if verbose:
                print(f"[SKIP] {log_file.name}: {e}")

    return stats


def print_report(stats: dict[str, int], verbose: bool = False) -> None:
    """打印清理报告。"""
    print("\n" + "=" * 70)
    print("审计日志清理报告")
    print("=" * 70)

    print(f"删除文件数: {stats['deleted_files']}")
    print(f"压缩文件数: {stats['compressed_files']}")
    print(f"释放空间: {stats['freed_bytes'] / 1024 / 1024:.2f} MB")

    if stats['deleted_files'] > 0 or stats['compressed_files'] > 0:
        print("\n状态: [OK] 清理完成")
    else:
        print("\n状态: [SKIP] 无需清理")

    print("=" * 70)


def main() -> int:
    """入口：运行审计日志清理。"""
    parser = argparse.ArgumentParser(
        description="清理过期审计日志",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础清理
  uv run python .agents/scripts/cleanup_audit_logs.py

  # 指定保留天数
  uv run python .agents/scripts/cleanup_audit_logs.py --retention-days 180

  # 干运行（预览）
  uv run python .agents/scripts/cleanup_audit_logs.py --dry-run --verbose
        """,
    )

    parser.add_argument(
        "--log-dir",
        type=Path,
        help="指定日志目录路径（默认自动查找）",
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=365,
        help="日志保留天数（默认 365）",
    )
    parser.add_argument(
        "--compress-after-days",
        type=int,
        default=30,
        help="多少天后压缩日志（默认 30）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="干运行模式（不实际删除文件）",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细信息",
    )

    args = parser.parse_args()

    # 执行清理
    stats = cleanup_logs(
        log_dir=args.log_dir,
        retention_days=args.retention_days,
        compress_after_days=args.compress_after_days,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    # 打印报告
    print_report(stats, verbose=args.verbose)

    return 0


if __name__ == "__main__":
    sys.exit(main())
