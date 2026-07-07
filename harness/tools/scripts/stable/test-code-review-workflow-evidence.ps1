param(
    [string]$Root = ".",
    [string]$Registry = "user/registry/projects.local.json",
    [string]$ProjectId = "",
    [string[]]$WorkflowEvidence = @(),
    [switch]$RequireUserReview,
    [switch]$RequireFixDisposition,
    [switch]$RequireRecheck,
    [switch]$RequireFinalReview,
    [switch]$RequireClosedLoop,
    [switch]$SelfTest
)

$ErrorActionPreference = "Stop"

function New-Finding {
    param(
        [string]$Severity,
        [string]$Code,
        [string]$Path,
        [string]$Message,
        [string]$RepairSuggestion
    )

    [pscustomobject]@{
        severity = $Severity
        code = $Code
        path = $Path
        message = $Message
        repairSuggestion = $RepairSuggestion
    }
}

function Add-Finding {
    param(
        [object]$List,
        [object]$ListRef,
        [string]$Severity,
        [string]$Code,
        [string]$Path,
        [string]$Message,
        [string]$RepairSuggestion
    )

    $target = if ($PSBoundParameters.ContainsKey("ListRef")) { $ListRef } else { $List }
    if ($null -ne $target -and $target.PSObject.Properties.Name -contains "Store") {
        $target = $target.Store
    } elseif ($null -ne $target -and $target.PSObject.Properties.Name -contains "Value") {
        $target = $target.Value
    }
    if ($null -eq $target -and ($script:FindingSinkStore -is [System.Collections.IList] -or $script:FindingSinkStore -is [hashtable])) {
        $target = $script:FindingSinkStore
    }
    while ($target -is [System.Collections.IList] -and $target.Count -eq 1 -and $target[0] -is [System.Collections.IList]) {
        $target = $target[0]
    }
    if (($null -eq $target -or (-not ($target -is [System.Collections.IList]) -and -not ($target -is [hashtable])) -or ($target -is [System.Collections.IList] -and $target.IsFixedSize)) -and ($script:FindingSinkStore -is [System.Collections.IList] -or $script:FindingSinkStore -is [hashtable])) {
        $target = $script:FindingSinkStore
    }

    $finding = New-Finding -Severity $Severity -Code $Code -Path $Path -Message $Message -RepairSuggestion $RepairSuggestion
    if ($target -is [hashtable] -and $target.ContainsKey("items")) {
        $target.items = @($target.items) + $finding
        return
    }

    if ($null -eq $target -or -not ($target -is [System.Collections.IList]) -or $target.IsFixedSize) {
        $typeName = if ($null -eq $target) { "<null>" } else { $target.GetType().FullName }
        throw "Findings list is not writable: $typeName."
    }

    [void]$target.Add($finding)
}

function Convert-ToRelativePath {
    param(
        [string]$RootPath,
        [string]$Path
    )

    $full = [System.IO.Path]::GetFullPath($Path)
    $rootFull = [System.IO.Path]::GetFullPath($RootPath)
    if ($full.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $full.Substring($rootFull.Length).TrimStart('\', '/') -replace '\\', '/'
    }
    return $Path -replace '\\', '/'
}

function Test-RelativePath {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) { return $false }
    if ([System.IO.Path]::IsPathRooted($Value)) { return $false }
    if ($Value -match '(^|[\\/])\.\.([\\/]|$)') { return $false }
    if ($Value -match '^[A-Za-z]:') { return $false }
    return $true
}

