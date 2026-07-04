param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("init-obsidian-vault", "sync-reviewed-index", "build-reviewed-graph", "health-reviewed", "query-reviewed", "reviewed-gap-plan", "govern-reviewed-duplicates", "dispose-residual-gaps", "canonicalize-vault-layout", "validate-knowledge-vault", "schema-context", "validate-llm-wiki-mechanisms", "candidate-cleanup-plan", "candidate-cleanup-apply", "enrich-gap-candidates", "gap-review-package", "promote-gap-candidates", "govern-vault", "pipeline-smoke")]
    [string]$Command,

    [string]$Root = ".",
    [string[]]$InputPath = @(),
    [string]$Vault = "user/knowledge",
    [string]$Reviewed = "user/knowledge/reviewed",
    [string]$Candidate = "user/knowledge/candidate",
    [string]$Raw = "user/knowledge/raw",
    [string]$Registry = "user/registry/knowledge.local.json",
    [string]$Domain = "agent",
    [string]$SourceDomain = "agent",
    [string]$TargetDomain = "agent-harness-engineering",
    [string]$SourceId = "agent-harness-engineering-a-survey",
    [string]$CanonicalPage = "agent-harness-engineering-survey",
    [ValidateSet("ingest", "promotion", "query", "validation", "cleanup", "all")]
    [string]$Task = "validation",
    [string]$Graph = "",
    [string]$Report = "",
    [string]$CandidateWiki = "",
    [string]$CandidateRunId = "reviewed-gap-concepts",
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
    [ValidateSet("fine", "standard", "coarse", "minimal", "custom")]
    [string]$ExtractionGranularity = "standard",
    [int]$EntityCap = 0,
    [int]$ConceptCap = 0,
    [string]$BatchStrategy = "single-pass-local-conversion",
    [ValidateSet("default", "custom")]
    [string]$TagVocabularyMode = "default",
    [string[]]$AllowedTag = @(),
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
    "govern-reviewed-duplicates" {
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
    }
    "dispose-residual-gaps" {
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($CandidateWiki)) { $argsList += @("--candidate-wiki", $CandidateWiki) }
        if (-not [string]::IsNullOrWhiteSpace($CandidateRunId)) { $argsList += @("--candidate-run-id", $CandidateRunId) }
    }
    "canonicalize-vault-layout" {
        $argsList += @("--candidate", $Candidate, "--raw", $Raw, "--registry", $Registry)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($SourceDomain)) { $argsList += @("--source-domain", $SourceDomain) }
        if (-not [string]::IsNullOrWhiteSpace($TargetDomain)) { $argsList += @("--target-domain", $TargetDomain) }
        if (-not [string]::IsNullOrWhiteSpace($SourceId)) { $argsList += @("--source-id", $SourceId) }
        if (-not [string]::IsNullOrWhiteSpace($CanonicalPage)) { $argsList += @("--canonical-page", $CanonicalPage) }
    }
    "validate-knowledge-vault" {
        $argsList += @("--candidate", $Candidate, "--raw", $Raw, "--registry", $Registry)
        if (-not [string]::IsNullOrWhiteSpace($Graph)) { $argsList += @("--graph", $Graph) }
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
    }
    "schema-context" {
        if ([string]::IsNullOrWhiteSpace($Domain)) { throw "schema-context requires -Domain." }
        $argsList += @("--registry", $Registry, "--domain", $Domain, "--task", $Task)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
    }
    "validate-llm-wiki-mechanisms" {
        $argsList += @("--candidate", $Candidate, "--raw", $Raw, "--registry", $Registry)
        if (-not [string]::IsNullOrWhiteSpace($Graph)) { $argsList += @("--graph", $Graph) }
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
    }
    "candidate-cleanup-plan" {
        $argsList += @("--candidate", $Candidate, "--raw", $Raw, "--registry", $Registry)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
    }
    "candidate-cleanup-apply" {
        if ([string]::IsNullOrWhiteSpace($Reviewer)) { throw "candidate-cleanup-apply requires -Reviewer." }
        if ([string]::IsNullOrWhiteSpace($ApprovalNote)) { throw "candidate-cleanup-apply requires -ApprovalNote." }
        $argsList += @("--candidate", $Candidate, "--raw", $Raw, "--registry", $Registry, "--reviewer", $Reviewer, "--approval-note", $ApprovalNote)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
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
        if (-not [string]::IsNullOrWhiteSpace($Domain)) { $argsList += @("--domain", $Domain) }
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
        $argsList += @("--candidate", $Candidate, "--raw", $Raw, "--registry", $Registry, "--domain", $Domain, "--scope", $Scope, "--reviewer", $Reviewer, "--approval-note", $ApprovalNote, "--review-after", $ReviewAfter, "--question", $Question, "--limit", [string]$Limit, "--max-chunk-chars", [string]$MaxChunkChars)
        $argsList += @("--extraction-granularity", $ExtractionGranularity, "--batch-strategy", $BatchStrategy, "--tag-vocabulary-mode", $TagVocabularyMode)
        if ($EntityCap -gt 0) { $argsList += @("--entity-cap", [string]$EntityCap) }
        if ($ConceptCap -gt 0) { $argsList += @("--concept-cap", [string]$ConceptCap) }
        if ($AllowedTag.Count -gt 0) { $argsList += @("--allowed-tags") + $AllowedTag }
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
