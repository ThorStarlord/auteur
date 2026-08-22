# Premise-to-StoryIdentity Stress Simulation v1.5 Learning Synthesis

**Status:** `INTERNAL SIMULATION EVIDENCE`

This document synthesizes the six v1.5 synthetic agent rehearsals recorded in
the [v1.5 registry](premise-to-story-identity-stress-simulation-v1-5.md),
including [run 23](premise-to-story-identity-stress-simulation-v1-5-runs/stress-v15-primary-revision-23.md).
It is not human participant research, creative-beginner validation, usability
validation, or product validation.

## Purpose and boundary

V1.5 tested whether an enforced authority gate could withhold Identity before
primary-thread authorization, require explicit `PROPOSED / NOT CANON` status,
support recovery, and preserve author-selected revisions. This synthesis asks
what the run 23 revision path adds and what remains untested before any later
human research.

The semantic model remains governed by
[Narrative Architecture](../narrative-architecture.md): Identity contains
commitments, Structure contains plans, and Book is a scope rather than a
semantic layer. The settled system/product distinction follows the
[Opinionated Narrative Engine](../opinionated-narrative-engine.md). The
research framing follows
[Auteur Product Design Research](product-design-research.md). The earlier
[v1.2 learning synthesis](premise-to-story-identity-stress-simulation-learning-synthesis.md)
provides the baseline candidate invariants; this document records the v1.5
authority-gate extension.

## Evidence set

All six runs used `Protocol v1.5`, `creative-beginner-v1.0`,
`simulation-evaluator-v1.0`, record type `SIMULATION`, zero human participants,
and the same Book-level premise. The full transcripts remain in the
[standalone v1.5 run directory](premise-to-story-identity-stress-simulation-v1-5-runs/).

| Run ID | Observed result | Narrow stress target | Evidence summary |
|---|---|---|---|
| `stress-v15-control-18` | `SIMULATION_PASS` | Valid ordering and explicit proposal status | The route was explicitly authorized before Identity, and the proposal was paraphrased before acceptance. |
| `stress-v15-mutation-order-19` | `SIMULATION_PASS` | Identity attempted before primary authorization | The gate blocked the attempt before Identity exposure and named the next primary-thread decision. |
| `stress-v15-mutation-status-20` | `SIMULATION_PASS` | Missing proposal status after authorization | The gate withheld the proposal until explicit status could be repaired. |
| `stress-v15-mutation-combined-21` | `SIMULATION_PASS` | Invalid ordering and missing status together | The complete invalid packet was blocked before exposure. |
| `stress-v15-recovery-22` | `SIMULATION_PASS` | Safe stop followed by corrected continuation | Explicit authorization, labeled proposal, bounded revision, acceptance, and next decision completed in sequence. |
| `stress-v15-primary-revision-23` | `SIMULATION_PASS` | Author rejects the recommendation and revises the primary thread | The recording-recovery thread became primary only after explicit author revision; the route remained important secondary context. |

Aggregate result: six `SIMULATION_PASS`, three injected mutations detected
before exposure, and two successful recovery paths. These are synthetic
protocol outcomes, not a success rate for people.

## Settled boundaries and open hypotheses

The following boundaries were treated as settled during the simulation:

- a recommendation is not an author commitment;
- an accepted `StoryIdentity` is a Layer 1 author commitment;
- proposals and canon remain distinct until explicit author acceptance;
- Book-level Identity work must not be presented as Chapter, Scene,
  Realization, or Expression work;
- authorial authority must be preserved for Identity-level changes.

The following remain product-design hypotheses or research questions:

- whether authors understand the distinction between recommendation, revision,
  authorization, proposal, and canon;
- whether a revised primary thread should automatically invalidate prior
  proposals;
- which visible evidence best shows that a proposal reflects the latest author
  decision;
- whether stale-proposal detection should block presentation or invite an
  explicit repair decision;
- which product surface could expose these states without adding unnecessary
  cognitive load.

## Observations

- Run 23 shows that rejecting a recommendation can be a coherent success path;
  the persona supplied an alternative primary thread instead of being pushed
  toward the facilitator's recommendation.
- The route recommendation and the author-selected recording primary were
  distinguishable in the transcript.
- The route remained visible as an important secondary intention after the
  primary-thread revision.
- The resident-authority and hopeful constraints remained visible after the
  revision and were strengthened through one bounded proposal revision.
- The proposal appeared only after explicit authorization and carried
  `PROPOSED / NOT CANON` status.
- The persona paraphrased the revised primary, secondary intention, and
  authority boundary before accepting the revised proposal.
- Every v1.5 run ended with either a safe-stop continuation decision or a next
  creative decision.
- The v1.5 gate tests ordering and status, but the existing runs do not yet
  test whether the content of a validly labeled proposal matches the latest
  author-selected primary thread.

