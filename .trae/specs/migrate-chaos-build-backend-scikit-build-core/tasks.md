# Tasks
- [x] Task 1: 梳理现有 PDM 后端配置与迁移映射
  - [x] SubTask 1.1: 记录当前 `[build-system]`、`[tool.pdm.version]`、`[tool.pdm.build]` 的功能含义
  - [x] SubTask 1.2: 确认项目是否存在主包 C/C++ 扩展、根级 CMake 配置和需要保留的包资源
  - [x] SubTask 1.3: 制定等价的 `scikit-build-core` 配置映射
- [x] Task 2: 修改 `apps/chaos/pyproject.toml` 构建后端配置
  - [x] SubTask 2.1: 将 `[build-system]` 改为 `scikit_build_core.build`
  - [x] SubTask 2.2: 移除 PDM 后端专属配置项
  - [x] SubTask 2.3: 添加 `scikit-build-core` 的 wheel、sdist、源码布局与动态版本配置
- [x] Task 3: 更新相关构建说明
  - [x] SubTask 3.1: 搜索现有构建文档或 CI 中关于 PDM backend 的说明
  - [x] SubTask 3.2: 仅在已有文档存在相关内容时更新为 `scikit-build-core` 说明
- [x] Task 4: 验证构建、安装、打包与产物一致性
  - [x] SubTask 4.1: 执行本地构建测试并记录结果
  - [x] SubTask 4.2: 执行依赖安装测试并记录结果
  - [x] SubTask 4.3: 执行生产环境打包测试并记录结果
  - [x] SubTask 4.4: 对比迁移前后 wheel/sdist 的关键内容与元数据
  - [x] SubTask 4.5: 执行项目 Python 标准 lint / format / test 验证，必要时说明降级原因

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 2 and Task 3