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
        "user/knowledge/",
        "harness/tools/external/",
        "harness/tools/scripts/historical/",
        "harness/tools/scripts/runtime/",
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
    if ($Value -match '^(AGENTS\.md|README\.md|INDEX\.md|harness/|harness\\|adapter/|adapter\\|user/|user\\|projects/|projects\\|sandbox/|sandbox\\|var/|var\\)') { return $true }
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
        "INDEX.md",
        "harness/HarnessIndex.md",
        "harness/architecture/PLANS.md",
        "harness/architecture/HarnessEngineering.md"
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

    $script = Join-Path $RootPath "harness/tools/scripts/stable/test-project-registry.ps1"
    if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
        Add-Finding -List $Findings -Severity "error" -Code "registryValidatorMissing" -Path "harness/tools/scripts/stable/test-project-registry.ps1" -Message "Registry validator is missing." -RepairSuggestion "Restore harness/tools/scripts/stable/test-project-registry.ps1 or update ProjectRegistrationModel."
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

function Invoke-ProjectLifecycleEvidenceSelfTest {
    param(
        [string]$RootPath,
        [System.Collections.ArrayList]$Findings
    )

    $script = Join-Path $RootPath "harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1"
    if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
        Add-Finding -List $Findings -Severity "error" -Code "projectLifecycleValidatorMissing" -Path "harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1" -Message "Project lifecycle evidence validator is missing." -RepairSuggestion "Restore test-project-lifecycle-evidence.ps1 or update Harness lifecycle validation docs."
        return $null
    }

    try {
        $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $script -Root $RootPath -SelfTest
        $result = $raw | ConvertFrom-Json
        if ($result.status -ne "passed") {
            Add-Finding -List $Findings -Severity "error" -Code "projectLifecycleValidatorSelfTestFailed" -Path "harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1" -Message "Project lifecycle evidence validator self-test failed." -RepairSuggestion "Run test-project-lifecycle-evidence.ps1 -SelfTest and repair listed findings."
        }
        return $result
    } catch {
        Add-Finding -List $Findings -Severity "error" -Code "projectLifecycleValidatorSelfTestError" -Path "harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1" -Message "Project lifecycle evidence validator self-test errored: $($_.Exception.Message)" -RepairSuggestion "Fix the lifecycle validator script."
        return $null
    }
}

function Invoke-MemoryStoreGate {
    param(
        [string]$RootPath,
        [System.Collections.ArrayList]$Findings
    )

    $script = Join-Path $RootPath "harness/tools/scripts/stable/invoke-memory.ps1"
    if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
        Add-Finding -List $Findings -Severity "error" -Code "memoryValidatorMissing" -Path "harness/tools/scripts/stable/invoke-memory.ps1" -Message "Memory validator is missing." -RepairSuggestion "Restore invoke-memory.ps1 or update Memory governance docs."
        return $null
    }

    try {
        $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $script -Root $RootPath -Command validate-memory-store
        $result = $raw | ConvertFrom-Json
        if ($result.state -ne "passed") {
            Add-Finding -List $Findings -Severity "error" -Code "memoryStoreValidationFailed" -Path "harness/memory" -Message "Memory store validation failed." -RepairSuggestion "Run invoke-memory.ps1 -Command validate-memory-store and repair listed Memory findings."
        }
        return $result
    } catch {
        Add-Finding -List $Findings -Severity "error" -Code "memoryStoreValidationError" -Path "harness/tools/scripts/stable/invoke-memory.ps1" -Message "Memory store validation errored: $($_.Exception.Message)" -RepairSuggestion "Fix the Memory validator script or Memory store."
        return $null
    }
}

function Invoke-MemoryStoreSelfTest {
    param(
        [string]$RootPath,
        [System.Collections.ArrayList]$Findings
    )

    $script = Join-Path $RootPath "harness/tools/scripts/stable/invoke-memory.ps1"
    if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
        Add-Finding -List $Findings -Severity "error" -Code "memoryValidatorMissing" -Path "harness/tools/scripts/stable/invoke-memory.ps1" -Message "Memory validator is missing." -RepairSuggestion "Restore invoke-memory.ps1 or update Memory governance docs."
        return $null
    }

    try {
        $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $script -Root $RootPath -Command validate-memory-store -SelfTest
        $result = $raw | ConvertFrom-Json
        if ($result.state -ne "passed") {
            Add-Finding -List $Findings -Severity "error" -Code "memoryStoreSelfTestFailed" -Path "harness/tools/scripts/stable/invoke-memory.ps1" -Message "Memory store validator self-test failed." -RepairSuggestion "Run invoke-memory.ps1 -Command validate-memory-store -SelfTest and repair the Memory validator."
        }
        return $result
    } catch {
        Add-Finding -List $Findings -Severity "error" -Code "memoryStoreSelfTestError" -Path "harness/tools/scripts/stable/invoke-memory.ps1" -Message "Memory store validator self-test errored: $($_.Exception.Message)" -RepairSuggestion "Fix the Memory validator self-test."
        return $null
    }
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$findings = New-Object System.Collections.ArrayList

