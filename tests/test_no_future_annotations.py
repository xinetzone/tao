"""守护门禁：禁止 ``from __future__ import annotations``（PEP 563 样板）。

本发行版 requires-python >= 3.14，注解默认按 PEP 649 惰性求值，该 future
import 纯属冗余且语义有别；代码生成与旧实现复制有语料惯性反复加回，故在
测试层硬阻断——任何文件加回即红。检测基于 AST（只认真实的 ImportFrom 节点），
注释、文档字符串与本守护自身的字符串常量均不误报。
"""

import ast
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SCAN_DIRS = ("src", "tests")


def _py_files() -> list[Path]:
    files: list[Path] = []
    for dirname in _SCAN_DIRS:
        files.extend(sorted((_PROJECT_ROOT / dirname).rglob("*.py")))
    return files


def _has_future_annotations(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module != "__future__":
            continue
        if any(alias.name == "annotations" for alias in node.names):
            return True
    return False


@pytest.mark.parametrize(
    "path",
    _py_files(),
    ids=lambda p: p.relative_to(_PROJECT_ROOT).as_posix(),
)
def test_no_future_annotations(path: Path) -> None:
    assert not _has_future_annotations(path), (
        f"{path.relative_to(_PROJECT_ROOT).as_posix()} 含冗余的 PEP 563 future import；"
        "Python 3.14+ 已默认 PEP 649 惰性注解，直接删除该行"
    )
