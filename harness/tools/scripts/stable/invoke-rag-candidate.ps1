param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("ingest", "health", "lint", "build-graph", "query", "stale-plan")]
    [string]$Command,

    [string]$Root = ".",
    [string[]]$InputPath = @(),
    [string]$RunId = "",
    [string]$Wiki = "",
    [string]$Report = "",
    [string]$Graph = "",
    [string]$Question = "",
    [string]$Manifest = "",
    [int]$Limit = 10,
    [switch]$CopyRaw,
    [int]$MaxChunkChars = 4000
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
        if ($CopyRaw) { $argsList += "--copy-raw" }
        $argsList += @("--max-chunk-chars", [string]$MaxChunkChars)
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
