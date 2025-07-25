# 依赖同一 tool-require 的不同版本

```{note}
这是高级用例。在绝大多数情况下都不需要这样做。
```

在一般情况下，尝试做类似这样的事情：

```python
def build_requirements(self):
    self.tool_requires("gcc/1.0")
    self.tool_requires("gcc/2.0")
```

将会生成“冲突”，显示错误信息如 Duplicated requirement 。在大多数情况下这是正确的，当明显无法使用同一编译器的两个版本来构建当前包时。

然而，在某些情况下，可能需要类似的功能。让我们重现这个潜在的场景。首先，请克隆源代码以重现这个项目。你可以在 GitHub 的 examples2 仓库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/graph/tool_requires/different_versions
```

在那里有 `gcc` 的假配方，包含：

```python
class Pkg(ConanFile):
    name = "gcc"

    def package(self):
        echo = f"@echo off\necho MYGCC={self.version}!!"
        save(self, os.path.join(self.package_folder, "bin", f"mygcc{self.version}.bat"), echo)
        save(self, os.path.join(self.package_folder, "bin", f"mygcc{self.version}.sh"), echo)
        os.chmod(os.path.join(self.package_folder, "bin", f"mygcc{self.version}.sh"), 0o777)
```

这不是真正的编译器，它通过 shell 或 bat 脚本来模拟编译器，执行时会打印 `MYGCC=current-version` 。注意二进制文件本身叫做 `mygcc1.0` 和 `mygcc2.0` ，也就是说，它将版本号包含在可执行文件名中。

可以为 `gcc/1.0` 和 `gcc/2.0` 创建两个不同版本，使用：
```bash
$ conan create gcc --version=1.0
$ conan create gcc --version=2.0
```

现在，在 `wine` 文件夹中有 `conanfile.py` 如下：

```python
class Pkg(ConanFile):
    name = "wine"
    version = "1.0"

    def build_requirements(self):
        # If we specify "run=False" they no longer conflict
        self.tool_requires("gcc/1.0", run=False)
        self.tool_requires("gcc/2.0", run=False)

    def generate(self):
        # It is possible to individually reference each one
        gcc1 = self.dependencies.build["gcc/1.0"]
        assert gcc1.ref.version == "1.0"
        gcc2 = self.dependencies.build["gcc/2.0"]
        assert gcc2.ref.version == "2.0"

    def build(self):
        ext = "bat" if platform.system() == "Windows" else "sh"
        self.run(f"mygcc1.0.{ext}")
        self.run(f"mygcc2.0.{ext}")
```

第一个重要点是 `build_requirements()` 方法，它对两个版本都执行 t`ool_requires()` ，但定义了 `run=False` 。这非常重要：告诉 Conan 实际上不需要从这些包中运行任何内容。由于 `tool_requires` 是不可见的，它们不定义头文件或库，因此没有任何内容可以让 Conan 识别这两个 `tool_requires` 为冲突。因此，依赖图可以无错误地构建，并且 `wine/1.0` 包将包含两个不同的 `tool-require`，分别对应 `gcc/1.0` 和 `gcc/2.0` 。

当然，并非不会从这些 `tool_requires` 中运行任何内容，但现在 Conan 并不知道这一点，管理这些内容完全是用户的责任。

```{warning}
使用 `run=False` 会使 `tool_requires()` 完全不可见，这意味着 `[tool_requires]` 配置文件无法覆盖其版本，但它会创建额外的 `tool-require` 依赖，依赖版本来自配置文件。你可能需要使用类似 `!wine/*: gcc/3.0` 的方式来排除特定包。
```

该配方仍然可以通过在 `generate()` 方法中提供完整引用，如 `self.dependencies.build["gcc/1.0"]` ，来访问每个不同的 `tool_require` 版本。

最后，最重要的是，这些工具的使用完全由用户负责。由于 `VirtualBuildEnv` 生成器默认更新 PATH 环境变量，因此包含可执行文件的 `tool_requires` 的 `bin` 文件夹将出现在路径中。在这种情况下，可执行文件是不同的，如 `mygcc1.0.sh 和 `mygcc2.0.sh` ，所以这不是问题，每个可执行文件都将在其包内被找到。

但如果可执行文件与 `gcc.exe` 完全相同，那么就需要通过类似 `self.dependencies.build["gcc/1.0"].cpp_info.bindir` 的方式获取完整文件夹（通常在 `generate()` 方法中），并使用完整路径来消除歧义。

看看它是如何工作的。如果执行：

```bash
$ conan create wine
...
wine/1.0: RUN: mygcc1.0.bat
MYGCC=1.0!!

wine/1.0: RUN: mygcc2.0.bat
MYGCC=2.0!!
```
