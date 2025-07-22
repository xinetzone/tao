# 捕获 Git scm 信息

处理配方中的源代码有 2 种主要策略：
- 第三方代码：当 `conanfile.py` 配方打包第三方代码，如开源库时，通常最好使用 `source()` 方法下载或克隆该库的源代码。这是 ConanCenter 仓库采用的方法。
- 自己的代码：当 `conanfile.py` 配方打包自己的代码时，通常最好将 `conanfile.py` 与源代码放在同一仓库中。然后，有 2 种替代方案可以实现可重复性：
    - 使用 `exports_sources` （或 `export_source()` 方法）在 Conan 包中捕获源代码的副本以及配方。这非常简单且实用，建议大多数情况下使用此方法。
    - 当无法将源代码存储在 Conan 配方旁边时，例如当该软件包需要供完全无法访问源代码的人使用时，那么当前的 scm 捕获方法将是解决方案。

在 scm 捕获方法中，不是捕获代码本身的副本，而是捕获该代码的“坐标”，在 Git 的情况下，是存储库的 `url` 和 `commit`。如果配方需要从源代码构建，它将使用这些信息来获取克隆，如果尝试该操作的用户没有授权，则过程将失败。他们仍然可以使用我们分发的预编译二进制文件，但不能从源代码构建或访问代码。

通过例子来看看它是如何工作的。请首先克隆源代码以重新创建这个项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/tools/scm/git/capture_scm
```

在那里我们将找到一个小的“hello”项目，包含这个 `conanfile.py` 。

```{code-block} python
:caption: conanfile.py

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.scm import Git


class helloRecipe(ConanFile):
    name = "hello"
    version = "0.1"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "CMakeDeps", "CMakeToolchain"

    def export(self):
        git = Git(self, self.recipe_folder)
        # save the url and commit in conandata.yml
        git.coordinates_to_conandata()

    def source(self):
        # we recover the saved url and commit from conandata.yml and use them to get sources
        git = Git(self)
        git.checkout_from_conandata_coordinates()

    ...
```


需要将这段代码放在它自己的 Git 仓库中，以查看它在实际场景中的运行情况，因此请创建位于 examples2 仓库之外的文件夹，并将当前文件夹的内容复制到那里，然后：

```
$ mkdir /home/myuser/myfolder # or equivalent in other OS
$ cp -R . /home/myuser/myfolder # or equivalent in other OS
$ cd /home/myuser/myfolder # or equivalent in other OS

# Initialize the git repo
$ git init .
$ git add .
$ git commit . -m wip
# Finally create the package
$ conan create .
...
======== Exporting recipe to the cache ========
hello/0.1: Exporting package recipe: /myfolder/conanfile.py
hello/0.1: Calling export()
hello/0.1: RUN: git status . --short --no-branch --untracked-files
hello/0.1: RUN: git rev-list HEAD -n 1 --full-history -- "."
hello/0.1: RUN: git remote -v
hello/0.1: RUN: git branch -r --contains cb7815a58529130b49da952362ce8b28117dee53
hello/0.1: RUN: git fetch origin --dry-run --depth=1 cb7815a58529130b49da952362ce8b28117dee53
hello/0.1: WARN: Current commit cb7815a58529130b49da952362ce8b28117dee53 doesn't exist in remote origin
This revision will not be buildable in other computer
hello/0.1: RUN: git rev-parse --show-toplevel
hello/0.1: Copied 1 '.py' file: conanfile.py
hello/0.1: Copied 1 '.yml' file: conandata.yml
hello/0.1: Exported to cache folder: /.conan2/p/hello237d6f9f65bba/e
...
======== Installing packages ========
hello/0.1: Calling source() in /.conan2/p/hello237d6f9f65bba/s
hello/0.1: Cloning git repo
hello/0.1: RUN: git clone "<hidden>"  "."
hello/0.1: Checkout: cb7815a58529130b49da952362ce8b28117dee53
hello/0.1: RUN: git checkout cb7815a58529130b49da952362ce8b28117dee53
```

逐步解释正在发生的事情：

- 当配方导出到 Conan 缓存时， `export()` 方法执行， `git.coordinates_to_conandata()` ，它通过内部调用 `git.get_url_and_commit()` 将 Git URL 和提交存储在 `conandata.yml` 文件中。有关这些方法的更多信息，请参阅 [Git 参考](https://docs.conan.io/2/reference/tools/scm/git.html#conan-tools-scm-git)。
- 这获取指向本地 `<local-path>/capture_scm` 的仓库的 URL 和提交 `8e8764c40bebabbe3ec57f9a0816a2c8e691f559`
- 它警告说，一旦软件包上传到服务器并在其他不包含 `<local-path>/capture_scm `所指向路径的计算机上尝试从源代码构建时，这些信息将不足以重新构建这个配方。这是可以预料的，因为我们创建的仓库没有定义任何远程仓库。如果我们的本地克隆定义了远程仓库，并且该远程仓库包含我们正在构建的 `commit` ，那么 `scm_url` 将指向远程仓库，从而使得从源代码构建完全可重复。
- `export()` 方法将 `url` 和 `commit` 信息存储在 `conandata.yml` 中，以实现未来的可重复性。
- 当需要从源代码构建包并调用 `source()` 方法时，它会在 `git.checkout_from_conandata_coordinates()` 方法中从 `conandata.yml` 文件中恢复信息，该方法内部使用这些信息调用 `git.clone()` 以获取源代码。在这种情况下，它将从 `<local-path>/capture_scm` 中的本地检出克隆，但如果定义了远程仓库，它将从远程仓库克隆。

```{warning}
为了实现可重复性，对于这种 scm 捕获技术来说，当前检出不能是脏的。如果检出是脏的，将无法保证构建的未来可重复性，因此 `git.get_url_and_commit()` 可能会引发错误，并要求提交更改。如果需要超过 1 个提交，建议在将更改推送到上游仓库之前合并这些提交。
```

如果我们现在进行第二次 `conan create .` ，由于仓库已处于脏状态，会得到：
```bash
$ conan create .
hello/0.1: Calling export()
ERROR: hello/0.1: Error in export() method, line 19
    scm_url, scm_commit = git.get_url_and_commit()
    ConanException: Repo is dirty, cannot capture url and commit: .../capture_scm
