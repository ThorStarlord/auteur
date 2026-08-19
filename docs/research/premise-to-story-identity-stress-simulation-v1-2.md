# Premise-to-StoryIdentity Stress Simulation v1.2 Registry

Status: `INTERNAL SIMULATION EVIDENCE`

This registry indexes the standalone v1.2 simulation run records for the
Book-level premise-to-`StoryIdentity` stress protocol. It is synthetic agent
evidence only. It is not human participant research, creative-beginner
validation, usability validation, or product validation.

The previous full transcript document remains preserved as the
[historical findings archive](premise-to-story-identity-stress-simulation-findings.md).
The registry does not rewrite or delete that archive. The standalone records
provide focused navigation and future append-only storage.

## Fixed configuration

| Field | Value |
|---|---|
| Protocol | `v1.2` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Scope | Book-level `StoryIdentity` only |
| Human participants | `0` |
| Transcript policy | Complete persona and evaluator transcript in each run record |

The behavioral protocol is defined in the
[v1.2 stress simulation protocol](premise-to-story-identity-stress-simulation.md).
The registry covers v1.2 only; v1.0 and v1.1 remain available through the
historical archive and their linked protocol documents.

## Run index

| Run ID | Stress target | Result | Run record |
|---|---|---|---|
| `stress-v12-ensemble-01` | Preserve every ensemble thread while choosing a Book-level center | `SIMULATION_PASS` | [run 01](premise-to-story-identity-stress-simulation-runs/stress-v12-ensemble-01.md) |
| `stress-v12-dense-setting-03` | Separate necessary context from optional worldbuilding | `SIMULATION_PASS` | [run 03](premise-to-story-identity-stress-simulation-runs/stress-v12-dense-setting-03.md) |
| `stress-v12-constraints-04` | Translate abstract constraints into observable commitments | `SIMULATION_PASS` | [run 04](premise-to-story-identity-stress-simulation-runs/stress-v12-constraints-04.md) |
| `stress-v12-overloaded-05` | Triage an overloaded premise before proposing Identity | `SIMULATION_PASS` | [run 05](premise-to-story-identity-stress-simulation-runs/stress-v12-overloaded-05.md) |
| `stress-v12-triage-stop-06` | Pause safely when no primary thread is authorized | `SIMULATION_PASS` | [run 06](premise-to-story-identity-stress-simulation-runs/stress-v12-triage-stop-06.md) |
| `stress-v12-primary-secondary-07` | Preserve a secondary goal and authority constraint after selecting a primary | `SIMULATION_PASS` | [run 07](premise-to-story-identity-stress-simulation-runs/stress-v12-primary-secondary-07.md) |

## Aggregate v1.2 result

- `SIMULATION_PASS`: 6
- `SIMULATION_FAILURE`: 0
- `SIMULATION_INCONCLUSIVE`: 0
- Human participants: `0`
- Mid-run protocol changes: none
- Protocol changes required after run 07: none

The v1.2 runs exercised four protections added after v1.1:

- a preservation map prevented supplied ensemble goals from being silently
  demoted;
- context triage reduced dense-setting cognitive load;
- observable constraints made agency and authority boundaries inspectable;
- primary-thread triage either produced an author-ratified center or stopped
  safely without generating a `StoryIdentity`.

Run 07 added a complementary case: after the author ratified one primary
thread, the protocol preserved a meaningful secondary goal and strengthened an
authority constraint through one bounded revision. The secondary goal was not
treated as background flavor, and the resident group was not represented by
the protagonists without authorization.

## v1.2 decision

The synthetic v1.2 record is internally coherent enough to proceed to a
bounded human research design for the Book-level premise-to-`StoryIdentity`
flow. This is a protocol-readiness decision only.

The results do not establish human comprehension, author motivation,
recommendation quality, product value, or the suitability of any browser, TUI,
editor, or CLI surface. The six passes cannot be interpreted as a human
success rate.

## Append-only continuation

Future v1.2 runs must receive a new run ID and a standalone file in the
`premise-to-story-identity-stress-simulation-runs/` directory, then be added
as one new row in the run index and one short entry in the aggregate findings.
Do not overwrite an existing run record. If the protocol, persona, evaluator,
or participant-facing materials change materially, create a new protocol
version and a new registry rather than mixing results.
