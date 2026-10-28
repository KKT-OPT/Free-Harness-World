param(
    [string]$Root = ".",
    [string]$Registry = "user/registry/projects.local.json",
    [string]$ProjectId = "",
    [string[]]$WorkflowEvidence = @(),
    [string[]]$ProjectReport = @(),
    [switch]$RequireReport,
    [switch]$RequireUserAcceptance,
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
        [System.Collections.ArrayList]$List,
        [string]$Severity,
        [string]$Code,
        [string]$Path,
        [string]$Message,
        [string]$RepairSuggestion
    )

    [void]$List.Add((New-Finding -Severity $Severity -Code $Code -Path $Path -Message $Message -RepairSuggestion $RepairSuggestion))
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

function Resolve-ProjectFileInput {
    param(
        [string]$RootPath,
        [string]$ProjectRoot,
        [string]$InputPath
    )

    if ([System.IO.Path]::IsPathRooted($InputPath)) {
        return [System.IO.Path]::GetFullPath($InputPath)
    }

    $normalized = $InputPath -replace '\\', '/'
    if ($normalized.StartsWith("projects/", [System.StringComparison]::OrdinalIgnoreCase)) {
        return Join-And-Resolve -Base $RootPath -Relative $normalized
    }

    return Join-And-Resolve -Base $ProjectRoot -Relative $normalized
}

function Test-MarkdownFrontMatter {
    param(
        [string]$Text,
        [string]$Path,
        [System.Collections.ArrayList]$Findings
    )

    if ($Text -notmatch '(?s)^---\s*\r?\n.*?\r?\n---') {
        Add-Finding -List $Findings -Severity "error" -Code "frontmatterMissing" -Path $Path -Message "Markdown evidence is missing YAML frontmatter." -RepairSuggestion "Add the standard Harness Markdown frontmatter before using this file as lifecycle evidence."
        return
    }

    $statusMatch = [regex]::Match($Text, '(?m)^status:[ \t]*([a-zA-Z0-9_-]+)[ \t]*(?:\r)?$')
    if (-not $statusMatch.Success) {
        Add-Finding -List $Findings -Severity "error" -Code "frontmatterStatusMissing" -Path $Path -Message "Markdown frontmatter is missing status." -RepairSuggestion "Set status to draft, review, active, stale, deprecated, archived or superseded."
        return
    }

    $status = $statusMatch.Groups[1].Value
    $allowed = @("draft", "review", "active", "stale", "deprecated", "archived", "superseded")
    if ($allowed -notcontains $status) {
        Add-Finding -List $Findings -Severity "error" -Code "frontmatterStatusInvalid" -Path $Path -Message "Markdown frontmatter status is invalid: $status." -RepairSuggestion "Use a supported Harness document status."
    }
}

