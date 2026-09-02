# Global Map / Focus Productization Pilot V1

Status: author review complete; Productization Pilot V1 partially validated.

## Pilot implementation baseline

- Branch: `feature/global-map-focus-productization-v1`
- Commit: `c60958a61c434cf0c747b39994444a4463f0835b`
- Status: **FROZEN FOR AUTHOR DOGFOOD**
- Permitted changes during dogfood: none, except execution-blocking defects.
- Evidence rule: every observation identifies this implementation SHA.

This was a bounded dogfood protocol, not a benchmark. The implementation remains frozen at the recorded SHA.

## Product hypotheses

1. Given accepted long-form history and an explicit planning intent, Focus surfaces a small understandable set of constraints, relevant history, and persistent pressures without manual whole-story reconstruction.
2. After one earlier accepted revision, Auteur surfaces downstream impact and review order without silently rewriting later accepted artifacts.

## Project shape

Use one real bounded project with 6–10 books or equivalent major entries:

- several accepted long-running commitments;
- 2–4 meaningful long-range causal chains;
- 2–3 persistent pressures;
- at least one obsolete fact;
- at least one dormant fact that can be explicitly reactivated.

Do not use a two-scene toy or a dedicated vertical-slice research fixture.

## Tasks

### 1. Planning

Enter an explicit planning intent for a later book, then run:

```text
auteur series focus PROJECT --book N
```

Ask the author: “What are the three most important existing constraints on this decision?” Record whether the output surfaced the right history, omitted distracting recent material, made pressure groupings understandable, and explained why each historical item matters now.

### 2. Counterfactual revision

Before changing canon, choose one accepted earlier realization and inspect the impact of a proposed revision. The author must be able to distinguish the proposal from accepted canon and understand likely downstream consequences.

### 3. Actual revision

Accept that one revision through the existing author acceptance boundary. Then rebuild the Map and Focus. Record whether affected later artifacts became stale, suspect, or contradictory as expected; unaffected artifacts remained accepted; the review order was understandable; no downstream payload was silently rewritten; and rebuilt Focus reflects the new accepted state.

## Observation sheet

| Measure | Author observation | Evidence / artifact IDs |
| --- | --- | --- |
| Orientation | Reviewed; Focus decision support was insufficient. | `focus-before.txt`, `focus-after.txt` |
| Provenance without YAML | Reviewed; contextual provenance remained insufficient. | `focus-before.txt`, `focus-after.txt` |
| Relevance / information load | Reviewed; relevant facts were surfaced but not narratively contextualized. | `pilot-observations.md` |
| Long-range value | Mixed; the dependency chain was mechanically useful, but its story meaning was not explained. | `impact-after.txt` |
| Revision safety | Positive; downstream impact propagated without silent rewriting. | `impact-after.txt` |
| Authority comprehension | Reviewed; accepted versus derived state remained technically distinguishable. | `focus-after.txt`, `impact-after.txt` |

## Author disposition

- Author dogfood: **COMPLETE**
- Author value review: **MIXED**
- Focus decision-support value: **NEGATIVE / INSUFFICIENT**
- Revision-safety value: **POSITIVE**
- Strongest demonstrated value: Auteur detected downstream consequences of the
  D19/Wren revision without rewriting accepted later story material.
- Primary author friction: Focus identified relevant facts and relationships,
  but did not explain the narrative context that makes them relevant to the
  current creative decision.
- Highest-leverage next capability: **Contextual, author-readable relevance
  explanations for Focus and revision impact.**
- Extraction reopening gate: **NO**
- Productization Pilot V1: **PARTIALLY VALIDATED**

Required explanation shape for the future capability:

`story fact → narrative meaning → connection to the current decision → consequence if ignored or changed`

## Friction log

Record each point where the author hesitates, asks “why is this here?”, cannot find the source, cannot tell what is accepted, or cannot tell what to review.

| Step | Friction | Classification | Smallest useful next capability |
| --- | --- | --- | --- |
| Planning / Focus | Relevant facts and relationships were surfaced without sufficient narrative context. | explanation / author-facing presentation | Contextual relevance explanations |
| Revision impact | Downstream impact and preservation were useful, but review leverage was not explained. | reconciliation workflow / explanation | Contextual impact explanations |

Classifications are intentionally narrow: Focus selection, relation representation, explanation/provenance, reconciliation workflow, commitment lifecycle, or scale/budget.

## Stopping rule

Stop after one project has produced a valid Map, one author-readable Focus, one genuinely long-range decision, one earlier accepted revision, correct downstream impact without silent rewriting, a successful rebuild, and a completed friction log naming the single highest-value next capability.

Do not begin Productization V2 automatically. The author-selected next capability is contextual relevance explanation. Do not reopen automatic extraction, generalized ontology, scaling, or another architecture cycle.

## Authority boundary

Accepted Series Directions, Book Directions, and realization revisions remain the source of truth. Global Map, Focus, and impact reports are derived and rebuildable. The productization command does not accept proposals or rewrite downstream artifacts.
