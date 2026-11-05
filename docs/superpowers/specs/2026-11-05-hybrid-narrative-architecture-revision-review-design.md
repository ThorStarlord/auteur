# Hybrid Narrative Architecture Revision Review — Design Specification

**Date:** 2026-11-05
**Status:** AUTHOR-SELECTED DIRECTION / PROPOSED SPEC — not implemented, not release-qualified
**Scope:** Read-only, source-bound review of holistic revisions to a **working** Narrative Architecture, combining whole-architecture before/after comparison and selected-entity/relationship overlays.
**Out of scope:** Rebuilding the graph engine, new persistent architecture history, manually editing candidate components, semantic agent actions on graph nodes, ontology changes, accepted Story Identity changes, or unreviewed model calls.

## 1. Purpose

When the active coding agent proposes a holistic architecture revision, an author needs two distinct views of its consequences:

1. **Whole architecture:** Is the revised narrative design more coherent, and what systems were changed together?
2. **Local meaning:** What happened to this particular engine, emotion, genre function, phase, or relationship, and what exactly is supported by recorded data?

The selected experience is a **hybrid**: readable revision summary first, synchronized *before-and-after* comparison for the whole working architecture, and an optional focused difference overlay when an author selects an element or relationship. The author can inspect the proposed changes without applying them.

**Product thesis:** Compare **meaning** and actual fields, not merely spatial graph appearance. A node with unchanged ID and geometry can undergo a major narrative change; nodes can move visually without semantic change.

## 2. Existing system and authority

This is an evolution of existing Studio behavior, not a replacement:

- Existing host-agent architecture proposal and holistic revision in src/auteur/beginner/studio_architecture.py.
- Existing deterministic review in src/auteur/beginner/studio_architecture_review.py.
- Existing read-first architecture overview and graph in src/auteur/beginner/browser/studio.js, studio_architecture_reader.js, studio.html and studio.css.
- Existing Full Architecture/Focused Unfolding remain separate navigation modes.
- Existing B1/B2 source-grounding prototype and no-inference rules in docs/prototypes/agent-interactive-graph/.
- Existing repository design and plan from 2026-11-03 and 2026-11-04, plus MISSION.md and docs/narrative-architecture.md.

**Exact live read contract at review_ready:** project_architecture() returns a current working candidate at projection.candidate and its request SHA at projection.candidate_request_sha256. It returns the proposed candidate inside projection.review.candidate, the proposed request SHA inside projection.review.request_sha256, and the previous request SHA in projection.review.prior_request_sha256. The baseline must match this previous request identity.

**Crucial:** During review_ready the current working architecture is still the **before** graph; the proposed candidate is only a pending **after** graph. The existing apply_architecture_review(...) endpoint is the sole path for applying the complete working revision. Neither that operation nor the review UI accepts canon.

## 3. Approaches and selection

| Alternative | Advantage | Risk | Decision |
| --- | --- | --- | --- |
| Overlay as default for every change | Fast visual localization | Dense graphs mix past and proposed states, hiding major reorganizations | Not default |
| Separate before/after only | Clear version boundary and global comparison | Harder to inspect small changed relationships in context | Not sufficient alone |
| **Hybrid: whole comparison + focused overlay** | Global architectural judgment and local precision, independently available | Requires coordinated selection, layout and focus-state semantics | **Selected** |

Do not show both full graphs and a full overlay simultaneously. One view is primary; the focused overlay is a deliberate drill-down.

## 4. Author journey

**Precondition:** A complete baseline working ArchitectureCandidate v2 exists and a host agent has returned a valid *revision* response (review_ready). Development from zero is not a before/after review.

1. Studio shows **Proposed working revision — review before applying**, and a readable request summary with the existing textual changes.
2. Author chooses **Compare architectures**; see two distinct, labeled snapshots: **Before — current working architecture** and **After — un-applied agent proposal**.
3. Both views share a stable semantic layout and synchronized selected-element focus; panning/zoom may be synchronized when useful but must not create coupled focus traps.
4. An author selects a changed node or relationship. The selected **same kind and same stable ID**, when present on both sides, is highlighted; if absent, show **Added** or **Removed** rather than matching another by title.
5. **Inspect focused changes** opens a local difference overlay and a semantic inspector showing exact changed fields, original and proposed values, source references, and the effects that the **agent expressly stated** when such explanations exist.
6. The author returns to the whole comparison without losing chosen scope, selected identity or reading context.
7. From the existing review workflow, author may apply the **whole working revision**, or leave it unapplied and request another revision. No per-node or per-edge partial acceptance and no canonical story acceptance.

