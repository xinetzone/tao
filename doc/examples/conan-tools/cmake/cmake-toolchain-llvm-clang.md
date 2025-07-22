# CMakeToolchain: 使用 LLVM/Clang Windows 编译器

Windows 中的 Clang 编译器可以来自两种不同的安装或分发：

- 使用 MSVC 运行的 LLVM/Clang 编译器
- 使用 Msys2 运行的 Msys2 Clang 编译器（`libstdc++6.dll`）

这个示例解释了使用 MSVC 运行时的 LLVM/Clang。这个 Clang 发行版可以以三种不同的方式使用：

- 使用 Visual Studio 安装程序安装的 Clang 组件作为 VS 的一部分
- 使用下载的 LLVM/Clang 编译器（它仍然使用 MSVC 运行时），通过 GNU-like 前端 `clang`
- 使用下载的 LLVM/Clang 编译器（它仍然使用 MSVC 运行时），通过 MSVC-like 前端 `clang-cl`

从简单的 `cmake_exe` 模板开始：

```bash
conan new cmake_exe -d name=mypkg -d version=0.1
```

这会创建基于 CMake 的项目和使用 CMakeToolchain 的 Conan 软件包配方。

## 使用 clang 的 LLVM/Clang GNU 风格前端

为了构建这个配置，将使用以下配置文件：

```{code-block} ini
:caption: llvm_clang

[settings]
os=Windows
arch=x86_64
build_type=Release
compiler=clang
compiler.version=18
compiler.cppstd=14
compiler.runtime=dynamic
compiler.runtime_type=Release
compiler.runtime_version=v144

[buildenv]
PATH=+(path)C:/ws/LLVM/18.1/bin

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
tools.compilation:verbosity=verbose

[tool_requires]
ninja/[*]
```

该配置文件的快速说明：

- `compiler.runtime` 的定义是区分 Msys2-Clang 和带有 MSVC 运行的 LLVM/Clang 的重要不同点。LLVM/Clang 定义了这个 `compiler.runtime` ，而 Msys2-Clang 没有定义。
- MSVC 运行时可以是动态的或静态的。同样重要的是定义这个运行时的版本（工具集版本 `v144` ），因为可能使用不同的版本。
- `[buildenv]` 允许指向 LLVM/Clang 编译器，如果它不在路径中。注意 `PATH=+(path)` 语法，以添加该路径，使其具有更高的优先级，否则 CMake 可能会找到并使用 Visual Studio 中安装的 Clang 组件。
- 正在使用 Ninja CMake 生成器，并从 `[tool_requires]` 安装它，但如果您的系统已安装 Ninja，则可能不需要这样做。

构建它：

```bash
$ conan build . -pr=llvm_clang
...
-- The CXX compiler identification is Clang 18.1.8 with GNU-like command-line
-- Check for working CXX compiler: C:/ws/LLVM/18.1/bin/clang++.exe - skipped
...
[1/3] C:\ws\LLVM\18.1\bin\clang++.exe   -O3 -DNDEBUG -std=c++14 -D_DLL -D_MT -Xclang --dependent-lib=msvcrt -MD -MT CMakeFiles/mypkg.dir/src/main.cpp.obj -MF CMakeFiles\mypkg.dir\src\main.cpp.obj.d -o CMakeFiles/mypkg.dir/src/main.cpp.obj -c C:/Users/Diego/conanws/kk/clang/src/main.cpp
[2/3] C:\ws\LLVM\18.1\bin\clang++.exe   -O3 -DNDEBUG -std=c++14 -D_DLL -D_MT -Xclang --dependent-lib=msvcrt -MD -MT CMakeFiles/mypkg.dir/src/mypkg.cpp.obj -MF CMakeFiles\mypkg.dir\src\mypkg.cpp.obj.d -o CMakeFiles/mypkg.dir/src/mypkg.cpp.obj -c C:/Users/Diego/conanws/kk/clang/src/mypkg.cpp
[3/3] cmd.exe /C "cd . && C:\ws\LLVM\18.1\bin\clang++.exe -fuse-ld=lld-link -nostartfiles -nostdlib -O3 -DNDEBUG -D_DLL -D_MT -Xclang --dependent-lib=msvcrt -Xlinker /subsystem:console CMakeFiles/mypkg.dir/src/mypkg.cpp.obj CMakeFiles/mypkg.dir/src/main.cpp.obj -o mypkg.exe -Xlinker /MANIFEST:EMBED -Xlinker /implib:mypkg.lib -Xlinker /pdb:mypkg.pdb -Xlinker /version:0.0   -lkernel32 -luser32 -lgdi32 -lwinspool -lshell32 -lole32 -loleaut32 -luuid -lcomdlg32 -ladvapi32 -loldnames  && cd ."
```

