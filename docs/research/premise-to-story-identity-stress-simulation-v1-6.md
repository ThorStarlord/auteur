# Premise-to-StoryIdentity Stress Simulation v1.6 Registry

**Status:** internal simulation evidence

This registry records synthetic agent rehearsals of the v1.6 enforced
proposal-alignment protocol. Agent runs are not human participant evidence, do
not validate creative-beginner behavior, and do not authorize runtime or
product implementation.

## Purpose

Run 24 showed that v1.5 ordering and status checks could allow a stale proposal
to reach the persona. V1.6 adds an alignment gate that compares the proposed
Identity with the latest author-authorized primary thread, secondary
dispositions, and observable constraints before exposure.

## Run configuration

| Field | Fixed value |
| --- | --- |
| Protocol | `v1.6` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Evidence layout | Registry plus standalone full-transcript run records |
| Frozen premise basis | v1.2-v1.5 primary-secondary premise |

## Frozen premise

> Six weeks before a mountain valley's only night bus is sold to a private
> operator, a young mechanic wants to keep the route serving isolated villages,
> while her older brother wants to recover their late mother's recordings about
> a mining company that poisoned the river. The operator will preserve the route
> only if the recordings remain private. The story must stay hopeful, and no one
> may speak for the villages or accept a settlement without the residents
> choosing the public position themselves.

## Run index

The standalone records are the authoritative full transcripts. Alignment
detection, exposure phase, recovery, and ordinary classification are reported
separately.

| Run | Scenario | Record | Gate result | Alignment result | Detection phase | Recovery | Classification |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `stress-v16-control-25` | Valid primary, secondary, constraint, ordering, and status alignment | [run 25](premise-to-story-identity-stress-simulation-v1-6-runs/stress-v16-control-25.md) | `IDENTITY_ACCEPTED` | `N/A` | `N/A` | `N/A` | `SIMULATION_PASS` |
| `stress-v16-mutation-primary-26` | Rejected route recommendation remains proposal primary | [run 26](premise-to-story-identity-stress-simulation-v1-6-runs/stress-v16-mutation-primary-26.md) | `GATE_BLOCKED` then `IDENTITY_ACCEPTED` | `DETECTED` | `BLOCKED_BEFORE_EXPOSURE` | `RECOVERY_PASS` | `SIMULATION_PASS` |
| `stress-v16-mutation-secondary-27` | Important recordings goal is dropped or demoted | [run 27](premise-to-story-identity-stress-simulation-v1-6-runs/stress-v16-mutation-secondary-27.md) | `GATE_BLOCKED` then `IDENTITY_ACCEPTED` | `DETECTED` | `BLOCKED_BEFORE_EXPOSURE` | `RECOVERY_PASS` | `SIMULATION_PASS` |
| `stress-v16-mutation-constraint-28` | Resident-authority constraint is weakened or omitted | [run 28](premise-to-story-identity-stress-simulation-v1-6-runs/stress-v16-mutation-constraint-28.md) | `GATE_BLOCKED` then `IDENTITY_ACCEPTED` | `DETECTED` | `BLOCKED_BEFORE_EXPOSURE` | `RECOVERY_PASS` | `SIMULATION_PASS` |
| `stress-v16-mutation-repeated-revision-29` | Intermediate proposal becomes stale after a second primary-thread revision | [run 29](premise-to-story-identity-stress-simulation-v1-6-runs/stress-v16-mutation-repeated-revision-29.md) | `GATE_BLOCKED` then `IDENTITY_ACCEPTED` | `DETECTED` | `BLOCKED_BEFORE_EXPOSURE` | `RECOVERY_PASS` | `SIMULATION_PASS` |

The classifications are transcript-based protocol rehearsal outcomes, not
claims about human users.

## Aggregate alignment findings

- The control aligned the recommendation, author decision, proposed primary,
  secondary intention, and resident-authority constraint before presentation.
