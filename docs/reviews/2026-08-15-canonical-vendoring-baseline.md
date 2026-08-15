# Auteur × Sensemaking — first canonical vendoring baseline (2026-08-15)

## Goal

Turn Auteur's historical mixed Sensemaking snapshot into a reproducible,
intentional dependency boundary without blindly upgrading the curated subset.
This is the first intentional update after the historical-provenance exception
recorded in `skills/VENDORED.yaml`.

## Upstream baseline

Selected upstream Sensemaking revision:

`1458f9210c79336175878b8527ed7ecba1e0b6a3`

At selection time this is `ThorStarlord/sensemaking-skills` `main`. It is the
reconciliation merge whose parents are the Workflow-v0/provenance lineage tip
`195cb77861203ae6fa74a9597eabc4f187d542e7` and the prior GitHub-main tip
`0ffb564b67eb7fcac3c1a2c8a1365ed6b2a0e6c5`. It therefore provides a single
current upstream state containing both lines of work.

The baseline is a **comparison anchor**, not a byte-identity claim. Auteur
continues to vendor a curated subset, and retained compatibility deviations are
listed explicitly in the manifest.

## Historical provenance boundary

The pre-baseline snapshot remains `unrecoverable_for_pinning`. Establishing
`1458f921...` as the first canonical baseline does not rewrite the old snapshot
or claim that it originated from this SHA. Historical evidence and the previous
reconciliation record remain unchanged.

## Project-classification decision — RETIRE

Issue #63 exposed that `scripts/validate-project-classification.py` was treated
by the fixture harness as a single-argument validator even though it ignored the
fixture path, changed to repository root, and scanned a hard-coded
`test-projects/` corpus. The valid-only harness exception tolerated that
contract mismatch rather than resolving it.

The capability-ownership investigation found:

- current upstream at `1458f921...` no longer contains the
  `project-classifier` skill or `validate-project-classification.py`;
- Auteur code search found no live consumer of `project-classifier` outside the
  vendored skill itself and `skills/VENDORED.yaml`;
- references to `validate-project-classification` outside historical
  review/design evidence are limited to the vendoring manifest, validator
  harness, and its fixture.

Disposition: Auteur does not continue to support this legacy vendored
responsibility. The coherent repair is retirement, not inventing a new local
validator contract.

## Implemented in this branch

- pin `skills/VENDORED.yaml` to upstream `1458f921...` as the first canonical
  comparison baseline;
- preserve the old mixed snapshot as historical, explicitly non-retrospective
  provenance;
- remove `project-classifier` from the supported skill inventory;
- remove `validate-project-classification.py` from the supported script
  inventory;
- remove the project-classifier skill/template, validator, and fixture;
- remove the validator harness's classifier-specific signature and valid-only
  exceptions;
- record retained upstream-absent compatibility surface explicitly instead of
  implying byte identity.

## Deliberately deferred

`workflow-orchestrator` is not renamed or removed in this slice. Unlike project
classification, it still has live references across vendored skills and
validators. Current upstream uses `workflow-planner`; reconciling that boundary
is a separate migration and must not be smuggled into the first-baseline pin.

Other upstream-absent legacy components recorded in
`retained_legacy_deviations` are likewise preserved pending responsibility-level
reconciliation. No current-era excluded component is imported merely because it
exists upstream.

## Work claim

```text
implemented:
  - first canonical upstream comparison baseline: 1458f9210c79336175878b8527ed7ecba1e0b6a3
  - legacy project-classification responsibility retired coherently
  - retained compatibility deviations made explicit

mechanically demonstrated before publication:
  - repository tree/manifest reconciliation via connected GitHub state
  - project-classification live-code references reduced to historical evidence only

pending deterministic validation:
  - scripts/verify_vendored_contract.py
  - scripts/test-validators.py
  - scripts/validate-repo.py / scripts/check.py as exercised by CI

not claimed:
  - historical snapshot retrospectively pinned
  - every retained vendored file byte-matches upstream
  - workflow-orchestrator migration completed
  - full Sensemaking upgrade
  - Workflow v1 started
```

## Finding-specific closure condition for #63

#63 may be closed only after branch/PR validation demonstrates that removing the
unsupported capability leaves the vendoring contract and Auteur verification
stack coherent. A generic green check is supporting evidence; the finding-
specific claim is that the contradictory project-classification verification
contract no longer exists because that unsupported responsibility is no longer
part of Auteur's supported vendored subset.
