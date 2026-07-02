param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("init-obsidian-vault", "sync-reviewed-index", "build-reviewed-graph", "health-reviewed", "query-reviewed", "reviewed-gap-plan", "enrich-gap-candidates", "gap-review-package", "promote-gap-candidates", "govern-vault", "pipeline-smoke")]
    [string]$Command,

    [string]$Root = ".",
    [string[]]$InputPath = @(),
    [string]$Vault = "user/knowledge",
    [string]$Reviewed = "user/knowledge/reviewed",
    [string]$Candidate = "user/knowledge/candidate",
    [string]$Raw = "user/knowledge/raw",
    [string]$Graph = "",
    [string]$Report = "",
    [string]$CandidateWiki = "",
    [string]$TargetDir = "",
    [string]$Target = "",
    [string]$Question = "",
    [int]$Limit = 10,
    [string]$Scope = "user-private",
    [string]$Reviewer = "",
    [string]$ApprovalNote = "",
    [string]$ReviewAfter = "source-updated-or-2026-12-31",
    [switch]$WriteCandidates,
    [switch]$ArchiveInactiveCandidates,
    [switch]$CopyRaw,
    [switch]$Overwrite,
    [int]$MaxChunkChars = 4000,
    [string]$RunId = ""
)

$ErrorActionPreference = "Stop"

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$stableDir = Join-Path $rootPath "harness/tools/scripts/stable"
$python = Join-Path $rootPath "var/rag/venvs/llm-wiki-agent/Scripts/python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $python = "python"
}

$previousPythonPath = $env:PYTHONPATH
if ([string]::IsNullOrWhiteSpace($previousPythonPath)) {
    $env:PYTHONPATH = $stableDir
} else {
    $env:PYTHONPATH = "$stableDir;$previousPythonPath"
}
$env:PYTHONUTF8 = "1"

$argsList = @("-m", "rag_knowledge.cli", $Command, "--root", $rootPath, "--vault", $Vault, "--reviewed", $Reviewed)
if (-not [string]::IsNullOrWhiteSpace($RunId)) {
    $argsList += @("--run-id", $RunId)
}

switch ($Command) {
    "init-obsidian-vault" {
    }
    "sync-reviewed-index" {
    }
    "build-reviewed-graph" {
        if (-not [string]::IsNullOrWhiteSpace($Graph)) { $argsList += @("--graph", $Graph) }
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
    }
    "health-reviewed" {
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
    }
    "query-reviewed" {
        if ([string]::IsNullOrWhiteSpace($Question)) { throw "query-reviewed requires -Question." }
        $argsList += @($Question, "--limit", [string]$Limit)
        if (-not [string]::IsNullOrWhiteSpace($Graph)) { $argsList += @("--graph", $Graph) }
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
    }
    "reviewed-gap-plan" {
        if (-not [string]::IsNullOrWhiteSpace($Graph)) { $argsList += @("--graph", $Graph) }
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($CandidateWiki)) { $argsList += @("--candidate-wiki", $CandidateWiki) }
        if ($WriteCandidates) { $argsList += @("--write-candidates") }
    }
    "enrich-gap-candidates" {
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($CandidateWiki)) { $argsList += @("--candidate-wiki", $CandidateWiki) }
    }
    "gap-review-package" {
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($CandidateWiki)) { $argsList += @("--candidate-wiki", $CandidateWiki) }
    }
    "promote-gap-candidates" {
        if ([string]::IsNullOrWhiteSpace($Reviewer)) { throw "promote-gap-candidates requires -Reviewer." }
        if ([string]::IsNullOrWhiteSpace($ApprovalNote)) { throw "promote-gap-candidates requires -ApprovalNote." }
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($CandidateWiki)) { $argsList += @("--candidate-wiki", $CandidateWiki) }
        if (-not [string]::IsNullOrWhiteSpace($TargetDir)) { $argsList += @("--target-dir", $TargetDir) }
        $argsList += @("--scope", $Scope, "--reviewer", $Reviewer, "--approval-note", $ApprovalNote, "--review-after", $ReviewAfter)
        if ($Overwrite) { $argsList += @("--overwrite") }
    }
    "govern-vault" {
        $argsList += @("--candidate", $Candidate, "--raw", $Raw)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if ($ArchiveInactiveCandidates) { $argsList += @("--archive-inactive-candidates") }
    }
    "pipeline-smoke" {
        if ($InputPath.Count -eq 0) { throw "pipeline-smoke requires -InputPath." }
        if ([string]::IsNullOrWhiteSpace($Reviewer)) { throw "pipeline-smoke requires -Reviewer." }
        if ([string]::IsNullOrWhiteSpace($ApprovalNote)) { throw "pipeline-smoke requires -ApprovalNote." }
        if ([string]::IsNullOrWhiteSpace($Question)) { throw "pipeline-smoke requires -Question." }
        $argsList += $InputPath
        $argsList += @("--candidate", $Candidate, "--raw", $Raw, "--scope", $Scope, "--reviewer", $Reviewer, "--approval-note", $ApprovalNote, "--review-after", $ReviewAfter, "--question", $Question, "--limit", [string]$Limit, "--max-chunk-chars", [string]$MaxChunkChars)
        if (-not [string]::IsNullOrWhiteSpace($Target)) { $argsList += @("--target", $Target) }
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if ($CopyRaw) { $argsList += @("--copy-raw") }
        if ($Overwrite) { $argsList += @("--overwrite") }
        if ($ArchiveInactiveCandidates) { $argsList += @("--archive-promoted-candidate") }
    }
}

try {
    & $python @argsList
    exit $LASTEXITCODE
} finally {
    $env:PYTHONPATH = $previousPythonPath
}