A revision with no structural changes but significant field/meaning changes must still be discoverable. A revision with only added/removed/redirected links must also be discoverable.

## 5. What appears in each surface

### 5.1 Readable summary (default)

Visible before either graph:

- The exact author revision request.
- An accurate count of added, removed, field-changed and unchanged records **by typed kind**; no inflated totals from rendering aliases.
- Important changes affecting emotion targets, genre contracts, engines, phases and directed relationships.
- Author-commitment warnings, including any removed/retyped author_declared emotion, represented as **changes requiring review**, not conclusively violated canon.
- Accepted constraints as **requirements to check**; unchanged object fields do not prove narrative/constraint compliance.
- The agent candidate's summary labeled **Revised architecture summary**, *not* "agent rationale" by inference.
- An explicit statement that causal consequences, creative justification and downstream impact are **not established** by a raw field diff.

Existing textual diff remains available as a fallback if the visual comparison cannot be rendered.

### 5.2 Whole-architecture before/after

- Read-only graph snapshots of **ArchitectureNode** and explicit **ArchitectureLink** and **GenreInteraction** (typed, directed) records. Do not invent edges from text similarity, placement, trope phrases, or neighboring node positions.
- Both sides distinguish **unchanged**, **added**, **removed**, **field-changed**. Added elements are naturally absent on Before; removed elements are naturally absent on After. Missing is **not recorded**, not nonexistent forever.
- Keep stable IDs in stable positions across snapshots where possible; use a single **union-layout** map for shared nodes, reserving slots for added/removed. Include scoped filtering and fit-to-view.
- Secondary elements (EmotionTarget, ComplexEmotion, GenreContract, NarrativePhase, candidate summary) are **first-class typed items in a searchable change index and semantic inspector**, not invented spatial graph nodes unless existing source-backed visualization supports them.
- Relationship redirection with stable link ID is a **changed relation** with old and new endpoints visible; do not collapse it into one unqualified edge.
- An accessible linear change index is always available and carries the same selection semantics as the graphs.
- Distinguish old/current and new/proposed with persistent text labels; do not rely on color alone.

### 5.3 Focused overlay

- Selecting a node, link, interaction or typed non-spatial component shows its **local before/after** meaning and relevant recorded one-hop relations.
- The view may overlay previous and proposed elements only for the chosen focal neighborhood; use separate labeled layers/toggles and a text diff, not two confusing unlabelled edge sets.
- Explicit changes appear field by field: source/target/function, genre interactions' kinds/mechanisms/risks, emotional effects and provenance, complex emotional components, genre roles/trope functions/payoffs, phase activations and transitions, node summaries and parents.
- Long or nested fields show abbreviated overview **and full expandable values**. Do not hide changed keys behind equal-looking narrative summaries.
- Where an entity is missing in one candidate, render a clearly labeled added/removed placeholder, not a guess about identity continuity.
- Never call an inference "causally affected" because it is graph-adjacent. A statement such as **possibly related** is a hypothesis and is distinguished from recorded links.

## 6. Semantic identity, diff and provenance

Use a **typed source identity**: (kind, stable ID). Existing comparable kinds:

- node, link, emotion_target, complex_emotion, genre_contract (stable key = genre_node_id), genre_interaction, phase; and top-level summary as a special singleton, not a fictional graph node.

Each displayed Before or After record includes:

- side = before | after
- owner request SHA = baseline candidate_request_sha256 | proposed review.request_sha256
- kind and stable ID
- exact source location for that **side**: e.g. nodes/3, links/4, genre_contracts/1 (array indices may differ)
- status = added | removed | changed | unchanged, computed by stable typed identity
- semantic field-level comparisons from actual before/after JSON values, **including nested arrays/objects**.

No title-based pairing, even if a node is renamed or replaced. Reused stable IDs with changed category or endpoints produce explicit changed-field records, not silent remapping. Each candidate must satisfy the existing ArchitectureCandidate validation when admitted as a real response; the comparison must fail safely on malformed legacy data.

The renderer may reuse the existing review.changed_components as navigation hints but derives **all actual visual comparisons from the two source candidates**, never from summary text alone. It does not create or alter an authoritative story graph.

## 7. States and constraints

**Review not ready:** no two-sided graph. State **Awaiting agent**, **No revision**, **Guidance changed**, or **Source stale** as actually reported; never synthesize the missing After candidate.

**Stale/superseded review:** clear/disable actionable apply review controls and show a plain mismatch, relying on the existing server as final authority. A newer baseline, request or canvas selection invalidates prior focus and comparison.

