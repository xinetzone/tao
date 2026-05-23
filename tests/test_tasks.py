from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip("invoke", reason="invoke 仅在 dev 依赖组，本测试需要根目录 tasks.py 依赖的 invoke")

TASKS_PY = Path(__file__).resolve().parent.parent / "tasks.py"
TASKS_SPEC = importlib.util.spec_from_file_location("tasks", TASKS_PY)
tasks = importlib.util.module_from_spec(TASKS_SPEC)
sys.modules[TASKS_SPEC.name] = tasks
TASKS_SPEC.loader.exec_module(tasks)

PLATFORM = tasks.PLATFORM
REPO_ROOT = tasks.REPO_ROOT
_check_mise = tasks._check_mise
_run_step = tasks._run_step
_print_plan = tasks._print_plan
_print_success_next_steps = tasks._print_success_next_steps
_write = tasks._write


class TestPlatformDetection:
    def test_reports_current_platform(self):
        assert PLATFORM in ("win32", "linux", "darwin")

    def test_resolves_repo_root(self):
        assert os.path.isdir(REPO_ROOT)
        assert os.path.isfile(os.path.join(REPO_ROOT, "tasks.py"))


class TestCheckMise:
    @patch("tasks.shutil.which", return_value="/usr/bin/mise")
    def test_returns_path_when_found(self, _mock):
        assert _check_mise() == "/usr/bin/mise"

    @patch("tasks.shutil.which", return_value=None)
    def test_raises_exit_with_onboarding_message_when_missing(self, _mock):
        from invoke import Exit

        with pytest.raises(Exit) as exc_info:
            _check_mise()
        message = str(exc_info.value)
        assert exc_info.value.code == 1
        assert "[ERROR] 未检测到 mise，无法继续初始化。" in message
        assert "[WHY]   AgentForge 使用 mise 统一管理 Python、uv、Node 与外部工具版本。" in message
        assert "[FIX]   请先安装 mise: https://mise.jdx.dev/getting-started.html" in message
        assert "[NEXT]  安装完成后重新打开终端，并运行: mise run init" in message


class TestPlanOutput:
    @patch("tasks._write")
    def test_prints_init_plan(self, mock_write):
        _print_plan(
            "AgentForge 新手接入初始化",
            [
                "信任 mise 配置",
                "安装 mise 工具链",
                "同步 Python 依赖组",
                "执行环境一致性校验",
            ],
        )
        calls = [c[0][0] for c in mock_write.call_args_list]
        assert "[INFO] AgentForge 新手接入初始化" in calls
        assert "[INFO] 将依次执行:" in calls
        assert "[INFO]   1. 信任 mise 配置" in calls
        assert "[INFO]   4. 执行环境一致性校验" in calls

    @patch("tasks._write")
    def test_prints_success_next_steps(self, mock_write):
        _print_success_next_steps(
            "初始化完成",
            ["建议运行: mise run test", "可选检查: mise run lint"],
        )
        calls = [c[0][0] for c in mock_write.call_args_list]
        assert "[OK] 初始化完成" in calls
        assert "[NEXT] 建议运行: mise run test" in calls
        assert "[NEXT] 可选检查: mise run lint" in calls


class TestRunStep:
    @patch("tasks._write")
    @patch("subprocess.run")
    def test_reports_ok_on_success(self, mock_run, mock_write):
        mock_run.return_value.returncode = 0
        _run_step("测试步骤", ["echo", "hello"])
        calls = [c[0][0] for c in mock_write.call_args_list]
        assert "[STEP] 测试步骤" in calls
        assert "[OK]   测试步骤" in calls

    @patch("tasks._write")
    @patch("subprocess.run")
    def test_reports_onboarding_hints_on_nonzero_exit(self, mock_run, mock_write):
        mock_run.return_value.returncode = 42
        from invoke import Exit

        with pytest.raises(Exit):
            _run_step(
                "失败步骤",
                ["false"],
                "可手动运行: false",
                "命令执行失败，常见原因包括工具链未安装或当前环境未同步。",
                "修复后重新运行: mise run init",
            )
        calls = "\n".join(c[0][0] for c in mock_write.call_args_list)
        assert "[FAIL] 失败步骤" in calls
        assert "[WHY]  命令执行失败，常见原因包括工具链未安装或当前环境未同步。" in calls
        assert "[FIX]  可手动运行: false" in calls
        assert "[NEXT] 修复后重新运行: mise run init" in calls

    @patch("tasks._write")
    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_reports_onboarding_hints_on_file_not_found(self, mock_run, mock_write):
        from invoke import Exit

        with pytest.raises(Exit) as exc_info:
            _run_step(
                "缺失命令",
                ["no-such-exe"],
                "请安装缺失命令",
                "系统找不到要执行的命令。",
                "安装后重新运行: mise run init",
            )
        assert exc_info.value.code == 1
        calls = "\n".join(c[0][0] for c in mock_write.call_args_list)
        assert "[FAIL] 缺失命令" in calls
        assert "[WHY]  系统找不到要执行的命令。" in calls
        assert "[FIX]  请安装缺失命令" in calls
        assert "[NEXT] 安装后重新运行: mise run init" in calls


class TestInvokeTasksModule:
    def test_exports_init_task(self):
        import importlib

        spec = importlib.util.spec_from_file_location("tasks", TASKS_PY)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "init")
        assert hasattr(mod, "init_check")
