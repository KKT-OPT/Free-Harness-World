[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [ValidateSet('codex','hermes','shared')]
    [string]$Agent = 'codex',

    [string[]]$Goals = @('test'),

    [string]$Module,

    [switch]$AlsoMake,

    [switch]$Offline,

    [switch]$SkipTests,

    [string]$Profile = 'real-local-maven',

    [string]$Config,

    [string]$Settings,

    [string]$LocalRepo,

    [string]$Maven,

    [string]$Java,

    [string]$RunName = 'maven-project',

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraMavenArgs
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
$WorkDir = Join-Path $TmpDir "maven-$Agent"
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$SafeRunName = ($RunName -replace '[^A-Za-z0-9_.-]', '-')
$Log = Join-Path $LogDir "$SafeRunName-$Agent-$Stamp.log"
$Status = Join-Path $LogDir "last-$SafeRunName-$Agent.json"

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
        maven = Join-Path $SandboxRoot 'tools\external\apache-maven-3.9.9\bin\mvn.cmd'
        java = Join-Path $SandboxRoot 'tools\external\jdk\bin\java.exe'
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
        goals = $Goals
        offline = [bool]$Offline
        skipTests = [bool]$SkipTests
        maven = $Maven
        java = $Java
        settings = $Settings
        localRepository = $LocalRepo
        sandboxHome = $HomeDir
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
    try {
        & $Exe @CommandArgs 2>&1 | ForEach-Object {
            $line = $_.ToString()
            Add-Content -LiteralPath $Log -Value $line -Encoding UTF8
            Write-Host $line
        }
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    Add-Log "EXIT: $exitCode"
    return $exitCode
}

try {
    $profileValues = Resolve-JavaMavenProfile
    if (-not $Maven) { $Maven = Expand-AgentPath $profileValues.maven }
    if (-not $Java) { $Java = Expand-AgentPath $profileValues.java }
    if (-not $Settings) { $Settings = Expand-AgentPath $profileValues.settings }
    if (-not $LocalRepo) { $LocalRepo = Expand-AgentPath $profileValues.localRepository }

    Assert-PathExists $ProjectRoot 'Project root'
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

    Add-Log 'Generic Maven project validation'
    Add-Log "Agent:       $Agent"
    Add-Log "Profile:     $Profile"
    Add-Log "Project:     $ProjectRoot"
    Add-Log "Module:      $Module"
    Add-Log "Goals:       $($Goals -join ' ')"
    Add-Log "Offline:     $([bool]$Offline)"
    Add-Log "Maven:       $Maven"
    Add-Log "Java:        $Java"
    Add-Log "JAVA_HOME:   $env:JAVA_HOME"
    Add-Log "Settings:    $Settings"
    Add-Log "Local repo:  $LocalRepo"
    Add-Log "Sandbox home:$HomeDir"
    Add-Log "Log:         $Log"
    Add-Log "Status:      $Status"

    $mavenArgs = @('-B', '-ntp', '-s', $Settings, "-Dmaven.repo.local=$LocalRepo")
    if ($Offline) {
        $mavenArgs += '-o'
    }
    if ($Module) {
        $mavenArgs += @('-pl', $Module)
    }
    if ($AlsoMake) {
        $mavenArgs += '-am'
    }
    if ($SkipTests) {
        $mavenArgs += '-DskipTests'
    }
    $mavenArgs += $Goals
    if ($ExtraMavenArgs) {
        $mavenArgs += $ExtraMavenArgs
    }

    $exitCode = Invoke-LoggedCommand -Label 'maven-project' -Exe $Maven -CommandArgs $mavenArgs -Cwd $ProjectRoot
    if ($exitCode -ne 0) {
        throw "Maven command failed with exit code $exitCode"
    }

    Write-Status -State 'passed' -ExitCode 0 -Details @{ commandArgs = $mavenArgs }
    Add-Log ''
    Add-Log 'MAVEN_PROJECT_PASS'
    Add-Log "Status file: $Status"
    exit 0
}
catch {
    $message = $_.Exception.Message
    Add-Log ''
    Add-Log 'MAVEN_PROJECT_FAIL'
    Add-Log $message
    Write-Status -State 'failed' -ExitCode 1 -Details @{ error = $message }
    exit 1
}
