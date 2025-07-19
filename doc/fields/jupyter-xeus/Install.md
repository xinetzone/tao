# 安装 `xeus`

该框架由三个库组成：
- `xeus`：提供了 Jupyter 协议的核心实现
- `xeus-zmq`：用于编写在专用进程中运行的内核的库
- `xeus-lite`：用于编写在浏览器中运行的内核的库

`xeus-zmq` 和 `xeus-lite` 都依赖于 `xeus`。

安装 `xeus` 最简单的方法是使用 `mamba` 或 `conda` 软件包管理器。
```bash
mamba install xeus -c conda-forge
```

## 使用 Mamba 或 Conda 安装 `xeus-zmq`

`xeus` 和 `xeus-zmq` 已经在所有平台上为 `mamba` （或 `conda`）软件包管理器打包。

```bash
mamba install xeus-zmq -c conda-forge
```

## 从源代码安装 `xeus-zmq`

xeus 依赖于以下库：[xtl](https://github.com/xtensor-stack/xtl) 和 [nlohmann_json](https://github.com/nlohmann/json)

xeus-zmq 依赖于以下库：[libzmq](https://github.com/zeromq/libzmq)、[cppzmq](https://github.com/zeromq/cppzmq)、[OpenSSL](https://github.com/OpenSSL/OpenSSL) 和 xeus。

在 Linux 平台上， `xeus` 还需要 `libuuid`，这在所有 Linux 发行版中都是可用的。所有这些依赖项打包在 conda-forge 上。安装它们的最简单的是运行：
```bash
mamba install cmake zeromq cppzmq OpenSSL xtl nlohmann_json -c conda-forge
```
在 Linux 平台上，您还需要：
```bash
mamba install libuuid -c conda-forge
```
安装完依赖后，你可以构建和安装 `xeus`：
```bash
cmake -D CMAKE_BUILD_TYPE=Release .
make
make install
```
然后你可以构建和安装 `xeus-zmq`：
```bash
cmake -D CMAKE_BUILD_TYPE=Release
make
make install
```

## 从源代码安装依赖项 `xeus-zmq`

依赖项也可以从源代码安装。只需克隆目录并运行以下 `cmake` 和 `make` 指令。

- libzmq  ZeroMQ 库
```bash
cmake -D WITH_PERF_TOOL=OFF -D ZMQ_BUILD_TESTS=OFF -D ENABLE_CPACK=OFF -D CMAKE_BUILD_TYPE=Release .
make
make install
```
- cppzmq  C++ZeroMQ(C++ZeroMQ 是一个仅包含头文件的库)
```bash
cmake -D CMAKE_BUILD_TYPE=Release .
make install
```

OpenSSL 已在大多数平台和包管理器中打包。通常不需要用户自行构建它。

`nlohmann_json` 是仅包含头文件的库：
```bash
cmake -DCMAKE_BUILD_TYPE=Release .
make install
```
xtl 是仅包含头文件的库：
```bash
cmake -DCMAKE_BUILD_TYPE=Release .
make install
```
