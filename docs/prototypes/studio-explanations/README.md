# Narrative Architecture explanatory-view experiment

Research prototype only, **not the production Studio**. Open `index.html` through a local HTTP server (from the repository root, run `python -m http.server 8765` and visit `/docs/prototypes/studio-explanations/`). Never open as `file://` because ES modules and JSON fixtures use `fetch`.

## Fixture ground truth

- **Paladin:** Transcribed/reconstructed from six owner screenshots dated 2026-10-12. Labels match the visible proposal where possible, but the synthetic connecting links, genre loops and explanations are **illustrative hypotheses**, not recovered agent packets.
- **Hybrid:** Uses the Mystery/Horror investigation + incursion phases and discovery/awe node idea from `tests/test_beginner_studio_architecture.py`, with additional stress-test elements clearly labeled synthetic.
- **Genre evidence:** `genre-evidence.json` distinguishes legacy Epic Fantasy, Mystery and Horror YAML from **missing versioned packs** for Progression and Heroic Fantasy. Absence from any pack is *unknown*, never proof of incompatibility or originality.

The shared fixture is read-only. Changing tabs, selecting nodes or returning from details may not mutate accepted story data. No provider call, CanvasStore, accepted identity, graph persistence or Genre Pack schema is involved. These are explanatory design candidates to compare, **not** recommended production UI yet.
