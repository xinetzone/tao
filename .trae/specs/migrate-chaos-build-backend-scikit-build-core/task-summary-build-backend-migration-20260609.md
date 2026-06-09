# 任务执行复盘报告：apps/chaos 构建后端迁移与 CMakeLists 优化

## 1. 执行概览

本次任务围绕 `apps/chaos` Python 项目的构建系统迁移展开，核心目标是将 `pdm-backend` 替换为 `scikit-build-core`，以改善构建速度和降低进程锁定风险，同时保持原有发布、安装和运行行为不被破坏。

最终完成内容：

- 将 `apps/chaos/pyproject.toml` 的构建后端从 `pdm.backend` 迁移到 `scikit_build_core.build`
- 移除 PDM backend 专属配置
- 使用 `setuptools-scm` 保留 SCM 动态版本能力
- 保留 `src/taolib` 源码布局和包打包路径
- 明确禁用无实际用途的 CMake 构建流程
- 按用户反馈将 `podman>=5.8.0` 从主依赖移入 `flowkit` 可选依赖
- 更新相关构建文档和源码注释
- 执行构建、安装、生产打包、lint、format、测试验证
- 将根级 `CMakeLists.txt` 优化为最小规范 CMake 项目

当前状态：任务已完成，验证通过，未执行 git commit。

---

## 2. 目标背景

用户最初要求针对 `apps/chaos/pyproject.toml` 进行构建后端迁移，原因是当前 PDM backend 存在：

- 运行速度慢
- 构建进程容易被锁定
- 不利于稳定的本地构建和生产打包

明确实施要求包括：

1. 先完整梳理原 PDM backend 配置，包括构建依赖、打包规则、项目元数据配置等。
2. 移除所有与 PDM backend 相关的配置。
3. 按 `scikit-build-core` 官方规范配置新后端。
4. 执行本地构建测试、依赖安装测试、生产环境打包测试。
5. 确保迁移后构建产物与原后端等价，不影响发布、安装和运行。
6. 更新相关构建文档说明。

---

## 3. 原 PDM backend 配置梳理

迁移前核心配置：

```toml
[build-system]
build-backend = "pdm.backend"
requires = ["pdm-backend"]
```

PDM 动态版本配置：

```toml
[tool.pdm.version]
source = "scm"
fallback_version = "0.0.0"
write_to = "taolib/_version.py"
write_template = "__version__ = '{}'
"
```

PDM 打包配置：

```toml
[tool.pdm.build]
includes = ["src/taolib"]
package-dir = "src"
```

对应功能语义：

| 配置 | 功能 |
|---|---|
| `pdm.backend` | PEP 517 构建后端 |
| `pdm-backend` | 构建依赖 |
| `source = "scm"` | 从 Git SCM 派生版本号 |
| `fallback_version = "0.0.0"` | SCM 信息不可用时的兜底版本 |
| `write_to` | 构建时写入版本文件 |
| `includes = ["src/taolib"]` | 指定被打包的源码目录 |
| `package-dir = "src"` | 使用 `src` layout |

---

## 4. 最终实现方案

迁移后的构建系统配置：

```toml
[build-system]
build-backend = "scikit_build_core.build"
requires = ["scikit-build-core[pyproject]>=0.12", "setuptools-scm>=8"]
```

`scikit-build-core` 配置：

```toml
[tool.scikit-build]
minimum-version = "build-system.requires"
metadata.version.provider = "scikit_build_core.metadata.setuptools_scm"
sdist.include = ["README.md", "LICENSE", "pyproject.toml", "src/taolib"]
sdist.exclude = ["src/taolib/**/__pycache__/**", "src/taolib/**/*.pyc", "src/taolib/**/*.pyo"]
sdist.cmake = false
wheel.packages = ["src/taolib"]
wheel.cmake = false
```

动态版本配置：

```toml
[tool.setuptools_scm]
fallback_version = "0.0.0"
version_file = "src/taolib/_version.py"
version_file_template = "__version__ = '{version}'
"
```

关键设计点：

