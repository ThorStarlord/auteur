# Bible Audit: Lore Drift Detection (Diagnostic Slice)

**Status**: accepted
**Date**: 2026-05-10
**Context**: Auteur Engine v1 — structure diagnostics extension

## Problem

After multiple chapters are drafted and accepted, the StoryBible accumulates
events but discards the Cartographer's `character_state_changes` during accept.
Only `draft_iterations` is stored. As a result, a character can silently
teleport from the Capital to the Dungeon across chapters with no intermediate
event — and no tool catches it. The author discovers these inconsistencies
during a manual re-read, often after the drift has compounded.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Scope | Lore-first (Bible facts vs. chapter drafts) | Bible already tracks character state; blueprint drift is partly version-control |
| Detection mechanism | Deterministic rules first, LLM escalation later | Matches the "no LLM in deterministic analysis" constraint; fast TDD loop |
| First rule | Location teleportation | Unambiguous, hard to false-positive, location data already in Cartographer outlines |
| Data dependency | Enrich Bible event recording during accept | Cartographer already produces `character_state_changes` per scene — it's just not written to the Bible |

## Architecture

The gap is between Layer 6 (Carriers — Bible facts) and Layer 7 (Representation
 — chapter drafts). The diagnostic ensures drafted events do not violate
tracked carrier state.

```
Cartographer outline
  └─ character_state_changes: [{character, field, before, after}]
       │
       ▼ (currently discarded)
  PipelineRunner.draft_chapter / accept
       │
       ▼ (after Slice 1)
  Bible event deltas + upsert_character
       │
       ▼ (Slice 3)
  audit_bible_locations(bible) → list[BibleAuditDiagnostic]
       │
       ▼ (Slice 4)
  auteur audit <project> CLI
```

## Issue Slices

### Slice 1: Enrich Bible event recording during accept

**What**: Modify `PipelineRunner.draft_chapter` and `_cmd_accept` to extract
`character_state_changes` from the Cartographer outline and record them in Bible
event `deltas`. Also call `bible.upsert_character` for each state change so the
Bible's character records stay current.

**Files**: `src/auteur/pipeline.py`, `src/auteur/cli.py`

**Acceptance**: After `auteur draft` passes, `bible.json` events contain
`character_state_changes` arrays and character records have updated `location`
fields. Existing tests still pass.

**Depends on**: Nothing. This is the prerequisite.

---

### Slice 2: Bible audit data model

**What**: Define `BibleAuditDiagnostic` as the output contract. Includes
`severity`, `layer` (new value: `carriers`), `rule`, `message`, `evidence`,
and `repair_options` matching the existing `preserve_intent` / `challenge_intent`
pattern.

**Files**: New file `src/auteur/structure/bible_audit.py` (data model + detector)

**Acceptance**: Pydantic model validates. Can be imported and instantiated in tests.

**Depends on**: Nothing (pure data model). Can be built in parallel with Slice 1.

---

### Slice 3: Location teleportation detector

**What**: A pure function `audit_bible_locations(bible: StoryBible) -> list[BibleAuditDiagnostic]`:
1. Iterates the Bible event log in order.
2. Tracks each character's last known location from event deltas.
3. For consecutive events where the same character appears with different
   locations but no intermediate event records a move for that character,
   emits a diagnostic.

Edge cases: first appearance (no diagnostic), clean linear movement (no
diagnostic), multiple characters moving (one diagnostic each), mixed valid
and invalid transitions within same chapter.

**Files**: `src/auteur/structure/bible_audit.py`

**Acceptance**: Unit tests for clean movement, teleportation, first appearance,
static location, intermediate event explaining the move, multiple characters.

**Depends on**: Slice 2 (data model), Slice 1 (Bible must have location data).

---

### Slice 4: CLI command `auteur audit`

**What**: Wire the detector to a CLI subcommand:
```
auteur audit <project_path> [--output JSON_PATH] [--format text|json]
```
Runs `audit_bible_locations` against the project's Bible, prints diagnostics to
stdout (text) or writes JSON. Exit code 0 if no errors, 1 if errors found.

**Files**: `src/auteur/cli.py`

**Acceptance**: CLI integration test with fixture project. `--output` writes
valid JSON. Error exit codes correct.

**Depends on**: Slice 3.

---

### Slice 5: Repair proposal output

**What**: For each location teleportation diagnostic, generate `repair_options`:
- `preserve_intent`: "Add a transition scene between chapter N and N+1."
- `challenge_intent`: "Revise chapter N+1 outline to place the character in
  the same location, or add an intermediate chapter."

Write proposals in `structure/proposals/` matching the existing format.

**Files**: `src/auteur/structure/bible_audit.py`, `src/auteur/cli.py`

**Acceptance**: `auteur audit --repair` writes proposal files.

**Depends on**: Slice 3, Slice 4.

## First Red Test

```python
# tests/test_bible_audit.py

from auteur.bible import StoryBible
from auteur.structure.diagnostics import DiagnosticSeverity
from auteur.structure.bible_audit import BibleAuditDiagnostic, audit_bible_locations


def test_detects_location_teleportation(tmp_path):
    """A character at the Throne Room in event 1 and the Dungeon in event 2,
    with no intermediate event explaining the move, should produce an error."""
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)

    bible.record_event(
        chapter_index=1,
        summary="Aldric confronts the king.",
        deltas={
            "character_state_changes": [
                {"character": "Aldric", "field": "location",
                 "before": None, "after": "Throne Room"}
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")

    bible.record_event(
        chapter_index=2,
        summary="Aldric escapes through the tunnels.",
        deltas={
            "character_state_changes": [
                {"character": "Aldric", "field": "location",
                 "before": "Throne Room", "after": "Dungeon"}
            ]
        },
    )
    bible.upsert_character("Aldric", location="Dungeon")

    bible.save()

    diagnostics = audit_bible_locations(bible)

    assert len(diagnostics) == 1
    d = diagnostics[0]
    assert d.severity == DiagnosticSeverity.ERROR
    assert d.rule == "carriers.location_teleportation"
    assert "Aldric" in d.message
    assert "Throne Room" in d.message
    assert "Dungeon" in d.message
```
