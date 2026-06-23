# Changelog - Archive Folder

所有关于 **archive-folder** 模块的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]

## [1.3.0] - 2026-06-22

### Added

- **P4：归档日志留存** — 新增 `-LogFile` 参数。
  - robocopy 通过 `/LOG+` 追加原生统计到指定文件。
  - 脚本各阶段输出（`Write-Stage`）同步写入日志。
  - 结果对象新增 `LogFile` 字段，返回实际日志路径。
  - 使用 .NET API（`[System.IO.File]::AppendAllText`）绕过 ShouldProcess，确保 WhatIf 预演模式下审计日志也能记录。
- **P11：日志文件自动命名** — 新增 `-LogDir` 参数。
  - 自动在指定目录下创建 `<src-name>-<yyyyMMdd>.log` 文件名。
  - 与 `-LogFile` 互斥，同时指定时 `-LogFile` 优先。
  - 适合每日定时归档场景，减少用户认知负担。
- **P12：日志追加模式** — 新增 `-LogAppend` switch。
  - 文件已存在时追加，写入 `===== Archive-Folder 追加 <timestamp> =====` 标记头。
  - 文件不存在时创建，写入 `===== Archive-Folder 日志 开始 <timestamp> =====` 标记头。
  - 适合批量归档同一日志归档场景，避免日志文件碎片化。
- **P14：HTML 声明一致性校验** — 新增 `-CheckDeclConsistency` switch。
  - 归档前在阶段 0.5 扫描源内所有 `.html`/`.htm` 文件。
  - 提取 `script[src]`/`img[src]`/`link[href]`/`@font-face url()` 四类引用。
  - 校验引用的资源是否实际存在，不一致项写入结果对象 `DeclIssues` 字段。
  - 设计原则：仅提示不阻断归档（归档是冻结快照，声明不一致是源的问题）。
  - 结果对象 `DeclIssues` 数组元素结构：`HtmlFile`/`DeclType`/`RefPath`/`Detail`。

### Changed

- SKILL.md 版本从 v1.2.0 升级至 v1.3.0。
- 功能描述补充 HTML 声明一致性检查阶段。
- 快速开始新增 3 个示例（日志自动命名/追加模式/声明检查）。
- 输入参数表新增 `-LogDir`/`-LogAppend`/`-CheckDeclConsistency`。
- 输出对象新增 `DeclIssues` 字段及元素结构说明。
- 执行流程图新增阶段 0.5。
- 最佳实践补充 3 条新条目。
- 注意事项补充 `-LogFile` 与 `-LogDir` 互斥、`-CheckDeclConsistency` 不阻断等说明。
- FAQ 新增 Q9-Q12。
- 参考链接新增 `bypass-shouldprocess.md` 与 `asset-declaration-matrix.md`。

## [1.2.0] - 2026-06-22

### Added

- **归档日志留存** — 新增 `-LogFile` 参数。
  - robocopy 通过 `/LOG+` 追加原生统计。
  - 脚本各阶段输出同步写入。
  - 结果对象新增 `LogFile` 字段。

## [1.1.0] - 2026-06-22

### Added

- **引用检查阶段** — 新增 `-CheckExternalRefs` + `-RefCheckRoot` 参数。
  - 删除源前扫描外部引用，避免误删被引用的文件。
  - 新增 ExitCode=3（引用检查阻止删除）。

## [1.0.0] - 2026-06-22

### Added

- 初始版本：实现三段式归档（复制 + 验证 + 可选删除）。
  - 使用 `robocopy /E /COPY:DAT /DCOPY:DAT` 保留目录结构、文件属性、时间戳与空目录。
  - 逐文件对比 `Size` + `LastWriteTime`，可选 `SHA256` 哈希校验。
  - 支持 `-DeleteSource`、`-IncludeHash`、`-Force`、`-WhatIf` 参数。