- The primary mutation was blocked because the proposal primary did not match
  the latest author-authorized primary.
- The secondary mutation was blocked because the proposal changed an important
  secondary intention without an author decision.
- The constraint mutation was blocked because the proposal no longer expressed
  the non-negotiable resident-authority boundary as observable behavior.
- The repeated-revision mutation was blocked because its intermediate proposal
  no longer matched the latest author-authorized primary decision.
- All three defective proposals were withheld before persona exposure.
- The repeated-revision proposal was also withheld before exposure and then
  invalidated before a corrected proposal was generated.
- Each mutation used a safe stop, a concrete repair decision, a fresh
  alignment check, and a corrected proposal marked `PROPOSED / NOT CANON`.
- No persona treated a proposal as canon prematurely, and no facilitator
  supplied substantive story content during recovery.
- Persona and evaluator roles remained separate.

## Recovery findings

The mutation runs demonstrate that `ALIGNMENT_MISMATCH` can be handled as a
recoverable `GATE_BLOCKED` reason. The invalid proposal is not accepted, the
author's existing commitments remain visible, and the corrected proposal is
shown only after the alignment ledger is repaired and rechecked.

The recovery result supports internal protocol executability. It does not show
that human authors would understand the mismatch category, prefer regeneration,
or retain the same commitments without additional support.

Run 29 adds evidence that the alignment ledger must compare a proposal with the
latest authorized decision, not merely the immediately preceding proposal or
an intermediate revision. Its recovery path explicitly invalidated the
intermediate proposal before continuing.

## Product hypotheses, not approved requirements

If later human research supports these observations, Auteur might eventually
need:

- authorization provenance linking recommendations, author actions, and the
  latest selected commitments;
- a proposal-alignment check before Identity rendering;
- stale-proposal invalidation or regeneration after author revision;
- preservation of secondary and constraint dispositions across revisions;
- before/after commitment views for repair and bounded revision.

These remain product-design hypotheses. This simulation does not authorize
implementation, choose a CLI, TUI, browser, editor, or other product surface,
or modify the semantic architecture.

## Limitations

The five runs use one frozen premise, one synthetic persona version, one
synthetic evaluator version, and no human participants. The same agent family
may shape packet preparation, persona behavior, and evaluator judgment. The
materials test prepared alignment cases and do not measure human comprehension,
creative ownership, accessibility, long-term retention, or continued creative
work.

The suite tests one primary, one secondary, one authority constraint, and two
successive primary revisions. It does not establish behavior under three or
more revisions, multiple secondary dispositions, conflicting constraints, or
different vocabulary. A clean result supports only internal protocol
executability.

## V1.6 freeze decision

**Decision: READY TO FREEZE FOR LATER HUMAN RESEARCH, SUBJECT TO HUMAN
VALIDATION.**

The control is `SIMULATION_PASS`; all four mutations are detected and blocked
before exposure; corrected proposals align with the latest author decisions;
no stale, demoted, or weakened commitment reaches the persona; each recovery
completes without substantive coaching; no persona treats Identity as canon
prematurely; proposal/canon status remains explicit; and persona/evaluator
roles remain separate.

This is a protocol-readiness decision only. It does not convert synthetic
evidence into human findings or authorize product implementation. Human
evidence remains reserved for
`docs/research/premise-to-story-identity-findings.md`.

## Related evidence

- [v1.6 protocol](premise-to-story-identity-stress-simulation.md)
- [v1.6 learning context](premise-to-story-identity-stress-simulation-v1-5-learning-synthesis.md)
- [v1.5 registry](premise-to-story-identity-stress-simulation-v1-5.md)
- [v1.5 stale-proposal run](premise-to-story-identity-stress-simulation-v1-5-runs/stress-v15-mutation-stale-primary-24.md)
- [historical v1.2 findings archive](premise-to-story-identity-stress-simulation-findings.md)
