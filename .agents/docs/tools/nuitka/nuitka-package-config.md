---
blogpost: true
date: Oct 31, 2025
author: flexloop
location: World
category: tool
tags: Nuitka, 教程
language: Chinese
---
# Nuitka 的包配置系统

我们来一起用华罗庚先生提出的“统筹方法”来探索 [Nuitka 包配置](https://nuitka.net/user-documentation/nuitka-package-config.html)的学习路径。华罗庚的学习法强调：

- **抓住关键**：找准问题的核心，集中突破；
- **化繁为简**：通过归纳、类比、抽象，把复杂问题简化；
- **由浅入深**：从基础出发，逐步深入；
- **举一反三**：学会迁移和类推，形成系统思维。

我们可以把 Nuitka 包配置的内容分成几个“关键点”，逐步探索：

## 探索 Nuitka 包配置的学习路径

### 👉第一步：抓住核心问题 —— Nuitka 为什么需要包配置？

Nuitka 是一个将 Python 代码编译为 C/C++ 的编译器，最终生成可执行文件。这种编译方式带来了性能提升和部署便利，但也引发了一些兼容性挑战，尤其是对第三方包的支持。下面列出几个关键问题：

- **依赖 DLL 或数据文件**：某些 Python 包（如图像处理、科学计算类库）依赖外部 DLL 或数据文件。如果这些文件在编译后未被正确包含，程序运行时就会报错。
- **隐式导入**：有些包在运行时动态导入模块（如通过 `__import__` 或插件机制），这些模块在静态分析时可能被遗漏，导致编译后的程序缺少必要组件。
- **依赖膨胀**：某些模块会引入大量不必要的依赖，增加编译体积，影响性能。
- **平台或 Python 版本差异**：不同操作系统或 Python 版本下，某些模块行为不同，可能需要特殊处理。

```{admonition} 思考
你觉得这些问题中，哪个最值得先解决？
```

### 👉第二步：化繁为简 —— 用 YAML 文件统一管理

Nuitka 用 `.nuitka-package.config.yml` 文件来集中管理这些问题。每个模块的配置都可以写成类似这样：

```yaml
# yamllint disable rule:line-length
# yamllint disable rule:indentation
# yamllint disable rule:comments-indentation
# too many spelling things, spell-checker: disable
---
- module-name: 'pandas._libs' # 解决 pandas._libs 模块的依赖问题
  implicit-imports:
    - depends:
      - 'pandas._libs.tslibs.np_datetime'
      - 'pandas._libs.tslibs.nattype'
```

这就是“统筹方法”的体现：把分散的问题集中处理，用统一格式解决不同类型的兼容问题。

````{note}
在文件的开头，您会发现以下几行，您可以忽略它们，它们基本上只是为了让检查器忽略那些难以避免的问题。
```yaml
# yamllint disable rule:line-length
# yamllint disable rule:indentation
# yamllint disable rule:comments-indentation
# too many spelling things, spell-checker: disable
---
```
````

```{admonition} 思考
你能看出这个配置解决了什么问题吗？
```

### 👉第三步：由浅入深 —— 分类学习配置项

可以把配置项分成几类，逐个突破：

| 配置项类型         | 作用说明                     |
|------------------|----------------------------|
| data-files       | 指定要复制的文件或目录         |
| dlls             | 指定要包含的 DLL 文件         |
| implicit-imports | 指定模块的隐式依赖             |
| anti-bloat       | 去除不必要的代码或依赖         |
| options          | 设置模块运行所需的选项         |
| import-hacks     | 处理特殊导入行为               |

```{admonition} 思考
你想先从哪一类开始深入？

后续内容逐步分析每个字段的含义和用法。
```

### 👉第四步：举一反三 —— 自定义配置与贡献

你可以写自己的配置文件并通过 `--user-package-configuration-file=xxx.yml` 使用它。如果你发现某个包的通用解决方案，也可以提交 PR 贡献给 Nuitka 社区。

## 🧱 `data-files` 字段结构解析

`data-files` 字段用于告诉 Nuitka 在编译时将哪些数据文件复制到最终的输出目录中。它支持以下几种配置方式：

| 字段名 | 作用 |
|--------|------|
| `dest_path` | 指定目标路径，默认是当前模块目录（`.`） |
| `dirs` | 要复制的整个目录列表 |
| `patterns` | 要匹配的文件名或通配符（如 `*.dat`） |
| `empty_dirs` | 要创建的空目录列表 |
| `empty_dir_structures` | 要创建的空目录结构（用于更复杂的场景） |
| `when` | 条件表达式，控制在哪些平台或模式下启用（如 `win32`） |

---

### 📦 示例解析与应用场景

#### ✅ 示例 1：复制一个数据目录

```yaml
- module-name: 'customtkinter'
  data-files:
    dirs:
      - 'assets'
```

```{admonition} 📌 应用场景
你的包中有一个 `assets` 文件夹，里面包含图标、样式等资源。这个配置会将整个目录复制到编译后的输出中。
```

#### ✅ 示例 2：复制架构相关的目录（但有局限）

```yaml
- module-name: 'tkinterweb'
  data-files:
    dirs:
      - 'tkhtml'
```

```{admonition} 📌 应用场景
你需要将 `tkhtml` 文件夹打包进去，但注意：如果文件内容依赖架构（如 32 位或 64 位），这种方式可能不够精确。
```

#### ✅ 示例 3：创建空目录

```yaml
- module-name: 'Crypto.Util._raw_api'
  data-files:
    empty_dirs:
      - '.'
```

```{admonition} 📌 应用场景
某些包运行时会通过 `__file__` 推导目录路径，如果目录不存在就会报错。这个配置确保目录存在，即使里面没有文件。
```

### 🧠 小练习：你来判断

假设你正在编译使用 `transformers` 的项目，它需要：

- 加载一个模型文件 `bert-base.bin`（位于 `models/` 目录）
- 读取一个配置文件 `config.json`（位于 `configs/` 目录）
- 创建一个空目录 `cache/` 用于运行时缓存

👉 请你试着写出一个 `data-files` 配置片段，包含这三项需求。你可以先写出一部分，我来帮你检查和补充。准备好了吗？

````{dropdown} 点击查看解析
```yaml
- module-name: 'transformers'
  data-files:
    dirs:
      - 'models'
      - 'configs'
    empty_dirs:
      - 'cache'
```

```{admonition} ✅ 配置解析

- `module-name: 'transformers'`  
  👉 表示这个配置是针对 `transformers` 包的。

- `dirs: ['models', 'configs']`  
  👉 Nuitka 会将这两个目录中的所有内容复制到编译后的输出目录中。适用于模型文件（如 `.bin`）和配置文件（如 `.json`）。

- `empty_dirs: ['cache']`  
  👉 Nuitka 会创建一个名为 `cache` 的空目录，确保运行时不会因为目录缺失而报错。
```
````

```{admonition} 🧠 延伸思考：是否需要 dest_path

如果你没有写 `dest_path`，这其实是个好习惯！因为：

- 默认目标路径是 `.`，即相对于包目录。
- 只有在某些特殊情况下（比如包运行时硬编码了某个路径），才需要手动指定 `dest_path`。
```

## `dlls`

👉 有些模块在运行时动态加载 DLL 文件，而不是通过扩展模块（如 `.pyd`）静态链接。这种情况下，Nuitka 无法自动检测这些 DLL，因此你必须在配置文件中**显式指定**它们。

存在两种方式来指定 DLLs：

### ✅ 方式一：`from_filenames`（推荐方式）

```yaml
dlls:
  - from_filenames:
      relative_path: 'dlls'
      prefixes:
        - 'dll1'
        - 'mydll*'
      suffixes:
        - 'pyd'
    dest_path: 'output_dir'
    when: 'win32'
```

- `relative_path`: DLL 所在目录，相对于模块路径。
- `prefixes`: DLL 文件名前缀，可以用通配符。
- `suffixes`: 文件后缀（如 `.dll`, `.pyd`），用于精确匹配。
- `dest_path`: DLL 复制到的目标目录。
- `when`: 条件表达式，控制在哪些平台或架构下启用。

📎这种方式是**推荐的**，因为它更稳定、易维护。

### ⚠️ 方式二：`by_code`（实验性）

```yaml
dlls:
  - by_code:
      setup_code: ''
      filename_code: ''
    dest_path: 'output_dir'
    when: 'linux'
```

- `setup_code`: 编译前执行的准备代码。
- `filename_code`: 生成 DLL 文件名的代码。

📎 这种方式依赖编译时执行代码，容易出错，目前仍在改进中。

你贴出的内容是 Nuitka 包配置文档中关于 DLL 文件处理的三个典型示例，我们来逐个解释它们的结构和用途，并结合页面内容理解它们背后的设计思路。

---

### 🧩 DLL 配置示例详解

#### ✅ 示例 1：最简单的情况 —— 直接从包目录复制 DLL

```yaml
- module-name: 'vosk'
  dlls:
    - from_filenames:
        prefixes:
          - 'libvosk'
```

📌 说明：
- `vosk` 包中包含名为 `libvosk*.dll` 的文件。
- Nuitka 会在该模块目录下查找以 `libvosk` 开头的 DLL 文件并打包进去。
- 没有指定 `relative_path`，默认就是模块目录。

📎 这是最常见、最推荐的方式，简单且稳定。


#### ✅ 示例 2：架构相关的 DLL 文件在子目录中

```yaml
- module-name: 'tkinterweb'
  dlls:
    - from_filenames:
        relative_path: 'tkhtml/Windows/32-bit'
        prefixes:
          - 'Tkhtml'
      when: 'win32 and arch_x86'
    - from_filenames:
        relative_path: 'tkhtml/Windows/64-bit'
        prefixes:
          - 'Tkhtml'
      when: 'win32 and arch_amd64'
```

📌 说明：
- `tkinterweb` 包的 DLL 文件根据架构（32位或64位）存放在不同子目录中。
- 使用 `relative_path` 指定子目录路径。
- 使用 `when` 条件表达式确保只在对应平台和架构下启用。

📎这种方式适用于架构敏感的 DLL 文件，避免错误打包。

---

#### ✅ 示例 3：根据平台选择不同后缀的 DLL 文件

```yaml
- module-name: 'tls_client.cffi'
  dlls:
    - from_filenames:
        relative_path: 'dependencies'
        prefixes:
          - 'tls-client'
        suffixes:
          - 'dll'
      when: 'win32'
    - from_filenames:
        relative_path: 'dependencies'
        prefixes:
          - 'tls-client'
        suffixes:
          - 'so'
      when: 'linux'
    - from_filenames:
        relative_path: 'dependencies'
        prefixes:
          - 'tls-client'
        suffixes:
          - 'dylib'
      when: 'macos'
```

📌 说明：
- `tls_client.cffi` 包在不同平台使用不同后缀的动态库文件。
- 所有 DLL 都在同一个目录 `dependencies` 中。
- 使用 `suffixes` 区分平台专属文件类型（Windows 用 `.dll`，Linux 用 `.so`，macOS 用 `.dylib`）。
- 使用 `when` 精准控制平台条件。

📎 这种方式可以避免打包多个平台的 DLL 文件，确保只包含当前平台所需的内容。

#### 🧠 总结

这些示例体现了 Nuitka 的 DLL 配置设计原则：

- **精确匹配**：通过 `prefixes` 和 `suffixes` 控制文件名。
- **路径控制**：通过 `relative_path` 指定 DLL 所在目录。
- **平台适配**：通过 `when` 条件表达式实现跨平台兼容。
- **推荐方式**：页面明确建议使用 `from_filenames`，而不是 `by_code`，因为前者更稳定、易维护。

这段话出现在你正在浏览的 Nuitka 包配置文档中，属于对 **EXEs 配置项**的说明。它解释了 Nuitka 如何处理可执行文件（EXE）与 DLL 文件的关系，并提供了配置方法。我们来逐句拆解，并结合页面内容深入理解它的含义。

## ✅EXE 配置

```yaml
dlls:
  - from_filenames:
      prefixes:
        - 'subprocess'
      executable: 'yes'
  - from_filenames:
      prefixes:
        - ''  # first match decides
```

✅ 第一项：
- `prefixes: ['subprocess']`：表示查找以 `subprocess` 开头的文件。
- `executable: 'yes'`：告诉 Nuitka，这个文件是一个 EXE，而不是普通 DLL。

⚠️ 第二项：
- `prefixes: ['']`：空前缀表示匹配第一个找到的文件。

🧠 总结：
- Nuitka 把 EXE 文件当作特殊的 DLL 文件处理。
- 默认 DLL 是不可执行的，只有加上 `executable: yes` 才会被当作 EXE。
- 这种设计让 DLL 和 EXE 的配置方式保持一致，简化了打包逻辑。

## 🧹 Anti-Bloat：去除不必要的依赖或代码

👉 如果你想在编译时修改某些模块的代码，比如去掉测试代码、日志模块或不必要的依赖，可以使用 `anti-bloat` 配置项。

字段功能如下：

| 字段名 | 作用 |
|--------|------|
| `description` | 描述这个去膨胀操作的目的 |
| `context` | 指定在哪个上下文中应用（通常为空） |
| `module_code` | 替换整个模块的代码 |
| `replacements_plain` | 用字符串替换方式修改代码 |
| `replacements_re` | 用正则表达式替换代码 |
| `replacements` | 用表达式替换代码 |
| `change_function` | 替换某个函数的定义，如设为 `un-callable` |
| `append_result` / `append_plain` | 向模块追加代码 |
| `when` | 条件表达式，控制在哪些平台或版本下启用

📎这种方式可以用来**精简打包体积、避免不必要的依赖**，尤其适用于大型包如 `matplotlib`、`scipy`。

### 🧠 示例分析

```yaml
- description: 'remove tests'
  module_code: 'from hello import world'
  change_function:
    'get_extension': 'un-callable'
```

📌 说明：
- 将整个模块替换为一行代码 `from hello import world`。
- 把 `get_extension` 函数设为不可调用（`un-callable`），防止它被执行。

## 🔍 Implicit-Imports：处理动态导入的模块

👉 有些包在运行时动态导入模块（比如插件机制），Nuitka 静态分析时无法识别这些依赖。你可以用 `implicit-imports` 显式声明它们。

字段功能如下：

| 字段名 | 作用 |
|--------|------|
| `depends` | 指定该模块依赖的其他模块 |
| `pre-import-code` / `post-import-code` | 在导入前后执行的代码 |
| `no-auto-follow` | 告诉 Nuitka 不要自动跟踪某些导入 |
| `when` | 条件表达式，控制在哪些平台或版本下启用

### 🧠 示例分析

#### ✅ `cv2` 的隐式依赖：

```yaml
- module-name: 'cv2'
  depends:
    - 'cv2.cv2'
    - 'numpy'
    - 'numpy.core'
  pre-import-code:
    - |
      import os
      os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(os.path.dirname(__file__), 'qt/plugins')
      os.environ['QT_QPA_FONTDIR'] = os.path.join(os.path.dirname(__file__), 'qt/fonts')
  when: 'linux and standalone'
```

📌 说明：
- 显式声明 `cv2` 依赖的模块。
- 在导入前设置环境变量，确保 Qt 插件和字体路径正确。

#### ✅ `tqdm.std` 的去膨胀配置：

```yaml
- module-name: 'tqdm.std'
  anti-bloat:
    - no-auto-follow:
        'pandas': 'ignore'
```

📌 说明：
- `tqdm` 会尝试注册 `pandas` 的方法，但如果 `pandas` 没有安装也不会报错。
- 所以可以告诉 Nuitka：**不要因为 `tqdm` 导入了 `pandas` 就自动打包 `pandas`**。

你贴出的内容来自 Nuitka 包配置文档的两个部分：**Options（选项提示）** 和 **Import-Hacks（导入黑科技）**。我们来逐句解释它们的含义，并结合页面内容理解它们在实际打包过程中的作用。

---

## ⚙️ Options：模块运行所需的编译选项提示

👉 如果某个模块在特定平台或模式下需要特定的编译选项（比如必须启用 GUI 模式或打包为 macOS bundle），你可以在这里声明这些要求。Nuitka 会在编译时发出提示或警告，帮助用户避免运行时崩溃。

---

### 🧰 示例解析

```yaml
- module-name: 'wx'
  options:
    checks:
      - description: 'wx will crash in console mode during startup'
        console: 'yes'
        when: 'macos'
      - description: 'wx requires program to be in bundle form'
        macos_bundle: 'yes'
        when: 'macos'
```

📌 说明：
- `wx` 是一个 GUI 框架，在 macOS 上如果以控制台模式运行会直接崩溃。
- 所以配置中要求：
  - 必须启用 GUI 模式（`console: yes`）
  - 必须打包为 macOS bundle（`macos_bundle: yes`）

📎 这些配置不会自动修改编译行为，而是**提示用户**必须设置这些选项，否则程序可能无法运行。

---

### 🧠 字段功能总结

| 字段名 | 作用 |
|--------|------|
| `description` | 描述这个选项的目的 |
| `console` | 是否启用控制台窗口（yes/no/recommend） |
| `macos_bundle` | 是否打包为 macOS 应用（yes/no/recommend） |
| `macos_bundle_as_onefile` | 是否将 bundle 打包为单文件 |
| `support_info` | 提示级别（info/warning/error） |
| `when` | 条件表达式，控制在哪些平台或模式下启用 |

---

## 🧪 Import-Hacks：解决特殊导入行为

👉 有些包会在运行时修改 `sys.path`，或使用 Nuitka 无法静态分析的导入方式。你可以用 `import-hacks` 显式告诉 Nuitka 如何处理这些导入。

### 🧰 示例解析

```yaml
- module-name: 'tkinterweb'
  import-hacks:
    - global-sys-path:
        - ''
```

📌 说明：
- `tkinterweb` 包中有如下代码：
  ```python
  sys.path.append(os.path.dirname(os.path.realpath(__file__)))
  ```
- 这会把包目录加入全局导入路径，使得包内模块可以被绝对导入。
- Nuitka 编译时无法自动识别这种行为，所以需要通过 `global-sys-path` 显式声明：**将当前目录加入导入路径**。

📎这种 hack 很少见，但对某些包是必须的。

你贴出的内容来自 Nuitka 包配置文档的 **Variables（变量）** 和 **Constants（常量）** 部分，它们是 Nuitka 配置系统中非常强大的机制，用于在编译时动态获取包信息，并在配置中灵活使用。我们来逐句解析，并结合页面内容理解它们的作用和使用方式。

## 🧠 Variables：编译时动态获取信息

👉 你可以在配置文件中使用变量来获取包的运行信息，比如版本、模块属性等，并在 `when` 条件或其他字段中使用。

👉 所有变量都通过 `get_variable("变量名")` 来访问，Nuitka 会记录和缓存这些变量的使用情况。

### 🧰 示例解析

```yaml
variables:
  setup_code: 'import whatever'
  declarations:
    'variable1_name': 'whatever.something()'
    'variable2_name': 'whatever.something2()'
```

📌 说明：
- `setup_code`：在编译时执行一次，用于准备变量获取的上下文。
- `declarations`：定义变量名和对应的表达式。
- 使用方式：在其他配置字段中通过 `get_variable("variable1_name")` 引用。

## 🔒 Constants：跨平台或通用值的定义

👉 常量用于定义跨平台的值，比如路径后缀、平台标识等，避免在多个地方重复写 `when` 条件。

### 🧰 示例解析

#### ✅ 示例 1：定义平台后缀

```yaml
constants:
  - declarations:
      'suffix': '_Windows'
    when: "win32"
  - declarations:
      'suffix': '_Linux'
    when: "linux"
  - declarations:
      'suffix': '_MacOS'
    when: "macos"

implicit-imports:
  depends:
    - '"package_name_%s" % get_variable("suffix")'
```

📌 说明：
- 根据平台定义不同的后缀。
- 在 `depends` 中动态拼接模块名，实现平台适配。

---

#### ✅ 示例 2：Torch 包的模块筛选

```yaml
constants:
  declarations:
    'torch_config_module_candidates': '[m for m in iterate_modules("torch") if m.split(".")[-1] in ("config", "_config")]'

variables:
  setup_code: 'import importlib'
  declarations:
    'torch_config_modules': 'dict((m,importlib.import_module(m)._compile_ignored_keys) for m in torch_config_module_candidates if hasattr(importlib.import_module(m), "_compile_ignored_keys"))'
```

📌 说明：
- 使用 `iterate_modules("torch")` 获取所有子模块。
- 通过常量筛选出以 `.config` 或 `._config` 结尾的模块。
- 使用变量导入这些模块并提取 `_compile_ignored_keys` 属性。

你贴出的内容来自 Nuitka 包配置文档的“表达式与条件判断”部分，它详细介绍了如何在配置文件中使用布尔表达式、平台判断、版本检测等机制来控制配置项的启用。我们来逐步拆解，并结合页面内容理解它的用途和实际写法。

---

## 🧠 表达式（Expression）：控制配置启用的核心机制

### 📌 示例表达式

```yaml
when: "macos and python3_or_higher"
```

📌 含义：
- 仅当当前操作系统是 macOS 且 Python 版本为 3 或更高时，才启用该配置项。
- 这是 Nuitka 配置中最常见的条件控制方式，适用于 `data-files`、`dlls`、`anti-bloat`、`options` 等字段。

---

## 🧩 可用变量分类

### ✅ 操作系统判断（OS Indications）

| 变量名 | 含义 |
|--------|------|
| `macos` | 当前平台是 macOS |
| `win32` | 当前平台是 Windows |
| `linux` | 当前平台是 Linux |

---

### ✅ 编译模式判断（Compilation Modes）

| 变量名 | 含义 |
|--------|------|
| `standalone` | 是否启用了独立打包模式（包括 onefile 和 app） |
| `onefile` | 是否启用了单文件打包模式 |
| `module_mode` | 是否启用了模块模式 |
| `deployment` | 是否启用了部署模式 |
| `onefile_cached` | 是否启用了 onefile 缓存机制 |

📎 大多数配置是针对 `standalone` 模式的，`onefile` 只在特殊情况下使用。

---

### ✅ Python 版本判断（Python Versions）

| 变量名 | 含义 |
|--------|------|
| `before_python3` | 是否是 Python 2 |
| `python3_or_higher` | 是否是 Python 3 或更高版本 |
| `python310_or_higher` | 是否是 Python 3.10 或更高版本 |
| `before_python310` | 是否是 Python 3.10 之前的版本 |

---

### ✅ Python 发行版判断（Python Flavors）

| 变量名 | 含义 |
|--------|------|
| `anaconda` | 是否是 Anaconda Python（不建议直接使用） |
| `debian_python` | 是否是 Debian 系统自带的 Python |

📎 建议：使用 `is_conda_package("包名")` 来判断某个包是否来自 conda，而不是判断整个 Python 环境。

---

### ✅ 包版本判断（Package Versions）

```yaml
version("rich") is not None and version("rich") >= (10, 2, 2)
```

📌 含义：
- 如果 `rich` 包已安装，且版本不低于 10.2.2，则启用该配置。

---

### ✅ Anti-Bloat 插件变量

| 变量名 | 含义 |
|--------|------|
| `use_setuptools` | 是否启用了 setuptools |
| `use_pytest` | 是否启用了 pytest |
| `use_unittest` | 是否启用了 unittest |
| `use_ipython` | 是否启用了 IPython |
| `use_dask` | 是否启用了 dask |

📎 这些变量主要用于 `anti-bloat` 配置，但也可以在其他地方使用。

---

### ✅ 其他辅助函数

- `get_variable("变量名")`：用于访问在 `variables` 中定义的变量。
- `experimental("flag-name")`：用于判断是否启用了某个实验性功能。
- `iterate_modules("包名")`：列出某个包下的所有子模块。

---

### ✅ 总结

- Nuitka 的配置系统支持丰富的条件表达式，帮助你根据平台、版本、模式等动态启用配置。
- 所有表达式都写在 `when:` 字段中，语法接近 Python 的布尔表达式。
- 页面强调：这些表达式不需要执行实际代码，只是用于条件判断，**安全且高效**。
