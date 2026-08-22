# Premise-to-StoryIdentity Stress Simulation v1.5 Registry

**Status:** internal simulation evidence

This registry records synthetic agent rehearsals of the v1.5 enforced
authority-gate protocol. Agent runs are not human participant evidence, do not
validate creative-beginner behavior, and do not authorize runtime or product
implementation.

## Purpose

V1.4 showed that detecting an authority defect after an invalid Identity had
been presented was insufficient. V1.5 tests a protocol-level gate that
withholds invalid Identity presentation before persona exposure, records the
blocked reason, and provides a concrete recovery decision. The scope remains
Book-level premise to proposed `StoryIdentity`.

## Run configuration

| Field | Fixed value |
| --- | --- |
| Protocol | `v1.5` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Evidence layout | Registry plus standalone full-transcript run records |
| Frozen premise basis | v1.2-v1.4 primary-secondary premise |

## Frozen premise

> Six weeks before a mountain valley's only night bus is sold to a private
> operator, a young mechanic wants to keep the route serving isolated villages,
> while her older brother wants to recover their late mother's recordings about
> a mining company that poisoned the river. The operator will preserve the route
> only if the recordings remain private. The story must stay hopeful, and no one
> may speak for the villages or accept a settlement without the residents
> choosing the public position themselves.

## Run index

The standalone records are the authoritative full transcripts. The result and
gate columns are reported separately: an ordinary protocol classification does
not conceal whether a mutation was blocked, exposed, or recovered.

| Run | Scenario | Record | Gate result | Mutation/gate detection | Classification |
| --- | --- | --- | --- | --- | --- |
| `stress-v15-control-18` | Valid gate and explicitly labeled proposal | [run 18](premise-to-story-identity-stress-simulation-v1-5-runs/stress-v15-control-18.md) | `IDENTITY_ACCEPTED` | `N/A` | `SIMULATION_PASS` |
| `stress-v15-mutation-order-19` | Attempted Identity before primary authorization | [run 19](premise-to-story-identity-stress-simulation-v1-5-runs/stress-v15-mutation-order-19.md) | `GATE_BLOCKED` before exposure | `DETECTED` | `SIMULATION_PASS` |
| `stress-v15-mutation-status-20` | Missing explicit proposal status after authorization | [run 20](premise-to-story-identity-stress-simulation-v1-5-runs/stress-v15-mutation-status-20.md) | `GATE_BLOCKED` before exposure | `DETECTED` | `SIMULATION_PASS` |
| `stress-v15-mutation-combined-21` | Invalid ordering and missing status together | [run 21](premise-to-story-identity-stress-simulation-v1-5-runs/stress-v15-mutation-combined-21.md) | `GATE_BLOCKED` before exposure | `DETECTED` | `SIMULATION_PASS` |
| `stress-v15-recovery-22` | Safe stop, corrected authorization, and continuation | [run 22](premise-to-story-identity-stress-simulation-v1-5-runs/stress-v15-recovery-22.md) | `IDENTITY_ACCEPTED` after recovery | `RECOVERY_PASS` | `SIMULATION_PASS` |
| `stress-v15-primary-revision-23` | Author rejects the recommendation and revises the primary thread during recovery | [run 23](premise-to-story-identity-stress-simulation-v1-5-runs/stress-v15-primary-revision-23.md) | `IDENTITY_ACCEPTED` after explicit revision | `RECOVERY_PASS` | `SIMULATION_PASS` |
| `stress-v15-mutation-stale-primary-24` | Proposal retains the rejected recommendation after primary-thread revision | [run 24](premise-to-story-identity-stress-simulation-v1-5-runs/stress-v15-mutation-stale-primary-24.md) | `IDENTITY_PROPOSED` with stale content exposed | `DETECTED` after exposure | `SIMULATION_PASS` |

The classifications above are the results of the transcripts in the linked
records. They are protocol rehearsal outcomes, not claims about human users.

Run 23 is an append-only extension of the v1.5 registry. It does not change
the frozen mutation matrix or any earlier run. It tests whether the gate can
authorize an author-selected revision rather than treating the recommended
primary direction as mandatory.

Run 24 is an append-only diagnostic extension. It keeps the v1.5 ordering and
status materials unchanged and tests a separate content-alignment question:
whether a validly labeled proposal reflects the latest authorized primary
thread.

## Aggregate findings

### Gate behavior

The valid control records explicit author acceptance of the route as the
primary thread before showing any Identity fields. The proposal is visibly
marked `PROPOSED / NOT CANON`, the persona paraphrases its main commitments,
and acceptance occurs only after that paraphrase.

The three mutation runs keep the attempted defective material evaluator-only.
The persona sees a safe-stop explanation and the required next decision, but no
invalid Identity fields. The order and status checks operate independently, so
an explicit status cannot repair premature ordering and a valid order cannot
repair missing status.

