# Domain Alignment Report

## 1. Repository Analyzed
Target repository path and brief description.

## 2. Contradictions
Conflicts found between code and documentation. Each entry MUST include:
- **Term**: The term or concept in conflict
- **Claim**: What the documentation says
- **Reality**: What the code actually does
- **Evidence**: Specific file paths and line numbers
- **Resolution**: Proposed fix (update docs or update code)

## 3. Fuzzy Language
Ambiguous or overloaded terms that need sharpening. Each entry MUST include:
- **Term**: The vague term
- **Current Usage**: How it's used in different places
- **Proposed Canonical Term**: The precise replacement
- **_Avoid_**: Terms that should not be used for this concept
- **Evidence**: File paths showing ambiguous usage

## 4. Undocumented Concepts
Domain-significant concepts found in code that are missing from CONTEXT.md. Each entry MUST include:
- **Concept**: The term or concept
- **Definition**: One-sentence definition
- **Where Found**: File paths and line numbers
- **Relationships**: How this concept relates to others

## 5. ADR Candidates
Hard-to-reverse decisions in the codebase that lack documentation. Each entry MUST include:
- **Decision**: What was decided
- **Evidence**: File paths showing the decision
- **Alternatives**: What alternatives exist
- **Reversibility**: Why this is hard to reverse
- **ADR Status**: `created` or `not_created` (with reason if skipped)

## 6. Glossary Mutations
Changes applied to CONTEXT.md. Each entry MUST include:
- **Action**: `added`, `updated`, `resolved_ambiguity`
- **Term**: The affected term
- **Before**: Previous state (if applicable)
- **After**: New state
- **Section**: Which section of CONTEXT.md was modified

## 7. ADRs Created
ADRs written during this run. Each entry MUST include:
- **File**: `docs/adr/NNNN-slug.md`
- **Title**: ADR title
- **Rationale**: Why this decision was documented

## 8. Summary
- Contradictions found: N
- Fuzzy terms sharpened: N
- Undocumented concepts discovered: N
- ADRs created: N
- Glossary entries added: N
- Glossary entries updated: N
