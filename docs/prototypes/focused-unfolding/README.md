# Auteur — Focused Unfolding (isolated concept study)

**Product direction:** a single graph-first workspace for progressive **authoring + explanation**, with 2–3 proactive **focus-local provisional** suggestions, an optional emotion-first invitation, other author-chosen starting anchors, explicitly separate Explore/Adopt/Dismiss actions, and visual cluster collapse. Source: [Focused Unfolding design](../../superpowers/specs/2026-10-12-focused-unfolding-authoring-explanation-design.md).

## Run

Open `index.html` through any static server at the repository root:

```bash
python -m http.server 8765
# then /docs/prototypes/focused-unfolding/index.html
```

Model tests:

```bash
node --test docs/prototypes/focused-unfolding/model.test.mjs
```

UI regression tests:

```bash
python -m pytest tests/test_focused_unfolding_browser.py -q
```

## Author experience

1. Start from intended reader emotion, or choose a premise, character, genre, trope, structure, setting, theme, conflict, relationship, or free-form idea.
2. The selected **working** idea remains in the spatial workspace. Up to **three** dashed, attributed *hypothesis* branches appear nearby; on narrow mobile there are **two** at once.
3. Clicking a suggestion explains its tentative relationship, caveat and an illustrative provenance token. Only **Adopt** creates a noncanonical working node; **Dismiss** hides just the unadopted option.
4. After adopting, select that node and the local potential mechanisms unfold. **Previous focus** returns without deleting adopted items.
5. **Explore more alternatives** pages through additional options. **Collapse this branch** only alters presentation, not stored nodes. **Edit current idea** preserves adopted downstream text and flags relevant nodes as needs-review. **Simulate source revision** invalidates original ghosts but never deletes working author decisions.

## Authority and verification ceiling

- The authored scenario, proposals, emotional effects, speculative genres and links are **illustrative design hypotheses**, not verified Genre Packs, recovered real packets, tested reader effects or story canon.
- This is **not** a live model integration, not a production AI provider, and **not** wired to CanvasStore. Adoption is **in-memory demo state** and will be lost on refresh. The real Studio is still on an unmerged PR stack.
- No network/provider request fires on render, focus, Explore, Adopt, or Dismiss. The source evidence identifiers are explicitly `demo-fixture/...`.
- Chromium interaction tests load the **same JS/CSS** through an inline browser harness. Direct navigation from Chromium to a local HTTP origin was blocked with `net::ERR_BLOCKED_BY_ADMINISTRATOR` in this environment; an HTTP `curl` head did confirm status `200`. This is *not* served-ESM qualification or testing of real Studio persistence.
- The actual working-document role/provenance extension, atomic server adoption and host-agent bounded suggestion request are covered by the **separate** development plans and require full Studio / server qualification.
