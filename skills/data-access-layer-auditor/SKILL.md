---
name: data-access-layer-auditor
description: audit a codebase to identify missing or incomplete data access functions. use when a system has database queries scattered throughout the codebase instead of abstracted into a dedicated data access layer.
---

# data-access-layer-auditor

Audits a codebase to identify gaps in the Data Access Layer (DAL) and produces a structured audit report. This skill is diagnostic, focusing on finding which database queries lack proper abstraction and which data access patterns are missing.

## Workflow
1. **Locate DAL**: Find the Data Access Layer directory (typically `lib/data-access/`, `src/db/`, `src/data/`, or similar).
2. **Inventory Functions**: Extract all existing data access functions and their signatures.
3. **Find Raw Queries**: Search the codebase for direct database calls (`.query()`, `.prisma`, `db.`, raw SQL strings, ORM chains).
4. **Cluster Queries**: Group similar queries by what they fetch or compute (e.g., all "get transaction by X" queries).
5. **Gap Analysis**: For each cluster, determine if a dedicated DAL function exists. If not, flag as missing.
6. **Assess Impact**: Rate each gap by impact (HIGH = used in 5+ places, MEDIUM = 2-4 places, LOW = 1 place) and risk (query complexity, edge cases).
7. **Synthesis**: Produce a Data Access Audit Report with missing functions prioritized by impact.

## Output Format
Every response must follow the [Data Access Audit Report](references/data-access-audit-template.md) structure.

## Boundary Rules
1. **No Implementation**: Do not create DAL functions. The output of this skill is a diagnostic artifact identifying what is missing, not an implementation plan.
2. **Concrete Evidence**: Every gap MUST be backed by specific file paths and line numbers where queries are found. No vague claims.
3. **Pattern Recognition**: Similar queries grouped by logical operation (fetch, filter, aggregate, update) rather than by file location. One DAL function may replace 5 scattered queries.
4. **Scope Limitation**: Audit only application code (src/, app/, lib/). Exclude test files, migrations, seed scripts, and vendor code.
5. **Framework Awareness**: Adapt query detection to the framework (Prisma, TypeORM, SQLAlchemy, etc.). Use framework-specific identifiers for consistency.

## References
- [Data Access Audit Template](references/data-access-audit-template.md)
