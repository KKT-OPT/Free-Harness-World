# Java/Maven Command Cookbook

This file collects commands that are safe to reuse for different Java projects. Replace project-specific placeholders; do not edit sandbox scripts for each project.

## Check Current Java/Maven Profile

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\show-java-maven-config.ps1 `
  -Agent codex `
  -Profile real-local-maven `
  -CheckVersion
```

## Run Maven Test For A Single-Module Project

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile real-local-maven `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -Goals test
```

## Run Maven Compile For A Multi-Module Project

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile real-local-maven `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -Module module-name `
  -AlsoMake `
  -Goals test-compile
```

## Run One Maven Test Class

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile real-local-maven `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -Module module-name `
  -AlsoMake `
  -Goals test `
  -- -Dtest=SomeTestClass
```

## Run Java Main With A Pass Marker

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-java-main.ps1 `
  -Agent codex `
  -Profile real-local-maven `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -Module module-name `
  -MainClass package.MainClass `
  -PassMarker PASS
```

## Run Java Main With Sibling Reactor Modules

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-java-main.ps1 `
  -Agent codex `
  -Profile real-local-maven `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -Module module-name `
  -MainClass package.MainClass `
  -ReactorClasspathModules common-module,api-module `
  -PassMarker PASS
```

## Use The Isolated Sandbox Maven Repository

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile isolated-sandbox-maven `
  -ProjectRoot <HARNESS_ROOT>\projects\java-smoke-test `
  -Goals test
```

## Hermes WeCom Rule

For Hermes, send one command and require one final reply:

```text
JAVA_SANDBOX_PASS
Status JSON: <path>
Log: <path>
Confirmed: <short result>
```

or:

```text
JAVA_SANDBOX_FAIL
Status JSON: <path if available>
Log: <path if available>
Failure detail: <one concise reason>
```
