# 使用四段一致性模型检查 Podman 环境：入口 -> 实例 -> 指向 -> 任务。
# 自动修复范围：
# - 没有 running machine 时启动默认 Podman machine；
# - default connection 未指向 running machine 时自动切换。
$ErrorActionPreference = 'Stop'

$script:AutoFixes = @()
$script:StageResults = [ordered]@{
    Entry = 'PENDING'
    Instance = 'PENDING'
    Pointer = 'PENDING'
    Task = 'PENDING'
}

function Write-Ok([string]$Message) { Write-Host "[OK] $Message" }
function Write-Warn([string]$Message) { Write-Host "[WARN] $Message" }
function Write-Fail([string]$Message) { Write-Error "[FAIL] $Message" }
function Write-Info([string]$Message) { Write-Host "[INFO] $Message" }
function Write-DebugLog([string]$Message) { Write-Host "[DEBUG] $Message" }
function Write-Step([string]$Message) { Write-Host "`n== $Message ==" }

function Format-CommandLine {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    return "podman $($Arguments -join ' ')"
}

function Invoke-PodmanText {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $commandLine = Format-CommandLine $Arguments
    Write-DebugLog "run: $commandLine"
    $output = & podman @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    Write-DebugLog "exit($commandLine): $exitCode"
    if ($output) {
        Write-DebugLog "output($commandLine):"
        $output | ForEach-Object { Write-Host $_ }
    }
    if ($exitCode -ne 0) {
        throw ($output -join "`n")
    }
    return $output
}

function Get-FirstRunningMachine {
    Write-DebugLog 'parse running machine from: podman machine list --format {{.Name}} {{.Running}}'
    try {
        $lines = Invoke-PodmanText @('machine', 'list', '--format', '{{.Name}} {{.Running}}')
    } catch {
        Write-DebugLog "running machine parse failed: $_"
        return $null
    }

    foreach ($line in $lines) {
        $parts = ($line -split '\s+') | Where-Object { $_ }
        if ($parts.Count -ge 2 -and $parts[1] -match '^(?i:true)$') {
            $name = $parts[0].TrimEnd('*')
            Write-DebugLog "parsed running machine: $name"
            return $name
        }
    }
    Write-DebugLog 'parsed running machine: <none>'
    return $null
}

function Get-DefaultMachineName {
    Write-DebugLog 'parse default machine from: podman machine list --format {{.Name}} {{.Default}}'
    try {
        $lines = Invoke-PodmanText @('machine', 'list', '--format', '{{.Name}} {{.Default}}')
    } catch {
        Write-DebugLog "default machine parse failed: $_"
        return $null
    }

    foreach ($line in $lines) {
        $parts = ($line -split '\s+') | Where-Object { $_ }
        if ($parts.Count -ge 2 -and $parts[1] -match '^(?i:true)$') {
            $name = $parts[0].TrimEnd('*')
            Write-DebugLog "parsed default machine: $name"
            return $name
        }
    }
    Write-DebugLog 'parsed default machine: <none>'
    return $null
}

function Get-DefaultConnectionName {
    Write-DebugLog 'parse default connection from: podman system connection list --format {{.Name}} {{.Default}}'
    try {
        $lines = Invoke-PodmanText @('system', 'connection', 'list', '--format', '{{.Name}} {{.Default}}')
    } catch {
        Write-DebugLog "default connection parse failed: $_"
        return $null
    }

    foreach ($line in $lines) {
        $parts = ($line -split '\s+') | Where-Object { $_ }
        if ($parts.Count -ge 2 -and $parts[1] -match '^(?i:true)$') {
            Write-DebugLog "parsed default connection: $($parts[0])"
            return $parts[0]
        }
    }
    Write-DebugLog 'parsed default connection: <none>'
    return $null
}

function Start-PodmanMachine {
    param([Parameter(Mandatory = $true)][string]$Name)

    Write-Info "auto-fix: ensure Podman machine '$Name' is running"
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = & podman machine start $Name 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    Write-DebugLog "exit(podman machine start $Name): $exitCode"
    if ($output) {
        Write-DebugLog "output(podman machine start $Name):"
        $output | ForEach-Object { Write-Host $_ }
    }

    if ($exitCode -ne 0) {
        $text = $output -join "`n"
        if ($text -match 'already running') {
            Write-Info "recoverable state: machine '$Name' is already running or still transitioning to running."
            $script:AutoFixes += "confirmed machine already running/starting: $Name"
            Start-Sleep -Seconds 2
            return
        }
        Write-Fail "non-recoverable machine start failure for '$Name'."
        throw $text
    }

    $script:AutoFixes += "started default machine: $Name"
    Start-Sleep -Seconds 2
}

function Test-ConnectionExists {
    param([Parameter(Mandatory = $true)][string]$Name)

    Write-DebugLog "check connection exists: $Name"
    try {
        $names = Invoke-PodmanText @('system', 'connection', 'list', '--format', '{{.Name}}')
    } catch {
        Write-DebugLog "connection existence check failed: $_"
        return $false
    }
    $exists = $names -contains $Name
    Write-DebugLog "connection exists($Name): $exists"
    return $exists
}

Write-Step '0. Script context'
Write-Info "timestamp: $((Get-Date).ToString('o'))"
Write-Info "script: $PSCommandPath"
Write-Info "cwd: $(Get-Location)"
Write-Info "os: $([System.Runtime.InteropServices.RuntimeInformation]::OSDescription)"
Write-Info "powershell: $($PSVersionTable.PSVersion)"