看看如何使用 `C:/ws` 文件夹中安装的所需 LLVM/Clang 编译器，以及如何使用 GNU-like 命令行语法。类似 GNU 的语法需要 `--dependent-lib=msvcrt` （由 CMake 自动添加）编译器和链接器标志来定义链接到动态 MSVC 运行时，否则 LLVM/Clang 会静态链接。还请注意， `-MD -MT` 标志与

可以运行我们的可执行文件，看看 Clang 编译器版本和 MSVC 运行时是否与定义的匹配：

```bash
$ build\Release\mypkg.exe
mypkg/0.1: Hello World Release!
    mypkg/0.1: _M_X64 defined
    mypkg/0.1: __x86_64__ defined
    mypkg/0.1: MSVC runtime: MultiThreadedDLL
    mypkg/0.1: _MSC_VER1943
    mypkg/0.1: _MSVC_LANG201402
    mypkg/0.1: __cplusplus201402
    mypkg/0.1: __clang_major__18
    mypkg/0.1: __clang_minor__1
```

## LLVM/Clang with clang-cl 类似 MSVC 的前端

为了构建这个配置，将使用以下配置文件：

```{code-block} ini
:caption: llvm_clang_cl

[settings]
os=Windows
arch=x86_64
build_type=Release
compiler=clang
compiler.version=18
compiler.cppstd=14
compiler.runtime=dynamic
compiler.runtime_type=Release
compiler.runtime_version=v144

[buildenv]
PATH=+(path)C:/ws/LLVM/18.1/bin

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
tools.build:compiler_executables = {"c": "clang-cl", "cpp": "clang-cl"}
tools.compilation:verbosity=verbose

[tool_requires]
ninja/[*]
```

该配置文件几乎与上面的一样，主要区别在于 `tools.build:compiler_executables` 的定义，定义了 `clang-cl` 编译器。

```{note}
使用 `clang-cl` 编译器定义 `tools.build:compiler_executables` 是 Conan 用来区分不同前端（在其它构建系统中也是如此）。这个前端不是 `setting` ，因为编译器仍然是相同的，生成的二进制文件应该是二进制兼容的。
```

构建它：

```bash
$ conan build . -pr=llvm_clang_cl
...
-- The CXX compiler identification is Clang 18.1.8 with MSVC-like command-line
-- Check for working CXX compiler: C:/ws/LLVM/18.1/bin/clang-cl.exe - skipped
...
[1/3] C:\ws\LLVM\18.1\bin\clang-cl.exe  /nologo -TP   /DWIN32 /D_WINDOWS /GR /EHsc /O2 /Ob2 /DNDEBUG -std:c++14 -MD /showIncludes /FoCMakeFiles\mypkg.dir\src\main.cpp.obj /FdCMakeFiles\mypkg.dir\ -c -- C:\project\src\main.cpp
[2/3] C:\ws\LLVM\18.1\bin\clang-cl.exe  /nologo -TP   /DWIN32 /D_WINDOWS /GR /EHsc /O2 /Ob2 /DNDEBUG -std:c++14 -MD /showIncludes /FoCMakeFiles\mypkg.dir\src\mypkg.cpp.obj /FdCMakeFiles\mypkg.dir\ -c -- C:\project\src\mypkg.cpp
[3/3] cmd.exe /C "cd . && C:\ws\cmake\cmake-3.27.9-windows-x86_64\bin\cmake.exe -E vs_link_exe --intdir=CMakeFiles\mypkg.dir --rc=C:\PROGRA~2\WI3CF2~1\10\bin\100226~1.0\x64\rc.exe --mt=C:\PROGRA~2\WI3CF2~1\10\bin\100226~1.0\x64\mt.exe --manifests  -- C:\ws\LLVM\18.1\bin\lld-link.exe /nologo CMakeFiles\mypkg.dir\src\mypkg.cpp.obj CMakeFiles\mypkg.dir\src\main.cpp.obj  /out:mypkg.exe /implib:mypkg.lib /pdb:mypkg.pdb /version:0.0 /machine:x64 /INCREMENTAL:NO /subsystem:console  kernel32.lib user32.lib gdi32.lib winspool.lib shell32.lib ole32.lib oleaut32.lib uuid.lib comdlg32.lib advapi32.lib && cd ."
```

查看如何使用安装在 `C:/ws` 文件夹中的目标 LLVM/Clang 编译器，以及如何使用 `MSVC-like` 命令行语法。这种类似 MSVC 的语法使用 `-MD/-MT` 标志来区分动态和静态 MSVC 运行时。

