# Corrections to the fresh agent's Book 24 function, and their checks

Status: **working and noncanonical.** Records every change made to the Book 24 function and its candidate after the fresh agent produced them. The agent's originals are kept unchanged. Each correction is listed with the defect it removes and the review that found it.

## The product revisions, in order

Each Book 24 candidate was submitted to the product's `prepare` and `complete-file` path on the disposable canvas. Each produced a reviewed revision. The live architecture was never changed (32 nodes throughout), because the bridge has no command to apply a reviewed revision. Only the last revision is pending.

| Step | Candidate | Product request | Status after |
|---|---|---|---|
| 0 | agent's `book-24-candidate.json` | `07ae948a…5108` | review ready; superseded |
| 1 | `book-24-candidate.corrected.json` (round 1) | `3c12d95abf7eab03…` | review ready; superseded |
| 2 | `book-24-candidate.corrected-2.json` (round 2, first submission) | `9739818ec8d4bf0a…` | review ready; superseded |
| 3 | `book-24-candidate.corrected-2.json` (round 2, after one further fix) | `e000e95646dc47ed…` | **review ready; pending** |

The product stores every request. A superseded request is still in its store, but the pending pointer names only the last one.

## Round 1: correction of the critique's required and recommended findings

Source: the focused critique (`cold-start/critique/report.md`) and the verification of round 1 (`cold-start/verification/report.md`).

- **F1, the governing variable (required).** The proposal said the governing variable "gains a third term". Now the capability record "bears on" the variable and "does not change who is counted for draw." The candidate link `l_b24_mark_variable` agrees.
- **F2, Hesper's motive (required).** The proposal had decided an author-reserved choice. It now says the motive is designed to be judged against open question 10, and that the author decides whether it is independent.
- **F3, the Reading Hall's refusal (recommended).** It rested on an institutional principle that tilted against Alternative B. It now rests on the limit of the instrument.
- **F4, the surge route (recommended).** P10 said the surge route "is avoided", which the packet cannot support. It now says the Book neither designates nor excludes the Lowfen.
- **F5, the gauge citation (recommended).** It cited a link to the Gate Table for the gauge.
- **F6, two wording claims (minor).** The gift-without-skill claim is now marked as a new assumption (P4). The granddaughter's parallel with Book 1 is now stated as a looser parallel.
- **K1, a knowledge omission in the architecture (restored).** The compact architecture had dropped that Hesper's household is one of the hand-light houses the Turn burdens. The original states this in Book 23, and the excerpt is in the verification packet.

## Round 2: correction of a defect the round-1 verification found

Source: the verification of round 1, which found one new defect and two partly fixed items, and one credible concern.

- **G1, a new defect that round 1 introduced: which gauge.** The round-1 text said "the gauge is the Source's own state." But the candidate names the Book 22 instrument "the Gate gauge", and the original names the Book 23 Balance Stones the public gauge. The Book 24 function now says **Balance Stones** wherever it means the Book 23 instrument. The Book 22 Gate gauge is named only where it is meant (architecture §3 and §4). Checked mechanically: the function has no occurrence of "gauge", and the candidate's Book 24 nodes and links have none.
- **G2, the Reading Hall's framing (partly fixed).** The §7.4 sentence about the Hall "defined a limit on itself" now says the Hall "declines to attribute balance to persons while the Stones cannot resolve local return (P3)."
- **G3, the surge route (partly fixed).** P10's "Any channel except the Long Return's surge route would serve" now reads "Any channel the crew can work would serve." The sentence on the author-reserved surge route is kept.
- **G4, the Hesper belief (credible concern).** The architecture's Hesper row now says the cohort's belief is a "working reading" that "her household's burden complicates". The function's Hesper line now says her motive is derived from "the cohort's Book 23 belief, which her household's burden complicates."
- **G5, the candidate's Book 24 node and two link functions.** The crew node's summary and the two gauge links now name the Balance Stones. Every link function stays within 120 characters (the longest is 93).

## Mechanical checks on the final files

- The round-2 function contains 0 occurrences of "gauge", 11 of "Balance Stones", and each of the intended phrases exactly once. The defective phrases "public gauge", "third term" and "Any channel except" are absent.
- The final candidate validates on current main's schema.
- The final candidate differs from the agent's candidate only in its Book 24 additions and the corrected text described above.

## What was not verified by a fresh reviewer

Round 2 was checked mechanically by the coordinating agent, not by a second fresh reviewer, because the mission bounds the review cycles. The checks above show that each intended change is present and the defective phrases are gone. They do not show that the new sentences are correct. A further independent verification would be needed for that, and it is not run here.
