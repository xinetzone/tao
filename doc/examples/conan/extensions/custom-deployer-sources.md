# 从所有依赖项复制源代码

请首先克隆源代码以重新创建此项目。你可以在 GitHub 的 examples2 仓库中找到它们：
```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/extensions/deployers/sources
```
在这个示例中，将看到如何创建和使用自定义的部署器。这个部署器会从你的依赖项中复制所有源文件，并将它们放到特定的输出文件夹中

```{note}
为了更好地理解这个示例，强烈建议你之前阅读过[部署器参考](https://docs.conan.io/2/reference/extensions/deployers.html#reference-extensions-deployer-direct-deploy)。
```

## 定位部署器

在这种情况下，部署者位于我们示例 conanfile 的同一目录中，但正如 [Deployers](https://docs.conan.io/2/reference/extensions/deployers.html#reference-extensions-deployer-direct-deploy) 参考中所示，Conan 将按顺序在几个额外位置查找指定的部署者，具体如下：

- 绝对路径
- 相对于当前工作目录的相对路径
- 在 `[CONAN_HOME]/extensions/deployers` 文件夹中
- 内置部署器

## 运行它

在我们的示例中，我们有一个简单的配方，它将 `zlib` 和 `mcap` 都列为主要依赖项。借助 `tools.build:download_source=True` 配置文件，我们可以强制调用它的 `source()` 方法，这将确保即使不需要执行构建，源代码也会可用。

现在，您应该能够在 `conan install` 和 `conan graph` 命令中为任何给定的配方使用新的部署器：
```bash
$ conan graph info . -c tools.build:download_source=True --deployer=sources_deploy
```

通过检查命令输出，我们可以看到它将直接依赖项 `zlib` 和 `mcap` 的源代码，以及传递依赖项 `zstd` 和 `lz4` 的源代码复制到 `dependencies_sources` 文件夹中。完成这些操作后，可以进行额外的预处理以满足更具体的需求。

注意，你可以传递 `--deployer-folder` 参数来更改部署器的输出基础文件夹路径。

## 代码导览

`source_deploy.py` 文件包含以下代码：
```{code-block} python
:caption: sources_deploy.py
from conan.tools.files import copy
import os


def deploy(graph, output_folder, **kwargs):
    # Note the kwargs argument is mandatory to be robust against future changes.
    for name, dep in graph.root.conanfile.dependencies.items():
        if dep.folders is None or dep.folders.source_folder is None:
            raise ConanException(f"Sources missing for {name} dependency.\n"
                                  "This deployer needs the sources of every dependency present to work, either building from source, "
                                  "or by using the 'tools.build:download_source' conf.")
        copy(graph.root.conanfile, "*", dep.folders.source_folder, os.path.join(output_folder, "dependency_sources", str(dep)))
```

## `deploy()`

Conan 调用 `deploy()` 方法，该方法接收依赖关系图和输出文件夹路径作为参数。它遍历我们的 recipe 的所有依赖项，并使用 `conan.tools.copy` 将每个源文件复制到 `dependencies_sources` 下的相应文件夹中。

```{note}
如果你将这个部署器作为你自己的示例使用，请记住 `tools.build:download_source=True` 是必要的，以便为依赖项定义 `dep.folders.source_folder` 。没有这个配置，对于不需要从源代码构建的依赖项或不需要构建的命令（如 `conan graph`），该变量将不会被定义。
```

```{note}
如果你的自定义部署器需要访问完整的依赖关系图，包括可能被跳过的库，请使用 `tools.graph:skip_binaries=False` 配置。这适用于收集 graph 中的所有许可证，例如。
```
