# Contextual Narrative Mentorship — Focused Studio Interaction Contract

**Date:** 2026-10-13
**Status:** Development contract merged through PR #436 (`main@4122321fe09d1959278fdd087fc29f85e2f3a9d2`); mechanical Studio qualification completed at `97354ee6ea293df6c6b15783406e6c1d560403bf`; not released or broadly author-validated.
**Authority:** Existing `MISSION.md`, `docs/narrative-architecture.md`, Studio candidate/CanvasStore, and host-agent boundaries remain unchanged.

## Post-merge qualification and creative-evidence boundary

The merged PR #436 reports **64/64 real Node checks, 28 focused Python/HTTP
mentor checks, 163 Studio Python checks, 16/16 Stage-B browser checks, 11 focused
Unfolding browser checks**, and an exact-head working-editor/reopen journey.
That PR's complete Python suite was **5,591 passed / 24 baseline-equivalent
failed / 2 skipped**. The subsequent Windows exact-byte repair in merged PR
#438 passed Node **64/64**, focused mentor Python **28**, Studio Python **163**,
and Stage B **16/16**. Its full Python suite was **5,599 passed / 16 inherited
failures / 2 skipped**, with no candidate-only failure or GitHub CI. Neither
result establishes product/release readiness. See the
post-merge addendum in
`2026-10-14-mentorship-integration-qualification.md` for provenance.

A separate owner-reported fresh independent coding-agent sample generated
three distinct acceptable mentorship/audit paths while preserving a temporary
canvas, privacy, and neighbor agency; it did not accept story canon. It is
**one exploratory creative sample**, not a general claim that mentoring
improves writing, reliably produces diverse mechanisms, or feels comfortable
to authors.

**Remaining product-use questions:** can a model honor deliberate
genre-subversion; revise an earlier interpretation after an author's
correction; decline unsupported Pack claims; help the author choose among
causally different directions; and remain legible in graph-first Focus/Full
navigation? Answer with bounded real interactions or human observation where
the claim requires it. Keep the existing noncanonical/author-authority
contracts unchanged. Do not create another default chat column.

## Product intent

Auteur should teach architecture through the author's story, show genuinely different local
possibilities, ask one useful question, and sometimes challenge a consequential assumption.
It must not become a mandatory wizard, a separate chat workspace, or a new story authority.
**Graph focus remains primary. Mentorship is contextual, optional and collapsible.**

## Implemented interaction slice

- The existing local Focused Unfolding surface gains **Learn / Explore / Question / Challenge**, now progressively disclosed behind one contextual contribution and a voluntary quiet option.
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


## Developed after the initial slice (2026-10-14)

- **#427:** `studio_mentor_context.js` projects author-owned working Story Vision,
  selected focus, source links, and proposed questions with explicit evidence labels.
  Accepted Identity and verified Genre Pack evidence are **not bound** in this
  projection and must not be inferred.
- **#428–#429:** `studio_mentor.py` adds a neutral host-agent `MentorAdvice`
  contract and scoped GET/prepare/response API with actual source fingerprints,
  canvas revision matching, strict Pydantic validation, stale/duplicate response
  handling, exact source references, and a local coding-agent CLI.
- **#430:** optional graph-local conversation lets an author submit a natural-language
  answer to the host-agent advice workflow without regenerating a full
  ArchitectureCandidate or invoking a provider on passive render.
- **#431:** a direction or interpretation becomes a *working* idea only after the
  author reviews an editable preview and explicitly chooses Keep. The resulting
  CanvasStore command is bound to the exact mentor request and working revision.
- **#432:** directions carry a concrete causal differentiator. Obvious duplicate
  mechanisms are rejected. This is NOT a guarantee of semantic novelty.
- **#433:** alternate mentorship modes are collapsed behind accessible disclosure,
  and guidance can be quieted without destroying working content.
- **#434:** combined synthetic authoring journey exercises mentoring,
  answer, preview, explicit working save, Focus/Full/Realization re-entry,
  and stale-refusal through actual JavaScript controllers and mocked server.

**Historical source-stage boundary:** PRs #427–#434 were sequential
draft additions at the time of this description; they were subsequently
reconciled and merged through PR #436. The separate candidate-head
qualification above supersedes the old unmerged/untested status. Release
qualification and broader experiential effectiveness remain open.

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

Committed Node and Python tests cover mentor grounding, distinct mechanisms,
malformed and stale advice, source references, author replies, author-governed
working adoption, ordinary Studio focus preservation, and real HTTP contract
paths. Source-level simulated JavaScript tests have been executed against
exact committed bytes (15/15 model/context, 20/20 focused controller, 10/10 dialogue,
2/2 combined journeys = 47/47 at the final source checkpoint). **This was a historical pre-merge source-only
check**; subsequent real process results are listed above.

Run locally on the **fully assembled Studio branch**, not just a standalone prototype:

```sh
node --test tests/test_studio_mentorship.mjs tests/test_studio_mentor_context.mjs tests/test_studio_unfolding_controller.mjs tests/test_studio_mentor_dialogue.mjs tests/test_studio_mentor_synthetic_journey.mjs
python -m pytest -q tests/test_studio_mentor_agent.py tests/test_beginner_studio_mentor_http.py tests -k studio
python scripts/studio_stage_b_check.py
```

Then exercise real served Browser → HTTP → CanvasStore journeys at desktop and 390px:
focus, switch modes, explain, inspect ghost, adopt, keep question, edit, fail a save,
reopen, stale response, Full/Review, author drafting, return-to-focus, and keyboard/screen
reader behavior. Verify zero new canonical writes and no silent backend activity.

**Claim ceiling:** Source implementation and regression definitions are present on the
stacked branch; these commands and real-user usefulness are NOT automatically proven.
The current agent environment has no cloneable local Auteur checkout (GitHub DNS unavailable),
so source/connector review cannot substitute for full local runtime and human qualification.

## Next work after integration

1. Reconcile the initial Studio development-default PR #404 and later #408–#424 dependency
   stack before promoting any mentorship UI; do not treat this draft as release-ready.
2. Qualify the real end-to-end Focus → mentor → working choice → Full → writing journey using actual served HTTP/CanvasStore, browser/keyboard/mobile and both failed and successful saves.
3. Evaluate authentic divergent quality and author interruption cost with real creative
   sessions; adjust adaptive timing using the author's observed behavior.
4. Only if demonstrated necessary, add richer source-backed explanation examples and
   host-agent follow-up presentation. Do not add a global tutor store or automated
   preference-learning machinery speculatively.

**Product criterion:** one author can discover a worthwhile alternative, understand
its narrative mechanism, interrogate an assumption, and keep a deliberate working
choice—without losing creative context or surrendering story authority.
