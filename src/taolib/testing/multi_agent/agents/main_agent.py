"""主智能体。

主智能体负责任务分析、决策和智能体调度。
"""

import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional
from datetime import UTC, datetime

from taolib.testing.multi_agent.agents.base import BaseAgent
from taolib.testing.multi_agent.agents.templates import get_all_templates
from taolib.testing.multi_agent.errors import AgentError, ModelUnavailableError, TaskError
from taolib.testing.multi_agent.llm import LLMManager, get_llm_manager
from taolib.testing.logging_config import get_logger
from taolib.testing.multi_agent.models import (
    AgentCreate,
    AgentDocument,
    AgentStatus,
    AgentType,
    Message,
    MessagePayload,
    MessageType,
    SubTask,
    TaskDocument,
    TaskProgress,
    TaskResult,
    TaskStatus,
)

logger = get_logger(__name__)


class SubAgentWrapper(BaseAgent):
    """子智能体包装器。"""

    def __init__(self, document: AgentDocument, llm_manager: LLMManager):
        """初始化子智能体包装器。

        Args:
            document: 智能体文档
            llm_manager: LLM管理器
        """
        super().__init__(document)
        self._llm_manager = llm_manager

    async def _handle_message(self, message: Message) -> None:
        """处理接收到的消息。

        Args:
            message: 接收到的消息
        """
        pass

    async def execute_task(self, task: TaskDocument) -> None:
        """执行任务。

        Args:
            task: 要执行的任务
        """
        try:
            task.status = TaskStatus.IN_PROGRESS

            # 使用LLM执行任务
            try:
                system_prompt = None
                if self._document.config.system_prompt:
                    system_prompt = self._document.config.system_prompt

                result = await self._llm_manager.generate(
                    prompt=task.user_input or task.description,
                    system_prompt=system_prompt,
                    temperature=self._document.config.temperature,
                )

                task.result = TaskResult(
                    success=True,
                    summary=result[:500] if len(result) > 500 else result,
                    details={"full_output": result},
                )
                task.status = TaskStatus.COMPLETED

            except ModelUnavailableError:
                task.result = TaskResult(
                    success=False,
                    summary="没有可用的模型",
                    errors=["No model available"],
                )
                task.status = TaskStatus.FAILED
            except Exception as e:
                task.result = TaskResult(
                    success=False,
                    summary=f"执行失败: {str(e)}",
                    errors=[str(e)],
                )
                task.status = TaskStatus.FAILED

        finally:
            await self.complete_task(task.status == TaskStatus.COMPLETED, task.result)


