#!/bin/bash
# run-pass.sh - Build and run HelloPass in one step
# Usage: bash scripts/run-pass.sh [input_file]
#
# This script is designed to run inside the miniconda3:llvm container.
# From host: podman run --rm -v $(pwd):/workspace/pass:Z miniconda3:llvm \
#                bash /workspace/pass/scripts/run-pass.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${PROJECT_DIR}/build"
INPUT_FILE="${1:-${PROJECT_DIR}/test/input.c}"

echo "=== [1/3] Building HelloPass ==="
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
cmake "$PROJECT_DIR" -G Ninja \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DLLVM_DIR="$(llvm-config --cmakedir)" \
    2>&1 | tail -3
ninja
echo ""

echo "=== [2/3] Generating LLVM IR ==="
# -Xclang -disable-O0-optnone: prevent optnone attribute from skipping our pass
clang -S -emit-llvm -Xclang -disable-O0-optnone \
    "$INPUT_FILE" -o "${BUILD_DIR}/input.ll"
echo "Generated: ${BUILD_DIR}/input.ll"
echo ""

echo "=== [3/3] Running HelloPass ==="
opt -load-pass-plugin "${BUILD_DIR}/HelloPass.so" \
    -passes=hello-pass \
    -disable-output \
    "${BUILD_DIR}/input.ll"

echo "=== Done ==="
