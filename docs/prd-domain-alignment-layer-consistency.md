# PRD: Domain Alignment Hardening — Layer Consistency & State Report Fixes

Status: Proposed
Date: 2026-05-21
Input: artifacts/domain_alignment_report.md

## 1. Executive Summary

Resolve the four contradictions found by docs-aligner between CONTEXT.md and the codebase, ensuring the domain language accurately reflects programmatic behavior. Covers the Layer 7 ownership mismatch, the Layer ordering in state report output (missing MODULATION), the CLI --layers flag outdated mapping, and the open_ended enum normalization documentation gap.

## 2. User Goal

The repo-sensemaker session diagnosed the weakest boundary as entry-point documentation contract drift. Follow-up docs-aligner revealed additional documentation-vs-code contradictions that must be resolved to keep CONTEXT.md authoritative.

## 3. Goal Preservation & Expansion

user_goal_preserved_as: exact_match
scope_expansion_proposed: false
scope_expansion_requires_approval: false
scope_expansion_status: exact_match

## 4. Features

### F1: Update state.py _LAYER_ORDER to include MODULATION at Layer 8 and THEME at Layer 9

CONTEXT.md defines 9 layers. Current _LAYER_ORDER skips MODULATION entirely and maps THEME to Layer 8.

Acceptance criteria:
- _LAYER_ORDER includes MODULATION at position 8
/ THEME moves to position 9
/ Existing tests pass (no diagnostic output change expected)

### F2: Update _parse_layers in cli.py to use correct layer mapping

The _parse_layers function maps CONSTRAINTS to layers 2 and 4, and THEME to layer 7. Needs to align with canonical DiagnosticLayer enum.

### F3: Document CLI normalization in CONTEXT.md
(DONE — already updated in alignment step)

## 5. Out of Scope

- Adding new diagnostic rules
- Changing the DiagnosticLayer enum
- Refactoring BibleAuditDiagnostic to Pydantic (ADR-003 pending)

## 6. Acceptance Criteria

- [F1] state.py _LAYER_ORDER includes (8, MODULATION, ...) and (9, THEME, ...)
- [F1] Full test suite passes
- [F2] _parse_layers maps layers to correct DiagnosticLayer values

## 7. Machine-Readable Handoff
artifact_id: prd
schema_version: 1
source_intent_ref: artifacts/domain_alignment_report.md
user_goal_preserved_as: exact_match
scope_expansion_proposed: false
scope_expansion_requires_approval: false
scope_expansion_status: exact_match
created_at: 2026-05-21T00:00:00Z
