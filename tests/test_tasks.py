from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

TASKS_PY = Path(__file__).resolve().parent.parent / "tasks.py"
TASKS_SPEC = importlib.util.spec_from_file_location("tasks", TASKS_PY)
tasks = importlib.util.module_from_spec(TASKS_SPEC)
sys.modules[TASKS_SPEC.name] = tasks
TASKS_SPEC.loader.exec_module(tasks)

PLATFORM = tasks.PLATFORM
REPO_ROOT = tasks.REPO_ROOT
_check_mise = tasks._check_mise
_run_step = tasks._run_step
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
    def test_raises_exit_when_missing(self, _mock):
        from invoke import Exit

        with pytest.raises(Exit) as exc_info:
            _check_mise()
        assert exc_info.value.code == 1
        assert "未检测到 mise" in str(exc_info.value)


class TestRunStep:
    @patch("tasks._write")
    @patch("subprocess.run")
    def test_reports_ok_on_success(self, mock_run, mock_write):
        mock_run.return_value.returncode = 0
        _run_step("测试步骤", ["echo", "hello"])
        calls = [c[0][0] for c in mock_write.call_args_list]
        assert "[STEP] 测试步骤" in calls
        assert "[OK]   测试步骤" in calls

    @patch("subprocess.run")
    def test_reports_fail_on_nonzero_exit(self, mock_run):
        mock_run.return_value.returncode = -999
        from invoke import Exit

        with pytest.raises(Exit) as exc_info:
            _run_step("失败步骤", ["false"], "修复提示")
        assert exc_info.value.code == -999

    @patch("tasks._write")
    @patch("subprocess.run")
    def test_reports_fail_and_fix_hint_on_nonzero_exit(self, mock_run, mock_write):
        mock_run.return_value.returncode = 42
        from invoke import Exit

        with pytest.raises(Exit):
            _run_step("失败步骤", ["false"], "修复提示")
        calls = "".join(c[0][0] for c in mock_write.call_args_list)
        assert "[FAIL] 失败步骤" in calls
        assert "[FIX]  修复提示" in calls

    @patch("tasks._write")
    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_reports_fail_on_file_not_found(self, mock_run, mock_write):
        from invoke import Exit

        with pytest.raises(Exit) as exc_info:
            _run_step("缺失命令", ["no-such-exe"], "请安装")
        assert exc_info.value.code == 1
        calls = "".join(c[0][0] for c in mock_write.call_args_list)
        assert "[FAIL] 缺失命令" in calls
        assert "[FIX]  请安装" in calls


class TestInvokeTasksModule:
    def test_exports_init_task(self):
        import importlib

        spec = importlib.util.spec_from_file_location("tasks", TASKS_PY)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "init")
        assert hasattr(mod, "init_check")