function Join-And-Resolve {
    param(
        [string]$Base,
        [string]$Relative
    )

    $combined = Join-Path $Base ($Relative -replace '/', '\')
    if (Test-Path -LiteralPath $combined) {
        return (Resolve-Path -LiteralPath $combined).Path
    }
    return [System.IO.Path]::GetFullPath($combined)
}

function Test-IsInsidePath {
    param(
        [string]$Path,
        [string]$Parent
    )

    $pathFull = [System.IO.Path]::GetFullPath($Path)
    $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\', '/')
    return $pathFull.StartsWith($parentFull + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase) -or
        $pathFull.Equals($parentFull, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-MarkdownFrontMatter {
    param(
        [string]$Text,
        [string]$Path,
        [object]$FindingsRef
    )

    if ($Text -notmatch '(?s)^---\s*\r?\n.*?\r?\n---') {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "frontmatterMissing" -Path $Path -Message "Code review workflow evidence is missing YAML frontmatter." -RepairSuggestion "Add standard Harness Markdown frontmatter."
        return
    }

    $statusMatch = [regex]::Match($Text, '(?m)^status:[ \t]*([a-zA-Z0-9_-]+)[ \t]*(?:\r)?$')
    if (-not $statusMatch.Success) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "frontmatterStatusMissing" -Path $Path -Message "Markdown frontmatter is missing status." -RepairSuggestion "Set status to draft, review, active, stale, deprecated, archived or superseded."
        return
    }

    $allowed = @("draft", "review", "active", "stale", "deprecated", "archived", "superseded")
    $status = $statusMatch.Groups[1].Value
    if ($allowed -notcontains $status) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "frontmatterStatusInvalid" -Path $Path -Message "Markdown frontmatter status is invalid: $status." -RepairSuggestion "Use a supported Harness document status."
    }
}

function Get-YamlScalar {
    param(
        [string]$Text,
        [string]$Key
    )

    $match = [regex]::Match($Text, "(?m)^$([regex]::Escape($Key)):[ \t]*([^#\r\n]+)[ \t]*(?:\r)?$")
    if ($match.Success) {
        return $match.Groups[1].Value.Trim().Trim('"', "'")
    }
    return ""
}

function Test-CodeReviewEvidenceText {
    param(
        [string]$Text,
        [string]$Path,
        [object]$FindingsRef,
        [bool]$RequireUserReviewValue,
        [bool]$RequireFixDispositionValue,
        [bool]$RequireRecheckValue,
        [bool]$RequireFinalReviewValue,
        [bool]$RequireClosedLoopValue
    )

    $checks = @(
        @{
            code = "codeReviewTaskBriefMissing"
            pattern = '(?is)(^|\n)##\s*\d*\.?\s*Task Brief|\bTask Brief\b|taskId:'
            message = "Code review evidence does not contain a Task Brief."
            repair = "Record taskId, projectId, goal, scope, acceptance criteria, risk and approval requirement."
        },
        @{
            code = "codeReviewScopeMissing"
            pattern = '(?is)reviewTarget|review target|Scope|targetFiles'
            message = "Code review evidence does not define review scope or target files."
            repair = "Record review target files, context files, tests and forbidden paths."
        },
        @{
            code = "codeReviewTraceMissing"
            pattern = '(?is)Trace|command summary|rg -n|git diff|Get-Content'
            message = "Code review evidence does not contain trace or command evidence."
            repair = "Record entry documents, searched symbols, inspected files and command summaries."
        },
        @{
            code = "codeReviewFindingsMissing"
            pattern = '(?is)Findings|finding|\bP[0-3]\b|severity'
            message = "Code review evidence does not contain review findings."
            repair = "Record findings with severity, file, line, evidence, impact and suggestion, or explicitly state no blocking findings."
        },
        @{
            code = "codeReviewUserReviewMissing"
            pattern = '(?is)User Review|userFeedbackState|reviewedBy|decision:|approve|reject|revise|defer'
            message = "Code review evidence does not contain user review or feedback section."
            repair = "Record user decision for findings: approve, reject, revise, defer or pending."
        },
        @{
            code = "codeReviewFixHandoffMissing"
            pattern = '(?is)Fix Handoff|Fix Plan|fixState|implementation'
            message = "Code review evidence does not contain fix handoff or implementation state."
            repair = "Record whether code modification is requested, not started, not required, partial, blocked or fixed pending recheck."
        },
        @{
            code = "codeReviewRecheckMissing"
            pattern = '(?is)Recheck|recheckState'
            message = "Code review evidence does not contain recheck state."
            repair = "Record recheck state after implementation or mark it pending."
        },
        @{
            code = "codeReviewFinalReviewMissing"
            pattern = '(?is)Final Review|finalUserReview'
            message = "Code review evidence does not contain final user review state."
            repair = "Record final user review as pending, accepted, rejected or deferred."
        }
    )

    foreach ($check in $checks) {
        if ($Text -notmatch $check.pattern) {
            Add-Finding -ListRef $FindingsRef -Severity "error" -Code $check.code -Path $Path -Message $check.message -RepairSuggestion $check.repair
        }
    }

    if ($Text -match '(?<![A-Za-z])[A-Za-z]:[\\/]') {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewConcretePrivatePath" -Path $Path -Message "Code review evidence contains a concrete private absolute path." -RepairSuggestion "Use project-relative paths or redacted placeholders in tracked workflow evidence."
    }

    if ($Text -match '(?i)(password|token|secret)\s*[:=]\s*["'']?[A-Za-z0-9_\-]{8,}') {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewPossibleCredential" -Path $Path -Message "Code review evidence contains a possible credential-like assignment." -RepairSuggestion "Remove credentials from tracked workflow evidence."
    }

    $codeReviewState = Get-YamlScalar -Text $Text -Key "codeReviewState"
    $userFeedbackState = Get-YamlScalar -Text $Text -Key "userFeedbackState"
    $fixState = Get-YamlScalar -Text $Text -Key "fixState"
    $recheckState = Get-YamlScalar -Text $Text -Key "recheckState"
    $finalUserReview = Get-YamlScalar -Text $Text -Key "finalUserReview"

    $allowedCodeReviewStates = @(
        "review-draft",
        "user-reviewed",
        "fix-requested",
        "fixed-pending-recheck",
        "rechecked",
        "accepted",
        "rejected-or-deferred"
    )

    if ([string]::IsNullOrWhiteSpace($codeReviewState)) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewStateMissing" -Path $Path -Message "codeReviewState is missing." -RepairSuggestion "Add codeReviewState under the workflow evidence closeout state block."
    } elseif ($allowedCodeReviewStates -notcontains $codeReviewState) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewStateInvalid" -Path $Path -Message "codeReviewState is invalid: $codeReviewState." -RepairSuggestion "Use review-draft, user-reviewed, fix-requested, fixed-pending-recheck, rechecked, accepted or rejected-or-deferred."
    }

    foreach ($statePair in @(
        @{ key = "userFeedbackState"; value = $userFeedbackState },
        @{ key = "fixState"; value = $fixState },
        @{ key = "recheckState"; value = $recheckState },
        @{ key = "finalUserReview"; value = $finalUserReview }
    )) {
        if ([string]::IsNullOrWhiteSpace($statePair.value)) {
            Add-Finding -ListRef $FindingsRef -Severity "error" -Code "$($statePair.key)Missing" -Path $Path -Message "$($statePair.key) is missing." -RepairSuggestion "Add $($statePair.key) to the code review workflow state block, using pending when the step has not happened yet."
        }
    }

    if ($RequireUserReviewValue -and $codeReviewState -eq "review-draft") {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewUserReviewRequired" -Path $Path -Message "User review is required but codeReviewState is still review-draft." -RepairSuggestion "Record approve, reject, revise or defer decision before requiring user review completion."
    }

    if ($RequireFixDispositionValue -and ($fixState -match '^(pending|not-started)?$')) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewFixDispositionRequired" -Path $Path -Message "Fix disposition is required but fixState is pending or not-started." -RepairSuggestion "Record not-required, blocked, partial, fixed-pending-recheck or another explicit fix disposition."
    }

    if ($RequireRecheckValue -and ($recheckState -match '^(pending|not-started)?$')) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewRecheckRequired" -Path $Path -Message "Recheck is required but recheckState is pending." -RepairSuggestion "Run code review recheck after implementation and record the result."
    }

    if ($RequireFinalReviewValue -and ($finalUserReview -match '^(pending|not-started)?$')) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewFinalReviewRequired" -Path $Path -Message "Final user review is required but finalUserReview is pending." -RepairSuggestion "Record final user decision before closing the workflow."
    }

    if ($RequireClosedLoopValue) {
        if ($codeReviewState -ne "accepted") {
            Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewClosedLoopNotAccepted" -Path $Path -Message "Closed loop is required but codeReviewState is not accepted." -RepairSuggestion "Complete user review, implementation, recheck and final user acceptance before requiring closed loop."
        }
        if ($finalUserReview -notmatch '^(accepted|approved|approved-by-user)$') {
            Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewFinalAcceptanceMissing" -Path $Path -Message "Closed loop is required but finalUserReview does not show acceptance." -RepairSuggestion "Record accepted final user review after recheck."
        }
        if ($recheckState -match '^(pending|not-started)?$') {
            Add-Finding -ListRef $FindingsRef -Severity "error" -Code "codeReviewClosedLoopRecheckMissing" -Path $Path -Message "Closed loop is required but recheckState is pending." -RepairSuggestion "Run and record recheck before closing the code review workflow."
        }
    }
}

