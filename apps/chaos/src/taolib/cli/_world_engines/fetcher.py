"""Git Fetch 引擎 — 从 Git 仓库获取 Fragment 源码。"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from taolib.cli._world_engines.registry_cache import inject_token


class FetchError(Exception):
    """Fetch 操作失败异常。"""


@dataclass
class FetchResult:
    """Fetch 操作结果。"""

    local_path: Path  # 已 fetch 到本地的目录
    manifest_path: Path  # manifest 文件的完整路径
    cleanup: Callable[[], None]  # 清理临时目录的回调


def _make_cleanup(tmpdir: Path) -> Callable[[], None]:
    """构造临时目录清理回调。"""

    def _cleanup() -> None:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return _cleanup


def fetch_git(
    git_url: str,
    git_ref: str,
    manifest_path: str = "manifest.toml",
) -> FetchResult:
    """从 Git 仓库获取 Fragment 源码到临时目录。

    流程：

    1. 创建临时目录。
    2. 执行 ``git clone --depth 1 --branch {git_ref} {git_url} {tmpdir}``。
    3. 验证 ``manifest_path`` 文件存在。
    4. 返回 :class:`FetchResult`。

    Args:
        git_url: Git 仓库 URL。
        git_ref: 分支名或 tag 名。
        manifest_path: manifest 文件相对于仓库根的路径。

    Returns:
        包含本地路径、manifest 路径和清理回调的 :class:`FetchResult`。

    Raises:
        FetchError: git 不可用、clone 失败、超时或 manifest 不存在。
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="world-fetch-"))
    cleanup = _make_cleanup(tmpdir)

    authed_url = inject_token(git_url)
    cmd = [
        "git",
        "clone",
        "--depth",
        "1",
        "--branch",
        git_ref,
        authed_url,
        str(tmpdir),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError as exc:
        cleanup()
        raise FetchError("git 命令不可用，请确认已安装 git 并加入 PATH") from exc
    except subprocess.TimeoutExpired as exc:
        cleanup()
        raise FetchError(f"git clone 超时（>120s）：{git_url}") from exc

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        cleanup()
        if "Authentication" in stderr or "could not read Username" in stderr:
            raise FetchError(
                f"认证失败: {git_url}\n请检查 WORLD_TOKEN 环境变量是否正确设置"
            )
        raise FetchError(
            f"git clone 失败 (exit={result.returncode}): {git_url}@{git_ref}\n{stderr}"
        )

    manifest_full_path = tmpdir / manifest_path
    if not manifest_full_path.exists():
        cleanup()
        raise FetchError(f"manifest 文件不存在: {manifest_path}")

    return FetchResult(
        local_path=tmpdir,
        manifest_path=manifest_full_path,
        cleanup=cleanup,
    )
