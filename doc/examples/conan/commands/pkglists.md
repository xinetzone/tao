# 使用 `packages-lists`

包列表是 Conan 的强大且便捷的功能，它允许自动化和串联不同的 Conan 命令。看看一些常见的用例：

## 列出包并下载它们

简单的使用案例可能是列出服务器中的一些配方和/或二进制文件，然后下载它们。

可以做任何 `conan list` ，例如，列出所有 `zlib` 以上的版本，最新的配方修订版，该最新配方修订版的全部 Windows 二进制文件，以及每个二进制文件的最新包修订版。请注意，如果我们稍后想要实际下载某些内容，必须指定 `latest` 包修订版，否则只会下载配方。

```bash
$ conan list "zlib/[>1.2.11]#latest:*#latest" -p os=Windows --format=json -r=conancenter > pkglist.json
```

命令的输出以 `json` 格式发送到文件 `pkglist.json` ，该文件看起来像：

```{code-block} json
:caption: pkglist.json (simplified)

"conancenter": {
    "zlib/1.2.12": {
        "revisions": {
            "b1fd071d8a2234a488b3ff74a3526f81": {
                "timestamp": 1667396813.987,
                "packages": {
                    "ae9eaf478e918e6470fe64a4d8d4d9552b0b3606": {
                        "revisions": {
                            "19808a47de859c2408ffcf8e5df1fdaf": {
                            }
                        },
                        "info": {
                            "settings": {
                                "arch": "x86_64",
                                "os": "Windows"
                            }
                        }
                    }
                }
            }
        },
    "zlib/1.2.13": {
    }
}
```

`pkglist.json` 的第一级是“origin”远程或“本地缓存”，如果列表发生在缓存中。在这种情况下，因为我们列出了 conancenter 远程中的包，所以那将是 `origin`。

现在可以用一次 `conan download` 调用来下载这些配方和二进制文件：
```bash
$ conan download --list=pkglist.json -r=conancenter
# Download the recipes and binaries in pkglist.json
# And displays a report of the downloaded things
```

## 从远程下载并上传到不同的远程

假设从上一步下载的包创建新的包列表：

```bash
$ conan download --list=pkglist.json -r=conancenter --format=json > downloaded.json
# Download the recipes and binaries in pkglist.json
# And stores the result in "downloaded.json"
```

生成的 `downloaded.json` 将与 `pkglist.json` 文件几乎相同，但在此情况下，这些软件包的“来源”是 "Local Cache" （因为下载的软件包将存放在缓存中）：

```{code-block} json
:caption: downloaded.json (simplified)

"Local Cache": {
        "zlib/1.2.12": {
            "revisions": {
            }
        }
    }
```

这意味着现在可以将同一套配方和二进制文件上传到不同的远程服务器：

```bash
$ conan upload --list=downloaded.json -r=myremote -c
# Upload those artifacts to the same remote
```

```{admonition} 最佳实践
这将是运行不同服务器仓库之间推广的慢速机制。像 Artifactory 这样的服务器提供了直接从一个仓库复制软件包到另一个仓库的方法，而无需使用客户端，由于文件去重，这种方法的速度要快几个数量级，因此这是推荐的方法。本节介绍的方法可能适用于离线环境和其他无法进行服务器到服务器复制的情况。
```

## 构建和上传软件包 

最有趣的过程之一是当一些包在本地缓存中通过 `conan create` 或 `conan install --build=xxx` 命令进行构建时。通常情况下，我们希望将本地构建的包上传到服务器，这样其他人就不必再重新构建它们。但我们可能只想上传构建的二进制文件，而不是所有其他传递依赖项，或之前已存在于本地缓存中的其他包。

可以从 `conan install` 、 `conan create` 和 `conan graph info` 命令的输出来计算一个包列表。然后，可以使用这个包列表进行上传。逐步说明如下：

首先，假设我们有一个自己的包 `mypkg/0.1` ，我们创建它：
```bash
$ conan new cmake_lib -d name=mypkg -d version=0.1
$ conan create . --format=json > create.json
```
这将创建一个图的 `json` 表示形式，包含已构建的包的信息 `"binary": "Build"`:

```{code-block} json
:caption: create.json (simplified)

{
"graph": {
    "nodes": {
        "0": {
            "ref": "conanfile",
            "id": "0",
            "recipe": "Cli",
            "context": "host",
            "test": false
        },
        "1": {
            "ref": "mypkg/0.1#f57cc9a1824f47af2f52df0dbdd440f6",
            "id": "1",
            "recipe": "Cache",
            "package_id": "2401fa1d188d289bb25c37cfa3317e13e377a351",
            "prev": "75f44d989175c05bc4be2399edc63091",
            "build_id": null,
            "binary": "Build"
        }
    }
}
```

可以从这个文件中计算一个包列表，然后使用以下命令将这些工件上传到服务器：
```bash
$ conan list --graph=create.json --graph-binaries=build --format=json > pkglist.json
# Create a pkglist.json with the known list of recipes and binaries built from sources
$ conan upload --list=pkglist.json -r=myremote -c
```

## 删除软件包列表

也可以先 `conan list` 创建一个待删除项列表，然后再进行删除：
```bash
# Removes everything from the cache
$ conan list "*#*" --format=json > pkglist.json
$ conan remove --list=pkglist.json  -c
```

需要注意的是，在 `list` 和 `remove` 中，默认模式有所不同，因为 `conan remove` 具有破坏性：

- 当将配方传递给 `remove` 如 `conan remove zlib/1.2.13` 时，它会删除 `zlib/1.2.13` 的配方及其所有二进制文件，因为二进制文件无法脱离配方而存在。
- 当传递 `package_id` 如 `conan remove zlib/1.2.13:package_id` 时，则只会删除特定的 `package_id` ，而配方不会被删除。

如果我们直接调用 `conan remove` ，或者先调用 `conan list` ，那么用来删除所有内容的模式将会不同，例如：

```bash
# Removes everything from the cache
$ conan remove "*"
# OR via list, we need to explicitly include all revisions
$ conan list "*#*" --format=json > pkglist.json
$ conan remove --list=pkglist.json  -c

# Removes only the binaries from the cache (leave recipes)
$ conan remove "*:*"
# OR via list, we need to explicitly include all revisions
$ conan list "*#*:*" --format=json > pkglist.json
$ conan remove --list=pkglist.json  -c
```

更多信息请参见参考[命令部分](https://docs.conan.io/2/reference/commands.html#reference-commands)
