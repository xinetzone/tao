# 使用系统提供的包管理器

使用系统提供的包是包管理解决方案中最古老和最常见的形式之一。为此，您使用系统的包安装程序（例如 apt、yum）将库和头文件安装到常见位置。然后，CMake 可以使用 find_package() 函数来搜索这些文件，并将它们提供给您的程序。

示例见：[boost unit test](../../05-unit-testing/boost/index) 和 [third-party-library](../../01-basic/H-third-party-library/index)。