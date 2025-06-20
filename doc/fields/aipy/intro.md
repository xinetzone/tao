# AiPy 简介

[爱派(AiPy)](https://www.aipyaipy.com/) —— 您的智能自动化助手，专注实现三大核心场景：智能创收、效率优化和智能匹配。基于LLM+Python技术生态，提供开放源码的本地化部署方案，实现对各类应用的自动化控制与智能决策。

爱派(AiPy)，用 Python Use，给 AI 装上双手，开放源码、本地部署，除了帮你思考，更能帮你干活，成为您的超级人工智能助手！从此，你只要说出你的想法，爱派帮你分析本地数据，操作本地应用，给你最终结果！

## 下载&安装

命令行安装 (Windows/macOS/Linux)：

```bash
pip install aipyapp
```

环境要求
1. python 版本≥3.9
2. 兼容 Windows、macOS、Linux 等
3. AiPy 开源地址：[GitHub](https://github.com/knownsec/aipyapp)

接下来输入 `aipy` 启动：

```bash
aipy
```

## 新范式 Python-use = LLM + Python Interpreter

Python-Use 是一种面向任务结果的新型智能执行范式，它通过将大模型与 Python 解释器深度结合，构建起“任务 -> 计划 -> 代码 -> 执行 -> 反馈”的完整闭环流程。

这使得模型具备两大关键能力：

- **API Calling**：模型自动编写并执行 Python 代码调用 API，实现服务间互通；
- **Packages Calling**：模型自主选择并调用 Python 生态中的丰富库，实现通用任务编排。

用户只需提供简单的 API Key 或任务描述，模型即可自动完成整个流程，无需工具链配置或插件接入，彻底摆脱传统 Workflow 与 Function Calling 的繁琐。

特别强调：**Python-Use 并不是一个“代码生成工具”或“智能 IDE”**，而是一个任务驱动、结果导向的 AI Agent。

对用户而言，Python-Use 就是一个“描述任务 → 自动完成 → 直接返回结果”的智能体系统：

- 用户无需掌握任何编程知识；
- 模型会自动完成理解、规划、编程、调试与结果生成；
- 自动修复 bug，持续优化方案，保障任务高质量完成。

代码只是模型实现目标的手段，最终交付的是任务完成的结果，而非中间的代码过程。

Python-use 范式还意味着：

- **No MCP**：无需统一协议，代码即协议、代码即标准；
- **No Workflow**：无需预设流程，模型自主规划执行；
- **No Tools**：不再依赖插件注册，模型直接调用生态工具；
- **No Agents**：无需外部代理，模型通过代码直接完成任务。

它真正建立起 LLM 与真实环境的通用通信桥梁，释放出模型的执行力与行动潜能。

## 统一入口：No Clients, Only AiPy

AI 执行不再需要繁杂客户端与套壳应用，用户只需运行一个 Python 环境：**AiPy**。

- **统一终端**：所有交互归于 Python 解释器
- **极简路径**：无需安装多个 Agent 或插件，入口统一、体验一致
- **AiPy**：https://www.aipy.app/

## 模式升级：AI ThinkDo = 真正的知行合一

- **任务**：用户用自然语言表达意图；
- **计划**：模型自动分解并规划执行路径；
- **代码**：生成最优 Python 方案；
- **执行**：直接与真实环境交互并完成动作；
- **反馈**：获取结果、分析偏差、自动调整。

模型具备从认知到行动、从计划到反思的全流程能力，不再依赖外部 Agent，真正释放 AI 自主行动力。

Python use (aipython) 是一个集成 LLM 的 Python 命令行解释器。你可以：
- 像往常一样输入和执行 Python 命令
- 用自然语言描述你的需求，aipython 会自动生成 Python 命令，然后执行

而且，两种模式可以互相访问数据。例如，aipython 处理完你的自然语言命令后，你可以用标准 Python 命令查看各种数据。

## Interfaces
### ai 对象
- \_\_call\_\_(instruction): 执行自动处理循环，直到 LLM 不再返回代码消息
- save(path): 保存交互过程到 svg 或 html 文件
- llm 属性： LLM 对象
- runner 属性： Runner 对象

### LLM 对象
- history 属性： 用户和LLL交互过程的消息历史

### Runner 对象
- globals: 执行 LLM 返回代码的 Python 环境全局变量
- locals: 执行 LLM 返回代码的 Python 环境局部变量

### runtime 对象
供 LLM 生成的代码调用，提供以下接口：
- install_packages(packages): 申请安装第三方包
- getenv(name, desc=None): 获取环境变量
- display(path=None, url=None): 在终端显示图片

## Usage
AIPython 有两种运行模式：
- 任务模式：非常简单易用，直接输入你的任务即可，适合不熟悉 Python 的用户。
- Python模式：适合熟悉 Python 的用户，既可以输入任务也可以输入 Python 命令，适合高级用户。

默认运行模式是任务模式，可以通过 `--python` 参数切换到 Python 模式。

### 任务模式
`uv run aipython`

```
>>> 获取Reddit r/LocalLLaMA 最新帖子
......
......
>>> /done
```

`pip install aipyapp` ，运行aipy命令进入任务模式

```
-> % aipy
🚀 Python use - AIPython (0.1.22) [https://aipy.app]
请输入需要 AI 处理的任务 (输入 /use <下述 LLM> 切换)
>> 获取Reddit r/LocalLLaMA 最新帖子
......
>>
```

### Python 模式

#### 基本用法
自动任务处理：

```
>>> ai("获取Google官网首页标题")
```

#### 自动申请安装第三方库
```
Python use - AIPython (Quit with 'exit()')
>>> ai("使用psutil列出当前MacOS所有进程列表")

📦 LLM 申请安装第三方包: ['psutil']
如果同意且已安装，请输入 'y [y/n] (n): y

```

## TODO
- 使用 AST 自动检测和修复 LLM 返回的 Python 代码

## Thanks
- 黑哥: 产品经理/资深用户/首席测试官
- Sonnet 3.7: 生成了第一版的代码，几乎无需修改就能使用。
- ChatGPT: 提供了很多建议和代码片段，特别是命令行接口。
- Codeium: 代码智能补齐
- Copilot: 代码改进建议和翻译 README



