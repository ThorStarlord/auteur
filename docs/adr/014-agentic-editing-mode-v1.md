# ADR 014: Agentic Editing Mode V1

## Status

Accepted.

## Context

Auteur needs a post-draft repair workflow that preserves author control. Editing
should not become an automatic rewrite system that silently mutates drafts or
collapses review, decision, and application into one step.

## Decision

Editing is a controlled repair system:

- edit passes produce findings and optional patch proposals;
- findings say something may be wrong;
- patches say one deterministic repair may be applied;
- patches are applied only after explicit author acceptance;
- patch application is deterministic and line-scoped;
- no editing pass overwrites `draft_vN.md` or `final.md`;
- `revised_draft.md` is written as a separate artifact under the versioned edit
  review directory;
- deterministic replacements are safe-but-simple suggestions, not claims of
  polished final prose.

V1 implements only deterministic AI-ism detection and replacement suggestions.
Developmental editing, continuity passes, style passes, LLM line editing, and
apply-all behavior are deferred.

## Consequences

Editing artifacts live under the source draft version:

```text
project/editing/chapter_03/draft_v2/
  edit_report.json
  patch_proposals.yaml
  review.md
  revised_draft.md
```

Patch IDs are scoped by project, chapter, and source draft version. A patch must
match exactly one occurrence inside its expected line range. If the line range no
longer contains the original text exactly once, the patch becomes `stale` and no
revised draft is written.
