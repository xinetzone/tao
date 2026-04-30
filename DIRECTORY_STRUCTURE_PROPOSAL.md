# 项目目录结构规范化方案

## 1. 当前问题分析

当前项目根目录下存在大量文档文件和配置文件，缺乏合理的分类组织，存在以下问题：
- 文档文件与配置文件混杂，查找困难
- 根目录文件过多，影响项目整体可读性
- 不符合Python项目的最佳实践
- 不利于新团队成员快速上手

## 2. 规范化目录结构设计

### 2.1 核心结构（基于现有项目调整）

```
flexloop/
├── src/                    # 源代码目录（已有）
│   └── taolib/             # 主包目录（已有）
├── doc/                    # 文档目录（已有，使用单数形式保持一致性）
│   ├── user_guide/         # 用户指南
│   ├── api_reference/      # API参考
│   ├── developer_guide/    # 开发者指南
│   ├── architecture/       # 架构文档
│   └── ...                 # 其他文档子目录
├── tests/                  # 测试代码目录（已有）
├── examples/               # 示例代码（已有）
├── reports/                # 报告文件（已有）
├── scripts/                # 辅助脚本（已有）
├── configs/                # 配置文件目录（新增）
├── build/                  # 构建输出目录（新增）
├── dist/                   # 分发包目录（新增）
├── .github/                # CI/CD配置（已有）
├── .qoder/                 # Qoder配置（已有）
├── .trae/                  # Trae IDE配置（已有）
├── .vscode/                # IDE配置（已有）
├── pyproject.toml          # 项目配置（根目录，已有）
├── pytest.ini              # 测试配置（根目录，已有）
├── .gitignore              # Git忽略文件（已有）
├── .pre-commit-config.yaml # 预提交配置（已有）
├── .readthedocs.yml        # ReadTheDocs配置（已有）
├── LICENSE                 # 许可证（已有）
├── README.md               # 项目说明（已有）
├── CHANGELOG.md            # 变更日志（已有）
└── CONTRIBUTING.md         # 贡献指南（已有）
```

### 2.2 详细目录说明

#### 2.2.1 源代码目录 (`src/`)
- 已存在，无需创建
- 结构保持不变：`src/taolib/testing/...`
- 遵循Python包的标准结构，所有代码文件存放在此目录

#### 2.2.2 文档目录 (`doc/`)
- 已存在（注意使用单数形式保持与现有项目一致）
- 现有内容：`_static/`, `scripts/`, `_config.toml`, `conf.py`, `index.md`, `refs.bib`
- 新增子目录结构：
  ```
  doc/
  ├── user_guide/           # 用户指南
  ├── api_reference/        # API参考
  ├── developer_guide/      # 开发者指南
  ├── architecture/         # 架构文档
  ├── _static/              # 静态资源（已有）
  ├── scripts/              # 文档脚本（已有）
  ├── _config.toml          # 配置（已有）
  ├── conf.py               # Sphinx配置（已有）
  ├── index.md              # 文档首页（已有）
  └── refs.bib              # 参考文献（已有）
  ```
- 文件移动计划：
  - README.md (保留在根目录作为项目入口)
  - AGENTS.md (保留在根目录作为导航，或移至doc/index.md)
  - python_environment.md → doc/user_guide/
  - commands.md → doc/user_guide/
  - architecture.md → doc/architecture/
  - api_reference.md → doc/api_reference/
  - coding_standards.md → doc/developer_guide/
  - environment_variables.md → doc/user_guide/
  - best_practices.md → doc/developer_guide/
  - project_experience.md → doc/developer_guide/
  - qoder_rules.md → doc/developer_guide/

#### 2.2.3 测试目录 (`tests/`)
- 已存在，但内容需整理
- 现有结构：`tests/testing/...`
- 建议结构：
  ```
  tests/
  ├── unit/                 # 单元测试
  ├── integration/          # 集成测试
  ├── functional/           # 功能测试
  └── conftest.py           # 测试配置（如需）
  ```

#### 2.2.4 示例代码目录 (`examples/`)
- 已存在，无需创建
- 现有内容：`multi_agent_example.py`
- 建议保持不变，新增示例代码继续存放在此目录

#### 2.2.5 报告目录 (`reports/`)
- 已存在，无需创建
- 现有内容：`PROJECT_ANALYSIS.md`, `TEST_REPORT.md`
- 建议保持不变，新增报告继续存放在此目录

#### 2.2.6 脚本目录 (`scripts/`)
- 已存在，无需创建
- 现有内容：`check_file_size.py`
- 建议保持不变，新增辅助脚本继续存放在此目录

#### 2.2.7 配置文件目录 (`configs/`)
- 新增目录
- 存放项目配置文件
- 结构：
  ```
  configs/
  ├── development/          # 开发环境配置
  ├── staging/              #  staging环境配置
  └── production/           # 生产环境配置
  ```

