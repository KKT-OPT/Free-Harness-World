param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("ingest", "health", "lint", "build-graph", "query", "enrichment-plan", "review-package", "promotion-plan", "promote-reviewed", "stale-plan")]
    [string]$Command,

    [string]$Root = ".",
    [string[]]$InputPath = @(),
    [string]$RunId = "",
    [string]$Wiki = "",
    [string]$Report = "",
    [string]$Graph = "",
    [string]$Question = "",
    [string]$Manifest = "",
    [ValidateSet("global", "domain", "project-reviewed", "user-private")]
    [string]$Scope = "user-private",
    [string]$Target = "",
    [string]$Reviewer = "",
    [string]$ApprovalNote = "",
    [string]$ReviewAfter = "",
    [int]$Limit = 10,
    [string]$RawDomain = "",
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
    [string[]]$AllowedTag = @()
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

$argsList = @("-m", "rag_candidate.cli", $Command, "--root", $rootPath)

switch ($Command) {
    "ingest" {
        if ($InputPath.Count -eq 0) { throw "ingest requires -InputPath." }
        $argsList += $InputPath
        if (-not [string]::IsNullOrWhiteSpace($RunId)) { $argsList += @("--run-id", $RunId) }
        if (-not [string]::IsNullOrWhiteSpace($RawDomain)) { $argsList += @("--raw-domain", $RawDomain) }
        if ($CopyRaw) { $argsList += "--copy-raw" }
        $argsList += @("--max-chunk-chars", [string]$MaxChunkChars)
        $argsList += @("--extraction-granularity", $ExtractionGranularity, "--batch-strategy", $BatchStrategy, "--tag-vocabulary-mode", $TagVocabularyMode)
        if ($EntityCap -gt 0) { $argsList += @("--entity-cap", [string]$EntityCap) }
        if ($ConceptCap -gt 0) { $argsList += @("--concept-cap", [string]$ConceptCap) }
        if ($AllowedTag.Count -gt 0) { $argsList += @("--allowed-tags") + $AllowedTag }
    }
    "health" {
        if ([string]::IsNullOrWhiteSpace($Wiki)) { throw "health requires -Wiki." }
        $argsList += @("--wiki", $Wiki)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($RunId)) { $argsList += @("--run-id", $RunId) }
    }
    "lint" {
        if ([string]::IsNullOrWhiteSpace($Wiki)) { throw "lint requires -Wiki." }
        $argsList += @("--wiki", $Wiki)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($RunId)) { $argsList += @("--run-id", $RunId) }
    }
    "build-graph" {
        if ([string]::IsNullOrWhiteSpace($Wiki)) { throw "build-graph requires -Wiki." }
        if ([string]::IsNullOrWhiteSpace($Graph)) { throw "build-graph requires -Graph." }
        $argsList += @("--wiki", $Wiki, "--graph", $Graph)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($RunId)) { $argsList += @("--run-id", $RunId) }
    }
    "query" {
        if ([string]::IsNullOrWhiteSpace($Wiki)) { throw "query requires -Wiki." }
        if ([string]::IsNullOrWhiteSpace($Question)) { throw "query requires -Question." }
        $argsList += @($Question, "--wiki", $Wiki, "--limit", [string]$Limit)
    }
    "enrichment-plan" {
        if ([string]::IsNullOrWhiteSpace($Manifest)) { throw "enrichment-plan requires -Manifest." }
        if ([string]::IsNullOrWhiteSpace($Wiki)) { throw "enrichment-plan requires -Wiki." }
        $argsList += @("--manifest", $Manifest, "--wiki", $Wiki)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($RunId)) { $argsList += @("--run-id", $RunId) }
    }
    "review-package" {
        if ([string]::IsNullOrWhiteSpace($Manifest)) { throw "review-package requires -Manifest." }
        if ([string]::IsNullOrWhiteSpace($Wiki)) { throw "review-package requires -Wiki." }
        $argsList += @("--manifest", $Manifest, "--wiki", $Wiki)
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($RunId)) { $argsList += @("--run-id", $RunId) }
    }
    "promotion-plan" {
        if ([string]::IsNullOrWhiteSpace($Manifest)) { throw "promotion-plan requires -Manifest." }
        if ([string]::IsNullOrWhiteSpace($Wiki)) { throw "promotion-plan requires -Wiki." }
        $argsList += @("--manifest", $Manifest, "--wiki", $Wiki, "--scope", $Scope)
        if (-not [string]::IsNullOrWhiteSpace($Target)) { $argsList += @("--target", $Target) }
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($RunId)) { $argsList += @("--run-id", $RunId) }
    }
    "promote-reviewed" {
        if ([string]::IsNullOrWhiteSpace($Manifest)) { throw "promote-reviewed requires -Manifest." }
        if ([string]::IsNullOrWhiteSpace($Wiki)) { throw "promote-reviewed requires -Wiki." }
        if ([string]::IsNullOrWhiteSpace($Target)) { throw "promote-reviewed requires -Target." }
        if ([string]::IsNullOrWhiteSpace($Reviewer)) { throw "promote-reviewed requires -Reviewer." }
        if ([string]::IsNullOrWhiteSpace($ApprovalNote)) { throw "promote-reviewed requires -ApprovalNote." }
        $argsList += @("--manifest", $Manifest, "--wiki", $Wiki, "--scope", $Scope, "--target", $Target, "--reviewer", $Reviewer, "--approval-note", $ApprovalNote)
        if (-not [string]::IsNullOrWhiteSpace($ReviewAfter)) { $argsList += @("--review-after", $ReviewAfter) }
        if (-not [string]::IsNullOrWhiteSpace($Report)) { $argsList += @("--report", $Report) }
        if (-not [string]::IsNullOrWhiteSpace($RunId)) { $argsList += @("--run-id", $RunId) }
        if ($Overwrite) { $argsList += "--overwrite" }
    }
    "stale-plan" {
        if ([string]::IsNullOrWhiteSpace($Manifest)) { throw "stale-plan requires -Manifest." }
        $argsList += @("--manifest", $Manifest)
    }
}

try {
    & $python @argsList
    exit $LASTEXITCODE
} finally {
    $env:PYTHONPATH = $previousPythonPath
}
