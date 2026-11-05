# Agent-Interactive Narrative Graph — Isolated Prototype

**Status:** `PROTOTYPE / EVALUATION ONLY`. This is not production Studio integration, not a released feature, and not an authority-bearing workflow.

This prototype tests one product question:

> Does interacting with source-bound Narrative Architecture entities and relationships help an author inspect the design, form a creative intention, and prepare a better coding-agent instruction than the current Studio interface alone?

The active coding agent remains Auteur's primary constructor and reviser. The graph interaction prepares an **editable intent draft**; it does not execute a model request, save a relationship, or accept story meaning.

## Run

From the repository root:

```bash
python -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765/docs/prototypes/agent-interactive-graph/index.html
```

Pure model and DOM tests:

```bash
node --test docs/prototypes/agent-interactive-graph/model.test.mjs
node --test docs/prototypes/agent-interactive-graph/view.test.mjs
```

Served-browser comparison test:

```bash
python -m pytest tests/test_agent_interactive_graph_browser.py -q
```

## Fixtures and identity

| Fixture | Source | Request SHA | Authority |
| --- | --- | --- | --- |
| Rich recorded candidate | `docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json` | `c6269dc2e1953498ced08c1e32fa10b4d7bf05274e72c6214bd8b1f5074b5d66` | Working proposal from the prior inline qualification; not accepted story |
| Exact source request | `docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-request.json` | same | Prepared host-agent request; the candidate is a working response |
| Sparse recorded candidate | `docs/qualification-evidence/agent-first-ontology-20261103/sparse-vision-candidate.json` | `38360e093b3722405bba70eed257d14d7ef64d031a834076704ba8d13a687c82` | Working proposal; genre explicitly unknown |
| Dense stress fixture | `docs/prototypes/agent-interactive-graph/fixtures/dense-synthetic.json` | `dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd` | **Visibly labeled synthetic stress fixture**, not recorded evidence |

The recorded rich candidate contains `memory_economy` (node `nodes/3`), emotion target `wonder` (`emotion_targets/0`), directed link `engine_drives_cost` (`links/3`), and no direct recorded relation between `memory_economy` and `wonder`. That missing relation is intentional test material: the prototype must report **No recorded relation**, not invent an edge.

## Author tasks

1. Inspect Memory Economy and distinguish its recorded outgoing links from possible interpretations.
2. Select Memory Economy and Wonder together, ask how they might relate, and confirm no link is saved.
3. Form the holistic direction “Make wonder dominate fear while preserving mystery and the memory cost.”
4. Challenge one recorded causal link and keep the source evidence distinct from inference.
5. Change the source request SHA and confirm old selections/drafts become visibly stale rather than rebinding by title.
6. Complete inspection, question preparation, and return using keyboard-operable controls; test a 390px viewport.
7. Use a dense synthetic fixture and a sparse fixture; verify bounded focus and explicit unknown states.

## Authority and evidence boundaries

- Candidate nodes, links, genre interactions, contracts, emotion targets, and phases are **working proposals**, not accepted story or ontology.
- Every displayed relationship must come from an explicit candidate reference: a directed link, genre interaction, contract emotion/complex reference, phase activation, phase parallel reference, or node parent reference.
- Text similarity, visual proximity, and same-name trope phrases do not create relationships.
- The prototype reads only the loaded fixture. It does not call a model, write `CanvasStore`, use `localStorage`, change ontology, accept story meaning, or mutate the current Studio.
- The draft is labeled `prepared_not_executed` and `noncanonical_intent_draft`. It is copyable/editable text, not a `HostAgentRequest`.
- Automated DOM and browser checks do not establish human author comprehension or literary quality.

## Evaluation outcome

The completed inquiry recommends **B1 — Question-First Semantic Inspector** as the smallest credible direction, with **no production integration now**: the automated and simulated-author evidence supports a source-precision improvement, but not a proven author-effectiveness improvement. B2 adds component density without demonstrated consequential advantage over B1. The current Studio remains stronger for actually executing a revision.

Full task matrix, tradeoffs, test results, and the future production boundary are in the [prototype assessment](../../research/2026-11-04-agent-interactive-graph-prototype-assessment.md).

Verification used in this inquiry:

```bash
node --test docs/prototypes/agent-interactive-graph/model.test.mjs
node --test docs/prototypes/agent-interactive-graph/view.test.mjs
python -m pytest tests/test_agent_interactive_graph_browser.py -q
```

The prototype is an isolated evaluation artifact. It is not released, not production-integrated, and not a substitute for the active coding agent.