- `scikit-build-core` 接管构建后端。
- `setuptools-scm` 复刻原 PDM SCM 动态版本能力。
- `wheel.packages = ["src/taolib"]` 保留源码包布局。
- `wheel.cmake = false` 和 `sdist.cmake = false` 避免无意义 CMake 构建。
- `sdist.include` 显式保留 README、LICENSE、pyproject 和源码包。

---

## 5. 用户反馈与修正

迁移过程中，用户指出 `podman>=5.8.0` 不应放在主依赖中。

修正后主依赖为：

```toml
dependencies = [
    "packaging>=24,<26",
]
```

`podman` 保留在 `flowkit` optional dependency：

```toml
flowkit = [
    "nuitka>=1,<2",
    "podman>=5.8.0",
]
```

该调整使默认安装更轻量，同时保留 `flowkit` 功能所需依赖。

---

## 6. CMakeLists.txt 优化

迁移过程中确认 `apps/chaos/CMakeLists.txt` 原内容只有：

```cmake
cmake_minimum_required(VERSION 3.29)
```

由于当前主包是纯 Python 包，没有实际 C/C++ 扩展目标，因此没有启用 CMake 构建。

用户后续要求优化该文件，并确认使用：

- 项目名：`chaos`
- 最低 CMake 版本：`3.29`
- 语言声明：`LANGUAGES NONE`

最终内容：

```cmake
cmake_minimum_required(VERSION 3.29)

project(chaos LANGUAGES NONE)
```

该方案的意义：

- 保留根级 CMake 文件
- 使其成为合法的最小 CMake 项目
- 不声明 C/C++ 编译语言
- 不添加编译目标
- 不影响当前 `scikit-build-core` 纯 Python 打包配置

---

## 7. 修改文件清单

### `apps/chaos/pyproject.toml`

核心迁移文件。完成：

- 替换 build backend
- 移除 PDM backend 配置
- 添加 `scikit-build-core` 配置
- 添加 `setuptools-scm` 动态版本配置
- 保留 `src/taolib` 包路径
- 调整主依赖与 optional dependency
- 禁用 CMake 构建流程

### `apps/chaos/CMakeLists.txt`

从单行 `cmake_minimum_required` 优化为最小规范 CMake 项目。

### `apps/chaos/src/taolib/__init__.py`

更新旧注释，避免继续引用 `pdm-backend` 和 `[tool.pdm.version]`。

### `docs/tech/build-conventions.md`

更新构建约定说明：

- 后端改为 `scikit-build-core`
- 动态版本由 `setuptools-scm` 提供
- 纯 Python 包禁用 CMake 构建

### `apps/chaos/README.md`

更新项目构建说明，说明当前使用 `scikit-build-core` 和 `setuptools-scm`。

### `apps/chaos/src/taolib/flowkit/podman_win.py`

修复 Ruff `UP015`：移除不必要的显式读模式，并应用格式化。

### `apps/chaos/src/taolib/flowkit/podman_context.py`

应用 Ruff 格式化。

### `.trae/specs/migrate-chaos-build-backend-scikit-build-core/*`

完成 spec、tasks、checklist 的任务记录和状态更新。

---

## 8. 验证结果

已完成以下验证：

| 验证项 | 命令/方式 | 结果 |
|---|---|---|
| 本地构建 | `uv build` | 通过 |
| 指定目录构建 | `uv build --out-dir .temp\task4-dist` | 通过 |
| 生产打包 | `uv build --wheel --sdist --out-dir .temp\task4-prod-dist` | 通过 |
| 隔离安装 | `uv venv` + `uv pip install <wheel>` | 通过 |
| 包导入 | `python -c "import taolib; print(taolib.__name__)"` | 输出 `taolib` |
| 元数据检查 | 检查 main deps / extras / artifact metadata | 通过 |
| Ruff lint | `uv run --no-sync ruff check .` | 通过 |
| Ruff format | `uv run --no-sync ruff format --check .` | 通过 |
| Pytest | `uv run --no-sync pytest tests\test_validate_roles.py` | `8 passed` |

验证结论：

- wheel 和 sdist 可正常生成。
- wheel 可安装。
- `taolib` 可正常导入。
- 主依赖不再包含 `podman`。
- `flowkit` extra 保留 `podman`。
- 没有触发无意义 CMake 构建。
- lint、format、目标测试均通过。