#### 2.2.8 构建和分发目录 (`build/`, `dist/`)
- 新增目录
- 用于存放构建输出和分发包
- 通常添加到.gitignore

## 3. 实施步骤

### 3.1 准备工作
1. 备份当前项目文件
2. 确保Git工作区干净（无未提交的更改）
3. 创建实施分支：`git checkout -b refactor-directory-structure`

### 3.2 目录创建
```bash
# 在doc目录下创建新的文档子目录
mkdir -p doc/user_guide doc/api_reference doc/developer_guide doc/architecture

# 创建配置文件目录
mkdir -p configs/development configs/staging configs/production

# 创建构建和分发目录
mkdir -p build dist
```

### 3.3 文件移动
```bash
# 移动文档文件
mv python_environment.md doc/user_guide/
mv commands.md doc/user_guide/
mv architecture.md doc/architecture/
mv api_reference.md doc/api_reference/
mv coding_standards.md doc/developer_guide/
mv environment_variables.md doc/user_guide/
mv best_practices.md doc/developer_guide/
mv project_experience.md doc/developer_guide/
mv qoder_rules.md doc/developer_guide/

# 移动测试文件（根据实际情况调整）
# mkdir -p tests/unit
# mv tests/testing/* tests/unit/

# 移动配置文件（如有）
# mv *.json configs/development/
# mv *.yaml configs/development/
```

### 3.4 配置更新
1. 更新`doc/conf.py`中的文档路径配置，确保能正确找到新位置的文档文件
2. 检查`.gitignore`文件（build/和dist/已存在于当前.gitignore中）
3. 更新IDE配置文件，调整目录结构
4. 更新任何引用了移动文件的脚本或配置
5. 更新`README.md`和`AGENTS.md`中的文件引用路径
6. 更新`CHANGELOG.md`，记录目录结构变更
7. 更新`CONTRIBUTING.md`，反映新的目录结构

### 3.5 验证
1. 运行测试确保所有功能正常：`python -m pytest tests/testing/ -v`
2. 构建文档确保文档生成正常：`python -m invoke doc`
3. 检查所有引用路径是否正确
4. 确保CI/CD流程正常工作

## 4. 注意事项

### 4.1 向后兼容性
- 对于已有的外部引用路径，需要进行更新
- 可以考虑在根目录创建软链接暂时保持兼容性（如果必要）

### 4.2 版本控制
- 在实施前创建专门的分支
- 实施后进行全面测试
- 提交时添加清晰的提交信息，说明目录结构变更
- 合并前进行代码审查

### 4.3 团队协作
- 提前通知团队成员结构变更计划
- 提供更新后的文档和指南
- 确保所有成员了解新的目录结构和命名规范
- 安排培训或演示（如需）

### 4.4 特殊文件处理
- 根目录保留核心配置文件（如pyproject.toml, README.md, LICENSE等）
- 对于有特殊要求的文件（如CI/CD配置），根据工具要求决定存放位置
- 保持与现有项目约定的一致性（如使用`doc/`而非`docs/`）

### 4.5 现有配置文件
- `.gitattributes`, `.gitignore`, `.pre-commit-config.yaml`, `.readthedocs.yml`等配置文件建议保留在根目录
- `pytest.ini`建议保留在根目录，方便测试运行

## 5. 命名规范

### 5.1 目录命名
- 使用小写字母，单词之间用下划线分隔（snake_case）
- 避免使用空格和特殊字符
- 保持简洁明了
- 与现有项目约定保持一致（如使用`doc/`而非`docs/`）

### 5.2 文件命名
- 源代码：使用小写字母，单词之间用下划线分隔（snake_case）
- 文档：使用小写字母，单词之间用连字符分隔（kebab-case）或下划线分隔（保持与现有文档一致）
- 配置文件：根据工具要求命名
- 测试文件：以`test_`开头，使用snake_case
- 报告文件：使用有意义的名称，保持一致性

### 5.3 包和模块命名
- 包：使用小写字母，避免使用下划线
- 模块：使用小写字母，单词之间用下划线分隔
- 类：使用驼峰命名法（CamelCase）
- 函数和变量：使用snake_case

## 6. 预期效果

实施规范化目录结构后，项目将具有以下优势：
- 文件分类清晰，易于查找和管理
- 提高代码可读性和可维护性
- 便于团队协作和新人快速上手
- 符合Python项目的最佳实践
- 为项目扩展提供良好的基础
- 保持与现有项目结构的兼容性

## 7. 后续维护

- 定期检查目录结构是否符合规范
- 新添加的文件和目录应遵循此规范
- 根据项目发展需要，适时调整目录结构
- 定期更新文档，确保与实际结构一致

---

**注意**：此方案基于项目现有结构进行调整，保持了与现有约定的一致性。在实施前，建议团队成员进行充分讨论，确保方案符合项目需求和团队习惯。