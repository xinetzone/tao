# 项目全面复盘与去重优化 Spec

## Why
项目中存在大量代码、配置及文档中的重复内容，降低了可维护性和开发效率。这些重复源于多轮迭代中信息的多次复制、配置文件的分散定义以及设计文档与用户文档之间的边界模糊。需要系统性识别并消除这些冗余，提升项目整体质量。

## What Changes
- 消除 `pytest.ini` 与 `pyproject.toml` 中 pytest 配置的重复定义（**BREAKING**：删除 `pytest.ini`）
- 统一各配置文件中 Python 版本要求的表述
- 精简 `AGENTS.md` 与 `README.md` 中重复的核心功能列表
- 整合 `specs/` 与 `.trae/specs/` 两个规格文档目录
- 评估 `reports/` 目录的保留必要性
- 清理 `.qoder/repowiki/` 与 `doc/` 目录之间的重叠内容
- 合并分散的脚本目录

## Impact
- 受影响的规格：无（新规格）
- 受影响的代码：根目录配置文件、doc/ 目录、reports/ 目录、specs/ 目录、.qoder/repowiki/ 目录
- **排除范围**：`s:\DevStack\flexloop\src` 目录及其所有子目录不受任何修改

---

## ADDED Requirements

### Requirement: 单源配置原则
所有测试配置 SHALL 仅在一处定义，避免多文件覆盖导致的不一致问题。

#### Scenario: pytest 配置统一
- **WHEN** 维护者修改测试配置
- **THEN** 只需修改 `pyproject.toml` 中的 `[tool.pytest.ini_options]` 段
- **AND** 不存在独立的 `pytest.ini` 文件覆盖该配置

### Requirement: Python 版本声明一致性
项目各文件中对 Python 版本的要求 SHALL 保持一致，以 `pyproject.toml` 中的 `requires-python` 为单一权威来源。

#### Scenario: 版本号不匹配检测
- **WHEN** 扫描项目配置文件
- **THEN** `README.md` 安装说明、`AGENTS.md` 速览描述、`.readthedocs.yml`、`.mise.toml` 中的 Python 版本应一致
- **AND** 如存在差异，以 `pyproject.toml` 为准进行修正

### Requirement: 文档核心内容单源化
核心功能列表 SHALL 仅在一份文档中详细定义，其余文档通过引用或摘要形式指向主文档。

#### Scenario: 核心功能列表去重
- **WHEN** 开发者查看 `AGENTS.md`
- **THEN** 其核心功能速览部分不应与 `README.md` 核心功能部分逐字重复
- **AND** 应通过引用链接指向主文档，或提供差异化的摘要视图

### Requirement: 规格文档目录统一
所有技术规格和设计文档 SHALL 集中存放在 `.trae/specs/` 目录下，`specs/` 根目录不再存放设计文档。

#### Scenario: 设计文档集中管理
- **WHEN** 查找 Symphony 相关设计文档
- **THEN** 所有设计规格应在 `.trae/specs/` 下找到
- **AND** `specs/` 目录下的原始设计草案应与 `.trae/specs/` 中的对应内容完成整合

### Requirement: 分析报告归档规范
一次性生成的分析报告 SHALL 归类存放，避免与持续维护的文档混淆。

#### Scenario: 报告与文档分离
- **WHEN** 开发者浏览项目文档
- **THEN** `reports/` 目录应仅包含时效性的一次性报告
- **AND** 报告中的改进建议如已实施，应体现在 `doc/` 或 `.trae/specs/` 中

### Requirement: 脚本目录精简
项目级工具脚本 SHALL 统一存放，消除功能重叠的脚本目录。

#### Scenario: 脚本目录合并
- **WHEN** 需要查找或运行项目脚本
- **THEN** 所有辅助脚本集中在 `scripts/` 目录下
- **AND** 不存在散布在 `doc/scripts/` 或 `.agents/skills/` 中的等价脚本

### Requirement: .qoder 自动生成文档与手写文档的边界清晰化
`.qoder/repowiki/` 目录 SHALL 仅包含自动生成内容，不应与 `doc/` 目录下手写文档形成事实上的重复。

#### Scenario: qoder 文档与手写文档不重叠
- **WHEN** 维护者更新 `doc/` 下的手写文档
- **THEN** `.qoder/repowiki/` 中的自动生成内容不应因手写文档更新而出现内容冲突
- **AND** 如 qoder 生成的文档已有完整描述，doc/ 下的手写文档应简化为索引/导航

---

## MODIFIED Requirements

### Requirement: README.md 安装说明 Python 版本修正
**原内容**：安装说明中写 "Python >= 3.10"，与 pyproject.toml 中 `requires-python = ">=3.13"` 不一致。
**修正后**：安装说明中的 Python 版本要求应与 `pyproject.toml` 一致。

#### Scenario: README 安装说明版本一致
- **WHEN** 用户阅读 README 安装说明
- **THEN** Python 版本要求与 `pyproject.toml` 中的 `requires-python` 字段一致

---

## REMOVED Requirements

### Requirement: 独立 pytest.ini 配置
**Reason**：与 `pyproject.toml` 中 `[tool.pytest.ini_options]` 段形成配置重复，且 `pytest.ini` 优先级更高会完全覆盖 `pyproject.toml` 设置，已在 `reports/TEST_REPORT.md` 中明确建议删除。
**Migration**：将 `pytest.ini` 中独有的 `markers` 配置和 `asyncio_mode` 合并到 `pyproject.toml` 的 `[tool.pytest.ini_options]` 段，然后删除 `pytest.ini`。

### Requirement: specs/ 根目录设计文档
**Reason**：`specs/` 下的 `SPEC.md`、`symphony-design.md`、`symphony-elixir-experience.md` 与 `.trae/specs/multi_agent_system/` 中的内容存在重叠，两个规格目录造成维护混乱。
**Migration**：将 `specs/` 下的设计文档移动到 `.trae/specs/multi_agent_system/` 目录下作为参考资料，原 `specs/` 目录仅保留或删除。
