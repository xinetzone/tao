# 版本控制简介

到目前为止，一直使用固定版本的 `requires`，例如 `requires = "zlib/1.2.12"`。但有时依赖项会演变，新版本发布，并且消费者希望尽可能轻松地更新到这些版本。

总是可以编辑 `conanfiles` 并显式地将版本更新到新版本，但在 Conan 中有一些机制允许在不修改 `recipe` 的情况下进行此类更新。

## 版本范围

`requires` 可以表达对给定软件包某个版本范围的依赖，语法是 `pkgname/[version-range-expression]`。

请先克隆源代码来重现此项目。您可以在 GitHub 的 examples2 仓库 中找到它们。

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/consuming_packages/versioning
```

可以看到那里有

```{code-block} python
:caption: conanfile.py

from conan import ConanFile


class CompressorRecipe(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("zlib/[~1.2]")
```

该 `requires` 包含表达式 `zlib/[~1.2]`，表示“大约” 1.2 版本。这意味着，它可以解析到任何 `zlib/1.2.8`、`zlib/1.2.11` 或 `zlib/1.2.12`，但不会解析到像 `zlib/1.3.0` 这样的版本。在所有匹配的版本中，版本范围将始终选择最新的一个。

如果执行 `conan install`，会看到类似以下内容

```bash
$ conan install .

Graph root
    conanfile.py: .../conanfile.py
Requirements
    zlib/1.2.12#87a7211557b6690ef5bf7fc599dd8349 - Downloaded
Resolved version ranges
    zlib/[~1.2]: zlib/1.2.12
```

如果改为尝试使用 `zlib/[<1.2.12]`，这意味着我们希望使用低于 `1.2.12` 的版本，但该版本被排除在外，因此满足该范围的最新版本将是 `zlib/1.2.11`

```bash
$ conan install .

Resolved version ranges
    zlib/[<1.2.12]: zlib/1.2.11
```

这同样适用于其他类型的 requirements，例如 `tool_requires`。让我们向 recipe 中添加

```{code-block} python
:caption: conanfile.py

from conan import ConanFile


class CompressorRecipe(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("zlib/[~1.2]")

    def build_requirements(self):
        self.tool_requires("cmake/[>3.10]")
```

看到它解析到最新的可用 CMake 软件包，版本至少为 `3.11`

```bash
$ conan install .
...
Graph root
    conanfile.py: .../conanfile.py
Requirements
    zlib/1.2.12#87a7211557b6690ef5bf7fc599dd8349 - Cache
Build requirements
    cmake/3.22.6#f305019023c2db74d1001c5afa5cf362 - Downloaded
Resolved version ranges
    cmake/[>3.10]: cmake/3.22.6
    zlib/[~1.2]: zlib/1.2.12
```

## 修订版本 (Revisions)

当软件包创建者对软件包 `recipe` 或源代码进行更改，但没有更新 `version` 来反映这些更改时，会发生什么？Conan 有内部机制来跟踪这些修改，称为 `revisions`。

`recipe revision` 是与软件包名称和版本一起显示的哈希值，形式为 `pkgname/version#recipe_revision` 或 `pkgname/version@user/channel#recipe_revision`。`recipe revision` 是 `recipe` 内容和源代码的哈希值。因此，如果 `recipe`、其关联文件或此 `recipe` 打包的源代码中发生任何更改，都会创建新的 `recipe revision`。

您可以使用 `conan list` 命令列出现有的 `revisions`

```bash
$ conan list "zlib/1.2.12#*" -r=conancenter
conancenter
  zlib
    zlib/1.2.12
      revisions
        82202701ea360c0863f1db5008067122 (2022-03-29 15:47:45 UTC)
        bd533fb124387a214816ab72c8d1df28 (2022-05-09 06:59:58 UTC)
        3b9e037ae1c615d045a06c67d88491ae (2022-05-13 13:55:39 UTC)
        ...
```

Revisions 总是解析到最新的（按创建或上传到服务器的时间顺序）revision。虽然这不是常见的做法，但可以在 conanfile 中直接显式固定某个 recipe revision，如下所示

```python
def requirements(self):
    self.requires("zlib/1.2.12#87a7211557b6690ef5bf7fc599dd8349")
```

然而，当创建新的 revisions 时，这种机制的维护和更新可能会很繁琐，所以在一般情况下，不应该这样做。

## Lockfiles

使用版本范围，以及在不更新版本的情况下创建给定软件包新 `revision` 的可能性，可以实现快速、自动和便捷的更新，而无需编辑 recipes。

但在某些情况下，还需要提供一组不可变且可重现的依赖项。此过程称为“锁定 (locking)”，允许此操作的机制是“lockfile”文件。Lockfile 是一个文件，其中包含固定的依赖项列表，指定了确切的版本和确切的 `revision`。因此，例如，`lockfile` 永远不会包含带有表达式的版本范围，而只包含固定的依赖项。

Lockfile 可以看作是给定依赖图在某个时间点的快照。这样的快照必须是“可实现的”，也就是说，它需要是一个可以从 `conanfile recipe` 实际重现的状态。并且可以在稍后的时间点使用此 lockfile 来强制执行相同的状态，即使创建了新的软件包版本。

让我们看看 lockfiles 的实际应用。首先，在我们的示例中将依赖项固定到 `zlib/1.2.11`

```bash
def requirements(self):
    self.requires("zlib/1.2.11")
```

然后，捕获 `lockfile`

```bash
conan lock create .

-------- Computing dependency graph ----------
Graph root
    conanfile.py: .../conanfile.py
Requirements
    zlib/1.2.11#4524fcdd41f33e8df88ece6e755a5dcc - Cache

Generated lockfile: .../conan.lock
```

看看 lockfile conan.lock 包含什么

```json
{
    "version": "0.5",
    "requires": [
        "zlib/1.2.11#4524fcdd41f33e8df88ece6e755a5dcc%1650538915.154"
    ],
    "build_requires": [],
    "python_requires": []
}
```

现在，恢复原始的 `requires` 版本范围

```bash
def requirements(self):
    self.requires("zlib/[~1.2]")
```

并运行 `conan install .`，它默认会查找 `conan.lock`，并运行等效的 `conan install . --lockfile=conan.lock`

```bash
conan install .

Graph root
    conanfile.py: .../conanfile.py
Requirements
    zlib/1.2.11#4524fcdd41f33e8df88ece6e755a5dcc - Cache
```

注意版本范围不再被解析，并且它没有获取 `zlib/1.2.12` 依赖项，即使它在允许的范围 `zlib/[~1.2]` 内，因为 `conan.lock lockfile` 强制它停留在 `zlib/1.2.11` 以及确切的 `revision`。