$requiredRoutes = @(
    "AGENTS.md",
    "INDEX.md",
    "README.md",
    "adapter/AdapterIndex.md",
    "harness/HarnessIndex.md",
    "harness/architecture/HarnessEngineering.md",
    "harness/architecture/PLANS.md",
    "harness/architecture/CHANGELOG.md",
    "harness/bootstrap/BootstrapIndex.md",
    "harness/governance/GovernanceIndex.md",
    "harness/governance/ArtifactLifecycle.md",
    "harness/governance/KnowledgePromotionPolicy.md",
    "harness/governance/MemoryGovernance.md",
    "harness/governance/SkillGovernance.md",
    "harness/governance/DocumentGovernance.md",
    "harness/governance/IndexMaintenancePolicy.md",
    "harness/governance/CleanupPolicy.md",
    "harness/governance/ScheduledGovernance.md",
    "harness/governance/ReportArchivePolicy.md",
    "harness/reports/ReportsIndex.md",
    "harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md",
    "harness/memory/MemoryIndex.md",
    "harness/memory/MemoryPolicy.md",
    "harness/skills/SkillIndex.md",
    "harness/skills/SkillPolicy.md",
    "harness/skills/usage/skill-usage.json",
    "harness/verification/VerificationIndex.md",
    "harness/verification/ReadinessCheckPolicy.md",
    "harness/verification/RegressionPolicy.md",
    "harness/verification/HarnessValidationPlan.md",
    "harness/verification/HarnessValidationCases.md",
    "harness/observability/ObservabilityIndex.md",
    "harness/observability/TraceSchema.md",
    "harness/observability/FailureAttribution.md",
    "harness/rag/RAGIndex.md",
    "harness/governance/KnowledgePromotionPolicy.md",
    "harness/tools/ToolsIndex.md",
    "harness/tools/docs/script-index/ScriptIndex.md",
    "harness/tools/scripts/stable/bootstrap-harness-workspace.ps1",
    "harness/tools/docs/command-surfaces/StableToolSurfaceModel.md",
    "harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md",
    "adapter/task-intake/TaskIntakeWorkflowModel.md",
    "sandbox/SandboxIndex.md",
    "user/knowledge/README.md",
    "user/registry/knowledge.local.example.json",
    "user/registry/projects.local.json",
    "harness/tools/scripts/stable/test-project-registry.ps1",
    "harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1",
    "harness/tools/scripts/stable/invoke-memory.ps1"
)

foreach ($route in $requiredRoutes) {
    $path = Join-Path $rootPath ($route -replace '/', '\')
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Finding -List $findings -Severity "error" -Code "requiredRouteMissing" -Path $route -Message "Required route does not exist." -RepairSuggestion "Restore the route or update INDEX.md, harness/HarnessIndex.md and harness/architecture/PLANS.md."
    }
}

Test-StaleRouteCandidates -RootPath $rootPath -Findings $findings

$legacyVerificationDir = Join-Path $rootPath "harness/governance/verification"
if (Test-Path -LiteralPath $legacyVerificationDir) {
    Add-Finding -List $findings -Severity "warning" -Code "legacyGovernanceVerificationPresent" -Path "harness/governance/verification" -Message "Legacy governance verification implementation path is present." -RepairSuggestion "Keep verification rules under harness/verification/ and route governance linkage through harness/governance/GovernanceIndex.md."
}