Run 24 passed the ordering and status checks but exposed a stale primary
commitment. The persona and evaluator detected the mismatch, and the persona
rejected the proposal without treating it as canon. This confirms that v1.5's
current gate does not yet block content misalignment before exposure.

### Recovery path

Run 22 demonstrates that `GATE_BLOCKED` is a recoverable protocol state rather
than an implicit rejection or a forced author decision. The flow names the
missing authorization, obtains the author's explicit primary-thread decision,
rechecks the corrected packet, shows the proposal with explicit status, and
continues through paraphrase, one bounded revision, acceptance, and a next
creative decision.

The recovery transcript is evidence that the safe stop can preserve author
authority while maintaining forward motion. It is not evidence that human
authors would understand or prefer this flow.

### Cross-run evaluator observations

- No Identity fields reached the persona in the three mutation runs.
- No persona treated a pre-canon proposal as canon.
- The blocked runs each stated what was unavailable, what decision or repair
  was required, and what the author could decide next.
- Run 23 preserved author authority when the persona rejected the recommended
  route as primary and explicitly revised the recording-recovery thread into
  the primary position.
- Run 24 separated proposal status from proposal alignment: a proposal can be
  visibly provisional and correctly ordered while still retaining a rejected
  primary direction.
- Run 24's persona independently detected and rejected the stale proposal, but
  that does not demonstrate pre-exposure protection or human comprehension.
- The control and recovery runs retained the recording-recovery goal as an
  important secondary intention while the route was selected as primary.
- The resident-authority constraint remained observable: the proposal did not
  let a protagonist speak for the villages or accept a settlement for them.
- Persona and evaluator roles remained separate; evaluator-only defect details
  were not included in participant-facing packets.
- The evaluator classified ordinary protocol behavior separately from mutation
  detection and recovery.

## Product hypotheses, not approved requirements

If later human research supports these observations, Auteur might eventually
need capabilities such as:

- an enforced display-state gate that prevents premature Identity rendering;
- a required, visible proposal-status field;
- authorization provenance attached to the primary-thread decision;
- proposal-to-authorization alignment checking with stale-proposal invalidation
  or regeneration;
- explicit safe-stop and recovery states with a next-decision prompt.

These are product-design hypotheses only. This simulation does not authorize
implementation, choose a CLI, TUI, browser, editor, or other surface, and does
not modify the semantic architecture.

## Limitations

The seven v1.5 records use one frozen premise, one synthetic persona version, one
synthetic evaluator version, and no human participants. The same agent family
may shape both the persona and evaluator behavior, creating shared blind spots.
The packets are authored for the protocol and do not measure long-term
comprehension, creative ownership, accessibility, emotional response, or
behavior under ordinary product conditions. A clean gate result therefore
supports only internal protocol executability.

The full transcripts are retained in the standalone records. This registry is
an index and synthesis, not a replacement for those records. Future v1.5
rehearsals must use append-only run numbers and a new protocol version if the
materials or gate behavior change.

## V1.5 freeze decision

**Decision: READY TO FREEZE FOR LATER HUMAN RESEARCH, SUBJECT TO HUMAN
VALIDATION.**

The control is `SIMULATION_PASS`; all three injected mutations are reported as
blocked before Identity exposure and `DETECTED`; no persona treats Identity as
canon prematurely; every blocked flow has a safe stop and next decision; the
recovery run completes without substantive coaching; proposal status remains
explicit after recovery; run 23 authorizes an explicit primary-thread revision;
and persona/evaluator roles remain separate.

This decision freezes the research protocol for a bounded human study only. It
does not convert synthetic evidence into human findings or authorize product
implementation. Human evidence, if collected later, belongs in
`docs/research/premise-to-story-identity-findings.md`, which remains reserved
for that purpose.

### Post-freeze diagnostic note

Run 24 does not retroactively change the freeze decision for the tested v1.5
authority gate. It records an unresolved content-alignment gap for future
protocol design: a stale proposal can pass ordering and status checks and reach
the persona. The run's `DETECTED` result came after exposure, so it is not
evidence of an enforced stale-content gate.

## Related evidence

- [v1.5 registry](premise-to-story-identity-stress-simulation-v1-5.md)
- [v1.5 protocol](premise-to-story-identity-stress-simulation.md)
- [v1.5 learning synthesis](premise-to-story-identity-stress-simulation-v1-5-learning-synthesis.md)
- [v1.4 registry](premise-to-story-identity-stress-simulation-v1-4.md)
- [v1.4 historical run records](premise-to-story-identity-stress-simulation-v1-4-runs/)
- [historical v1.2 findings archive](premise-to-story-identity-stress-simulation-findings.md)
