<#
.SYNOPSIS
Updates Hermes from the official/fork main branch, reapplies the local Windows
Codex transport patch when needed, and rebuilds the local Desktop shell only
when Desktop source files changed.

.USAGE
  powershell -ExecutionPolicy Bypass -File <path>\hermes-update-codex.ps1
  powershell -ExecutionPolicy Bypass -File <path>\hermes-update-codex.ps1 -CheckOnly
  powershell -ExecutionPolicy Bypass -File <path>\hermes-update-codex.ps1 -ForceDesktopBuild
  powershell -ExecutionPolicy Bypass -File <path>\hermes-update-codex.ps1 -SkipDesktopBuild

.NOTES
  Keep this script outside the Hermes agent repo so it does not dirty the
  Hermes git worktree. Configure local paths through parameters or environment
  variables such as HERMES_HOME, HERMES_AGENT_REPO and CODEX_HOME.

  Run this script instead of plain `hermes update` until the upstream PR for
  the Windows Codex fix is merged.

  Desktop updates are handled as a source/build refresh:
    1. `hermes update` pulls the open-source repo changes.
    2. This script checks whether Desktop source changed since the last local
       Desktop build.
    3. If needed, it runs `hermes desktop --build-only --hermes-root <repo>`.

  This does not run the official Desktop installer and does not bootstrap a new
  Hermes install.
#>
[CmdletBinding()]
param(
    [string]$Repo = $env:HERMES_AGENT_REPO,
    [string]$HermesHome = $env:HERMES_HOME,
    [string]$CodexHome = $env:CODEX_HOME,
    [string]$GitSshCommand = $env:GIT_SSH_COMMAND,
    [switch]$CheckOnly,
    [switch]$SkipDesktopBuild,
    [switch]$ForceDesktopBuild,
    [switch]$DesktopBuildOnly,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$HermesArgs
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Repo)) {
    throw "Repo is required. Pass -Repo or set HERMES_AGENT_REPO."
}
if ([string]::IsNullOrWhiteSpace($HermesHome)) {
    throw "HermesHome is required. Pass -HermesHome or set HERMES_HOME."
}

$PatchFile = Join-Path $HermesHome 'patches\windows-codex-transport.patch'
$RunAgent = Join-Path $Repo 'run_agent.py'
$HermesExe = Join-Path $Repo 'venv\Scripts\hermes.exe'
$PythonExe = Join-Path $Repo 'venv\Scripts\python.exe'
$DesktopDir = Join-Path $Repo 'apps\desktop'
$DesktopExe = Join-Path $DesktopDir 'release\win-unpacked\Hermes.exe'
$DesktopStamp = Join-Path $DesktopDir 'build\install-stamp.json'
$Marker = 'base_url_host_matches(str(base_url or ""), "chatgpt.com")'
$DesktopPathspec = @(
    'apps/desktop',
    'apps/shared',
    'package.json',
    'package-lock.json'
)

function Write-Step([string]$Message) {
    Write-Host "==> $Message"
}

function Invoke-GitChecked {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $oldPreference = $global:ErrorActionPreference
    $global:ErrorActionPreference = 'Continue'
    & git -C $Repo @Arguments
    $code = $LASTEXITCODE
    $global:ErrorActionPreference = $oldPreference
    if ($code -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $code"
    }
}

function Invoke-GitQuiet {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $oldPreference = $global:ErrorActionPreference
    $global:ErrorActionPreference = 'Continue'
    $out = & git -C $Repo @Arguments 2>$null
    $code = $LASTEXITCODE
    $global:ErrorActionPreference = $oldPreference
    if ($code -ne 0) {
        return $null
    }
    return ($out -join "`n")
}

function Test-GitCommandClean {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $oldPreference = $global:ErrorActionPreference
    $global:ErrorActionPreference = 'Continue'
    & git -C $Repo @Arguments *> $null
    $code = $LASTEXITCODE
    $global:ErrorActionPreference = $oldPreference
    return ($code -eq 0)
}