class MainAgent(BaseAgent):
    """主智能体。"""

    def __init__(
        self,
        document: AgentDocument,
        llm_manager: Optional[LLMManager] = None,
    ):
        """初始化主智能体。

        Args:
            document: 智能体文档
            llm_manager: LLM管理器,如果为None则使用全局管理器
        """
        super().__init__(document)
        self._llm_manager = llm_manager or get_llm_manager()
        self._sub_agents: Dict[str, BaseAgent] = {}
        self._task_queue: List[TaskDocument] = []
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._is_running = False
        self._main_loop_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """初始化主智能体。"""
        await super().initialize()

        # 创建默认子智能体
        await self._create_default_agents()

        # 启动主循环
        self._is_running = True
        self._main_loop_task = asyncio.create_task(self._main_loop())

    async def _create_default_agents(self) -> None:
        """创建默认子智能体。"""
        templates = get_all_templates()

        for template in templates:
            agent_create = AgentCreate(
                name=f"{template.name} (默认)",
                description=template.description,
                agent_type=template.agent_type,
                capabilities=template.capabilities,
                config=template.config,
                skills=template.skills,
                tags=template.tags,
            )

            agent_doc = AgentDocument(
                _id=str(uuid.uuid4()),
                **agent_create.model_dump(),
            )

            # 创建简单的子智能体包装器
            sub_agent = SubAgentWrapper(agent_doc, self._llm_manager)
            self._sub_agents[agent_doc.id] = sub_agent
            await sub_agent.initialize()

    async def _main_loop(self) -> None:
        """主循环。"""
        while self._is_running:
            try:
                await self._process_task_queue()
                await self._check_completed_tasks()
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"主循环异常: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def _process_task_queue(self) -> None:
        """处理任务队列。"""
        if not self._task_queue:
            return

        task = self._task_queue.pop(0)
        await self._execute_task(task)

    async def _check_completed_tasks(self) -> None:
        """检查已完成的任务。"""
        completed_task_ids = []

        for task_id, async_task in self._running_tasks.items():
            if async_task.done():
                completed_task_ids.append(task_id)
                try:
                    await async_task
                except Exception as e:
                    logger.error(f"任务 {task_id} 执行失败: {e}", exc_info=True)

        for task_id in completed_task_ids:
            del self._running_tasks[task_id]

    async def _handle_message(self, message: Message) -> None:
        """处理接收到的消息。

        Args:
            message: 接收到的消息
        """
        if message.message_type == MessageType.TASK_COMPLETE:
            task_id = message.payload.task_id
            if task_id and task_id in self._running_tasks:
                logger.info(f"任务 {task_id} 已完成")
        elif message.message_type == MessageType.TASK_ERROR:
            task_id = message.payload.task_id
            if task_id:
                logger.error(f"任务 {task_id} 出错: {message.payload.data}")

    async def execute_task(self, task: TaskDocument) -> None:
        """执行任务。

        Args:
            task: 要执行的任务
        """
        start_time = time.time()

        try:
            # 更新任务状态
            task.status = TaskStatus.ANALYZING
            task.started_at = datetime.now(UTC)

            # 分析任务
            analysis_result = await self._analyze_task(task)

            # 更新进度
            task.progress = TaskProgress(
                current_step="分析任务",
                progress_percent=10.0,
                completed_steps=["任务接收"],
            )

            # 分解任务
            subtasks = await self._decompose_task(task, analysis_result)
            task.subtasks = subtasks

            # 调度子任务
            task.progress = TaskProgress(
                current_step="调度子任务",
                progress_percent=30.0,
                completed_steps=["任务接收", "任务分析"],
            )

            # 执行子任务
            results = await self._execute_subtasks(subtasks)

            # 聚合结果
            task.progress = TaskProgress(
                current_step="聚合结果",
                progress_percent=90.0,
                completed_steps=["任务接收", "任务分析", "调度子任务"],
            )

            final_result = await self._aggregate_results(task, results)

            # 完成任务
            task.result = final_result
            task.status = TaskStatus.COMPLETED
            task.progress = TaskProgress(
                current_step="完成",
                progress_percent=100.0,
                completed_steps=["任务接收", "任务分析", "调度子任务", "执行子任务", "聚合结果"],
            )

            execution_time = time.time() - start_time
            task.execution_seconds = execution_time
            task.completed_at = datetime.now(UTC)

            await self.complete_task(True, final_result)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = TaskResult(
                success=False,
                summary=f"任务执行失败: {str(e)}",
                errors=[str(e)],
            )
            task.completed_at = datetime.now(UTC)
            await self.complete_task(False, None)
            raise TaskError(f"Task execution failed: {e}")

    async def _analyze_task(self, task: TaskDocument) -> Dict[str, Any]:
        """分析任务。

        Args:
            task: 任务

        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            # 使用LLM分析任务
            analysis_prompt = f"""请分析以下任务,并提供:
1. 任务类型
2. 需要的能力
3. 建议的执行步骤
4. 可能的子任务分解

任务: {task.name}
描述: {task.description}
用户输入: {task.user_input}

