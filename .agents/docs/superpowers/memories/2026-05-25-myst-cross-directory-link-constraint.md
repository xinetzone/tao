# MyST 跨目录链接边界约束

## Type

约束 + 反例

## Scope

- 适用项目：使用 MyST Markdown + Sphinx 的项目
- 适用场景：在 MyST 文档中创建跨目录链接；链接 source tree 之外的文件；使用 `{contents}` 指令
- 不适用场景：纯 GitHub Markdown（不经 Sphinx 构建）

## Content

- 记忆内容：
  1. **source tree 边界**：Sphinx source tree 之外的文件（如 `.agents/`）不能用 MyST hyperlink 引用，只能用绝对 URL 或不链接
  2. **`{contents}` 指令兼容性**：在 myst-parser 5.1 + Sphinx 9.1 环境下，`{contents}` 指令可能触发 KeyError，应直接移除改用手动目录
  3. **相对路径基准**：MyST 相对链接以当前 .md 文件的目录为基准，跨子目录需使用 `../` 前缀
  4. **git mv 对未追踪文件失效**：移动文件时如果文件未被 git 追踪，`git mv` 会报错，需回退到 `Move-Item`（PowerShell）或 `mv`

- 为什么值得记忆：每个约束都是实施中踩到的坑，固化后可避免重复排查
- 它未来能降低什么成本：排查成本（直接知道边界在哪）、试错成本（避免尝试不可行方案）

## Source

- 来源类型：问题修复 + 复盘
- 来源位置：`.agents/docs/superpowers/retrospectives/2026-05-25-docs-dual-track-restructure.md`
- 形成日期：2026-05-25

## Expiration Conditions

- 何时可能过期：升级到 myst-parser 6.x 或 Sphinx 10.x 时需复查
- 何时需要复查：每次升级 myst-parser 或 sphinx 版本时
- 哪些变化会使它失效：myst-parser 修复了 `{contents}` KeyError bug；Sphinx 支持 source tree 外链接

## Feedback Suggestion

- 建议回流位置：规则（`.agents/rules/documentation.md` 补充"MyST 约束"章节）
- 回流理由：高频踩坑点，适合规则级约束
- 是否需要做梦重组：是（可与其他链接管理经验合并为"站内链接完整规范"）
