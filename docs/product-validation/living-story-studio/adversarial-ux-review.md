# Adversarial UX Review — Does Studio Reduce Author Work?

**Frozen target:** \`bd2ba539d2f300941681fa7c7b80ab4765354b79\`
**Review lens:** interaction and mental-model attack; no acceptance of graph-first utility merely from UI presence.
**Evidence:** source control flow, selected contracts, one isolated execution of original JS handlers against a minimal DOM stub; **no live Browser or human subject session**.
**Provisional disposition:** **REFINE INTERACTION / BLOCK DEFAULT PROMOTION**. Graph-first UX may be worthwhile, but two core re-entry/editing flows require repair and observation.

## 1. Intended author journey and baseline

The [existing Beginner Home](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/index.html#L17-L65) asks for a premise, optionally a first-scene intent, then offers shape-first or Quick Draft. The Studio's empty canvas allows an idea or scene *without premise*. This is a real new entry affordance, but its effectiveness depends on avoiding extra mandatory labeling, graph positioning and duplicated prose entry.

The relevant author-facing promise from [the selected contract](../../design/2026-10-09-living-story-studio.md): free capture -> relationships -> focused scene writing -> discoveries -> deliberate acceptance -> meaningful Book re-entry.

## 2. Highest-consequence findings

### U-01 — Switching nodes overwrites unsaved inspector edits
**Evidence:** directly demonstrable from original JS control flow; isolated minimal-DOM execution reproduced the loss; **live Browser execution not yet run**.
**Priority:** repair before relying on Studio for prose or note capture.
**Source:** [renderInspector](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L342-L383), [choose](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L385-L391), [saveCurrent](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L444-L449).

Mechanism:
1. Select A: renderInspector copies \`A.content\` to the textarea.
2. Type unsaved text in A's inspector without selecting "Save working note."
3. Select B: choose(B) calls renderInspector without capturing A's edits.
4. Return to A: original \`A.content\` reappears. The typed content is not in the working model and cannot be autosaved by the document store.

A minimal DOM stub executing **the extracted original functions** returned \`initial_visible="Original A"\`, after typing \`"Unsaved crucial dialogue"\`, then switching B -> A, \`after_switch_back="Original A"\`; model remained unchanged. This is a narrow logic reproduction, not a full-app browser check.

**Counterargument:** explicit Save is visible. But "working canvas saves on this computer" and scene field auto-saves can create a conflicting mental model. Use on-change capture, a dirty-state guard, or on-selection commit; verify actual work preservation and status truth. Do not quietly make the user responsible for remembering which fields save differently.

### U-02 — Re-entering Studio from Home creates a *new* canvas instead of finding prior work
**Evidence:** conclusive navigation-code path; **user confusion predicted, not observed**.
**Priority:** high for multi-session usefulness.
**Source:** [static Home link](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/index.html#L54); [openRemote](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L53-L69) creates a fresh \`canvas\` when no query parameter exists.

A saved working canvas can be revisited via its exact URL, but there is no comparable in-app "Your working canvases" selector. Clicking the Home opt-in link again has no remembered canvas identity. This can make durable work appear missing after normal navigation.

**Counterargument:** the prototype deliberately supports URL identity; that can be adequate for developer testing. It is not an adequate unqualified default Book re-entry experience. Prefer a simple local recent-canvas entry, not a new global dashboard.

### U-03 — Prose writing still crosses two authoring surfaces
**Evidence:** source-established interaction seam; actual friction unobserved.
**Source:** [Studio expanded scene](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L519-L537) and [Quick Draft handoff](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L487-L516).

The scene text is editable in Studio, but generating needs separately-entered \`scene_premise\` and \`scene_intent\`, and discovery/review takes the author into the legacy Quick Draft route. A free-form scene note is not yet the single author-intent source across those views.

**Risk:** story creation feels like choosing among adjacent tools rather than continuing one workpiece. **Counterargument:** keeping the accepted-story path in an existing owner protects narrative authority. Prefer preserving scene and editor focus through roundtrip, not inventing shadow canon.

### U-04 — Dense canvas limits and discoverability are not qualified
**Evidence:** bounded source positions and feature availability; usability consequences hypothetical.
**Source:** [CanvasPosition / max counts](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_store.py#L48-L82); [toolbar](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.html).

Free canvas actions coexist with search, layers, evidence workspace ID, advanced impact artifact ID, JSON import/export and Book controls. Some controls expose raw backend concepts (workspace/artifact IDs) even though Beginner's stated design favors author language. In large graphs the 1400 × 1040 coordinate bounds, 200 notes and 500 connections become meaningful constraints.

**Counterargument:** these are acceptable experimental guardrails and advanced controls. Evaluate how quickly real author tasks hit them, then simplify or group—not automatically move to an unbounded canvas engine.

### U-05 — Source-meaning hierarchy is uneven
**Evidence:** UI and labels; author comprehension unobserved.
**Source:** [relationship/impact/Book views](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L187-L310).

The implementation correctly distinguishes working versus read-only derived nodes and describes hypothetical impact, but a chapter-change filter shows current relationship values rather than a historical snapshot. The UI explicitly warns about that distinction; test whether it is still comprehensible. Also test whether raw provenance is too prominent at beginner level.

## 3. Scenario walkthrough probes (hypotheses, not observations)

| Scenario | Predicted friction / falsifier | Evidence required |
| --- | --- | --- |
| S1 no-premise first note | A blank map may be inviting or intimidating | first useful idea and time-to-first prose, self-reported confusion |
| S2 edit A -> B -> A | Unsaved edits should never disappear silently | actual Browser reproducer + durable reload |
| S3 scene before Story Identity | Two generation inputs can be redundant after free-form writing | matched Quick Draft comparison |
| S4 unexpected Sister Beatrice | Prose discovery could require duplicate entry in graph | accepted selection and source-link re-entry trace |
| S5 changing ambiguous romance | Directed edge labels may imply more certainty than intended | task comprehension and correction action |
| S6 12 characters / three threads | Hairball, zoom limits, and group discoverability | navigation time, lost-focus occurrences |
| S7 revise accepted event | Hypothetical impact must not be mistaken for changes made | comprehension and API no-write evidence |
| S8 six-Chapter reopen | Previous canvas may be undiscoverable from Home | re-entry without remembered URL, compare baseline |
| S9 keyboard and mobile | keyboard actions present but full focus/state fidelity unverified | device + assistive tech walkthrough |
| S10 interrupted save | failure message should preserve all unsent text and recovery | controlled disconnect + tab concurrency |

## 4. Recommended interaction changes (not implemented in this review)

1. Capture or guard inspector edits on every selection change; show truthful saved/unsaved status. Verify both rapid typing and node switching.
2. Provide a local way to reopen existing canvases without the original URL; preserve selected node and edit context when returning from guided Quick Draft.
3. Avoid duplicate scene-intent entry when the author has already supplied a meaningful scene note, while preserving explicit authority for generation.
4. Reduce default toolbar cognitive load: Create/Connect/Write first, source evidence and artifact IDs on progressive disclosure.
5. Evaluate contextual focus over showing an entire graph; maintain the accessible outline as a first-class alternative.
6. Make provenance/accepted/provisional distinctions legible without presenting all technical data by default.

## 5. Verdict

**REFINE INTERACTION.** The two core creation/re-entry defects are stronger evidence than aesthetic intuitions. Neither establishes that spatial creativity is worthless. Do not default the Studio until S2/S8 loss and re-entry are repaired and S1/S5/S6 demonstrate actual author value.

**Claim ceiling:** one narrow code-executed DOM-stub reproduction, source-grounded UI mapping and proposed comparative scenarios; no real browser accessibility results or human preference claims.
