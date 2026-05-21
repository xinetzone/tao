# -*- coding: utf-8 -*-
"""项目环境初始化脚本。

安装项目所需的外部工具依赖（npm 全局包）。

用法:
    ./init.ps1          # Windows PowerShell
    pwsh -File init.ps1 # PowerShell Core
"""

param(
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Install-IfMissing {
    param(
        [string]$Package,
        [string]$InstallCmd
    )
    if (Test-Command $Package) {
        Write-Host "[SKIP] $Package already installed" -ForegroundColor DarkGray
        return $true
    }
    if ($CheckOnly) {
        Write-Host "[MISSING] $Package not found" -ForegroundColor Yellow
        return $false
    }
    Write-Host "[INSTALL] Installing $Package..." -ForegroundColor Cyan
    Invoke-Expression $InstallCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $Package installed" -ForegroundColor Green
        return $true
    } else {
        Write-Host "[ERROR] Failed to install $Package" -ForegroundColor Red
        return $false
    }
}

Write-Host "=== AgentForge 环境初始化 ===" -ForegroundColor White

$node_ok = Test-Command "node"
if (-not $node_ok) {
    Write-Host "[ERROR] Node.js not found. Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

$npm_ok = Test-Command "npm"
if (-not $npm_ok) {
    Write-Host "[ERROR] npm not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[INFO] Node.js version: $(node --version)" -ForegroundColor Gray
Write-Host "[INFO] npm version: $(npm --version)" -ForegroundColor Gray
Write-Host ""

$allGood = $true

Write-Host "--- 检查工具依赖 ---" -ForegroundColor White

$allGood = (Install-IfMissing "defuddle" "npm install -g defuddle") -and $allGood

Write-Host ""
if ($CheckOnly) {
    if ($allGood) {
        Write-Host "[OK] 所有工具依赖已就绪" -ForegroundColor Green
    } else {
        Write-Host "[WARN] 部分工具依赖缺失，请运行不带 -CheckOnly 参数的脚本安装" -ForegroundColor Yellow
    }
} else {
    Write-Host "=== 初始化完成 ===" -ForegroundColor Green
    Write-Host "运行 'defuddle --help' 验证安装" -ForegroundColor Gray
}
