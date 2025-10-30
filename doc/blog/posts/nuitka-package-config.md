---
blogpost: true
date: Oct 31, 2025
author: xinetzone
location: World
category: 教程
tags: Nuitka
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
