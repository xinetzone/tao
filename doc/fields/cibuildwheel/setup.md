# cibuildwheel 入门指南

Python 轮子很棒。跨 Mac、Linux、Windows，在多个 Python 版本上构建它们并不容易。

cibuildwheel 正是为了帮助您。cibuildwheel 在您的 CI 服务器上运行——目前它支持 GitHub Actions、Azure Pipelines、Travis CI、CircleCI 和 GitLab CI——并在所有您的平台上构建和测试您的轮子。

在设置 CI 之前，可以在本地测试 cibuildwheel，以便快速迭代和排查问题，而无需每次提交更改、推送，然后检查 CI 日志。

像这样安装 cibuildwheel 并运行构建：
```bash
# run using uv
uvx cibuildwheel

# or pipx
pipx run cibuildwheel

# or, install it first
pip install cibuildwheel
cibuildwheel
```

```{tip}
即使你不是在 Linux 系统上，也可以通过向 cibuildwheel 传递 `--platform linux` 选项来构建 Linux 轮。在大多数机器上，最容易尝试的构建是 Linux 构建。除了 Docker 守护程序（如 Docker Desktop）之外，你不需要安装任何其他软件。cibuildwheel 支持每个平台都有其自己的系统要求和平台特定行为。有关详细信息，请参阅[平台页面](https://cibuildwheel.pypa.io/en/stable/platforms/)。
```

如果你将你的选项写入 `pyproject.toml`，你可以在本地工作，并在运行 CI 时自动获取这些选项。

```toml
[tool.cibuildwheel]
before-all = "uname -a"
```

然后调用 cibuildwheel，例如：
```bash
cibuildwheel
```

- 一旦在本地成功构建，你就可以继续[设置 CI 服务](https://cibuildwheel.pypa.io/en/stable/ci-services/)。
- 查看[完整选项参考](https://cibuildwheel.pypa.io/en/stable/options/)，了解 cibuildwheel 能做什么。
- 查看[FAQ](https://cibuildwheel.pypa.io/en/stable/faq/)以获取常见问题的答案。
