<#
.SYNOPSIS
    Windows 文件夹归档工具 - 三段式可验证归档流程

.DESCRIPTION
    本脚本实现 "Windows 文件归档三段式" 方法论:
      1. 复制阶段:使用 robocopy /E /COPY:DAT /DCOPY:DAT 保留目录结构、
         文件属性与时间戳(含空目录)
      2. 验证阶段:逐文件对比 Size + LastWriteTime,可选 SHA256 哈希校验
      3. 清理阶段:验证通过后可选删除源文件夹

    设计原则:
      - 可验证:输出结构化结果对象,包含布尔判定与不一致清单
      - 可回滚:验证失败时绝不删除源,目标保留供人工排查
      - 可审计:每阶段输出明确日志,支持 -WhatIf 预演

.PARAMETER Source
    源文件夹绝对路径(必需)。必须存在。

.PARAMETER Destination
    目标父目录绝对路径(必需)。脚本会在此目录下创建与 Source 同名的子目录。
    若父目录不存在会自动创建。

.PARAMETER DeleteSource
    验证通过后删除源文件夹。默认不删除,需显式指定。

.PARAMETER IncludeHash
    额外进行 SHA256 哈希校验(更严格但更慢,适用于关键资产)。

.PARAMETER Force
    若目标子目录已存在,先清空再归档。默认遇到已存在目标会报错退出。

.PARAMETER CheckExternalRefs
    删除源之前,扫描 -RefCheckRoot 范围内的文本文件,检查是否有文件引用了源内的
    文件(按文件名或源文件夹名匹配)。发现引用时阻止删除,ExitCode=3。
    适用于源文件夹可能被项目其他位置引用的场景。

.PARAMETER RefCheckRoot
    外部引用检查的扫描根目录。默认为 Source 的父目录。
    仅在 -CheckExternalRefs 启用时生效。

.EXAMPLE
    .\Archive-Folder.ps1 -Source "D:\work\react-survey" -Destination "D:\archive\docs"
    # 复制到 D:\archive\docs\react-survey,验证后保留源

.EXAMPLE
    .\Archive-Folder.ps1 -Source "D:\work\react-survey" -Destination "D:\archive\docs" -DeleteSource
    # 复制 + 验证 + 删除源

.EXAMPLE
    .\Archive-Folder.ps1 -Source "D:\work\critical" -Destination "D:\backup" -IncludeHash -DeleteSource
    # 关键资产归档,带 SHA256 校验

.EXAMPLE
    .\Archive-Folder.ps1 -Source "D:\work\module-a" -Destination "D:\archive" -DeleteSource -CheckExternalRefs -RefCheckRoot "D:\work"
    # 归档并删除源,删除前检查 D:\work 下是否有文件引用 module-a 内的资源

.OUTPUTS
    PSCustomObject,包含字段:
      Source, Destination, TargetPath
      FilesCopied, DirsCopied, BytesCopied
      Verified (bool), Mismatches (array)
      SourceDeleted (bool), ExternalRefs (array), RefCheckSkipped (bool)
      Duration (timespan), ExitCode (int)
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Source,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Destination,

    [switch]$DeleteSource,

    [switch]$IncludeHash,

    [switch]$Force,

    [switch]$CheckExternalRefs,

    [string]$RefCheckRoot
)

$ErrorActionPreference = 'Stop'

function Write-Stage {
    param([string]$Stage, [string]$Message, [string]$Color = 'Cyan')
    Write-Host "[$Stage] $Message" -ForegroundColor $Color
}

function Test-PathSafe {
    param([string]$Path, [switch]$MustExist, [string]$Label)
    if (-not $Path) { throw "$Label 不能为空" }
    if ($MustExist -and -not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "$Label 不存在或不是目录: $Path"
    }
}

function Get-FolderSignature {
    param([string]$Root)
    Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
        ForEach-Object {
            $rel = $_.FullName.Substring($Root.Length)
            [PSCustomObject]@{
                RelPath  = $rel
                Size     = $_.Length
                MTime    = $_.LastWriteTime.ToString('o')
                Hash     = if ($IncludeHash) { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash } else { $null }
            }
        }
}

function Get-DirSignature {
    param([string]$Root)
    Get-ChildItem -LiteralPath $Root -Recurse -Directory -Force |
        ForEach-Object { $_.FullName.Substring($Root.Length) }
}

