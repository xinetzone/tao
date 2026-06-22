# PowerShell 绕过 ShouldProcess 模式

## 背景

PowerShell 的 `SupportsShouldProcess` 是实现 `-WhatIf` 与 `-Confirm` 参数的标准机制。当脚本声明 `[CmdletBinding(SupportsShouldProcess=$true)]` 后,所有写操作 cmdlet(`Set-Content`、`Add-Content`、`New-Item`、`Remove-Item` 等)在 `-WhatIf` 模式下都会被自动跳过。

这一机制在大多数场景下是合理的,但**审计日志场景**存在矛盾:审计日志的价值正在于记录"预演过程"或"未实际执行的操作",如果日志写入本身也被 WhatIf 跳过,则审计日志失效。

## 适用场景

- **审计日志**:必须在 WhatIf 模式下也写入的日志文件
- **调试输出**:需要在预演模式下也记录的调试信息
- **状态文件**:需要在预演模式下也更新的状态标记
- **临时文件**:需要在预演模式下也创建的临时文件

## 解决方案:用 .NET API 替代 PowerShell cmdlet

.NET API 不经过 PowerShell 的 ShouldProcess 流程,因此在 WhatIf 模式下也能正常执行。

### 文件写入

```powershell
# ❌ 被 ShouldProcess 拦截,WhatIf 模式下不写入
Set-Content -Path $logFile -Value $content
Add-Content -Path $logFile -Value $content

# ✅ 绕过 ShouldProcess,WhatIf 模式下也写入
[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)
[System.IO.File]::AppendAllText($path, $content, [System.Text.Encoding]::UTF8)
```

### 目录创建

```powershell
# ❌ 被 ShouldProcess 拦截,WhatIf 模式下不创建
New-Item -ItemType Directory -Path $dir

# ✅ 绕过 ShouldProcess,WhatIf 模式下也创建
[System.IO.Directory]::CreateDirectory($dir) | Out-Null
```

### 文件删除(谨慎使用)

```powershell
# ❌ 被 ShouldProcess 拦截
Remove-Item -Path $file -Force

# ⚠️ 绕过 ShouldProcess,但删除操作通常不应绕过(仅在特殊场景使用)
# [System.IO.File]::Delete($file)
```

> **警告**:删除操作绕过 ShouldProcess 极其危险,仅在有充分理由的场景使用(如清理临时文件)。一般情况下,删除操作应保留 ShouldProcess 拦截。

## 完整示例:审计日志写入

```powershell
[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [string]$LogFile
)

function Write-Stage {
    param([string]$Message)
    # 控制台输出(受 WhatIf 影响,但 Write-Host 不受影响)
    Write-Host $Message

    # 日志写入(绕过 WhatIf,确保审计日志始终记录)
    if ($LogFile) {
        $logDir = Split-Path $LogFile -Parent
        if ($logDir -and -not (Test-Path $logDir)) {
            # 绕过 WhatIf 创建目录
            [System.IO.Directory]::CreateDirectory($logDir) | Out-Null
        }
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $line = "[$timestamp] $Message`r`n"
        # 绕过 WhatIf 写入文件
        [System.IO.File]::AppendAllText($LogFile, $line, [System.Text.Encoding]::UTF8)
    }
}

# 首次覆盖写入(避免旧日志污染)
if ($LogFile -and (Test-Path $LogFile)) {
    [System.IO.File]::WriteAllText($LogFile, "", [System.Text.Encoding]::UTF8)
}

Write-Stage "开始执行"
# ... 业务逻辑 ...
Write-Stage "执行完成"
```

## 排查清单

当发现 WhatIf 模式下文件未创建/未写入时,按以下清单排查:

| 检查项 | 命令 | 期望 |
|---|---|---|
| 脚本是否声明 SupportsShouldProcess | `Get-Command $script \| Select Definition` | 包含 `SupportsShouldProcess` |
| 写操作是否用了 cmdlet | 检查代码中的 `Set-Content`/`Add-Content`/`New-Item` | 应替换为 .NET API |
| 目录是否被拦截 | 检查 `New-Item -ItemType Directory` | 应替换为 `[System.IO.Directory]::CreateDirectory()` |
| 编码是否正确 | 检查 .NET API 调用是否传入 `[System.Text.Encoding]::UTF8` | 确保中文不乱码 |

## 编码注意事项

.NET API 的默认编码是 UTF-16 LE,与 PowerShell 的 UTF-8 不同。**必须显式传入 UTF8 编码**,否则中文会乱码:

```powershell
# ❌ 默认 UTF-16,中文乱码
[System.IO.File]::AppendAllText($path, $content)

# ✅ 显式 UTF-8
[System.IO.File]::AppendAllText($path, $content, [System.Text.Encoding]::UTF8)
```

## 参考链接

- [archive-folder 技能](../../skills/archive-folder/SKILL.md) — 本模式的实际应用(v1.2.0 的 `-LogFile` 参数)
- [task-summary-archive-and-cleanup-20260622.md](../../../docs/tech/task-summary-archive-and-cleanup-20260622.md) — 问题 6/7 详细记录
- [PowerShell ShouldProcess 官方文档](https://learn.microsoft.com/en-us/powershell/scripting/learn/deep-dives/everything-about-shouldprocess)
