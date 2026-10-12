# Explanatory Semantic Navigation — Product Specification

**Decision date:** 2026-10-12  
**Status:** Owner-endorsed interaction direction; executable plans follow; not yet implemented.  
**Product:** Auteur Narrative Architecture, initially in the merged explanatory prototype, then in the separate draft Living Story Studio lineage.

## Problem grounded in the repository

The merged concept study at \`docs/prototypes/studio-explanations/\` has four visually distinct perspectives. Its \`app.mjs\` holds both \`history\` and \`selectionHistory\`, but the former is only appended to, and the latter remembers item IDs without perspective, origin, reason or focus. \`views/anatomy.mjs\` passes "How this story employs it" items into the detail inspector; \`views/comparison.mjs\` mainly has "Inspect provenance"; \`views/mechanism.mjs\` can refocus neighboring nodes. This is useful exploration but not yet consistent cross-perspective semantic navigation.

The live Studio does **not** exist on \`main\` at this decision point. Its source is in the open UX PR lineage ending at #392. That code already has \`visitFacet\`, a 12-entry \`facetHistory\`, cross-facet inspector links and presentation-only \`rememberFocus\`; a later integration must extend this rather than introduce a rival routing authority.

## User outcome

From a meaningful relationship in Genre Anatomy, Tropes, Structure, Timeline or Overview, the author can follow **a labelled, source-honest connection** to the appropriate explanation, see *why* they arrived, inspect the evidence and return to the exact point of inquiry. The story is the hero; the navigation system should not become another crowded interface.

### Owner decisions selected

1. **Immediate navigation** on activation (mouse, touch, Enter). Do **not** require a preview popover; previews are a separately warranted, optional later experiment.
2. **Semantic links, not merely tabs:** visibly name the source, relationship verb and destination; give the destination a concise "Why you arrived here" context line and its evidence status.
3. **Compact trail:** a previous-context action and a breadcrumb of up to three visible hops; collapse older hops to an accessible "Earlier" control when necessary. No permanent navigation side rail or duplicate inspector.
4. **Overview remains spatial** in the actual Studio; Genres use Anatomy, Tropes use Convention vs. Invention, Structure uses source-backed Mechanism Map, and Timeline/Emotions remain specialized views. In the independent concept study, keep its existing grouped Story Map as a comparison baseline, **not** a production graph replacement.
5. **No authorial mutation:** following, hovering, selecting or backing out of a link never edits Story Vision, proposal data, working canvas or accepted story.

## Navigation and relation contract

Define a read-only \`SemanticLink\` (prototype) with these fields:
- \`id\`: ephemeral stable within the current proposal/fixture; not a global trope ontology ID.
- \`from\`, \`to\`: \`{kind:"genre"|"item"|"phase", id:string}\`, always source-local.
- \`targetPerspective\`: \`"anatomy"|"comparison"|"mechanism"|"overview"|"timeline"|"emotions"\`; the prototype resolves only its four supported modes; Studio integration resolves additional modes.
- \`verb\`: a short original meaning-preserving relation, not an invented causal assertion.
- \`explanation\`: explicitly sourced description when present; otherwise a neutral statement of the documented relationship (do not invent plot, emotions or purposes).
- \`sourceRef\`, \`sourceKind\`, \`supportStatus\`: preserve provenance; \`source_backed\` still means **source-backed proposal**, not canon or empirical proof; \`hypothesis\` remains visibly hypothetical.
- \`ownerGenreId?\`, \`phaseId?\`: only when a source field explicitly establishes those scopes.

Only derive navigable links from existing \`model.genre_links\`, \`model.proposal_edges\`, and the Studio's actual \`genre_contracts\`, \`links\`, \`genre_interactions\`, \`emotion_target_ids\` and phase activation references. A trope-function phrase inside a contract is **source-scoped**; it must not be assigned an invented globally shared trope ID. A genre targeting an emotion **does not** prove that each trope in that genre causes the emotion. A missing Genre Pack, absent connection or disputed convention **cannot** be rendered as authoritative evidence or as proof of incompatibility/originality.

Genre-to-trope and trope-to-genre traversal may be reciprocal navigation **over the same declared relation**; it must not create new causal edges. Labels must say "explore", "used by", "supports" or the actual recorded \`verb\`, not imply a mechanistic effect the record does not support.

## Route / history behavior

- Concept-study state: \`{storyId, perspective, focus:{kind,id}|null, viaLinkId:string|null, trail:ViewSnapshot[]}\`; \`ViewSnapshot\` includes previous view, selection, originating focus target, and viewport scroll/focus locator. Max 12 history snapshots; no duplicate consecutive hop. An ordinary within-view selection is not a cross-view breadcrumb.
- For the **public static fixture prototype only**, serialize allowlisted fixture IDs, perspective and source-local IDs in the URL hash; use browser History API for Back/Forward and refresh. No prose or story contents in the URL. Keyboard/touch links are actual accessible anchors with valid hrefs; interception preserves normal modified-click/new-tab behavior.
- In Studio, reuse its existing presentation-only local focus mechanism. **Do not put canvas IDs, private story identifiers or working prose in a public URL** without a separate privacy decision. Browser history parity is an enhancement only if safe in that origin; an in-app reversible trail is mandatory.
- Opening a deep link directly with no previous exploration shows no fabricated "Back" destination. Back/Forward restores the exact prior view when valid. An unknown item/retired source/replaced proposal offers a visible "This reference is unavailable" state, plus return to the last valid view/Overview. No silent navigation to a similarly titled different element.
- A workspace switch from Architecture to Story Realization and back restores the authoring selection; semantic navigation must not steal editor focus or push source data into a canonical save.

## Interaction / accessibility

A user arriving through a link sees **one concise** context bar, e.g.:

> From "Progression Fantasy" → *uses* → "Earned breakthrough" · Hypothesis (not a curated rule) · See source

"See source" opens an explicitly requested lightweight inspector; the main visualization is unchanged. Keyboard focus moves to the destination heading and returns to the invoking link after Back, with a visible focus ring and a polite announcement. Breadcrumb controls must be real links/buttons with names; do not hide all navigation in icons, hover, colors or tooltips. Mobile at 390px wraps the context without horizontal page overflow. Respect reduced-motion preferences.

## Acceptance journeys

1. **Paladin:** Progression Fantasy Anatomy → linked "Earned breakthrough" trope (Convention view) → explicitly declared "illustrates Challenge/Learning/Transformation" link (Mechanism view) → Back twice to the originating genre and focused control. The illustrated mechanism remains labelled hypothesis where applicable.
2. **Multi-genre:** Same trope → Progression Fantasy and Heroic Fantasy are two **different** genre-relative roles with separate evidence and independently functioning Back.
3. **Absent knowledge:** No Versioned Progression/Heroic Pack must display "not classified by versioned pack" (not "not expected"); no unsupported trope→emotion shortcut.
4. **Resilience:** Unknown ID, changed proposal/source SHA, duplicate link click, deep-link reload, browser Back/Forward (prototype), narrow viewport and keyboard-only traversal remain recoverable.
5. **Authority:** Navigation does not submit acceptance, invoke an agent, alter working story/CanvasStore, or bypass explicit copy/review actions.

## Work boundaries

**First responsibility:** improve the isolated, already-merged prototype (source-honest links + testable navigation). **Second responsibility:** once the draft Studio UX lineage and actual server are reconciled, integrate those interaction principles into the real Studio's projections without copying fixture-specific hypotheses into live genre knowledge.

**Non-goals:** automatic concept previews; a new graph/layout engine; adding versioned Progression/Heroic Genre Packs; new canonical trope/genre schemas; scoring creativity; tracking full navigation telemetry; syncing private story routes via public URL; claiming end-user comprehension from synthetic fixtures alone.
