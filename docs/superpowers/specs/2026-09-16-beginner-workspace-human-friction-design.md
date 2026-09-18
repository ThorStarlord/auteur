# Beginner Workspace human-friction correction design

Status: approved for implementation by the observed human walkthrough findings.

## Scope

This package corrects four bounded failures in the Beginner Workspace vertical
slice: shallow option-specific consequences, raw provenance in beginner
evidence, valid alternatives incorrectly blocking acceptance, and the browser
not exposing the complete milestone journey. It does not redesign the
application or broaden the Mystery workflow.

## Option-specific impact

The Mystery decision adapter will expose deterministic, derived impact metadata
for each valid option. The impact is a reusable semantic projection with these
dimensions:

- audience experience;
- aesthetic framing;
- expected tropes/conventions;
- narrative or structural consequence;
- trade-offs.

The metadata belongs to the curated Beginner guidance contract, sourced from
the existing Howdunit genre-contract knowledge. It is not canonical Story
Identity and is never persisted as narrative truth. The selected option causes
the current Decision Card projection to render that option's impact before
Continue. The existing domain acceptance boundary remains the only path to
canon.

## Guidance divergence versus blocking contradiction

Selection of a valid option that differs from the recommendation is guidance
divergence. It may produce a nonblocking trade-off or authorial tension and may
change the contextual explanation, but it is not a contradiction.

Blocking remains reserved for an actual semantic incompatibility, invalid
combination, unmet invariant, or materially stale assumption. Existing real
contradiction and acknowledgement behavior remains intact. The application
must therefore distinguish `GUIDANCE_DIVERGENCE` from a blocking contradiction
in its derived issue classification.

## Human-readable evidence

Evidence projections retain exact machine-readable source, field, rule, and
claim-role data for validation, provenance, and advanced inspection. The
beginner projection additionally exposes a stable human-readable label,
description, and claim role. Repeated source references are deduplicated by
visible claim while the underlying references remain recoverable. Technical
source identifiers are available only as secondary evidence, not as the main
beginner label.

## Browser action availability

The server projection will expose context-sensitive available actions derived
from the application projection. The browser will render those actions and
send existing command-envelope requests; it will not decide readiness or
reimplement journey rules.

The browser must expose, when the projection allows them:

- open milestone review;
- acknowledge a valid blocking issue;
- accept Story Direction, Story Identity, or Whole-Story Structure;
- open and cancel a revision;
- accept an applicable revised milestone.

The same projection continues to show at-risk stages during revision and
stale downstream state only after accepted replacement.

## Out of scope

- new canonical narrative layers or ontology;
- changing existing promotion, provenance, or staleness authority;
- LLM guidance;
- the full nine-phase Mystery workflow in the beginner surface;
- broad visual polish;
- CLI parity;
- release qualification, merge, or publication.
