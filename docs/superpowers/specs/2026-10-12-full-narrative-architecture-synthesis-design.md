# Full Narrative Architecture — Coordinated Synthesis and Review

**Date:** 2026-10-12
**Status:** Architecture design for author review; not product implementation.
**Baseline:** Auteur `main` at `1c5978299e03c7ffb0ae7f28cc42f84fcf7e7947`. Isolated Focused Unfolding is merged (#406–#407); live Studio UX and focused-unfolding integration remain unmerged draft stacks (#386–#392, #401–#403, #408–#413).

## 1. Intent and scope

**Requested outcome:** The Focused Unfolding creative process must culminate in a **complete, explorable narrative architecture**, not simply an ever-growing list of provisional suggestions. The result must show all of the following in one coherent story design:
- **Genre-by-genre morphology:** reader promise, target basic emotions where source-supported, conventions/tropes with strength, narrative engine, structural and payoff expectations.
- **This story's relationship to each genre:** which conventions it uses, adapts, deliberately subverts, rejects or leaves undecided.
- **Story-specific additions beyond evidenced genre morphology:** author-created mechanisms, tropes, structures, themes, emotional intentions, and how they connect. This is **not** a global claim of literary originality.
- **Integrated Book-level Identity and Structure:** target reader experience, primary engine, thematic commitments, arcs/phases, story-level structural functions, genre activations, emotional progression, conflicts and expected payoffs.
- **A terminal synthesis and readiness review** that exposes missing author decisions, conflicts, uncertain evidence and deliberately deferred downstream detail.

**Owner scope decision:** "Full" means a complete **Book-level Identity + Structure blueprint**. A full scene-by-scene plan, concrete scene realization and prose are optional subsequent stages, not prerequisites. For different scope/length, require only meaningful structural detail; do not fabricate chapters or scenes.

The canonical taxonomy stays `docs/narrative-architecture.md`: Ontology, Identity, Structure, Realization, Expression are kinds of knowledge, with Universe/Series/Book/Chapter/Scene as a separate scope axis. "Genre morphology" and "Full Architecture" are **views**, not sixth semantic layers or new canonical stores.

## 2. Considered UX approaches

| Approach | Value | Failure | Choice |
| --- | --- | --- | --- |
| Continue unfolding until every element is expanded | Simple | Unbounded graph clutter; no evidence/completion summary | Reject |
| Dedicated separate "finished story" application | Clean summary | Forks story state; breaks authoring/explanation continuity | Reject |
| **Two coordinated Focus / Full Architecture views** | Same data, local discovery and global coherence | Needs explicit provenance and derived readiness model | **Select** |

Keep the spatial graph primary from first session. **Focus view** keeps the approved 2–3 locally suggested, explicitly provisional branches and optional emotion-first start. **Full Architecture view** is accessible at any time, including on an early draft; it shows meaningful collapsed clusters and a coherent whole-story overview. The views are projections of **one existing story state**, not separate editable copies.

## 3. Full Architecture information hierarchy

The whole-story hero shows the author-designed premise, intended reader experience, genre constellation, core dramatic/renewable engine and thematic direction. Beneath it, a collapsible graph/index exposes:

1. **Story Identity and reader experience:** governing/supporting/local genre roles; primary and supporting basic emotions; richer reader experiences (hope, awe, belonging); tone/aesthetic framing; core thematic commitments.
2. **Genre Constellation and Morphology:** *one evidence panel per genre*, source-specific promises, emotion expectations, trope conventions, characteristic engines, structural patterns, escalation, resolution/payoff and any missing knowledge.
3. **Genre-to-story comparison:** same genre-specific trope/effect/pattern shown alongside the story's actual use, adaptation, departure, omission or undecided status. One trope can hold distinct roles in different genres.
4. **Story-specific additions:** author-adopted elements outside or beyond the currently evidenced morphology, and links to the emotion/structure/identity they are meant to serve. Distinguish "story-specific relative to sources" from "provably unprecedented" (never inferred).
5. **Integrated Book Structure:** major conflicts, renewable narrative mechanisms, thematic threads, macro phases/arcs, genre interactions and phase-specific activations, emotional progression, planned payoff/resolution. Character and relationship plans may be referenced from their actual owners; do not invent canonical characters.
6. **Open Design Decisions and Review:** source gaps, missing authored links, contradictory assumptions, waived genre defaults, needs-review items and optional deferred scenes.

The same summary is reachable through the selected concept's semantic hyperlinks and through the full graph. Do not create six competing permanent panels; expand one relevant cluster/evidence comparison at a time. "Show all" is explicit; "Collapse to overview" restores high-level density without losing data.

## 4. Source and authority matrix

Use **read-only derived projections** over existing owners. Never promote a proposal to a verified genre rule or to accepted story canon:

| Actual repository source | What it supplies | Mandatory limitation |
| --- | --- | --- |
| Versioned `GenrePack` (`src/auteur/genre_packs/models.py`) | Audience promises, emotional targets, `RuleStrength`, conventions, engines, escalation/resolution and boundary rules | Must have matching actual pack/version/hash and applicability; absent pack is unknown |
| Legacy `GenreContract` (`src/auteur/genres/models.py`) | Available audience product, required/optional tropes, engine bias and setup contract | Label **legacy**, not a verified versioned-pack rule |
| Studio `ArchitectureCandidate` (`src/auteur/beginner/studio_architecture.py`) | Proposed basic emotion targets, genre contracts, trope functions, engine, structural pattern, genre interactions and phases | Source-scoped **candidate interpretation**; never independently verified morphology |
| CanvasStore working items (unmerged #408 lineage) | Explicitly adopted and edited working ideas with source/provenance pointer | **Working, not canon**, including after adoption |
| Explicitly accepted Identity / Structure owners | Accepted author commitments and plans | Read-only display, never auto-accept or update on navigation |
| Focus/presentation preferences | Selected focus, collapsed clusters and dismissed ghost IDs | No authoring or canonical authority |

Every displayed claim or edge retains `source_kind`, `source_ref`, relevant proposal SHA/canvas revision/pack version/hash, `genre_id` where applicable, evidence status, authoring authority status, and an exact meaning-preserving relation verb. Unknown evidence is a normal first-class state.

**Crucial distinction:** A proposed Studio `genre_contracts[].trope_functions` phrase describes the proposal's genre interpretation; it is **not** a verified Genre Pack convention. A proposed `emotion_target_ids` relation does not show that an individual trope causes a particular reader emotion. Pack absence does not show a trope is forbidden, original or intentionally subversive.

**Classification relative to the *available* source:** `source_evidenced_convention`, `legacy_convention`, `candidate_genre_interpretation`, `adapted_by_story`, `author_added`, `intentional_subversion`, `unattributed_or_unknown`. These are derived comparison labels, **not** accepted originality verdicts or new global ontology IDs.

## 5. Target basic emotions, rich experience and structure

The existing Studio candidate declares six basic-emotion labels: `joy`, `sadness`, `fear`, `anger`, `disgust`, `surprise`. Show them as **proposed or authored reader targets** with `primary/supporting/contrasting/local` roles, intended effect, eliciting condition, aesthetic strategy and provenance. The accepted Identity's richer target experience may include hope, belonging or heroic awe; do not force them into a basic-emotion field.

Respect `docs/emotional-trajectory-contract.md`: reader promise (Identity), macro progression (Identity/Structure), planned scene experience (Structure if authored), concrete character emotion (Realization), prose rendering (Expression) are **not interchangeable**. A genre's typical emotional product is not automatically an author commitment; an author goal is not proof of audience impact.

Structure should display not only "Challenge → Growth → Responsibility", but which genre engines/patterns (if evidenced) and **which story-specific choices** support its arcs, transitions and planned payoffs. Mark unsupported causal edges as hypotheses or open questions. Scope-aware completeness does not invent scene-level requirements.

## 6. Coordination with Focused Unfolding

- Authors may start with reader emotion, genre, premise, character, trope, setting, conflict or theme. No mandatory wizard.
- On selecting a node, **Focus** shows at most 2–3 source-honest local provisional ghost branches. Explore is read-only; Adopt explicitly persists **working** architecture only; accepted Identity/Structure still needs a separate author approval.
- Switch to **Full** at any stage. Show all *author-chosen* working and accepted architectural elements in collapsible related groups; optional toggles expose unadopted proposals, genre evidence and unresolved questions.
- Select a Full node to return to Focus and develop or inspect it; browser/app Back restores graph selection, source/context, pan/zoom/search and active cluster. Use existing semantic navigation state; do **not** add a competing router.
- If an upstream emotion/genre/intention or source revision changes, mark affected dependent projections stale. Do not rewrite, delete or silently reclassify author-owned content. Reopen the exact impacted decision.

Use a compact consistent legend with labels beyond color: "Verified Pack", "Legacy contract", "Candidate interpretation", "Working idea", "Accepted commitment", "Source unknown".

## 7. Terminal review: what "complete" means

**Review Full Architecture** remains accessible throughout creation; it is not a locked final page. When the user chooses to finish narrative design, this action generates a **derived whole-story synthesis and author decision record** from actual stored data:

- Genre roles and how each genre's available conventions/emotions/structures were used or changed.
- Author target experience and links to planned mechanisms/phases/payoffs.
- Working vs accepted Identity commitments, themes, structure, arcs and intentional departures.
- Source-backed vs hypothetical links, unresolved genre tensions and missing author decisions.
- Open questions and optional deferred details, including scene plans if not currently needed.

**Coverage states:** `not_applicable` (scope doesn't need this), `not_established` (source absent), `open_author_decision`, `specified`, `integrated`, `reviewed`, `intentionally_deferred`. A missing Pack is **not** an author failure; a planned but unlinked story engine is an actionable authoring gap. Never score literary quality, demand all genre defaults, or create a universal numeric "completeness %" target.

"Ready for author review" means enough meaningful Identity and Structure choices are specified and their relationships inspectable; it **does not mean accepted**. Acceptance must still occur through existing canonical owner/review pathways, with explicit author authority. A coherent Book blueprint can be complete while scenes remain deferred.

## 8. Projector and integration contract

Derive `FullArchitectureProjection`, never persist it as a rival canonical document:

- `source_fingerprint`: exact CanvasStore revision, candidate request SHA, accepted owner revision, pack ID/version/hash;
- `identity`: differentiated working and accepted reader promises/genre commitments;
- `genre_views[]`: per-genre role, morphology evidence and story-relative use, no globally conflated trope source IDs;
- `story_specific[]`: attributed additions/adaptations and unknown classifications;
- `structure`: engines, phases/arcs, genre activations, explicit structural links;
- `emotional_design`: basic targets, richer experiences and planned trajectory;
- `typed_links[]`: actual source IDs and relation verbs, no same-title binding;
- `review_items[]`: actionable coverage statuses, source conflicts and return-to-focus IDs.

Pure projector reads existing candidate and author working state; attach versioned Pack/legacy evidence **only when delivered**. Keep accidental revisions, missing sources and conflicting evidence **visible**, not automatically reconciled by the model. No provider call on render, navigation or Review. New proposals use the existing **explicit, bounded host-agent handoff**.

**Delivery boundaries after design approval:** (1) pure evidence/projection model + tests; (2) standalone Focus ↔ Full comparative graph and author review (no production persistence claims); (3) reconciled live Studio integration plus actual CanvasStore/canonical-authority, served HTTP and browser tests. Studio PR ancestors #386–#413 remain draft; do not claim the prototype merge qualifies production source.

## 9. Failure and acceptance journeys

1. **Paladin:** emotion-first intention → adopt Earned Breakthrough → develop Challenge/Growth/Responsibility → open Full. See per-genre Progression/Heroic/Epic explanations with honest pack coverage; see story-specific generosity and continuing responsibility; follow the structure/effect edges back into Focus without losing working nodes.
2. **Shared trope, distinct genres:** same phrase with separate genre-relative roles, source identity and evidence. No invented unified genre law or "globally original" claim.
3. **No Pack:** still possible to produce a coherent Book Identity + Structure; unknown morphology is not a missing creative decision. Legacy/candidate sources remain separately labelled.
4. **Nonlinear creation:** start from premise or character, add reader emotions and genres later, review the same coherent Full view; scene plans optional.
5. **Unlinked story addition:** appears in Full as an actual author addition needing a link, not an invented edge. Authors can focus it and create one.
6. **Conflicts/staleness:** revision/pack hash/source SHA changes invalidate affected synthesis, preserve author-owned notes and trigger a visible refresh/review reason.
7. **Authority:** View switching and review make **zero** CanvasStore/acceptance writes. Explicit working adoption and canonical acceptance remain independent.
8. **Accessibility/scale:** full graph is usable with dense 80-node/180-link candidate and 14 genre contracts, keyboard focus and Back, reduced motion and 390px no horizontal overflow; use collapsible grouping, not a default global node explosion.
9. **Real integration verification:** focused projection tests + actual served Studio browser/HTTP/CanvasStore and accepted Identity/Structure boundary tests on the exact reconciled draft PR lineage. A mock/inline Chromium screenshot does not qualify real persistence.

## 10. Explicit non-goals and design gate

Not in scope: mandatory scene-level Realization, prose writing, automatic originality judgment, enforcing unsupported packs, an extra semantic layer, new canonical story owner, continuous paid model generation, automatic adoption or acceptance, or a wholesale unrelated graph rewrite.

**Decisions selected for the owner:** Complete Book-level Identity + Structure endpoint, with optional scenes; two coordinated graph modes; genre morphology per genre and evidence strength; explicit genre-to-story comparison; author additions relative to known evidence; readable evidence-linked final synthesis; no new canonical data store.

**Review requirement:** This is a written architectural specification, not a claim that the code or integration is implemented. Review of this spec precedes the separate test-first implementation plan and product changes.
