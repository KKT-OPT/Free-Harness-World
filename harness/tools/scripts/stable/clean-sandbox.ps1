[CmdletBinding()]
param(
    [switch]$Apply,

    [int]$KeepLatestPerLogFamily = 1,

    [switch]$KeepTmp,

    [string]$Root
)

$ErrorActionPreference = 'Stop'

function Find-HarnessRoot {
    $dir = $PSScriptRoot
    while ($dir) {
        if (Test-Path -LiteralPath (Join-Path $dir 'AGENTS.md')) {
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

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Find-HarnessRoot
}

$logsDir = Join-Path $Root 'var\logs'
$tmpDir = Join-Path $Root 'var\tmp'
$candidates = [System.Collections.Generic.List[object]]::new()

function Add-Candidate {
    param(
        [string]$Path,
        [string]$Kind,
        [string]$Reason
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    $item = Get-Item -LiteralPath $Path -Force
    $candidates.Add([ordered]@{
        path = $item.FullName
        kind = $Kind
        reason = $Reason
        length = if ($item.PSIsContainer) { $null } else { $item.Length }
        lastWriteTime = $item.LastWriteTime
    })
}

if ((Test-Path -LiteralPath $tmpDir) -and -not $KeepTmp) {
    Get-ChildItem -Force -LiteralPath $tmpDir | ForEach-Object {
        Add-Candidate -Path $_.FullName -Kind 'tmp' -Reason 'generated temporary process output'
    }
}

if (Test-Path -LiteralPath $logsDir) {
    $timestampedLogs = Get-ChildItem -Force -LiteralPath $logsDir -File -Filter '*.log' |
        Where-Object { $_.Name -match '^(?<family>.+)-\d{8}-\d{6}\.log$' }

    $timestampedLogs |
        Group-Object { if ($_.Name -match '^(?<family>.+)-\d{8}-\d{6}\.log$') { $Matches.family } else { $_.BaseName } } |
        ForEach-Object {
            $_.Group |
                Sort-Object LastWriteTime -Descending |
                Select-Object -Skip $KeepLatestPerLogFamily |
                ForEach-Object {
                    Add-Candidate -Path $_.FullName -Kind 'log' -Reason "older than latest $KeepLatestPerLogFamily for log family"
                }
        }
}

$summary = [ordered]@{
    root = $Root
    apply = [bool]$Apply
    keepLatestPerLogFamily = $KeepLatestPerLogFamily
    keepTmp = [bool]$KeepTmp
    candidateCount = $candidates.Count
    candidates = $candidates
}

$summary | ConvertTo-Json -Depth 8

if (-not $Apply) {
    Write-Host ''
    Write-Host 'Dry run only. Re-run with -Apply to delete these candidates.'
    exit 0
}

foreach ($candidate in $candidates) {
    Remove-Item -LiteralPath $candidate.path -Recurse -Force
}

Write-Host ''
Write-Host "Deleted $($candidates.Count) sandbox cleanup candidate(s)."
