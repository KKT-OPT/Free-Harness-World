[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $true)]
    [string]$MainClass,

    [ValidateSet('codex','hermes','shared')]
    [string]$Agent = 'codex',

    [string]$Module,

    [string[]]$MavenGoals = @('test-compile'),

    [string[]]$ReactorClasspathModules = @(),

    [string[]]$ClasspathRoots = @(),

    [string[]]$ProgramArgs = @(),

    [string[]]$JvmArgs = @('-Dfile.encoding=UTF-8'),

    [string]$PassMarker,

    [string]$JavaWorkingDirectory,

    [switch]$AlsoMake,

    [switch]$Offline,

    [switch]$SkipCompile,

    [string]$Profile = 'real-local-maven',

    [string]$Config,

    [string]$Settings,

    [string]$LocalRepo,

    [string]$Maven,

    [string]$Java,

    [string]$RunName = 'java-main',

    [string[]]$ExtraMavenArgs = @()
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

$SandboxRoot = Find-HarnessRoot
if ([string]::IsNullOrWhiteSpace($Config)) {
    $Config = Join-Path $SandboxRoot 'user\settings\maven\java-maven.local.json'
}
$LogDir = Join-Path $SandboxRoot 'var\logs'
$HomeDir = Join-Path $SandboxRoot "var\homes\$Agent"
$TmpDir = Join-Path $SandboxRoot 'var\tmp'
$WorkDir = Join-Path $TmpDir "java-main-$Agent"
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$SafeRunName = ($RunName -replace '[^A-Za-z0-9_.-]', '-')
$Log = Join-Path $LogDir "$SafeRunName-$Agent-$Stamp.log"
$Status = Join-Path $LogDir "last-$SafeRunName-$Agent.json"
$ClasspathFile = Join-Path $WorkDir "$SafeRunName-classpath.txt"
$JavaArgFile = Join-Path $WorkDir "$SafeRunName-java-args.txt"

New-Item -ItemType Directory -Force -Path $LogDir, $HomeDir, $TmpDir, $WorkDir | Out-Null

function Expand-AgentPath {
    param([string]$Value)
    if (-not $Value) {
        return $Value
    }
    return ($Value -replace '\{agent\}', $Agent)
}

function Resolve-JavaMavenProfile {
    $values = @{
        maven = Join-Path $SandboxRoot 'harness\tools\external\apache-maven-3.9.9\bin\mvn.cmd'
        java = Join-Path $SandboxRoot 'harness\tools\external\jdk\bin\java.exe'
        settings = Join-Path $SandboxRoot 'user\settings\maven\settings-sandbox.xml'
        localRepository = Join-Path $SandboxRoot "var\m2\$Agent\repository"
    }

    $javaFromPath = Get-Command java.exe -ErrorAction SilentlyContinue
    if ($javaFromPath -and $javaFromPath.Source) {
        $values.java = $javaFromPath.Source
    }

    if (Test-Path -LiteralPath $Config) {
        $configObj = Get-Content -Raw -LiteralPath $Config | ConvertFrom-Json
        $profileObj = $configObj.profiles.PSObject.Properties[$Profile].Value
        if (-not $profileObj) {
            $available = ($configObj.profiles.PSObject.Properties.Name -join ', ')
            throw "Java/Maven profile not found: $Profile. Available profiles: $available"
        }
        foreach ($key in @('maven','java','settings','localRepository')) {
            $prop = $profileObj.PSObject.Properties[$key]
            if ($prop -and $prop.Value) {
                $values[$key] = [string]$prop.Value
            }
        }
    }

    return $values
}

function Add-Log {
    param([string]$Message)
    Add-Content -LiteralPath $Log -Value $Message -Encoding UTF8
    Write-Host $Message
}

function Add-FileToLog {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    Get-Content -LiteralPath $Path | ForEach-Object {
        Add-Content -LiteralPath $Log -Value $_ -Encoding UTF8
        Write-Host $_
    }
}

function Assert-PathExists {
    param([string]$Path, [string]$Name)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Name not found: $Path"
    }
}

function Ensure-LocalRepo {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        return
    }

    if ($Path.StartsWith($SandboxRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
        return
    }

    throw "Maven local repository not found: $Path"
}

function Write-Status {
    param(
        [string]$State,
        [int]$ExitCode,
        [hashtable]$Details = @{}
    )

    $payload = [ordered]@{
        state = $State
        exitCode = $ExitCode
        agent = $Agent
        timestamp = (Get-Date).ToString('o')
        profile = $Profile
        config = $Config
        projectRoot = $ProjectRoot
        module = $Module
        mainClass = $MainClass
        offline = [bool]$Offline
        maven = $Maven
        java = $Java
        settings = $Settings
        localRepository = $LocalRepo
        sandboxHome = $HomeDir
        javaWorkingDirectory = $JavaWorkingDirectory
        classpathFile = $ClasspathFile
        javaArgFile = $JavaArgFile
        log = $Log
        details = $Details
    }
    $payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Status -Encoding UTF8
}

