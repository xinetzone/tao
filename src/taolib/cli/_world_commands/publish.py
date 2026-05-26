"""``world publish`` 子命令 — 将本地组件发布到 Registry。"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from .._world_engines.manifest_parser import find_world_toml, parse_manifest
from .._world_engines.registry_config import load_registry_config
from .._world_engines.registry_index import (
    _version_tuple,
    query_entry,
    resolve_index_path,
)


def register_publish_parser(subparsers: argparse._SubParsersAction) -> None:
    """注册 publish 子命令到 argparse。"""
    parser = subparsers.add_parser("publish", help="发布组件到 Registry")
    parser.add_argument("path", nargs="?", default=".", help="组件目录路径")
    parser.add_argument("--registry", default=None, help="目标 Registry 名称")
    parser.add_argument("--tag", default=None, help="Git tag 名称")
    parser.add_argument(
        "--dry-run", action="store_true", default=False, help="模拟发布"
    )
    parser.set_defaults(handler=handle_publish)


def _flatten_contents(manifest: object) -> list[str]:
    """将 FragmentContents 的所有字段合并为扁平文件列表。"""
    contents = manifest.contents  # type: ignore[attr-defined]
    return [
        *contents.rules,
        *contents.skills,
        *contents.scripts,
        *contents.docs,
        *contents.templates,
    ]


def _escape_toml_string(value: str) -> str:
    """转义 TOML 基础字符串中的特殊字符。"""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def handle_publish(args: argparse.Namespace) -> int:
    """world publish 命令处理函数。"""
    # === Step 1: validate ===
    component_path = Path(args.path).resolve()
    manifest_path = component_path / "manifest.toml"

    if not manifest_path.exists():
        print(
            f"错误: 未找到 manifest.toml: {manifest_path}",
            file=sys.stderr,
        )
        return 1

    try:
        manifest = parse_manifest(manifest_path)
    except Exception as exc:
        print(f"错误: 解析 manifest.toml 失败: {exc}", file=sys.stderr)
        return 1

    # 检查必填字段
    if not manifest.name:
        print("错误: manifest 缺少必填字段 name", file=sys.stderr)
        return 1
    if not manifest.version:
        print("错误: manifest 缺少必填字段 version", file=sys.stderr)
        return 1
    if not manifest.description:
        print("错误: manifest 缺少必填字段 description", file=sys.stderr)
        return 1

    # 检查 contents 中声明的文件实际存在
    all_contents = _flatten_contents(manifest)
    for rel_path in all_contents:
        full_path = component_path / rel_path.rstrip("/\\")
        if not full_path.exists():
            print(
                f"错误: contents 声明的文件不存在: {rel_path}",
                file=sys.stderr,
            )
            return 1

    # === Step 2: version check ===
    world_toml_path = find_world_toml()
    if world_toml_path is None:
        print(
            "错误: 未找到 world.toml，请确认位于 AgentForge 世界目录",
            file=sys.stderr,
        )
        return 1
    agents_dir = world_toml_path.parent

    registry_sources = load_registry_config(agents_dir)
    if not registry_sources:
        print(
            "错误: 未配置 Registry 源（.agents/registry.toml）",
            file=sys.stderr,
        )
        return 1

    # 定位目标 Registry
    registry_name: str = ""
    target_source = None
    if args.registry:
        for source in registry_sources:
            if source.name == args.registry:
                target_source = source
                registry_name = source.name
                break
        if target_source is None:
            print(
                f"错误: 未找到指定的 Registry: {args.registry}",
                file=sys.stderr,
            )
            return 1
    else:
        target_source = registry_sources[0]
        registry_name = target_source.name

    index_path = resolve_index_path(target_source)
    if index_path is None:
        print(
            f"错误: 无法解析 Registry '{registry_name}' 的 Index 路径",
            file=sys.stderr,
        )
        return 1

    # 查询已有条目，进行版本递增检查
    existing_entry = query_entry(index_path, manifest.name)
    if existing_entry is not None and existing_entry.versions:
        max_existing = max(
            _version_tuple(v.version) for v in existing_entry.versions
        )
        new_version = _version_tuple(manifest.version)
        if new_version <= max_existing:
            max_version_str = ".".join(str(p) for p in max_existing)
            print(
                f"错误: 新版本 {manifest.version} 必须大于已有最大版本"
                f" {max_version_str}",
                file=sys.stderr,
            )
            return 1

    # === Step 3: tag (除非 --dry-run) ===
    tag_name = args.tag or f"v{manifest.version}"

    if not args.dry_run:
        # 创建 Git tag
        result = subprocess.run(
            ["git", "tag", tag_name],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            print(
                f"错误: 创建 Git tag 失败: {stderr}",
                file=sys.stderr,
            )
            return 3

        # 推送 tag
        result = subprocess.run(
            ["git", "push", "origin", tag_name],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            print(
                f"错误: 推送 Git tag 失败: {stderr}",
                file=sys.stderr,
            )
            return 3

    # === Step 4: index update (除非 --dry-run) ===
    if not args.dry_run:
        # 确定 category 和 index 文件路径
        if existing_entry is not None:
            category = existing_entry.category
        else:
            category = manifest.name[:2]

        category_dir = index_path / "fragments" / category
        entry_file = category_dir / f"{manifest.name}.toml"

        now_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        if entry_file.exists():
            # 追加新版本条目并更新 latest
            existing_text = entry_file.read_text(encoding="utf-8")

            # 构建新的 [[versions]] 条目
            new_version_block = (
                f"\n[[versions]]\n"
                f'version = "{_escape_toml_string(manifest.version)}"\n'
                f'git_url = "{_escape_toml_string(target_source.url)}"\n'
                f'git_ref = "{_escape_toml_string(tag_name)}"\n'
                f'manifest_path = "manifest.toml"\n'
                f"yanked = false\n"
                f'published_at = "{now_iso}"\n'
            )

            # 替换 [latest] 段
            latest_pattern = re.compile(
                r"\[latest\]\s*\n(?:.*\n)*?(?=\n*\Z|\n*\[)",
                re.MULTILINE,
            )
            new_latest = (
                f"[latest]\n"
                f'stable = "{_escape_toml_string(manifest.version)}"\n'
            )

            if latest_pattern.search(existing_text):
                # 在 [latest] 之前插入新版本，然后替换 [latest]
                updated_text = latest_pattern.sub(new_latest, existing_text)
                # 在 [latest] 之前插入新版本条目
                latest_pos = updated_text.find("[latest]")
                updated_text = (
                    updated_text[:latest_pos]
                    + new_version_block
                    + "\n"
                    + updated_text[latest_pos:]
                )
            else:
                # 没有 [latest] 段，直接追加
                updated_text = (
                    existing_text.rstrip("\n")
                    + "\n"
                    + new_version_block
                    + "\n"
                    + new_latest
                )

            entry_file.write_text(updated_text, encoding="utf-8")
        else:
            # 首次发布：创建完整的 Index 条目 TOML
            category_dir.mkdir(parents=True, exist_ok=True)

            new_entry_text = (
                f"[metadata]\n"
                f'name = "{_escape_toml_string(manifest.name)}"\n'
                f'description = "{_escape_toml_string(manifest.description)}"\n'
                f'authors = []\n'
                f'license = "MIT"\n'
                f"keywords = []\n"
                f'category = "{_escape_toml_string(category)}"\n'
                f'type = "fragment"\n'
                f"\n"
                f"[source]\n"
                f'repository = "{_escape_toml_string(target_source.url)}"\n'
                f"\n"
                f"[[versions]]\n"
                f'version = "{_escape_toml_string(manifest.version)}"\n'
                f'git_url = "{_escape_toml_string(target_source.url)}"\n'
                f'git_ref = "{_escape_toml_string(tag_name)}"\n'
                f'manifest_path = "manifest.toml"\n'
                f"yanked = false\n"
                f'published_at = "{now_iso}"\n'
                f"\n"
                f"[latest]\n"
                f'stable = "{_escape_toml_string(manifest.version)}"\n'
            )

            entry_file.write_text(new_entry_text, encoding="utf-8")

    # === Step 5: 输出摘要 ===
    if args.dry_run:
        print(f"[dry-run] 将发布: {manifest.name} {manifest.version}")
        print(f"[dry-run] Tag: {tag_name}")
        print(f"[dry-run] Registry: {registry_name}")
    else:
        print(f"已发布: {manifest.name} {manifest.version}")
        print(f"Tag: {tag_name}")
        print(f"Registry: {registry_name}")

    return 0
