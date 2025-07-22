# Conan 简介

```{admonition} Conan 是通用且可移植的。
它适用于所有操作系统，包括 Windows、Linux、OSX、FreeBSD 等，并且可以定位任何平台，包括桌面、服务器以及针对移动设备（Android 和 iOS）的交叉编译，以及嵌入式和裸机设备。它与 Docker、MinGW、WSL 等其他工具以及 CMake、MSBuild、Makefiles、Meson、SCons 等所有构建系统集成。它甚至可以与任何专有构建系统集成。
```

```{admonition} Conan 是开源的，完全免费。
它与 JFrog Artifactory 有原生集成，包括免费的 [Conan 版 Artifactory 社区版](https://conan.io/downloads.html)，使开发人员能够在自己的服务器上托管自己的私有包。Conan 由完整的全职维护团队开发，他们支持从小型企业到大型企业的数千名用户，以及活跃且优秀的社区。
```

```{admonition} Conan 可以管理任意数量的不同二进制文件。
不仅是不同的二进制文件，还包括不同的构建配置，包括不同的架构、编译器、编译器版本、运行时、C++ 标准库等。当某个配置下没有可用的二进制文件时，可以根据需要从源代码构建。Conan 可以使用相同的命令和流程在每个平台上创建、上传和下载二进制文件，从而节省开发和持续集成的大量时间。
```

## 安装

