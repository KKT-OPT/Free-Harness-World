# Hermes WeCom Generic Java Validation Prompt Template

Please run one Java/Maven validation through the local agent sandbox, then reply to this WeCom chat with only the final status summary.

Fill in the command before sending this prompt:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent hermes `
  -Profile real-local-maven `
  -ProjectRoot <PROJECT_ROOT> `
  -Goals <GOAL_1>,<GOAL_2> `
  -Module <OPTIONAL_MODULE> `
  -AlsoMake
```

For a Java main class validation, use this form instead:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-java-main.ps1 `
  -Agent hermes `
  -Profile real-local-maven `
  -ProjectRoot <PROJECT_ROOT> `
  -Module <OPTIONAL_MODULE> `
  -MainClass <PACKAGE.CLASS> `
  -ReactorClasspathModules <OPTIONAL_MODULE_A>,<OPTIONAL_MODULE_B> `
  -PassMarker <OPTIONAL_PASS_MARKER>
```

Rules:

- Do not print or inspect Maven settings contents, credentials, tokens, or auth files.
- Do not invent project-specific success criteria. Use the Maven exit code, Java exit code, and optional pass marker only.
- If the command exits zero and any requested pass marker is found, reply:

```text
JAVA_SANDBOX_PASS

Status JSON: <path from script output>
Log: <path from script output>
Confirmed: <short command/result description>
```

- If the command exits non-zero, or the requested pass marker is missing, reply:

```text
JAVA_SANDBOX_FAIL

Status JSON: <path from script output if available>
Log: <path from script output if available>
Failure detail: <one concise reason>
```
