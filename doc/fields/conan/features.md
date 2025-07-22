# 其他重要的 Conan 功能

## `python_requires`

可以使用 [`python_requires`](https://docs.conan.io/2/reference/extensions/python_requires.html#reference-extensions-python-requires) 功能重用来自其他 recipe 的代码。

如果你维护许多针对不同包的 recipe，它们共享一些公共逻辑，而你不想在每个 recipe 中重复代码，你可以将这些公共代码放在 Conan conanfile.py 中，上传到你的服务器，然后让其他 recipe 的 conanfiles 执行 `python_requires = "mypythoncode/version"` 来依赖它并重用它。

## 包清单

可以通过“packages-list”功能一起管理包、配方和二进制文件的列表。`upload` 、 `download` 和 `remove` 等多个命令允许将包文件列表作为输入，并在该列表上执行操作。典型的用例是“上传最近 conan create 内构建的包到服务器”，这可以通过以下方式完成：

```bash
$ conan create . --format=json > build.json
$ conan list --graph=build.json --graph-binaries=build --format=json > pkglist.json
$ conan upload --list=pkglist.json -r=myremote -c
```

参见[示例](https://docs.conan.io/2/examples/commands/pkglists.html#examples-commands-pkglists)。

## 从缓存中删除未使用的包

```{warning}
最不常用的功能目前处于预览阶段。有关更多信息，请参阅 [Conan 稳定性部分](https://docs.conan.io/2/introduction.html#stability)。
```

Conan 缓存没有实现任何自动过期策略，因此其大小将不断增加，除非删除包或定期清理缓存。可以删除最近未使用的配方和包，同时保留在特定时间段内使用过的那些（最近最少使用 LRU 策略）。这可以通过 `--lru` 命令和 `conan remove` 、 `conan list` 命令的 `--lru` 参数来完成：

```bash
# remove all binaries (but not recipes) not used in the last 4 weeks
$ conan remove "*:*" --lru=4w -c
# remove all recipes that have not been used in the last 4 weeks (with their binaries)
$ conan remove "*" --lru=4w -c
```

请注意，LRU 时间遵循 `remove` 命令的规则。如果使用 `"*"` 模式删除配方，将只检查配方的 LRU 时间。如果一个配方最近被使用过，它将保留所有二进制文件；如果配方最近未被使用，它将删除自己和所有二进制文件。如果我们使用 `"*:*"` 模式，它将只检查二进制文件，并删除那些未使用的，但始终保留配方。

首先使用 `conan list` （请注意， `conan list` 不默认列出所有版本，与 `remove` 相反，因此如果需要，必须明确指定 `#*` 来选择所有版本）可以创建最近最少使用的包列表：

```bash
# List all unused (last 4 weeks) recipe revisions
$ conan list "*#*" --lru=4w --format=json > old.json
# Remove those recipe revisions (and their binaries)
$ conan remove --list=old.json -c
```