function Test-WorkingPatchPresent {
    if (-not (Test-Path -LiteralPath $RunAgent)) {
        return $false
    }
    return [bool](Select-String -LiteralPath $RunAgent -SimpleMatch -Pattern $Marker -Quiet)
}

function Test-HeadPatchPresent {
    $headText = Invoke-GitQuiet show HEAD:run_agent.py
    if ($null -eq $headText) {
        return $false
    }
    return $headText.Contains($Marker)
}

function Unstage-RunAgentIfNeeded {
    $cached = Invoke-GitQuiet diff --cached --name-only -- run_agent.py
    if ($cached -and $cached.Trim().Length -gt 0) {
        Write-Host 'Unstaging run_agent.py local patch from the index.'
        Invoke-GitChecked reset -- run_agent.py
    }
}

function Get-TrackedDirtyLines {
    $dirty = Invoke-GitQuiet status --porcelain --untracked-files=no
    if ($null -eq $dirty -or $dirty.Trim().Length -eq 0) {
        return @()
    }
    return @($dirty -split "`n" | Where-Object { $_ -and $_.Trim().Length -gt 0 })
}

function Apply-LocalPatch {
    if (Test-GitCommandClean apply --check $PatchFile) {
        Invoke-GitChecked apply $PatchFile
        return
    }

    Write-Host 'Plain patch apply did not fit exactly; trying 3-way apply.'
    Invoke-GitChecked apply --3way $PatchFile
    Unstage-RunAgentIfNeeded
}

function Get-HeadSha {
    $sha = Invoke-GitQuiet rev-parse HEAD
    if ($null -eq $sha -or $sha.Trim().Length -eq 0) {
        throw 'Unable to resolve HEAD.'
    }
    return $sha.Trim()
}

function Test-CommitExists([string]$Commit) {
    if (-not $Commit) {
        return $false
    }
    $oldPreference = $global:ErrorActionPreference
    $global:ErrorActionPreference = 'Continue'
    & git -C $Repo rev-parse --verify $Commit *> $null
    $code = $LASTEXITCODE
    $global:ErrorActionPreference = $oldPreference
    return ($code -eq 0)
}

function Get-DesktopBuiltCommit {
    if (-not (Test-Path -LiteralPath $DesktopStamp)) {
        return $null
    }
    try {
        $stamp = Get-Content -LiteralPath $DesktopStamp -Raw | ConvertFrom-Json
        if ($stamp.commit) {
            return [string]$stamp.commit
        }
    }
    catch {
        return $null
    }
    return $null
}

function Get-ChangedFiles {
    param(
        [string]$From,
        [string]$To,
        [string[]]$Pathspec
    )
    if (-not $From -or -not $To -or $From -eq $To) {
        return @()
    }
    if (-not (Test-CommitExists $From) -or -not (Test-CommitExists $To)) {
        return @()
    }

    $args = @('diff', '--name-only', $From, $To, '--') + $Pathspec
    $changed = Invoke-GitQuiet @args
    if ($null -eq $changed -or $changed.Trim().Length -eq 0) {
        return @()
    }
    return @($changed -split "`n" | Where-Object { $_ -and $_.Trim().Length -gt 0 })
}

function Get-DesktopBuildPlan {
    param(
        [string]$BeforeHead,
        [string]$AfterHead
    )

    if ($ForceDesktopBuild) {
        return @{
            Needed = $true
            Reason = 'ForceDesktopBuild requested'
            Files = @()
        }
    }

    if (-not (Test-Path -LiteralPath $DesktopExe)) {
        return @{
            Needed = $true
            Reason = "Desktop executable missing: $DesktopExe"
            Files = @()
        }
    }

    $builtCommit = Get-DesktopBuiltCommit
    if (-not $builtCommit) {
        return @{
            Needed = $true
            Reason = "Desktop build stamp missing or unreadable: $DesktopStamp"
            Files = @()
        }
    }

    $sinceBuilt = Get-ChangedFiles -From $builtCommit -To $AfterHead -Pathspec $DesktopPathspec
    if ($sinceBuilt.Count -gt 0) {
        return @{
            Needed = $true
            Reason = "Desktop source changed since local build $($builtCommit.Substring(0, [Math]::Min(10, $builtCommit.Length)))"
            Files = $sinceBuilt
        }
    }

    $duringUpdate = Get-ChangedFiles -From $BeforeHead -To $AfterHead -Pathspec $DesktopPathspec
    if ($duringUpdate.Count -gt 0) {
        return @{
            Needed = $true
            Reason = 'Desktop source changed during this update'
            Files = $duringUpdate
        }
    }

    return @{
        Needed = $false
        Reason = 'Desktop build is current for the checked desktop source'
        Files = @()
    }
}