运行可执行文件，看看 Clang 编译器版本和 MSVC 运行时是否与定义的匹配：
```bash
$ build\Release\mypkg.exe
mypkg/0.1: Hello World Release!
    mypkg/0.1: _M_X64 defined
    mypkg/0.1: __x86_64__ defined
    mypkg/0.1: MSVC runtime: MultiThreadedDLL
    mypkg/0.1: _MSC_VER1943
    mypkg/0.1: _MSVC_LANG201402
    mypkg/0.1: __cplusplus201402
    mypkg/0.1: __clang_major__18
    mypkg/0.1: __clang_minor__1
```

正如预期，输出与之前相同，因为除了编译器前端外，没有其他变化。

## MSVC Clang 组件（ClangCL Visual Studio 工具集）

为了构建这个配置，将使用以下配置文件：

```{code-block} ini
:caption: llvm_clang_vs

[settings]
os=Windows
arch=x86_64
build_type=Release
compiler=clang
compiler.version=19
compiler.cppstd=14
compiler.runtime=dynamic
compiler.runtime_type=Release
compiler.runtime_version=v144

[conf]
tools.cmake.cmaketoolchain:generator=Visual Studio 17
tools.compilation:verbosity=verbose
```

此配置文件将使用 CMake 的“Visual Studio”生成器。这表示 Clang 编译器将是 Visual Studio 提供的那个，并通过 Visual Studio 安装程序作为 Visual Studio 的组件进行安装。请注意， `compiler.version=19` 是与上面使用的不同版本，上面使用的是 `compiler.version=18` ，因为 Visual Studio 内部的版本是由其安装程序自动定义的。

这种设置将始终使用类似 MSVC 的 `clang-cl` 前端，并激活 ClangCL 工具集，以告知 Visual Studio 这是它应该使用的编译器。在这里定义 `tools.build:compiler_executable` 是不必要的。

构建它：
```bash
$ conan build . -pr=llvm_clang_vs
...
-- Conan toolchain: CMAKE_GENERATOR_TOOLSET=ClangCL
-- The CXX compiler identification is Clang 19.1.1 with MSVC-like command-line
...
ClCompile:
    C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\Llvm\x64\bin\clang-cl.exe /c /nologo /W1 /WX- /diagnostics:column /O2 /Ob2 /D _MBCS /D WIN
32 /D _WINDOWS /D NDEBUG /D "CMAKE_INTDIR=\"Release\"" /EHsc /MD /GS /fp:precise /GR /std:c++14 /Fo"mypkg.dir\Release\\" /Gd /TP --target=amd64-pc-windows-
msvc  C:\project\src\mypkg.cpp C:\project\src\main.cpp
Link:
C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\Llvm\x64\bin\lld-link.exe /OUT:"C:\project\build\Release\mypkg.exe" /
INCREMENTAL:NO kernel32.lib user32.lib gdi32.lib winspool.lib shell32.lib ole32.lib oleaut32.lib uuid.lib comdlg32.lib advapi32.lib /MANIFEST /MANIFESTUAC:
"level='asInvoker' uiAccess='false'" /manifest:embed /PDB:"C:/Users/Diego/conanws/kk/clang/build/Release/mypkg.pdb" /SUBSYSTEM:CONSOLE /DYNAMICBASE /NXCOMP
AT /IMPLIB:"C:/Users/Diego/conanws/kk/clang/build/Release/mypkg.lib"   /machine:x64 mypkg.dir\Release\mypkg.obj
mypkg.dir\Release\main.obj
mypkg.vcxproj -> C:\project\build\Release\mypkg.exe
```

`CMAKE_GENERATOR_TOOLSET=ClangCL` 已定义，同时使用了内部 VS Clang 组件，并且也显示了 `19.1.1` 版本。然后，使用了常规的 `MSVC-like` 语法，包括通过 `/MD` 标志定义运行时。

运行可执行文件，看看 Clang 编译器版本（ `19` ）和 MSVC 运行时是否与定义的一致：

```bash
$ build\Release\mypkg.exe
mypkg/0.1: Hello World Release!
    mypkg/0.1: _M_X64 defined
    mypkg/0.1: __x86_64__ defined
    mypkg/0.1: MSVC runtime: MultiThreadedDLL
    mypkg/0.1: _MSC_VER1943
    mypkg/0.1: _MSVC_LANG201402
    mypkg/0.1: __cplusplus201402
    mypkg/0.1: __clang_major__19
    mypkg/0.1: __clang_minor__1
```
