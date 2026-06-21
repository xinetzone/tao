"""审计日志集成示例 — 展示如何在 Agent 执行流程中集成审计功能

本示例展示：
1. 在 Agent 执行前后记录审计日志
2. 记录操作耗时
3. 处理异常情况
4. 支持会话关联

用法：
    uv run python .agents/scripts/audit_integration_example.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

# 添加父目录到路径
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from audit_logger import AuditLogger, AuditLogLevel, create_audit_logger


# === 示例 Agent 定义 ===

@dataclass
class Task:
    """任务定义。"""
    action: str
    input_data: dict[str, Any]
    agent_id: str = "demo-agent"


@dataclass
class AgentResult:
    """Agent 执行结果。"""
    success: bool
    output_data: dict[str, Any]
    error: str | None = None


class DemoAgent:
    """演示 Agent。"""

    def __init__(self, agent_id: str = "demo-agent"):
        self.id = agent_id

    def run(self, task: Task) -> AgentResult:
        """执行任务。"""
        # 模拟执行
        time.sleep(0.1)

        if task.action == "fail":
            raise ValueError("模拟失败")

        return AgentResult(
            success=True,
            output_data={"result": f"processed {task.action}"},
        )


# === 审计装饰器 ===

def with_audit(audit_logger: AuditLogger):
    """审计装饰器工厂。

    用法：
        @with_audit(audit)
        def my_agent_function(agent, task):
            return agent.run(task)
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(agent, task: Task, **kwargs) -> AgentResult:
            start_time = time.time()

            # 记录开始
            audit_logger.log_action(
                agent_id=agent.id,
                action=task.action,
                input_data=task.input_data,
                metadata={"phase": "start"},
            )

            try:
                # 执行函数
                result = func(agent, task, **kwargs)

                # 计算耗时
                duration_ms = int((time.time() - start_time) * 1000)

                # 记录成功
                audit_logger.log_action(
                    agent_id=agent.id,
                    action=task.action,
                    input_data=task.input_data,
                    output_data=result.output_data,
                    metadata={"phase": "complete", "status": "success"},
                    duration_ms=duration_ms,
                )

                return result

            except Exception as e:
                # 计算耗时
                duration_ms = int((time.time() - start_time) * 1000)

                # 记录失败
                audit_logger.log_error(
                    agent_id=agent.id,
                    action=task.action,
                    error=e,
                    input_data=task.input_data,
                    metadata={"duration_ms": duration_ms},
                )

                raise

        return wrapper
    return decorator


# === 审计执行器 ===

class AuditedAgentExecutor:
    """带审计功能的 Agent 执行器。"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit = audit_logger

    def execute(
        self,
        agent: DemoAgent,
        task: Task,
        user_id: str | None = None,
    ) -> AgentResult:
        """执行 Agent 并记录审计日志。"""
        start_time = time.time()

        # 记录开始
        self.audit.log_action(
            agent_id=agent.id,
            action=task.action,
            input_data=task.input_data,
            user_id=user_id,
            metadata={"phase": "start"},
        )

        try:
            # 执行 Agent
            result = agent.run(task)

            # 计算耗时
            duration_ms = int((time.time() - start_time) * 1000)

            # 记录成功
            self.audit.log_action(
                agent_id=agent.id,
                action=task.action,
                input_data=task.input_data,
                output_data=result.output_data,
                user_id=user_id,
                metadata={"phase": "complete", "status": "success"},
                duration_ms=duration_ms,
            )

            return result

        except Exception as e:
            # 计算耗时
            duration_ms = int((time.time() - start_time) * 1000)

            # 记录失败
            self.audit.log_error(
                agent_id=agent.id,
                action=task.action,
                error=e,
                input_data=task.input_data,
                metadata={"duration_ms": duration_ms},
            )

            raise


# === 批量执行器 ===

class BatchExecutor:
    """批量任务执行器（带审计）。"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit = audit_logger
        self.executor = AuditedAgentExecutor(audit_logger)

    def execute_batch(
        self,
        agent: DemoAgent,
        tasks: list[Task],
        user_id: str | None = None,
    ) -> list[AgentResult]:
        """批量执行任务。"""
        # 开始会话
        session_id = self.audit.start_session()

        results = []
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] 执行任务: {task.action}")

            try:
                result = self.executor.execute(agent, task, user_id)
                results.append(result)
                print(f"   状态: 成功")
            except Exception as e:
                print(f"   状态: 失败 - {e}")
                results.append(AgentResult(
                    success=False,
                    output_data={},
                    error=str(e),
                ))

        # 结束会话
        self.audit.end_session()

        return results


