# Workflow Evidence Observability

Status: draft
Version: v0.1.0-p9-preflight
Date: 2026-06-08

## Purpose

This document defines the observability hooks P9 must exercise through workflow evidence.

## Required Evidence

- Task Brief.
- Harness Run Card.
- Stable tool command surface.
- Status JSON path.
- Log path.
- Validation summary.
- Failure attribution if validation fails.
- Sensitive handling statement.

## P9 Rule

P9 does not need a tracing backend. It must prove that evidence paths and validation status are visible, structured, and safe to summarize.
