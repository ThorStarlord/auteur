# Guided Author Workspace V2 — Owner Dogfood Protocol

**Status:** `NOT_RUN`  
**Evidence class:** owner usability; this protocol cannot mark itself PASS.  
**Release role:** required bounded evidence for the V1 beginner-interface claim.

## Purpose

Test whether a beginner can traverse the supported browser decision loop without implementation documentation, raw YAML, or CLI knowledge beyond starting the local Workspace.

This is not a literary-quality evaluation and does not authorize architecture expansion by itself.

## Preconditions

- exact frozen release-candidate SHA recorded;
- fresh installed artifact from that SHA;
- one project with accepted StoryIdentity/Blueprint and at least one current Tutor/Structure decision path;
- Workspace started locally with `auteur workspace --project .`;
- no source code, implementation docs, or raw project YAML open during the interaction.

## Journey

1. Open the local Workspace.
2. Identify what currently needs attention.
3. Explain, in the owner's own words, why that item matters and whether it is advice or accepted story state.
4. Record a Tutor choice where applicable.
5. Review the resulting Structure proposal and its trade-off.
6. Select one option.
7. Create and validate the revision plan.
8. Preview what will change and what downstream work is affected.
9. Decide whether to cross the explicit Structure authority boundary.
10. If applying, use the separate browser confirmation and verify the story changed only after that action.
11. Return to Author Attention and identify the next state/action.
12. Restart the Workspace/process and verify the project still explains the current state.

## Questions to record

- Could I determine what to do next without implementation documentation?
- Could I distinguish derived advice/proposals from accepted story authority?
- Did the confirmation step communicate a meaningful story-state change rather than generic UI ceremony?
- Could I understand why an action was blocked when currentness/validation failed?
- Could I recover orientation after refresh/restart?
- Did I need to inspect raw YAML to understand the core decision loop?
- Did the Workspace expose a safe next action without implying that a creative choice was objectively good?

## Evidence record

Fill this section only after performing the protocol on the exact release candidate.

```yaml
candidate_sha: null
package_artifact_sha256: null
performed_at: null
performed_by: owner
result: NOT_RUN # PASS | PASS_WITH_FRICTION | FAIL
journey_completed_without_raw_yaml: null
journey_completed_without_implementation_docs: null
authority_boundary_understood: null
restart_orientation_successful: null
friction: []
```

Each friction item must have exactly one primary class:

```yaml
- step: 0
  class: UX # UX | workflow | craft_knowledge | domain_model | infrastructure
  severity: low # low | medium | high | blocker
  observation: ""
  smallest_reproducible_case: ""
  recommended_smallest_intervention: ""
```

## Decision rule

- `PASS`: core browser decision loop completed without implementation docs/raw YAML and authority boundaries were understandable.
- `PASS_WITH_FRICTION`: journey completed safely but bounded non-blocking friction remains; record follow-up candidates.
- `FAIL`: the core V1 beginner claim is not supported. Fix the smallest owning boundary or explicitly narrow the V1 Product Contract before candidate freeze.

Do not convert subjective creative preference into a release failure. Do not convert one UX problem into a new ontology by default.