function Invoke-DesktopBuild {
    Write-Step 'Rebuilding local Desktop shell from source'
    Write-Host "Desktop source: $DesktopDir"
    Write-Host "Desktop output: $DesktopExe"
    $env:HERMES_HOME = $HermesHome
    $env:HERMES_DESKTOP_HERMES_ROOT = $Repo

    $oldPreference = $global:ErrorActionPreference
    $global:ErrorActionPreference = 'Continue'
    & $HermesExe desktop --build-only --hermes-root $Repo
    $buildExit = $LASTEXITCODE
    $global:ErrorActionPreference = $oldPreference
    if ($buildExit -ne 0) {
        throw "Desktop build failed with exit code $buildExit"
    }
}

function Show-State {
    $branch = Invoke-GitQuiet rev-parse --abbrev-ref HEAD
    $head = Invoke-GitQuiet rev-parse --short HEAD
    $origin = Invoke-GitQuiet rev-parse --short origin/main
    $upstream = Invoke-GitQuiet rev-parse --short upstream/main
    $aheadBehind = Invoke-GitQuiet rev-list --left-right --count upstream/main...origin/main
    $builtCommit = Get-DesktopBuiltCommit
    if (-not $builtCommit) {
        $builtCommit = '<none>'
    }
    elseif ($builtCommit.Length -gt 10) {
        $builtCommit = $builtCommit.Substring(0, 10)
    }

    Write-Host "Repo:        $Repo"
    Write-Host "Branch:      $branch @ $head"
    Write-Host "origin/main: $origin"
    Write-Host "upstream:    $upstream"
    Write-Host "fork diff:   $aheadBehind (upstream...origin)"
    Write-Host "HEAD patch:  $(Test-HeadPatchPresent)"
    Write-Host "Work patch:  $(Test-WorkingPatchPresent)"
    Write-Host "Patch file:  $PatchFile"
    Write-Host "Desktop exe: $(Test-Path -LiteralPath $DesktopExe)"
    Write-Host "Desktop at:  $builtCommit"
}

if (-not (Test-Path -LiteralPath $Repo)) {
    throw "Repo not found: $Repo"
}
if (-not (Test-Path -LiteralPath $PatchFile)) {
    throw "Patch file not found: $PatchFile"
}
if (-not (Test-Path -LiteralPath $HermesExe)) {
    throw "Hermes executable not found: $HermesExe"
}
if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}
if (-not (Test-Path -LiteralPath $DesktopDir)) {
    throw "Desktop source directory not found: $DesktopDir"
}

Set-Location -LiteralPath $Repo
$env:HERMES_HOME = $HermesHome
$env:HERMES_DESKTOP_HERMES_ROOT = $Repo
if ($CodexHome -and -not $env:CODEX_HOME) {
    $env:CODEX_HOME = $CodexHome
}
if ($GitSshCommand) {
    $env:GIT_SSH_COMMAND = $GitSshCommand
}

Write-Step 'Current state'
Show-State

$beforeHead = Get-HeadSha

if ($DesktopBuildOnly) {
    Invoke-DesktopBuild
    Write-Step 'Final state'
    Show-State
    Write-Host 'Done. Desktop shell rebuilt from the current local source.'
    exit 0
}

