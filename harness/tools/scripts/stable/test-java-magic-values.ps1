[CmdletBinding()]
param(
    [string]$Root,

    [string]$Target,

    [string[]]$AllowLiteral = @("0", "1"),
    [string[]]$IgnorePath = @(),
    [string]$ClassificationFile,
    [switch]$FailOnFindings,
    [switch]$FailOnUnclassified,
    [switch]$SelfTest
)

$ErrorActionPreference = "Stop"

function Convert-ToRelativePath {
    param(
        [string]$RootPath,
        [string]$Path
    )

    $full = [System.IO.Path]::GetFullPath($Path)
    $rootFull = [System.IO.Path]::GetFullPath($RootPath).TrimEnd('\', '/')
    if (-not $full.StartsWith($rootFull + [System.IO.Path]::DirectorySeparatorChar,
            [System.StringComparison]::OrdinalIgnoreCase) -and
        -not $full.Equals($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Target must remain inside Root: $Path"
    }
    return $full.Substring($rootFull.Length).TrimStart('\', '/') -replace '\\', '/'
}

function Resolve-TargetFiles {
    param(
        [string]$RootPath,
        [string]$TargetPath
    )

    $resolved = if ([System.IO.Path]::IsPathRooted($TargetPath)) {
        [System.IO.Path]::GetFullPath($TargetPath)
    } else {
        [System.IO.Path]::GetFullPath((Join-Path $RootPath ($TargetPath -replace '/', '\')))
    }
    [void](Convert-ToRelativePath -RootPath $RootPath -Path $resolved)
    if (-not (Test-Path -LiteralPath $resolved)) {
        throw "Target not found: $TargetPath"
    }
    $item = Get-Item -LiteralPath $resolved
    if ($item.PSIsContainer) {
        return @(Get-ChildItem -LiteralPath $item.FullName -Recurse -File -Filter *.java |
            Sort-Object FullName | ForEach-Object { $_.FullName })
    }
    if ($item.Extension -ne ".java") {
        throw "Target must be a Java file or a directory containing Java files: $TargetPath"
    }
    return @($item.FullName)
}

function Remove-JavaNonCode {
    param([string[]]$Lines)

    $result = New-Object System.Collections.Generic.List[string]
    $inBlockComment = $false
    foreach ($line in $Lines) {
        $builder = New-Object System.Text.StringBuilder
        $inString = $false
        $inChar = $false
        $escaped = $false
        for ($index = 0; $index -lt $line.Length; $index++) {
            $current = $line[$index]
            $next = if ($index + 1 -lt $line.Length) { $line[$index + 1] } else { [char]0 }

            if ($inBlockComment) {
                if ($current -eq '*' -and $next -eq '/') {
                    $inBlockComment = $false
                    $index++
                }
                [void]$builder.Append(' ')
                continue
            }
            if (-not $inString -and -not $inChar -and $current -eq '/' -and $next -eq '/') {
                break
            }
            if (-not $inString -and -not $inChar -and $current -eq '/' -and $next -eq '*') {
                $inBlockComment = $true
                $index++
                [void]$builder.Append(' ')
                continue
            }
            if ($inString -or $inChar) {
                [void]$builder.Append(' ')
                if ($escaped) {
                    $escaped = $false
                } elseif ($current -eq '\') {
                    $escaped = $true
                } elseif ($inString -and $current -eq '"') {
                    $inString = $false
                } elseif ($inChar -and $current -eq "'") {
                    $inChar = $false
                }
                continue
            }
            if ($current -eq '"') {
                $inString = $true
                [void]$builder.Append(' ')
                continue
            }
            if ($current -eq "'") {
                $inChar = $true
                [void]$builder.Append(' ')
                continue
            }
            [void]$builder.Append($current)
        }
        $result.Add($builder.ToString())
    }
    return @($result.ToArray())
}

function Normalize-Literal {
    param([string]$Literal)

    $normalized = $Literal -replace '_', ''
    $normalized = $normalized -replace '[dDfFlL]$', ''
    if ($normalized -match '^[+-]?0+(?:\.0+)?(?:[eE][+-]?0+)?$') {
        return "0"
    }
    if ($normalized -match '^\+?1(?:\.0+)?(?:[eE]\+?0+)?$') {
        return "1"
    }
    return $normalized
}

function Test-IgnoredPath {
    param(
        [string]$RelativePath,
        [string[]]$Patterns
    )

    foreach ($pattern in $Patterns) {
        if (-not [string]::IsNullOrWhiteSpace($pattern) -and $RelativePath -like $pattern) {
            return $true
        }
    }
    return $false
}

function Find-MagicValueCandidates {
    param(
        [string]$FilePath,
        [string]$RootPath,
        [string[]]$Allowed
    )

    $relative = Convert-ToRelativePath -RootPath $RootPath -Path $FilePath
    $sourceLines = @(Get-Content -LiteralPath $FilePath -Encoding UTF8)
    $codeLines = @(Remove-JavaNonCode -Lines $sourceLines)
    $allowedNormalized = @{}
    foreach ($literal in $Allowed) {
        $allowedNormalized[(Normalize-Literal -Literal $literal)] = $true
    }
    $findings = New-Object System.Collections.Generic.List[object]
    $inConstantDeclaration = $false
    $numberPattern = '(?<![A-Za-z0-9_$.])(?:0[xX][0-9A-Fa-f_]+|0[bB][01_]+|(?:\d[\d_]*\.?[\d_]*|\.\d[\d_]*)(?:[eE][+-]?\d[\d_]*)?)[dDfFlL]?(?![A-Za-z0-9_])'

    for ($lineIndex = 0; $lineIndex -lt $codeLines.Count; $lineIndex++) {
        $code = $codeLines[$lineIndex]
        if (-not $inConstantDeclaration -and
            $code -match '\b(?:static\s+final|final\s+static)\b') {
            $inConstantDeclaration = $true
        }
        if (-not $inConstantDeclaration -and $code.TrimStart().StartsWith('@')) {
            continue
        }
        if (-not $inConstantDeclaration) {
            foreach ($match in [regex]::Matches($code, $numberPattern)) {
                $normalized = Normalize-Literal -Literal $match.Value
                if ($allowedNormalized.ContainsKey($normalized)) {
                    continue
                }
                $lineText = $sourceLines[$lineIndex].Trim()
                if ($lineText.Length -gt 240) {
                    $lineText = $lineText.Substring(0, 240)
                }
                $findings.Add([pscustomobject]@{
                    severity = "warning"
                    code = "javaNumericLiteralCandidate"
                    path = $relative
                    line = $lineIndex + 1
                    literal = $match.Value
                    normalizedLiteral = $normalized
                    category = "unclassified"
                    lineText = $lineText
                    repairSuggestion = "Classify as configuration, versioned domain policy, unit/math constant, protocol constant, test fixture, or justified inline identity. Extract only when the classification requires it."
                })
            }
        }
        if ($inConstantDeclaration -and $code.Contains(';')) {
            $inConstantDeclaration = $false
        }
    }
    return @($findings.ToArray())
}

function Read-ClassificationRules {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return @()
    }
    $resolved = [System.IO.Path]::GetFullPath($Path)
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        throw "Classification file not found: $Path"
    }
    $document = Get-Content -Raw -LiteralPath $resolved -Encoding UTF8 | ConvertFrom-Json
    if ($document.schemaVersion -ne "java-magic-value-classification-v1") {
        throw "Unsupported classification schemaVersion: $($document.schemaVersion)"
    }
    return @($document.rules)
}

function Set-FindingClassification {
    param(
        [object]$Finding,
        [object[]]$Rules
    )

    foreach ($rule in $Rules) {
        if ([string]::IsNullOrWhiteSpace([string]$rule.id) -or
            [string]::IsNullOrWhiteSpace([string]$rule.pathRegex) -or
            [string]::IsNullOrWhiteSpace([string]$rule.category) -or
            [string]::IsNullOrWhiteSpace([string]$rule.reason)) {
            throw "Classification rules require id, pathRegex, category, and reason"
        }
        if ($Finding.path -notmatch [string]$rule.pathRegex) {
            continue
        }
        if ($rule.literalRegex -and
            $Finding.normalizedLiteral -notmatch [string]$rule.literalRegex) {
            continue
        }
        if ($rule.lineTextRegex -and $Finding.lineText -notmatch [string]$rule.lineTextRegex) {
            continue
        }
        $Finding.category = [string]$rule.category
        $Finding | Add-Member -NotePropertyName classificationRule -NotePropertyValue ([string]$rule.id)
        $Finding | Add-Member -NotePropertyName classificationReason -NotePropertyValue ([string]$rule.reason)
        $Finding.repairSuggestion = "Review the matched classification rule when the literal meaning changes."
        return
    }
}

if ($SelfTest) {
    $fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("java-magic-values-" + [guid]::NewGuid().ToString("N"))
    try {
        New-Item -ItemType Directory -Force -Path $fixtureRoot | Out-Null
        $fixture = Join-Path $fixtureRoot "Sample.java"
        $fixtureText = @"
public class Sample {
    private static final double NAMED_THRESHOLD = 12.5D;
    public double scale(double value) {
        if (value <= 0.0D) {
            return 0.0D;
        }
        return value * 2.5D;
    }
}
"@
        [System.IO.File]::WriteAllText($fixture, $fixtureText, [System.Text.UTF8Encoding]::new($false))
        $classificationFixture = Join-Path $fixtureRoot "classification.json"
        $classificationText = @"
{
  "schemaVersion": "java-magic-value-classification-v1",
  "rules": [
    {
      "id": "self-test-unit-rule",
      "pathRegex": "Sample[.]java$",
      "literalRegex": "^2[.]5$",
      "category": "unit-or-math",
      "reason": "Self-test numeric identity fixture."
    }
  ]
}
"@
        [System.IO.File]::WriteAllText(
            $classificationFixture,
            $classificationText,
            [System.Text.UTF8Encoding]::new($false)
        )
        $selfFindings = @(Find-MagicValueCandidates -FilePath $fixture -RootPath $fixtureRoot -Allowed @("0", "1"))
        $selfRules = @(Read-ClassificationRules -Path $classificationFixture)
        foreach ($finding in $selfFindings) {
            Set-FindingClassification -Finding $finding -Rules $selfRules
        }
        $passed = $selfFindings.Count -eq 1 -and
            $selfFindings[0].normalizedLiteral -eq "2.5" -and
            $selfFindings[0].category -eq "unit-or-math" -and
            $selfFindings[0].classificationRule -eq "self-test-unit-rule"
        [ordered]@{
            status = if ($passed) { "passed" } else { "failed" }
            mode = "java-magic-values-self-test"
            checkedAt = (Get-Date).ToString("s")
            summary = [ordered]@{
                expectedFindingCount = 1
                actualFindingCount = $selfFindings.Count
                expectedClassifiedCount = 1
                actualClassifiedCount = @($selfFindings | Where-Object { $_.category -ne "unclassified" }).Count
            }
            findings = $selfFindings
        } | ConvertTo-Json -Depth 8
        if (-not $passed) { exit 1 }
        exit 0
    } finally {
        if (Test-Path -LiteralPath $fixtureRoot) {
            Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
        }
    }
}

if ([string]::IsNullOrWhiteSpace($Root)) {
    throw "input/root: Root is required unless SelfTest is used."
}
if ([string]::IsNullOrWhiteSpace($Target)) {
    throw "input/target: Target is required unless SelfTest is used."
}

$rootFull = [System.IO.Path]::GetFullPath($Root)
$files = @(Resolve-TargetFiles -RootPath $rootFull -TargetPath $Target)
$classificationRules = @(Read-ClassificationRules -Path $ClassificationFile)
$allFindings = New-Object System.Collections.Generic.List[object]
$scannedFiles = New-Object System.Collections.Generic.List[string]

foreach ($file in $files) {
    $relative = Convert-ToRelativePath -RootPath $rootFull -Path $file
    if (Test-IgnoredPath -RelativePath $relative -Patterns $IgnorePath) {
        continue
    }
    $scannedFiles.Add($relative)
    foreach ($finding in (Find-MagicValueCandidates -FilePath $file -RootPath $rootFull -Allowed $AllowLiteral)) {
        Set-FindingClassification -Finding $finding -Rules $classificationRules
        $allFindings.Add($finding)
    }
}

$unclassifiedFindings = @($allFindings | Where-Object { $_.category -eq "unclassified" })
$failed = ($FailOnFindings -and $allFindings.Count -gt 0) -or
    ($FailOnUnclassified -and $unclassifiedFindings.Count -gt 0)
$payload = [ordered]@{
    status = if ($failed) { "failed" } else { "passed" }
    mode = if ($FailOnFindings) { "strict" } elseif ($FailOnUnclassified) {
        "classification-gate"
    } else { "report-only" }
    root = $rootFull
    target = $Target
    checkedAt = (Get-Date).ToString("s")
    summary = [ordered]@{
        fileCount = $scannedFiles.Count
        findingCount = $allFindings.Count
        classifiedCount = $allFindings.Count - $unclassifiedFindings.Count
        unclassifiedCount = $unclassifiedFindings.Count
        allowLiteral = @($AllowLiteral)
        ignoredPathCount = $files.Count - $scannedFiles.Count
        classificationRuleCount = $classificationRules.Count
    }
    findings = @($allFindings.ToArray())
}
$payload | ConvertTo-Json -Depth 8
if ($failed) { exit 1 }
exit 0
