# 产物路径合规检查脚本
# 用途：验证任务产物是否按 AGENTS.md 规则放置
# 规则：中间产物 → .temp/，归档产物 → docs/，禁止放仓库根目录
# 用法：pwsh -File check-artifact-paths.ps1 [-RepoRoot <path>]

param(
    [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"

# AGENTS.md 规定的合法产物目录
$validDirs = @(
    ".temp",
    "apps",
    "docs",
    ".github",
    ".git",
    ".agents",
    "node_modules",
    "rebirth"
)

# 仓库根目录下不应出现的产物文件扩展名
$forbiddenExtensions = @(
    ".md", ".html", ".pdf", ".docx", ".pptx", ".xlsx", ".json", ".csv"
)

# 但这些根目录文件是合法的
$allowedRootFiles = @(
    "AGENTS.md",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    ".gitignore",
    ".gitattributes",
    "package.json",
    "package-lock.json",
    "pyproject.toml",
    "uv.lock",
    ".env",
    ".env.example"
)

Write-Host "=== 产物路径合规检查 ===" -ForegroundColor Cyan
Write-Host "仓库根目录: $RepoRoot" -ForegroundColor Gray
Write-Host ""

$errors = @()
$warnings = @()

# 检查 1：仓库根目录下不应有产物文件
$rootFiles = Get-ChildItem -Path $RepoRoot -File -Force | Where-Object { $_.Extension -in $forbiddenExtensions }

foreach ($file in $rootFiles) {
    if ($file.Name -notin $allowedRootFiles) {
        $errors += "根目录违规文件: $($file.Name) → 应放入 .temp/ 或 docs/"
    }
}

# 检查 2：.temp/ 目录命名规范（task-summary-{topic}-{date} 或 {topic}-article-extract-{date}）
$tempDir = Join-Path $RepoRoot ".temp"
if (Test-Path $tempDir) {
    $tempFiles = Get-ChildItem -Path $tempDir -File -Force | Where-Object { $_.Extension -in @(".md", ".json", ".html") }
    foreach ($file in $tempFiles) {
        $name = $file.BaseName
        # 检查是否包含日期模式 YYYYMMDD
        if ($name -notmatch '\d{8}' -and $name -notmatch '^\.' -and $name -ne 'README') {
            $warnings += ".temp/ 文件未含日期: $($file.Name) → 建议命名: {topic}-{date}.md"
        }
    }

    # 检查 .temp/ 子目录
    $tempDirs = Get-ChildItem -Path $tempDir -Directory -Force
    foreach ($dir in $tempDirs) {
        $name = $dir.Name
        if ($name -notmatch '\d{8}') {
            $warnings += ".temp/ 子目录未含日期: $name → 建议命名: {topic}-{date}/"
        }
    }
}

# 检查 3：docs/ 下归档文件命名规范
$docsTechDir = Join-Path $RepoRoot "apps\chaos\docs\tech"
if (Test-Path $docsTechDir) {
    $techFiles = Get-ChildItem -Path $docsTechDir -File -Force | Where-Object { $_.Extension -eq ".md" }
    foreach ($file in $techFiles) {
        $name = $file.BaseName
        if ($name -notmatch '\d{8}$') {
            $warnings += "docs/tech/ 文件未以日期结尾: $($file.Name) → 建议命名: {topic}-{date}.md"
        }
    }
}

# 输出结果
if ($errors.Count -gt 0) {
    Write-Host "[FAIL] 发现 $($errors.Count) 个违规:" -ForegroundColor Red
    foreach ($e in $errors) {
        Write-Host "  ✗ $e" -ForegroundColor Red
    }
}

if ($warnings.Count -gt 0) {
    Write-Host "[WARN] 发现 $($warnings.Count) 个警告:" -ForegroundColor Yellow
    foreach ($w in $warnings) {
        Write-Host "  ⚠ $w" -ForegroundColor Yellow
    }
}

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "[PASS] 所有产物路径合规" -ForegroundColor Green
}

Write-Host ""
Write-Host "检查规则:" -ForegroundColor Gray
Write-Host "  - 仓库根目录禁止放置产物文件（.md/.html/.pdf 等）" -ForegroundColor Gray
Write-Host "  - 中间产物放入 .temp/，命名含日期 YYYYMMDD" -ForegroundColor Gray
Write-Host "  - 归档产物放入 docs/tech/ 或 docs/topics/，命名以日期结尾" -ForegroundColor Gray

# 退出码：有错误返回 1，仅警告返回 0
if ($errors.Count -gt 0) { exit 1 } else { exit 0 }
