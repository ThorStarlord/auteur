# Narrative Architecture Visual Explanations — Comparative Review

**Date:** 2026-10-12  
**Decision:** **BOUNDED_HYBRID** (Genres = Anatomy; Tropes = Convention vs. Invention; Structure = Mechanism Map; Overview remains the original graph; Timeline remains its specialized phase projection).  
**Evidence classification:** Prototype implementation and browser heuristic inspection, **not** an author usability study or a production Studio qualification.  
**Scope:** Isolated `docs/prototypes/studio-explanations/` static browser research tool, fixture-only, no story mutations.

## Baselines and truth boundaries

- The previous Studio screenshots provided by the owner show a crowded top row of graph nodes, category dimming rather than unique visual explanations, repeated controls, an often-empty persistent inspector, and abundant blank lower graph space. This is a **screenshot baseline**, not a timed or freshly served test against PR #392.
- The prototype's **Story map** is a semantic column index, not an exact reproduction of the production spatial graph. The recommendation is to **retain the real graph as the eventual Overview**, not replace it with this index.
- Paladin material is reconstructed from six owner screenshots. Hybrid investigation/incursion phases and one explicit `discovery supports awe` source link originate from `tests/test_beginner_studio_architecture.py`; additional hybrid links and genre loops are labelled synthetic hypotheses.
- Existing main has a versioned Erotic Fiction pack and legacy genre YAML contracts, including Epic Fantasy. Progression/Heroic Fantasy versioned packs are **not established** in examined source. The pilot shows missing coverage and never assumes a missing mention means disallowed, unconventional or globally original.

## Comparison at a glance

| Variant | Best question it answers | Observed strength | Observed weakness | Selection |
| --- | --- | --- | --- | --- |
| Existing graph (screenshot baseline) | What are the story's connected parts? | Spatial exploration and relationship breadth | Clutter and visually underspecified meanings in owner screenshots | **Preserve as Overview**, not explanatory default for every facet |
| A. Genre Anatomy | What does a genre typically promise and how can it work? | Explicit promise → renewable mechanism → pressure → payoff; source coverage beside it | Provisional knowledge can look more authoritative than warranted; missing curated genre packs limit accuracy | **Genres** |
| B. Convention vs. Invention | What is genre-relative and what is distinctive in this proposal? | Two semantic axes, multi-genre source rows, treatment note; readily explains paladin generosity | Comparisons are long on mobile; bilateral layout doesn't reveal full temporal modulation | **Tropes** |
| C. Narrative Mechanism Map | How do the story's proposed elements aim to affect one another? | Source-backed vs hypothetical links, explicit verbs, text equivalent, empty-state no-arrow | One hop at a time; longer causal chains require traversal; source-proposal link quality is a ceiling | **Structure** |

## Controlled tasks and outcomes

Legend: **P** = supported by scripted interaction/visual inspection in the prototype; **H** = plausible heuristic reading only; **U** = untested with actual end users.

| Task | A | B | C | Grounded observation |
| --- | --- | --- | --- | --- |
| Locate a genre's reader promise | **P** | H | H | Anatomy makes it the dominant typographic hero. |
| Separate a conventional technique from a story-specific use | H | **P** | H | Convention view preserves genre-relative rows and story treatment separately, with a clear unknown-coverage label. |
| Follow a trope's structural/reader-purpose links | H | H | **P** | Mechanism shows only fixture-declared, status-labelled links; selecting a linked item allows further traversal. |
| Explain an absent pack without fabricating authority | **P** | **P** | P | Genre anatomy warns about missing versioned pack; comparison uses null strengths and "not classified"; mechanism still labels inference as hypothetical. |
| Return to the selected context without mutating accepted story | P | **P** | **P** | A focused Back-to-previous-element control was added after adversarial interaction identified that chips opened the detail inspector unexpectedly. |
| Hybrid phase overlap / long labels | H | **P** | P | All render on mobile without horizontal overflow, but long items consume significant vertical scroll. |
| Contradictory, stale or unsupported links | H | H | **P** | A deliberately disconnected item produces no arrows; `source_backed` exists only for the actual repository test link. Stale-refresh behavior is not exercised by this static prototype. |