function Test-LifecycleTextCoverage {
    param(
        [string]$CombinedText,
        [System.Collections.ArrayList]$Findings,
        [bool]$RequireUserAcceptanceValue
    )

    $checks = @(
        @{
            code = "lifecycleTaskBriefMissing"
            pattern = '(?im)^#{1,6}\s*(?:\d+\.?\s*)?\u4efb\u52a1\u7b80\u62a5|\bTask Brief\b|taskId:'
            message = "Lifecycle evidence does not contain a Task Brief."
            repair = "Record goal, projectId, scope, acceptance criteria, validation plan, risk and approval requirement."
        },
        @{
            code = "lifecycleEntryRouteMissing"
            pattern = '(?is)AGENTS\.md.*ProjectIndex\.md|ProjectIndex\.md.*AGENTS\.md|project entry'
            message = "Lifecycle evidence does not show project entry routing."
            repair = "Record that the task entered through the project AGENTS.md and docs/project/ProjectIndex.md route."
        },
        @{
            code = "lifecyclePlanMissing"
            pattern = '(?im)^#{1,6}\s*(?:\d+\.?\s*)?(?:\u6267\u884c\u8ba1\u5212|\u65b9\u6848\u8bbe\u8ba1)|Execution Plan|implementation plan|repair plan|design'
            message = "Lifecycle evidence does not contain design or execution planning."
            repair = "Record the implementation plan or design decision before the execution record."
        },
        @{
            code = "lifecycleDevelopmentMissing"
            pattern = '(?im)^#{1,6}\s*(?:\d+\.?\s*)?(?:\u6267\u884c\u8bb0\u5f55|\u6587\u4ef6\u53d8\u66f4\u6458\u8981)|Execution Record|File Change Summary|file change|implementation'
            message = "Lifecycle evidence does not contain development or file-change evidence."
            repair = "Record changed files, implementation summary and why each change was needed."
        },
        @{
            code = "lifecycleValidationMissing"
            pattern = '(?im)^#{1,6}\s*(?:\d+\.?\s*)?(?:\u9a8c\u8bc1\u62a5\u544a|\u9a8c\u8bc1\u7ed3\u679c)|Verification Report|validation result|validation command|Regression|test-compile|JAVA_MAIN_PASS'
            message = "Lifecycle evidence does not contain validation or regression evidence."
            repair = "Record validation command summaries, status, regression result and residual risk."
        },
        @{
            code = "lifecycleGovernanceMissing"
            pattern = '(?im)^#{1,6}\s*(?:\d+\.?\s*)?(?:\u6cbb\u7406\u5019\u9009|\u5019\u9009\u6e05\u5355)|Governance Candidates|Candidate Table|candidate-first|Non-Promotion|candidate'
            message = "Lifecycle evidence does not contain governance candidate or closeout evidence."
            repair = "Record governance candidates, dispositions, targets and approval requirements."
        }
    )

    foreach ($check in $checks) {
        if ($CombinedText -notmatch $check.pattern) {
            Add-Finding -List $Findings -Severity "error" -Code $check.code -Path "workflow-evidence" -Message $check.message -RepairSuggestion $check.repair
        }
    }

    # A heading or an earlier approval cannot override an explicit pending/rejected final state.
    $finalDecisions = @([regex]::Matches($CombinedText, '(?m)^finalUserReview:[ \t]*([^#\r\n]*)') |
        ForEach-Object { $_.Groups[1].Value.Trim().Trim('"', "'") })
    $acceptancePresent = $CombinedText -match '(?im)^acceptedBy[ \t]*=[ \t]*user[ \t]*\r?$|^decision:[ \t]*(accepted|approved|approved-by-user)[ \t]*\r?$'
    if ($finalDecisions.Count -gt 0) {
        $acceptancePresent = @($finalDecisions | Where-Object { $_ -notin @("accepted", "approved", "approved-by-user") }).Count -eq 0
    }
    if ($RequireUserAcceptanceValue -and -not $acceptancePresent) {
        Add-Finding -List $Findings -Severity "error" -Code "lifecycleAcceptanceMissing" -Path "workflow-evidence" -Message "Lifecycle evidence does not contain user acceptance." -RepairSuggestion "Record accepted yes/no/pending, user feedback and repair requirement."
    }

    if ($CombinedText -notmatch '(?is)\u7a33\u5b9a\u5de5\u5177|stable tools|stable command surface|invoke-java-main\.ps1|invoke-maven-project\.ps1|Tool Invocation Evidence') {
        Add-Finding -List $Findings -Severity "warning" -Code "stableToolEvidenceMissing" -Path "workflow-evidence" -Message "Lifecycle evidence does not clearly show stable tool usage." -RepairSuggestion "Record the stable command surface used, or explain why the task did not require one."
    }
}

function Test-ProjectReportTextCoverage {
    param(
        [string]$ReportText,
        [string]$Path,
        [System.Collections.ArrayList]$Findings
    )

    $checks = @(
        @{
            code = "reportCandidateTableMissing"
            pattern = '(?im)^#{1,6}\s*(?:\d+\.?\s*)?(?:\u5019\u9009\u6e05\u5355|\u6cbb\u7406\u5019\u9009)|Candidate Table|Governance Candidates'
            message = "Project report is missing candidate table or governance candidate summary."
            repair = "Add candidate id, type, proposal, source evidence, target asset, disposition and approval requirement."
        },
        @{
            code = "reportApprovalMissing"
            pattern = '(?im)^#{1,6}\s*(?:\d+\.?\s*)?\u5ba1\u6838\u4e0e\u5904\u7f6e|Approval|Human approval|review-first|already-approved|acceptedBy[ \t]*=[ \t]*user'
            message = "Project report is missing approval or review evidence."
            repair = "Record who approved, what was approved and what remains pending."
        },
        @{
            code = "reportBoundaryMissing"
            pattern = '(?im)^#{1,6}\s*(?:\d+\.?\s*)?\u975e\u664b\u5347\u8fb9\u754c|Non-Promotion|not a fact source|promotion boundary|Report is not a fact'
            message = "Project report is missing non-promotion or fact-boundary statement."
            repair = "State that report suggestions are not facts until absorbed into the target asset after review."
        },
        @{
            code = "reportValidationMissing"
            pattern = '(?im)^#{1,6}\s*(?:\d+\.?\s*)?\u9a8c\u8bc1\u7ed3\u679c|Validation|self-check|git diff --check'
            message = "Project report is missing validation summary."
            repair = "Record validation commands, checks, residual findings and repair path."
        }
    )

    foreach ($check in $checks) {
        if ($ReportText -notmatch $check.pattern) {
            Add-Finding -List $Findings -Severity "error" -Code $check.code -Path $Path -Message $check.message -RepairSuggestion $check.repair
        }
    }
}

