# 核心指南

来源：[核心指南](https://docs.conan.io/2/knowledge/guidelines.html)

## 良好实践

- `build()` 应该简单，在 `generate()` 中准备构建：配方中的 `generate()` 方法的目的是尽可能多地准备构建。调用 `conan install` 的用户将执行此方法，生成的文件应尽可能方便用户进行“本地”构建（直接调用“cmake”、“meson”等）。因此，尽量避免在 `build()` 方法中包含任何逻辑，并将其移至 `generate()` 方法，这有助于开发者在本地实现与本地缓存中 `conan create` 构建相同的构建。
- 始终在生产环境中使用自己的配置文件，而不是依赖自动检测的配置文件，因为自动检测的输出可能会随时间变化，导致意外结果。配置文件（以及许多其他配置）可以通过 `conan config install` 进行管理。
- 开发者不应能够上传到服务器上的“开发”和“生产”仓库。只有 CI 构建在服务器上具有写入权限。开发者应仅具有读取权限，最多只能访问一些“游乐场”仓库，这些仓库用于与同事协作和共享事物，但包永远不会被使用、移动或复制到开发或生产仓库中。
- 测试包的目的是验证包的正确创建，而不是进行功能测试。`test_package` 的目的是检查包是否已正确创建（也就是说，它是否已正确地将头文件、库等打包到正确的文件夹中），而不是检查包的功能是否正确。然后，它应该尽可能简单，例如构建并运行一个使用头文件并链接到打包库的可执行文件就足够了。这种执行也应该尽可能简单。任何类型的单元测试和功能测试都应该在 `build()` 方法中完成。
- 所有输入源必须对所有二进制配置都通用：所有“源”输入，包括 `conanfile.py`、 `conandata.yml` 、 `exports` 和 `exports_source` 、 `source()` 方法、在 `source()` 方法中应用的补丁，都不能依赖于任何内容、平台、操作系统或编译器，因为它们在所有配置中共享。此外，所有这些内容的行尾应该相同，建议在所有平台上始终使用仅换行符，并且在 Windows 中不要转换或检出为 `crlf` ，否则会导致不同的配方修订。
- 保持 `python_requires` 尽可能简单。避免传递性依赖 `python_requires` ，尽量减少它们，最多在“扁平”结构中明确要求，且 `python_requires` 不需要依赖其他 `python_requires` 。如果非必要，避免使用继承（通过 `python_requires_extend` ），并且不惜一切代价避免多重继承，因为它极其复杂，且与内置的 Python 机制不同。
- 目前 Conan 缓存不是并发操作的。避免任何形式的并发或并行，例如不同的并行 CI 作业应该使用不同的缓存（通过 `CONAN_HOME` 环境变量）。这在未来可能会改变，我们将努力在缓存中提供并发操作，但在此之前，请为并发任务使用隔离的缓存。
- 避免将‘force’和‘override’特性用作版本控制机制。解决冲突的 `force` 和 `override` 特性不应作为通用的版本解决方案，而应仅作为临时解决版本冲突的变通方法。应尽可能避免使用它，推荐的方法是在图中更新版本或版本范围以避免冲突，而无需使用覆盖和强制。
- 请勿滥用‘tool_requires’。这些仅用于在“构建”上下文中运行的 cmake 和 ninja 等可执行文件，不适用于库或类似库的依赖项，后者必须使用 `requires` 或 `test_requires` 。
- 调用 Conan 时，位置参数应先于任何命名参数指定。例如， `conan install . -s="os=Windows"` 是正确的，但 `conan install -s="os=Windows" .` 是不正确的。同样，建议在命名参数的名称和值之间使用 `=` 而不是空格。这是为了避免解析命令行参数时出现一些歧义情况。
- 强烈不建议使用 `user`/`channel` 来表示任何质量、阶段、成熟度或变量信息。`channel` 部分非常过时，在大多数情况下应避免使用，或者使用固定的字符串作为 `stable` 。`user` 可能用于组织内部的私有包，而来自 ConanCenter 或 `conan-center-index` Github 仓库分支的包则建议不使用任何用户或频道，就像 `zlib/1.3.1` ConanCenter 的引用一样，即使是对这些第三方库的配方和包进行定制也是如此。
- 管理包质量、阶段或成熟度提升的方式是使用不同的服务器仓库，而广为人知的开发者最佳实践建议通过在不同服务器仓库之间进行提升（复制）不可变工件或包来管理流程，例如在包通过某些质量检查后，将它们从 `staging` 仓库复制到 `production` 仓库。但重要的是，这种提升不能以任何方式改变这些包，它们必须是完全不可变的，甚至不能改变其 `user/channel` ，这就是为什么上述建议不鼓励使用用户和频道，包和工件必须是不可变的。

## 禁止的实践

Conan 不是可重入的：不能从 Conan 本身调用 Conan 进程。这包括从配方代码、钩子、插件以及 Conan 被调用时已执行的任何代码中调用 Conan。这样做会导致未定义行为。例如，从 `conan search` 中运行 `conanfile.py` 是不合法的。这还包括间接调用，比如在构建脚本（如 `CMakeLists.txt` ）中运行 Conan，而该构建脚本本身是作为 Conan 调用结果被执行的。出于相同的原因，Conan Python API 不能在配方中使用：Conan Python API 只能从 Conan 自定义命令或用户 Python 脚本中调用，但绝不能从 `conanfile.py` 配方、钩子、扩展、插件或 Conan 执行的任何其他代码中调用。

在配方中，设置和配置（`conf`）是只读的：设置和配置不能在配方中定义或赋值。在配方中做类似 `self.settings.compiler = "gcc"` 的事情是不应该的。这是未定义行为，可能会导致随时崩溃，或者被忽略。设置和配置只能定义在配置文件中、命令行参数或 `profile.py` 插件中。

保留名称的配方：Conan `conanfile.py` 配方用户属性和方法应始终以 `_` 开头。Conan 为所有属性和方法保留“public”命名空间，为私有属性保留 `_conan` 。如果某个非文档化的 Python 函数、方法、类或属性在 Python 意义上被视为“public”，但未在此文档中说明，则使用该元素的行为是未定义的。

Conan 资产是不可变的：一旦 Conan 包和资产进入 Conan 缓存，它们就被视为不可变。任何尝试修改导出的源代码、配方、`conandata.yml` 或任何导出或打包的资产的行为都是未定义的。例如，无法在 `package_info()` 方法或 `package_id()` 方法中修改包的内容，这些方法不应修改、删除或创建包中的新文件。如果您需要修改某个包，您可以使用自己的自定义 `deployer` 。

Conan 缓存路径是内部实现细节：Conan 缓存路径是内部实现细节。Conan 配方提供如 `self.build_folder` 之类的抽象来表示关于文件夹的必要信息，以及如 conan cache path 之类的命令来获取当前文件夹的信息。在调试时可能会检查 Conan 缓存，以只读方式，但禁止通过 Conan 命令行或公共 API 以外的任何其他方式编辑、修改或删除 Conan 缓存中的工件或文件。

配方中使用的源必须是不可变的。一旦配方被导出到 Conan 缓存，就期望源是不可变的，也就是说，将来检索源时总是会检索完全相同的源。不允许使用移动目标，例如 git 分支或从不断被服务器重写的文件下载。 git 检出必须是不可变的标签或提交，而 `download()`/`get()` 必须使用校验和来验证服务器文件没有变化。不使用不可变源会导致未定义行为。
