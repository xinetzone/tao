"""数据同步 CLI 入口。

提供命令行接口用于运行同步作业。
"""

import argparse
import asyncio
import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)


async def _connect(mongo_url: str, mongo_db: str) -> tuple[Any, Any]:
    """创建 MongoDB 连接。"""
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(mongo_url)
    db = client[mongo_db]
    return client, db


async def _run_job(mongo_url: str, mongo_db: str, job_id: str) -> None:
    """运行同步作业。"""
    from taolib.data_sync.repository.checkpoint_repo import CheckpointRepository
    from taolib.data_sync.repository.failure_repo import FailureRecordRepository
    from taolib.data_sync.repository.job_repo import SyncJobRepository
    from taolib.data_sync.repository.log_repo import SyncLogRepository
    from taolib.data_sync.services.orchestrator import SyncOrchestrator

    client, db = await _connect(mongo_url, mongo_db)
    try:
        orchestrator = SyncOrchestrator(
            job_repo=SyncJobRepository(db.sync_jobs),
            log_repo=SyncLogRepository(db.sync_logs),
            checkpoint_repo=CheckpointRepository(db.sync_checkpoints),
            failure_repo=FailureRecordRepository(db.sync_failures),
        )

        print(f"运行作业: {job_id}")
        log = await orchestrator.run_job(job_id)
        print(f"  状态: {log.status}")
        print(f"  模式: {log.mode}")
        if log.duration_seconds:
            print(f"  耗时: {log.duration_seconds:.1f}s")
        metrics = log.metrics
        if hasattr(metrics, "total_extracted"):
            print(f"  提取: {metrics.total_extracted}")
            print(f"  转换: {metrics.total_transformed}")
            print(f"  加载: {metrics.total_loaded}")
            print(f"  失败: {metrics.total_failed}")
            print(f"  跳过: {metrics.total_skipped}")
        print("完成。")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


async def _list_jobs(mongo_url: str, mongo_db: str) -> None:
    """列出所有作业。"""
    from taolib.data_sync.repository.job_repo import SyncJobRepository

    client, db = await _connect(mongo_url, mongo_db)
    try:
        repo = SyncJobRepository(db.sync_jobs)
        jobs = await repo.list(limit=100)

        if not jobs:
            print("没有找到同步作业。")
            return

        # 表头
        print(
            f"{'Name':<30} {'Mode':<15} {'Enabled':<10} {'Last Run':<25} {'Status':<12}"
        )
        print("-" * 92)

        for job in jobs:
            last_run = (
                job.last_run_at.strftime("%Y-%m-%d %H:%M:%S")
                if job.last_run_at
                else "-"
            )
            print(
                f"{job.name:<30} {job.mode:<15} "
                f"{'Yes' if job.enabled else 'No':<10} "
                f"{last_run:<25} {job.last_run_status or '-':<12}"
            )

        print(f"\n共 {len(jobs)} 个作业。")
    finally:
        client.close()


async def _show_status(
    mongo_url: str,
    mongo_db: str,
    job_id: str | None,
) -> None:
    """查看作业状态。"""
    from taolib.data_sync.repository.checkpoint_repo import CheckpointRepository
    from taolib.data_sync.repository.failure_repo import FailureRecordRepository
    from taolib.data_sync.repository.log_repo import SyncLogRepository
    from taolib.data_sync.services.metrics_service import MetricsService

    client, db = await _connect(mongo_url, mongo_db)
    try:
        svc = MetricsService(
            log_repo=SyncLogRepository(db.sync_logs),
            failure_repo=FailureRecordRepository(db.sync_failures),
            checkpoint_repo=CheckpointRepository(db.sync_checkpoints),
        )

        if job_id:
            summary = await svc.get_job_summary(job_id)
            print(f"作业: {summary['job_id']}")
            print(f"  总运行次数: {summary['total_runs']}")
            print(f"  成功次数: {summary['success_runs']}")
            print(f"  成功率: {summary['success_rate']}%")

            checkpoints = summary.get("checkpoints", [])
            if checkpoints:
                print("  检查点:")
                for cp in checkpoints:
                    ts = cp["last_synced_timestamp"] or "未同步"
                    print(
                        f"    {cp['collection_name']}: "
                        f"已同步 {cp['total_synced']} 条, 时间戳={ts}"
                    )
        else:
            summary = await svc.get_global_summary()
            print("全局同步状态:")
            print(f"  活跃作业数: {summary['total_jobs']}")
            print(f"  最近运行数: {summary['recent_runs']}")
            print(f"  完成: {summary['completed']}")
            print(f"  失败: {summary['failed']}")
    finally:
        client.close()


def main() -> None:
    """CLI 入口函数。"""
    parser = argparse.ArgumentParser(
        description="MongoDB 数据同步管道 CLI",
    )
    parser.add_argument(
        "--mongo-url",
        default="mongodb://localhost:27017",
        help="MongoDB 连接 URL（默认: mongodb://localhost:27017）",
    )
    parser.add_argument(
        "--mongo-db",
        default="data_sync",
        help="MongoDB 数据库名（默认: data_sync）",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别（默认: INFO）",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # run 命令
    run_parser = subparsers.add_parser("run", help="运行同步作业")
    run_parser.add_argument("job_id", help="作业 ID")

    # list 命令
    subparsers.add_parser("list", help="列出所有作业")

    # status 命令
    status_parser = subparsers.add_parser("status", help="查看作业状态")
    status_parser.add_argument("job_id", nargs="?", help="作业 ID（可选）")

    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.command == "run":
        asyncio.run(_run_job(args.mongo_url, args.mongo_db, args.job_id))
    elif args.command == "list":
        asyncio.run(_list_jobs(args.mongo_url, args.mongo_db))
    elif args.command == "status":
        job_id = getattr(args, "job_id", None)
        asyncio.run(_show_status(args.mongo_url, args.mongo_db, job_id))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
