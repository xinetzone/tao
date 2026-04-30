# API 参考

## `taolib.testing.remote` 导出项

| 导出名称 | 类型 | 说明 |
|----------|------|------|
| `SshConfig` | 类 | SSH 配置数据类 |
| `load_ssh_config()` | 函数 | 加载 SSH 配置（带缓存） |
| `redact_ssh_config()` | 函数 | SSH 配置脱敏 |
| `RemoteProbeCommands` | 类 | 远程探测命令配置 |
| `RemoteProbeReport` | 类 | 探测结果报告 |
| `RemoteProbeRunOptions` | 类 | 探测运行选项 |
| `RemoteProber` | 类 | 远程探测器类 |
| `probe_remote()` | 函数 | 远程探测入口函数 |
| `remote_prefixes()` | 函数 | 命令前缀上下文管理器 |
| `RemoteConfigError` | 异常 | 配置错误 |
| `RemoteDependencyError` | 异常 | 依赖错误 |
| `RemoteExecutionError` | 异常 | 执行错误 |
| `DEFAULT_*` | 常量 | 默认命令和编码常量 |

## `taolib.testing.plot.configs` 导出项

| 导出名称 | 类型 | 说明 |
|----------|------|------|
| `configure_matplotlib_fonts()` | 函数 | 配置 Matplotlib 中文字体 |

## 文档整合原则

### 1. 单一真实来源 (SSOT) 原则
- `src/taolib/testing/_base/cache_keys.py` 文件作为所有 Redis 键命名规范的唯一权威来源
- 所有 Redis 键的定义、格式、用途说明必须在此文件中维护
- 其他任何地方不得重复定义相同的键名，只能引用此文件

### 2. 交叉引用机制
- 功能规格文档与架构文档之间建立明确的引用关联
- 规格文档中的技术细节应链接到架构文档中的相应实现说明

### 3. 避免重复原则
- **Phase 进度信息**仅在本文档中进行维护和更新
- 其他文档如需展示进度信息，必须通过引用或链接方式指向本文档