---

## 9. 关键决策复盘

### 决策一：迁移到 `scikit-build-core`，但禁用 CMake

原因：当前项目主包是纯 Python，根级 CMake 文件没有实际扩展目标。禁用 CMake 可避免引入额外构建步骤和潜在失败点。

最终配置：

```toml
wheel.cmake = false
sdist.cmake = false
```

### 决策二：用 `setuptools-scm` 保留动态版本

原因：原 PDM backend 使用 SCM 派生版本，迁移后需要保留等价能力。

最终通过 `scikit-build-core` metadata provider 接入 `setuptools-scm`。

### 决策三：修正版本文件路径

原 PDM 配置的 `write_to = "taolib/_version.py"` 与 `src` layout 不完全匹配。迁移后改为：

```toml
version_file = "src/taolib/_version.py"
```

### 决策四：`podman` 只保留在 `flowkit` extra

原因：`podman` 属于 flowkit 功能相关依赖，不应成为主包默认安装依赖。

### 决策五：CMakeLists 只做最小规范化

原因：当前没有实际 C/C++ 构建需求，因此只补齐项目声明，不添加 target，不扩大范围。

---

## 10. 问题与处理

### 问题一：根目录存在空壳式 CMakeLists.txt

处理：

- 在 `pyproject.toml` 中禁用 CMake 构建。
- 将 `CMakeLists.txt` 优化为最小规范结构。

结果：构建未被 CMake 干扰。

### 问题二：`podman` 初始依赖归属不符合预期

处理：

- 从 `[project].dependencies` 移除。
- 保留在 `[project.optional-dependencies].flowkit`。

结果：默认安装更干净，flowkit 能力不受影响。

### 问题三：Ruff 检查发现历史代码问题

处理：

- 修复 `podman_win.py` 的 `UP015`。
- 格式化 `podman_win.py` 和 `podman_context.py`。

结果：lint 和 format 通过。

### 问题四：早期构建输出状态不够清晰

处理：

- 后续使用明确 `--out-dir` 重新执行构建验证。

结果：构建产物稳定生成，验证结果清晰。

---

## 11. 目标达成度分析

| 目标 | 达成情况 |
|---|---|
| 梳理原 PDM backend 配置 | 已完成 |
| 移除 PDM backend 配置 | 已完成 |
| 配置 `scikit-build-core` | 已完成 |
| 保留动态版本 | 已完成 |
| 保留包路径和产物行为 | 已完成 |
| 执行本地构建测试 | 已完成 |
| 执行依赖安装测试 | 已完成 |
| 执行生产打包测试 | 已完成 |
| 验证运行导入 | 已完成 |
| 更新相关文档 | 已完成 |
| 优化 CMakeLists.txt | 已完成 |

综合评价：本次任务目标已完整达成。

---

## 12. 经验总结

### 成功经验

- 构建后端迁移前应先盘点原后端配置语义，避免遗漏动态版本、包路径等隐性行为。
- 对纯 Python 项目使用 `scikit-build-core` 时，应明确判断是否需要 CMake。
- 根目录存在 `CMakeLists.txt` 不代表一定要启用 CMake 构建。
- 主依赖和 optional dependency 应按功能边界划分，避免默认安装过重。
- 构建验证最好覆盖 wheel、sdist、安装、导入、元数据和测试。

### 可改进点

- 应更早检查根级 `CMakeLists.txt`，减少后续补充判断。
- 构建验证一开始就使用明确输出目录，避免产物位置和命令状态混淆。
- 对依赖归属可在迁移设计阶段更明确地区分主依赖和功能 extra。
- 执行 Ruff 修复前可先说明将触及非核心迁移文件。

---

## 13. 后续建议

建议后续只做轻量收尾，不再扩大修改范围：

1. 查看 git diff，确认最终变更范围。
2. 如需提交，再生成 conventional commit message。
3. 如 CI 中仍有 PDM backend 字样，可做一次 CI 配置专项搜索。
4. 如果未来确实接入 C/C++ 扩展，再重新启用 `wheel.cmake` 并扩展 `CMakeLists.txt`。

当前不需要继续修改代码。
