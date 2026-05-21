#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""基于 AST 的 Python 弃用 API 检测脚本。

使用 ast 模块解析源码，检测未来版本中将移除的 API 调用模式。
比纯 grep 更精确，能区分函数调用与普通字符串匹配。

用法:
    python check_python_deprecations.py [--target-version 3.16]
"""

import ast
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEPRECATION_PATTERNS = {
    "3.16": [
        {
            "module": "asyncio",
            "names": ["iscoroutinefunction"],
            "message": "asyncio.iscoroutinefunction() 计划在 3.16 移除。改用 inspect.iscoroutinefunction()。",
        },
        {
            "module": "functools",
            "names": ["reduce"],
            "check_keywords": True,
            "message": "functools.reduce() 使用关键字参数计划在 3.16 移除。改用位置参数。",
        },
        {
            "module": "sys",
            "names": ["_enablelegacywindowsfsencoding"],
            "message": "sys._enablelegacywindowsfsencoding() 计划在 3.16 移除。",
        },
        {
            "module": "sysconfig",
            "names": ["expand_makefile_vars"],
            "message": "sysconfig.expand_makefile_vars() 计划在 3.16 移除。",
        },
    ],
    "3.17": [
        {
            "module": "datetime",
            "classes": ["datetime"],
            "methods": ["utcnow", "utcfromtimestamp"],
            "message": "datetime.datetime.utcnow()/utcfromtimestamp() 计划在 3.17 移除。改用 datetime.now(tz=datetime.UTC)。",
        },
        {
            "module": "logging",
            "names": ["warn"],
            "message": "logging.warn() 计划在 3.17 移除。改用 logging.warning()。",
        },
        {
            "module": "codecs",
            "names": ["open"],
            "message": "codecs.open() 计划在 3.17 移除。改用内置 open()。",
        },
        {
            "module": "typing",
            "names": ["Text"],
            "message": "typing.Text 计划在 3.17 移除。改用 str。",
        },
    ],
    "future": [
        {
            "module": "re",
            "names": ["match"],
            "check_fullmatch": True,
            "message": "re.match() 在 Python 3.15+ 被标记为软弃用。优先使用 re.prefixmatch() 或 re.fullmatch()。",
        },
        {
            "module": "threading",
            "names": ["currentThread", "activeCount"],
            "message": "threading 旧方法名计划在未来移除。改用 current_thread() / active_count()。",
        },
        {
            "module": "threading",
            "classes": ["Thread"],
            "methods": ["getName", "setName", "isDaemon", "setDaemon"],
            "message": "Thread 旧方法名计划在未来移除。改用 .name 属性 / .daemon 属性。",
        },
        {
            "module": "calendar",
            "names": ["January", "February"],
            "message": "calendar.January/February 计划移除。改用 calendar.JANUARY / calendar.FEBRUARY。",
        },
        {
            "module": "ssl",
            "names": ["PROTOCOL_SSLv3", "PROTOCOL_TLSv1", "PROTOCOL_TLSv1_1", "PROTOCOL_TLSv1_2"],
            "message": "ssl.PROTOCOL_* 旧常量计划移除。改用 ssl.PROTOCOL_TLS_CLIENT / ssl.PROTOCOL_TLS_SERVER。",
        },
        {
            "module": "os.path",
            "names": ["commonprefix"],
            "message": "os.path.commonprefix() 计划移除。改用 os.path.commonpath()。",
        },
        {
            "module": "shutil.rmtree",
            "names": [],
            "check_kwarg": "onerror",
            "message": "shutil.rmtree(onerror=...) 计划移除。改用 onexc=。",
        },
    ],
}


class DeprecationVisitor(ast.NodeVisitor):
    def __init__(self, target_version: str, file_path: str):
        self.target_version = target_version
        self.file_path = file_path
        self.results: list[dict] = []
        self._import_map: dict[str, str] = {}

    def _add_result(self, line: int, col: int, message: str):
        self.results.append({
            "file": self.file_path,
            "line": line,
            "col": col,
            "message": message,
        })

    def visit_Import(self, node):
        for alias in node.names:
            self._import_map[alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                full = f"{node.module}.{alias.name}"
                self._import_map[alias.asname or alias.name] = full
        self.generic_visit(node)

    def visit_Call(self, node):
        for pattern_set in DEPRECATION_PATTERNS.get(self.target_version, []):
            for pattern in DEPRECATION_PATTERNS.get("future", []):
                self._check_pattern(node, pattern)
        for pattern in DEPRECATION_PATTERNS.get(self.target_version, []):
            self._check_pattern(node, pattern)
        self.generic_visit(node)

    def _check_pattern(self, node, pattern):
        module = pattern.get("module", "")
        target_names = pattern.get("names", [])
        target_classes = pattern.get("classes", [])
        target_methods = pattern.get("methods", [])

        if isinstance(node.func, ast.Attribute):
            obj = node.func.value
            attr_name = node.func.attr

            if target_classes and isinstance(obj, ast.Attribute):
                if obj.attr in target_classes and attr_name in target_methods:
                    full_name = self._resolve_name(obj)
                    if module in full_name or not module:
                        self._add_result(node.lineno, node.col_offset, pattern["message"])
                        return

            if attr_name in target_names:
                full_name = self._resolve_name(obj)
                if module in full_name:
                    if pattern.get("check_keywords") and not node.keywords:
                        return
                    if pattern.get("check_fullmatch"):
                        return
                    self._add_result(node.lineno, node.col_offset, pattern["message"])

        elif isinstance(node.func, ast.Name):
            name = node.func.id
            if name in target_names:
                resolved = self._import_map.get(name, name)
                if module in resolved:
                    if pattern.get("check_keywords") and not node.keywords:
                        return
                    self._add_result(node.lineno, node.col_offset, pattern["message"])

        if pattern.get("check_kwarg"):
            for kw in node.keywords:
                if kw.arg == pattern["check_kwarg"]:
                    self._add_result(node.lineno, node.col_offset, pattern["message"])

    def _resolve_name(self, node):
        if isinstance(node, ast.Name):
            return self._import_map.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            return self._resolve_name(node.value) + "." + node.attr
        return ""


def scan_file(file_path: Path, target_version: str) -> list[dict]:
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except (OSError, SyntaxError):
        return []

    visitor = DeprecationVisitor(target_version, str(file_path.relative_to(PROJECT_ROOT)))
    visitor.visit(tree)
    return visitor.results


def main():
    target_version = "3.16"
    if "--target-version" in sys.argv:
        idx = sys.argv.index("--target-version")
        if idx + 1 < len(sys.argv):
            target_version = sys.argv[idx + 1]

    print(f"🔍 Python {target_version}+ 弃用 API AST 检测")
    print(f"   扫描目录: {PROJECT_ROOT}")
    print()

    exclude_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".tox"}
    total_files = 0
    all_results = []

    for py_file in PROJECT_ROOT.rglob("*.py"):
        parts = set(py_file.parts)
        if parts & exclude_dirs:
            continue
        total_files += 1
        results = scan_file(py_file, target_version)
        all_results.extend(results)

    print(f"   扫描文件: {total_files}")
    print(f"   发现潜在问题: {len(all_results)}")
    print()

    if all_results:
        for r in sorted(all_results, key=lambda x: (x["file"], x["line"])):
            print(f"  [{r['file']}:L{r['line']}:C{r['col']}]")
            print(f"    {r['message']}")
            print()

    if not all_results:
        print("   ✅ 未发现已知弃用 API 调用。")

    sys.exit(0)


if __name__ == "__main__":
    main()
