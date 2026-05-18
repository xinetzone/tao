# 验证清单

## 配置去重验证

- [x] `pytest.ini` 文件已被完全删除
- [x] `pyproject.toml` 的 `[tool.pytest.ini_options]` 段包含 `markers` 配置
- [x] `pyproject.toml` 的 `[tool.pytest.ini_options]` 段包含 `asyncio_mode = "auto"`
- [x] `pyproject.toml` 包含 `testpaths`、`python_files`、`python_classes`、`python_functions` 配置

## Python 版本一致性验证

- [x] `README.md` 安装说明中的 Python 版本与 `pyproject.toml` 的 `requires-python` 一致
- [x] `AGENTS.md` 中的 Python 版本描述与 `pyproject.toml` 一致
- [x] `.readthedocs.yml` 中的 Python 版本与 `pyproject.toml` 版本区间兼容
- [x] `.mise.toml` 中的 Python 版本与 `pyproject.toml` 版本区间兼容

## 文档去重验证

- [x] `AGENTS.md` 的核心功能速览部分不再与 `README.md` 核心功能部分逐字重复
- [x] `AGENTS.md` 包含指向 `README.md` 或 `doc/` 下文档的引用链接

## qoder 与手写文档边界验证

- [x] `doc/` 中不包含与 `.qoder/repowiki/` 自动生成内容逐字重复的手写描述
- [x] 如存在重叠，`doc/` 中的对应内容已简化为导航索引

## 规格文档整合验证

- [x] `specs/` 目录已被删除或仅包含归档性质的说明文件
- [x] `specs/SPEC.md` 已移动到 `.trae/specs/multi_agent_system/` 下
- [x] `specs/symphony-design.md` 已移动到 `.trae/specs/multi_agent_system/` 下
- [x] `specs/symphony-elixir-experience.md` 已移动到 `.trae/specs/multi_agent_system/` 下
- [x] `.trae/specs/multi_agent_system/` 中的文档引用已更新

## 报告归档验证

- [x] `reports/` 目录包含说明文件，解释各报告的来源和时效性
- [x] `reports/TEST_REPORT.md` 中已实施的改进建议已标注状态

## 脚本目录精简验证

- [x] `scripts/` 目录包含所有项目级辅助脚本（原 `doc/scripts/` 中的内容已移入）
- [x] `doc/scripts/` 目录已被删除
- [x] `.pre-commit-config.yaml` 中的 `scripts/check_file_size.py` 路径仍然有效

## 整体验证

- [x] `git status` 确认所有变更为预期内容
- [x] 项目根目录结构清晰，无冗余目录
- [x] `CHANGELOG.md` 记录了本次优化变更
- [x] `src/` 目录及其所有子目录未被任何修改操作触及
