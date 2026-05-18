# 任务列表

## 阶段一：配置去重与统一

- [x] Task 1: 合并 pytest 配置并删除 pytest.ini
  - **Priority**: P0
  - **Depends On**: 无
  - **Description**: 
    - 将 `pytest.ini` 中的 `markers` 配置迁移到 `pyproject.toml` 的 `[tool.pytest.ini_options]` 段
    - 验证 `pyproject.toml` 已包含 `asyncio_mode = "auto"`（已在 `[tool.pytest.ini_options]` 中）
    - 删除 `pytest.ini` 文件
  - **Acceptance Criteria Addressed**: 单源配置原则
  - **Notes**: `reports/TEST_REPORT.md` 已明确指出此配置冲突问题

- [x] Task 2: 统一 Python 版本声明
  - **Priority**: P0
  - **Depends On**: 无
  - **Description**:
    - 修正 `README.md` 安装说明中的 Python 版本要求（当前为 `>= 3.10`，应改为与 `pyproject.toml` 一致的 `>= 3.13`）
    - 审视 `AGENTS.md` 中的 Python 版本描述（当前 `>= 3.14`），与 `pyproject.toml` 对齐
    - 确认 `.readthedocs.yml` 和 `.mise.toml` 中的版本一致性
  - **Acceptance Criteria Addressed**: Python 版本声明一致性
  - **Notes**: `pyproject.toml` 的 `requires-python = ">=3.13"` 为权威来源

## 阶段二：文档去重

- [x] Task 3: 精简 AGENTS.md 核心功能速览
  - **Priority**: P1
  - **Depends On**: 无
  - **Description**:
    - `AGENTS.md` 的"核心功能速览"段落与 `README.md` 的"核心功能"段落完全逐字重复
    - 将 `AGENTS.md` 中的核心功能列表替换为指向 `README.md` 的引用链接
    - 或保留为简化列表（仅功能名，不重复详细描述），加上"详见 README.md"的指引
  - **Acceptance Criteria Addressed**: 文档核心内容单源化
  - **Notes**: `AGENTS.md` 主要面向 AI Agent，保留导航功能即可

- [x] Task 4: 评估 .qoder/repowiki 与 doc/ 的内容去重
  - **Priority**: P2
  - **Depends On**: Task 3
  - **Description**:
    - `.qoder/repowiki/` 包含约 50 个自动生成的 Markdown 文档，与 `doc/` 目录下的手写文档存在主题重叠
    - 分析 `.qoder/repowiki/zh/content/` 下的文档内容，识别与 `doc/` 的重复
    - 在 `doc/` 中添加说明，指引到 qoder 文档的查看方式
  - **Acceptance Criteria Addressed**: qoder 文档与手写文档边界清晰化
  - **Notes**: `.qoder/repowiki/` 的文档多为自动生成，不宜手动修改。重点在 `doc/` 中添加导航指引

## 阶段三：规格文档整合

- [x] Task 5: 整合 specs/ 目录到 .trae/specs/
  - **Priority**: P1
  - **Depends On**: 无
  - **Description**:
    - 将 `specs/SPEC.md` 移动到 `.trae/specs/multi_agent_system/` 作为 `symphony_spec_ref.md` 参考资料
    - 将 `specs/symphony-design.md` 移动到 `.trae/specs/multi_agent_system/` 作为 `symphony_design_detail.md`
    - 将 `specs/symphony-elixir-experience.md` 移动到 `.trae/specs/multi_agent_system/` 作为 `symphony_elixir_reference.md`
    - 删除空出的 `specs/` 目录
    - 更新 `.trae/specs/multi_agent_system/spec.md` 中的相关引用
  - **Acceptance Criteria Addressed**: 规格文档目录统一
  - **Notes**: 移动而非复制，确保 Git 历史可追踪

- [x] Task 6: 处理 reports/ 目录
  - **Priority**: P2
  - **Depends On**: 无
  - **Description**:
    - `reports/TEST_REPORT.md` 中的改进建议如已实施（如 pytest.ini 删除），在报告末尾添加状态标注
    - `reports/PROJECT_ANALYSIS.md` 是项目整体分析，内容与 README/doc 存在重叠但有其独立价值（CSDN 文章衍生）
    - 在 `reports/` 目录添加 README 说明文件，解释两个报告的来源和时效性
  - **Acceptance Criteria Addressed**: 分析报告归档规范
  - **Notes**: 两个报告都有外部引用价值（CSDN 文章），暂不建议删除

## 阶段四：脚本目录精简

- [x] Task 7: 分析与合并脚本目录
  - **Priority**: P2
  - **Depends On**: 无
  - **Description**:
    - `scripts/` 目录仅有 `check_file_size.py`
    - `doc/scripts/` 目录下有 `compress_static.py`、`monitor_build_size.py`、`build_metrics.json`
    - 将 `doc/scripts/` 中的脚本移动到 `scripts/` 目录下
    - 更新 `.pre-commit-config.yaml` 中的脚本路径（如需要）
    - 删除空出的 `doc/scripts/` 目录
  - **Acceptance Criteria Addressed**: 脚本目录精简
  - **Notes**: `.agents/skills/` 中的 `SKILL.md` 和 `land_watch.py` 是 AI Agent 技能，属于不同体系，保留不动

## 阶段五：最终验证

- [x] Task 8: 全面验证与文档更新
  - **Priority**: P1
  - **Depends On**: Task 1, Task 2, Task 3, Task 5, Task 7
  - **Description**:
    - 验证 `pytest.ini` 已删除且测试可正常运行
    - 验证所有 Python 版本声明一致
    - 运行 `ruff check` 确认无配置错误
    - 更新 `CHANGELOG.md` 记录本次优化变更
  - **Acceptance Criteria Addressed**: 全部
  - **Notes**: 此为最终验收任务

# 任务依赖关系

- Task 8 依赖 Task 1, Task 2, Task 3, Task 5, Task 7
- Task 1, Task 2, Task 5, Task 6, Task 7 可并行执行（互不依赖）
- Task 3 可与上述任务并行
- Task 4 依赖 Task 3（仅在文档结构确定后再分析 qoder 去重）