No task above is an observed completion by a novice writer. These results mean the prototype **displays the information and responds to the scripted interaction**, not that a user would understand it without help.

## Verification record

- **Data/semantic:** `python -m pytest tests/test_studio_explanatory_fixtures.py tests/test_studio_explanatory_prototypes.py -q` — green; `node --test docs/prototypes/studio-explanations/model.test.mjs` — green. Pure projection tests also reject mismatched curated provenance and false legacy Genre Pack rule strengths, and cover independent genre links, absent packs, legacy strength preservation, noncanonical authority, no mutation, no dangling edges and a deliberately disconnected item.
- **Syntax:** `node --check` used on `model.mjs`, `app.mjs` and all three views — green.
- **HTTP asset availability:** Local `python -m http.server 8765` responded 200 to `index.html` via `curl`.
- **Actual Chromium layout:** Local Playwright + `/usr/bin/chromium` rendered **24 fixture × perspective × viewport** combinations: 2 fixtures, 4 perspectives, desktop 1440×900, intermediate 900×700 and mobile 390×844. Logged **zero JavaScript runtime exceptions** and **zero document-level horizontal overflow**. Screenshots recorded for seven substantive cases. Fixture switching, detail disclosure/close, noncanonical source label, keyboard arrow navigation, select/return, named source-backed link and unknown/no-arrow behavior were exercised.
- **Important limitation:** Browser navigation to HTTP/file URLs was blocked by the execution environment (`ERR_BLOCKED_BY_ADMINISTRATOR`). The Chromium inspections therefore used an inline bundle of the **same source JS/CSS and fixture JSON** with an in-memory `fetch` stub, via Playwright `set_content`. This tests real CSS/layout/event handling, but **not live ES-module resource loading or the Studio server path**. Do not call it production browser qualification.
- **Visual inspection:** Desktop Anatomy and Comparison have one clearly dominant explanation; persistent empty inspector is removed. Mobile remains readable but long label selectors and source notes can cause deep scrolling. No actual screen-reader session, human comprehension test, contrast audit or production persistence exercise was performed.

## Defects discovered and repairs

1. **Inspector surprise during selection:** Switching the chosen trope/mechanism previously opened and scrolled to the details panel. Repaired by separating visual focus (`focusItem`) from explicit inspection (`selectItem`); failing test was added first, then passed.
2. **Navigation lost origin context:** Following a mechanism neighbor lacked a way to return to the previous item. Added bounded (12-item) selection history and an explicit Previous element action; verified with a failing-then-passing source test and Chromium interaction.
3. **One-card layout waste:** A single mechanism edge occupied half a wide two-column row. Adjusted adaptive grid and single-card max width; verified in Chromium.
4. **Test-format false positive:** The initial CSS viewport assertion searched an exact whitespace literal. It was corrected to a regex for the actual media query syntax; this was a test issue, not product behavior.

## Design decision and rejection rationale

**SELECT: BOUNDED_HYBRID.** None of the candidates individually answers all the owner's questions. Keeping separate **visual heroes** is justified by their complementary evidence-bearing functions, whereas a single all-purpose graph had already exposed clutter in screenshots.

- **Overview:** Keep the production graph, offer focused neighborhoods instead of reproducing every facet's information at once. Source/proposal status remains legible.
- **Genres → A:** Present one genre's promise/grammar/pressure/payoff and sources. If there is no curated pack, display hypotheses, not a faux taxonomy. Multi-genre blending is examined genre by genre; do not invent cross-pack synthesis.
- **Tropes → B:** Present attributed genre-role rows beside story-specific treatment and intended function. Preserve distinct genre relationships; never use a scalar originality score.
- **Structure → C:** Trace explicitly recorded proposal links with verbs and provenance. Hide absent links; mark model interpretations as hypotheses. Add progressive multi-hop exploration only when real tasks warrant it.
- **Timeline:** Retain compact phases from PR #391. The chosen views may link to phases but should not duplicate full genre essays.
- **Inspector:** Closed by default; only opened for an explicit Inspect action or node detail selection, never just changing an explanatory filter.

