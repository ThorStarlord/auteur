# Session R revision candidate and acceptance

The existing `SeriesVerticalSliceService.propose_realization` and
`accept_realization_revision` operations were used. The accepted YAML was not
hand-edited. The candidate referenced `book-1-direction` revision 1 and copied
all twelve Book-1 transitions, changing only `mara-ion-trust`.

Candidate ID: `book-1-sounding-line-outcome-revision-2`

Changed transition:

```yaml
transition_id: mara-ion-trust
subject: Mara Venn and Ion Vale
attribute: relationship
before: null
after: strained cooperation under unresolved distrust
explanation: Ion still delivers Mara's evidence, but Mara learns that he concealed the seizure orders until after she publicly committed herself. They cooperate on the immediate crisis without establishing conditional trust.
```

Acceptance returned the same artifact and bundle IDs:

- artifact: `realization-bundle-book-1-sounding-line-outcome`
- bundle: `realization-bundle-book-1-sounding-line-outcome`
- candidate: `book-1-sounding-line-outcome-revision-2`
- transition count: 12

Revision payload hashes:

- revision 1: `1f7f1a6cffc2b3f755a3d4090caf3ee0797e4a03a940554bf377e567c265d3ee`
- revision 2: `842f5f86c8157005fac127d542e2ea998246e060a36cdc9e54de70085772157a`

Book 2 and Book 3 payload hashes remained unchanged from the pre-revision
snapshot. No Book 2 or Book 3 acceptance operation was run.
