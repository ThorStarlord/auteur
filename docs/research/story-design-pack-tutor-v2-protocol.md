# Story Design Pack Tutor V2 Experiment Protocol

This protocol evaluates the next Tutor investment without treating literary
quality as an automated engineering score.

## Conditions

Each case is rendered as three matched packets:

- `control`: the decision is oriented without pack recommendation;
- `single_pack`: one selected pack supplies guidance;
- `composed_pack`: the selected pack set supplies guidance and explicit interactions.

Packet construction is deterministic and records pack versions and hashes. Human
evaluators should not see condition labels.

## Experiments

1. **Pack Effect:** Does pack-informed guidance produce a more specific,
   actionable author decision than control?
2. **Composition Effect:** Does composition produce a useful interaction that
   is absent from the single-pack condition without only increasing verbosity?
3. **Tutor Comprehension:** Can the author explain the craft principle after
   receiving guidance?
4. **Learning Transfer:** Can the author make a related decision on a new case
   with less help?

Artifact value and learning value must be recorded separately. A completed
packet is not evidence that the recommendation was accepted or correct.
