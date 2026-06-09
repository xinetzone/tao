#!/usr/bin/env bash
# 共享 CI 测试依赖同步脚本
# 由 mise.toml (install-test-deps) 和 Containerfile.test 共同引用
# 注意：两处引用需保持同步，修改此脚本即同时影响容器化和非容器化测试环境
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
    uv sync --group test --extra github-app --extra harness
elif command -v uv.exe >/dev/null 2>&1; then
    uv.exe sync --group test --extra github-app --extra harness
else
    echo "uv executable not found" >&2
    exit 127
fi