foreach ($legacyRoute in @(
    "harness/INDEX.md",
    "harness/PLANS.md",
    "harness/templates/project",
    "harness/project-template",
    "harness/governance/promotion",
    "harness/architecture/HarnessEngineering_v2.3_feedback23_review.md",
    "entities"
)) {
    $legacyPath = Join-Path $rootPath ($legacyRoute -replace '/', '\')
    if (Test-Path -LiteralPath $legacyPath) {
        Add-Finding -List $findings -Severity "warning" -Code "legacyRoutePresent" -Path $legacyRoute -Message "Legacy route remains after target migration." -RepairSuggestion "Delete the legacy route after confirming active indexes point to the target path."
    }
}

$docsRoot = Join-Path $rootPath "docs"
if (Test-Path -LiteralPath $docsRoot -PathType Container) {
    $docsFiles = Get-ChildItem -LiteralPath $docsRoot -Recurse -File -Force
    foreach ($file in $docsFiles) {
        $relative = Convert-ToRelativePath -RootPath $rootPath -Path $file.FullName
        $text = Get-Content -Raw -LiteralPath $file.FullName
        if ($text -notmatch 'compatibility-stub|Compatibility Stub') {
            Add-Finding -List $findings -Severity "warning" -Code "legacyDocsNonStubFilePresent" -Path $relative -Message "Legacy docs root contains a non-stub file." -RepairSuggestion "Move durable content to the target path, then keep only compatibility stubs or delete the legacy docs route after review."
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
foreach ($file in $architectureFiles) {
    if ($file.Name -notin @("HarnessEngineering.md", "PLANS.md", "CHANGELOG.md")) {
        Add-Finding -List $findings -Severity "warning" -Code "architectureLegacyInputPresent" -Path "harness/architecture/$($file.Name)" -Message "Architecture folder contains a non-authority input document." -RepairSuggestion "Review merge/delete timing; move historical inputs to archive only after the authority document and PLANS no longer depend on them."
    }
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

$indexPath = Join-Path $rootPath "INDEX.md"
if (Test-Path -LiteralPath $indexPath -PathType Leaf) {
    $indexText = Get-Content -Raw -LiteralPath $indexPath
    if ($indexText -notmatch [regex]::Escape("harness/architecture/PLANS.md")) {
        Add-Finding -List $findings -Severity "warning" -Code "indexPlansRouteMissing" -Path "INDEX.md" -Message "INDEX.md does not route to harness/architecture/PLANS.md." -RepairSuggestion "Keep phase status in harness/architecture/PLANS.md and route to it from the long-term index."
    }
    if ($indexText -notmatch [regex]::Escape("harness/HarnessIndex.md")) {
        Add-Finding -List $findings -Severity "warning" -Code "indexHarnessRouteMissing" -Path "INDEX.md" -Message "INDEX.md does not route to harness/HarnessIndex.md." -RepairSuggestion "Route General Harness assets through harness/HarnessIndex.md."
    }
}

$gitignorePath = Join-Path $rootPath ".gitignore"
if (-not (Test-Path -LiteralPath $gitignorePath -PathType Leaf)) {
    Add-Finding -List $findings -Severity "warning" -Code "gitignoreMissing" -Path ".gitignore" -Message "Root .gitignore is missing." -RepairSuggestion "Add .gitignore before GitHub management so runtime state, local settings and project work copies stay out of the Harness Root repo."
} else {
    $gitignoreText = Get-Content -Raw -LiteralPath $gitignorePath
    foreach ($requiredPattern in @("/var/", "/user/settings/", "/user/github/", "/user/auth/", "/user/knowledge/**", "/user/registry/*.local.json", "/harness/tools/scripts/runtime/**", "/harness/tools/external/", "/projects/*/", "/.obsidian/workspace.json")) {
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
$projectLifecycleSelfTestResult = Invoke-ProjectLifecycleEvidenceSelfTest -RootPath $rootPath -Findings $findings
$memoryStoreResult = Invoke-MemoryStoreGate -RootPath $rootPath -Findings $findings
$memoryStoreSelfTestResult = Invoke-MemoryStoreSelfTest -RootPath $rootPath -Findings $findings

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
        projectLifecycleEvidenceStatus = if ($projectLifecycleSelfTestResult) { $projectLifecycleSelfTestResult.status } else { "not-run" }
        memoryStoreStatus = if ($memoryStoreResult) { $memoryStoreResult.state } else { "not-run" }
        memoryStoreSelfTestStatus = if ($memoryStoreSelfTestResult) { $memoryStoreSelfTestResult.state } else { "not-run" }
    }
    checks = @(
        "required-routes",
        "stale-route-candidates",
        "docs-compatibility-stubs",
        "gitkeep-placeholders",
        "architecture-authority-boundary",
        "sensitive-boundary",
        "build-output",
        "index-plans-route",
        "repository-boundary",
        "project-registry",
        "project-lifecycle-evidence-self-test",
        "memory-store-validation",
        "memory-store-self-test"
    )
    findings = @($findings)
}

$output | ConvertTo-Json -Depth 8
if ($status -eq "passed") { exit 0 } else { exit 1 }
