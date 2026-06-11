[CmdletBinding()]
param(
    [ValidateSet('config','compile','e2e-s8')]
    [string]$Mode = 'config',

    [ValidateSet('codex','hermes','shared')]
    [string]$Agent = 'codex',

    [string]$ProjectRoot = $env:HARNESS_REAL_JAVA_PROJECT_ROOT,
    [string]$Module = 'lfms-decision-algorithm',
    [string]$MainClass = 'MultiFusionV2.e2e.E2eScenarioS8Program',
    [string]$Maven = $env:HARNESS_MAVEN_CMD,
    [string]$Java = $env:HARNESS_JAVA_EXE,
    [string]$Settings = $env:HARNESS_MAVEN_SETTINGS,
    [string]$LocalRepo = $env:HARNESS_MAVEN_LOCAL_REPO,
    [switch]$Offline,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraMavenArgs
)

$ErrorActionPreference = 'Stop'

foreach ($required in @(
    @{ name = 'ProjectRoot'; value = $ProjectRoot; hint = 'HARNESS_REAL_JAVA_PROJECT_ROOT' },
    @{ name = 'Maven'; value = $Maven; hint = 'HARNESS_MAVEN_CMD' },
    @{ name = 'Java'; value = $Java; hint = 'HARNESS_JAVA_EXE' },
    @{ name = 'Settings'; value = $Settings; hint = 'HARNESS_MAVEN_SETTINGS' },
    @{ name = 'LocalRepo'; value = $LocalRepo; hint = 'HARNESS_MAVEN_LOCAL_REPO' }
)) {
    if ([string]::IsNullOrWhiteSpace($required.value)) {
        throw "$($required.name) is required. Pass the parameter or set $($required.hint)."
    }
}

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
$LogDir = Join-Path $SandboxRoot 'var\logs'
$WorkDir = Join-Path $SandboxRoot "var\evidence\legacy-real-java\$Agent"
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$ModeName = if ($Offline) { "$Mode-offline" } else { $Mode }
$Log = Join-Path $LogDir "real-java-$Agent-$ModeName-$Stamp.log"
$Status = Join-Path $LogDir "last-real-java-$Agent-$ModeName.json"
$CpFile = Join-Path $WorkDir 'e2e-s8-classpath.txt'
$JavaArgFile = Join-Path $WorkDir 'e2e-s8-java-args.txt'

New-Item -ItemType Directory -Force -Path $LogDir, $WorkDir | Out-Null

function Add-Log {
    param([string]$Message)
    $Message | Tee-Object -FilePath $Log -Append
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
        mode = $ModeName
        agent = $Agent
        timestamp = (Get-Date).ToString('o')
        projectRoot = $ProjectRoot
        module = $Module
        mainClass = $MainClass
        maven = $Maven
        java = $Java
        settings = $Settings
        localRepository = $LocalRepo
        log = $Log
        details = $Details
    }
    $payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Status -Encoding UTF8
}

function Assert-PathExists {
    param([string]$Path, [string]$Name)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Name not found: $Path"
    }
}

