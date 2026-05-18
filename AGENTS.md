# AGENTS.md

> **注意**：本文档已拆分至多个独立文档中，以提高可维护性和可读性。请查看以下文档获取详细信息。

## 文档导航

- [README.md](README.md) - 项目概述与快速开始
- [Python 环境](doc/user_guide/python_environment.md) - Python 环境与 3.14 新特性
- [常用命令](doc/user_guide/commands.md) - 常用命令
- [架构说明](doc/architecture/architecture.md) - 架构说明
- [API 参考](doc/api_reference/api_reference.md) - API 参考与文档整合原则
- [编码规范](doc/developer_guide/coding_standards.md) - 编码规范
- [环境变量](doc/user_guide/environment_variables.md) - 环境变量
- [最佳实践](doc/developer_guide/best_practices.md) - 最佳实践
- [项目经验总结](doc/developer_guide/project_experience.md) - 项目经验总结
- [Qoder 规范](doc/developer_guide/qoder_rules.md) - Qoder 规范
- [测试指南](doc/developer_guide/testing.md) - 测试命令、规范与策略
- [目录结构](doc/architecture/directory_structure.md) - 项目目录结构规范

## 核心功能速览

`taolib` 是一个 Python 库（Python >= 3.13），核心功能列表详见 [README.md](README.md#核心功能)。

核心设计理念：最小化核心依赖（`dependencies = []`），通过可选依赖组提供扩展功能。
