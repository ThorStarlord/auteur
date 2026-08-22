# Premise-to-StoryIdentity simulation retrospective

Status: `INTERNAL SIMULATION EVIDENCE AND PROCESS RETROSPECTIVE`

This document records cross-version learning from the v1.2 through v1.6
Book-level premise-to-`StoryIdentity` simulations. It is synthetic protocol
evidence only. It is not human participant research, creative-beginner
validation, usability validation, or product validation.

The run registries and standalone transcripts remain the source of truth for
individual results. This document records what the sequence taught us about
the research process, where the returns began to diminish, and when to stop
synthetic testing.

## Evidence base

| Protocol | Records | Main question | Decision recorded |
|---|---:|---|---|
| [v1.2](premise-to-story-identity-stress-simulation-v1-2.md) | 6 | Can the Book-level flow preserve intentions, triage context, express constraints, and stop safely? | Internally coherent enough for adversarial rehearsal. |
| [v1.3](premise-to-story-identity-stress-simulation-v1-3.md) | 5 | Can separate evaluation detect defective packets? | Not ready. Detection did not prevent an author-facing authority failure. |
| [v1.4](premise-to-story-identity-stress-simulation-v1-4.md) | 5 | Do ordering and proposal-status checks prevent premature Identity treatment? | Not ready. The combined defect still reached the persona. |
| [v1.5](premise-to-story-identity-stress-simulation-v1-5.md) | 7 | Can a hard authority gate block invalid Identity presentation and recover safely? | Authority behavior was coherent, but run 24 exposed stale-proposal alignment as a separate gap. |
| [v1.6](premise-to-story-identity-stress-simulation-v1-6.md) | 5 | Can alignment checks block stale, demoted, or weakened proposals before exposure? | Ready for later human-research planning, subject to human validation. |

The sequence contains 28 registry records with run identifiers extending
through `stress-v16-mutation-repeated-revision-29`. Every record has zero
human participants. The [historical findings archive](premise-to-story-identity-stress-simulation-findings.md)
and the [v1.2 learning synthesis](premise-to-story-identity-stress-simulation-learning-synthesis.md)
provide earlier context.

The [human-research readiness addendum](premise-to-story-identity-human-research-readiness.md)
defines the separate preparation path. The [narrative architecture](../narrative-architecture.md),
[opinionated narrative engine](../opinionated-narrative-engine.md), and
[product-design research](product-design-research.md) remain authoritative for
system boundaries and product-design context.

## What changed from v1.2 through v1.6

The revisions were useful when each one answered a new process question.

### v1.2 established the basic rehearsal

The first stress suite tested cognitive load within Book-level scope. It
required the packet to preserve ensemble intentions, separate required context
from deferred context, translate constraints into observable commitments, and
stop when no primary thread was authorized. The suite showed that a manual
packet could execute the intended flow.

This was a protocol-execution result. It did not show that a human author would
understand the packet or value the recommendation.

### v1.3 separated detection from ordinary success

The controlled mutations made an important distinction visible. An evaluator
can detect a defective packet while the persona still experiences an unsafe
interaction. The authority mutation was detected in the evaluator pass, but the
persona treated prematurely shown Identity content as effectively chosen.

The process failure was a missing participant-facing checkpoint. It was not a
reason to blame the persona or evaluator.

### v1.4 tested ordering and status independently

Separating the two checks showed that explicit wording alone could not protect
the author boundary. The combined mutation reproduced premature Identity
treatment even though the evaluator identified both defects.

This changed the question from "Can the evaluator spot the problem?" to "Can
the protocol prevent the problem from reaching the author?"

### v1.5 added a hard authority gate and recovery

The pre-Identity gate withheld invalid content until primary-thread authorization
and explicit proposal status were present. The recovery run showed that a
blocked flow could explain the reason, obtain the missing author decision,
regenerate the packet, and continue.

Run 24 exposed the next process gap. A proposal could pass ordering and status
checks while still naming a rejected primary thread. That gap was kept separate
from the earlier v1.5 results and led to v1.6.

### v1.6 added content alignment

The alignment gate compared the proposed primary, secondary dispositions, and
observable constraints with the latest author-authorized commitments. The
mutation runs blocked defective proposals before persona exposure, repaired the
packets, and rechecked alignment before continuation.

This is the current synthetic readiness baseline. It does not prove that human
authors will notice alignment errors, prefer regeneration, or find the flow
helpful.

## Observations

- The most important failures appeared at the proposal and canon boundary.
- Evaluator detection did not make an author-facing interaction safe.
- Author rejection and revision had to become explicit process events.
- The latest author decision had to supersede an earlier recommendation.
- Secondary intentions and constraints needed explicit dispositions so they
  could not disappear during primary-thread selection.
