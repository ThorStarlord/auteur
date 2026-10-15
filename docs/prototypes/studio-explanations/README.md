# Narrative Architecture explanatory-view experiment

Research prototype only, **not the production Studio**. Open `index.html` through a local HTTP server (from the repository root, run `python -m http.server 8765` and visit `/docs/prototypes/studio-explanations/`). Never open as `file://` because ES modules and JSON fixtures use `fetch`.

## Fixture ground truth

- **Paladin:** Transcribed/reconstructed from six owner screenshots dated 2026-10-12. Labels match the visible proposal where possible, but the synthetic connecting links, genre loops and explanations are **illustrative hypotheses**, not recovered agent packets.
- **Hybrid:** Uses the Mystery/Horror investigation + incursion phases and discovery/awe node idea from `tests/test_beginner_studio_architecture.py`, with additional stress-test elements clearly labeled synthetic.
- **Genre evidence:** `genre-evidence.json` distinguishes legacy Epic Fantasy, Mystery and Horror YAML from **missing versioned packs** for Progression and Heroic Fantasy. Absence from any pack is *unknown*, never proof of incompatibility or originality.

The shared fixture is read-only. Changing tabs, selecting nodes or returning from details may not mutate accepted story data. No provider call, CanvasStore, accepted identity, graph persistence or Genre Pack schema is involved. These are explanatory design candidates to compare, **not** recommended production UI yet.

## Semantic links and navigation (2026-10-12)

The exploratory interface now supports immediate, source-labelled links across Genre Anatomy, Convention vs. Invention, Mechanism Map and the grouped Story Map. Following a link shows the originating idea, relationship verb, supporting source and evidence status. **Hypothesis** means proposed, not proven; source-backed still means a *source-backed proposal*, never accepted canon.

Use **Previous context** or the breadcrumb buttons to return to your inquiry. Native browser Back/Forward works inside the prototype. A direct fixture deep link uses only public fixture IDs, for example `#story=paladin&view=comparison&kind=item&key=earn`; there is no author prose in this URL. Missing/retired references show an unavailable notice rather than selecting a similarly named element. Normal category/filter changes do not invent semantic relationship history.

Inspector details open only by an explicit Inspect action or a selected Story Map component. Keyboard users may Tab to any labelled link and press Enter to navigate. Returning restores focus to the invoking link when it still exists. Modified clicks can open valid public fixture destinations in a new tab. Mobile context wraps and respects reduced motion.

Verification commands from repository root:

```bash
node --test docs/prototypes/studio-explanations/*.test.mjs
python -m pytest tests/test_studio_explanatory_fixtures.py tests/test_studio_explanatory_prototypes.py tests/test_studio_semantic_browser.py -q
python -m http.server 8765
```

The Chromium integration test exercises the *same JS/CSS and JSON fixtures* through an inline ES-module adaptation because this environment's browser blocked direct HTTP navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`). It verifies real DOM/layout/keyboard events but **does not** establish real served-module loading, privacy of a production Studio URL, author comprehension, Studio persistence or a production release. This remains a read-only independent concept study.
