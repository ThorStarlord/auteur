# Stage B packet manifest

Frozen before Stage B ran. Verify with `sha256sum stage-b/packet/*` on the Windows working copy (CRLF line endings).

| Packet file | sha256 | Source | Treatment |
|---|---|---|---|
| `00-stage-b-instructions.md` | `f33313666249d1b63fac7feb2bdc2d4ddde337158911bfa4da559cf86d1f80d2` | Written by the coordinator | Tasks §5.1–5.4 and report format; scope limits |
| `04-revision-delta.md` | `9086dc119f8e5db180ad7637bd377ef49b8da735ca0c016779d6561b0c301d41` | `experiments/series-architecture-30-book-v1/C-revision-delta.md` at `3168963b` | Edited: one paragraph of §7 removed (the designer's own "known omission" finding); links to withheld or out-of-packet files converted to plain text or `[WITHHELD reference]` |
| `05-revised-candidate.json` | `faa9c89321552580807e26471ff98bf06cda317a8241f4cea536df1165cfa48b` | `C-studio-candidate-revised.json` at `3168963b` | Edited: the same retrospective clause withheld as in the Stage A packet (`ph_4_settled_water`) |
| `06-review-evidence.json` | `7781cf0ec3296dac7a1979ec2152cdd35163058dd3b6258cba2df33c85c72bb4` | `evidence/07-complete-revision.json` (`review` object), `evidence/02-complete-original.json` (status only), `evidence/09-apply-revision.json` | Extracted: the duplicated candidate copy removed from the review object (it matches `05`); the same clause withheld (zero occurrences in the review object, checked) |

Unchanged for Stage B: the frozen original candidate is the Stage A packet file `stage-a/packet/03-original-studio-candidate.json`. The original architecture is `stage-a/packet/02-original-architecture.md`.

## Withholdings at Stage B (exact)

1. `04-revision-delta.md`, §7: the paragraph beginning "**Known omission, found by reviewing the delta:**" and naming `et_grief_of_orders` and a link to the product observations file. It was the designer's own finding that the grief target was stale. Withheld so that the reviewer could test the same question independently. The packet marks the removal.
2. `04-revision-delta.md`, §5: the link to the local-versus-global judgment file, replaced by `[WITHHELD reference]`.
3. `05-revised-candidate.json` and the review evidence: the retrospective clause, as in Stage A.

Nothing else was withheld. In particular, §8 of the delta (effect on identity) was kept, because the mission lists the whole delta as Stage B input.

## Known limits

- The reviewer was told that a §7 paragraph had been withheld, so the omission may have been directed attention. See the record's README.
- The coordinator read the delta before preparing this packet, so its selection of what to withhold is a documented judgment.
