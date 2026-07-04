param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "memory-flow-status",
        "verify-source-evidence",
        "detect-from-workflow",
        "classify-candidate-suitability",
        "record-no-memory-disposition",
        "create-candidate",
        "classify-memory-type",
        "validate-memory-store",
        "detect-memory-duplicate-conflict",
        "reject-or-merge-candidate",
        "conflict-review-package",
        "candidate-review-package",
        "apply-review-decision",
        "promote-reviewed",
        "archive-candidate",
        "delete-candidate",
        "revise-candidate",
        "sync-memory-index"
    )]
    [string]$Command,

    [string]$Root = ".",
    [string]$MemoryRoot = "harness/memory",
    [string]$Candidate = "harness/memory/candidate",
    [string]$Reviewed = "harness/memory/reviewed",
    [string]$Archive = "harness/memory/archive",
    [string]$CandidateId = "",
    [string]$CandidatePath = "",
    [string]$Report = "",
    [string]$SourcePath = "",
    [string]$MemoryId = "",
    [string]$Statement = "",
    [string]$Scope = "agent-operation",
    [string]$ProjectId = "null",
    [string]$Confidence = "medium",
    [string]$StalenessRule = "",
    [string]$Decision = "",
    [string]$Reviewer = "",
    [string]$ApprovalNote = "",
    [string]$Reason = "",
    [string]$ReviewAfter = "",
    [string]$NewStatement = "",
    [switch]$SelfTest,
    [switch]$Apply
)

$ErrorActionPreference = "Stop"

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$stableDir = Join-Path $rootPath "harness/tools/scripts/stable"
$python = "python"

$previousPythonPath = $env:PYTHONPATH
if ([string]::IsNullOrWhiteSpace($previousPythonPath)) {
    $env:PYTHONPATH = $stableDir
} else {
    $env:PYTHONPATH = "$stableDir;$previousPythonPath"
}
$env:PYTHONUTF8 = "1"

$argsList = @(
    "-m", "memory_tool.cli",
    $Command,
    "--root", $rootPath,
    "--memory-root", $MemoryRoot,
    "--candidate", $Candidate,
    "--reviewed", $Reviewed,
    "--archive", $Archive
)

if (-not [string]::IsNullOrWhiteSpace($Report)) {
    $argsList += @("--report", $Report)
}
if ($SelfTest) {
    $argsList += "--self-test"
}
if ($Apply) {
    $argsList += "--apply"
}

$optionalArgs = @(
    @("--source-path", $SourcePath),
    @("--memory-id", $MemoryId),
    @("--statement", $Statement),
    @("--scope", $Scope),
    @("--project-id", $ProjectId),
    @("--confidence", $Confidence),
    @("--staleness-rule", $StalenessRule),
    @("--decision", $Decision),
    @("--reviewer", $Reviewer),
    @("--approval-note", $ApprovalNote),
    @("--reason", $Reason),
    @("--review-after", $ReviewAfter),
    @("--new-statement", $NewStatement)
)

foreach ($pair in $optionalArgs) {
    if (-not [string]::IsNullOrWhiteSpace($pair[1])) {
        $argsList += @($pair[0], $pair[1])
    }
}

if (-not [string]::IsNullOrWhiteSpace($CandidateId)) {
    $argsList += @("--candidate-id", $CandidateId)
}
if (-not [string]::IsNullOrWhiteSpace($CandidatePath)) {
    $argsList += @("--candidate-path", $CandidatePath)
}

try {
    & $python @argsList
    exit $LASTEXITCODE
} finally {
    $env:PYTHONPATH = $previousPythonPath
}