# === 演示函数 ===

def demo_basic_usage():
    """演示基础用法。"""
    print("\n" + "=" * 70)
    print("演示 1: 基础用法")
    print("=" * 70)

    # 创建审计日志记录器
    audit = create_audit_logger()

    # 创建 Agent 和执行器
    agent = DemoAgent("basic-agent")
    executor = AuditedAgentExecutor(audit)

    # 执行任务
    task = Task(
        action="process_data",
        input_data={"data": "test"},
    )

    result = executor.execute(agent, task, user_id="user@example.com")
    print(f"\n执行结果: {result}")

    # 查询日志
    entries = audit.query(agent_id="basic-agent", limit=5)
    print(f"\n查询到 {len(entries)} 条审计记录")


def demo_decorator_usage():
    """演示装饰器用法。"""
    print("\n" + "=" * 70)
    print("演示 2: 装饰器用法")
    print("=" * 70)

    # 创建审计日志记录器
    audit = create_audit_logger()

    # 创建 Agent
    agent = DemoAgent("decorator-agent")

    # 使用装饰器
    @with_audit(audit)
    def execute_task(agent, task):
        return agent.run(task)

    # 执行任务
    task = Task(
        action="decorated_action",
        input_data={"test": True},
    )

    result = execute_task(agent, task)
    print(f"\n执行结果: {result}")


def demo_batch_execution():
    """演示批量执行。"""
    print("\n" + "=" * 70)
    print("演示 3: 批量执行")
    print("=" * 70)

    # 创建审计日志记录器
    audit = create_audit_logger()

    # 创建 Agent 和批量执行器
    agent = DemoAgent("batch-agent")
    batch_executor = BatchExecutor(audit)

    # 创建任务列表
    tasks = [
        Task(action="task_1", input_data={"id": 1}),
        Task(action="task_2", input_data={"id": 2}),
        Task(action="task_3", input_data={"id": 3}),
    ]

    # 批量执行
    results = batch_executor.execute_batch(agent, tasks, user_id="batch-user")

    print(f"\n批量执行完成: {len(results)} 个任务")

    # 查询会话日志
    entries = audit.query(session_id=audit.session_id, limit=10)
    print(f"会话日志: {len(entries)} 条记录")


def demo_error_handling():
    """演示错误处理。"""
    print("\n" + "=" * 70)
    print("演示 4: 错误处理")
    print("=" * 70)

    # 创建审计日志记录器
    audit = create_audit_logger()

    # 创建 Agent 和执行器
    agent = DemoAgent("error-agent")
    executor = AuditedAgentExecutor(audit)

    # 执行失败任务
    task = Task(
        action="fail",
        input_data={"test": True},
    )

    try:
        result = executor.execute(agent, task)
    except Exception as e:
        print(f"\n预期错误: {e}")

    # 查询错误日志
    entries = audit.query(agent_id="error-agent", limit=5)
    print(f"\n查询到 {len(entries)} 条审计记录")

    # 显示错误详情
    for entry in entries:
        if entry.level == "ERROR":
            print(f"错误类型: {entry.metadata.get('error_type')}")
            print(f"错误消息: {entry.metadata.get('error_message')}")


def demo_statistics():
    """演示统计功能。"""
    print("\n" + "=" * 70)
    print("演示 5: 统计功能")
    print("=" * 70)

    # 创建审计日志记录器
    audit = create_audit_logger()

    # 执行一些操作
    agent = DemoAgent("stats-agent")
    executor = AuditedAgentExecutor(audit)

    for i in range(5):
        task = Task(action=f"action_{i}", input_data={"id": i})
        executor.execute(agent, task)

    # 获取统计信息
    stats = audit.get_statistics()

    print("\n审计统计:")
    print(f"  总操作数: {stats['total_actions']}")
    print(f"  唯一 Agent 数: {stats['unique_agents']}")
    print(f"  唯一操作类型: {stats['unique_actions']}")
    print(f"  人工审批数: {stats['human_approved_count']}")
    print(f"  错误数: {stats['error_count']}")


def main():
    """运行所有演示。"""
    print("\n" + "=" * 70)
    print("审计日志集成示例")
    print("=" * 70)

    demo_basic_usage()
    demo_decorator_usage()
    demo_batch_execution()
    demo_error_handling()
    demo_statistics()

    print("\n" + "=" * 70)
    print("所有演示完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