function Test-ExternalReferences {
    <#
    .SYNOPSIS
        扫描指定根目录下的文本文件,检查是否引用了源文件夹内的文件。
    .DESCRIPTION
        匹配策略(按优先级):
          1. 源文件夹名(如 "react-survey")— 识别路径引用
          2. 源内文件名(如 "echarts.min.js")— 识别文件引用
        扫描范围:RefCheckRoot 下所有文本文件,排除源文件夹本身。
        误报策略:宁可误报不漏报,误报仅阻止删除,用户可手动确认。
    #>
    param(
        [string]$SourcePath,
        [string]$CheckRoot
    )

    $sourceName = Split-Path $SourcePath -Leaf
    $sourceFiles = Get-ChildItem -LiteralPath $SourcePath -Recurse -File -Force
    # 文件名去重(不同目录可能有同名文件,只取唯一名)
    $fileNames = @($sourceFiles.Name | Sort-Object -Unique)
    # 过滤掉过短的文件名(<=3 字符,如 "a.js",避免误报)
    $fileNames = @($fileNames | Where-Object { $_.Length -gt 3 })

    # 待扫描的文本文件扩展名
    $textExts = @('.html', '.htm', '.md', '.css', '.js', '.json', '.xml',
                  '.txt', '.ts', '.jsx', '.tsx', '.vue', '.py', '.yaml', '.yml',
                  '.toml', '.ini', '.cfg', '.conf', '.svg')
    # 跳过大文件(> 5MB),避免性能问题
    $maxSize = 5MB

    Write-Stage 'RefCheck' "源文件夹名: $sourceName"
    Write-Stage 'RefCheck' "源内唯一文件名数: $($fileNames.Count)"

    # 扫描 CheckRoot 下的文本文件,排除源文件夹本身
    $sourcePathFull = (Resolve-Path -LiteralPath $SourcePath).Path.TrimEnd('\')
    $externalFiles = Get-ChildItem -LiteralPath $CheckRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notlike "$sourcePathFull*" -and
            $textExts -contains $_.Extension.ToLower() -and
            $_.Length -lt $maxSize
        }

    Write-Stage 'RefCheck' "待扫描外部文本文件数: $(@($externalFiles).Count)"

    $refs = @()
    $checkedCount = 0
    foreach ($extFile in $externalFiles) {
        $checkedCount++
        $content = Get-Content -LiteralPath $extFile.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        $matched = $false

        # 策略 1:检查源文件夹名(识别路径引用,如 "react-survey/assets/...")
        if ($content -match [regex]::Escape($sourceName)) {
            $refs += [PSCustomObject]@{
                RefFile   = $extFile.FullName
                MatchType = 'FolderName'
                Pattern   = $sourceName
            }
            $matched = $true
        }

        # 策略 2:检查源内文件名(仅在未匹配文件夹名时检查,减少重复报告)
        if (-not $matched) {
            foreach ($fileName in $fileNames) {
                if ($content -match [regex]::Escape($fileName)) {
                    $refs += [PSCustomObject]@{
                        RefFile   = $extFile.FullName
                        MatchType = 'FileName'
                        Pattern   = $fileName
                    }
                    break  # 一个文件只报告第一个匹配
                }
            }
        }
    }

    Write-Stage 'RefCheck' "已扫描 $checkedCount 个文件,发现 $(@($refs).Count) 处引用"
    return $refs
}

# ========== 阶段 0:参数校验 ==========
$startTime = Get-Date
$result = [PSCustomObject]@{
    Source          = $Source
    Destination     = $Destination
    TargetPath      = $null
    FilesCopied     = 0
    DirsCopied      = 0
    BytesCopied     = 0L
    Verified        = $false
    Mismatches      = @()
    SourceDeleted   = $false
    ExternalRefs    = @()
    RefCheckSkipped = $true
    Duration        = $null
    ExitCode        = 0
}

