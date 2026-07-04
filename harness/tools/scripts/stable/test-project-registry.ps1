param(
    [string]$Root = ".",
    [string]$Registry = "user/registry/projects.local.json",
    [switch]$SelfTest
)

$ErrorActionPreference = "Stop"

function New-ErrorItem {
    param(
        [string]$Code,
        [string]$Message,
        [string]$ProjectId = ""
    )

    [pscustomobject]@{
        code = $Code
        projectId = $ProjectId
        message = $Message
    }
}

function Test-RelativePath {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }
    if ([System.IO.Path]::IsPathRooted($Value)) {
        return $false
    }
    if ($Value -match '(^|[\\/])\.\.([\\/]|$)') {
        return $false
    }
    if ($Value -match '^[A-Za-z]:') {
        return $false
    }
    return $true
}

function Join-And-Resolve {
    param(
        [string]$Base,
        [string]$Relative
    )

    $combined = Join-Path $Base $Relative
    if (Test-Path -LiteralPath $combined) {
        return (Resolve-Path -LiteralPath $combined).Path
    }
    return [System.IO.Path]::GetFullPath($combined)
}

function Test-ProjectRegistryObject {
    param(
        [object]$RegistryObject,
        [string]$HarnessRoot
    )

    $errors = @()
    $projectsOut = @()

    $rootPath = (Resolve-Path -LiteralPath $HarnessRoot).Path
    $projectsRoot = Join-Path $rootPath "projects"
    $allowedTopKeys = @("schemaVersion", "registryKind", "projects")
    $allowedProjectKeys = @(
        "projectId",
        "root",
        "entry",
        "projectIndex",
        "defaultValidationProfile",
        "knowledgeScopes",
        "sensitiveBoundarySummary"
    )

    foreach ($property in $RegistryObject.PSObject.Properties.Name) {
        if ($allowedTopKeys -notcontains $property) {
            $errors += New-ErrorItem -Code "topLevelKeyNotAllowed" -Message "Top-level key '$property' is not allowed in the project registry."
        }
    }

    if ($RegistryObject.schemaVersion -ne "harness.projects.v1") {
        $errors += New-ErrorItem -Code "schemaVersionInvalid" -Message "schemaVersion must be harness.projects.v1."
    }

    $hasProjects = $RegistryObject.PSObject.Properties.Name -contains "projects"
    if (-not $hasProjects) {
        $errors += New-ErrorItem -Code "projectsMissing" -Message "projects array is required."
    }

    $projectEntries = if ($hasProjects -and $null -ne $RegistryObject.projects) { @($RegistryObject.projects) } else { @() }
    $seen = @{}

    foreach ($project in $projectEntries) {
        $projectId = [string]$project.projectId

        foreach ($property in $project.PSObject.Properties.Name) {
            if ($allowedProjectKeys -notcontains $property) {
                $errors += New-ErrorItem -Code "projectKeyNotAllowed" -ProjectId $projectId -Message "Project key '$property' is not allowed in registry entries."
            }
        }

        if ($projectId -notmatch '^[a-z0-9][a-z0-9-]*[a-z0-9]$') {
            $errors += New-ErrorItem -Code "projectIdInvalid" -ProjectId $projectId -Message "projectId must use lower-case letters, digits and hyphens."
        }

        if ($seen.ContainsKey($projectId)) {
            $errors += New-ErrorItem -Code "duplicateProjectId" -ProjectId $projectId -Message "Duplicate projectId '$projectId'."
        } else {
            $seen[$projectId] = $true
        }

        if (-not (Test-RelativePath -Value $project.root)) {
            $errors += New-ErrorItem -Code "rootNotRelative" -ProjectId $projectId -Message "root must be a relative path under projects/<project-id>."
        }

        $rootResolved = Join-And-Resolve -Base $rootPath -Relative ([string]$project.root)
        $projectsRootFull = [System.IO.Path]::GetFullPath($projectsRoot)
        if (-not $rootResolved.StartsWith($projectsRootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            $errors += New-ErrorItem -Code "rootOutOfBounds" -ProjectId $projectId -Message "root must stay under the Harness projects directory."
        }

        if (-not (Test-Path -LiteralPath $rootResolved -PathType Container)) {
            $errors += New-ErrorItem -Code "missingProjectRoot" -ProjectId $projectId -Message "Project root does not exist."
        }

        foreach ($pathField in @("entry", "projectIndex")) {
            $value = [string]$project.$pathField
            if (-not (Test-RelativePath -Value $value)) {
                $errors += New-ErrorItem -Code "$($pathField)NotRelative" -ProjectId $projectId -Message "$pathField must be relative to the project root."
                continue
            }
            $resolved = Join-And-Resolve -Base $rootResolved -Relative $value
            if (-not $resolved.StartsWith($rootResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
                $errors += New-ErrorItem -Code "$($pathField)OutOfBounds" -ProjectId $projectId -Message "$pathField must stay inside the project root."
            }
            if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
                $errors += New-ErrorItem -Code "$($pathField)Missing" -ProjectId $projectId -Message "$pathField file does not exist."
            }
        }

        if ([string]::IsNullOrWhiteSpace($project.defaultValidationProfile)) {
            $errors += New-ErrorItem -Code "defaultValidationProfileMissing" -ProjectId $projectId -Message "defaultValidationProfile is required."
        }

        foreach ($value in @($project.knowledgeScopes)) {
            if ([string]::IsNullOrWhiteSpace($value)) {
                $errors += New-ErrorItem -Code "knowledgeScopeInvalid" -ProjectId $projectId -Message "knowledgeScopes values must be non-empty strings."
            }
        }

        foreach ($value in @($project.sensitiveBoundarySummary)) {
            $text = [string]$value
            if ($text -match '[\\/:*]' -or $text -match 'settings\.xml|password|token|secret') {
                $errors += New-ErrorItem -Code "sensitiveBoundarySummaryTooSpecific" -ProjectId $projectId -Message "sensitiveBoundarySummary must stay as a summary and must not contain paths, globs or secret-like terms."
            }
        }

        $projectsOut += [pscustomobject]@{
            projectId = $projectId
            root = $project.root
            entry = $project.entry
            projectIndex = $project.projectIndex
            defaultValidationProfile = $project.defaultValidationProfile
        }
    }

    $status = "passed"
    if ($errors.Count -gt 0) {
        $status = "failed"
    }

    [pscustomobject]@{
        status = $status
        projectCount = @($projectEntries).Count
        errorCount = @($errors).Count
        errors = @($errors)
        projects = @($projectsOut)
    }
}

function New-TestRegistry {
    param([object[]]$Projects)

    [pscustomobject]@{
        schemaVersion = "harness.projects.v1"
        registryKind = "self-test"
        projects = $Projects
    }
}

if ($SelfTest) {
    $validProject = [pscustomobject]@{
        projectId = "lfms-decision"
        root = "projects/lfms-decision"
        entry = "AGENTS.md"
        projectIndex = "docs/project/ProjectIndex.md"
        defaultValidationProfile = "real-local-maven"
        knowledgeScopes = @("project-reviewed:lfms-decision", "domain:java", "global")
        sensitiveBoundarySummary = @("credential-material-excluded", "private-settings-excluded", "auth-files-excluded")
    }

    $cases = @(
        [pscustomobject]@{
            name = "missing-project"
            registry = (New-TestRegistry -Projects @([pscustomobject]@{
                projectId = "missing-demo"
                root = "projects/missing-demo"
                entry = "AGENTS.md"
                projectIndex = "docs/project/ProjectIndex.md"
                defaultValidationProfile = "example"
                knowledgeScopes = @("project-reviewed:missing-demo", "global")
                sensitiveBoundarySummary = @("credential-material-excluded")
            }))
            expectedCode = "missingProjectRoot"
        },
        [pscustomobject]@{
            name = "duplicate-project-id"
            registry = (New-TestRegistry -Projects @($validProject, $validProject))
            expectedCode = "duplicateProjectId"
        },
        [pscustomobject]@{
            name = "out-of-bounds-root"
            registry = (New-TestRegistry -Projects @([pscustomobject]@{
                projectId = "bad-root"
                root = "../outside"
                entry = "AGENTS.md"
                projectIndex = "docs/project/ProjectIndex.md"
                defaultValidationProfile = "example"
                knowledgeScopes = @("global")
                sensitiveBoundarySummary = @("credential-material-excluded")
            }))
            expectedCode = "rootOutOfBounds"
        }
    )

    $caseResults = foreach ($case in $cases) {
        $result = Test-ProjectRegistryObject -RegistryObject $case.registry -HarnessRoot $Root
        $codes = @($result.errors | ForEach-Object { $_.code })
        [pscustomobject]@{
            name = $case.name
            expectedCode = $case.expectedCode
            detected = ($codes -contains $case.expectedCode)
            codes = $codes
        }
    }

    $failedCases = @($caseResults | Where-Object { -not $_.detected })
    $status = "passed"
    if ($failedCases.Count -gt 0) {
        $status = "failed"
    }

    $output = [pscustomobject]@{
        status = $status
        mode = "self-test"
        caseCount = $caseResults.Count
        failedCaseCount = $failedCases.Count
        cases = @($caseResults)
    }

    $output | ConvertTo-Json -Depth 8
    if ($status -eq "passed") { exit 0 } else { exit 1 }
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$registryPath = Join-Path $rootPath $Registry
if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
    $output = [pscustomobject]@{
        status = "failed"
        registryPath = $registryPath
        projectCount = 0
        errorCount = 1
        errors = @((New-ErrorItem -Code "registryMissing" -Message "Registry file does not exist."))
        projects = @()
    }
    $output | ConvertTo-Json -Depth 8
    exit 1
}

$registryObject = Get-Content -Raw -LiteralPath $registryPath | ConvertFrom-Json
$result = Test-ProjectRegistryObject -RegistryObject $registryObject -HarnessRoot $rootPath
$result | Add-Member -NotePropertyName registryPath -NotePropertyValue $registryPath
$result | ConvertTo-Json -Depth 8
if ($result.status -eq "passed") { exit 0 } else { exit 1 }
