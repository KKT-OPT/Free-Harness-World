param(
    [ValidateSet("status", "init", "commit", "push", "commit-and-push")]
    [string]$Mode = "status",

    [string]$Root = "",

    [string]$RemoteName = "origin",

    [string]$RemoteUrl = $env:HARNESS_GIT_REMOTE_URL,

    [string]$BaseBranch = "main",

    [string]$AgentBranch = "agent-git",

    [string]$CommitMessage = "Update Harness framework assets",

    [string]$Registry = "user/registry/projects.local.json",

    [string]$GitSshCommand = $env:GIT_SSH_COMMAND,

    [switch]$SkipGovernanceCheck,

    [switch]$AllowNoChanges
)

$ErrorActionPreference = "Stop"

function Find-HarnessRoot {
    $dir = $PSScriptRoot
    while ($dir) {
        if (Test-Path -LiteralPath (Join-Path $dir "AGENTS.md")) {
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

function Set-OptionalEnv {
    param(
        [string]$Name,
        [AllowNull()][string]$Value
    )
    if ($null -eq $Value) {
        Remove-Item -Path "Env:$Name" -ErrorAction SilentlyContinue
    } else {
        Set-Item -Path "Env:$Name" -Value $Value
    }
}

function Invoke-GitChecked {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

    $oldPrompt = $env:GIT_TERMINAL_PROMPT
    $oldSsh = $env:GIT_SSH_COMMAND
    $oldPreference = $global:ErrorActionPreference
    Set-OptionalEnv -Name "GIT_TERMINAL_PROMPT" -Value "0"
    if ($script:EffectiveGitSshCommand) {
        Set-OptionalEnv -Name "GIT_SSH_COMMAND" -Value $script:EffectiveGitSshCommand
    }

    try {
        $global:ErrorActionPreference = "Continue"
        $output = @(& git @Arguments 2>&1 | ForEach-Object { $_.ToString() })
        $code = $LASTEXITCODE
    } finally {
        $global:ErrorActionPreference = $oldPreference
        Set-OptionalEnv -Name "GIT_TERMINAL_PROMPT" -Value $oldPrompt
        Set-OptionalEnv -Name "GIT_SSH_COMMAND" -Value $oldSsh
    }

    if ($code -ne 0) {
        $joined = $output -join [Environment]::NewLine
        throw "git $($Arguments -join ' ') failed with exit code $code`n$joined"
    }
    return $output
}

function Test-GitSuccess {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $oldPreference = $global:ErrorActionPreference
    $global:ErrorActionPreference = "Continue"
    try {
        & git @Arguments *> $null
        return ($LASTEXITCODE -eq 0)
    } finally {
        $global:ErrorActionPreference = $oldPreference
    }
}

function Get-CurrentBranch {
    $branch = @(Invoke-GitChecked branch --show-current)
    if ($branch.Count -eq 0) { return "" }
    return $branch[0].Trim()
}

function Test-PathExcludedFromSensitiveScan {
    param([string]$Path)

    $normalized = $Path -replace "\\", "/"
    foreach ($prefix in @(
        "projects/",
        "var/",
        "user/settings/",
        "user/github/",
        "user/auth/",
        "harness/tools/scripts/runtime/",
        "harness/tools/external/"
    )) {
        if ($normalized.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Invoke-GovernanceCheck {
    param([string]$RootPath)

    if ($SkipGovernanceCheck) {
        return [pscustomobject]@{ status = "skipped"; findingCount = $null }
    }

    $scriptPath = Join-Path $RootPath "harness/tools/scripts/stable/test-harness-governance.ps1"
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        throw "Governance self-check script missing: harness/tools/scripts/stable/test-harness-governance.ps1"
    }

    $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $scriptPath -Root $RootPath -Registry $Registry
    $result = $raw | ConvertFrom-Json
    if ($result.status -ne "passed") {
        throw "Governance self-check failed with status=$($result.status)."
    }
    return [pscustomobject]@{
        status = $result.status
        findingCount = $result.summary.findingCount
    }
}

function Initialize-Or-VerifyGit {
    param([string]$RootPath)

    $gitDir = Join-Path $RootPath ".git"
    $repoExists = Test-Path -LiteralPath $gitDir -PathType Container

    if (-not $repoExists) {
        if (-not $RemoteUrl) {
            throw "RemoteUrl is required when initializing a new Harness Root repository."
        }
        Invoke-GitChecked init | Out-Null
        Invoke-GitChecked remote add $RemoteName $RemoteUrl | Out-Null
        Invoke-GitChecked fetch $RemoteName $BaseBranch | Out-Null
        Invoke-GitChecked symbolic-ref HEAD "refs/heads/$AgentBranch" | Out-Null
        Invoke-GitChecked update-ref "refs/heads/$AgentBranch" "refs/remotes/$RemoteName/$BaseBranch" | Out-Null
        Invoke-GitChecked reset --mixed | Out-Null
        return
    }

    $remoteExists = Test-GitSuccess remote get-url $RemoteName
    if ($RemoteUrl) {
        if ($remoteExists) {
            Invoke-GitChecked remote set-url $RemoteName $RemoteUrl | Out-Null
        } else {
            Invoke-GitChecked remote add $RemoteName $RemoteUrl | Out-Null
        }
    } elseif (-not $remoteExists) {
        throw "Remote $RemoteName is missing. Pass -RemoteUrl or set HARNESS_GIT_REMOTE_URL."
    }

    Invoke-GitChecked fetch $RemoteName $BaseBranch | Out-Null

    $currentBranch = Get-CurrentBranch
    if ($currentBranch -eq $BaseBranch) {
        throw "Refusing to operate on base branch $BaseBranch. Switch to $AgentBranch first."
    }

    $agentBranchExists = Test-GitSuccess rev-parse --verify "refs/heads/$AgentBranch"
    if (-not $agentBranchExists) {
        Invoke-GitChecked branch $AgentBranch "$RemoteName/$BaseBranch" | Out-Null
    }

    if ($currentBranch -ne $AgentBranch) {
        Invoke-GitChecked checkout $AgentBranch | Out-Null
    }
}

function Test-StagedSensitiveContent {
    param([string]$RootPath)

    $findings = New-Object System.Collections.ArrayList
    $files = @(Invoke-GitChecked diff --cached --name-only)
    foreach ($file in $files) {
        if (Test-PathExcludedFromSensitiveScan -Path $file) { continue }
        $full = Join-Path $RootPath ($file -replace "/", "\")
        if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { continue }
        $extension = [System.IO.Path]::GetExtension($full).ToLowerInvariant()
        if ($extension -notin @(".md", ".json", ".yaml", ".yml", ".ps1", ".txt", ".gitignore", ".gitattributes")) {
            continue
        }
        $text = Get-Content -Raw -LiteralPath $full
        if ($text -match '[A-Za-z]:\\[A-Za-z0-9_. $(){}\[\]-]') {
            [void]$findings.Add("Concrete local path detected in staged file: $file")
        }
        if ($text -match '(?i)(password|token|secret)\s*[:=]\s*[^\s`]{8,}') {
            [void]$findings.Add("Credential-like assignment detected in staged file: $file")
        }
    }

    if ($findings.Count -gt 0) {
        throw ($findings -join [Environment]::NewLine)
    }
}

function Commit-HarnessChanges {
    param([string]$RootPath)

    Invoke-GovernanceCheck -RootPath $RootPath | Out-Null
    Invoke-GitChecked add . | Out-Null
    Invoke-GitChecked diff --cached --check | Out-Null
    Test-StagedSensitiveContent -RootPath $RootPath

    $staged = @(Invoke-GitChecked diff --cached --name-only)
    if ($staged.Count -eq 0) {
        if ($AllowNoChanges) {
            return [pscustomobject]@{ committed = $false; sha = $null; stagedFileCount = 0 }
        }
        throw "No staged changes to commit."
    }

    Invoke-GitChecked commit -m $CommitMessage | Out-Null
    $sha = @(Invoke-GitChecked rev-parse --short HEAD)[0].Trim()
    return [pscustomobject]@{
        committed = $true
        sha = $sha
        stagedFileCount = $staged.Count
    }
}

function Push-AgentBranch {
    Invoke-GitChecked push -u $RemoteName $AgentBranch | Out-Null
    $heads = @(Invoke-GitChecked ls-remote --heads $RemoteName $BaseBranch $AgentBranch)
    return $heads
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is not available on PATH."
}

$rootPath = if ([string]::IsNullOrWhiteSpace($Root)) { Find-HarnessRoot } else { (Resolve-Path -LiteralPath $Root).Path }
Set-Location -LiteralPath $rootPath
$script:EffectiveGitSshCommand = $GitSshCommand

$commitResult = $null
$pushHeads = @()

if ($Mode -in @("init", "commit", "push", "commit-and-push")) {
    Initialize-Or-VerifyGit -RootPath $rootPath
}

if ($Mode -in @("commit", "commit-and-push")) {
    $commitResult = Commit-HarnessChanges -RootPath $rootPath
}

if ($Mode -in @("push", "commit-and-push")) {
    $pushHeads = Push-AgentBranch
}

$branch = Get-CurrentBranch
$head = @(Invoke-GitChecked rev-parse --short HEAD)[0].Trim()
$statusLines = @(Invoke-GitChecked status --short --branch)

[pscustomobject]@{
    status = "passed"
    mode = $Mode
    root = $rootPath
    branch = $branch
    head = $head
    remote = $RemoteName
    baseBranch = $BaseBranch
    agentBranch = $AgentBranch
    commit = $commitResult
    pushedHeads = $pushHeads
    statusLines = $statusLines
} | ConvertTo-Json -Depth 6
