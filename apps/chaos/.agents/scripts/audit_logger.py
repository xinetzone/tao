"""审计日志记录器 — EU AI Act Article 12 合规实现

提供完整的审计日志记录功能，满足 EU AI Act Article 12（记录留存）要求：
- 所有 Agent 操作可追溯
- 日志保留 365 天以上
- 支持日志轮转和清理
- 提供审计查询接口

用法：
    from audit_logger import AuditLogger

    audit = AuditLogger()
    audit.log_action(
        agent_id="code-review-agent",
        action="review_pull_request",
        input_data={"pr_id": 123},
        output_data={"approved": True},
    )
"""

from __future__ import annotations

import gzip
import hashlib
import json
import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class AuditLogLevel(Enum):
    """审计日志级别。"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AuditEntry:
    """审计日志条目。"""
    timestamp: str
    agent_id: str
    action: str
    input_hash: str | None
    output_hash: str | None
    human_approved: bool
    metadata: dict[str, Any]
    level: str = "INFO"
    session_id: str | None = None
    user_id: str | None = None
    duration_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return {
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "action": self.action,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "human_approved": self.human_approved,
            "metadata": self.metadata,
            "level": self.level,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "duration_ms": self.duration_ms,
        }

    def to_json(self) -> str:
        """转换为 JSON。"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AuditLogger:
    """EU AI Act 合规审计日志记录器。"""

    def __init__(
        self,
        log_dir: str | Path = ".agents/audit_logs",
        retention_days: int = 365,
        max_file_size_mb: int = 100,
        compress_after_days: int = 30,
    ):
        """初始化审计日志记录器。

        Args:
            log_dir: 日志目录路径
            retention_days: 日志保留天数
            max_file_size_mb: 单个日志文件最大大小（MB）
            compress_after_days: 多少天后压缩日志
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.retention_days = retention_days
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.compress_after_days = compress_after_days

        # 创建日志记录器
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

        # 移除现有处理器
        self.logger.handlers.clear()

        # 添加文件处理器
        self._setup_file_handler()

        # 会话 ID（用于关联同一会话的多个操作）
        self.session_id: str | None = None

    def _setup_file_handler(self) -> None:
        """设置文件处理器。"""
        log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m')}.log"

        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(message)s'))

        self.logger.addHandler(handler)
        self.current_log_file = log_file

    def _check_file_rotation(self) -> None:
        """检查是否需要轮转日志文件。"""
        if not self.current_log_file.exists():
            return

        # 检查文件大小
        if self.current_log_file.stat().st_size >= self.max_file_size_bytes:
            self._rotate_log_file()

        # 检查月份变化
        current_month = datetime.now().strftime('%Y%m')
        expected_file = self.log_dir / f"audit_{current_month}.log"

        if self.current_log_file != expected_file:
            self._setup_file_handler()

    def _rotate_log_file(self) -> None:
        """轮转日志文件。"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rotated_file = self.current_log_file.with_suffix(f'.{timestamp}.log')

        # 关闭当前处理器
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

        # 重命名当前文件
        if self.current_log_file.exists():
            shutil.move(str(self.current_log_file), str(rotated_file))

        # 创建新文件
        self._setup_file_handler()

    def _hash_data(self, data: dict[str, Any] | None) -> str | None:
        """计算数据哈希（用于审计追溯，避免存储敏感数据）。"""
        if data is None:
            return None

        try:
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
            return hashlib.sha256(data_str.encode()).hexdigest()[:16]
        except Exception:
            return None

    def start_session(self, session_id: str | None = None) -> str:
        """开始审计会话。

        Args:
            session_id: 会话 ID（可选，自动生成）

        Returns:
            会话 ID
        """
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return self.session_id

    def end_session(self) -> None:
        """结束审计会话。"""
        self.session_id = None

    def log_action(
        self,
        agent_id: str,
        action: str,
        input_data: dict[str, Any] | None = None,
        output_data: dict[str, Any] | None = None,
        human_approved: bool = False,
        metadata: dict[str, Any] | None = None,
        level: AuditLogLevel = AuditLogLevel.INFO,
        user_id: str | None = None,
        duration_ms: int | None = None,
    ) -> AuditEntry:
        """记录 Agent 操作。

        Args:
            agent_id: Agent 标识符
            action: 操作类型
            input_data: 输入数据
            output_data: 输出数据
            human_approved: 是否经过人工审批
            metadata: 元数据
            level: 日志级别
            user_id: 用户 ID
            duration_ms: 操作耗时（毫秒）

        Returns:
            审计日志条目
        """
        # 检查文件轮转
        self._check_file_rotation()

        # 创建审计条目
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            action=action,
            input_hash=self._hash_data(input_data),
            output_hash=self._hash_data(output_data),
            human_approved=human_approved,
            metadata=metadata or {},
            level=level.value,
            session_id=self.session_id,
            user_id=user_id,
            duration_ms=duration_ms,
        )

        # 记录日志
        self.logger.info(entry.to_json())

        return entry

    def log_error(
        self,
        agent_id: str,
        action: str,
        error: Exception,
        input_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """记录错误。

        Args:
            agent_id: Agent 标识符
            action: 操作类型
            error: 异常对象
            input_data: 输入数据
            metadata: 元数据

        Returns:
            审计日志条目
        """
        error_metadata = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            **(metadata or {}),
        }

        return self.log_action(
            agent_id=agent_id,
            action=action,
            input_data=input_data,
            metadata=error_metadata,
            level=AuditLogLevel.ERROR,
        )

    def log_approval(
        self,
        request_id: str,
        action: str,
        approver: str,
        approved: bool,
        comment: str | None = None,
    ) -> AuditEntry:
        """记录审批操作。

        Args:
            request_id: 审批请求 ID
            action: 操作类型
            approver: 审批人
            approved: 是否批准
            comment: 审批意见

        Returns:
            审计日志条目
        """
        return self.log_action(
            agent_id="approval-workflow",
            action="approval_decision",
            input_data={"request_id": request_id, "action": action},
            output_data={"approved": approved, "comment": comment},
            human_approved=True,
            metadata={
                "approver": approver,
                "request_id": request_id,
            },
        )

    def query(
        self,
        agent_id: str | None = None,
        action: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """查询审计日志。

        Args:
            agent_id: Agent ID 过滤
            action: 操作类型过滤
            start_time: 开始时间
            end_time: 结束时间
            user_id: 用户 ID 过滤
            session_id: 会话 ID 过滤
            limit: 返回条数限制

        Returns:
            审计日志条目列表
        """
        entries = []

        # 确定要查询的日志文件
        log_files = sorted(self.log_dir.glob("audit_*.log*"), reverse=True)

        for log_file in log_files:
            # 处理压缩文件
            if log_file.suffix == '.gz':
                open_func = gzip.open
                mode = 'rt'
            else:
                open_func = open
                mode = 'r'

            try:
                with open_func(log_file, mode, encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            entry = AuditEntry(**data)

                            # 应用过滤条件
                            if agent_id and entry.agent_id != agent_id:
                                continue
                            if action and entry.action != action:
                                continue
                            if user_id and entry.user_id != user_id:
                                continue
                            if session_id and entry.session_id != session_id:
                                continue
                            if start_time:
                                entry_time = datetime.fromisoformat(entry.timestamp)
                                if entry_time < start_time:
                                    continue
                            if end_time:
                                entry_time = datetime.fromisoformat(entry.timestamp)
                                if entry_time > end_time:
                                    continue

                            entries.append(entry)

                            if len(entries) >= limit:
                                return entries

                        except (json.JSONDecodeError, TypeError):
                            continue
            except Exception:
                continue

        return entries

    def get_statistics(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        """获取审计统计信息。

        Args:
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            统计信息
        """
        entries = self.query(start_time=start_time, end_time=end_time, limit=10000)

        if not entries:
            return {
                "total_actions": 0,
                "unique_agents": 0,
                "unique_actions": 0,
                "human_approved_count": 0,
                "error_count": 0,
            }

        agents = set()
        actions = set()
        human_approved_count = 0
        error_count = 0

        for entry in entries:
            agents.add(entry.agent_id)
            actions.add(entry.action)
            if entry.human_approved:
                human_approved_count += 1
            if entry.level == "ERROR":
                error_count += 1

        return {
            "total_actions": len(entries),
            "unique_agents": len(agents),
            "unique_actions": len(actions),
            "human_approved_count": human_approved_count,
            "error_count": error_count,
            "human_approval_rate": human_approved_count / len(entries) if entries else 0,
            "error_rate": error_count / len(entries) if entries else 0,
        }

    def cleanup_old_logs(self) -> dict[str, int]:
        """清理过期日志文件。

        Returns:
            清理统计信息
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        compress_date = datetime.now() - timedelta(days=self.compress_after_days)

        stats = {
            "deleted_files": 0,
            "compressed_files": 0,
            "freed_bytes": 0,
        }

        for log_file in self.log_dir.glob("audit_*.log*"):
            try:
                # 提取文件日期
                file_name = log_file.stem
                if log_file.suffix == '.gz':
                    file_name = log_file.stem.replace('.log', '')

                # 尝试解析日期（格式：audit_YYYYMM 或 audit_YYYYMMDD_HHMMSS）
                parts = file_name.split('_')
                if len(parts) >= 2:
                    date_str = parts[1][:6]  # YYYYMM
                    file_date = datetime.strptime(date_str, "%Y%m")

                    # 检查是否需要删除
                    if file_date < cutoff_date:
                        file_size = log_file.stat().st_size
                        log_file.unlink()
                        stats["deleted_files"] += 1
                        stats["freed_bytes"] += file_size
                        continue

                    # 检查是否需要压缩
                    if file_date < compress_date and log_file.suffix != '.gz':
                        self._compress_file(log_file)
                        stats["compressed_files"] += 1

            except (ValueError, IndexError, OSError):
                continue

        return stats

    def _compress_file(self, file_path: Path) -> None:
        """压缩日志文件。"""
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')

        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        file_path.unlink()

    def export_logs(
        self,
        output_path: str | Path,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        format: str = "json",
    ) -> int:
        """导出审计日志。

        Args:
            output_path: 输出文件路径
            start_time: 开始时间
            end_time: 结束时间
            format: 输出格式（json, csv）

        Returns:
            导出的条目数
        """
        entries = self.query(start_time=start_time, end_time=end_time, limit=100000)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                for entry in entries:
                    f.write(entry.to_json() + '\n')

        elif format == "csv":
            import csv

            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)

                # 写入表头
                writer.writerow([
                    "timestamp", "agent_id", "action", "input_hash",
                    "output_hash", "human_approved", "level", "session_id",
                    "user_id", "duration_ms"
                ])

                # 写入数据
                for entry in entries:
                    writer.writerow([
                        entry.timestamp,
                        entry.agent_id,
                        entry.action,
                        entry.input_hash,
                        entry.output_hash,
                        entry.human_approved,
                        entry.level,
                        entry.session_id,
                        entry.user_id,
                        entry.duration_ms,
                    ])

        return len(entries)


# 便捷函数
def create_audit_logger(
    log_dir: str | Path | None = None,
    retention_days: int = 365,
) -> AuditLogger:
    """创建审计日志记录器。

    Args:
        log_dir: 日志目录路径（默认 .agents/audit_logs）
        retention_days: 日志保留天数

    Returns:
        审计日志记录器实例
    """
    if log_dir is None:
        # 查找 .agents 目录
        current = Path.cwd()
        for _ in range(10):
            candidate = current / ".agents" / "audit_logs"
            if candidate.parent.is_dir():
                log_dir = candidate
                break
            parent = current.parent
            if parent == current:
                break
            current = parent

        if log_dir is None:
            log_dir = Path(".agents/audit_logs")

    return AuditLogger(log_dir=log_dir, retention_days=retention_days)


if __name__ == "__main__":
    # 演示用法
    print("=== 审计日志记录器演示 ===\n")

    # 创建审计日志记录器
    audit = create_audit_logger()

    # 开始会话
    session_id = audit.start_session()
    print(f"会话 ID: {session_id}\n")

    # 记录操作
    print("1. 记录 Agent 操作...")
    entry1 = audit.log_action(
        agent_id="code-review-agent",
        action="review_pull_request",
        input_data={"pr_id": 123, "files": ["src/main.py"]},
        output_data={"approved": True, "comments": []},
        user_id="developer@company.com",
    )
    print(f"   已记录: {entry1.action}")

    # 记录审批
    print("\n2. 记录审批操作...")
    entry2 = audit.log_approval(
        request_id="req_001",
        action="production_deploy",
        approver="tech-lead@company.com",
        approved=True,
        comment="代码已审查，可以部署",
    )
    print(f"   已记录审批: {entry2.metadata['request_id']}")

    # 记录错误
    print("\n3. 记录错误...")
    try:
        raise ValueError("测试错误")
    except Exception as e:
        entry3 = audit.log_error(
            agent_id="test-agent",
            action="test_action",
            error=e,
            input_data={"test": True},
        )
    print(f"   已记录错误: {entry3.metadata['error_type']}")

    # 结束会话
    audit.end_session()

    # 查询日志
    print("\n4. 查询审计日志...")
    entries = audit.query(limit=5)
    print(f"   查询到 {len(entries)} 条记录")

    # 获取统计信息
    print("\n5. 获取统计信息...")
    stats = audit.get_statistics()
    print(f"   总操作数: {stats['total_actions']}")
    print(f"   唯一 Agent 数: {stats['unique_agents']}")
    print(f"   人工审批率: {stats['human_approval_rate']:.2%}")

    print("\n=== 演示完成 ===")
