<#
.SYNOPSIS
Daily launcher for a local Hermes Desktop install.

.DESCRIPTION
This script updates the local source install through hermes-update-codex.ps1,
which preserves the local Windows Codex patch and rebuilds the Desktop shell
only when Desktop source files changed. After the update succeeds, it launches
the already built Desktop app through `hermes desktop --skip-build`.

The script intentionally avoids the official Desktop installer/bootstrap path.
#>
[CmdletBinding()]
param(
    [string]$HermesHome = $env:HERMES_HOME,
    [string]$CodexHome = $env:CODEX_HOME,
    [switch]$SkipUpdate,
    [switch]$CheckOnly,
    [switch]$LaunchOnUpdateFailure
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($HermesHome)) {
    throw "HermesHome is required. Pass -HermesHome or set HERMES_HOME."
}

$Repo = Join-Path $HermesHome 'hermes-agent'
$UpdateScript = Join-Path $HermesHome 'hermes-update-codex.ps1'
$HermesExe = Join-Path $Repo 'venv\Scripts\hermes.exe'
$DesktopExe = Join-Path $Repo 'apps\desktop\release\win-unpacked\Hermes.exe'
$LogDir = Join-Path $HermesHome 'logs'
$LogFile = Join-Path $LogDir 'desktop-launcher.log'

function Write-LauncherLog([string]$Message) {
    $line = '[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    Write-Host $line
    Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
}

function Show-LauncherError([string]$Message) {
    try {
        $shell = New-Object -ComObject WScript.Shell
        [void]$shell.Popup($Message, 0, 'Hermes Desktop launcher', 0x10)
    }
    catch {
        Write-Host $Message
    }
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

try {
    if (-not (Test-Path -LiteralPath $UpdateScript)) {
        throw "Update script not found: $UpdateScript"
    }
    if (-not (Test-Path -LiteralPath $HermesExe)) {
        throw "Hermes executable not found: $HermesExe"
    }

    $env:HERMES_HOME = $HermesHome
    $env:HERMES_DESKTOP_HERMES_ROOT = $Repo
    $env:PYTHONUTF8 = '1'
    $env:PYTHONIOENCODING = 'utf-8'
    if ($CodexHome -and -not $env:CODEX_HOME) {
        $env:CODEX_HOME = $CodexHome
    }

    Set-Location -LiteralPath $Repo
    Write-LauncherLog 'Starting Hermes Desktop launcher.'
    Write-LauncherLog "HERMES_HOME=$env:HERMES_HOME"
    Write-LauncherLog "HERMES_DESKTOP_HERMES_ROOT=$env:HERMES_DESKTOP_HERMES_ROOT"

    if ($SkipUpdate) {
        Write-LauncherLog 'Skipping update because -SkipUpdate was requested.'
    }
    else {
        Write-LauncherLog 'Running protected Hermes update flow.'
        $updateArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $UpdateScript)
        if ($CheckOnly) {
            $updateArgs += '-CheckOnly'
        }

        & powershell @updateArgs
        $updateExit = $LASTEXITCODE
        if ($updateExit -ne 0) {
            $message = "Hermes update failed with exit code $updateExit. See $LogFile and the Hermes log directory for details."
            Write-LauncherLog $message
            if (-not $LaunchOnUpdateFailure) {
                throw $message
            }
        }
    }

    if ($CheckOnly) {
        Write-LauncherLog 'CheckOnly requested; not launching Desktop.'
        exit 0
    }

    if (-not (Test-Path -LiteralPath $DesktopExe)) {
        Write-LauncherLog 'Desktop executable is missing; building it from current source.'
        & $HermesExe desktop --build-only --hermes-root $Repo
        $buildExit = $LASTEXITCODE
        if ($buildExit -ne 0) {
            throw "Desktop build failed with exit code $buildExit"
        }
    }

    Write-LauncherLog 'Launching Hermes Desktop.'
    & $HermesExe desktop --skip-build --hermes-root $Repo
    $launchExit = $LASTEXITCODE
    if ($launchExit -ne 0) {
        throw "Hermes Desktop launch failed with exit code $launchExit"
    }
}
catch {
    $message = $_.Exception.Message
    Write-LauncherLog "ERROR: $message"
    Show-LauncherError "$message`n`nLog: $LogFile"
    exit 1
}
