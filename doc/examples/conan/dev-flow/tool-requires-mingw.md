# 使用 MinGW 作为 `tool_requires` 在 Windows 上使用 `gcc` 构建

如果环境中已安装 MinGW，可以定义配置文件，如下所示：

```
[settings]
os=Windows
compiler=gcc
compiler.version=12
compiler.libcxx=libstdc++11
compiler.threads=posix
compiler.exception=sjlj
arch=x86_64
build_type=Release

[buildenv]
PATH+=(path)C:/path/to/mingw/bin
# other environment we might need like
CXX=C:/path/to/mingw/bin/g++
# etc

[conf]
# some configuration like 'tools.build:compiler_executables' might be needed for some cases
```

但也可以使用包含 MinGW 编译器副本的 Conan 包，并将其作为 `tool_requires` 使用：

`mingw-profile.txt`:
```ini
[settings]
os=Windows
compiler=gcc
compiler.version=12
compiler.libcxx=libstdc++11
compiler.threads=posix
compiler.exception=seh
arch=x86_64
build_type=Release


[tool_requires]
mingw-builds/12.2.0
```

使用此配置文件，可以在 Windows 中创建包：

```bash
# Using a basic template project
$ conan new cmake_lib -d name=mypkg -d version=0.1
$ conan create . -pr=mingw
...
-- The CXX compiler identification is GNU 12.2.0
...


======== Testing the package: Executing test ========
mypkg/0.1 (test package): Running test()
mypkg/0.1 (test package): RUN: .\example
mypkg/0.1: Hello World Release!
mypkg/0.1: _M_X64 defined
mypkg/0.1: __x86_64__ defined
mypkg/0.1: _GLIBCXX_USE_CXX11_ABI 1
mypkg/0.1: MSVC runtime: MultiThreadedDLL
mypkg/0.1: __cplusplus201703
mypkg/0.1: __GNUC__12
mypkg/0.1: __GNUC_MINOR__2
mypkg/0.1: __MINGW32__1
mypkg/0.1: __MINGW64__1
mypkg/0.1 test_package
```

```{seealso}
1. `https://conan.io/center/recipes/mingw-builds` 包的 [ConanCenter 网页](https://conan.io/center/recipes/mingw-builds)
2. conan-center-index mingw-builds[ Github 仓库的 recipe](https://github.com/conan-io/conan-center-index/tree/master/recipes/mingw-builds/all)
```
