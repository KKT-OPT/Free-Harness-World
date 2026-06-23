param(
    [ValidateSet("status", "init")]
    [string]$Mode = "status",

    [string]$Root = "",

    [switch]$RunSelfCheck
)

$ErrorActionPreference = "Stop"

function Find-HarnessRoot {
    $dir = $PSScriptRoot
    while ($dir) {
        if (Test-Path -LiteralPath (Join-Path $dir "AGENTS.md")) {
            return $dir
        }
        $parent = Split-Path -Parent $dir
        if (-not $parent -or $parent -eq $dir) {
            break
        }
        $dir = $parent
    }
    throw "Harness root not found from script path: $PSScriptRoot"
}

function Convert-ToRelativePath {
    param(
        [string]$RootPath,
        [string]$Path
    )
    $rootFull = [System.IO.Path]::GetFullPath($RootPath).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $pathFull = [System.IO.Path]::GetFullPath($Path)
    $rootUri = [System.Uri]::new($rootFull + [System.IO.Path]::DirectorySeparatorChar)
    $pathUri = [System.Uri]::new($pathFull)
    return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($pathUri).ToString()).Replace("/", [System.IO.Path]::DirectorySeparatorChar)
}

function Ensure-Directory {
    param(
        [string]$RootPath,
        [string]$RelativePath,
        [System.Collections.ArrayList]$Actions
    )
    $path = Join-Path $RootPath ($RelativePath -replace '/', '\')
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        New-Item -ItemType Directory -Path $path | Out-Null
        [void]$Actions.Add([pscustomobject]@{ action = "created-directory"; path = $RelativePath })
    } else {
        [void]$Actions.Add([pscustomobject]@{ action = "exists-directory"; path = $RelativePath })
    }
}

function Copy-ExampleIfMissing {
    param(
        [string]$RootPath,
        [string]$ExampleRelativePath,
        [string]$TargetRelativePath,
        [System.Collections.ArrayList]$Actions
    )
    $source = Join-Path $RootPath ($ExampleRelativePath -replace '/', '\')
    $target = Join-Path $RootPath ($TargetRelativePath -replace '/', '\')
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Example file missing: $ExampleRelativePath"
    }
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        Copy-Item -LiteralPath $source -Destination $target
        [void]$Actions.Add([pscustomobject]@{ action = "created-local-file"; path = $TargetRelativePath; source = $ExampleRelativePath })
    } else {
        [void]$Actions.Add([pscustomobject]@{ action = "exists-local-file"; path = $TargetRelativePath })
    }
}

function Test-GitIgnored {
    param(
        [string]$RootPath,
        [string]$RelativePath
    )
    $oldLocation = Get-Location
    try {
        Set-Location -LiteralPath $RootPath
        & git check-ignore $RelativePath *> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    } finally {
        Set-Location -LiteralPath $oldLocation
    }
}

$rootPath = if ([string]::IsNullOrWhiteSpace($Root)) { Find-HarnessRoot } else { (Resolve-Path -LiteralPath $Root).Path }
$actions = New-Object System.Collections.ArrayList
$requiredFiles = @(
    "AGENTS.md",
    "INDEX.md",
    "README.md",
    "LICENSE",
    "harness/HarnessIndex.md",
    "harness/architecture/HarnessEngineering.md",
    "harness/architecture/PLANS.md",
    "harness/bootstrap/BootstrapIndex.md",
    "harness/tools/scripts/stable/test-harness-governance.ps1",
    "harness/tools/scripts/stable/test-project-registry.ps1",
    "user/registry/projects.local.example.json",
    "user/registry/knowledge.local.example.json",
    "projects/README.md",
    ".gitignore"
)

if ($Mode -eq "init") {
    foreach ($dir in @("user/registry", "user/knowledge", "projects", "var", "var/logs", "var/tmp", "var/rag")) {
        Ensure-Directory -RootPath $rootPath -RelativePath $dir -Actions $actions
    }
    Copy-ExampleIfMissing -RootPath $rootPath -ExampleRelativePath "user/registry/projects.local.example.json" -TargetRelativePath "user/registry/projects.local.json" -Actions $actions
    Copy-ExampleIfMissing -RootPath $rootPath -ExampleRelativePath "user/registry/knowledge.local.example.json" -TargetRelativePath "user/registry/knowledge.local.json" -Actions $actions
}

$missing = New-Object System.Collections.ArrayList
foreach ($file in $requiredFiles) {
    $path = Join-Path $rootPath ($file -replace '/', '\')
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        [void]$missing.Add($file)
    }
}

$ignoredChecks = @(
    "var/bootstrap-check.tmp",
    "projects/example-project/AGENTS.md",
    "user/registry/projects.local.json",
    "user/registry/knowledge.local.json",
    "user/settings/example.local.json",
    "user/knowledge/example-source/wiki/index.md"
)

$ignoredResults = foreach ($item in $ignoredChecks) {
    [pscustomobject]@{
        path = $item
        ignored = Test-GitIgnored -RootPath $rootPath -RelativePath $item
    }
}

$selfCheck = $null
if ($RunSelfCheck) {
    $selfCheckScript = Join-Path $rootPath "harness/tools/scripts/stable/test-harness-governance.ps1"
    $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $selfCheckScript -Root $rootPath
    $selfCheck = $raw | ConvertFrom-Json
}

$ignoredOk = -not ($ignoredResults | Where-Object { -not $_.ignored })
$status = if ($missing.Count -eq 0 -and $ignoredOk -and (($null -eq $selfCheck) -or $selfCheck.status -eq "passed")) { "passed" } else { "failed" }

[pscustomobject]@{
    status = $status
    mode = $Mode
    root = $rootPath
    requiredFileCount = $requiredFiles.Count
    missingRequiredFiles = $missing
    actions = $actions
    ignoredChecks = $ignoredResults
    selfCheck = $selfCheck
    nextActions = @(
        "Edit user/registry/projects.local.json for real local projects.",
        "Keep projects/<project-id> as independent Git repositories or local workspaces.",
        "Run test-harness-governance.ps1 before committing Harness changes.",
        "Publish only agent-git from agent automation; main remains human-owned."
    )
} | ConvertTo-Json -Depth 8