**No semantic differences:** distinguish revised candidate summary-only change from unchanged object graph; do not misleadingly paint unchanged nodes as affected.

**High density:** the current candidate model permits up to 80 nodes and 180 links, plus genre interactions. Limit labels/visible neighborhoods, allow filter/index, preserve a working textual alternative, and verify performance without introducing a graph database.

**Mobile/keyboard:** when two graphs cannot be shown legibly, use **Before | After | Differences** controls with the same stable focus; keyboard selection/return, clear focus, reduced motion and screen-reader usable change index. Test 390px and high contrast. Do not rely on click-only SVG paths.

**Read-only:** comparing and hovering do not write CanvasStore, call models, modify current candidate, or cause acceptance.

**No new generation backend:** the existing prepare/complete/review/apply lifecycle remains unchanged.

## 8. Truthfulness and author authority

The UI must distinguish:

- **Observed semantic diff:** an exact field change or recorded link difference.
- **Agent explanation:** only when source-backed to an actual explicit agent explanation; the existing candidate summary does not count as a causal rationale.
- **Interpretive possibility:** a clearly marked hypothesis, not a verified impact.
- **Accepted author commitment:** a separate source authority, not a label inferred from an architecture node or role.
- **Preservation:** field-identical can be reported as "unchanged in the candidate"; accepted-constraint **compliance** is "not checked" unless separately verified.

Do not carry forward existing UI statements that overclaim "Preserved accepted constraints" or "Agent's stated rationale" when the source evidence does not establish those claims. Fix **only copy and projections necessary for the new review surface**, rather than starting an unrelated defect-repair initiative.

Review may be dismissed without applying. Only the exact existing author-triggered **Apply to working architecture** operation changes the current working candidate, with backend concurrency/freshness checks. Accepted Story Identity, Structure, Realization, Expression and shared ontology remain untouched.

## 9. Design scope, execution and release gates

**This specification is an approved *design direction*, not implementation authorization in this turn.** The companion plan describes a staged deliverable: a source-bound deterministic semantic comparison, a read-only UI experiment using the existing live review payload, an author-facing evaluation, and gated integration into Studio's revision-review surface.

The 2026-11-04 B1/B2 inquiry determined **no immediate production integration** without a consequential author-task improvement. This design does not retroactively change that evidence. The new holistic revision review must demonstrate incremental value over the **existing** Studio textual diff and working graph, not a deliberately weakened baseline.

**Production default/release gate:** no automatic activation of the new visual review as the primary default until a real-author evaluation or an explicitly recorded owner policy decision authorizes it. An opt-in internal/experimental integration may be technically developed and tested, with clear labeling, without claiming release qualification.

## 10. Author validation and acceptance criteria

Minimum comparison scenario using real baseline/proposal pairs (with synthetic mutations clearly labeled):

1. **Semantic-only node change:** same graph topology, but node.summary and emotional function differ. Author can identify the consequential meaning change.
2. **Redirected relationship:** stable link ID, changed source or target; old and new endpoints separately legible.
3. **Genre/phase/complex-emotion change:** one non-spatial typed record changes despite unchanged graph nodes; author can find it in the index and inspect full values.
4. **Author commitment/provenance:** previously author_declared emotion changed or removed; review does not misreport it as preserved.
5. **Accepted constraints:** are listed as requirements to verify; cannot be mistaken for checked compliance.
6. **No-op/summary-only revision:** correctly reported with no invented graph deltas.
7. **Freshness:** while viewing, newer request or canvas selection makes the old comparison and action unavailable.
8. **Keyboard/mobile:** complete review and return with equivalent text interaction at 390px without relying on geometry.
9. **Large graph:** inspect one changed link without losing orientation or encountering an unbounded visual explosion.
10. **Apply authority:** no writes from inspection; a deliberate apply still uses the existing server-verified whole-working-revision path.

**Evaluation question:** Does the hybrid help an author **explain what changed and decide whether to keep the whole working revision** better than the current text review + graph? Record source inspection, automated tests, real served browser, simulated tasks and **actual human author observations** separately. No claims about narrative quality solely from green checks.

## 11. Selected product posture

- **Default for a future qualified integration:** readable change summary, then optional synchronized Before/After, then focused overlay when selecting a specific difference.
- **Fallback:** existing textual review and graph.
- **Do not add:** partial acceptance, new graph-persistence store, automatic canon mutation, graph simulation claiming causality, or model invocation from viewing a diff.

See the companion [Hybrid Narrative Architecture Revision Review Implementation Plan](../plans/2026-11-05-hybrid-narrative-architecture-revision-review.md).