```

这可以通过使用 `git clean -xdf` 清理仓库来解决，或者向仓库中添加 `.gitignore` 文件，内容如下（这无论如何对于源代码控制来说可能都是好习惯）：

```{code-block} bash
:caption: .gitignore

test_package/build
test_package/CMakeUserPresets.json
```

坐标的捕获使用 `Git.get_url_and_commit()` 方法，默认情况下执行：
- 如果仓库不干净，它将抛出异常
- 如果仓库干净，但提交不存在于远程仓库，它将发出警告，但会返回本地文件夹作为仓库 `url`。这样，可以在不需要将它们推送到服务器的情况下测试本地提交。`core.scm:local_url=allow` 可以抑制警告，而 `core.scm:local_url=block` 将立即抛出错误：这个最后的值对于 CI 场景很有用，可以快速失败并保存后来会被阻塞的构建 `conan upload`。
- 使用本地提交构建的包如果尝试使用 `conan upload` 上传到服务器将会失败，因为这些本地提交不在服务器上，然后包可能无法重现。通过设置 `core.scm:local_url=allow` 可以避免这个上传错误。
- 如果仓库不是脏的，并且提交存在于服务器上，它将返回远程 URL 和提交。

## 凭证管理

在上面的示例中，不需要凭证，因为本地仓库不需要它们。但在现实场景中，凭证可能是必需的。

首先重要的是，`git.get_url_and_commit()` 将捕获 `origin` 远程的 URL。这个 URL 不能编码令牌、用户名或密码，有以下几个原因。首先，这将使流程不可重复，不同的构建、不同的用户会得到不同的 URL，进而导致不同的配方修订版本。`url` 应始终保持不变。推荐的方法是采用正交的方式来管理凭证，例如使用 SSH 密钥。提供的示例包含 GitHub 动作，它执行了这种操作：

```{code-block} yaml
:caption: .github/workflows/hello-demo.yml

name: Build "hello" package capturing SCM in Github actions
run-name: ${{ github.actor }} checking hello-ci Git scm capture
on: [push]
jobs:
Build:
    runs-on: ubuntu-latest
    steps:
    - name: Check out repository code
        uses: actions/checkout@v3
        with:
        ssh-key: ${{ secrets.SSH_PRIVATE_KEY }}
    - uses: actions/setup-python@v4
        with:
        python-version: '3.10'
    - uses: webfactory/ssh-agent@v0.7.0
        with:
        ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
    - run: pip install conan
    - run: conan profile detect
    - run: conan create .
```

`hello-demo.yml` 负责以下内容：
- checkout `actions/checkout@v3` 操作会接收 `ssh-key` 以 `checkout` 为 `git@` 而不是 `https`
- `webfactory/ssh-agent@v0.7.0` 操作会确保在执行后续任务时 `ssh` 密钥也被激活，而不仅仅是在 `checkout` 时。
- 需要在 Github 界面中设置 `SSH_PRIVATE_KEY` 密钥，以及为仓库设置 `deploy key` （包含 `ssh` 密钥的私钥和公钥部分）

这样，可以完全将认证和凭证与配方功能分离，没有任何泄露凭证的风险。

```{admonition} 最佳实践
:class: tip

- 不要使用在 URL 中编码信息的认证机制。这是有风险的，容易在日志中泄露凭证。建议使用系统机制，如 SSH 密钥。
- 对于本地开发，不建议执行 `conan create` ，而是运行 `conan install` 并在本地构建，以避免过多的不必要提交。只有当本地一切正常时，才是开始检查 `conan create` 流程的时候。
```
