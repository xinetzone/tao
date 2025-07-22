# 在本地开发软件包

正如教程[前面的部分](https://docs.conan.io/2/tutorial/creating_packages.html#tutorial-creating-packages)所学的，在开发 Conan 软件包时最直接的方法是运行 `conan create`。这意味着每次运行时，Conan 都会在 Conan 缓存中执行一系列耗时的操作，例如下载、解压缩、复制源代码以及从头开始构建整个库。有时，特别是对于大型库，在开发配方时，这些操作无法每次都执行。

本节将首先展示 Conan 的本地开发流程，即在本地项目目录中直接处理软件包，而无需先将软件包内容导出到 Conan 缓存中。

还将介绍如何使用**可编辑模式**让其他软件包消费正在开发的软件包。

最后，将深入解释 Conan 包的布局。这是使其能够在 Conan 缓存或本地使用 Conan 包而不做任何更改的关键特性。

```{toctree}
local-package-dev-flow
editable-packages
package-layout
workspaces
```