function Resolve-ProjectFromRegistry {
    param(
        [string]$RootPath,
        [string]$RegistryPath,
        [string]$RequestedProjectId,
        [object]$FindingsRef
    )

    $registryFullPath = Join-Path $RootPath ($RegistryPath -replace '/', '\')
    if (-not (Test-Path -LiteralPath $registryFullPath -PathType Leaf)) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "registryMissing" -Path $RegistryPath -Message "Project registry file does not exist." -RepairSuggestion "Create user/registry/projects.local.json or pass the correct -Registry path."
        return $null
    }

    $registryObject = Get-Content -Raw -LiteralPath $registryFullPath | ConvertFrom-Json
    $projects = @($registryObject.projects)
    $effectiveProjectId = $RequestedProjectId
    if ([string]::IsNullOrWhiteSpace($effectiveProjectId)) {
        if ($projects.Count -eq 1) {
            $effectiveProjectId = [string]$projects[0].projectId
        } else {
            Add-Finding -ListRef $FindingsRef -Severity "error" -Code "projectIdRequired" -Path $RegistryPath -Message "ProjectId is required when registry contains zero or multiple projects." -RepairSuggestion "Pass -ProjectId explicitly."
            return $null
        }
    }

    $project = @($projects | Where-Object { $_.projectId -eq $effectiveProjectId }) | Select-Object -First 1
    if ($null -eq $project) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "projectNotRegistered" -Path $RegistryPath -Message "Project is not registered: $effectiveProjectId." -RepairSuggestion "Add the project to the local registry or pass the correct ProjectId."
        return $null
    }

    if (-not (Test-RelativePath -Value $project.root)) {
        Add-Finding -ListRef $FindingsRef -Severity "error" -Code "projectRootNotRelative" -Path $RegistryPath -Message "Project registry root must be relative." -RepairSuggestion "Use projects/<project-id> as a relative project root."
        return $null
    }

    $projectRoot = Join-And-Resolve -Base $RootPath -Relative ([string]$project.root)
    [pscustomobject]@{
        projectId = $effectiveProjectId
        root = $projectRoot
        relativeRoot = Convert-ToRelativePath -RootPath $RootPath -Path $projectRoot
    }
}