function Invoke-LoggedCommand {
    param(
        [string]$Label,
        [string]$Exe,
        [string[]]$CommandArgs,
        [string]$Cwd
    )

    Add-Log ""
    Add-Log ">>> $Label"
    Add-Log "CWD: $Cwd"
    Add-Log "EXE: $Exe"
    Add-Log "ARGS: $($CommandArgs -join ' ')"

    $commandId = [Guid]::NewGuid().ToString('N')
    $stdoutFile = Join-Path $WorkDir "native-$commandId.stdout.log"
    $stderrFile = Join-Path $WorkDir "native-$commandId.stderr.log"

    $proc = Start-Process -FilePath $Exe `
        -ArgumentList $CommandArgs `
        -WorkingDirectory $Cwd `
        -RedirectStandardOutput $stdoutFile `
        -RedirectStandardError $stderrFile `
        -NoNewWindow `
        -Wait `
        -PassThru
    $code = $proc.ExitCode

    if (Test-Path -LiteralPath $stdoutFile) {
        Get-Content -LiteralPath $stdoutFile | Tee-Object -FilePath $Log -Append
    }
    if (Test-Path -LiteralPath $stderrFile) {
        Get-Content -LiteralPath $stderrFile | Tee-Object -FilePath $Log -Append
    }
    Add-Log "EXIT: $code"
    if ($code -ne 0) {
        throw "$Label failed with exit code $code"
    }
}

try {
    Assert-PathExists $ProjectRoot 'Project root'
    Assert-PathExists (Join-Path $ProjectRoot 'pom.xml') 'Root pom.xml'
    Assert-PathExists (Join-Path $ProjectRoot "$Module\pom.xml") 'Module pom.xml'
    Assert-PathExists (Join-Path $ProjectRoot "$Module\src\test\java\MultiFusionV2\e2e\E2eScenarioS8Program.java") 'E2E S8 program'
    Assert-PathExists $Maven 'Maven executable'
    Assert-PathExists $Java 'Java executable'
    Assert-PathExists $Settings 'Maven settings file'
    Assert-PathExists $LocalRepo 'Maven local repository'

    $JavaBin = Split-Path -Parent $Java
    $JavaHome = Split-Path -Parent $JavaBin
    Assert-PathExists $JavaHome 'Java home'
    $env:JAVA_HOME = $JavaHome
    if (-not (($env:Path -split ';') -contains $JavaBin)) {
        $env:Path = "$JavaBin;$env:Path"
    }

    [xml]$settingsXml = Get-Content -LiteralPath $Settings
    $serverCount = @($settingsXml.settings.servers.server).Count
    $activeProfiles = @($settingsXml.settings.activeProfiles.activeProfile)
    $repoTopLevel = @(Get-ChildItem -LiteralPath $LocalRepo -Directory -ErrorAction SilentlyContinue | Select-Object -First 20 -ExpandProperty Name)

    Add-Log "Real Java smoke validation"
    Add-Log "Mode:        $ModeName"
    Add-Log "Agent:       $Agent"
    Add-Log "Project:     $ProjectRoot"
    Add-Log "Module:      $Module"
    Add-Log "Main class:  $MainClass"
    Add-Log "Maven:       $Maven"
    Add-Log "Java:        $Java"
    Add-Log "Settings:    $Settings"
    Add-Log "Local repo:  $LocalRepo"
    Add-Log "Log:         $Log"
    Add-Log "Status:      $Status"
    Add-Log "Settings summary: servers=$serverCount activeProfiles=$($activeProfiles -join ',')"
    Add-Log "Local repo sample groups: $($repoTopLevel -join ', ')"

    $mavenBase = @('-B', '-ntp', '-s', $Settings, "-Dmaven.repo.local=$LocalRepo")
    if ($Offline) {
        $mavenBase += '-o'
    }

    Invoke-LoggedCommand -Label 'maven-version' -Exe $Maven -CommandArgs @('-version') -Cwd $ProjectRoot

    $evaluateArgs = $mavenBase + @('-pl', $Module, 'help:evaluate', '-Dexpression=project.artifactId', '-q', '-DforceStdout')
    Invoke-LoggedCommand -Label 'maven-settings-and-local-repo-check' -Exe $Maven -CommandArgs $evaluateArgs -Cwd $ProjectRoot

    if ($Mode -eq 'compile' -or $Mode -eq 'e2e-s8') {
        $compileArgs = $mavenBase + @('-pl', $Module, '-am', '-DskipTests', 'test-compile')
        if ($ExtraMavenArgs) { $compileArgs += $ExtraMavenArgs }
        Invoke-LoggedCommand -Label 'maven-test-compile-reactor' -Exe $Maven -CommandArgs $compileArgs -Cwd $ProjectRoot
    }

    if ($Mode -eq 'e2e-s8') {
        if (Test-Path -LiteralPath $CpFile) { Remove-Item -LiteralPath $CpFile -Force }
        $classpathArgs = $mavenBase + @('-pl', $Module, 'dependency:build-classpath', '-Dmdep.includeScope=test', "-Dmdep.outputFile=$CpFile")
        Invoke-LoggedCommand -Label 'maven-build-test-classpath' -Exe $Maven -CommandArgs $classpathArgs -Cwd $ProjectRoot
        Assert-PathExists $CpFile 'Generated classpath file'

        $reactorClassDirs = @(
            (Join-Path $ProjectRoot "$Module\target\test-classes"),
            (Join-Path $ProjectRoot "$Module\target\classes"),
            (Join-Path $ProjectRoot 'lfms-decision\target\classes'),
            (Join-Path $ProjectRoot 'lfms-decision-api\target\classes')
        ) | Where-Object { Test-Path -LiteralPath $_ }

        $dependencyClasspath = (Get-Content -LiteralPath $CpFile -Raw).Trim()
        $parts = @($reactorClassDirs)
        if ($dependencyClasspath) { $parts += $dependencyClasspath }
        $fullClasspath = ($parts -join [IO.Path]::PathSeparator)

        if (-not $fullClasspath) {
            throw 'Computed classpath is empty.'
        }

        $javaArgLines = @(
            '-Dfile.encoding=UTF-8',
            '-cp',
            $fullClasspath,
            $MainClass
        )
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllLines($JavaArgFile, $javaArgLines, $utf8NoBom)

        Add-Log "Java argfile: $JavaArgFile"
        $javaArgs = @("@$JavaArgFile")
        Invoke-LoggedCommand -Label 'java-e2e-s8-program' -Exe $Java -CommandArgs $javaArgs -Cwd (Join-Path $ProjectRoot $Module)

        $logText = Get-Content -LiteralPath $Log -Raw
        if ($logText -notmatch '\[E2E\]\[S8\]\[PASS\]') {
            throw 'E2E S8 program exited successfully but PASS marker was not found in the log.'
        }
    }

    Write-Status -State 'passed' -ExitCode 0 -Details @{
        settingsServerCount = $serverCount
        activeProfiles = $activeProfiles
        localRepoSampleGroups = $repoTopLevel
        classpathFile = if ($Mode -eq 'e2e-s8') { $CpFile } else { $null }
        passMarker = if ($Mode -eq 'e2e-s8') { '[E2E][S8][PASS]' } else { $null }
    }

    Add-Log ""
    Add-Log "REAL_JAVA_SMOKE_PASS"
    Add-Log "Status file: $Status"
    exit 0
}
catch {
    $message = $_.Exception.Message
    Add-Log ""
    Add-Log "REAL_JAVA_SMOKE_FAIL"
    Add-Log $message
    Write-Status -State 'failed' -ExitCode 1 -Details @{ error = $message }
    exit 1
}
