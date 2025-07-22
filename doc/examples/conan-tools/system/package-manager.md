# 将系统需求封装在 Conan 包中 

Conan 可以管理系统包，让你轻松安装平台特定的依赖。当你需要安装平台特定的系统包时，这非常有用。例如，你可能需要安装提供特定驱动程序或图形库的包，而这些驱动程序或库只在特定平台上有效。

Conan 提供了一种使用[系统包管理工具安装系统包](https://docs.conan.io/2/reference/tools/system/package_manager.html#conan-tools-system-package-manager)的方法。

在这个示例中，将探讨创建围绕系统库的包装包所需的步骤，以及如何在 Conan 包中消费它。请注意，该包不包含二进制工件，它只是通过调用 `system_requirements()` 和相应的系统包管理器（例如 Apt、Yum）来管理检查/安装它们。在这个示例中，将创建 Conan 包来封装系统 [ncurses](https://invisible-island.net/ncurses/) 需求，然后展示如何在应用程序中使用这个需求。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/tools/system/package_manager/
```

你会找到以下树状结构：

```bash
.
├── conanfile.py
└── consumer
    ├── CMakeLists.txt
    ├── conanfile.py
    └── ncurses_version.c
```

`conanfile.py` 文件是封装 `ncurses` 系统库的配方。最后，消费者目录包含使用 `ncurses` 库的简单 C 应用程序，稍后会查看它。

在封装预构建的系统库时，不需要从源代码构建项目，只需安装系统库并打包其信息。在这种情况下，将首先检查封装 `ncurses` 库的 `conanfile.py` 文件：
```{code-block} python
:caption: conanfile.py

from conan import ConanFile
from conan.tools.system import package_manager
from conan.tools.gnu import PkgConfig
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.0"


class SysNcursesConan(ConanFile):
    name = "ncurses"
    version = "system"
    description = "A textual user interfaces that work across a wide variety of terminals"
    topics = ("curses", "terminal", "toolkit")
    homepage = "https://invisible-mirror.net/archives/ncurses/"
    license = "MIT"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def package_id(self):
        self.info.clear()

    def validate(self):
        supported_os = ["Linux", "Macos", "FreeBSD"]
        if self.settings.os not in supported_os:
            raise ConanInvalidConfiguration(f"{self.ref} wraps a system package only supported by {supported_os}.")

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["ncurses-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["ncurses-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libncurses-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["ncurses"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["ncurses"], update=True, check=True)

        brew = package_manager.Brew(self)
        brew.install(["ncurses"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["ncurses"], update=True, check=True)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "Curses")
        self.cpp_info.set_property("cmake_target_name", "Curses::Curses")
        self.cpp_info.set_property("cmake_additional_variables_prefixes", ["CURSES",])

        pkg_config = PkgConfig(self, 'ncurses')
        pkg_config.fill_cpp_info(self.cpp_info, is_system=True)
```

在这个 `conanfile.py` 文件中，使用[系统包管理工具](https://docs.conan.io/2/reference/tools/system/package_manager.html#conan-tools-system-package-manager)根据不同的包管理器安装 `ncurses` 库，这是在 `system_requirements` 方法中实现的。需要注意的是，[`system_requirements`](https://docs.conan.io/2/reference/conanfile/methods/system_requirements.html#reference-conanfile-methods-system-requirements) 方法在构建时始终被调用，即使包已经安装也是如此。这有助于确保包在系统中被安装。

每个包管理器可能使用不同的包名来安装 `ncurses` 库，因此我们需要先查阅包管理器的文档以找到正确的包名。

另一个重要的细节是 `package_info` 方法。在这个方法中，使用 [`PkgConfig`](https://docs.conan.io/2/reference/tools/gnu/pkgconfig.html#conan-tools-gnu-pkgconfig) 工具根据系统包管理器安装的文件 `ncurses.pc` 来填充 `cpp_info` 数据。

现在，使用 `conanfile.py` 文件来安装 `ncurses` 库：
```bash
conan create . --build=missing -c tools.system.package_manager:mode=install -c tools.system.package_manager:sudo=true
```

请注意，使用 [Conan 配置](https://docs.conan.io/2/reference/tools/system/package_manager.html#conan-tools-system-package-manager-config) `tools.system.package_manager:mode` 作为安装，否则 Conan 不会安装系统包，而只是检查是否已安装。同样，使用 `tools.system.package_manager:sudo` 作为 `True` 以 root 权限运行包管理器。执行此命令后，您应该能够在系统中看到 `ncurses` 库已安装，如果尚未安装的话。

现在，检查消费者目录。这个目录包含使用 `ncurses` 库的简单 C 应用程序。

消费者目录中的 `conanfile.py` 文件是：

```python
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class AppNCursesVersionConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    package_type = "application"
    exports_sources = "CMakeLists.txt", "ncurses_version.c"

    def requirements(self):
        if self.settings.os in ["Linux", "Macos", "FreeBSD"]:
            self.requires("ncurses/system")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        app_path = os.path.join(self.build_folder, "ncurses_version")
        self.output.info(f"The example application has been successfully built.\nPlease run the executable using: '{app_path}'")
```

这个配方很简单。它需要刚刚创建的 `ncurses` 包，并使用 CMake 工具来构建应用程序。一旦应用程序构建完成，它会显示 `ncurses_version` 应用程序路径，这样你就可以按需手动运行它并检查其输出。

`ncurses_version.c` 文件是简单的 C 应用程序，它使用 `ncurses` 库来打印 `ncurses` 版本，但使用白色背景和蓝色文本：
```c
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <ncurses.h>


int main(void) {
    int max_y, max_x;
    char message [256] = {0};

    initscr();

    start_color();
    init_pair(1, COLOR_BLUE, COLOR_WHITE);
    getmaxyx(stdscr, max_y, max_x);

    snprintf(message, sizeof(message), "Conan 2.x Examples - Installed ncurses version: %s\n", curses_version());
    attron(COLOR_PAIR(1));
    mvprintw(max_y / 2, max_x / 2 - (strlen(message) / 2), "%s", message);
    attroff(COLOR_PAIR(1));

    refresh();

    return EXIT_SUCCESS;
}
```

`CMakeLists.txt` 文件是简单的 CMake 文件，用于构建 `ncurses_version` 应用程序：
```cmake
cmake_minimum_required(VERSION 3.15)
project(ncurses_version C)

find_package(Curses CONFIG REQUIRED)

add_executable(${PROJECT_NAME} ncurses_version.c)
target_link_libraries(${PROJECT_NAME} PRIVATE Curses::Curses)
```

CMake 目标 `Curses::Curses` 由刚刚创建的 `ncurses` 包提供。它遵循官方的 [`FindCurses`](https://cmake.org/cmake/help/latest/module/FindCurses.html) CMake 模块。关于库和包含目录的信息现在可以在 `cpp_info` 对象中找到，因为使用 `PkgConfig` 工具填充了它。

现在，构建应用程序：

```bash
$ cd consumer/
$ conan build . --name=ncurses-version --version=0.1.0
  ...
  conanfile.py (ncurses-version/0.1.0): The example application has been successfully built.
  Please run the executable using: '/tmp/consumer/build/Release/ncurses_version'
```

构建应用程序后，它会显示可执行路径。您可以运行它来检查输出：

```bash
$ /tmp/consumer/build/Release/ncurses_version

Conan 2.x Examples - Installed ncurses version: ncurses 6.0.20160213
```

如果显示的版本与这里所示的不同，或者可执行路径不同，请不用担心。这取决于您系统中安装的版本以及您构建应用程序的位置。

搞定！你已经成功地将系统库打包，并在 Conan 包中使用了它。
