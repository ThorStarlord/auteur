# Story-Instance Relationship Extraction V1.1 Attempt 2

## Status

**ATTEMPT 2 INVALIDATED — REMAINS UNBLINDED — NO PRODUCT INFERENCE**

All 78 scheduled model calls completed:

- extractor: 3/3
- downstream generator: 36/36
- extraction evaluator: 3/3
- downstream evaluator: 36/36

No prior empirical observation was reused. The condition map remains sealed.
No CASE A/B/C/D classification was made.

## Defect

The second fresh extractor response was mechanically 'STRUCTURE_VALID'.
However, when constructing the downstream generator packets, its
'R-DERIVED' overlay was incorrectly treated as 'EMPTY' for repetitions 2 and
3. The frozen protocol requires every structurally valid extractor response to
be canonically projected and used for its paired downstream repetition.

This is an execution error, not a protocol ambiguity. The affected generator
packets and all downstream judgments are retained as evidence but are not
valid observations for the preregistered experiment.

The first extractor response was mechanically 'STRUCTURE_VALID'; the second
was mechanically 'STRUCTURE_VALID'; the third was 'FORMAT_INVALID' because its
abstention objects contained a disallowed extra field. No repair, retry, or
semantic reconstruction was performed.

## Packet integrity

All 39 evaluator packets passed the exact embedded-response equality check
before inference:

- extraction evaluators: 3/3
- downstream evaluators: 36/36

The packet-integrity defect from Attempt 1 did not recur. This does not cure
the incorrect derived-overlay assignment described above.

## Freeze boundary

The 39/78 capture was committed as a mid-run evidence anchor on this fresh
branch; it is not a true pre-unblind freeze. Because the run is invalidated,
no true 78/78 pre-unblind freeze, unblind, result join, or empirical-results PR
was created.

