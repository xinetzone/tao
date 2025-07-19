# 故障排除

如果您的 wheel 文件没有成功编译，可能是在您的配置中存在错误。

为了快速测试您的配置，而无需进行 git push 并等待代码在 CI 上构建，您可以在本地的 Docker 容器中[测试 Linux 构建](https://cibuildwheel.pypa.io/en/stable/platforms/#linux)。

## 依赖项缺失

有时，由于缺少依赖项，构建会失败。

如果构建缺少 Python 包，你应该将其[添加到 pyproject.toml 中](https://cibuildwheel.pypa.io/en/stable/faq/#cibw-options-alternatives-deps)。

如果你需要构建工具（例如 cmake、automake、ninja），你可以通过 apt/yum、brew 或 choco 等包管理器使用 [`before-all`](https://cibuildwheel.pypa.io/en/stable/options/#before-all) 选项进行安装。

如果你的构建链接到原生库依赖，你可以在 before-all 中构建/安装该库。但是，在 Linux、Mac（以及如果你使用 [`delvewheel`](https://github.com/adang1345/delvewheel) 的 Windows）上，你安装的库将在[修复步骤](https://cibuildwheel.pypa.io/en/stable/options/#repair-wheel-command)中捆绑到轮子中。因此，请务必确保

- 捆绑的库不会意外地增加最低系统要求（例如最低 macOS 版本）。
- 打包的库与你在交叉编译时构建的轮的架构相匹配

## Windows: 'ImportError: DLL load failed: The specific module could not be found'

Visual Studio 和 MSVC 将编译的二进制轮文件链接到 Microsoft Visual C++ 运行库。通常情况下，Python 会包含运行库的 C 部分，但 C++ 组件不会。在用 C++ 编译模块时，如果系统没有安装完整的运行库，用户可能会遇到问题。解决方法是要求用户从[微软网站](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)下载相应的 Visual C++ 运行库并安装它。

此外，Visual Studio 2019 除了链接到最近 Python 版本（从 Python 3.5 开始；[更多](https://wiki.python.org/moin/WindowsCompilers)关于用于编译不同 Python 版本的相应 Visual Studio & MSVC 版本的信息请参考此处）包含的 VCRUNTIME140.dll 之外，还链接到了一个更新的 DLL，即 `VCRUNTIME140_1.dll`。为了避免对 `VCRUNTIME140_1.dll` 的额外依赖，可以在 MSVC 调用中添加 [`/d2FH4-` 标志](https://devblogs.microsoft.com/cppblog/making-cpp-exception-handling-smaller-x64/)（详情和参考请查看[此问题](https://github.com/pypa/cibuildwheel/issues/423)）。CPython 3.8.3 及所有后续版本都包含这个额外的 DLL，因此它仅在 3.8 及更早版本中需要。

要用 setuptools 为标准 setup.py 添加 `/d2FH4-` 标志，可以使用 `extra_compile_args` 选项：
```python
   ext_modules=[
        Extension(
            'c_module',
            sources=['extension.c'],
            extra_compile_args=['/d2FH4-'] if sys.platform == 'win32' else []
        )
    ],
```

要调查 C 扩展（即伪装成 DLL 的 `.pyd` 文件）在 Windows 上的依赖关系，[Dependency Walker](http://www.dependencywalker.com/) 是很好的工具。对于诊断失败的导入，[dlltracer](https://pypi.org/project/dlltracer/) 工具也可能提供更多详细信息。