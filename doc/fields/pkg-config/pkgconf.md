# `pkgconf`

[`pkgconf`](https://github.com/pkgconf/pkgconf) 是一个程序，它有助于为开发库配置编译器和链接器标志。它是 freedesktop.org 的 pkg-config 提供的功能的超集，但不提供与原始 pkg-config 的错误兼容性。

`libpkgconf` 是一个库，它提供对 `pkgconf` 大部分功能的访问，以允许其他工具（如编译器和 IDE）发现和使用 `pkgconf` 配置的库。

## 构建系统设置

如果您想直接使用 git 源代码，或来自 GitHub 的源代码的快照，则需要自行重新生成 autotools 构建系统工件，或者改用 Meson。例如，在 Alpine 上：
```bash
apk add autoconf automake libtool build-base
sh ./autogen.sh
```

## `pkgconf-lite`

如果您只需要原始的 `pkg-config` 功能，还可以使用 `pkgconf-lite`，它将 `pkgconf` 前端和 `libpkgconf` 功能的相关部分构建到一个二进制文件中：
```bash
make -f Makefile.lite
```

## 为什么选择 `pkgconf` 而不是原始的 `pkg-config`？

`pkgconf` 构建了扁平化的有向依赖关系图，它允许更深入地了解依赖关系之间的关系，允许进行一些链接时依赖优化，这允许用户更保守地链接他们的二进制文件，这在某些环境中可能会有所帮助，例如当使用 `prelink(1)` 时。

该求解器还经过优化，可以处理具有数十万条边的大型依赖关系图，例如，在任何使用 Abseil 框架的项目中都可以看到这一点。

此外，`pkgconf` 完全支持虚拟包，而原始 `pkg-config` 则没有，并且在依赖关系解析时完全支持 `Conflicts`，这比在遍历依赖关系图时检查 `Conflicts` 更有效。

## 链接器标志优化

如果有效使用，`pkgconf` 可以进行优化以避免过度链接二进制文件。

此功能取决于 `pkg-config` 模块正确声明其依赖树，而不是使用 `Libs` 和 `Cflags` 字段直接链接到安装了 `pkg-config` 元数据文件的其他模块。

出于这个原因， 在 [Dan Nicholson 的 `pkg-config` 教程](http://people.freedesktop.org/~dbn/pkg-config-guide.html)中不建议使用 `Libs` 和 `Cflags` 来描述不相关的依赖项。

## 与原始 `pkg-config` 的错误兼容性

一般来说，`pkgconf` 不提供与原始 `pkg-config` 的错误级别兼容性。

这意味着，如果您认为与 `pkg-config` 存在合法的回归，请告诉 `pkgconf` 社区，但是也要确保 `.pc` 文件有效并遵循 [`pkg-config` 教程的规则](http://people.freedesktop.org/~dbn/pkg-config-guide.html)，因为很可能将它们修复为遵循指定的规则将解决问题。

## 调试输出

请仅使用稳定的接口查询 `pkg-config`。不要对 `--debug` 的输出进行屏幕抓取：这是出于某种原因发送到 `stderr` 的，它不打算被抓取。`--debug` 输出不是稳定的接口， 永远不应该依赖它作为信息来源。如果您需要稳定的接口来查询未涵盖的 `pkg-config`，请联系 `pkgconf` 社区。

## 在 UNIX 上编译 `pkgconf` 和 `libpkgconf`

`pkgconf` 的编译方式基本上与任何其他基于 Autotools 的项目的编译方式相同：

```bash
$ ./configure
$ make
$ sudo make install
```

如果您要将 `pkgconf` 安装到自定义前缀中，例如 `/opt/pkgconf`，您可能需要为工具链定义默认系统 `includeir` 和 `libdir`。为此，请使用 `--with-system-includedir` 和 `--with-system-libdir` 配置标志，如下所示：

```bash
$ ./configure \
     --prefix=/opt/pkgconf \
     --with-system-libdir=/lib:/usr/lib \
     --with-system-includedir=/usr/include
$ make
$ sudo make install
```

## 使用 Meson 编译 `pkgconf` 和 `libpkgconf`（通常适用于 Windows）

`pkgconf` 是在 Windows 上使用 Meson 编译的。理论上，你也可以使用 Meson 在 UNIX 上构建，但目前不建议这样做，因为 `pkgconf` 通常比 Meson 早得多。

```bash
$ meson setup build -Dtests=disabled
$ meson compile -C build
$ meson install -C build
```

## `pkg-config` 符号链接

如果您希望在调用 `pkg-config` 时使用 `pkgconf`，您应该为此安装一个符号链接。`pkgconf` 不会为您这样做，因为 `pkgconf` 认为供应商最好自己做出此决定。

```bash
$ ln -sf pkgconf /usr/bin/pkg-config
```

## 使用 conda 安装

参考：[conda-forge/pkgconf](https://anaconda.org/conda-forge/pkgconf)

```bash
conda install conda-forge::pkgconf
```