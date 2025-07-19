# GitHub Actions

要使用 GitHub Actions 构建 Linux、macOS 和 Windows 轮子，请在您的仓库中创建 `.github/workflows/build_wheels.yml` 文件。

## Action

对于 GitHub Actions，`cibuildwheel` 提供了可以使用的 Action。这是简洁的，并且可以通过 GitHub 的 Dependabot 实现更轻松的自动更新；参见[自动更新](https://cibuildwheel.pypa.io/en/stable/faq/#automatic-updates)。

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

      - name: Build wheels
        uses: pypa/cibuildwheel@v3.0.1
        # env:
        #   CIBW_SOME_OPTION: value
        #   ...
        # with:
        #   package-dir: .
        #   output-dir: wheelhouse
        #   config-file: "{package}/pyproject.toml"

      - uses: actions/upload-artifact@v4
        with:
          name: cibw-wheels-${{ matrix.os }}-${{ strategy.job-index }}
          path: ./wheelhouse/*.whl
```

使用 `env:` 传递[构建选项](https://cibuildwheel.pypa.io/en/stable/options/)，使用 `with:` 设置 `package-dir: .`、`output-dir: wheelhouse` 和 `config-file: ''` 的位置（这些值是默认值）。

## `pipx`

GitHub Actions runners 已安装 `pipx`，因此您可以轻松地通过一行代码进行构建。这是该操作内部的工作方式；该操作形式的主要优势是通过 GitHub 的 Dependabot 进行轻松更新。

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

      - name: Build wheels
        run: pipx run cibuildwheel==3.0.1

      - uses: actions/upload-artifact@v4
        with:
          name: cibw-wheels-${{ matrix.os }}-${{ strategy.job-index }}
          path: ./wheelhouse/*.whl
```

## 通用

这是使用 `setup-python` 和 `pip` 的最通用形式；它看起来最像其他 CI 示例。如果你想要避免使用那些利用 GitHub Actions 功能或预先安装的 `pipx` 的 `setup`，这可能适合你。

```yaml
name: Build

on: [push, pull_request]

jobs:
  build_wheels:
    name: Build wheels on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, ubuntu-24.04-arm, windows-latest, windows-11-arm, macos-13, macos-latest]

    steps:
      - uses: actions/checkout@v4

      # Used to host cibuildwheel
      - uses: actions/setup-python@v5

      - name: Install cibuildwheel
        run: python -m pip install cibuildwheel==3.0.1

      - name: Build wheels
        run: python -m cibuildwheel --output-dir wheelhouse
        # to supply options, put them in 'env', like:
        # env:
        #   CIBW_SOME_OPTION: value
        #   ...

      - uses: actions/upload-artifact@v4
        with:
          name: cibw-wheels-${{ matrix.os }}-${{ strategy.job-index }}
          path: ./wheelhouse/*.whl
```

## 提交

提交 `.github/workflows/build_wheels.yml` 文件，并推送到 GitHub——可以推送到你的默认分支，也可以推送到 PR 分支。构建应该会自动开始。

有关此文件的更多信息，请查看[文档](https://help.github.com/en/actions/reference/workflow-syntax-for-github-actions)。

[`examples/github-deploy.yml`](https://github.com/pypa/cibuildwheel/blob/main/examples/github-deploy.yml) 将这个最小示例扩展到包含 iOS 和 Pyodide 构建，并展示如何自动将构建的轮子上传到 PyPI。