if ($CheckOnly) {
    Write-Step 'Checking official Hermes update status'
    $oldPreference = $global:ErrorActionPreference
    $global:ErrorActionPreference = 'Continue'
    & $HermesExe update --check @HermesArgs
    $checkExit = $LASTEXITCODE
    $global:ErrorActionPreference = $oldPreference
    if ($checkExit -ne 0) {
        exit $checkExit
    }

    $plan = Get-DesktopBuildPlan -BeforeHead $beforeHead -AfterHead $beforeHead
    Write-Step 'Desktop build check'
    Write-Host $plan.Reason
    if ($plan.Files.Count -gt 0) {
        $plan.Files | Select-Object -First 30 | ForEach-Object { Write-Host "  $_" }
        if ($plan.Files.Count -gt 30) {
            Write-Host "  ... $($plan.Files.Count - 30) more"
        }
    }
    Write-Host 'CheckOnly requested; no files changed.'
    exit 0
}

$removedPatch = $false
$headHasPatch = Test-HeadPatchPresent
$workHasPatch = Test-WorkingPatchPresent

if (-not $headHasPatch -and $workHasPatch) {
    Write-Step 'Removing local Windows Codex patch before update'
    Unstage-RunAgentIfNeeded
    if (-not (Test-GitCommandClean apply --reverse --check $PatchFile)) {
        throw 'run_agent.py contains the Codex marker, but the known patch cannot be reversed cleanly. Please inspect local edits before updating.'
    }
    Invoke-GitChecked apply --reverse $PatchFile
    $removedPatch = $true
}
elseif ($headHasPatch) {
    Write-Step 'Patch is already committed in HEAD; leaving it in place before update'
}
else {
    Write-Step 'No local patch to remove before update'
}

$dirty = Get-TrackedDirtyLines
if ($dirty.Count -gt 0) {
    Write-Host 'Tracked local changes remain after patch cleanup:'
    $dirty | ForEach-Object { Write-Host "  $_" }
    throw 'Refusing to run hermes update with unrelated tracked changes. Commit, stash, or inspect them first.'
}

Write-Step 'Running hermes update'
$oldPreference = $global:ErrorActionPreference
$global:ErrorActionPreference = 'Continue'
& $HermesExe update @HermesArgs
$updateExit = $LASTEXITCODE
$global:ErrorActionPreference = $oldPreference

if ($updateExit -ne 0) {
    Write-Host "hermes update failed with exit code $updateExit."
    if ($removedPatch -and -not (Test-WorkingPatchPresent) -and -not (Test-HeadPatchPresent)) {
        Write-Host 'Trying to restore the local Windows Codex patch after failed update...'
        Apply-LocalPatch
    }
    exit $updateExit
}

$afterHead = Get-HeadSha

Write-Step 'Ensuring Windows Codex patch is present'
if (Test-HeadPatchPresent) {
    Write-Host 'Patch is already present in HEAD; no local patch needed.'
}
elseif (Test-WorkingPatchPresent) {
    Write-Host 'Patch is already present in the working tree.'
}
else {
    Apply-LocalPatch
    Write-Host 'Applied local Windows Codex patch.'
}

Write-Step 'Validating run_agent.py'
$oldPreference = $global:ErrorActionPreference
$global:ErrorActionPreference = 'Continue'
& $PythonExe -m py_compile $RunAgent
$compileExit = $LASTEXITCODE
$global:ErrorActionPreference = $oldPreference
if ($compileExit -ne 0) {
    throw 'py_compile failed for run_agent.py after applying the local patch.'
}

if ($SkipDesktopBuild) {
    Write-Step 'Desktop build skipped'
}
else {
    Write-Step 'Checking Desktop source/build status'
    $plan = Get-DesktopBuildPlan -BeforeHead $beforeHead -AfterHead $afterHead
    Write-Host $plan.Reason
    if ($plan.Files.Count -gt 0) {
        $plan.Files | Select-Object -First 30 | ForEach-Object { Write-Host "  $_" }
        if ($plan.Files.Count -gt 30) {
            Write-Host "  ... $($plan.Files.Count - 30) more"
        }
    }
    if ($plan.Needed) {
        Invoke-DesktopBuild
    }
}

Write-Step 'Final state'
Show-State
Write-Host 'Done. Continue using Hermes normally; run this script instead of plain hermes update until the upstream fix is merged.'
