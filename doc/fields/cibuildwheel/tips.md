# 技巧

## 为非原生架构仿真构建 Linux 轮子

cibuildwheel 支持在 Linux 上构建非原生架构，通过 binfmt_misc 内核功能进行仿真。最简单的方法是使用 GitHub Actions 上的 [`docker/setup-qemu-action`](https://github.com/docker/setup-qemu-action) 或 [`tonistiigi/binfmt`](https://hub.docker.com/r/tonistiigi/binfmt)。

查看以下配置示例，了解如何在 GitHub Actions 上设置它。一旦 QEMU 设置完成并注册，您只需设置 `CIBW_ARCHS_LINUX` 环境变量（或在 Linux 上使用 `--archs` 选项），其他架构将自动模拟。

`.github/workflows/build.yml`：
```yaml
name: Build

on: [push, pull_request]

jobs:
  build_wheels:
    name: Build wheels on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        # macos-13 is an intel runner, macos-14 is apple silicon
        os: [ubuntu-latest, ubuntu-24.04-arm, windows-latest, windows-11-arm, macos-13, macos-14]

    steps:
      - uses: actions/checkout@v4

      - name: Set up QEMU
        if: runner.os == 'Linux' && runner.arch == 'X64'
        uses: docker/setup-qemu-action@v3
        with:
          platforms: all

      - name: Build wheels
        uses: pypa/cibuildwheel@v3.0.1
        env:
          # configure cibuildwheel on Linux to build native archs ('auto'),
          # and to split the remaining architectures between the x86_64 and
          # ARM runners
          CIBW_ARCHS_LINUX: ${{ runner.arch == 'X64' && 'auto ppc64le s390x' || 'auto' }}

      - uses: actions/upload-artifact@v4
        with:
          name: cibw-wheels-${{ matrix.os }}-${{ strategy.job-index }}
          path: ./wheelhouse/*.whl
```

## 构建 CPython ABI3 轮（有限 API）

CPython 有限 API 是 Python C 扩展 API 的子集，它被声明为向前兼容，这意味着你可以为 Python 的版本编译轮，它们将与未来的版本兼容。使用有限 API 的轮被称为 ABI3 轮。

要创建构建 ABI3 轮的包，你需要配置你的构建后端来正确编译库，并使用正确的标签创建轮。[查看这个仓库](https://github.com/joerick/python-abi3-package-sample)以了解如何使用 setuptools 完成此操作。

你也可以考虑在生成的轮上运行 [`abi3audit`](https://github.com/trailofbits/abi3audit)，以检查 ABI3 违规或不一致。你可以在你的 [`repair-wheel-command`](https://cibuildwheel.pypa.io/en/stable/options/#repair-wheel-command) 中与默认命令一起运行它。

## 带可选 C 扩展的包

cibuildwheel 定义环境变量 `CIBUILDWHEEL` 为值 `1`，允许在构建轮子时将可选的 C 扩展变为强制要求。

在 Python 3 中，一种简单的方法是通过 `optional` 构造函数的 `Extension` 命名参数在你的 `setup.py` 中实现：

```python
myextension = Extension(
    "myextension",
    ["myextension.c"],
    optional=os.environ.get('CIBUILDWHEEL', '0') != '1',
)
```

## 使用 NumPy 进行构建

如果使用 NumPy，有几点可以帮助你。

首先，如果你在构建时需要 numpy 包（某些绑定工具，如 pybind11 和 nanobind 不需要），那么对于 Python <3.9，你的 `build-backend.build-requires` 的向后兼容性会稍微复杂一些：

- NumPy <1.25: 你必须使用你想要在运行时支持的最老版本的 NumPy 进行构建。
- NumPy 1.25 和 1.26: 默认情况下，你构建的任何内容都与 1.19+ 兼容，你可以使用 `#define NPY_TARGET_VERSION NPY_1_22_API_VERSION` 将最低目标设置为例如 1.22。
- NumPy 2.x: 你必须使用 NumPy 2 来支持 NumPy 2；否则与 1.25+ 相同。

所以规则是：

- Python <3.8: 使用最老的支持的 NumPy（如果你需要，可以通过辅助工具 oldest-supported-numpy 来使用）
- Python 3.9+: 使用最新支持 NumPy（2+）。

其次，可能存在你想发布的目标平台，NumPy（或其他一些科学 Python 库）尚未发布。这通常适用于新 Python 版本的候选 beta 版本，例如。要处理这个问题，你可以使用科学 Python 的每日轮。这里是例子，取决于你使用的前端：

对于像 `build` （默认）和 `pip` 这样的前端：

```toml
[tool.cibuildwheel]
environment.PIP_ONLY_BINARY = "numpy"
environment.PIP_PREFER_BINARY = "1"

[[tool.cibuildwheel.overrides]]
select = ["cp314*"]
inherit.environment = "append"
environment.PIP_EXTRA_INDEX_URL = "https://pypi.anaconda.org/scientific-python-nightly-wheels/simple/"
environment.PIP_PRERELEASE = "allow"
```

对于像 `build[uv]` 这样的前端：

```toml
[tool.cibuildwheel]
environment.UV_ONLY_BINARY = "numpy"
environment.UV_PREFER_BINARY = "1"

[[tool.cibuildwheel.overrides]]
select = ["cp314*"]
inherit.environment = "append"
environment.UV_INDEX = "https://pypi.anaconda.org/scientific-python-nightly-wheels/simple/"
environment.UV_INDEX_STRATEGY = "unsafe-best-match"
environment.UV_PRERELEASE = "allow"
```

请注意，`*ONLY_BINARY` 变量也支持 `":all:"`，并且您不需要同时使用 `*ONLY_BINARY` 和 `*PREFER_BINARY`，您可以根据是否希望缺少的 wheel 导致失败或尝试在 CI 中构建来选择使用其中一个。

## 使用 Dependabot 自动更新

在持续集成中选择不断变化的版本（如最新发布版）通常是个坏主意。如果出现故障，你无法判断是自己的代码还是上游更新导致了问题，在极端情况下，它甚至可能发生在发布期间。

有两种建议的方法来保持 cibuildwheel 的更新，这些方法涉及使用 GitHub 的 Dependabot 进行定期的拉取请求。

### 选项 1：GitHub Action

如果你使用 GitHub Actions 进行构建，可以将 cibuildwheel 作为操作使用：

```yaml
uses: pypa/cibuildwheel@v3.0.1
```

这是复合步骤，它只是使用 `pipx` 运行 `cibuildwheel`。你可以将命令行选项作为 `with:` 参数设置，并像 `env:` 那样正常使用。

然后，你的 `.github/dependabot.yml` 文件可以像这样：

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 选项 2：需求文件

第二种选择，也是唯一支持其他 CI 系统的选项，是使用 `requirements-*.txt` 文件。该文件应有独特的名称，并且只包含一个条目：

```
# requirements-cibw.txt
cibuildwheel==3.0.1
```

然后你的安装步骤中会包含 `python -m pip install -r requirements-cibw.txt`。你的 `.github/dependabot.yml` 文件可以像这样：

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
```

这也会尝试更新所有需求文件中的其他 pin，所以请确保你真的想这样做。你对所使用文件的控制仅通过目录选项来实现。

## cibuildwheel 选项的替代方案

cibuildwheel 提供了许多配置构建环境的机会。然而，您可能需要考虑将此构建配置添加到软件包本身中——通常情况下这是更受欢迎的做法，因为您的软件包的 `'sdist'` 用户也会从中受益。

### 缺少构建依赖项 

如果你的构建需要 Python 依赖项，最好将 `before-build` 添加到 `pyproject.toml` 的 [`build-system.requires`](https://www.python.org/dev/peps/pep-0518/#build-system-table) 部分。例如，如果你的项目需要 Cython 来构建，你的 pyproject.toml 可能包含如下所示的章节：

```toml
[build-system]
requires = [
    "setuptools>=42",
    "Cython",
]

build-backend = "setuptools.build_meta"
```

### 构建前需要执行的操作

在构建之前，你可能需要运行一些其他命令，比如运行执行代码生成的脚本或下载源代码树中未存储的一些数据。

与其使用 `before-all` 或 `before-build`，你可以将这些步骤整合到你的包的构建过程中。例如，如果你使用 setuptools，你可以使用类似这样的结构向你的包的 `setup.py` 添加步骤：

```python
import subprocess
import setuptools
import setuptools.command.build_py


class BuildPyCommand(setuptools.command.build_py.build_py):
    """Custom build command."""

    def run(self):
        # your custom build steps here
        # e.g.
        #   subprocess.run(['python', 'scripts/my_custom_script.py'], check=True)
        setuptools.command.build_py.build_py.run(self)


setuptools.setup(
    cmdclass={
        'build_py': BuildPyCommand,
    },
    # Usual setup() args.
    # ...
)
```

### 编译器标志

您的构建可能需要通过环境变量设置一些编译器标志。可以考虑将这些内容整合到您的软件包中，例如在 `setup.py` 中使用 [`extra_compile_args` 和 `extra_link_args`](https://setuptools.pypa.io/en/latest/userguide/ext_modules.html#setuptools.Extension)。
