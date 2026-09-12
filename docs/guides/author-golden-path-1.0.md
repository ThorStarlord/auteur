# Auteur 1.0 author golden path

Auteur 1.0 is a whole-story structure engine first. The safe author workflow
is intentionally staged: inspect the current state, create derived reports or
candidates, review them, and explicitly accept a canonical change through the
owning command.

## Start here

From the project root, run:

```text
auteur workflow next
```

The command reports the first useful action, its command, its authority level,
and a description. `workflow next --json` is the stable machine-readable
projection for automation. Actions marked `read_only`, `derived_artifact`, or
`candidate_generation` may be safely dispatched by the workflow executor;
`authority_bearing` and `canonical_mutation` actions require the author.

## Golden path

1. Establish Story Identity and the global constraints for the story.
2. Create and validate the whole-story blueprint.
3. Run deterministic structure diagnosis and inspect the derived report.
4. Generate proposals or candidates for gaps; do not edit accepted artifacts
   from a report or critic.
5. Review the proposal or decision, resolve required author choices, and use
   the owning acceptance command with explicit confirmation.
6. Build Chapter and Scene realization only from fresh accepted structure.
7. Draft Chapter Expression from fresh realization, then inspect the Book
   composition and its derived reasoning report.

## Recovery rules

- Missing or incomplete identity: follow the identity action shown by
  `workflow next`; do not start structure generation yet.
- Rejected discovery candidate: inspect the rejection and generate a new
  candidate; rejection never mutates the accepted identity.
- Stale report or proposal: rerun the owning analysis from current accepted
  inputs. Do not apply a stale proposal or substitute a newer revision.
- Incomplete Chapter or Book composition: repair the owning lower-level
  artifact first, then recompose the derived higher-level view.
- Deferred capability: treat the command as informational and use the
  documented supported path. Markerless mapping, merge/split, grouped
  decisions, and broad long-horizon Series intelligence are not 1.0 promises.

Every canonical mutation must be author-triggered, atomic, provenance-bearing,
and attributable. Reports, recommendations, simulations, and previews remain
derived and cannot be accepted directly.
