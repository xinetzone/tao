<#
.SYNOPSIS
    Static Site Asset Redundancy Analyzer
.DESCRIPTION
    Identifies "declared but missing" and "exists but unreferenced" redundancy in static sites.
    Implements the "Static Asset Redundancy Analysis Three-Step Method":
    HTML reference extraction -> File existence validation -> Unreferenced file identification.
    Optional SHA256 hash comparison to identify exact duplicates.
.PARAMETER Path
    Absolute path to the static site directory.
.PARAMETER IncludeHash
    Enable SHA256 hash comparison to identify duplicate files.
.PARAMETER WhatIf
    Preview mode (this skill is read-only by default, this only affects output format).
.PARAMETER Format
    Output format: text (human-readable) or json (machine-readable).
.EXAMPLE
    .\Analyze-Redundancy.ps1 -Path "D:\docs\react-survey"
.EXAMPLE
    .\Analyze-Redundancy.ps1 -Path "D:\docs\react-survey" -IncludeHash -Format json
.NOTES
    Version: 1.0.0
    Dependencies: PowerShell 5.1+, no external dependencies
#>

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [string]$Path,

    [switch]$IncludeHash,

    [string]$Format = "text"
)

# ============================================================================
# Stage 0: Parameter validation
# ============================================================================

if (-not (Test-Path $Path -PathType Container)) {
    Write-Error "Path does not exist or is not a directory: $Path"
    exit 1
}

$Path = (Resolve-Path $Path).Path
$whatIfPrefix = if ($WhatIfPreference) { "[WhatIf] " } else { "" }

Write-Host "${whatIfPrefix}=== Asset Redundancy Analyzer v1.0.0 ===" -ForegroundColor Cyan
Write-Host "${whatIfPrefix}Path: $Path" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Stage 1: Scan directory for HTML files
# ============================================================================

Write-Host "${whatIfPrefix}[Stage 1] Scanning directory..." -ForegroundColor Yellow

$allFiles = Get-ChildItem -Path $Path -Recurse -File
$htmlFiles = $allFiles | Where-Object { $_.Extension -in @('.html', '.htm') }

if ($htmlFiles.Count -eq 0) {
    Write-Error "No HTML files found"
    exit 1
}

Write-Host "${whatIfPrefix}  Found $($htmlFiles.Count) HTML file(s), $($allFiles.Count) total file(s)"

# ============================================================================
# Stage 2: Extract HTML references
# ============================================================================

Write-Host "${whatIfPrefix}[Stage 2] Extracting HTML references..." -ForegroundColor Yellow