- A safe stop preserved author authority better than forcing a direction.
- Every blocked or completed flow benefited from an explicit next decision.
- The same frozen premise and synthetic persona/evaluator versions made the
  later rounds comparable, but limited generalization.

## Interpretations

The sequence suggests that the protocol needed a small set of explicit
checkpoints rather than more persuasive wording. The useful checkpoints were:

1. record the author action separately from the recommendation;
2. record the latest authorized commitments;
3. compare the proposal with those commitments before exposure;
4. withhold and repair invalid proposals;
5. show proposal status before asking for acceptance;
6. end blocked and completed flows with a concrete next decision.

The process also showed why evidence categories must remain separate:

- ordinary protocol classification;
- mutation detection;
- detection phase, especially before or after persona exposure;
- persona confusion or premature canon treatment;
- recovery result;
- facilitator intervention.

Combining these categories into one pass or failure count would hide the most
important failure mode.

## Product hypotheses, not requirements

If human research supports the same needs, Auteur might eventually need:

- authorization provenance linking recommendations, author actions, and the
  latest selected commitments;
- stale-proposal invalidation or regeneration after an author revision;
- an alignment check before any Identity proposal is shown;
- before-and-after commitment views for bounded revisions;
- visible preservation of secondary and constraint dispositions;
- a safe-stop state with a repair decision and next creative decision.

These are product-design hypotheses. They do not authorize runtime changes,
schema changes, APIs, CLI behavior, a semantic-layer change, or selection of a
browser, TUI, editor, or CLI surface.

## Process lessons

The failures were process failures. The recurring causes were missing gates,
unclear evidence categories, and insufficient separation between packet design
and evaluation. The appropriate response was to add a checkpoint, freeze the
materials, preserve the original run, or clarify the evidence record.

The main methodological limitation is shared-agent bias. The packet author,
synthetic persona, facilitator, and evaluator came from the same agent family
and used the same domain vocabulary. Separate transcript passes helped, but
they did not create independent judgment. The mutation cases were also
hand-designed against known weaknesses. They test protocol coverage, not the
frequency or severity of real product failures.

Future audits should use a fresh premise and an independent evaluator if they
are run at all. The evaluator should receive the transcript and mutation
disclosure only after the persona pass. The packet author should not silently
change the participant-facing materials during a run.

## Diminishing returns and stopping decision

The largest learning gains came from v1.2 through v1.5 and run 24. Each round
closed a concrete gap:

- v1.2 added preservation and safe triage;
- v1.3 showed that detection is not prevention;
- v1.4 showed that wording is not a hard gate;
- v1.5 added pre-exposure authority and recovery;
- run 24 showed that status and order do not guarantee content alignment;
- v1.6 tested alignment and repeated revision.

After v1.6, another run using the same premise, agent family, and mutation
style is likely to test whether the research process can anticipate its own
next case. It is unlikely to establish whether Auteur helps real authors. That
is diminishing return, not evidence that every possible failure has been
eliminated.

Decision: freeze v1.6 as the synthetic protocol baseline. Do not create a v1.7
simulation by default. Create one only if an independent audit reveals a new
failure class or if human preparation changes the protocol materially.

## Bounded autonomous-cycle rule

An autonomous audit may be useful as a limited process check. It must have:

1. one explicit hypothesis or failure class;
2. frozen participant-facing materials;
3. a fresh premise or an explicit reason to reuse one;
4. separate packet-author, persona, and evaluator records;
5. a fixed maximum number of runs;
6. a written stop decision when no new invariant appears.

The cycle is:

`hypothesis -> adversarial rehearsal -> evidence separation -> synthesis -> stop decision`

It must not become an open-ended stream of version numbers or a substitute for
human research.

## Next evidence gate

The next meaningful evidence gate is the approved human study. The readiness
addendum remains preparation only. Recruitment, consent, fallback-premise,
raw-note storage, and facilitator-assignment decisions must be supplied before
sessions begin.

Synthetic runs do not count toward the human study's 5 to 8 session stopping
rules. The human findings document must remain absent until those sessions are
complete. No product surface should be selected from this simulation sequence
alone.

## Repository decision

This retrospective is a process record, not a new architecture or product
definition. Keep the v1.2 through v1.6 registries and run records append-only.
Keep human participant evidence separate from synthetic evidence.

Current decision: `V1.6 SYNTHETIC BASELINE FROZEN; HUMAN VALIDATION REMAINS OPEN`.

If later work produces new synthetic evidence, append a dated section with a
new protocol or audit identifier. Do not rewrite earlier run conclusions or
pool synthetic outcomes with human participant outcomes.
