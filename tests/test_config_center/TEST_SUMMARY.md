# Config Center 测试套件

## 测试文件结构

```
tests/test_config_center/
├── __init__.py                      # 测试包初始化
├── conftest.py                      # 共享 fixtures 和 mocks
├── test_models_config.py            # 配置数据模型测试
├── test_models_version_audit.py     # 版本和审计模型测试
├── test_repository_config.py        # 配置仓库测试
├── test_cache.py                    # 缓存层测试
├── test_validation.py               # 验证框架测试
├── test_auth.py                     # 认证授权测试 (JWT + RBAC)
├── test_services.py                 # 服务层测试
├── test_client.py                   # 客户端 SDK 测试
└── run_tests.bat                    # Windows 测试运行脚本
```

## 测试覆盖范围

### 1. 模型测试 (`test_models_config.py`, `test_models_version_audit.py`)
- ✅ ConfigBase 验证和约束
- ✅ ConfigCreate/ConfigUpdate 模型
- ✅ ConfigResponse 序列化
- ✅ ConfigDocument 和 to_response() 转换
- ✅ 所有枚举类型 (Environment, ConfigValueType, ConfigStatus)
- ✅ ConfigVersion 模型 CRUD
- ✅ AuditLog 模型验证
- ✅ 字段长度限制和边界检查

### 2. 仓库层测试 (`test_repository_config.py`)
- ✅ find_by_key_env_service 查询
- ✅ find_by_tags 带过滤条件
- ✅ find_by_status 带过滤条件
- ✅ find_by_environment_and_service
- ✅ create_indexes
- ✅ 内存集成测试 (MockMongoCollection)

### 3. 缓存层测试 (`test_cache.py`)
- ✅ Redis Key 生成函数
- ✅ InMemoryConfigCache CRUD 操作
- ✅ 缓存过期机制
- ✅ 模式删除 (delete_pattern)
- ✅ 环境隔离
- ✅ RedisConfigCache (Mock 测试)

### 4. 验证框架测试 (`test_validation.py`)
- ✅ ValidationResult 数据类
- ✅ ValidatorRegistry 注册和匹配
- ✅ JsonSchemaValidator
- ✅ RegexValidator
- ✅ RangeValidator
- ✅ 通配符模式匹配
- ✅ 多验证器错误聚合

### 5. 认证授权测试 (`test_auth.py`)
- ✅ JWT Access Token 创建和验证
- ✅ JWT Refresh Token 创建
- ✅ Token 过期和类型验证
- ✅ 5 个系统角色权限测试
- ✅ RBAC 环境和服务 scope 检查
- ✅ 多角色权限组合

### 6. 服务层测试 (`test_services.py`)
- ✅ create_config 带版本和审计
- ✅ get_config 直接查询
- ✅ get_config_by_key_env_service 带缓存
- ✅ update_config 带版本创建和缓存失效
- ✅ delete_config 带缓存清理
- ✅ publish_config 状态转换
- ✅ list_configs 带过滤条件

### 7. 客户端 SDK 测试 (`test_client.py`)
- ✅ 本地缓存机制
- ✅ get_config 同步获取
- ✅ aget_config 异步获取
- ✅ get_configs 列表获取
- ✅ HTTP 错误处理
- ✅ 缓存过期
- ✅ 认证头设置

## 运行测试

### Windows
```bash
# 运行所有测试
pytest tests/test_config_center/ -v

# 带覆盖率
pytest tests/test_config_center/ -v --cov=taolib.config_center

# 使用批处理脚本
cd tests\test_config_center
run_tests.bat

# 带覆盖率
run_tests.bat --cov
```

### Linux/Mac
```bash
# 运行所有测试
python -m pytest tests/test_config_center/ -v

# 带覆盖率
python -m pytest tests/test_config_center/ -v --cov=taolib.config_center --cov-report=html

# 运行单个测试文件
python -m pytest tests/test_config_center/test_models_config.py -v

# 运行特定测试
python -m pytest tests/test_config_center/test_models_config.py::TestConfigBase::test_create_valid_config -v
```

## 测试 Fixtures

### 数据 Fixtures (conftest.py)
- `sample_config_data`: 示例配置数据
- `sample_user_data`: 示例用户数据
- `sample_role_data`: 示例角色数据

### Mock Fixtures
- `mock_mongo_db`: 模拟 MongoDB 数据库
- `mock_mongo_client`: 模拟 Motor 客户端
- `mock_redis`: 模拟 Redis 客户端
- `jwt_secret`: JWT 密钥
- `jwt_algorithm`: JWT 算法
- `sample_token_payload`: 示例 Token payload

## 测试设计原则

1. **隔离性**: 每个测试独立，使用 mocks 避免外部依赖
2. **可读性**: 测试名称描述行为，使用 AAA (Arrange-Act-Assert) 模式
3. **覆盖率**: 覆盖正常路径、边界条件和错误场景
4. **异步支持**: 使用 pytest-asyncio 测试异步代码
5. **无状态**: 每个测试后清理 mocks 和状态

## 覆盖率目标

- **行覆盖率**: ≥ 80%
- **分支覆盖率**: ≥ 75%
- **函数覆盖率**: 100%

## CI/CD 集成

在 CI/CD 流水线中添加：

```yaml
# 示例 GitHub Actions
- name: Run tests
  run: |
    pip install pytest pytest-asyncio pytest-cov
    pytest tests/test_config_center/ -v --cov=taolib.config_center --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## TODO (待补充)

以下测试需要额外的基础设施或集成测试环境：

- [ ] API 端点集成测试 (需要 FastAPI TestClient)
- [ ] WebSocket 连接和消息测试
- [ ] 完整端到端流程测试
- [ ] 性能基准测试
- [ ] 并发和竞态条件测试
