# Conan 简介

```{admonition} Conan 是通用且可移植的。
它适用于所有操作系统，包括 Windows、Linux、OSX、FreeBSD 等，并且可以定位任何平台，包括桌面、服务器以及针对移动设备（Android 和 iOS）的交叉编译，以及嵌入式和裸机设备。它与 Docker、MinGW、WSL 等其他工具以及 CMake、MSBuild、Makefiles、Meson、SCons 等所有构建系统集成。它甚至可以与任何专有构建系统集成。
```

```{admonition} Conan 是开源的，完全免费。
它与 JFrog Artifactory 有原生集成，包括免费的 Conan 版 Artifactory 社区版，使开发人员能够在自己的服务器上托管自己的私有包。Conan 由一个完整的全职维护团队开发，他们支持从小型企业到大型企业的数千名用户，以及一个活跃且优秀的社区。
```

```{admonition} Conan 可以管理任意数量的不同二进制文件。
不仅是不同的二进制文件，还包括不同的构建配置，包括不同的架构、编译器、编译器版本、运行时、C++ 标准库等。当某个配置下没有可用的二进制文件时，可以根据需要从源代码构建。Conan 可以使用相同的命令和流程在每个平台上创建、上传和下载二进制文件，从而节省开发和持续集成的大量时间。
```

安装见：[Conan 安装](https://conan.io/downloads)

推荐使用 pip
```bash
pip install conan
```

更多信息见：[为什么在您的 C++ 工作流中采用 Conan](https://conan.org.cn/why-conan)。
