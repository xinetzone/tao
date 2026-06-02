# Tasks
- [x] Task 1: 获取 Hello Agents 教程内容
  - [x] SubTask 1.1: 使用网页抽取工具抓取首页内容，并识别教程目录和页面导航结构
  - [x] SubTask 1.2: 根据目录抓取直接相关的教程页面内容
  - [x] SubTask 1.3: 将抓取中间产物放入 `.temp/`，不作为长期引用目标
- [x] Task 2: 判断项目归档位置
  - [x] SubTask 2.1: 根据文档治理规则判断内容面向对象和生命周期
  - [x] SubTask 2.2: 检查候选目录的现有结构和索引写法
- [x] Task 3: 编写结构化教程萃取文档
  - [x] SubTask 3.1: 按知识逻辑提炼核心概念、知识点、操作步骤和实践案例
  - [x] SubTask 3.2: 将内容整理为清晰的 Markdown 文档
  - [x] SubTask 3.3: 保留来源链接，并避免直接依赖临时抓取文件
- [x] Task 4: 更新必要索引
  - [x] SubTask 4.1: 如归档位置有目录索引或 toctree，按既有风格添加新文档入口
  - [x] SubTask 4.2: 确保项目内引用使用相对路径
- [x] Task 5: 验证萃取结果
  - [x] SubTask 5.1: 检查文档是否覆盖教程主要章节、关键概念、步骤和案例
  - [x] SubTask 5.2: 检查归档路径、索引、来源链接和临时产物边界是否符合项目规则
  - [x] SubTask 5.3: 如项目提供文档构建或严格校验命令，运行相应验证

# Task Dependencies
- Task 2 depends on Task 1 的教程结构识别结果。
- Task 3 depends on Task 1 和 Task 2。
- Task 4 depends on Task 3。
- Task 5 depends on Task 3 和 Task 4。
