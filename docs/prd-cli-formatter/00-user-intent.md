# User Intent: Improve Code Structure

## Source

Conversation with user on 2026-06-10.

## Stated Goal (Exact)

> "Analyze my current project and propose a P0 task to improve the code structure."

## Context

The user asked for a codebase architecture analysis and a P0 (highest priority) improvement task. The analysis identified several architectural gaps, with the most impactful being the CLI monolith (1812 lines of argparse + domain logic + stdout formatting interleaved). The architecture document declares a "core separation" (domain logic → structured objects → formatter/serializer) that is documented but not implemented.

## Discovery Summary

The `improve-codebase-architecture` analysis revealed:

1. **CLI monolith** (1812 lines, ~140 print() calls) — mixes argument parsing, domain orchestration, error handling, artifact writing, and stdout formatting in one file. The documented architecture says these should be separate layers.
2. **Structure analyzer monolith** (1647 lines, 83.5KB) — ~41 diagnostic rules as sequential if-blocks, no rule registry or plugin mechanism.
3. **Identity module** (984 lines) — 6+ responsibilities bundled.
4. **No conftest.py** — ~10 copies of fixture code across test files.

The P0 recommendation was the CLI formatter/serializer extraction because it touches every user-facing command, reconciles the documented architecture with implementation, and unlocks genuine dual-native operation (agents consuming structured artifacts instead of parsing human-readable stdout).

## Goal Classification

**Category**: Engineering architecture improvement (not a user-facing product feature).
**Preservation**: `core_with_expansion` — the core is the CLI extraction; natural adjacent improvements exist.
