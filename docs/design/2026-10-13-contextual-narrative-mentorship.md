# Contextual Narrative Mentorship — Focused Studio Interaction Contract

**Date:** 2026-10-13
**Status:** Reversible development candidate, stacked on Studio Full Architecture PR #424; not yet served-browser qualified, merged, or released.
**Authority:** Existing `MISSION.md`, `docs/narrative-architecture.md`, Studio candidate/CanvasStore, and host-agent boundaries remain unchanged.

## Product intent

Auteur should teach architecture through the author's story, show genuinely different local
possibilities, ask one useful question, and sometimes challenge a consequential assumption.
It must not become a mandatory wizard, a separate chat workspace, or a new story authority.
**Graph focus remains primary. Mentorship is contextual, optional and collapsible.**

## Implemented interaction slice

- The existing local Focused Unfolding surface gains **Learn / Explore / Question / Challenge**.
- Selecting a concept reveals role-specific craft explanation and the concept's actual authored
  or candidate summary. This is general craft guidance, not an attributed genre rule.
- **Explore** uses only exact source-scoped, existing proposal-edge suggestions. When suggestions
  have duplicate role + relation mechanisms, only one per mechanism appears. If fewer useful
  directions are available, the UI says so; it never invents three alternatives.
- **Question** prefers an actual declared relation from the selected candidate; otherwise it
  asks a transparent open creative question. **Keep question** explicitly creates an editable
  *working* canvas question, never accepted StoryIdentity or Structure.
- **Challenge** is suggested automatically only for an explicitly declared proposal tension
  (`contrasts/conflicts/contradicts/opposes/undermines`). Otherwise it is an opt-in conditional
  question, not a defect or genre-quality verdict.
- **Learn** can navigate to the existing genre/trope/structure/emotion facets without creating
  parallel teaching screens. Switching mentor modes does not reconstruct unsaved inline edits.
- Requesting **fresh divergent options or a follow-up** explicitly invokes the existing
  architecture host-agent handoff with current request SHA, selected concept, story details
  and the author's Story Vision. No model/provider request occurs during passive rendering.
- The default adaptive contribution is source-declared tension when present, otherwise a
  source-linked exploratory option, otherwise an explanation. Users can freely switch modes.

## Visibility / authority / evidence

These dimensions are independent:

| Dimension | Allowed values or treatment |
| --- | --- |
| Meaning | Emotion, genre, trope, engine, structure, character, theme, etc. |
| Visibility | Focus-local selected panel; no global expanding mentor graph |
| Authority | Illustrative guidance, noncanonical architecture candidate, author-owned working idea, accepted story through existing owner only |
| Evidence | General craft lesson; proposed exact link; conditional hypothesis; attributed Pack/legacy knowledge stays with existing evidence views |

A proposed link **never** establishes actual causality, a Pack rule, or accepted canon.
Absence of a Pack never proves a genre deviation or originality. Pure mentor projection
cannot write CanvasStore, accepted Identity/Structure, or provider data.

## Author-control and recovery contract

- `Explore`, `Learn`, `Question` display and `Challenge` are read-only.
- `Keep question` requires an explicit click and uses existing `create-item` persistence,
  including revision/conflict checks and confirmed-save feedback.
- Existing `Adopt` and working edits remain under the Studio's verified explicit actions.
- A changed focus or architecture request SHA invalidates an attempted keep or fresh request.
- Question answers belong in an editable working item; there is no transient, unsaved
  secondary chat form that silently disappears when moving between graph nodes.
- User creative commitments remain the constraints for exploratory model reasoning,
  not assumptions the model is free to rewrite.

## Validation and limitations

Covered by new Node regression sources: generic lesson and absent-Pack honesty, differing
source-local roles, duplicate-suppression, stale SHA and malformed refs, source-bound questions,
declared versus hypothetical challenges, explicit question adoption, preserving unsaved working
edits across mentor modes, and no implicit model invocation.

Run locally on the **fully assembled Studio branch**, not just a standalone prototype:

```sh
node --test tests/test_studio_mentorship.mjs tests/test_studio_unfolding_controller.mjs
python -m pytest -q tests -k beginner_studio
python scripts/studio_stage_b_check.py
```

Then exercise real served Browser → HTTP → CanvasStore journeys at desktop and 390px:
focus, switch modes, explain, inspect ghost, adopt, keep question, edit, fail a save,
reopen, stale response, Full/Review, author drafting, return-to-focus, and keyboard/screen
reader behavior. Verify zero new canonical writes and no silent backend activity.

**Claim ceiling:** Source implementation and regression definitions are present on the
stacked branch; these commands and real-user usefulness are NOT automatically proven.
The current tool environment has no cloneable local Auteur checkout (GitHub DNS unavailable),
so source/connector review cannot substitute for full local runtime and human qualification.

## Next work after integration

1. Reconcile the initial Studio development-default PR #404 and later #408–#424 dependency
   stack before promoting any mentorship UI; do not treat this draft as release-ready.
2. Qualify the real end-to-end Focus → mentor → working choice → Full → writing journey.
3. Evaluate authentic divergent quality and author interruption cost with real creative
   sessions; adjust adaptive timing using the author's observed behavior.
4. Only if demonstrated necessary, add richer source-backed explanation examples and
   host-agent follow-up presentation. Do not add a global tutor store or automated
   preference-learning machinery speculatively.

**Product criterion:** one author can discover a worthwhile alternative, understand
its narrative mechanism, interrogate an assumption, and keep a deliberate working
choice—without losing creative context or surrendering story authority.
