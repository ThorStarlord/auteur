# Premise-to-StoryIdentity Human-Research Readiness

**Status:** `PREPARATION ONLY — NO HUMAN SESSIONS COMPLETED`

**Readiness decision:** **READY FOR FUTURE SESSION PREPARATION; NOT READY TO CLAIM HUMAN VALIDATION.**

This addendum prepares the approved
[Premise-to-StoryIdentity Research Experiment](premise-to-story-identity-experiment.md)
for eventual human execution. It does not run sessions, recruit participants,
collect consent, store human data, create human findings, or implement Auteur
behavior.

## Evidence boundary

The [v1.6 stress-simulation registry](premise-to-story-identity-stress-simulation-v1-6.md)
and [run 29](premise-to-story-identity-stress-simulation-v1-6-runs/stress-v16-mutation-repeated-revision-29.md)
are internal synthetic protocol evidence. They demonstrate protocol rehearsal
only and are not human participant evidence, creative-beginner validation,
usability validation, or product validation. They do not count toward the
human study's 5-8 participant stopping rule.

The settled system boundary follows
[Narrative Architecture](../narrative-architecture.md): Identity is a Layer 1
authority and Book is a scope, not a semantic layer. The product-definition
distinction follows the
[Opinionated Narrative Engine](../opinionated-narrative-engine.md). The
research framing follows
[Auteur Product Design Research](product-design-research.md).

## Frozen human-study scope

The approved human experiment remains unchanged in scope:

- one-on-one moderated sessions;
- approximately 45-60 minutes per session;
- creative beginners with limited long-form narrative-planning experience;
- the participant's own one-to-three-sentence premise when available;
- a standardized fallback premise only when necessary and explicitly labeled;
- a surface-neutral, facilitator-created proposal packet;
- no invocation of `auteur identity recommend`;
- no runtime, schema, CLI, persistence, or canonical artifact mutation;
- no chapter planning, prose drafting, structural diagnosis, or full five-layer
  disclosure.

The participant may accept, reject, or revise the proposal. A thoughtful
rejection or revision is valid evidence and is not treated as a failed creative
outcome.

## Frozen materials and version control

Before any future session begins, the facilitator must record the exact
versions of:

- the approved [experiment brief](premise-to-story-identity-experiment.md);
- the [facilitator guide](premise-to-story-identity-facilitator-guide.md);
- the v1.6 alignment protocol and registry;
- the proposal-packet template;
- the private evidence-capture sheet.

The v1.6 simulation protocol is the current synthetic readiness baseline. The
human session flow remains the approved experiment flow, with the manual
alignment checklist below applied before any proposal is shown. Freeze the
facilitator guide, packet template, checklist, and evidence sheet before
session one. If a critical failure requires a material change, increment and
label the human protocol version; do not pool pre-change and post-change
sessions without separate analysis.

### Freeze the facilitator guide

The facilitator guide, proposal template, alignment checklist, and evidence
sheet must be frozen before session one.

## Session flow

Use the same sequence for every future participant:

1. Explain the study, obtain the applicable consent, and assign a participant
   code.
2. Capture the participant's premise verbatim in private external notes.
3. Prepare and present a plain-language reflection.
4. Present one recommended direction, its rationale, and meaningful rejected
   alternatives.
5. Ask the participant to accept, reject, or revise the primary direction.
6. Run the manual v1.6 alignment checklist before displaying any Identity
   fields.
7. Present the compact `PROPOSED / NOT CANON` `StoryIdentity` only after the
   checklist passes.
8. Ask the participant to paraphrase the main commitments.
9. Ask for an explicit accept, reject, or revision decision.
10. Apply at most one author-directed revision with visible before/after
    commitments.
11. Ask for the next useful creative decision and record what remains open.

The facilitator uses neutral prompts only. The facilitator must not supply
narrative reasoning, silently repair a premise, decide the primary thread, or
turn participant evidence into canon.

The manual state sequence is `PRE_IDENTITY` -> `PRIMARY_AUTHORIZED` ->
`IDENTITY_PROPOSED` -> explicit participant decision. If the alignment checklist
fails, remain in `GATE_BLOCKED` until the packet is repaired and rechecked.

## Manual v1.6 alignment checklist

Complete this checklist privately before showing any proposal. Store the
completed checklist outside the repository with the raw session notes.

| Check | Required record |
| --- | --- |
| System recommendation | The direction recommended by the facilitator and its rationale. |
| Author action | `ACCEPT`, `REJECT`, or `REVISE`, in the participant's words where possible. |
| Latest authorized primary | The primary Book-level thread after the participant's latest explicit decision. |
| Secondary intentions | Each important secondary goal and its disposition: preserved, revised, deferred, unresolved, or rejected by the author. |
| Observable constraints | Each non-negotiable constraint and the behavior that would preserve or violate it. |
| Proposal source revision | The decision version or revision from which the packet was prepared. |
| Proposal alignment | Proposed primary, secondary dispositions, and constraints compared with the latest authorized record. |
| Proposal status | Exact visible label: `PROPOSED / NOT CANON`. |

The checklist passes only when:

- the author action is explicit;
- the proposal primary matches the latest authorized primary;
- important secondary intentions retain their authorized dispositions;
- non-negotiable constraints remain observable commitments;
- the packet was prepared from the latest decision revision; and
- the proposal is visibly marked `PROPOSED / NOT CANON`.

Do not show Identity fields while any check is incomplete or mismatched.

## Safe stop and regeneration

When alignment fails, say in plain language:

> This proposal is not available yet because it does not reflect your latest
> decision. We will keep the current decision visible, repair or regenerate the
> proposal, and check it again before you review it.

Then:

1. record the reason without assigning blame to the participant;
2. show no fields from the unaligned proposal;
3. ask the participant to confirm the next repair decision;
4. invalidate or set aside the earlier packet;
5. prepare a corrected packet from the latest authorized record;
6. repeat the alignment checklist; and
7. show the corrected proposal only with `PROPOSED / NOT CANON` status.

The participant may then paraphrase, reject, revise, or accept the corrected
proposal. A safe stop, rejection, or revision is evidence and must not be
silently classified as abandonment.

## Evidence-capture template

Completed sheets remain external to the repository. Only anonymized aggregate
synthesis may enter the later human findings document.

```text
Participant code:
Human protocol version:
Date:
Fallback premise used: YES / NO

System facts
- Packet version:
- Alignment checklist version:
- Proposal source revision:
- Start/end time and time by step:
- Flow completed: YES / NO
- Gate result: PASSED / SAFE_STOP / REGENERATED

Participant statements
- Premise, captured verbatim externally:
- Recommendation response: ACCEPT / REJECT / REVISE
- Latest authorized primary and rationale:
- Secondary intentions and dispositions:
- Observable constraint paraphrase:
- StoryIdentity paraphrase:
- Accept/reject/revise decision and rationale:
- Commitment to preserve:
- Commitment to revise:
- Next useful creative decision:

Observed behavior
- Primary thread clear: YES / PARTIAL / NO
- Important intentions preserved: YES / PARTIAL / NO
- Proposal/canon distinction: CLEAR / UNCLEAR
- Alignment understood: YES / PARTIAL / NO / NOT TESTED
- Main commitments understood: YES / PARTIAL / NO
- Hesitation, confusion, or abandonment:

Facilitator intervention
- Neutral prompts used:
- Safe-stop wording used:
- Substantive coaching required: YES / NO
- Rescue or unplanned explanation:

Researcher interpretation
- Classification: SUCCESS / FAILURE / INCONCLUSIVE
- Failure category, if any:
  PROPOSAL_MISMATCH / PREMISE_PRESERVATION / ALIGNMENT /
  CONSTRAINT_COMPREHENSION / AUTHORITY_BOUNDARY / COMPREHENSION /
  FACILITATION_RESCUE / TASK_FRICTION / OTHER
- Evidence supporting classification:
- Follow-up question or material change suggested:
```

Keep system facts, participant statements, observations, facilitator actions,
and researcher interpretation separate. Do not use the template to place raw
participant data in the repository.

## Participant-level classification

Classify a session as `SUCCESS` only when the participant:

- makes an informed accept, reject, or revision decision;
- accurately explains the main commitments;
- distinguishes proposal from accepted canon;
- can identify what to preserve or revise;
- understands or can inspect whether the proposal reflects the latest decision;
- identifies the next useful creative decision; and
- does so without substantive facilitator coaching.

Classify as `FAILURE` when the participant:

- treats a proposal as accepted canon;
- cannot identify the decision or commitments after one neutral clarification;
- loses premise intent without noticing;
- cannot distinguish the latest author decision from an earlier recommendation;
- requires facilitator rescue; or
- abandons because the concepts or authority boundary remain unclear.

Classify as `INCONCLUSIVE` when the session is interrupted, a protocol
deviation prevents interpretation, the fallback materially changes the task,
or evidence is insufficient to distinguish comprehension from task friction.

Report proposal mismatch, alignment failure, comprehension, authority-boundary
confusion, facilitation rescue, and task friction separately.

## Stopping rules and post-session decision

Use the approved human-study stopping rules:

- run at least five sessions;
- pause after two consecutive critical failures of the same kind;
- stop at five if at least four succeed and the final two contain no critical
  failure;
- continue to a maximum of eight sessions when results are mixed or new
  failures appear; and
- classify the experiment as failed or inconclusive after eight if the success
  threshold is unmet.

After sessions are complete, create the anonymized
`docs/research/premise-to-story-identity-findings.md` document and use it to
decide whether to prototype, revise and repeat, or stop/narrow the product
hypothesis. Do not create that document during preparation or place synthetic
simulation transcripts in it.

## Privacy and repository boundary

- Raw premises, notes, recordings, consent records, names, contact details, and
  participant codes remain outside the repository.
- Do not record audio or video without the applicable explicit consent.
- Store only anonymized aggregate findings in the repository after sessions are
  complete.
- Do not write participant decisions to `story_identity.yaml` or any canonical
  project artifact.
- The human findings document remains absent until human sessions are complete.

Human evidence remains reserved for the post-session findings document.

## Unresolved operational prerequisites

The following decisions must be supplied externally before human sessions begin:

- recruitment source and participant contact process;
- applicable consent process and retention period;
- standardized fallback premise;
- secure external location for raw notes and any recordings; and
- facilitator assignment and conflict-of-interest handling.

This preparation artifact does not infer or authorize any of those decisions.
No recruitment outreach, participant contact, consent collection, or session
execution has occurred.

## Readiness gate

The preparation package is internally ready for future session preparation when
the manual alignment checklist is executable, proposal packets cannot be shown
before alignment passes, revision history and latest authorization are recorded,
safe-stop and regeneration behavior are unambiguous, privacy rules are explicit,
and no human data is stored in the repository.

It is not a claim that human research has begun, that participants are
available, or that Auteur has been validated.

## Related documentation

- [Approved research experiment](premise-to-story-identity-experiment.md)
- [Facilitator guide](premise-to-story-identity-facilitator-guide.md)
- [V1.6 stress-simulation registry](premise-to-story-identity-stress-simulation-v1-6.md)
- [V1.6 repeated-revision run](premise-to-story-identity-stress-simulation-v1-6-runs/stress-v16-mutation-repeated-revision-29.md)
- [Stress-simulation protocol](premise-to-story-identity-stress-simulation.md)
