# The Spring Ledger: working Series architecture (consolidated, noncanonical)

This package is the consolidated working architecture of *The Spring Ledger*, a 30-Book fantasy Series about a shared water commons. It replaces the accumulated experimental archive as the thing a future author or agent reads first. It also records one cold-start test: a fresh agent, given only this package and the product's access route, wrote and then had corrected a Book 24 function.

**Status: working and noncanonical. Not author-approved. Nothing here is accepted canon.** Some elements are the author's own intentions, some are agent proposals awaiting the author's decisions, and some are unresolved. Section 9 of the architecture separates them.

## Start here

1. [`01-series-architecture.md`](01-series-architecture.md): the compact architecture. Story Vision, the three engines, the arcs, the characters and institutions, the promises, the finale alternatives, the provisional assumptions and the open choices.
2. [`03-author-intentions.md`](03-author-intentions.md): the author's fixed intentions, verbatim, kept apart from any interpretation.
3. [`02-working-candidate-W6.json`](02-working-candidate-W6.json): the machine-readable working candidate, validated on current main's schema. It agrees with the architecture.
4. [`04-provenance.md`](04-provenance.md): where every element comes from, the exact source commits, and every consolidation edit.
5. [`09-continuation-assessment.md`](09-continuation-assessment.md): what the cold-start test showed, and the next responsibility.

## How to use the package

**As an author.** Read the architecture's sections 1 and 8. Those are the Story Vision and the choices only you can make. Any proposal an agent makes should be labelled, and you can accept, change or reject it.

**As an agent continuing the Series.** Read the architecture in full, then the candidate through the product:

    PYTHONPATH=<repo>/src PYTHONUTF8=1 python -m auteur.beginner.studio_architecture --project <project> --canvas <canvas> resume

Before adding anything, follow §10 of the architecture: name the pressure you develop and the loop it exercises; keep the author's intentions and the reserved choices exactly as they are; label any new element as agent-proposed and say how it would be reversed; prefer development inside Books 24–26 to a redesign of Arcs IV or V; keep every finale alternative open.

The product's operations, their limits and the candidate's schema are in [`cold-start/packet-as-given/03-auteur-operations.md`](cold-start/packet-as-given/03-auteur-operations.md). Read it before writing, and note the correction in section 6 of the continuation assessment: the host instructions forbid `character` nodes, which the schema allows.

## What is in the package

| Path | What it is |
|---|---|
| `01-series-architecture.md` | The compact architecture (the main document). |
| `02-working-candidate-W6.json` | The consolidated candidate, W5-derived. |
| `03-author-intentions.md` | The author's intentions, verbatim. |
| `04-provenance.md` | Sources, identities, consolidation edits and product operations. |
| `09-continuation-assessment.md` | The cold-start assessment, its gaps, its product findings and the next responsibility. |
| `cold-start/packet-as-given/` | The exact packet the fresh agent received (five files). |
| `cold-start/output/` | The agent's Book 24 function and candidate, as produced, and the corrected versions with their product responses. |
| `cold-start/critique/` | The critique packet and the critique report, verbatim. |
| `cold-start/verification/` | The verification packet and report, verbatim. |
| `cold-start/corrections.md` | Every correction to the Book 24 proposal, with the defect each removes and the mechanical checks. |
| `evidence/` | The scripts that build the candidate, the concepts and the disposable canvas, and the correction script. |
| `evidence/concepts/` | The five provisional concepts, each recorded with status `provisional`. |

## Reproduce

Run from the repository root, using its own `src`.

    export PYTHONPATH="$PWD/src" PYTHONUTF8=1
    P=experiments/spring-ledger-working-architecture
    python $P/evidence/make_consolidated_candidate.py "$PWD" $P/02-working-candidate-W6.json
    python $P/evidence/make_concepts.py $P
    python $P/evidence/build_canvas.py "$PWD" <scratch>/proj spring-ledger-consolidated

`make_consolidated_candidate.py` reads W5 from its source commit, `d6dd636d62e23c0138ae0a561bf329332852124c`. The canvas builder records the story vision and the intentions from PR #551 through the product's own bridge, and it writes nothing into the repository.

## Provenance in one line

Built on current main (`fa432cc3`). The machine-readable candidate is W5 from PR #554 (`d6dd636d`), with five consolidation edits. The architecture is written from PR #553's construction (`aaae0eaa`), its verification in PR #554, and the original architecture in PR #551 (`3168963b`). PR #552 (`ac1fbff8`) was used as evidence in #553 and is not a source here.

## What the cold-start test shows, in brief

- **Reconstructed:** the engines, the arcs, the Book 23 chain, the finale alternatives and the open choices, from the compact architecture alone, with the one exception of a fact we had dropped (Hesper's household is hand-light), now restored.
- **Produced:** a Book 24 function, "The Uncounted Crew", locally closed, derived from Books 20–23, and labelled throughout.
- **Corrected:** the function had one whole-Series change it did not justify, two decisions on author-reserved choices, a Hall framing that tilted against Alternative B, and a gauge ambiguity. Each correction is recorded, and most were verified by a fresh reviewer. The last round was checked mechanically.
- **Not applied:** the bridge cannot apply a reviewed revision, so the live architecture still has no Book 24.

See [`09-continuation-assessment.md`](09-continuation-assessment.md) §§ 7 and 8 for the answers, and for the verdict on whether this is a reusable product capability. The short answer: it is a successful freeform-agent exercise supported by real product operations, not yet a demonstrated reusable capability for Book-level development.

## Claim ceiling

This package shows that the architecture can be read and reconstructed from compact prose and a candidate, that a fresh agent can add a locally coherent Book-level function within it, and that the product can validate such a function but cannot yet apply it. It does not show that the Book is good fiction, that any author would accept it, or that the architecture is reliably reconstructable by any agent. The continuation is one run. The agent was not blind: its environment carried the same inherited context as the coordinator, and the packet included two pieces of experimental history, both recorded in the assessment.

## Open

- **Author decisions** (architecture §8). The capability record and the Right's review point, which Book 24 uses, are the most consequential open choices here.
- **Product.** Expose the existing reviewed-revision apply step through the bridge. Reconcile the host-prompt category rule with the schema.
- **Representation.** The Arc V phase and the open questions are at their caps. Any further Book-level development will need either more room or a Book-scope representation. That is a design question, not a quick fix.
