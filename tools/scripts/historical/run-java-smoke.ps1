[CmdletBinding()]
param(
    [ValidateSet('codex','hermes','shared')]
    [string]$Agent = 'codex',
    [switch]$Offline,
    [string]$Goal = 'test',
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraMavenArgs
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

$Root = Find-HarnessRoot
$Project = Join-Path $Root 'var\evidence\legacy-java-smoke-test'
$MavenHome = Join-Path $Root 'tools\external\apache-maven-3.9.9'
$Mvn = Join-Path $MavenHome 'bin\mvn.cmd'
$Settings = Join-Path $Root 'user\settings\maven\settings-sandbox.xml'
$Repo = Join-Path $Root "var\m2\$Agent\repository"
$HomeDir = Join-Path $Root "var\homes\$Agent"
$TmpDir = Join-Path $Root 'var\tmp'
$LogDir = Join-Path $Root 'var\logs'
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Mode = if ($Offline) { 'offline' } else { 'online' }
$Log = Join-Path $LogDir "java-smoke-$Agent-$Mode-$Stamp.log"

foreach ($Path in @($Project, $MavenHome, $Settings)) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required path not found: $Path"
    }
}
foreach ($Path in @($Repo, $HomeDir, $TmpDir, $LogDir)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

if ($Repo -like "$env:USERPROFILE*") {
    throw "Refusing to use real user profile as Maven repo: $Repo"
}
if ($Settings -like "$env:USERPROFILE*") {
    throw "Refusing to use real user profile settings: $Settings"
}

$env:MAVEN_OPTS = "-Duser.home=$HomeDir -Djava.io.tmpdir=$TmpDir"
$env:MAVEN_SKIP_RC = 'true'

$mavenArgs = @(
    '-B',
    '-ntp',
    '-s', $Settings,
    "-Dmaven.repo.local=$Repo"
)
if ($Offline) {
    $mavenArgs += '-o'
}
$mavenArgs += $Goal
if ($ExtraMavenArgs) {
    $mavenArgs += $ExtraMavenArgs
}

Write-Host "Agent:       $Agent"
Write-Host "Mode:        $Mode"
Write-Host "Project:     $Project"
Write-Host "Maven:       $Mvn"
Write-Host "Settings:    $Settings"
Write-Host "Local repo:  $Repo"
Write-Host "User home:   $HomeDir"
Write-Host "Log:         $Log"
Write-Host "Command:     $Mvn $($mavenArgs -join ' ')"
Write-Host ""

Push-Location $Project
try {
    & $Mvn @mavenArgs 2>&1 | Tee-Object -FilePath $Log
    $exit = $LASTEXITCODE
}
finally {
    Pop-Location
}

if ($exit -ne 0) {
    Write-Host "Maven smoke test failed. See: $Log"
    exit $exit
}

$repoFiles = (Get-ChildItem -LiteralPath $Repo -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host ""
Write-Host "Maven smoke test passed. Repository file count: $repoFiles"
Write-Host "Log file: $Log"
exit 0