function Invoke-SelfTest {
    $findings = New-Object System.Collections.ArrayList
    $goodWorkflow = @"
## 1. Task Brief
taskId: sample
projectId: sample-project
acceptanceCriteria: present
validationPlan: present

AGENTS.md and ProjectIndex.md were loaded from the project entry.

## 2. Execution Plan
Use the stable tool surface.

## 3. File Change Summary
Implementation changed one file.

## 4. Verification Report
invoke-java-main.ps1 returned JAVA_MAIN_PASS.

## 5. User Acceptance
User accepted the result.
acceptedBy = user

## 6. Governance Candidates
candidate-first closeout recorded.
"@

    $goodReport = @"
## Candidate Table
| candidateId | type | disposition |
| c1 | Governance | absorbed |

## Approval And Disposition
Human approval recorded.

## Non-Promotion Statement
Report is not a fact source.

## Validation
git diff --check pass.
"@

    Test-LifecycleTextCoverage -CombinedText $goodWorkflow -Findings $findings -RequireUserAcceptanceValue $true
    Test-ProjectReportTextCoverage -ReportText $goodReport -Path "self-test-report" -Findings $findings

    $badFindings = New-Object System.Collections.ArrayList
    Test-LifecycleTextCoverage -CombinedText "## 1. Task Brief`nAGENTS.md ProjectIndex.md`n## 2. Execution Plan" -Findings $badFindings -RequireUserAcceptanceValue $true
    $badCodes = @($badFindings | ForEach-Object { $_.code })
    $expectedBadCodes = @("lifecycleDevelopmentMissing", "lifecycleValidationMissing", "lifecycleGovernanceMissing", "lifecycleAcceptanceMissing")
    foreach ($code in $expectedBadCodes) {
        if ($badCodes -notcontains $code) {
            Add-Finding -List $findings -Severity "error" -Code "selfTestExpectedCodeMissing" -Path "self-test" -Message "Self-test did not detect expected code: $code." -RepairSuggestion "Repair lifecycle text coverage checks."
        }
    }

    # Unicode escapes keep this script safe on Windows PowerShell without a BOM.
    $localized = [regex]::Unescape(@'
## 1. \u4efb\u52a1\u7b80\u62a5
goal, scope and acceptance criteria recorded
AGENTS.md ProjectIndex.md
## 2. \u6267\u884c\u8ba1\u5212
read the source before editing
## 3. \u6587\u4ef6\u53d8\u66f4\u6458\u8981
changed one file
## 4. \u9a8c\u8bc1\u62a5\u544a
commands and results recorded
## 5. \u7528\u6237\u9a8c\u6536
acceptedBy = user
## 6. \u6cbb\u7406\u5019\u9009
no automatic promotion
\u7a33\u5b9a\u5de5\u5177
'@)
    $localizedReport = [regex]::Unescape(@'
## \u5019\u9009\u6e05\u5355
types, targets and validation recorded
## \u5ba1\u6838\u4e0e\u5904\u7f6e
pending new assets
## \u975e\u664b\u5347\u8fb9\u754c
no automatic fact promotion
## \u9a8c\u8bc1\u7ed3\u679c
commands passed
'@)
    Test-LifecycleTextCoverage -CombinedText $localized -Findings $findings -RequireUserAcceptanceValue $true
    Test-ProjectReportTextCoverage -ReportText $localizedReport -Path "self-test-localized-report" -Findings $findings
    foreach ($case in @(
        @{ text = $localized.Replace("acceptedBy = user", "finalUserReview: pending"); code = "lifecycleAcceptanceMissing" },
        @{ text = $goodWorkflow.Replace("acceptedBy = user", "finalUserReview: rejected"); code = "lifecycleAcceptanceMissing" },
        @{ text = $goodWorkflow.Replace("acceptedBy = user", ""); code = "lifecycleAcceptanceMissing" },
        @{ text = [regex]::Replace($localized, '(?m)^## 4\..*\r?\n', ''); code = "lifecycleValidationMissing" }
    )) {
        $actual = New-Object System.Collections.ArrayList
        Test-LifecycleTextCoverage -CombinedText $case.text -Findings $actual -RequireUserAcceptanceValue $true
        if (@($actual | ForEach-Object { $_.code }) -notcontains $case.code) {
            Add-Finding -List $findings -Severity "error" -Code "selfTestLocalizedRejectionMissing" -Path "self-test" -Message "Missing rejection: $($case.code)." -RepairSuggestion "Repair bilingual coverage without accepting pending reviews."
        }
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
$findings = New-Object System.Collections.ArrayList
$registryPath = Join-Path $rootPath ($Registry -replace '/', '\')

if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
    Add-Finding -List $findings -Severity "error" -Code "registryMissing" -Path $Registry -Message "Project registry file does not exist." -RepairSuggestion "Create user/registry/projects.local.json or pass the correct -Registry path."
} else {
    $registryObject = Get-Content -Raw -Encoding UTF8 -LiteralPath $registryPath | ConvertFrom-Json
    $projects = @($registryObject.projects)
    if ([string]::IsNullOrWhiteSpace($ProjectId)) {
        if ($projects.Count -eq 1) {
            $ProjectId = [string]$projects[0].projectId
        } else {
            Add-Finding -List $findings -Severity "error" -Code "projectIdRequired" -Path $Registry -Message "ProjectId is required when registry contains zero or multiple projects." -RepairSuggestion "Pass -ProjectId explicitly."
        }
    }

    $project = @($projects | Where-Object { $_.projectId -eq $ProjectId }) | Select-Object -First 1
    if ($null -eq $project) {
        Add-Finding -List $findings -Severity "error" -Code "projectNotRegistered" -Path $Registry -Message "Project is not registered: $ProjectId." -RepairSuggestion "Add the project to the local registry or pass the correct ProjectId."
    } elseif (-not (Test-RelativePath -Value $project.root)) {
        Add-Finding -List $findings -Severity "error" -Code "projectRootNotRelative" -Path $Registry -Message "Project registry root must be relative." -RepairSuggestion "Use projects/<project-id> as a relative project root."
    } else {
        $projectRoot = Join-And-Resolve -Base $rootPath -Relative ([string]$project.root)
        $projectRootRelative = Convert-ToRelativePath -RootPath $rootPath -Path $projectRoot

        if (-not (Test-IsInsidePath -Path $projectRoot -Parent (Join-Path $rootPath "projects"))) {
            Add-Finding -List $findings -Severity "error" -Code "projectRootOutOfBounds" -Path $projectRootRelative -Message "Project root is outside projects/." -RepairSuggestion "Keep managed projects under projects/<project-id>."
        }

        foreach ($requiredProjectPath in @("AGENTS.md", "docs/project/ProjectIndex.md", "docs/project/workflow", "docs/project/reports/README.md")) {
            $requiredFullPath = Join-Path $projectRoot ($requiredProjectPath -replace '/', '\')
            if (-not (Test-Path -LiteralPath $requiredFullPath)) {
                Add-Finding -List $findings -Severity "error" -Code "projectLifecycleRouteMissing" -Path "$projectRootRelative/$requiredProjectPath" -Message "Required project lifecycle route is missing." -RepairSuggestion "Instantiate or repair the project template route before validating lifecycle evidence."
            }
        }

        if ($WorkflowEvidence.Count -eq 0) {
            Add-Finding -List $findings -Severity "error" -Code "workflowEvidenceArgumentMissing" -Path $projectRootRelative -Message "No workflow evidence paths were provided." -RepairSuggestion "Pass one or more -WorkflowEvidence paths for the real task being validated."
        }

        $combinedWorkflowText = ""
        foreach ($item in $WorkflowEvidence) {
            $resolved = Resolve-ProjectFileInput -RootPath $rootPath -ProjectRoot $projectRoot -InputPath $item
            $relative = Convert-ToRelativePath -RootPath $rootPath -Path $resolved
            if (-not (Test-IsInsidePath -Path $resolved -Parent $projectRoot)) {
                Add-Finding -List $findings -Severity "error" -Code "workflowEvidenceOutOfProject" -Path $item -Message "Workflow evidence must stay under the project instance." -RepairSuggestion "Move project task evidence to projects/<project-id>/docs/project/workflow/."
                continue
            }
            if ($relative -notmatch '^projects/[^/]+/docs/project/workflow/') {
                Add-Finding -List $findings -Severity "error" -Code "workflowEvidenceWrongLocation" -Path $relative -Message "Workflow evidence is not under docs/project/workflow/." -RepairSuggestion "Store project task lifecycle evidence under docs/project/workflow/."
                continue
            }
            if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
                Add-Finding -List $findings -Severity "error" -Code "workflowEvidenceMissing" -Path $relative -Message "Workflow evidence file does not exist." -RepairSuggestion "Create the workflow evidence file or pass the correct path."
                continue
            }
            $text = Get-Content -Raw -Encoding UTF8 -LiteralPath $resolved
            Test-MarkdownFrontMatter -Text $text -Path $relative -Findings $findings
            $combinedWorkflowText += "`n" + $text
        }

        if (-not [string]::IsNullOrWhiteSpace($combinedWorkflowText)) {
            Test-LifecycleTextCoverage -CombinedText $combinedWorkflowText -Findings $findings -RequireUserAcceptanceValue ([bool]$RequireUserAcceptance)
        }

        if ($RequireReport -and $ProjectReport.Count -eq 0) {
            Add-Finding -List $findings -Severity "error" -Code "projectReportArgumentMissing" -Path $projectRootRelative -Message "Project report is required but no report path was provided." -RepairSuggestion "Pass one or more -ProjectReport paths under docs/project/reports/."
        }

        foreach ($item in $ProjectReport) {
            $resolved = Resolve-ProjectFileInput -RootPath $rootPath -ProjectRoot $projectRoot -InputPath $item
            $relative = Convert-ToRelativePath -RootPath $rootPath -Path $resolved
            if (-not (Test-IsInsidePath -Path $resolved -Parent $projectRoot)) {
                Add-Finding -List $findings -Severity "error" -Code "projectReportOutOfProject" -Path $item -Message "Project report must stay under the project instance." -RepairSuggestion "Move concrete project reports to projects/<project-id>/docs/project/reports/."
                continue
            }
            if ($relative -notmatch '^projects/[^/]+/docs/project/reports/') {
                Add-Finding -List $findings -Severity "error" -Code "projectReportWrongLocation" -Path $relative -Message "Project report is not under docs/project/reports/." -RepairSuggestion "Store concrete project reports under projects/<project-id>/docs/project/reports/."
                continue
            }
            if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
                Add-Finding -List $findings -Severity "error" -Code "projectReportMissing" -Path $relative -Message "Project report file does not exist." -RepairSuggestion "Create the project report or pass the correct path."
                continue
            }
            $text = Get-Content -Raw -Encoding UTF8 -LiteralPath $resolved
            Test-MarkdownFrontMatter -Text $text -Path $relative -Findings $findings
            Test-ProjectReportTextCoverage -ReportText $text -Path $relative -Findings $findings
        }
    }
}

$severityCounts = [ordered]@{
    error = @($findings | Where-Object { $_.severity -eq "error" }).Count
    warning = @($findings | Where-Object { $_.severity -eq "warning" }).Count
    info = @($findings | Where-Object { $_.severity -eq "info" }).Count
}

$status = "passed"
if ($severityCounts.error -gt 0) {
    $status = "failed"
}

$output = [pscustomobject]@{
    status = $status
    mode = "project-lifecycle-evidence"
    root = $rootPath
    checkedAt = (Get-Date).ToString("s")
    projectId = $ProjectId
    summary = [pscustomobject]@{
        workflowEvidenceCount = $WorkflowEvidence.Count
        projectReportCount = $ProjectReport.Count
        findingCount = $findings.Count
        severityCounts = $severityCounts
    }
    checks = @(
        "project-route",
        "workflow-evidence-location",
        "workflow-frontmatter",
        "task-brief",
        "entry-routing",
        "design-or-plan",
        "development-evidence",
        "validation-evidence",
        "user-acceptance",
        "governance-candidates",
        "project-report-location",
        "project-report-review-boundary"
    )
    findings = @($findings)
}

$output | ConvertTo-Json -Depth 8
if ($status -eq "passed") { exit 0 } else { exit 1 }
