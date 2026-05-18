# 测试指南

## Python 环境

执行 Python 相关测试和代码运行时，默认使用路径为 `${PYTHON_ENV_DIR:-C:\Users\XMICUser\.conda\envs\py314}` 的 Python 环境（Python 3.14）。

## 常用测试命令

```bash
# 安装（开发模式，包含测试依赖）
pip install -e ".[dev,doc,test]"

# 运行所有测试
python -m pytest tests/testing/ -v

# 运行单个测试文件
python -m pytest tests/testing/test_remote/ -v

# 按名称模式运行测试
python -m pytest tests/testing/ -k "test_probe" -v

# 带覆盖率
coverage run -m pytest tests/testing/ && coverage report

# 性能基准测试
python tests/testing/perf_remote_bench.py

# Lint/格式化
pre-commit run --all-files
```

## 测试规范

### 编码规范
- **类型注解**：所有公开 API 必须有类型提示，使用 Python 3.14 的延迟注解机制
- **前向引用**：标注中包含前向引用时不再需要将其包裹在字符串中
- **文档字符串**：Google 风格（sphinx.ext.napoleon 解析）
- **Lint**：ruff（格式化 + linting），通过 pre-commit 执行
- **编码**：UTF-8，LF 换行（见 `.editorconfig`）
- **测试覆盖率目标**：≥ 80%

## 测试环境配置

- 使用 `pytest.ini` 配置测试环境变量
- 为测试提供 mock 实现，避免依赖外部服务
- 确保测试数据库与生产数据库结构一致

## 测试策略

- **单元测试**：测试单个组件的功能
- **集成测试**：测试组件之间的交互
- **系统测试**：测试整个系统的功能
- **端到端测试**：测试完整的业务流程
- **测试覆盖率目标**：≥ 80%

## 性能测试

- 运行性能基准测试：`python tests/testing/perf_remote_bench.py`

## 项目里程碑

| 阶段 | 内容 | 状态 | 完成日期 |
|------|------|------|----------|
| Phase D | 类型安全与质量提升（OpenAPI、测试、CI） | ✅ ${milestones.phase_d.status} | ${milestones.phase_d.date} |

## 依赖管理策略

- 使用 `pyproject.toml` 明确指定依赖版本范围
- 定期运行 `pip-audit` 检查安全漏洞
- 使用可选依赖组（extras）管理可选功能

## 常见问题解决方案

- **Redis Mock 数据结构**：扩展 `MockRedis` 支持 LIST、HASH、pipeline、scan 等命令
- **Windows GBK 编码崩溃**：包装 `sys.stdout` 为 UTF-8 + `errors="replace"`
