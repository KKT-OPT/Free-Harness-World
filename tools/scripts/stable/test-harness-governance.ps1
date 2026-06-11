param(
    [string]$Root = ".",
    [string]$Registry = "user/registry/projects.local.json"
)

$ErrorActionPreference = "Stop"

function New-Finding {
    param(
        [string]$Severity,
        [string]$Code,
        [string]$Path,
        [string]$Message,
        [string]$RepairSuggestion
    )

    [pscustomobject]@{
        severity = $Severity
        code = $Code
        path = $Path
        message = $Message
        repairSuggestion = $RepairSuggestion
    }
}

function Add-Finding {
    param(
        [System.Collections.ArrayList]$List,
        [string]$Severity,
        [string]$Code,
        [string]$Path,
        [string]$Message,
        [string]$RepairSuggestion
    )

    [void]$List.Add((New-Finding -Severity $Severity -Code $Code -Path $Path -Message $Message -RepairSuggestion $RepairSuggestion))
}

function Convert-ToRelativePath {
    param(
        [string]$RootPath,
        [string]$Path
    )

    $full = [System.IO.Path]::GetFullPath($Path)
    $rootFull = [System.IO.Path]::GetFullPath($RootPath)
    if ($full.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $full.Substring($rootFull.Length).TrimStart('\', '/') -replace '\\', '/'
    }
    return $Path -replace '\\', '/'
}

function Test-IsExcludedPath {
    param([string]$RelativePath)

    $normalized = $RelativePath -replace '\\', '/'
    $excludedPrefixes = @(
        ".git/",
        "var/",
        "user/settings/",
        "tools/external/",
        "tools/scripts/historical/",
        "tools/scripts/runtime/",
        "projects/",
        "node_modules/",
        ".idea/",
        ".gradle/",
        ".obsidian/"
    )

    foreach ($prefix in $excludedPrefixes) {
        if ($normalized.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }

    if ($normalized -match '^user/registry/.+\.private\.json$') {
        return $true
    }

    return $false
}

function Get-TextFilesForGovernanceScan {
    param([string]$RootPath)

    $extensions = @(".md", ".json", ".yaml", ".yml", ".ps1", ".txt", ".gitignore")
    Get-ChildItem -LiteralPath $RootPath -Recurse -File -Force |
        Where-Object {
            $relative = Convert-ToRelativePath -RootPath $RootPath -Path $_.FullName
            -not (Test-IsExcludedPath -RelativePath $relative) -and
            ($extensions -contains $_.Extension.ToLowerInvariant() -or $_.Name -eq ".gitignore")
        }
}

function Test-RouteCandidate {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) { return $false }
    if ($Value -match '[<>*{}]') { return $false }
    if ($Value -match '^\w+://') { return $false }
    if ($Value -match '^[a-zA-Z0-9_.-]+$') { return $false }
    if ($Value -eq 'docs/project') { return $false }
    if ($Value -match '[/\\]target$') { return $false }
    if ($Value -match '^[A-Za-z]:\\') { return $true }
    if ($Value -match '^(AGENTS\.md|README\.md|docs/|docs\\|harness/|harness\\|adapter/|adapter\\|tools/|tools\\|user/|user\\|projects/|projects\\|rag/|rag\\|sandbox/|sandbox\\|var/|var\\)') { return $true }
    return $false
}

function Resolve-RouteCandidate {
    param(
        [string]$RootPath,
        [string]$Value
    )

    $candidate = $Value.Trim()
    if ($candidate -match '^[A-Za-z]:\\') {
        return $candidate
    }
    return Join-Path $RootPath ($candidate -replace '/', '\')
}

function Test-StaleRouteCandidates {
    param(
        [string]$RootPath,
        [System.Collections.ArrayList]$Findings
    )

    $routeFiles = @(
        "README.md",
        "AGENTS.md",
        "harness/INDEX.md",
        "harness/PLANS.md",
        "docs/INDEX.md",
        "docs/PLANS.md",
        "docs/architecture/HarnessEngineering.md"
    )
    $pattern = '`([^`]+)`'

    foreach ($routeFile in $routeFiles) {
        $path = Join-Path $RootPath ($routeFile -replace '/', '\')
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { continue }
        $text = Get-Content -Raw -LiteralPath $path
        $matches = [regex]::Matches($text, $pattern)
        foreach ($match in $matches) {
            $value = $match.Groups[1].Value.Trim()
            if (-not (Test-RouteCandidate -Value $value)) { continue }
            if ($value -match '\s') { continue }
            $resolved = Resolve-RouteCandidate -RootPath $RootPath -Value $value
            if (-not (Test-Path -LiteralPath $resolved)) {
                Add-Finding -List $Findings -Severity "warning" -Code "staleRouteCandidate" -Path $routeFile -Message "Route candidate does not currently resolve: $value" -RepairSuggestion "If this is a real route, create it or update the index; if it is only a pattern, keep it outside default route lists."
            }
        }
    }
}

function Invoke-ProjectRegistryCheck {
    param(
        [string]$RootPath,
        [string]$RegistryPath,
        [System.Collections.ArrayList]$Findings
    )

    $script = Join-Path $RootPath "tools/scripts/stable/test-project-registry.ps1"
    if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
        Add-Finding -List $Findings -Severity "error" -Code "registryValidatorMissing" -Path "tools/scripts/stable/test-project-registry.ps1" -Message "Registry validator is missing." -RepairSuggestion "Restore tools/scripts/stable/test-project-registry.ps1 or update ProjectRegistrationModel."
        return $null
    }

    try {
        $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $script -Root $RootPath -Registry $RegistryPath
        $result = $raw | ConvertFrom-Json
        if ($result.status -ne "passed") {
            Add-Finding -List $Findings -Severity "error" -Code "projectRegistryFailed" -Path $RegistryPath -Message "Project registry validation failed." -RepairSuggestion "Run test-project-registry.ps1 directly and repair listed registry findings."
        }
        return $result
    } catch {
        Add-Finding -List $Findings -Severity "error" -Code "projectRegistryCheckError" -Path $RegistryPath -Message "Project registry check errored: $($_.Exception.Message)" -RepairSuggestion "Fix the registry validator or local registry file."
        return $null
    }
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$findings = New-Object System.Collections.ArrayList

$requiredRoutes = @(
    "AGENTS.md",
    "README.md",
    "harness/INDEX.md",
    "harness/PLANS.md",
    "harness/architecture/HarnessEngineering.md",
    "harness/governance/GovernanceIndex.md",
    "harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md",
    "tools/docs/script-index/ScriptIndex.md",
    "adapter/task-intake/TaskIntakeWorkflowModel.md",
    "user/registry/projects.local.json",
    "tools/scripts/stable/test-project-registry.ps1",
    "docs/INDEX.md",
    "docs/PLANS.md",
    "docs/architecture/HarnessEngineering.md"
)

foreach ($route in $requiredRoutes) {
    $path = Join-Path $rootPath ($route -replace '/', '\')
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Finding -List $findings -Severity "error" -Code "requiredRouteMissing" -Path $route -Message "Required route does not exist." -RepairSuggestion "Restore the route or update harness/INDEX.md and harness/PLANS.md."
    }
}

Test-StaleRouteCandidates -RootPath $rootPath -Findings $findings

$docsRoot = Join-Path $rootPath "docs"
if (-not (Test-Path -LiteralPath $docsRoot -PathType Container)) {
    Add-Finding -List $findings -Severity "error" -Code "docsStubRootMissing" -Path "docs" -Message "docs compatibility root is missing." -RepairSuggestion "Restore docs stubs or remove compatibility route after review."
} else {
    $allowedDocsFiles = @(
        "docs/INDEX.md",
        "docs/PLANS.md",
        "docs/architecture/HarnessEngineering.md"
    )
    $docsFiles = Get-ChildItem -LiteralPath $docsRoot -Recurse -File -Force
    foreach ($file in $docsFiles) {
        $relative = Convert-ToRelativePath -RootPath $rootPath -Path $file.FullName
        if ($allowedDocsFiles -notcontains $relative) {
            Add-Finding -List $findings -Severity "error" -Code "docsNonStubFilePresent" -Path $relative -Message "docs contains a non-stub file after P12.4." -RepairSuggestion "Move durable content to harness/, adapter/, tools/, rag/ or user/, then keep only compatibility stubs under docs/."
            continue
        }
        $text = Get-Content -Raw -LiteralPath $file.FullName
        if ($text -notmatch 'compatibility-stub|Compatibility Stub') {
            Add-Finding -List $findings -Severity "error" -Code "docsStubMarkerMissing" -Path $relative -Message "docs compatibility file does not declare itself as a stub." -RepairSuggestion "Replace it with a thin compatibility stub that points to the new harness path."
        }
    }
}

$gitkeepFiles = Get-ChildItem -LiteralPath $rootPath -Recurse -File -Force -Filter ".gitkeep" | Where-Object { -not (Test-IsExcludedPath -RelativePath (Convert-ToRelativePath -RootPath $rootPath -Path $_.FullName)) }
foreach ($file in $gitkeepFiles) {
    if ($file.Length -ne 0) {
        Add-Finding -List $findings -Severity "error" -Code "gitkeepNotEmpty" -Path (Convert-ToRelativePath -RootPath $rootPath -Path $file.FullName) -Message ".gitkeep must be empty." -RepairSuggestion "Clear the .gitkeep file content."
    }
}

$architectureDir = Join-Path $rootPath "harness/architecture"
$architectureFiles = @()
if (Test-Path -LiteralPath $architectureDir) {
    $architectureFiles = @(Get-ChildItem -LiteralPath $architectureDir -File -Force)
}
if ($architectureFiles.Count -ne 1 -or $architectureFiles[0].Name -ne "HarnessEngineering.md") {
    Add-Finding -List $findings -Severity "error" -Code "architectureSingleFileRule" -Path "harness/architecture" -Message "harness/architecture must contain only HarnessEngineering.md." -RepairSuggestion "Move historical inputs to harness/archive and keep one architecture authority."
}

$privatePathPattern = '[A-Za-z]:\\[A-Za-z0-9_. $(){}\[\]-]'
$textFiles = @(Get-TextFilesForGovernanceScan -RootPath $rootPath)
foreach ($file in $textFiles) {
    $relative = Convert-ToRelativePath -RootPath $rootPath -Path $file.FullName
    $text = Get-Content -Raw -LiteralPath $file.FullName

    if ($text -match $privatePathPattern) {
        Add-Finding -List $findings -Severity "error" -Code "concretePrivatePath" -Path $relative -Message "Concrete private path detected in a default scanned text asset." -RepairSuggestion "Replace concrete private paths with a reviewed placeholder or move the value into user-local config."
    }

    if ($text -match '(?i)(password|token|secret)\s*[:=]\s*["'']?[A-Za-z0-9_\-]{8,}') {
        Add-Finding -List $findings -Severity "error" -Code "possibleCredentialValue" -Path $relative -Message "Possible credential-like assignment detected." -RepairSuggestion "Remove credential values from tracked assets and keep only redacted policy text."
    }
}

$buildOutputDirs = Get-ChildItem -LiteralPath $rootPath -Recurse -Directory -Force |
    Where-Object {
        $relative = Convert-ToRelativePath -RootPath $rootPath -Path $_.FullName
        -not (Test-IsExcludedPath -RelativePath $relative) -and
        ($_.Name -in @("target", "build", "dist", "out"))
    }
foreach ($dir in $buildOutputDirs) {
    Add-Finding -List $findings -Severity "error" -Code "buildOutputPresent" -Path (Convert-ToRelativePath -RootPath $rootPath -Path $dir.FullName) -Message "Generated build output is present in default-scanned areas." -RepairSuggestion "Remove generated output or keep it under ignored runtime/project build directories."
}

$indexPath = Join-Path $rootPath "harness/INDEX.md"
if (Test-Path -LiteralPath $indexPath -PathType Leaf) {
    $indexText = Get-Content -Raw -LiteralPath $indexPath
    if ($indexText -notmatch [regex]::Escape("harness/PLANS.md")) {
        Add-Finding -List $findings -Severity "warning" -Code "indexPlansRouteMissing" -Path "harness/INDEX.md" -Message "harness/INDEX.md does not route to harness/PLANS.md." -RepairSuggestion "Keep phase status in harness/PLANS.md and route to it from the long-term index."
    }
}

$gitignorePath = Join-Path $rootPath ".gitignore"
if (-not (Test-Path -LiteralPath $gitignorePath -PathType Leaf)) {
    Add-Finding -List $findings -Severity "warning" -Code "gitignoreMissing" -Path ".gitignore" -Message "Root .gitignore is missing." -RepairSuggestion "Add .gitignore before GitHub management so runtime state, local settings and project work copies stay out of the Harness Root repo."
} else {
    $gitignoreText = Get-Content -Raw -LiteralPath $gitignorePath
    foreach ($requiredPattern in @("/var/", "/user/settings/", "/user/github/", "/user/auth/", "/user/registry/*.local.json", "/tools/external/", "/projects/*/", "/.obsidian/workspace.json")) {
        if ($gitignoreText -notmatch [regex]::Escape($requiredPattern)) {
            Add-Finding -List $findings -Severity "warning" -Code "gitignorePatternMissing" -Path ".gitignore" -Message "Required gitignore pattern is missing: $requiredPattern" -RepairSuggestion "Add the pattern to keep local/runtime/project/editor data out of the Harness Root repo."
        }
    }
}

$projectGitDirs = @(Get-ChildItem -LiteralPath (Join-Path $rootPath "projects") -Recurse -Directory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq ".git" })
foreach ($gitDir in $projectGitDirs) {
    Add-Finding -List $findings -Severity "info" -Code "managedProjectSeparateGit" -Path (Convert-ToRelativePath -RootPath $rootPath -Path $gitDir.FullName) -Message "Managed project has its own .git directory." -RepairSuggestion "Keep project repository separate from the Harness Root repository."
}

$registryResult = Invoke-ProjectRegistryCheck -RootPath $rootPath -RegistryPath $Registry -Findings $findings

$severityCounts = [ordered]@{
    error = @($findings | Where-Object { $_.severity -eq "error" }).Count
    warning = @($findings | Where-Object { $_.severity -eq "warning" }).Count
    info = @($findings | Where-Object { $_.severity -eq "info" }).Count
}

$status = "passed"
if ($severityCounts.error -gt 0) {
    $status = "failed"
}

$output = [pscustomobject]@{
    status = $status
    mode = "dry-run"
    root = $rootPath
    checkedAt = (Get-Date).ToString("s")
    summary = [pscustomobject]@{
        requiredRouteCount = $requiredRoutes.Count
        scannedTextFileCount = $textFiles.Count
        findingCount = $findings.Count
        severityCounts = $severityCounts
        registryStatus = if ($registryResult) { $registryResult.status } else { "not-run" }
    }
    checks = @(
        "required-routes",
        "stale-route-candidates",
        "docs-compatibility-stubs",
        "gitkeep-placeholders",
        "architecture-single-file",
        "sensitive-boundary",
        "build-output",
        "index-plans-route",
        "repository-boundary",
        "project-registry"
    )
    findings = @($findings)
}

$output | ConvertTo-Json -Depth 8
if ($status -eq "passed") { exit 0 } else { exit 1 }
