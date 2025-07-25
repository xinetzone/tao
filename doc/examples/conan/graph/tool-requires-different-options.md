# 依赖相同版本的 `tool-require` 但使用不同选项 

```{note}
这是高级用例。在绝大多数情况下都不需要这样做。
```

在一般情况下，尝试做类似这样的事情：

```python
def build_requirements(self):
    self.tool_requires("gcc/1.0")
    self.tool_requires("gcc/1.0")
```

将生成一个“冲突”，显示类似 `Duplicated requirement` 的错误。

然而，有一些特殊情况我们需要依赖相同的 `tool-require` 版本，但使用该 `tool-require` 的不同二进制文件。这可以通过向这些 `tool-require` 传递不同的 options 来实现。请首先克隆源代码以重新创建此项目。您可以在 GitHub 上的 examples2 仓库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/graph/tool_requires/different_options
```

在那里有 gcc 的假配方，包含：

```{code-block} python
class Pkg(ConanFile):
    name = "gcc"
    version = "1.0"
    options = {"myoption": [1, 2]}

    def package(self):
        # This fake compiler will print something different based on the option
        echo = f"@echo off\necho MYGCC={self.options.myoption}!!"
        save(self, os.path.join(self.package_folder, "bin", f"mygcc{self.options.myoption}.bat"), echo)
        save(self, os.path.join(self.package_folder, "bin", f"mygcc{self.options.myoption}.sh"), echo)
        os.chmod(os.path.join(self.package_folder, "bin", f"mygcc{self.options.myoption}.sh"), 0o777)
```

这不是实际的编译器，它通过 shell 或 bat 脚本来模拟编译器，当执行时会打印 `MYGCC=current-option` 。注意，该二进制文件本身被称为 mygcc1 和 mygcc2 ，也就是说，选项包含在可执行文件名中。

可以为 `gcc/1.0` 创建 `2` 个不同的二进制文件，具体方法如下：
```bash
$ conan create gcc -o myoption=1
$ conan create gcc -o myoption=2
```

现在，在 `wine` 文件夹中有 `conanfile.py` 如下：

```python
class Pkg(ConanFile):
    name = "wine"
    version = "1.0"

    def build_requirements(self):
        self.tool_requires("gcc/1.0", run=False, options={"myoption": 1})
        self.tool_requires("gcc/1.0", run=False, options={"myoption": 2})

    def generate(self):
        gcc1 = self.dependencies.build.get("gcc", options={"myoption": 1})
        assert gcc1.options.myoption == "1"
        gcc2 = self.dependencies.build.get("gcc", options={"myoption": 2})
        assert gcc2.options.myoption == "2"

    def build(self):
        ext = "bat" if platform.system() == "Windows" else "sh"
        self.run(f"mygcc1.{ext}")
        self.run(f"mygcc2.{ext}")
```

第一个重要点是 `build_requirements()` 方法，它对两个二进制文件都执行 `tool_requires()` ，但定义了 `run=False` 和 `options={"myoption": value}` 特性。这一点非常重要：在告诉 Conan 实际上不需要从这些包中运行任何内容。由于 `tool_requires` 是不可见的，它们不定义头文件或库，并且定义了不同的 `options` ，因此没有任何内容能让 Conan 识别这两个 `tool_requires` 为冲突。因此，依赖图可以无错误地构建，而 `wine/1.0` 包将包含两个不同的 `tool-require`，分别用于 `gcc/1.0` 使用 `myoption=1` 和 `myoption=2` 。

当然，并非不会从这些 `tool_requires` 中运行任何内容，但现在 Conan 并不知道这一点，管理这些内容完全是用户的责任。

```{warning}
使用 `run=False` 会使 `tool_requires()` 完全不可见，这意味着 `[tool_requires]` 配置文件无法覆盖其版本，但它会创建额外的 `tool-require` 依赖，依赖版本来自配置文件。你可能需要使用类似 `!wine/*: gcc/3.0` 的方式来排除特定包。
```

该配方仍然可以通过在 `generate()` 方法中提供依赖所需的选项值，来访问每个不同的 `tool_require` 版本。

最后，最重要的是，这些工具的使用完全由用户负责。由于 `VirtualBuildEnv` 生成器默认更新 `PATH` 环境变量，因此包含可执行文件的 `tool_requires` 的 `bin` 文件夹将出现在路径中。在这种情况下，可执行文件是不同的，如 `mygcc1.sh` 和 `mygcc2.sh` ，所以这不是问题，每个可执行文件都将在其包内被找到。

但如果可执行文件与 `gcc.exe` 完全相同，那么就需要通过类似 `self.dependencies.build.get("gcc", options={"myoption": 1}).cpp_info.bindir` 的方式获取完整文件夹（通常在 `generate()` 方法中），并使用完整路径来消除歧义。

看看它是如何工作的。如果执行：
```bash
$ conan create wine
...
wine/1.0: RUN: mygcc1.bat
MYGCC=1!!

wine/1.0: RUN: mygcc2.bat
MYGCC=2!!
```
