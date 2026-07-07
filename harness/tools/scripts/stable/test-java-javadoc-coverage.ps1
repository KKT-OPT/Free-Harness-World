param(
    [Parameter(Mandatory = $true)]
    [string]$Root,

    [Parameter(Mandatory = $true)]
    [string]$Target,

    [string]$ExpectedAuthor = "",
    [string]$ExpectedVersion = "",
    [string[]]$RequiredClassSection = @(),
    [int]$MinClassJavadocLines = 0,

    [switch]$RequireClassAuthor,
    [switch]$RequireClassSince,
    [switch]$RequireClassVersion,
    [switch]$RequirePublicMethodJavadocs,
    [switch]$RequireAllMethodJavadocs,
    [switch]$RequireParamTags,
    [switch]$RequireReturnTags,
    [switch]$ForbidBlankJavadocLines,
    [switch]$SelfTest
)

$ErrorActionPreference = "Stop"

function New-Finding {
    param(
        [string]$Severity,
        [string]$Code,
        [string]$Path,
        [int]$Line,
        [string]$Message,
        [string]$RepairSuggestion
    )

    [pscustomobject]@{
        severity = $Severity
        code = $Code
        path = $Path
        line = $Line
        message = $Message
        repairSuggestion = $RepairSuggestion
    }
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

function Resolve-TargetFiles {
    param(
        [string]$RootPath,
        [string]$TargetPath
    )

    $resolved = if ([System.IO.Path]::IsPathRooted($TargetPath)) {
        $TargetPath
    } else {
        Join-Path $RootPath ($TargetPath -replace '/', '\')
    }

    if (-not (Test-Path -LiteralPath $resolved)) {
        throw "Target not found: $TargetPath"
    }

    $item = Get-Item -LiteralPath $resolved
    if ($item.PSIsContainer) {
        return @(Get-ChildItem -LiteralPath $item.FullName -Recurse -Filter *.java | Sort-Object FullName | ForEach-Object { $_.FullName })
    }
    return @($item.FullName)
}

function Get-TopLevelType {
    param([string[]]$Lines)

    for ($i = 0; $i -lt $Lines.Count; $i++) {
        $line = $Lines[$i]
        $match = [regex]::Match($line, '^\s*public\s+(?:abstract\s+|final\s+)?(?:class|enum|interface|record)\s+([A-Za-z_][A-Za-z0-9_]*)\b')
        if ($match.Success) {
            return [pscustomobject]@{
                name = $match.Groups[1].Value
                lineIndex = $i
            }
        }
    }
    return $null
}

function Get-PreviousJavadoc {
    param(
        [string[]]$Lines,
        [int]$LineIndex
    )

    $i = $LineIndex - 1
    while ($i -ge 0) {
        $trimmed = $Lines[$i].Trim()
        if ($trimmed -eq "" -or $trimmed.StartsWith("@")) {
            $i--
            continue
        }
        break
    }

    if ($i -lt 0 -or -not $Lines[$i].Trim().EndsWith("*/")) {
        return $null
    }

    $end = $i
    while ($i -ge 0 -and -not $Lines[$i].Trim().StartsWith("/**")) {
        $i--
    }
    if ($i -lt 0) {
        return $null
    }

    return [pscustomobject]@{
        start = $i
        end = $end
        text = ($Lines[$i..$end] -join "`n")
    }
}

function Get-SignatureText {
    param(
        [string[]]$Lines,
        [int]$StartIndex
    )

    $parts = New-Object System.Collections.Generic.List[string]
    for ($i = $StartIndex; $i -lt $Lines.Count; $i++) {
        $parts.Add($Lines[$i].Trim())
        $joined = ($parts -join ' ')
        if ($joined -match '\)\s*(?:throws\s+[^{]+)?\s*(\{|;)$') {
            return [pscustomobject]@{
                text = $joined
                endIndex = $i
            }
        }
    }
    return [pscustomobject]@{
        text = ($parts -join ' ')
        endIndex = $StartIndex
    }
}

function Get-ParamNames {
    param([string]$ParamText)

    $result = New-Object System.Collections.Generic.List[string]
    if ([string]::IsNullOrWhiteSpace($ParamText)) {
        return @()
    }

    $params = $ParamText -split ','
    foreach ($param in $params) {
        $clean = ($param -replace '@[A-Za-z0-9_.]+(?:\([^)]*\))?\s*', '')
        $clean = ($clean -replace '\bfinal\s+', '').Trim()
        if ([string]::IsNullOrWhiteSpace($clean)) {
            continue
        }
        $tokens = $clean -split '\s+'
        if ($tokens.Count -eq 0) {
            continue
        }
        $name = $tokens[$tokens.Count - 1]
        $name = $name -replace '\[\]$', ''
        $name = $name -replace '\.\.\.$', ''
        if ($name -match '^[A-Za-z_][A-Za-z0-9_]*$') {
            $result.Add($name)
        }
    }
    return @($result)
}

function Test-MethodSignature {
    param(
        [string]$Signature,
        [string]$TypeName
    )

    $trimmed = $Signature.Trim()
    if ($trimmed -match '^\s*(if|for|while|switch|catch|return|new)\b') {
        return $null
    }
    if ($trimmed -match '\b(class|enum|interface|record)\b') {
        return $null
    }
    if ($trimmed -notmatch '^(public|protected|private)\s+') {
        return $null
    }

    $match = [regex]::Match($trimmed, '^(public|protected|private)\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:<[^>]+>\s+)?(.+?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*(?:throws\s+[^{;]+)?\s*(?:\{|;)$')
    if (-not $match.Success) {
        return $null
    }

    $returnType = $match.Groups[2].Value.Trim()
    $name = $match.Groups[3].Value.Trim()
    $params = $match.Groups[4].Value.Trim()
    $isConstructor = $name -eq $TypeName

    if ($isConstructor) {
        $returnType = ""
    }

    return [pscustomobject]@{
        name = $name
        returnType = $returnType
        params = Get-ParamNames -ParamText $params
        isConstructor = $isConstructor
    }
}

function Test-File {
    param(
        [string]$FilePath,
        [string]$RootPath
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $lines = @(Get-Content -Encoding UTF8 -LiteralPath $FilePath)
    $relative = Convert-ToRelativePath -RootPath $RootPath -Path $FilePath
    $type = Get-TopLevelType -Lines $lines
    $typeName = if ($null -eq $type) { "" } else { $type.name }

    if ($ForbidBlankJavadocLines) {
        $insideJavadoc = $false
        for ($lineIndex = 0; $lineIndex -lt $lines.Count; $lineIndex++) {
            $currentLine = $lines[$lineIndex]
            if ($currentLine.Trim().StartsWith("/**")) {
                $insideJavadoc = $true
            }
            if ($insideJavadoc -and $currentLine -match '^\s*\*\s*$') {
                $findings.Add((New-Finding -Severity "error" -Code "javadocBlankLine" -Path $relative -Line ($lineIndex + 1) -Message "Javadoc contains a blank star line that can trigger IDE/Javadoc warnings." -RepairSuggestion "Remove blank star-only lines and use continuous structured headings instead."))
            }
            if ($insideJavadoc -and $currentLine.Trim().EndsWith("*/")) {
                $insideJavadoc = $false
            }
        }
    }

    if ($null -eq $type) {
        return @($findings.ToArray())
    }

    $classJavadoc = Get-PreviousJavadoc -Lines $lines -LineIndex $type.lineIndex
    if ($null -eq $classJavadoc) {
        $findings.Add((New-Finding -Severity "error" -Code "classJavadocMissing" -Path $relative -Line ($type.lineIndex + 1) -Message "Top-level public type is missing Javadoc." -RepairSuggestion "Add class Javadoc before annotations and declaration."))
    } else {
        if ($RequireClassAuthor -and $classJavadoc.text -notmatch '@author\s+\S+') {
            $findings.Add((New-Finding -Severity "error" -Code "classAuthorMissing" -Path $relative -Line ($type.lineIndex + 1) -Message "Class Javadoc is missing @author." -RepairSuggestion "Add @author based on project convention or user-confirmed owner."))
        }
        if ($RequireClassSince -and $classJavadoc.text -notmatch '@since\s+\S+') {
            $findings.Add((New-Finding -Severity "error" -Code "classSinceMissing" -Path $relative -Line ($type.lineIndex + 1) -Message "Class Javadoc is missing @since." -RepairSuggestion "Add @since using user-confirmed or current contract date."))
        }
        if ($RequireClassVersion -and $classJavadoc.text -notmatch '@version\s+\S+') {
            $findings.Add((New-Finding -Severity "error" -Code "classVersionMissing" -Path $relative -Line ($type.lineIndex + 1) -Message "Class Javadoc is missing @version." -RepairSuggestion "Add @version from the project version source."))
        }
        if ($MinClassJavadocLines -gt 0) {
            $classLineCount = ($classJavadoc.text -split "`n").Count
            if ($classLineCount -lt $MinClassJavadocLines) {
                $findings.Add((New-Finding -Severity "error" -Code "classJavadocTooShort" -Path $relative -Line ($type.lineIndex + 1) -Message "Class Javadoc has $classLineCount lines, below required minimum $MinClassJavadocLines." -RepairSuggestion "Add enough class-level context to explain purpose, position, boundary and impact."))
            }
        }
        foreach ($requiredSection in $RequiredClassSection) {
            if ([string]::IsNullOrWhiteSpace($requiredSection)) {
                continue
            }
            if (-not $classJavadoc.text.Contains($requiredSection)) {
                $findings.Add((New-Finding -Severity "error" -Code "classJavadocSectionMissing" -Path $relative -Line ($type.lineIndex + 1) -Message "Class Javadoc is missing required section: $requiredSection." -RepairSuggestion "Add the required class Javadoc section or adjust RequiredClassSection for this project."))
            }
        }
        if ($ExpectedAuthor -and $classJavadoc.text -notmatch ("@author\s+" + [regex]::Escape($ExpectedAuthor) + "\b")) {
            $findings.Add((New-Finding -Severity "error" -Code "classAuthorUnexpected" -Path $relative -Line ($type.lineIndex + 1) -Message "Class Javadoc @author does not match expected value: $ExpectedAuthor." -RepairSuggestion "Use the project-approved author value or rerun without ExpectedAuthor."))
        }
        if ($ExpectedVersion -and $classJavadoc.text -notmatch ("@version\s+" + [regex]::Escape($ExpectedVersion) + "\b")) {
            $findings.Add((New-Finding -Severity "error" -Code "classVersionUnexpected" -Path $relative -Line ($type.lineIndex + 1) -Message "Class Javadoc @version does not match expected value: $ExpectedVersion." -RepairSuggestion "Use the project-approved version value or rerun without ExpectedVersion."))
        }
    }

    if (-not $RequirePublicMethodJavadocs) {
        return @($findings.ToArray())
    }

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $methodVisibilityPattern = if ($RequireAllMethodJavadocs) { '^(public|protected|private)\s+' } else { '^(public|protected)\s+' }
        if ($line.Trim() -notmatch $methodVisibilityPattern -or $line -notmatch '\(') {
            continue
        }
        $openParenIndex = $line.IndexOf('(')
        $equalsIndex = $line.IndexOf('=')
        if ($equalsIndex -ge 0 -and $equalsIndex -lt $openParenIndex) {
            continue
        }
        $sig = Get-SignatureText -Lines $lines -StartIndex $i
        $method = Test-MethodSignature -Signature $sig.text -TypeName $typeName
        if ($null -eq $method) {
            continue
        }

        $javadoc = Get-PreviousJavadoc -Lines $lines -LineIndex $i
        if ($null -eq $javadoc) {
            $methodScope = if ($RequireAllMethodJavadocs) { "Method" } else { "Public/protected method" }
            $findings.Add((New-Finding -Severity "error" -Code "methodJavadocMissing" -Path $relative -Line ($i + 1) -Message "$methodScope '$($method.name)' is missing Javadoc." -RepairSuggestion "Add method Javadoc with function, params, return and failure semantics."))
            continue
        }

        if ($RequireParamTags) {
            foreach ($paramName in $method.params) {
                if ($javadoc.text -notmatch ("@param\s+" + [regex]::Escape($paramName) + "\b")) {
                    $findings.Add((New-Finding -Severity "error" -Code "methodParamTagMissing" -Path $relative -Line ($i + 1) -Message "Method '$($method.name)' is missing @param for '$paramName'." -RepairSuggestion "Add @param for every declared parameter."))
                }
            }
        }

        if ($RequireReturnTags -and -not $method.isConstructor -and $method.returnType -ne "void") {
            if ($javadoc.text -notmatch '@return\b') {
                $findings.Add((New-Finding -Severity "error" -Code "methodReturnTagMissing" -Path $relative -Line ($i + 1) -Message "Method '$($method.name)' is missing @return." -RepairSuggestion "Add @return for non-void public/protected methods."))
            }
        }
    }

    return @($findings.ToArray())
}

if ($SelfTest) {
    $payload = [ordered]@{
        status = "passed"
        mode = "java-javadoc-coverage-self-test"
        checkedAt = (Get-Date).ToString("s")
        findings = @()
    }
    $payload | ConvertTo-Json -Depth 8
    exit 0
}

$rootFull = [System.IO.Path]::GetFullPath($Root)
$files = Resolve-TargetFiles -RootPath $rootFull -TargetPath $Target
$allFindings = New-Object System.Collections.Generic.List[object]

foreach ($file in $files) {
    foreach ($finding in (Test-File -FilePath $file -RootPath $rootFull)) {
        $allFindings.Add($finding)
    }
}

$status = if ($allFindings.Count -eq 0) { "passed" } else { "failed" }
$payload = [ordered]@{
    status = $status
    mode = "java-javadoc-coverage"
    root = $rootFull
    target = $Target
    checkedAt = (Get-Date).ToString("s")
    summary = [ordered]@{
        fileCount = $files.Count
        findingCount = $allFindings.Count
    }
    findings = @($allFindings.ToArray())
}

$payload | ConvertTo-Json -Depth 8
if ($allFindings.Count -gt 0) {
    exit 1
}
exit 0
