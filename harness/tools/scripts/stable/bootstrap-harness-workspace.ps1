param(
    [ValidateSet("status", "init", "install", "uninstall")]
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

function Write-JsonIfMissing {
    param(
        [string]$RootPath,
        [string]$RelativePath,
        [object]$Value,
        [string]$SourceDescription,
        [System.Collections.ArrayList]$Actions
    )
    $target = Join-Path $RootPath ($RelativePath -replace '/', '\')
    Assert-UnderHarnessRoot -RootPath $RootPath -Path $target
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        $json = $Value | ConvertTo-Json -Depth 8
        Set-Content -LiteralPath $target -Value $json -Encoding UTF8
        [void]$Actions.Add([pscustomobject]@{ action = "created-local-file"; path = $RelativePath; source = $SourceDescription })
    } else {
        [void]$Actions.Add([pscustomobject]@{ action = "exists-local-file"; path = $RelativePath })
    }
}

function Assert-UnderHarnessRoot {
    param(
        [string]$RootPath,
        [string]$Path
    )
    $rootFull = [System.IO.Path]::GetFullPath($RootPath).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $pathFull = [System.IO.Path]::GetFullPath($Path)
    if (-not $pathFull.StartsWith($rootFull + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to operate outside Harness root: $pathFull"
    }
}

function Remove-LocalFileIfExists {
    param(
        [string]$RootPath,
        [string]$RelativePath,
        [System.Collections.ArrayList]$Actions
    )
    $path = Join-Path $RootPath ($RelativePath -replace '/', '\')
    Assert-UnderHarnessRoot -RootPath $RootPath -Path $path
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        Remove-Item -LiteralPath $path
        [void]$Actions.Add([pscustomobject]@{ action = "removed-local-file"; path = $RelativePath })
    } else {
        [void]$Actions.Add([pscustomobject]@{ action = "missing-local-file"; path = $RelativePath })
    }
}

function Remove-EmptyDirectoryIfExists {
    param(
        [string]$RootPath,
        [string]$RelativePath,
        [System.Collections.ArrayList]$Actions
    )
    $path = Join-Path $RootPath ($RelativePath -replace '/', '\')
    Assert-UnderHarnessRoot -RootPath $RootPath -Path $path
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        [void]$Actions.Add([pscustomobject]@{ action = "missing-directory"; path = $RelativePath })
        return
    }
    $children = @(Get-ChildItem -LiteralPath $path -Force)
    if ($children.Count -eq 0) {
        Remove-Item -LiteralPath $path
        [void]$Actions.Add([pscustomobject]@{ action = "removed-empty-directory"; path = $RelativePath })
    } else {
        [void]$Actions.Add([pscustomobject]@{ action = "kept-nonempty-directory"; path = $RelativePath })
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
$installDirs = @("user/registry", "user/knowledge", "projects", "var", "var/logs", "var/tmp", "var/rag")
$localRegistryFiles = @(
    @{ Example = "user/registry/projects.local.example.json"; Target = "user/registry/projects.local.json" },
    @{ Example = "user/registry/knowledge.local.example.json"; Target = "user/registry/knowledge.local.json" }
)
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

if ($Mode -in @("init", "install")) {
    foreach ($dir in $installDirs) {
        Ensure-Directory -RootPath $rootPath -RelativePath $dir -Actions $actions
    }
    Write-JsonIfMissing -RootPath $rootPath -RelativePath "user/registry/projects.local.json" -SourceDescription "empty-install-registry" -Actions $actions -Value ([pscustomobject]@{
        schemaVersion = "harness.projects.v1"
        registryKind = "local"
        projects = @()
    })
    Write-JsonIfMissing -RootPath $rootPath -RelativePath "user/registry/knowledge.local.json" -SourceDescription "empty-install-registry" -Actions $actions -Value ([pscustomobject]@{
        schemaVersion = "harness.knowledgeRegistry.v1"
        registryKind = "local"
        knowledgeSources = @()
    })
}

if ($Mode -eq "uninstall") {
    foreach ($file in $localRegistryFiles) {
        Remove-LocalFileIfExists -RootPath $rootPath -RelativePath $file.Target -Actions $actions
    }
    foreach ($dir in @("var/logs", "var/tmp", "var/rag", "var")) {
        Remove-EmptyDirectoryIfExists -RootPath $rootPath -RelativePath $dir -Actions $actions
    }
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
        "Use -Mode install for first-run local workspace setup; init remains a compatibility alias.",
        "Use -Mode uninstall to remove generated local registry files and empty runtime directories without deleting the Git clone.",
        "Edit user/registry/projects.local.json for real local projects.",
        "Keep projects/<project-id> as independent Git repositories or local workspaces.",
        "Run test-harness-governance.ps1 before committing Harness changes.",
        "Publish only agent-git from agent automation; main remains human-owned."
    )
} | ConvertTo-Json -Depth 8
