# Stabilization verification — R06

**Date:** 2026-11-16
**Base:** `41b37fa5` (R02/R05 in #588, R03/R04 in #589)
**Method:** each original finding is re-tested against the repaired implementation. Limitations are recorded as tests rather than prose, so they cannot be quietly forgotten.

## Dispositions

| Original finding | Disposition | Evidence |
|---|---|---|
| Agent-Series-only `derived` inherited claim admitted | **Verified repaired** | `test_the_original_failure_is_prevented` — the exact T10 shape now raises with the element named |
| Author-sourced `derived` claims stay usable | **Verified repaired** | `test_a_claim_backed_by_author_source_may_be_asserted` (R02 suite) |
| Agent-proposed invention remains available | **Verified repaired** | `test_agent_proposed_creative_material_remains_available` — admitted and reported as `working_series_proposal`, `author_grounded: false` |
| Resume omits objective and premise status | **Verified repaired** | `test_a_genuinely_fresh_process_recovers_objective_and_premise_status` — a separate process, not two calls in one interpreter |
| Prose-only host-agent schema | **Verified repaired** | R03/R04 suites; contract bound into the request fingerprint and tamper-detected |
| Historical requests keep identity | **Verified repaired** | `test_a_request_without_a_contract_keeps_its_historical_fingerprint`; `test_a_historical_packet_without_the_key_still_loads` |

## Residual limitation — recorded, not solved

**Reference validity is not semantic support.** A claim may cite a real author `source_item` that does not actually entail it.

`test_known_limitation_a_cited_but_unrelated_author_source_still_passes` demonstrates it: an invented founding council citing `book-2-source` is admitted with `source_basis: author_source`, `author_grounded: true`, even though the source says nothing about a council.

The repair removes the *silent* path (citing only agent proposals) but does not establish entailment, and JSON Schema cannot express it. Building a semantic-support detector would be a new capability, not a repair, and would risk a false authority model. The honest state is: reference validity is enforced; claim support is not.

## Incidental discovery

`ArchitectureCandidate` contains **two different `role` enums**:

- `GenreContract.role` = `governing | supporting | tertiary | local`
- `GenreParticipation.role` = `governing | locally_dominant | supporting | background`

They overlap but disagree. The historical host agent used `GenreParticipation`'s vocabulary on `GenreContract` — an understandable mistake given the near-collision. The machine-readable contract now makes the distinction explicit, but the vocabulary itself remains a usability trap. Recorded for D01-style follow-up; not changed here, because renaming a production enum is a separate decision.

## What R06 does not cover

The R03/R04 row of the matrix was verified mechanically. Whether the contract actually reduces rejections under authentic execution is R07's question, not R06's.
