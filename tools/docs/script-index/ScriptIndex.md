# Harness Script Index

Status: active
Version: v0.5.0-p12.3
Date: 2026-06-11

## Purpose

This document indexes current Harness scripts by stability and exposure.

Stable scripts are Tool Assets. Candidate, runtime and historical scripts are not default command surfaces.

## Stable Scripts

### `tools/scripts/stable/show-java-maven-config.ps1`

Purpose:

- show a safe Java/Maven profile summary;
- check whether Maven, Java, settings path and local repository path exist;
- avoid printing Maven settings XML or credentials.

Key inputs:

| Parameter | Meaning |
|---|---|
| `-Agent` | `codex`, `hermes` or `shared`. |
| `-Profile` | Java/Maven profile ID. |
| `-Config` | Local Java/Maven config path. |
| `-InspectSettingsMetadata` | Explicit diagnostic mode; off by default. |
| `-CheckVersion` | Run Maven version check. |

Output:

- JSON summary;
- no settings XML body by default;
- no credentials by default.

### `tools/scripts/stable/invoke-maven-project.ps1`

Purpose:

- run stable Maven validation for a managed project;
- default goal is `test`;
- write status JSON and log path.

Key inputs:

| Parameter | Meaning |
|---|---|
| `-ProjectRoot` | Project root. |
| `-Agent` | Agent name. |
| `-Goals` | Maven goals. |
| `-Module` | Maven module. |
| `-Profile` | Java/Maven profile ID. |
| `-Offline` | Maven offline mode. |
| `-SkipTests` | Skip tests. |
| `-Settings`, `-LocalRepo`, `-Maven`, `-Java` | Explicit path overrides. |

Safety:

- passes settings path to Maven but does not parse settings XML;
- does not print settings XML;
- tracked docs may record status JSON/log paths and safe summary fields only.

### `tools/scripts/stable/invoke-java-main.ps1`

Purpose:

- compile a Java/Maven project or module;
- build classpath;
- run a Java main class;
- optionally check a pass marker.

Key inputs:

| Parameter | Meaning |
|---|---|
| `-ProjectRoot` | Project root. |
| `-MainClass` | Java main class. |
| `-Agent` | Agent name. |
| `-MavenGoals` | Maven goals. |
| `-Module` | Maven module. |
| `-Profile` | Java/Maven profile ID. |
| `-ProgramArgs` | Program arguments. |
| `-JvmArgs` | JVM arguments. |
| `-PassMarker` | Success marker. |

Safety:

- passes settings path to Maven but does not parse settings XML;
- generated classpath and argument files are runtime evidence;
- tracked docs may record log/status paths and safe summary fields only.

### `tools/scripts/stable/clean-sandbox.ps1`

Purpose:

- clean old `var/logs` and `var/tmp` runtime state;
- default mode is dry-run.

Key inputs:

| Parameter | Meaning |
|---|---|
| `-Apply` | Actually delete candidates; requires explicit user approval. |
| `-KeepLatestPerLogFamily` | Number of logs to keep per family. |
| `-KeepTmp` | Keep tmp files. |
| `-Root` | Sandbox root. |

Safety:

- dry-run by default;
- `-Apply` requires explicit user authorization.

### `tools/scripts/stable/test-project-registry.ps1`

Purpose:

- validate `user/registry/projects.local.json`;
- confirm project registry entries stay as routing metadata;
- detect missing project roots, duplicate `projectId` values and out-of-bound roots.

Key inputs:

| Parameter | Meaning |
|---|---|
| `-Root` | Harness Root. |
| `-Registry` | Registry path relative to Harness Root. |
| `-SelfTest` | Run built-in negative checks without writing temporary files. |

Output:

- JSON status summary;
- project count;
- error list with stable error codes;
- routed project summary.

Safety:

- read-only;
- does not read credential files, private settings contents or auth files;
- validates only registry shape and project entry existence.

### `tools/scripts/stable/test-harness-governance.ps1`

Purpose:

- run the P12.3 Harness Root governance self-check;
- verify required routes, stale route candidates, `docs/_temporary`, `.gitkeep`, single architecture authority, sensitive boundary, build output, INDEX/PLANS drift, repository boundary and project registry status;
- keep cleanup and governance checks report-first and dry-run.

Key inputs:

| Parameter | Meaning |
|---|---|
| `-Root` | Harness Root. |
| `-Registry` | Project registry path relative to Harness Root. |

Output:

- JSON status summary;
- severity counts;
- stable check list;
- findings with repair suggestions.

Safety:

- read-only and dry-run;
- excludes runtime state, settings, external tools, historical scripts, runtime helper candidates and local-only profile files from default scanning;
- does not read Maven settings XML, auth files, credential bodies or raw runtime logs;
- invokes `test-project-registry.ps1` as the registry sub-check.

## Historical Or Restricted Scripts

| Script | Status | Reason |
|---|---|---|
| `tools/scripts/historical/run-java-smoke.ps1` | historical | Historical smoke proof only; not a default stable command surface. |
| `tools/scripts/historical/run-real-java-smoke.ps1` | historical-restricted | Requires explicit local project/settings parameters or environment variables; not default agent exposure. |
| `tools/scripts/runtime/hermes-wecom-generic-java-prompt.md` | prompt-candidate | Should be rewritten as Task Brief/adapter example when needed. |

## Candidate Root Helpers

| Script | Status | Next Review |
|---|---|---|
| `tools/scripts/runtime/audio_core.ps1` | candidate-helper | P12 or later, only if audio runtime support becomes a Harness concern. |
| `tools/scripts/runtime/hermes-update-codex.ps1` | candidate-helper | P12 or later, after runtime boundary review; local paths must come from parameters or environment variables. |
| `tools/scripts/runtime/Start-Hermes-Desktop.ps1` | candidate-runtime-helper | P12 or later, after runtime boundary review; local paths must come from parameters or environment variables. |

Candidate helpers are not default stable tools.
