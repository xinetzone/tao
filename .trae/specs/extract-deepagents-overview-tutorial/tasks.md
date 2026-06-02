# Tasks
- [x] Task 1: 获取 DeepAgents overview 页面内容
  - [x] SubTask 1.1: 使用网页抽取工具抓取 `https://docs.langchain.com/oss/python/deepagents/overview` 正文内容
  - [x] SubTask 1.2: 将抓取中间产物放入 `.temp/`，不作为长期引用目标
  - [x] SubTask 1.3: 识别页面标题结构、主要章节、示例代码和教程步骤
- [x] Task 2: 判断项目归档位置
  - [x] SubTask 2.1: 根据文档治理规则判断内容面向对象和生命周期
  - [x] SubTask 2.2: 检查候选目录的现有结构、命名风格和索引写法
- [x] Task 3: 编写结构化教程萃取文档
  - [x] SubTask 3.1: 提炼 DeepAgents 的核心概念、设计动机和适用场景
  - [x] SubTask 3.2: 提炼页面中的操作步骤、代码使用方式和实践案例
  - [x] SubTask 3.3: 按知识逻辑分类整理为中文 Markdown 文档，并保留官方来源链接
- [x] Task 4: 更新必要索引
  - [x] SubTask 4.1: 如归档位置存在目录索引、README 或导航入口，按既有风格添加新文档入口
  - [x] SubTask 4.2: 确保项目内引用使用相对路径，且不引用 `.temp/` 临时产物
- [x] Task 5: 验证萃取结果
  - [x] SubTask 5.1: 检查文档是否覆盖页面主要章节、关键概念、步骤和案例
  - [x] SubTask 5.2: 检查归档路径、索引、来源链接和临时产物边界是否符合项目规则
  - [x] SubTask 5.3: 如项目提供文档构建或严格校验命令，运行相应验证；如不可用，说明原因

## Verification Notes
- 已修复 `docs-internal-linkcheck` 报告的 3 条既有失效链接：`docs/tech/resource-curation-guide.md` 中 2 条模板占位链接，以及 `docs/topics/rule-lifecycle.md` 中 1 条不存在的 `../../zh/content/核心概念/双态孵化模型.md` 链接。
- 修复后运行 `mise run docs-internal-linkcheck`，已通过：共校验 `docs/` 下 394 条相对链接、`.agents/` 下 270 条相对链接，全部有效。
- 已运行 `mise run lint`，首次运行自动修复 Markdown 尾随空白与文件末尾格式，复跑已通过。
- 已运行 `mise run test`，未通过；失败发生在 `uv sync` 安装 `accessible-pygments==0.0.5` 时 wheel 元数据缺失，并伴随 Sphinx 环境中缺少 `sphinx_rtd_theme`，属于当前环境/依赖安装问题。

# Task Dependencies
- Task 2 depends on Task 1 的页面结构识别结果。
- Task 3 depends on Task 1 和 Task 2。
- Task 4 depends on Task 3。
- Task 5 depends on Task 3 和 Task 4。
