# 创建包

本节将介绍如何使用 Conan recipe 创建 Conan 包。首先创建基本的 Conan recipe，用于打包简单的 C/C++ 库，你可以使用 `conan new` 命令来构建它的框架。然后，将解释你可以在 Conan recipe 中定义的各种方法以及它们的功能。

- 使用 `source()` 方法从外部仓库获取源码并应用补丁。
- 在 `requirements()` 方法中为 Conan 包添加依赖项。
- 使用 `generate()` 方法准备包的构建，并自定义工具链。
- 在 `configure()` 和 `config_options()` 方法中配置设置和选项，以及它们如何影响包的二进制兼容性。
- 使用 `build()` 方法自定义构建过程并运行你正在打包的库的测试。
- 使用 `package()` 方法选择哪些文件将包含在 Conan 包中。
- 在 `package_info()` 方法中定义包的信息，以便包的使用者可以使用它。
- 使用 `test_package()` 来测试 Conan 包是否可以正确使用。

在介绍了 Conan recipe 的一些方法之后，将解释不同类型 Conan 包的一些特殊性，例如，仅头文件库、预构建二进制包、用于构建其他包的工具包或打包你自己的应用程序。

```{toctree}
create-your-first-package
handle-sources-in-packages
add-dependencies-to-packages
preparing-the-build
configure-options-settings
build-packages
package-method
define-package-information
test-conan-packages
```

