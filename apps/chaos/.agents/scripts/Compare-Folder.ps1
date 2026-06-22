<#
.SYNOPSIS
    文件夹对比工具 - 独立验证两个目录的一致性

.DESCRIPTION
    本脚本是 P2 改进建议的落地产物,从 archive-folder 技能的验证逻辑中提取
    为独立可复用模板。仅做"两个已有目录的对比",不涉及复制/删除。

    适用场景:
      - 同步校验:验证 rsync/robocopy 同步结果
      - 备份对比:对比备份与源是否一致
      - 迁移验证:验证迁移前后内容是否完整
      - 归档复核:对已归档资产做定期一致性检查
      - 一般性文件对比:任意两个目录树的差异分析

    对比维度:
      1. 目录结构:目录树是否一致(含空目录)
      2. 文件清单:相对路径是否完全匹配
      3. 文件大小:每个对应文件的字节数
      4. 修改时间:LastWriteTime 精确到 ticks
      5. SHA256 哈希(可选):二进制内容一致性,适用于关键资产

.PARAMETER Reference
    参考目录绝对路径(必需)。作为对比基准。

.PARAMETER Difference
    对比目录绝对路径(必需)。被验证的目录。

.PARAMETER IncludeHash
    额外进行 SHA256 哈希校验(更严格但更慢)。

.EXAMPLE
    .\Compare-Folder.ps1 -Reference "D:\src" -Difference "D:\backup\src"
    # 基础对比(Size + LastWriteTime)

.EXAMPLE
    .\Compare-Folder.ps1 -Reference "D:\src" -Difference "D:\backup\src" -IncludeHash
    # 严格对比(含 SHA256)

.OUTPUTS
    PSCustomObject,包含字段:
      Reference, Difference
      FileCount, DirCount
      Verified (bool), Mismatches (array)
      Duration (timespan), ExitCode (int)
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Reference,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Difference,

    [switch]$IncludeHash
)

$ErrorActionPreference = 'Stop'

function Write-Stage {
    param([string]$Stage, [string]$Message, [string]$Color = 'Cyan')
    Write-Host "[$Stage] $Message" -ForegroundColor $Color
}

function Get-FolderSignature {
    param([string]$Root)
    Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
        ForEach-Object {
            $rel = $_.FullName.Substring($Root.Length)
            [PSCustomObject]@{
                RelPath = $rel
                Size    = $_.Length
                MTime   = $_.LastWriteTime.ToString('o')
                Hash    = if ($IncludeHash) { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash } else { $null }
            }
        }
}

function Get-DirSignature {
    param([string]$Root)
    Get-ChildItem -LiteralPath $Root -Recurse -Directory -Force |
        ForEach-Object { $_.FullName.Substring($Root.Length) }
}

# ========== 主流程 ==========
$startTime = Get-Date
$result = [PSCustomObject]@{
    Reference  = $Reference
    Difference = $Difference
    FileCount  = 0
    DirCount   = 0
    Verified   = $false
    Mismatches = @()
    Duration   = $null
    ExitCode   = 0
}

try {
    # 参数校验
    if (-not (Test-Path -LiteralPath $Reference -PathType Container)) {
        throw "Reference 目录不存在或不是目录: $Reference"
    }
    if (-not (Test-Path -LiteralPath $Difference -PathType Container)) {
        throw "Difference 目录不存在或不是目录: $Difference"
    }

    Write-Stage 'Init' "Reference:  $Reference"
    Write-Stage 'Init' "Difference: $Difference"
    if ($IncludeHash) {
        Write-Stage 'Init' '启用 SHA256 哈希校验(较慢)' 'Yellow'
    }

    # 采集签名
    Write-Stage 'Scan' '采集文件签名...'
    $refFiles = Get-FolderSignature $Reference
    $diffFiles = Get-FolderSignature $Difference

    Write-Stage 'Scan' '采集目录签名...'
    $refDirs = Get-DirSignature $Reference
    $diffDirs = Get-DirSignature $Difference

    $result.FileCount = @($refFiles).Count
    $result.DirCount = @($refDirs).Count

    Write-Stage 'Scan' "Reference:  文件=$($result.FileCount) 目录=$($result.DirCount)"
    Write-Stage 'Scan' "Difference: 文件=$(@($diffFiles).Count) 目录=$(@($diffDirs).Count)"

    # 构造哈希表加速查找
    $refMap = @{}; foreach ($f in $refFiles) { $refMap[$f.RelPath] = $f }
    $diffMap = @{}; foreach ($f in $diffFiles) { $diffMap[$f.RelPath] = $f }

    $mismatches = @()

    # 检查 Reference 中每个文件在 Difference 中是否存在且一致
    Write-Stage 'Compare' '逐文件对比...'
    foreach ($key in $refMap.Keys) {
        if (-not $diffMap.ContainsKey($key)) {
            $mismatches += [PSCustomObject]@{
                Path = $key; Issue = 'Missing'; Detail = "Difference 缺失此文件"
            }
            continue
        }
        $r = $refMap[$key]; $d = $diffMap[$key]
        if ($r.Size -ne $d.Size) {
            $mismatches += [PSCustomObject]@{
                Path = $key; Issue = 'SizeMismatch'; Detail = "Reference=$($r.Size) Difference=$($d.Size)"
            }
        }
        elseif ($r.MTime -ne $d.MTime) {
            $mismatches += [PSCustomObject]@{
                Path = $key; Issue = 'TimeMismatch'; Detail = "Reference=$($r.MTime) Difference=$($d.MTime)"
            }
        }
        elseif ($IncludeHash -and $r.Hash -ne $d.Hash) {
            $mismatches += [PSCustomObject]@{
                Path = $key; Issue = 'HashMismatch'; Detail = "Reference=$($r.Hash) Difference=$($d.Hash)"
            }
        }
    }

    # 检查 Difference 是否有多余文件
    foreach ($key in $diffMap.Keys) {
        if (-not $refMap.ContainsKey($key)) {
            $mismatches += [PSCustomObject]@{
                Path = $key; Issue = 'Extra'; Detail = "Difference 多余此文件"
            }
        }
    }

    # 目录结构对比
    Write-Stage 'Compare' '目录结构对比...'
    foreach ($d in $refDirs) {
        if ($diffDirs -notcontains $d) {
            $mismatches += [PSCustomObject]@{
                Path = $d; Issue = 'DirMissing'; Detail = "Difference 缺失此目录"
            }
        }
    }
    foreach ($d in $diffDirs) {
        if ($refDirs -notcontains $d) {
            $mismatches += [PSCustomObject]@{
                Path = $d; Issue = 'DirExtra'; Detail = "Difference 多余此目录"
            }
        }
    }

    $result.Mismatches = $mismatches
    $result.Verified = (@($mismatches).Count -eq 0)

    if ($result.Verified) {
        Write-Stage 'Result' "✅ 验证通过:文件=$($result.FileCount) 目录=$($result.DirCount) 全部一致" 'Green'
    } else {
        Write-Stage 'Result' "❌ 验证失败:发现 $(@($mismatches).Count) 处不一致" 'Red'
        Write-Host ""
        $mismatches | Format-Table -AutoSize | Out-String | Write-Host
        $result.ExitCode = 2
    }

} catch {
    Write-Stage 'ERROR' $_.Exception.Message 'Red'
    if ($result.ExitCode -eq 0) { $result.ExitCode = 1 }
} finally {
    $result.Duration = (Get-Date) - $startTime
    Write-Stage 'Done' "耗时: $($result.Duration.ToString('mm\:ss\.fff'))" 'Cyan'
}

$result