The evidence does not justify a new canonical layer, an automatic Genre Pack/genre ontology rewrite, or merging the current draft Studio stack. The next responsibility is a **separate production integration plan** against a current exact head, after verifying the unmerged PR #392 chain and performing a true browser/server/persistence test. A curated Progression/Heroic Fantasy Pack pilot is conditional on finding that absent knowledge prevents an explanatory task with real users; it is not a prerequisite to the UI experiment.

## Stop/go and remaining uncertainties

**GO for a bounded integration design; NO-GO for production merge or claims of improved novice comprehension.** Major remaining unknowns: how an actual beginner reads the diagrams, whether dense long-form real proposals work without artificial shortening, accessibility with a screen reader, accepted story/agent review persistence under real Studio, verified book-level genre mixing, and how to source genre conventions beyond the single versioned pack.

**Cost if this recommendation is wrong:** A bounded hybrid could create too many conceptual modes; preserve the ability to compare again and to remove a view without changing canonical story data. If actual author observation favors a simpler single explanation, consolidate on that evidence rather than multiplying surfaces.

## Separate integration handoff (not implemented by this discovery plan)

1. **Preflight (owner: Studio integration engineer):** Resolve current `main`, PR #392 and ancestors, check for intervening UI changes/overlapping implementations, inspect a disposable exact-head Studio checkout, run focused tests in `tests/test_beginner_studio_*.py`, and record the real-browser baseline. Do not assume the 2026-10-12 draft head is still integration-current.
2. **Data binding (read-only):** Adapt existing `studio_architecture` candidate/projection fields and `genre_packs`/legacy `genres` data through a deterministic, noncanonical source-bound read model. Reject stale/mismatched IDs. Required interfaces: `genre_id`, `source_kind`, version/hash where available, rule-strength or unknown, proposal-relative story treatment, source-local trope reference, relation verb and evidence path. No migration or mutation of `CanvasStore`/accepted Identity.
3. **Genres hero:** Behind the existing Genres navigation, render Anatomy from actual genre sources. Missing curated coverage must visibly abstain. Preserve return-to-graph focus and source details; keep format lightweight and avoid duplicating the full genre record in every phase.
4. **Tropes hero:** Behind Tropes, show genre-relative rows and story-specific treatment, including ambiguity and explicit subversions. A text phrase owned by one genre contract is **not** a new globally shared trope ID. Test one trope serving two genres differently.
5. **Structure hero:** Behind Structure, render a bounded source-defined mechanism neighborhood; outgoing/incoming relationship verbs with source refs and explicit hypothesis status. Untyped or missing relationship is displayed as unresolved, not invented. Support keyboard and return to origin.
6. **Release gate:** Run real HTTP/ES-module browser tests (desktop 1440×900, intermediate 900×700, mobile 390×844), representative dense long-form candidate, keyboard and screen-reader review, Story Vision save/reopen, and no mutation of accepted story from navigation. Reconcile exact SHA; qualify only a frozen candidate when a genuine release milestone exists.

**Editorial follow-up, separately warranted:** Draft versioned Progression/Heroic Fantasy packs only if user tasks repeatedly require convention strength and current absent coverage blocks comprehension; test editorial claims and keep acceptance explicit. Do not import the illustrated genre loops as canonical rules.

**Post-review provenance hardening:** An adversarial test first demonstrated that a model could accept a legacy-contract source claim on an inference-only genre. The pure projection now rejects that source/coverage mismatch and any Genre Pack rule-strength label attached to a legacy-only contract; the Node test suite increased to 8/8. This repair is part of the discovery prototype, not a new accepted-story rule.
