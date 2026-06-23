[CmdletBinding()]
param(
    [ValidateSet('codex','hermes','shared')]
    [string]$Agent = 'codex',

    [string]$Profile = 'real-local-maven',

    [string]$Config,

    [switch]$InspectSettingsMetadata,

    [switch]$CheckVersion
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

function Expand-AgentPath {
    param([string]$Value)
    if (-not $Value) {
        return $Value
    }
    return ($Value -replace '\{agent\}', $Agent)
}

$SandboxRoot = Find-HarnessRoot
if ([string]::IsNullOrWhiteSpace($Config)) {
    $Config = Join-Path $SandboxRoot 'user\settings\maven\java-maven.local.json'
}

if (-not (Test-Path -LiteralPath $Config)) {
    throw "Config not found: $Config"
}

$configObj = Get-Content -Raw -LiteralPath $Config | ConvertFrom-Json
$profileObj = $configObj.profiles.PSObject.Properties[$Profile].Value
if (-not $profileObj) {
    $available = ($configObj.profiles.PSObject.Properties.Name -join ', ')
    throw "Java/Maven profile not found: $Profile. Available profiles: $available"
}

$maven = Expand-AgentPath ([string]$profileObj.maven)
$java = Expand-AgentPath ([string]$profileObj.java)
$settings = Expand-AgentPath ([string]$profileObj.settings)
$localRepo = Expand-AgentPath ([string]$profileObj.localRepository)

$settingsSummary = [ordered]@{
    exists = Test-Path -LiteralPath $settings
    metadataInspection = if ($InspectSettingsMetadata) { 'explicitly-enabled' } else { 'disabled' }
    serverCount = $null
    activeProfiles = @()
    profileIds = @()
    mirrorIds = @()
}

if ($settingsSummary.exists -and $InspectSettingsMetadata) {
    try {
        [xml]$settingsXml = Get-Content -LiteralPath $settings
        $settingsSummary.serverCount = @($settingsXml.settings.servers.server).Count
        $settingsSummary.activeProfiles = @($settingsXml.settings.activeProfiles.activeProfile)
        $settingsSummary.profileIds = @($settingsXml.settings.profiles.profile | ForEach-Object { $_.id })
        $settingsSummary.mirrorIds = @($settingsXml.settings.mirrors.mirror | ForEach-Object { $_.id })
    }
    catch {
        $settingsSummary.parseError = $_.Exception.Message
    }
}

$summary = [ordered]@{
    schemaVersion = $configObj.schemaVersion
    agent = $Agent
    profile = $Profile
    description = $profileObj.description
    maven = [ordered]@{
        path = $maven
        exists = Test-Path -LiteralPath $maven
    }
    java = [ordered]@{
        path = $java
        exists = Test-Path -LiteralPath $java
    }
    settings = [ordered]@{
        path = $settings
        summary = $settingsSummary
    }
    localRepository = [ordered]@{
        path = $localRepo
        exists = Test-Path -LiteralPath $localRepo
    }
}

$summary | ConvertTo-Json -Depth 8

if ($CheckVersion) {
    if (-not (Test-Path -LiteralPath $maven)) {
        throw "Maven executable not found: $maven"
    }
    Write-Host ''
    Write-Host 'Maven version check:'
    & $maven -version
    exit $LASTEXITCODE
}