安装见：[Conan 安装](https://conan.io/downloads)

推荐使用 `pip`
```bash
pip install conan
```

更多信息见：[为什么在您的 C++ 工作流中采用 Conan](https://conan.org.cn/why-conan)。

## 去中心化包管理器

Conan 是具有客户端-服务器架构的去中心化包管理器。这意味着客户端可以从不同的服务器（“远程”）获取包，也可以向这些服务器上传包，类似于与 git 远程仓库的 push-pull 模型。

从宏观上看，服务器只是存储软件包，它们不构建也不创建软件包。软件包是由客户端创建的，如果从源代码构建二进制文件，那么编译工作也是由客户端应用程序完成的。

- Conan 客户端：这是一个控制台/终端命令行应用程序，包含包创建和消费的重逻辑。Conan 客户端具有本地缓存用于存储包，因此它允许您离线完全创建和测试包。只要不需要从远程服务器获取新包，您也可以离线工作。
- [JFrog Artifactory Community Edition (CE)](https://conan.io/downloads.html) 是推荐的 Conan 服务器，用于在您控制下私下托管自己的私有包。它是 JFrog Artifactory 的免费社区版，适用于 Conan 包，包括 WebUI、多种认证协议（LDAP）、虚拟和远程仓库以创建高级拓扑结构、Rest API 以及通用仓库以托管任何工件。
- conan_server 是与 Conan 客户端一同分发的轻量级服务器。它是简单的开源实现，提供基本功能，但没有 WebUI 或其他高级特性。
- [ConanCenter](https://conan.io/center) 是中央公共仓库，社区为流行的开源库（如 Boost、Zlib、OpenSSL、Poco 等）贡献软件包。

## 二进制管理

Conan 最强大的功能之一是它能够为任何可能的平台和配置创建和管理预编译二进制文件。通过使用预编译二进制文件并避免从源代码重复构建，它为开发者和持续集成服务器节省了大量时间，同时也提高了工件的可重复性和可追溯性。

软件包由“conanfile.py”定义。这是定义软件包依赖项、源代码、如何从源代码构建二进制文件等的文件。“conanfile.py”配方可以生成任意数量的二进制文件，每个不同的平台和配置一个：操作系统、架构、编译器、构建类型等。这些二进制文件可以在所有平台上使用相同的命令创建并上传到服务器，为所有软件包提供单一的事实来源，并且不需要为每个不同的操作系统提供不同的解决方案。

从服务器安装软件包也非常高效。仅下载当前平台和配置所需的二进制文件，而不是全部。如果兼容的二进制文件不可用，客户端也可以从源代码构建软件包。

## 所有平台、所有构建系统和编译器

Conan 支持 Windows、Linux（Ubuntu、Debian、Red Hat、ArchLinux、Raspbian）、OSX、FreeBSD 和 SunOS，并且由于它具有可移植性，可能在任何可以运行 Python 的平台上都可用。它可以针对任何现有平台：从裸机到桌面、移动、嵌入式、服务器以及交叉编译。

Conan 也适用于任何构建系统。内置集成支持最流行的构建系统，如 CMake、Visual Studio（MSBuild）、Autotools 和 Makefiles、Meson、SCons 等，但使用其中任何一种并非强制要求。所有包使用相同的构建系统也并非必要：每个包可以使用自己的构建系统，并依赖于使用不同构建系统的其他包。也可以与任何构建系统集成，包括专有构建系统。

同样地，Conan 可以管理任何编译器及其任何版本。对于最流行的编译器，如 gcc、cl.exe、clang、apple-clang、intel 等，都有默认定义，包括不同版本配置、运行时、C++标准库等。该模型也可扩展到任何自定义配置。

## Conan 2 特性

### 依赖图模型

Conan 2 定义了新的需求特征（头文件、库、构建、运行、测试、包 ID 模式、选项、传递性头文件、传递性库）和包类型（静态、共享、应用程序、仅头文件），以更好地表示与 C 和 C++二进制文件（如可执行文件或共享库链接静态库或共享库）相关的关系。

### 公共 Python API

模块化 Python API 已提供，公开并文档化。这是真正的 API，其构建模块已被用于构建 Conan 内置命令，但将允许进一步扩展。有针对不同功能组的子 API，如 `api.list` 、 `api.search` 、 `api.remove` 、 `api.profile` 、 `api.graph` 、 `api.upload` 、 `api.remotes` 等，将允许实现高级用户流程、功能和自动化。

### 构建系统集成

Conan 2 使用现代构建系统集成，如 CMakeDeps 和 CMakeToolchain ，这些是完全透明的 CMake 集成（即消费端 `CMakeLists.txt` 完全不需要知道有关 Conan 的任何信息）。这些集成还可以实现更好的 IDE 集成，例如通过 `CMakePresets.json`。

### 自定义用户命令

Conan 2 允许通过 Python 编写的自定义用户命令扩展 Conan，这些命令可以作为 `conan xxxx` 调用。这些命令可以与 `conan config install` 共享和安装，并具有命令层级和子命令。自定义用户命令使用新的 2.0 公共 Python API 实现其功能。

### CLI

Conan 2 设计了 CLI，以增强一致性、消除歧义并提升用户体验。新的 CLI 还将所有信息、警告和错误消息发送到 stderr，同时将最终结果保留在 stdout，支持 `--format=html` 或 `--format=json` 等多种输出格式，并使用重定向创建文件 `--format=json > myfile.json`。CLI 提供的信息将更加结构化和全面，以便更轻松地用于自动化，特别是在 CI/CD 系统中。

### 部署器

Conan 2 实现了“部署器”，可以在命令行中调用 `conan install …. --deployer=mydeploy` ，通常用于将 Conan 缓存中的文件复制到用户文件夹。这类部署器可以是内置的（目前提供了“full_deploy”、“direct_deploy”和“runtime_deploy”），也可以是用户自定义的，这些自定义部署器可以与 conan config install 共享和管理。部署器会在生成器之前运行，并且可以更改目标文件夹。例如，如果 `--deployer=full_deploy` 部署器在 CMakeDeps 之前运行，那么 CMakeDeps 生成的文件将指向由 full_deploy 部署器在用户文件夹中完成的本地复制，而不是指向 Conan 缓存。

部署器可以是多配置的。通过针对不同配置反复运行 `conan install . --deployer=full_deploy` ，可以实现完全自包含的项目，包括所有工件、二进制文件和构建文件，该项目完全独立于 Conan，并且不再需要 Conan 来构建。

### `package_id`

Conan 2 定义了新的动态 `package_id`，它比 Conan 1.X 的限制有了很大的改进。这个 `package_id` 会考虑包类型和需求类型，根据不同场景实施更有意义的策略。例如，众所周知，当应用程序 `myapp` 链接静态库 `mylib` 时，静态库二进制文件的任何更改 `mylib` 都需要重新构建应用程序 `myapp`。因此，Conan 会默认采用类似 `full_mode` 的模式，在 `mylib` 方案或二进制文件发生任何更改时，都会生成新的 `myapp package_id`。虽然静态库 `mylib_a` 之间的依赖关系并不意味着 `mylib_b` 的更改总是需要重新构建 `mylib_a`，这种关系可以默认为 `minor_mode` 模式。在 Conan 2 中，对 `mylib_a` 进行修改的人可以更好地表达消费者 `mylib_b` 是否需要重新构建（补丁版本的更新不会触发重新构建，而次版本号的更新会触发）。

此外，Conan 中的默认版本号方案已扩展到任意数量的数字和字母，而官方的“semver”仅使用 3 个字段。

### `compatibility.py`

Conan 2 新增了一种扩展机制，用于在全局层面定义二进制兼容性。Conan 缓存中的 `compatibility.py` 文件将用于定义在给定包缺少某些二进制文件时应该使用哪些回退方案。Conan 会提供默认方案来处理 cppstd 兼容性和可执行文件兼容性，但这个扩展完全由用户配置（并且还可以与 `conan config install` 共享和管理）。

### 锁定文件

Conan 2 中的锁文件已被大大简化并变得更加灵活。锁文件现在被建模为排序参考的列表，这允许单个锁文件用于多个配置、合并锁文件、应用部分定义的锁文件、严格或非严格、向锁文件添加用户定义的约束，等等。

### 配置和环境管理

在配置文件和命令行中被称为 `[conf]` 的新配置系统，在 Conan 1.X 中实验性引入，现已成为配置和控制 Conan 行为的主要机制。其理念是利用配置系统将信息从 Conan（Conan 配置文件）传输到 Conan（Conan 配置文件，或像 CMakeToolchain 这样的 Conan 构建系统集成）。这个新的配置系统可以定义字符串、布尔值、列表，比环境变量更清晰、结构化且功能更强大。在 Conan 1.X 中引入的更优、更明确的环境管理方式，现已成为从 Conan（配置文件）向工具（如编译器、构建系统）传递信息的方法。详细内容：[env](https://docs.conan.io/2/reference/tools/env.html#reference-tools-env)

### 多版本缓存

Conan 缓存已被完全重新设计，以支持同时存储多个版本。它还缩短了路径，使用哈希值，从而无需在 Windows 中使用 `short_paths`。请注意，缓存仍然不是并发执行的，因此并行任务或作业应使用独立的缓存。

### 扩展插件

已添加几个名为“plugins”的插件点，以提供比 Conan 配方实现的高级且通常正交的功能。这些插件可以通过 `conan config install` 进行共享、管理和安装。

#### 配置检查器

提供了新的 `profile.py` 插件点，可以在配置处理完成后执行操作。提供了一默认实现，用于检查所提供的编译器版本是否能够支持指定的编译器 `cppstd`，但用户可以完全自定义此功能。

#### 命令包装器

的 `cmd_wrapper.py` 插件提供了一个方法，可以将任何 · 命令（即在任何食谱中运行在 · 内的任何内容）包装在一个新命令中。这项功能对于在 · 或编译缓存等构建优化工具中包装构建命令非常有用

#### 包签名

新的 `sign.py` 插件已被添加，用于实现软件包的签名和验证。随着人们越来越意识到软件供应链安全的重要性，签名和验证软件包的能力变得愈发关键。这个扩展点将很快基于 Sigstore 获得插件实现。

### 软件包不可变性优化

Conan 2 中对 `revisions` 的全面使用（已在 Conan 1.X 中作为可选功能引入 https://docs.conan.io/en/latest/versioning/revisions.html），结合对工件不可变性的声明，能够改进下载、安装、更新和上传依赖项的过程。

`Revisions` 允许精确追踪工件，从而实现更好的更新流程。例如，只要它们来自相同的配方修订版本，从不同的存储库获取针对不同配置的不同二进制文件将更加容易。

基于 `revisions`，软件包的传输、上传和下载也将更加高效。只要指定的版本存在于服务器或缓存中，Conan 就不会为该软件包传输任何工件。

### 包清单

Conan 2 允许通过“包清单”（Package lists）功能对多个配方和包进行批量操作。该功能允许用户使用单个命令上传、下载、删除和列出多个配方和包。

包清单也可以从由 `conan create` 或 `conan install` 命令生成的依赖图创建，因此只需串联两个命令，就可以将属于给定依赖图的全部包上传到服务器。

### 元数据文件

Conan 2 允许存储、上传、下载和修改与配方和包关联的[元数据文件](https://blog.conan.io/2023/10/24/Conan-launches-metadata-files.html)。此功能对于管理构建日志、测试可执行文件、测试结果、覆盖率数据以及各种其他用于可追溯性、合规性和商业目的的文件非常有用。

### 第三方备份源

当为第三方构建具有互联网来源的软件包时，这些来源可能会被删除或更改。[“备份源码”](https://blog.conan.io/2023/10/03/backup-sources-feature.html)可以自动将那些来源的副本存储在您自己的服务器上，因此您的构建始终可以完全重现，无论原始互联网来源发生什么情况。

### 从 Conan 包中安装配置

从 Conan 2.2 版本开始，不仅可以从 git 仓库和 http 服务器安装配置，还可以[从 Conan 包中安装](https://docs.conan.io/2/reference/commands/config.html#reference-commands-conan-config-install-pkg)。对于存储在 Conan 服务器上的 Conan 包 myconf/myversion ，运行 `conan config install-pkg myconf/myversion` 将会安装该包内的配置文件。它还允许使用版本范围轻松更新到范围内的最新版本，并使用锁文件实现可重复性。
