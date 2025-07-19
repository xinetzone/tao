# 发布到 PyPI

在构建好你的轮子后，你可能会想将它们发布到 PyPI。

## 自动方法

如果你对包的发布过程不需要太多控制，你可以设置你的 CI 提供者直接将轮子发布到 PyPI。你只需要增加版本号并打上标签。

具体设置方法取决于你使用的 CI 提供者。但通常，过程如下：

- 使用 `cibuildwheel` 构建你的轮子
- 使用[构建](https://github.com/pypa/build)工具构建 `sdist`
- 检查当前 CI 运行是否在发布期间进行（例如，它是响应 `vXX` 标签的）
- 将这些资产集中到一个运行器上
- 使用 `twine upload <paths>` 将它们上传到 PyPI

GitHub actions 在所有运行器中都将 pipx 作为支持的包管理器，以及 `pypa/gh-action-pypi-publish`，它可以用作 `twine` 的替代。除了现有的运行 `cibuildwheel` 以制作轮子的作业之外，你可能还想构建 `sdist`：

```yaml
 make_sdist:
    name: Make SDist
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Optional, use if you use setuptools_scm
        submodules: true  # Optional, use if you have submodules

    - name: Build SDist
      run: pipx run build --sdist

    - uses: actions/upload-artifact@v4
      with:
        name: cibw-sdist
        path: dist/*.tar.gz
```

然后，你需要发布先前作业构建的工件。这个最终的作业应该只在发布或标签上运行，取决于你的偏好。它从 `sdist` 和 `wheel` 作业中收集工件，并将它们上传到 PyPI。发布环境（示例中的 `pypi` ）将在该工作流第一次运行时创建。

```yaml
 upload_all:
    needs: [build_wheels, make_sdist]
    environment: pypi
    permissions:
      id-token: write
    runs-on: ubuntu-latest
    if: github.event_name == 'release' && github.event.action == 'published'
    steps:
    - uses: actions/download-artifact@v4
      with:
        pattern: cibw-*
        path: dist
        merge-multiple: true

    - uses: pypa/gh-action-pypi-publish@release/v1
```

上述示例使用 PyPI 受信任发布来交付轮子，这需要对[新项目](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc)或[现有项目](https://docs.pypi.org/trusted-publishers/adding-a-publisher)在 PyPI 端进行一些配置。您可以使用 Dependabot 来保持发布动作的更新。

参见 [`examples/github-deploy.yml`](https://github.com/pypa/cibuildwheel/blob/main/examples/github-deploy.yml) 获取自动上传轮子到 PyPI 的示例配置。也请参见 [`scikit-hep.org/developer/gha_wheels`](https://scikit-hep.org/developer/gha_wheels) 获取完整指南。