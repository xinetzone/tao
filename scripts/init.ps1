param(
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")

function Test-Command {
    param([string]$Command)

    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Fail-WithHint {
    param(
        [string]$Message,
        [string]$FixHint
    )

    Write-Host "[ERROR] $Message" -ForegroundColor Red
    if ($FixHint) {
        Write-Host "[FIX]   $FixHint" -ForegroundColor Yellow
    }
    exit 1
}

function Invoke-Step {
    param(
        [string]$Label,
        [scriptblock]$Action,
        [string]$FixHint = ""
    )

    Write-Host "[STEP] $Label" -ForegroundColor Cyan

    try {
        & $Action
        if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) {
            throw "Exit code: $LASTEXITCODE"
        }
        Write-Host "[OK]   $Label" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] $Label" -ForegroundColor Red
        if ($FixHint) {
            Write-Host "[FIX]  $FixHint" -ForegroundColor Yellow
        }
        throw
    }
}

if (-not (Test-Command "mise")) {
    Fail-WithHint `
        "未检测到 mise，请先安装后再初始化项目环境。" `
        "参考安装说明: https://mise.jdx.dev/getting-started.html"
}

Write-Host "=== AgentForge 环境初始化 ===" -ForegroundColor White
Write-Host "[INFO] 仓库根目录: $RepoRoot" -ForegroundColor DarkGray

Push-Location $RepoRoot
try {
    Invoke-Step `
        "信任仓库 mise 配置" `
        { & mise trust } `
        "可手动运行: mise trust"

    if ($CheckOnly) {
        Invoke-Step `
            "校验当前工具链与版本基线" `
            { & mise run check-env } `
            "可手动运行: mise install ; mise run check-env"

        Write-Host ""
        Write-Host "[OK] 环境检查完成" -ForegroundColor Green
        Write-Host "建议后续命令: mise run test / mise run lint / mise run docs-html" -ForegroundColor DarkGray
        exit 0
    }

    Invoke-Step `
        "安装 mise 工具链 (Python 3.14.5 / uv 0.11.16 / Node 22.22.3 等)" `
        { & mise install } `
        "可手动运行: mise install"

    Invoke-Step `
        "同步 Python 依赖组" `
        { & mise run sync } `
        "可手动运行: mise run sync"

    Invoke-Step `
        "执行环境一致性校验" `
        { & mise run check-env } `
        "可手动运行: mise run check-env"

    Write-Host ""
    Write-Host "[OK] 初始化完成" -ForegroundColor Green
    Write-Host "常用入口: mise run test / mise run lint / mise run docs-html" -ForegroundColor DarkGray
} finally {
    Pop-Location
}