try {
    Test-PathSafe $Source -MustExist -Label 'Source'
    if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
        throw "Source 必须是目录: $Source"
    }

    $sourceName = Split-Path $Source -Leaf
    $targetPath = Join-Path $Destination $sourceName
    $result.TargetPath = $targetPath

    Write-Stage '0-Init' "源: $Source"
    Write-Stage '0-Init' "目标: $targetPath"

    if (Test-Path -LiteralPath $targetPath) {
        if ($Force) {
            Write-Stage '0-Init' "目标已存在,-Force 清空: $targetPath" 'Yellow'
            if ($PSCmdlet.ShouldProcess($targetPath, 'Remove-Item (Force)')) {
                Remove-Item -LiteralPath $targetPath -Recurse -Force
            }
        } else {
            throw "目标已存在: $targetPath (使用 -Force 覆盖,或手动清理)"
        }
    }

    if (-not (Test-Path -LiteralPath $Destination)) {
        Write-Stage '0-Init' "创建目标父目录: $Destination" 'Yellow'
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }

    # ========== 阶段 1:robocopy 复制 ==========
    Write-Stage '1-Copy' '开始 robocopy 复制(保留属性/时间戳/空目录)'
    $robocopyArgs = @(
        $Source
        $targetPath
        '/E'           # 含空目录
        '/COPY:DAT'    # Data + Attributes + Timestamps
        '/DCOPY:DAT'   # 目录的 Data + Attributes + Timestamps
        '/R:1'
        '/W:1'
        '/NP'
        '/NFL'         # 不列文件名(用日志解析更清晰)
        '/NDL'         # 不列目录名
    )
    if ($PSCmdlet.ShouldProcess("$Source -> $targetPath", 'robocopy')) {
        $rcOutput = & robocopy @robocopyArgs 2>&1
        $rcExit = $LASTEXITCODE
    } else {
        $rcExit = 0
    }

    # robocopy 退出码 0-7 均为成功,>=8 才是错误
    if ($rcExit -ge 8) {
        $rcLog = $rcOutput -join "`n"
        throw "robocopy failed with exit $rcExit`n$rcLog"
    }
    Write-Stage '1-Copy' "robocopy 完成(退出码 $rcExit,属成功范围 0-7)" 'Green'

    # 解析 robocopy 统计(从输出末尾提取)
    $stats = $rcOutput | Where-Object { $_ -match '^\s+(目录|文件|字节):' }
    foreach ($line in $stats) {
        if ($line -match '目录:\s+(\d+)\s+(\d+)') { $result.DirsCopied = [int]$Matches[2] }
        elseif ($line -match '文件:\s+(\d+)\s+(\d+)') { $result.FilesCopied = [int]$Matches[2] }
        elseif ($line -match '字节:\s+([\d.]+\s*[kmgt]?b?)\s+([\d.]+\s*[kmgt]?b?)') {
            $result.BytesCopied = $Matches[2]
        }
    }

    # ========== 阶段 2:逐文件验证 ==========
    Write-Stage '2-Verify' '开始逐文件验证(Size + LastWriteTime)'
    if ($IncludeHash) {
        Write-Stage '2-Verify' '启用 SHA256 哈希校验(较慢)' 'Yellow'
    }

    $srcFiles = Get-FolderSignature $Source
    $dstFiles = Get-FolderSignature $targetPath

    $srcMap = @{}; foreach ($f in $srcFiles) { $srcMap[$f.RelPath] = $f }
    $dstMap = @{}; foreach ($f in $dstFiles) { $dstMap[$f.RelPath] = $f }

    $mismatches = @()

    # 检查源中每个文件是否在目标存在且一致
    foreach ($key in $srcMap.Keys) {
        if (-not $dstMap.ContainsKey($key)) {
            $mismatches += [PSCustomObject]@{ Path = $key; Issue = 'Missing'; Detail = '目标缺失' }
            continue
        }
        $s = $srcMap[$key]; $d = $dstMap[$key]
        if ($s.Size -ne $d.Size) {
            $mismatches += [PSCustomObject]@{ Path = $key; Issue = 'SizeMismatch'; Detail = "源=$($s.Size) 目标=$($d.Size)" }
        }
        elseif ($s.MTime -ne $d.MTime) {
            $mismatches += [PSCustomObject]@{ Path = $key; Issue = 'TimeMismatch'; Detail = "源=$($s.MTime) 目标=$($d.MTime)" }
        }
        elseif ($IncludeHash -and $s.Hash -ne $d.Hash) {
            $mismatches += [PSCustomObject]@{ Path = $key; Issue = 'HashMismatch'; Detail = "源=$($s.Hash) 目标=$($d.Hash)" }
        }
    }

    # 检查目标是否有多余文件
    foreach ($key in $dstMap.Keys) {
        if (-not $srcMap.ContainsKey($key)) {
            $mismatches += [PSCustomObject]@{ Path = $key; Issue = 'Extra'; Detail = '目标多余' }
        }
    }

    # 目录结构对比
    $srcDirs = Get-DirSignature $Source
    $dstDirs = Get-DirSignature $targetPath
    foreach ($d in $srcDirs) {
        if ($dstDirs -notcontains $d) {
            $mismatches += [PSCustomObject]@{ Path = $d; Issue = 'DirMissing'; Detail = '目录缺失' }
        }
    }
    foreach ($d in $dstDirs) {
        if ($srcDirs -notcontains $d) {
            $mismatches += [PSCustomObject]@{ Path = $d; Issue = 'DirExtra'; Detail = '目录多余' }
        }
    }

    $result.Mismatches = $mismatches
    $result.Verified = (@($mismatches).Count -eq 0)

    # 用验证阶段的实际值覆盖 robocopy 统计(更准确,且兼容 PS 5.1)
    $result.FilesCopied = @($srcFiles).Count
    $result.DirsCopied = @($srcDirs).Count + 1  # +1 包含根目录

    if ($result.Verified) {
        Write-Stage '2-Verify' "✅ 验证通过:文件=$(@($srcFiles).Count) 目录=$(@($srcDirs).Count) 全部一致" 'Green'
    } else {
        Write-Stage '2-Verify' "❌ 验证失败:发现 $(@($mismatches).Count) 处不一致" 'Red'
        $mismatches | Format-Table -AutoSize | Out-String | Write-Host
        $result.ExitCode = 2
        throw "验证失败,源未删除,请人工排查目标: $targetPath"
    }

    # ========== 阶段 2.5:外部引用检查(可选,删除源之前)==========
    $skipDelete = $false
    if ($DeleteSource -and $CheckExternalRefs) {
        $refRoot = if ($RefCheckRoot) { $RefCheckRoot } else { Split-Path $Source -Parent }
        if (-not (Test-Path -LiteralPath $refRoot -PathType Container)) {
            Write-Stage '2.5-RefCheck' "RefCheckRoot 不存在,跳过引用检查: $refRoot" 'Yellow'
        } else {
            Write-Stage '2.5-RefCheck' "开始外部引用检查(扫描根: $refRoot)"
            $externalRefs = Test-ExternalReferences -SourcePath $Source -CheckRoot $refRoot
            $result.ExternalRefs = $externalRefs
            $result.RefCheckSkipped = $false

            if (@($externalRefs).Count -gt 0) {
                Write-Stage '2.5-RefCheck' "❌ 发现 $(@($externalRefs).Count) 处外部引用,阻止删除源" 'Red'
                Write-Host ""
                $externalRefs | Format-Table -AutoSize | Out-String | Write-Host
                $result.ExitCode = 3
                $skipDelete = $true
                Write-Stage '2.5-RefCheck' "源已保留,请人工确认引用后再决定是否删除: $Source" 'Yellow'
            } else {
                Write-Stage '2.5-RefCheck' "✅ 未发现外部引用,可安全删除源" 'Green'
            }
        }
    }

    # ========== 阶段 3:可选删除源 ==========
    if ($DeleteSource -and -not $skipDelete) {
        Write-Stage '3-Cleanup' '验证已通过,执行删除源文件夹'
        if ($PSCmdlet.ShouldProcess($Source, 'Remove-Item (DeleteSource)')) {
            Remove-Item -LiteralPath $Source -Recurse -Force
            if (-not (Test-Path -LiteralPath $Source)) {
                $result.SourceDeleted = $true
                Write-Stage '3-Cleanup' "✅ 源已删除: $Source" 'Green'
            } else {
                throw "源删除失败,仍存在: $Source"
            }
        }
    } elseif ($skipDelete) {
        Write-Stage '3-Cleanup' '因外部引用检查阻止删除,源已保留' 'Yellow'
    } else {
        Write-Stage '3-Cleanup' '未指定 -DeleteSource,保留源文件夹' 'Yellow'
    }

} catch {
    Write-Stage 'ERROR' $_.Exception.Message 'Red'
    if ($result.ExitCode -eq 0) { $result.ExitCode = 1 }
} finally {
    $result.Duration = (Get-Date) - $startTime
    Write-Stage 'Done' "耗时: $($result.Duration.ToString('mm\:ss\.fff'))" 'Cyan'
}

# 输出结果对象(便于管道消费)
$result
# 显式设置退出码(避免被 robocopy 等内部命令的非零退出码污染)
exit $result.ExitCode