Write-Step '1. Entry: podman CLI'
$podmanCommand = Get-Command podman -ErrorAction SilentlyContinue
if (-not $podmanCommand) {
    $script:StageResults.Entry = 'FAIL'
    Write-Fail 'podman command not found. Install Podman or fix PATH.'
    exit 127
}
Write-Info "podman path: $($podmanCommand.Source)"
$podmanVersion = Invoke-PodmanText @('--version')
Write-Ok ($podmanVersion -join ' ')
$script:StageResults.Entry = 'OK'

Write-Step '2. Instance: Podman backend or machine'
$runningMachine = $null
$machineSupported = $true
try {
    Write-Info 'raw machine list:'
    Invoke-PodmanText @('machine', 'list') | Out-Null
} catch {
    $machineSupported = $false
    Write-Warn "podman machine list is unavailable or unsupported; treating this as native/service-based Podman. detail: $_"
}

if ($machineSupported) {
    $runningMachine = Get-FirstRunningMachine
    $defaultMachine = Get-DefaultMachineName
    $shownRunningMachine = $runningMachine
    if (-not $shownRunningMachine) { $shownRunningMachine = '<none>' }
    $shownDefaultMachine = $defaultMachine
    if (-not $shownDefaultMachine) { $shownDefaultMachine = '<none>' }
    Write-Info "parsed running machine: $shownRunningMachine"
    Write-Info "parsed default machine: $shownDefaultMachine"
    if ($runningMachine) {
        Write-Ok "running machine: $runningMachine"
    } elseif ($defaultMachine) {
        Write-Warn "no running Podman machine found; starting default machine '$defaultMachine'."
        Start-PodmanMachine $defaultMachine
        $runningMachine = Get-FirstRunningMachine
        if ($runningMachine) {
            Write-Ok "running machine after auto-fix: $runningMachine"
        } else {
            Write-Warn "machine '$defaultMachine' is starting; continuing to task-level verification."
        }
    } else {
        Write-Warn 'no running or default Podman machine found; this may be fine on native Linux.'
    }
}
$script:StageResults.Instance = 'OK'

Write-Step '3. Pointer: default connection'
$defaultConnection = Get-DefaultConnectionName
try {
    Write-Info 'raw connection list:'
    Invoke-PodmanText @('system', 'connection', 'list') | Out-Null
} catch {
    Write-Warn "podman system connection list is unavailable or unsupported. detail: $_"
}

$shownDefaultConnection = $defaultConnection
if (-not $shownDefaultConnection) { $shownDefaultConnection = '<none>' }
Write-Info "parsed default connection: $shownDefaultConnection"
if ($defaultConnection) {
    Write-Ok "default connection: $defaultConnection"
} else {
    Write-Warn 'no default Podman connection found; this may be fine on native Linux.'
}

if ($runningMachine -and $defaultConnection -ne $runningMachine) {
    if (Test-ConnectionExists $runningMachine) {
        $shownDefaultConnection = $defaultConnection
        if (-not $shownDefaultConnection) {
            $shownDefaultConnection = '<none>'
        }
        Write-Warn "default connection points to '$shownDefaultConnection', switching to '$runningMachine'."
        Invoke-PodmanText @('system', 'connection', 'default', $runningMachine) | Out-Null
        $script:AutoFixes += "switched default connection: $shownDefaultConnection -> $runningMachine"
        $defaultConnection = Get-DefaultConnectionName
        $shownDefaultConnectionAfterFix = $defaultConnection
        if (-not $shownDefaultConnectionAfterFix) { $shownDefaultConnectionAfterFix = '<none>' }
        Write-Info "default connection after auto-fix: $shownDefaultConnectionAfterFix"
        if ($defaultConnection -eq $runningMachine) {
            Write-Ok "default connection switched to $runningMachine"
        } else {
            $script:StageResults.Pointer = 'FAIL'
            Write-Fail "failed to switch default connection to $runningMachine"
            exit 1
        }
    } else {
        Write-Warn "running machine '$runningMachine' has no matching system connection; skip auto-fix."
    }
}
$script:StageResults.Pointer = 'OK'

Write-Step '4. Task: podman info and smoke command'
try {
    Write-Info 'run task verification: podman info'
    Invoke-PodmanText @('info') | Out-Null
    Write-Ok 'podman info succeeded'
} catch {
    $script:StageResults.Task = 'FAIL'
    Write-Fail "podman info failed. Backend, socket, or connection is still not usable.`n$_"
    exit 1
}

try {
    Write-Info 'run task verification: podman ps'
    Invoke-PodmanText @('ps') | Out-Null
    Write-Ok 'podman ps succeeded'
} catch {
    $script:StageResults.Task = 'FAIL'
    Write-Fail "podman ps failed. Podman is reachable but basic container listing failed.`n$_"
    exit 1
}
$script:StageResults.Task = 'OK'

Write-Step '5. Summary'
foreach ($key in $script:StageResults.Keys) {
    Write-Host "[$($script:StageResults[$key])] $key"
}
if ($script:AutoFixes.Count -gt 0) {
    Write-Info 'auto-fixes applied:'
    $script:AutoFixes | ForEach-Object { Write-Host "- $_" }
} else {
    Write-Info 'auto-fixes applied: none'
}
Write-Host "`nPodman four-stage consistency check passed."