function Invoke-LoggedCommand {
    param(
        [string]$Label,
        [string]$Exe,
        [string[]]$CommandArgs,
        [string]$Cwd
    )

    Add-Log ''
    Add-Log ">>> $Label"
    Add-Log "CWD: $Cwd"
    Add-Log "EXE: $Exe"
    Add-Log "ARGS: $($CommandArgs -join ' ')"

    Push-Location $Cwd
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & $Exe @CommandArgs 2>&1 | ForEach-Object {
            $line = $_.ToString()
            Add-Content -LiteralPath $Log -Value $line -Encoding UTF8
            Write-Host $line
        }
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
        Pop-Location
    }

    Add-Log "EXIT: $exitCode"
    return $exitCode
}

function Add-ClasspathRootIfExists {
    param(
        [System.Collections.Generic.List[string]]$Roots,
        [string]$Path
    )
    if (Test-Path -LiteralPath $Path) {
        $Roots.Add($Path)
    }
}

function Resolve-JavaWorkingDirectory {
    param(
        [string]$Value,
        [string]$ProjectRootPath,
        [string]$ModuleRootPath
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $ModuleRootPath
    }

    $normalized = $Value.Trim()
    switch -Regex ($normalized.ToLowerInvariant()) {
        '^(module|module-root|\{module-root\})$' {
            return $ModuleRootPath
        }
        '^(project|project-root|\{project-root\})$' {
            return $ProjectRootPath
        }
        default {
            if ([System.IO.Path]::IsPathRooted($normalized)) {
                $candidate = $normalized
            }
            else {
                $candidate = Join-Path $ProjectRootPath $normalized
            }
            Assert-PathExists $candidate 'Java working directory'
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
}

try {
    $profileValues = Resolve-JavaMavenProfile
    if (-not $Maven) { $Maven = Expand-AgentPath $profileValues.maven }
    if (-not $Java) { $Java = Expand-AgentPath $profileValues.java }
    if (-not $Settings) { $Settings = Expand-AgentPath $profileValues.settings }
    if (-not $LocalRepo) { $LocalRepo = Expand-AgentPath $profileValues.localRepository }

    Assert-PathExists $ProjectRoot 'Project root'
    $ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
    Assert-PathExists (Join-Path $ProjectRoot 'pom.xml') 'Project pom.xml'
    if ($Module) {
        Assert-PathExists (Join-Path $ProjectRoot "$Module\pom.xml") 'Module pom.xml'
    }
    Assert-PathExists $Maven 'Maven executable'
    Assert-PathExists $Java 'Java executable'
    Assert-PathExists $Settings 'Maven settings file'
    Ensure-LocalRepo $LocalRepo

    $JavaBin = Split-Path -Parent $Java
    $JavaHome = Split-Path -Parent $JavaBin
    Assert-PathExists $JavaHome 'Java home'
    $env:JAVA_HOME = $JavaHome
    if (-not (($env:Path -split ';') -contains $JavaBin)) {
        $env:Path = "$JavaBin;$env:Path"
    }

    $env:MAVEN_OPTS = "-Duser.home=$HomeDir -Djava.io.tmpdir=$TmpDir"
    $env:MAVEN_SKIP_RC = 'true'

    Add-Log 'Generic Java main validation'
    Add-Log "Agent:       $Agent"
    Add-Log "Profile:     $Profile"
    Add-Log "Project:     $ProjectRoot"
    Add-Log "Module:      $Module"
    Add-Log "Main class:  $MainClass"
    Add-Log "Maven goals: $($MavenGoals -join ' ')"
    Add-Log "Java cwd:    $JavaWorkingDirectory"
    Add-Log "Offline:     $([bool]$Offline)"
    Add-Log "Maven:       $Maven"
    Add-Log "Java:        $Java"
    Add-Log "JAVA_HOME:   $env:JAVA_HOME"
    Add-Log "Settings:    $Settings"
    Add-Log "Local repo:  $LocalRepo"
    Add-Log "Sandbox home:$HomeDir"
    Add-Log "Log:         $Log"
    Add-Log "Status:      $Status"

    $mavenBase = @('-B', '-ntp', '-s', $Settings, "-Dmaven.repo.local=$LocalRepo")
    if ($Offline) {
        $mavenBase += '-o'
    }

    $selectorArgs = @()
    if ($Module) {
        $selectorArgs += @('-pl', $Module)
    }
    if ($AlsoMake) {
        $selectorArgs += '-am'
    }

    if (-not $SkipCompile) {
        $compileArgs = $mavenBase + $selectorArgs + $MavenGoals
        if ($ExtraMavenArgs) {
            $compileArgs += $ExtraMavenArgs
        }
        $compileExit = Invoke-LoggedCommand -Label 'maven-compile' -Exe $Maven -CommandArgs $compileArgs -Cwd $ProjectRoot
        if ($compileExit -ne 0) {
            throw "Maven compile command failed with exit code $compileExit"
        }
    }

    if (Test-Path -LiteralPath $ClasspathFile) {
        Remove-Item -LiteralPath $ClasspathFile -Force
    }
    $classpathArgs = $mavenBase + $selectorArgs + @('dependency:build-classpath', '-Dmdep.includeScope=test', "-Dmdep.outputFile=$ClasspathFile")
    $classpathExit = Invoke-LoggedCommand -Label 'maven-build-classpath' -Exe $Maven -CommandArgs $classpathArgs -Cwd $ProjectRoot
    if ($classpathExit -ne 0) {
        throw "Maven classpath command failed with exit code $classpathExit"
    }
    Assert-PathExists $ClasspathFile 'Generated classpath file'

    $classRootList = [System.Collections.Generic.List[string]]::new()
    $mainOutputBase = if ($Module) { Join-Path $ProjectRoot $Module } else { $ProjectRoot }
    $javaRunCwd = Resolve-JavaWorkingDirectory -Value $JavaWorkingDirectory -ProjectRootPath $ProjectRoot -ModuleRootPath $mainOutputBase
    Add-ClasspathRootIfExists -Roots $classRootList -Path (Join-Path $mainOutputBase 'target\test-classes')
    Add-ClasspathRootIfExists -Roots $classRootList -Path (Join-Path $mainOutputBase 'target\classes')

    foreach ($reactorModule in $ReactorClasspathModules) {
        $reactorBase = Join-Path $ProjectRoot $reactorModule
        Add-ClasspathRootIfExists -Roots $classRootList -Path (Join-Path $reactorBase 'target\test-classes')
        Add-ClasspathRootIfExists -Roots $classRootList -Path (Join-Path $reactorBase 'target\classes')
    }

    foreach ($root in $ClasspathRoots) {
        Add-ClasspathRootIfExists -Roots $classRootList -Path $root
    }

    $dependencyClasspath = (Get-Content -LiteralPath $ClasspathFile -Raw).Trim()
    $classpathParts = @($classRootList.ToArray())
    if ($dependencyClasspath) {
        $classpathParts += $dependencyClasspath
    }
    $fullClasspath = ($classpathParts -join [IO.Path]::PathSeparator)
    if (-not $fullClasspath) {
        throw 'Computed Java classpath is empty.'
    }

    $javaArgLines = @()
    $javaArgLines += $JvmArgs
    $javaArgLines += @('-cp', $fullClasspath, $MainClass)
    $javaArgLines += $ProgramArgs
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($JavaArgFile, $javaArgLines, $utf8NoBom)

    Add-Log "Java argfile: $JavaArgFile"
    Add-Log "Classpath file: $ClasspathFile"
    Add-Log "Classpath entry count: $($classpathParts.Count)"
    Add-Log "Resolved Java cwd: $javaRunCwd"
    $javaExit = Invoke-LoggedCommand -Label 'java-main' -Exe $Java -CommandArgs @("@$JavaArgFile") -Cwd $javaRunCwd
    if ($javaExit -ne 0) {
        throw "Java main command failed with exit code $javaExit"
    }

    $passMarkerFound = $null
    if ($PassMarker) {
        $logText = Get-Content -LiteralPath $Log -Raw
        $passMarkerFound = $logText.Contains($PassMarker)
        if (-not $passMarkerFound) {
            throw "Java main exited successfully but pass marker was not found: $PassMarker"
        }
    }

    Write-Status -State 'passed' -ExitCode 0 -Details @{
        passMarker = $PassMarker
        passMarkerFound = $passMarkerFound
        reactorClasspathModules = $ReactorClasspathModules
        extraClasspathRoots = $ClasspathRoots
        javaWorkingDirectory = $javaRunCwd
    }
    Add-Log ''
    Add-Log 'JAVA_MAIN_PASS'
    Add-Log "Status file: $Status"
    exit 0
}
catch {
    $message = $_.Exception.Message
    Add-Log ''
    Add-Log 'JAVA_MAIN_FAIL'
    Add-Log $message
    Write-Status -State 'failed' -ExitCode 1 -Details @{ error = $message }
    exit 1
}
