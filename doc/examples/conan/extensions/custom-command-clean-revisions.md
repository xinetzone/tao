# 自定义命令：清理旧配方和包版本

请首先克隆源代码以重新创建此项目。你可以在 GitHub 的 examples2 仓库中找到它们：
```bash
$ git clone https://github.com/conan-io/examples2.git
$ cd examples2/examples/extensions/commands/clean
```

在这个示例中，将看到如何创建/使用自定义命令：`conan clean`。它从本地缓存或远程中删除每个配方及其包版本，但保留最新配方中的最新包版本。

```{note}
为了更好地理解这个示例，强烈建议先阅读[自定义命令参考](https://docs.conan.io/2/reference/extensions/custom_commands.html#reference-commands-custom-commands)。
```

## 定位命令

将命令文件 `cmd_clean.py` 复制到你的 `[YOUR_CONAN_HOME]/extensions/commands/` 文件夹（如果不存在则创建它）。如果你不知道 `[YOUR_CONAN_HOME]` 的位置，可以运行 `conan config home` 来检查它。

## 运行它

现在，你应该能在你的命令提示符中看到这个新命令：
```bash
$ conan -h
...
Custom commands
clean        Deletes (from local cache or remotes) all recipe and package revisions but the
               latest package revision from the latest recipe revision.

$ conan clean -h
usage: conan clean [-h] [-r REMOTE] [--force]

Deletes (from local cache or remotes) all recipe and package revisions but
the latest package revision from the latest recipe revision.

optional arguments:
  -h, --help            show this help message and exit
  -r REMOTE, --remote REMOTE
                        Will remove from the specified remote
  --force               Remove without requesting a confirmation
```

最后，如果你执行 `conan clean`：

```bash
$ conan clean
Do you want to remove all the recipes revisions and their packages ones, except the latest package revision from the latest recipe one? (yes/no): yes
other/1.0
Removed package revision: other/1.0#31da245c3399e4124e39bd4f77b5261f:da39a3ee5e6b4b0d3255bfef95601890afd80709#a16985deb2e1aa73a8480faad22b722c [Local cache]
Removed recipe revision: other/1.0#721995a35b1a8d840ce634ea1ac71161 and all its package revisions [Local cache]
hello/1.0
Removed package revision: hello/1.0#9a77cdcff3a539b5b077dd811b2ae3b0:da39a3ee5e6b4b0d3255bfef95601890afd80709#cee90a74944125e7e9b4f74210bfec3f [Local cache]
Removed package revision: hello/1.0#9a77cdcff3a539b5b077dd811b2ae3b0:da39a3ee5e6b4b0d3255bfef95601890afd80709#7cddd50952de9935d6c3b5b676a34c48 [Local cache]
libcxx/0.1
```

再次运行它时，什么也不应该发生：
```bash
$ conan clean
Do you want to remove all the recipes revisions and their packages ones, except the latest package revision from the latest recipe one? (yes/no): yes
other/1.0
hello/1.0
libcxx/0.1
```

## 代码导览

conan clean 命令具有以下代码：

```{code-block} python
:caption: cmd_clean.py

from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput, Color
from conan.cli.command import OnceArgument, conan_command


recipe_color = Color.BRIGHT_BLUE
removed_color = Color.BRIGHT_YELLOW


@conan_command(group="Custom commands")
def clean(conan_api: ConanAPI, parser, *args):
    """
    Deletes (from local cache or remotes) all recipe and package revisions but
    the latest package revision from the latest recipe revision.
    """
    parser.add_argument('-r', '--remote', action=OnceArgument,
                        help='Will remove from the specified remote')
    args = parser.parse_args(*args)

    out = ConanOutput()
    remote = conan_api.remotes.get(args.remote) if args.remote else None
    output_remote = remote or "Local cache"

    # Getting all the recipes
    recipes = conan_api.search.recipes("*/*", remote=remote)
    for recipe in recipes:
        out.writeln(f"{str(recipe)}", fg=recipe_color)
        all_rrevs = conan_api.list.recipe_revisions(recipe, remote=remote)
        latest_rrev = all_rrevs[0] if all_rrevs else None
        for rrev in all_rrevs:
            if rrev != latest_rrev:
                conan_api.remove.recipe(rrev, remote=remote)
                out.writeln(f"Removed recipe revision: {rrev.repr_notime()} "
                            f"and all its package revisions [{output_remote}]", fg=removed_color)
            else:
                packages = conan_api.list.packages_configurations(rrev, remote=remote)
                for package_ref in packages:
                    all_prevs = conan_api.list.package_revisions(package_ref, remote=remote)
                    latest_prev = all_prevs[0] if all_prevs else None
                    for prev in all_prevs:
                    if prev != latest_prev:
                        conan_api.remove.package(prev, remote=remote)
                        out.writeln(f"Removed package revision: {prev.repr_notime()} [{output_remote}]", fg=removed_color)
```

分析最重要的部分。

## parser

`parser` 参数是 Python 命令行解析 {class}`argparse.ArgumentParser` 的实例，如果你想了解更多关于它的 API，请访问它的[官方网站](https://docs.python.org/3/library/argparse.html)。

## 用户输出

`ConanOutput()` : 管理用户输出的类。在这个示例中，只使用了 `out.writeln(message, fg=None, bg=None)` ，其中 `fg` 是字体前景色，`bg` 是字体背景色。除此之外，还有一些预定义的方法，如 `out.info()` 、 `out.success()` 、 `out.error()` 等。

## Conan 公共 API

这个示例中最重要的部分是通过 `conan_api` 参数使用 Conan API。以下是在这个自定义命令中使用的一些示例：

```python
conan_api.remotes.get(args.remote)
conan_api.search.recipes("*/*", remote=remote)
conan_api.list.recipe_revisions(recipe, remote=remote)
conan_api.remove.recipe(rrev, remote=remote)
conan_api.list.packages_configurations(rrev, remote=remote)
conan_api.list.package_revisions(package_ref, remote=remote)
conan_api.remove.package(prev, remote=remote)
```

- `conan_api.remotes.get(...)` : `[RemotesAPI]` 根据远程名称返回一个 RemoteRegistry。
- `conan_api.search.recipes(...)` : `[SearchAPI]` 返回所有匹配给定模式的配方列表。
- `conan_api.list.recipe_revisions(...)` : `[ListAPI]` 根据配方引用返回所有配方修订版本列表。
- `conan_api.list.packages_configurations(...)` : [ListAPI] 返回指定配方修订版本的配置列表（package_id）。
- `conan_api.list.package_revisions(...)` : `[ListAPI]` 返回指定配方修订版本的包修订版本列表。
- `conan_api.remove.recipe(...)` : `[RemoveAPI]` 删除指定的配方版本。
- `conan_api.remove.package(...)` : `[RemoveAPI]` 删除指定的软件包版本。

除此之外，这些行值得特别关注：

```python
all_rrevs = conan_api.list.recipe_revisions(recipe, remote=remote)
latest_rrev = all_rrevs[0] if all_rrevs else None

...

packages = conan_api.list.packages_configurations(rrev, remote=remote)

...

all_prevs = conan_api.list.package_revisions(package_ref, remote=remote)
latest_prev = all_prevs[0] if all_prevs else None
```

基本上，这些 API 调用分别返回食谱修订版本和软件包修订版本的列表，但我们保存第一个元素为最新版本，因为这些调用总是获取一个有序列表。
如需了解更多关于 Conan API 的信息，请访问 [ConanAPI 部分](https://docs.conan.io/2/reference/extensions/python_api/ConanAPI.html#reference-python-api-conan-api)