## Interpretations

The v1.5 gate appears internally coherent for authority ordering, visible
proposal status, safe stops, and recovery in this prepared premise. Run 23
also suggests that the gate should treat an explicit author revision as the
authoritative replacement for a recommendation rather than as a minor edit to
the recommendation.

The evidence leaves a content-alignment gap. A proposal can satisfy the
ordering and status checks while still containing an outdated primary thread.
That is a protocol question, not a semantic-architecture conclusion. Run 24
tested this stale-proposal mutation under unchanged v1.5 materials and kept
evaluator detection separate from persona comprehension and ordinary protocol
classification. The resulting v1.6 protocol added a pre-exposure alignment
gate and tested primary, secondary, constraint, and repeated-revision drift.

## Candidate interaction invariants

These are candidates for protocol and later product-design testing. They are
not new semantic layers, runtime rules, schemas, or approved implementation
requirements.

| Candidate invariant | V1.5 evidence | What would disconfirm it |
|---|---|---|
| Recommendation is not authorization. | Run 23 allowed the persona to reject the route recommendation before any Identity proposal. | A packet treats recommendation display as author acceptance, or the evaluator cannot identify the author action. |
| Author rejection or revision is a valid success path. | Run 23 classified an explicit revision and later acceptance as `SIMULATION_PASS`. | The flow forces acceptance, loses the alternative, or treats principled rejection as abandonment. |
| The latest authorized primary thread supersedes the recommendation. | Run 23 recorded the recording-recovery thread as the authorized primary. | A later proposal or decision silently restores the rejected recommendation. |
| Secondary intentions remain visible after primary revision. | Run 23 retained the route as an important secondary goal. | The rejected recommendation disappears without disposition, or the secondary goal is silently demoted. |
| Identity proposals align with the latest authorized direction. | Run 23's corrected proposal matched the recording-centered primary; this remains a targeted invariant for the next mutation. | A validly labeled proposal still presents the old primary and the flow fails to block, invalidate, or repair it. |
| Stale proposals require rejection, invalidation, or regeneration. | The need is inferred from the revision path; v1.5 has not yet tested the stale case. | A stale proposal is accepted as if it reflected the latest author decision. |
| Proposal and canon remain separate. | Runs 18 and 22-23 used explicit status and paraphrase before acceptance. | The persona treats a proposal as settled without explicit authorization. |
| Every blocked or completed flow ends with a next decision. | All six runs supplied a safe-stop continuation or creative next decision. | The author is left without an actionable next decision. |

## Candidate future Auteur capabilities

If later human research supports these observations, Auteur might eventually
need capabilities such as:

1. Separate records for system recommendation, author action, and selected
   primary thread.
2. Authorization provenance attached to the selected primary decision.
3. A preservation map that carries the rejected recommendation's remaining
   secondary, deferred, or unresolved disposition.
4. A proposal-alignment check that compares the proposed Identity primary with
   the latest authorized primary decision.
5. Automatic invalidation or regeneration of a stale proposal after an author
   revision, with an explicit repair decision when needed.
6. A before/after commitment view for bounded revisions.
7. Safe-stop and next-decision states that preserve forward motion without
   presenting stale or unauthorized Identity content.

These are product-design hypotheses only. They do not authorize implementation,
choose a CLI, TUI, browser, editor, or other surface, or modify the canonical
architecture.

## Limitations

The six runs use one frozen premise, one synthetic persona version, one
synthetic evaluator version, and no human participants. The same agent family
may shape the persona and evaluator, creating shared blind spots. The packets
were prepared for the protocol and do not measure human comprehension,
creative ownership, accessibility, emotional response, long-term retention,
or continued creative work.

Run 23 demonstrates one author-selected reversal, not general preference for
the recording-centered direction. The all-pass result may reflect shared
assumptions between packet author, persona, and evaluator. A stale proposal can
also be detected by an evaluator without being understandable to a human
author; those outcomes must remain separate.

## Decision and next experiment

**Decision:** v1.5 is internally coherent for the tested authority-gate
behavior and remains suitable for bounded human-research planning, subject to
human validation. Run 24 confirmed that content alignment after author
revision was a separate unresolved coverage gap; it was not retroactively
folded into the v1.5 gate result.

The append-only
`stress-v15-mutation-stale-primary-24` run recorded the gap: a validly labeled
but stale proposal could reach the persona under v1.5. The v1.6 alignment suite
then tested pre-exposure blocking, repair, and repeated-revision alignment.
Its registry records the synthetic freeze decision and the remaining boundary:
the protocol is ready for later human research planning, not human validation.

This document records synthetic protocol learning only. Human evidence remains
reserved for `docs/research/premise-to-story-identity-findings.md`.