请以JSON格式返回分析结果。"""

            # 这里简化处理,实际应该调用LLM
            return {
                "task_type": "general",
                "required_capabilities": ["问答", "信息检索"],
                "steps": ["理解需求", "收集信息", "生成回答"],
                "subtasks": [],
            }
        except Exception as e:
            return {
                "task_type": "unknown",
                "error": str(e),
            }

    async def _decompose_task(
        self, task: TaskDocument, analysis: Dict[str, Any]
    ) -> List[SubTask]:
        """分解任务为子任务。

        Args:
            task: 任务
            analysis: 任务分析结果

        Returns:
            List[SubTask]: 子任务列表
        """
        subtasks = []

        # 如果分析结果中有子任务,使用它们
        if "subtasks" in analysis and analysis["subtasks"]:
            for i, subtask_info in enumerate(analysis["subtasks"]):
                subtask = SubTask(
                    id=str(uuid.uuid4()),
                    name=subtask_info.get("name", f"子任务 {i+1}"),
                    description=subtask_info.get("description", ""),
                    status=TaskStatus.PENDING,
                )
                subtasks.append(subtask)
        else:
            # 创建默认子任务
            subtask = SubTask(
                id=str(uuid.uuid4()),
                name=f"执行任务: {task.name}",
                description=task.description,
                status=TaskStatus.PENDING,
            )
            subtasks.append(subtask)

        return subtasks

    async def _execute_subtasks(self, subtasks: List[SubTask]) -> List[TaskResult]:
        """执行子任务。

        Args:
            subtasks: 子任务列表

        Returns:
            List[TaskResult]: 子任务结果列表
        """
        results = []

        for subtask in subtasks:
            # 选择合适的子智能体
            agent = await self._select_agent_for_subtask(subtask)

            if agent:
                # 创建临时任务文档
                temp_task_doc = TaskDocument(
                    _id=subtask.id,
                    name=subtask.name,
                    description=subtask.description,
                    status=TaskStatus.PENDING,
                )

                # 分配并执行任务
                await agent.assign_task(temp_task_doc)

                # 等待任务完成(简化处理)
                subtask.status = TaskStatus.IN_PROGRESS

                # 这里简化处理,实际应该异步执行
                result = TaskResult(
                    success=True,
                    summary=f"{subtask.name} 完成",
                )
                subtask.result = result
                subtask.status = TaskStatus.COMPLETED
                subtask.completed_at = datetime.now(UTC)

                results.append(result)
            else:
                result = TaskResult(
                    success=False,
                    summary="没有找到合适的智能体",
                    errors=["No suitable agent found"],
                )
                subtask.result = result
                subtask.status = TaskStatus.FAILED
                results.append(result)

        return results

    async def _select_agent_for_subtask(self, subtask: SubTask) -> Optional[BaseAgent]:
        """为子任务选择合适的智能体。

        Args:
            subtask: 子任务

        Returns:
            Optional[BaseAgent]: 选中的智能体,如果没有则返回None
        """
        # 简单策略: 选择第一个空闲的智能体
        for agent in self._sub_agents.values():
            if agent.status == AgentStatus.IDLE:
                return agent

        return None

    async def _aggregate_results(
        self, task: TaskDocument, subtask_results: List[TaskResult]
    ) -> TaskResult:
        """聚合子任务结果。

        Args:
            task: 主任务
            subtask_results: 子任务结果列表

        Returns:
            TaskResult: 聚合后的结果
        """
        all_success = all(r.success for r in subtask_results)
        summaries = [r.summary for r in subtask_results if r.summary]

        return TaskResult(
            success=all_success,
            summary="\n".join(summaries),
            details={"subtask_results": [r.model_dump() for r in subtask_results]},
        )

    async def submit_task(self, task: TaskDocument) -> str:
        """提交任务。

        Args:
            task: 任务

        Returns:
            str: 任务ID
        """
        self._task_queue.append(task)
        return task.id

    async def shutdown(self) -> None:
        """关闭主智能体。"""
        self._is_running = False

        if self._main_loop_task:
            self._main_loop_task.cancel()
            try:
                await self._main_loop_task
            except asyncio.CancelledError:
                pass

        # 关闭所有子智能体
        for agent in self._sub_agents.values():
            await agent.destroy()

        await self.destroy()
