```{include} ../README.md
:end-before: <!-- end-doc-include -->
```

> **补充参考**：`.qoder/repowiki/` 目录下提供了一份自动生成的模块详细文档（约 50 个 Markdown 文件），涵盖认证授权、配置中心、邮件服务、文件存储、OAuth 集成、任务队列、数据分析、多智能体等各模块的 API 参考与系统说明。本 `doc/` 目录下的手写文档侧重于开发指南与架构概述，两者互补；如需深入了解各模块实现细节，可查阅 `.qoder/repowiki/zh/content/`。

```{toctree}
:maxdepth: 2
:caption: 用户指南
:hidden:

user_guide/python_environment
user_guide/commands
user_guide/environment_variables
user_guide/symphony_tutorial
```

```{toctree}
:maxdepth: 2
:caption: 开发者指南
:hidden:

developer_guide/coding_standards
developer_guide/testing
developer_guide/best_practices
developer_guide/project_experience
developer_guide/qoder_rules
```

```{toctree}
:maxdepth: 2
:caption: 架构与设计
:hidden:

architecture/architecture
architecture/directory_structure
```

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
