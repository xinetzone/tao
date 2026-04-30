# 常用命令

## 安装与开发

```bash
# 安装（开发模式）
pip install -e ".[dev,doc,test]"
```

## 测试

```bash
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
```

## Lint 与格式化

```bash
# Lint/格式化
pre-commit run --all-files
```

## 文档构建

```bash
# 构建文档（默认 HTML）
python -m invoke doc

# 严格模式构建
python -m invoke doc.build --nitpick

# 清理输出
python -m invoke doc.clean

# 指定语言构建
python -m invoke doc.build --language en
```

## 打包

```bash
# 打包
python -m build
```