function Resolve-WorkflowEvidencePath {
    param(
        [string]$RootPath,
        [object]$Project,
        [string]$InputPath
    )

    if ([System.IO.Path]::IsPathRooted($InputPath)) {
        return [System.IO.Path]::GetFullPath($InputPath)
    }

    $normalized = $InputPath -replace '\\', '/'
    if ($normalized.StartsWith("projects/", [System.StringComparison]::OrdinalIgnoreCase)) {
        return Join-And-Resolve -Base $RootPath -Relative $normalized
    }

    if ($null -ne $Project) {
        return Join-And-Resolve -Base $Project.root -Relative $normalized
    }

    return Join-And-Resolve -Base $RootPath -Relative $normalized
}

function Invoke-SelfTest {
    $findings = @()

    $good = @"
---
documentName: sample.md
status: draft
---
# Code Review Evidence

## 1. Task Brief
taskId: sample
projectId: sample

## 2. Scope
reviewTarget:
  - src/main/java/Sample.java

## 3. Trace
rg -n "Sample" src

## 4. Findings
| P2 | src/main/java/Sample.java:1 | evidence | impact | suggestion |

## 5. User Review
decision: approved

## 6. Fix Handoff
Fix Plan completed.

## 7. Recheck
Recheck passed.

## 8. Final Review
final review accepted.

```yaml
codeReviewState: accepted
userFeedbackState: approved
fixState: fixed
recheckState: passed
finalUserReview: accepted
```
"@

    $requiredGoodPatterns = @(
        '(?s)^---\s*\r?\n.*?\r?\n---',
        '(?is)(^|\n)##\s*\d*\.?\s*Task Brief|\bTask Brief\b|taskId:',
        '(?is)reviewTarget|review target|Scope|targetFiles',
        '(?is)Trace|command summary|rg -n|git diff|Get-Content',
        '(?is)Findings|finding|\bP[0-3]\b|severity',
        '(?is)User Review|userFeedbackState|reviewedBy|decision:|approve|reject|revise|defer',
        '(?is)Fix Handoff|Fix Plan|fixState|implementation',
        '(?is)Recheck|recheckState',
        '(?is)Final Review|finalUserReview'
    )
    foreach ($pattern in $requiredGoodPatterns) {
        if ($good -notmatch $pattern) {
            $findings += (New-Finding -Severity "error" -Code "selfTestGoodPatternMissing" -Path "self-test-good" -Message "Good fixture did not match expected pattern." -RepairSuggestion "Repair self-test fixture or pattern.")
        }
    }
    foreach ($state in @("codeReviewState", "userFeedbackState", "fixState", "recheckState", "finalUserReview")) {
        if ([string]::IsNullOrWhiteSpace((Get-YamlScalar -Text $good -Key $state))) {
            $findings += (New-Finding -Severity "error" -Code "selfTestGoodStateMissing" -Path "self-test-good" -Message "Good fixture state is missing: $state." -RepairSuggestion "Repair self-test fixture or state parser.")
        }
    }

    $bad = @"
---
status: draft
---
## 1. Task Brief
taskId: bad
"@
    $badExpectations = @{
        codeReviewScopeMissing = '(?is)reviewTarget|review target|Scope|targetFiles'
        codeReviewTraceMissing = '(?is)Trace|command summary|rg -n|git diff|Get-Content'
        codeReviewFindingsMissing = '(?is)Findings|finding|\bP[0-3]\b|severity'
    }
    foreach ($entry in $badExpectations.GetEnumerator()) {
        if ($bad -match $entry.Value) {
            $findings += (New-Finding -Severity "error" -Code "selfTestBadFixtureUnexpectedMatch" -Path "self-test-bad" -Message "Bad fixture unexpectedly matched missing check: $($entry.Key)." -RepairSuggestion "Repair self-test bad fixture.")
        }
    }
    if (-not [string]::IsNullOrWhiteSpace((Get-YamlScalar -Text $bad -Key "codeReviewState"))) {
        $findings += (New-Finding -Severity "error" -Code "selfTestBadStateUnexpected" -Path "self-test-bad" -Message "Bad fixture unexpectedly contains codeReviewState." -RepairSuggestion "Repair self-test bad fixture.")
    }

    $status = "passed"
    if (@($findings | Where-Object { $_.severity -eq "error" }).Count -gt 0) {
        $status = "failed"
    }

    [pscustomobject]@{
        status = $status
        mode = "self-test"
        findingCount = $findings.Count
        findings = @($findings)
    }
}

