# Semantic packet manifest

Frozen before the semantic review ran. Hashes are sha256 of the files as written (CRLF on the Windows working copy; see README).

| File | sha256 | Source | Treatment |
|---|---|---|---|
| 00-instructions.md | see file | Written by the coordinator | Reviewer task, scope limits, report format |
| 01-working-candidate.json | 718c27635b664e1c7f04c5519c9e910e3adec6ac4ee3d4de69285829ecd613fe | This construction, `03-working-candidate.json` (W1) | None |
| 02-h1-candidate.json | 5ea399e4212f236d0cbc459c204fa7f883ba43dae4bd87c74255181f7fd882d9 | Derived from W1 by `evidence/make_h1_path.py`; validated and applied in scratch canvas `h1v1` | None |
| 03-h1-revision-instruction.txt | c4c625b7e6e9b90b9531b50bd258424969a106628221e93ef1910cf0c1440d31 | `evidence/instruction-h1.txt`, the instruction recorded in canvas `h1v1` | None |
| 04-preserved-ids.json | be0ce220d2a25606968e89dcd87533ef5d9050d61db655f7076b6b680ee912f5 | Product review (`preserved` object) for canvas `h1v1` | None |

**Not in this packet, by design:** the H1 focused-delta document; PR #552's reconciliation; the designer's evaluation files; the blind-test output; the coordinator's consistency record. The semantic reviewer is told that the preserved list compares identifiers only.
