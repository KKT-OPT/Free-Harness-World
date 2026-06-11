# Semantic Dictionary Template

Status: template
Version: v0.1.0-p12.1
Date: 2026-06-10

## Purpose

Maintain canonical project terminology so humans and agents use the same names for domain terms, modules, fields, states and workflows.

## Inputs

- architecture facts
- PRD facts
- API and data facts
- source naming conventions
- reviewed user terminology

## Outputs

- `projects/<project-id>/docs/project/dictionary/SemanticDictionary.md`
- canonical term table
- alias and forbidden-term table
- candidate term review list

## Sensitive Boundary

Do not include customer secrets, credentials, private settings, raw user data, unredacted logs, private paths or real private repository URLs. Redact or generalize examples.

## Instantiation Rules

1. Copy this file to `projects/<project-id>/docs/project/dictionary/SemanticDictionary.md`.
2. Prefer terms already used in reviewed project facts.
3. Record unresolved terms as candidates.
4. Update architecture, API, data and test docs when a canonical term changes.

## Core Terms

| Term | Recommended English Name | Definition | Forbidden Alias | Related Docs |
|---|---|---|---|---|
| `<term>` | `<english-name>` | `<definition>` | `<forbidden-alias>` | `<doc-link>` |

## Module Names

| Module | Recommended Name | Responsibility | Forbidden Name | Architecture Layer |
|---|---|---|---|---|
| `<module>` | `<recommended-name>` | `<responsibility>` | `<forbidden-name>` | `<layer>` |

## Field Meanings

| Field | Object | Type | Meaning | Constraint |
|---|---|---|---|---|
| `<field>` | `<object>` | `<type>` | `<meaning>` | `<constraint>` |

## States

| State | Meaning | Trigger | Next State |
|---|---|---|---|
| `<state>` | `<meaning>` | `<trigger>` | `<next-state>` |

## Workflow Names

| Workflow | Recommended Name | Start | End | Description |
|---|---|---|---|---|
| `<workflow>` | `<recommended-name>` | `<start>` | `<end>` | `<description>` |

## Alias Normalization

| Alias | Canonical Term | Reason |
|---|---|---|
| `<alias>` | `<canonical-term>` | `<reason>` |

## Candidate Terms

| Candidate | Source | Question | Review Status |
|---|---|---|---|
| `<candidate>` | `<source>` | `<question>` | `<status>` |
