# Reconciliation — Auteur vendored Sensemaking contract (2026-08-14)

## Work claim

```text
implemented:
  - skills/VENDORED.yaml — machine-readable vendoring contract: source
    repository + revision (recorded honestly as UNRECORDED, historical
    snapshot predating the workflow-planner rename and probe engine),
    intentional included subset (16 skills, 24 scripts, 2 framework docs),
    intentional exclusions (5 current-era components), known
    characteristics (the vendored validate-repo warnings), update policy
    (manual + gated; record upstream SHA at next sync), validation
    expectations
  - scripts/verify_vendored_contract.py — drift check: included paths must
    exist, excluded components must stay absent; exit 0/1/2; path-value
    validation (repo-relative only); malformed-YAML handled
  - scripts/check.py — drift check wired into the gate (CHECK_COMMANDS)
  - tests/test_vendored_contract.py — 7 focused tests (manifest load,
    malformed/missing manifest, clean contract, missing-included drift,
    excluded-present drift, real-tree clean)

mechanically demonstrated:
  - `python scripts/verify_vendored_contract.py` -> VENDORED CONTRACT: OK
    (included present, excluded absent) against the real tree
  - drift detection: missing included file -> exit 1; excluded component
    present -> exit 1 (unit-tested)
  - gate: test-validators 26/26 PASS; validate-repo PASS (known,
    documented warnings); verify-vendored-contract OK; ruff clean
  - focused tests 7/7 passed; security review: no blocking issues (two
    LOW hardening items fixed: path-value validation, malformed-YAML exit)

still interpretive:
  - source.revision = UNRECORDED (honest record of the historical snapshot;
    the upstream SHA is pinned at the NEXT intentional update, per policy)
  - update policy is manual and gated (no automation added by design)

deliberately unchanged:
  - the vendored snapshot content (NO upgrade to current Sensemaking)
  - the vendored validators and their behavior (warnings documented, not
    silenced)
  - scripts/sync_interface_skills.py (covers a different source)
  - product code, routing, Workflow v0, Sensemaking Skills repository
  - no external dependency / distribution architecture introduced

deferred:
  - none within this finding's scope; upstream-SHA pinning occurs at the
    next intentional snapshot update

unresolved:
  - none decision-blocking
```

## Claim-by-claim reconciliation

| Claim | Classification | Evidence |
|---|---|---|
| Vendoring now has an explicit, durable contract | **VERIFIED** | `skills/VENDORED.yaml` committed (ab1d6ee): source, revision, included/excluded lists, update policy, validation expectations |
| Contract matches the real tree | **VERIFIED** | `verify_vendored_contract.py` -> "VENDORED CONTRACT: OK (included present, excluded absent)"; real-tree test asserts clean |
| Gate validates the supported subset | **VERIFIED** | drift check in `check.py` CHECK_COMMANDS; `check.py --skip-pytest` runs it and passes |
| No blind snapshot upgrade | **VERIFIED** | vendored skills/scripts untouched; only manifest + drift check + tests + one gate line added |
| No new external dependency | **VERIFIED** | no dependency/install/distribution changes; vendoring remains in-tree |
| Known vendored-validator warnings documented | **VERIFIED** | `known_characteristics` in the manifest; gate still treats them as warnings |
| Upstream revision pinned | **DISPUTED** (claim not made) | recorded as UNRECORDED by design; pinning deferred to the next intentional update per the manifest's own update policy |

**Omitted:** none material.

## Repair verification (finding-specific)

Original finding (evidence 0022 Auteur brief, 2026-08-14): "Auteur
contains a partial/diverging vendored subset of Sensemaking Skills and its
local framework validation reports inconsistencies; no vendoring contract,
provenance, or sync mechanism documented."

Owner decision (2026-08-14): curated vendored subset is intentional;
implement a vendoring contract (source revision, supported subset,
exclusions, sync expectations) and make the gate validate the supported
subset.

```text
acquisition_status: SUCCEEDED
  (drift check executed on the real tree; focused tests run; gate run)

observation (finding-specific):
  - the vendored relationship now has an explicit, machine-enforced
    contract (skills/VENDORED.yaml + verify-vendored-contract.py in the
    gate); included paths verified present, excluded components verified
    absent
  - the hidden dependency is now explicit and governable; the known
    validator warnings are documented characteristics, not silent drift

disposition: closed
  (the "hidden, ungoverned vendoring" defect is resolved. The snapshot
   content itself is intentionally unchanged per the owner decision, so
   no upgrade/alignment-of-content claim is made or implied)
```

Note: generic green (gate PASS) is not the closure proof; the closure
proof is the committed contract + the mechanically verified included/
excluded state, which this record cites.