# Build regex patterns using escaped quotes to avoid variable expansion issues
# In PowerShell double-quoted strings, `" is an escaped double quote, ' is literal
$patterns = @(
    @{ Type = 'script';    Regex = "(?i)<script[^>]+src=[`"`']([^`"`']+)[`"`']" },
    @{ Type = 'img';       Regex = "(?i)<img[^>]+src=[`"`']([^`"`']+)[`"`']" },
    @{ Type = 'link';      Regex = "(?i)<link[^>]+href=[`"`']([^`"`']+)[`"`']" },
    @{ Type = 'font-face'; Regex = "(?i)url\([`"`']?([^`"`')]+)[`"`']?\)" },
    @{ Type = 'a';         Regex = "(?i)<a[^>]+href=[`"`']([^`"`']+)[`"`']" }
)

$declaredRefs = @()

foreach ($html in $htmlFiles) {
    $content = $null
    try {
        $content = [System.IO.File]::ReadAllText($html.FullName, [System.Text.Encoding]::UTF8)
    } catch {
        $content = Get-Content $html.FullName -Raw -ErrorAction SilentlyContinue
    }
    if (-not $content) { continue }

    foreach ($pat in $patterns) {
        $matches = [regex]::Matches($content, $pat.Regex)
        foreach ($m in $matches) {
            $ref = $m.Groups[1].Value
            # Skip external URLs, anchors, data URIs, javascript:
            if ($ref -match '^(https?:)?//' -or
                $ref -match '^#' -or
                $ref -match '^data:' -or
                $ref -match '^javascript:' -or
                $ref -match '^mailto:' -or
                $ref -match '^tel:') {
                continue
            }
            $declaredRefs += [PSCustomObject]@{
                RefFile  = $html.Name
                RefType  = $pat.Type
                Declared = $ref
            }
        }
    }
}

Write-Host "${whatIfPrefix}  Extracted $($declaredRefs.Count) local reference(s)"

# ============================================================================
# Stage 3: File existence validation (identify "declared but missing")
# ============================================================================

Write-Host "${whatIfPrefix}[Stage 3] Validating file existence..." -ForegroundColor Yellow

$missingFiles = @()
$validRefs = @()

foreach ($ref in $declaredRefs) {
    $refPath = $ref.Declared
    # Remove query parameters and anchors
    $refPath = $refPath -replace '[?#].*$',''
    # Remove ./ prefix
    $refPath = $refPath -replace '^\./',''
    # Resolve relative to site root
    $absPath = Join-Path $Path $refPath
    # Handle ../ prefixes
    while ($refPath -match '^\.\./') {
        $refPath = $refPath -replace '^\.\./',''
        $absPath = Join-Path $Path $refPath
    }

    if (Test-Path $absPath -PathType Leaf) {
        $validRefs += $ref
    } else {
        $missingFiles += [PSCustomObject]@{
            RefFile    = $ref.RefFile
            RefType    = $ref.RefType
            Declared   = $ref.Declared
            Issue      = 'FileNotFound'
            Suggestion = 'Remove declaration or add missing file'
        }
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "${whatIfPrefix}  Found $($missingFiles.Count) declared but missing file(s)" -ForegroundColor Red
} else {
    Write-Host "${whatIfPrefix}  All declared references exist"
}

# ============================================================================
# Stage 4: Unreferenced file identification (identify "exists but unreferenced")
# ============================================================================

Write-Host "${whatIfPrefix}[Stage 4] Identifying unreferenced files..." -ForegroundColor Yellow

# Build set of referenced file relative paths
$referencedSet = @{}
foreach ($ref in $validRefs) {
    $refPath = $ref.Declared -replace '[?#].*$',''
    $refPath = $refPath -replace '^\./',''
    $referencedSet[$refPath.ToLower()] = $true
}

# HTML files themselves are considered referenced
foreach ($html in $htmlFiles) {
    $relPath = $html.FullName.Substring($Path.Length).TrimStart('\','/') -replace '\\','/'
    $referencedSet[$relPath.ToLower()] = $true
}

$unreferencedFiles = @()

foreach ($file in $allFiles) {
    $relPath = $file.FullName.Substring($Path.Length).TrimStart('\','/') -replace '\\','/'
    # Skip HTML files
    if ($file.Extension -in @('.html', '.htm')) { continue }
    # Check if referenced
    if (-not $referencedSet.ContainsKey($relPath.ToLower())) {
        # Also check by filename (some references may use different path formats)
        $fileName = $file.Name
        $isReferenced = $false
        foreach ($key in $referencedSet.Keys) {
            if ($key -like "*$fileName*") {
                $isReferenced = $true
                break
            }
        }
        if (-not $isReferenced) {
            $sizeReadable = if ($file.Length -ge 1MB) {
                "{0:N2} MB" -f ($file.Length / 1MB)
            } elseif ($file.Length -ge 1KB) {
                "{0:N2} KB" -f ($file.Length / 1KB)
            } else {
                "$($file.Length) B"
            }
            $unreferencedFiles += [PSCustomObject]@{
                File         = "./$relPath"
                Size         = $file.Length
                SizeReadable = $sizeReadable
                Issue        = 'NotReferenced'
                Suggestion   = 'Delete'
            }
        }
    }
}

if ($unreferencedFiles.Count -gt 0) {
    $totalUnrefSize = ($unreferencedFiles | Measure-Object -Property Size -Sum).Sum
    $totalUnrefReadable = if ($totalUnrefSize -ge 1MB) {
        "{0:N2} MB" -f ($totalUnrefSize / 1MB)
    } elseif ($totalUnrefSize -ge 1KB) {
        "{0:N2} KB" -f ($totalUnrefSize / 1KB)
    } else {
        "$totalUnrefSize B"
    }
    Write-Host "${whatIfPrefix}  Found $($unreferencedFiles.Count) unreferenced file(s) (total $totalUnrefReadable)" -ForegroundColor Red
} else {
    Write-Host "${whatIfPrefix}  All files are referenced"
}

# ============================================================================
# Stage 5: Hash comparison (optional, identify duplicates)
# ============================================================================

$duplicateFiles = @()

if ($IncludeHash) {
    Write-Host "${whatIfPrefix}[Stage 5] Computing file hashes..." -ForegroundColor Yellow

    $hashMap = @{}
    foreach ($file in $allFiles) {
        try {
            $hash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash
            if (-not $hashMap.ContainsKey($hash)) {
                $hashMap[$hash] = @()
            }
            $relPath = $file.FullName.Substring($Path.Length).TrimStart('\','/') -replace '\\','/'
            $hashMap[$hash] += "./$relPath"
        } catch {
            # Skip unreadable files
        }
    }

    foreach ($hash in $hashMap.Keys) {
        if ($hashMap[$hash].Count -gt 1) {
            $duplicateFiles += [PSCustomObject]@{
                Hash       = $hash
                Files      = $hashMap[$hash]
                Suggestion = 'Merge to common directory or remove redundant copies'
            }
        }
    }

    if ($duplicateFiles.Count -gt 0) {
        Write-Host "${whatIfPrefix}  Found $($duplicateFiles.Count) duplicate file group(s)" -ForegroundColor Red
    } else {
        Write-Host "${whatIfPrefix}  No duplicate files"
    }
}

# ============================================================================
# Stage 6: Decision matrix
# ============================================================================

Write-Host "${whatIfPrefix}[Stage 6] Generating recommendations..." -ForegroundColor Yellow

$recommendations = @()

# Recommendations for unreferenced files
foreach ($unref in $unreferencedFiles) {
    $action = 'Delete'
    $reason = 'Not referenced'
    $priority = 'High'

    # If hash enabled and file has duplicates, suggest merge
    if ($IncludeHash -and $duplicateFiles.Count -gt 0) {
        foreach ($dup in $duplicateFiles) {
            if ($dup.Files -contains $unref.File) {
                $action = 'Merge'
                $reason = 'Not referenced and duplicate of another file'
                $priority = 'High'
                break
            }
        }
    }

    $recommendations += [PSCustomObject]@{
        File     = $unref.File
        Action   = $action
        Reason   = $reason
        Priority = $priority
    }
}

# Recommendations for missing files
foreach ($miss in $missingFiles) {
    $recommendations += [PSCustomObject]@{
        File     = $miss.Declared
        Action   = 'FixDecl'
        Reason   = "Declared in $($miss.RefFile) but file not found"
        Priority = 'Medium'
    }
}

Write-Host "${whatIfPrefix}  Generated $($recommendations.Count) recommendation(s)"

# ============================================================================
# Output report
# ============================================================================

Write-Host ""
Write-Host "${whatIfPrefix}=== Analysis Report ===" -ForegroundColor Cyan
Write-Host ""

if ($Format -eq 'json') {
    $result = [PSCustomObject]@{
        Path              = $Path
        HtmlFiles         = $htmlFiles.Name
        TotalFiles        = $allFiles.Count
        DeclaredRefs      = $declaredRefs.Count
        MissingFiles      = $missingFiles
        UnreferencedFiles = $unreferencedFiles
        DuplicateFiles    = $duplicateFiles
        Recommendations   = $recommendations
        ExitCode          = 0
    }
    $result | ConvertTo-Json -Depth 5
} else {
    # Text format report
    Write-Host "Path: $Path"
    Write-Host "HTML files: $($htmlFiles.Name -join ', ')"
    Write-Host "Total files: $($allFiles.Count)"
    Write-Host "Declared refs: $($declaredRefs.Count)"
    Write-Host ""

    if ($missingFiles.Count -gt 0) {
        Write-Host "--- Declared but Missing ($($missingFiles.Count)) ---" -ForegroundColor Red
        $missingFiles | Format-Table RefFile, RefType, Declared, Suggestion -AutoSize
        Write-Host ""
    }

    if ($unreferencedFiles.Count -gt 0) {
        Write-Host "--- Exists but Unreferenced ($($unreferencedFiles.Count)) ---" -ForegroundColor Red
        $unreferencedFiles | Format-Table File, SizeReadable, Suggestion -AutoSize
        Write-Host ""
    }

    if ($IncludeHash -and $duplicateFiles.Count -gt 0) {
        Write-Host "--- Duplicate Files ($($duplicateFiles.Count) groups) ---" -ForegroundColor Red
        foreach ($dup in $duplicateFiles) {
            Write-Host "  Hash: $($dup.Hash.Substring(0,16))..."
            Write-Host "  Files: $($dup.Files -join ', ')"
            Write-Host "  Suggestion: $($dup.Suggestion)"
            Write-Host ""
        }
    }

    if ($recommendations.Count -gt 0) {
        Write-Host "--- Recommendations ($($recommendations.Count)) ---" -ForegroundColor Yellow
        $recommendations | Format-Table File, Action, Reason, Priority -AutoSize
        Write-Host ""
    }

    if ($missingFiles.Count -eq 0 -and $unreferencedFiles.Count -eq 0 -and $duplicateFiles.Count -eq 0) {
        Write-Host "[OK] No redundancy found, site is healthy" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Redundancy found, please clean up according to recommendations" -ForegroundColor Yellow
    }
}

# Return result object
return [PSCustomObject]@{
    Path              = $Path
    HtmlFiles         = $htmlFiles.Name
    TotalFiles        = $allFiles.Count
    DeclaredRefs      = $declaredRefs.Count
    MissingFiles      = $missingFiles
    UnreferencedFiles = $unreferencedFiles
    DuplicateFiles    = $duplicateFiles
    Recommendations   = $recommendations
    ExitCode          = 0
}
