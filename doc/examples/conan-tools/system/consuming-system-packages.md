# 仅在使用构建包时消耗系统需求 

在某些情况下，您可能希望仅在使用构建包时消耗系统需求，而不是在安装时。当您希望在 CI/CD 管道中构建包，但在不同环境中安装 Conan 包时不希望运行系统包管理器时，这会很有用。对于这些情况，有几种方法可以实现这一目标。

## 将系统包作为构建需求消耗 Conan 包包装器 

在这种方法中，您可以使用用于[包装系统包](https://docs.conan.io/2/examples/tools/system/system_package/package_manager.html#examples-tools-system-package-manager)的 Conan 包。然后，该包可以通过 [`build_requirements()`](https://docs.conan.io/2/reference/conanfile/methods/build_requirements.html#reference-conanfile-methods-build-requirements) 方法常规地被消耗。

```python
from conan import ConanFile

class MyPackage(ConanFile):
    name = "mypackage"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.tool_requires("ncurses/system")

    ...
```

这确保了包 `mypackage` 的下游消费者不会直接调用系统包管理器（例如 `apt-get`）。只有系统 `wrap` 包的直接消费者 `ncurses` 在构建包时才会执行系统包管理器。

将 `ncurses` 集中并封装在独立的配方中，可以使其在多个场景中复用，并且避免代码重复是一种良好的实践。

## 在 `build()` 方法中直接消费系统包 

如果只想在构建包时运行系统包管理器，但没有用于封装系统库信息的 Conan 包，可以在 `build()` 方法中运行系统包管理器：

```python
from conan import ConanFile
from conan.tools.system import package_manager

class MyPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    ...

    def build(self):
        if self.settings.os == "Linux":
            apt = package_manager.Apt(self)
            apt.install(["libncurses-dev"], update=True, check=True)
```

这样，系统包管理器仅在构建包时被调用，而不是在安装时。其优点是不需要创建单独的 Conan 包来封装系统库信息，这是更简单的情况，只需要单个 recipe 来安装系统包。

然而，如果多个 recipe 使用相同的系统包，这种方法可能会导致代码重复。建议谨慎使用此方法，仅在情况明确且独立时使用。