if ($SelfTest) {
    $selfTestResult = Invoke-SelfTest
    $selfTestResult | ConvertTo-Json -Depth 8
    if ($selfTestResult.status -eq "passed") { exit 0 } else { exit 1 }
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$findings = @{ items = @() }
$script:FindingSinkStore = $findings
$project = $null
if (-not [string]::IsNullOrWhiteSpace($ProjectId) -or (Test-Path -LiteralPath (Join-Path $rootPath ($Registry -replace '/', '\')) -PathType Leaf)) {
    $project = Resolve-ProjectFromRegistry -RootPath $rootPath -RegistryPath $Registry -RequestedProjectId $ProjectId -FindingsRef (New-Object psobject -Property @{ Store = $findings })
}

if ($WorkflowEvidence.Count -eq 0) {
    Add-Finding -List $findings -Severity "error" -Code "workflowEvidenceArgumentMissing" -Path "workflow-evidence" -Message "No code review workflow evidence paths were provided." -RepairSuggestion "Pass one or more -WorkflowEvidence paths under projects/<project-id>/docs/project/workflow/."
}

foreach ($item in $WorkflowEvidence) {
    $resolved = Resolve-WorkflowEvidencePath -RootPath $rootPath -Project $project -InputPath $item
    $relative = Convert-ToRelativePath -RootPath $rootPath -Path $resolved

    if ($relative -notmatch '^projects/[^/]+/docs/project/workflow/') {
        Add-Finding -List $findings -Severity "error" -Code "codeReviewWorkflowWrongLocation" -Path $relative -Message "Code review workflow evidence is not under docs/project/workflow/." -RepairSuggestion "Store real project code review evidence under projects/<project-id>/docs/project/workflow/."
        continue
    }

    if ($null -ne $project -and -not (Test-IsInsidePath -Path $resolved -Parent $project.root)) {
        Add-Finding -List $findings -Severity "error" -Code "codeReviewWorkflowOutOfProject" -Path $relative -Message "Code review workflow evidence is outside the selected project root." -RepairSuggestion "Pass evidence from the selected project instance."
        continue
    }

    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        Add-Finding -List $findings -Severity "error" -Code "codeReviewWorkflowMissing" -Path $relative -Message "Code review workflow evidence file does not exist." -RepairSuggestion "Create the workflow evidence file or pass the correct path."
        continue
    }

    $text = Get-Content -Raw -LiteralPath $resolved
    Test-MarkdownFrontMatter -Text $text -Path $relative -FindingsRef (New-Object psobject -Property @{ Store = $findings })
    Test-CodeReviewEvidenceText -Text $text -Path $relative -FindingsRef (New-Object psobject -Property @{ Store = $findings }) -RequireUserReviewValue ([bool]$RequireUserReview) -RequireFixDispositionValue ([bool]$RequireFixDisposition) -RequireRecheckValue ([bool]$RequireRecheck) -RequireFinalReviewValue ([bool]$RequireFinalReview) -RequireClosedLoopValue ([bool]$RequireClosedLoop)
}

$findingItems = @($findings.items)
$severityCounts = [ordered]@{
    error = @($findingItems | Where-Object { $_.severity -eq "error" }).Count
    warning = @($findingItems | Where-Object { $_.severity -eq "warning" }).Count
    info = @($findingItems | Where-Object { $_.severity -eq "info" }).Count
}

$status = "passed"
if ($severityCounts.error -gt 0) {
    $status = "failed"
}

$findingArray = @()
foreach ($item in $findingItems) { $findingArray += $item }
$effectiveProjectId = if ($null -ne $project -and $project.PSObject.Properties.Name -contains "projectId") { [string]$project.projectId } else { $ProjectId }

$output = [pscustomobject]@{
    status = $status
    mode = "code-review-workflow-evidence"
    root = $rootPath
    checkedAt = (Get-Date).ToString("s")
    projectId = $effectiveProjectId
    summary = [pscustomobject]@{
        workflowEvidenceCount = $WorkflowEvidence.Count
        requireUserReview = [bool]$RequireUserReview
        requireFixDisposition = [bool]$RequireFixDisposition
        requireRecheck = [bool]$RequireRecheck
        requireFinalReview = [bool]$RequireFinalReview
        requireClosedLoop = [bool]$RequireClosedLoop
        findingCount = $findingArray.Count
        severityCounts = $severityCounts
    }
    checks = @(
        "workflow-evidence-location",
        "workflow-frontmatter",
        "task-brief",
        "review-scope",
        "trace",
        "findings",
        "user-review",
        "fix-handoff",
        "recheck",
        "final-review",
        "state-block",
        "closed-loop"
    )
    findings = $findingArray
}

$output | ConvertTo-Json -Depth 8
if ($status -eq "passed") { exit 0 } else { exit 1 }
