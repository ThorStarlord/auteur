# 00. Freeze and provenance

Status: **working / noncanonical.** Records what was verified, what was frozen, and who or what reviewed it. It is the first file to read when checking the record.

## 1. Starting state (verified 2026-11-12)

| Item | Value |
|---|---|
| Repository | ThorStarlord/auteur |
| PR #553 (construction, draft) | head `aaae0eaaddfbfa98ccb6d239fc01cef5ffe3d478`; base `experiment/series-architecture-30-book`; 37 changed files; MERGEABLE; not merged |
| PR #551 (original, draft) | head `3168963b7df262d81354d3fec2cf8ef2ec74cd4b`; unchanged |
| PR #552 (challenge, draft) | head `ac1fbff80ab77cac0c44adc9c91b9568f6689d42`; unchanged |
| Worktree for this work | `H:/GithubRepositories/auteur-30book-verification`, branch `experiment/series-architecture-30-book-verification`, created from `aaae0eaa`. The repository's `.git` is the shared common directory. |
| Unrelated open PR bound to the session | PR #540 (Wandering Islands draft). Not touched. |

The construction files at `aaae0eaa` match the recorded hashes, so the artifacts are the ones described in PR #553:

| File (committed blob) | SHA-256 |
|---|---|
| `01-causal-construction.md` | `67a790e120d3dd40…` |
| `02-finale-alternatives.md` | `b3694f4db9e8a458…` |
| `03-working-candidate.json` (W1) | `718c27635b664e1c…` |
| `03-working-candidate-v2.json` (W2) | `0fbf5c9cbbe24113fbe50411fa9336a57f3199c73162aeca01ac675b30ef4364` |
| `04-h1-focused-delta.md` | `67cf009fe869a9dd…` |
| `evidence/make_h1_path.py` | `65b9acd0b4f3488b…` |
| `evidence/instruction-h1.txt` | `c4c625b7e6e9b90b…` |

## 2. Artifact identity

- **Final candidate:** W2, `03-working-candidate-v2.json`. Validated against `ArchitectureCandidate` (schema v2): 32 nodes, 34 links, 5 phases, 7 emotion targets, 7 complex emotions, 16 open questions. It is the candidate the Stage A reviewer read.
- **H1-from-W2:** derived in a disposable scratch location, not in the repository, by running the recorded script `evidence/make_h1_path.py` on a copy of W2. Output SHA-256 `face0464875dd7f1357b16904083fa13961a446251667d4a884e34354226b5c4`. It matches the recorded H1-from-W2 hash in PR #553. Schema validation: passed. It has 33 nodes, 37 links and 5 phases.
- **Not used:** W1, H1-from-W1, the blind Haiku response that structural validation rejected, and its diagnostic copy.

## 3. Reviews

### 3.1 Stage A (final W2)

- **Packet:** `review/stage-a-packet/` (seven files; hashes in `review/stage-a-manifest.json`). It contains the author's brief, the original architecture with its §8 and one §4 sentence withheld, the causal construction unmodified, the finale alternatives with the nomination section and one advocacy paragraph withheld, and W2 byte-for-byte.
- **Reviewer:** one fresh general-purpose subagent, model Opus, one invocation. The reviewer self-identified as Claude Opus 5.5. Its report is `review/stage-a-report.md`, verbatim.
- **Known exposure:** the reviewer's automatically supplied session context included repository metadata (`CLAUDE.md`, a memory index and a branch name). It reported that it opened none of these and that they did not bear on the architecture. It did not see the construction files beyond the packet, the earlier reviews, the earlier candidate or the synthesis.
- **Limit:** the reviewer shares a model family with the earlier Opus reviewers, and the coordinator is a different model. Independence is by fresh context, not by a different author.

### 3.2 Stage B (H1-from-W2)

- **Packet:** `review/stage-b-packet/` (eleven files; hashes in `review/stage-b-manifest.json`). It contains the Stage A files, a Stage B mandate, the H1 premise, the focused revision instruction, H1-from-W2 (file 09), and a mechanical change list (file 10).
- **Reviewer:** one fresh general-purpose subagent, model Opus, one invocation. Self-identified as Claude Opus 5.5. It had no access to the Stage A report. Its report is `review/stage-b-report.md`, verbatim.
- **Known exposure:** the same session metadata as Stage A. It reported that this did not inform its findings.

## 4. The shared crisis (frozen)

- **File:** `03-shared-crisis.md`.
- **SHA-256:** `7a1be986281db9cca673a155e4eb301d8dcc5cab9adda9ec8a66cc44957314e9`.
- **Freeze point:** frozen after both review reports were recorded and before any trace was written. No trace has been run against an earlier version of the scenario.
- **Coordinator knowledge:** the coordinator had read both review reports when it built the scenario. The scenario is written to avoid relying on the two findings it might otherwise have used (the Book 15 surfeit mechanism, and the ratification body). Any remaining dependency is stated in its §11.
- **Single author of the scenario:** the coordinator. No adversarial scenario designer was used, and the scenario is therefore not independently checked. That limit is recorded in the README.

## 5. Corrections to earlier claims in PR #553 (recorded here, not in PR #553's files)

1. **The product's preserved check.** PR #553's synthesis §5 and the consistency record (C2) say that the product's preserved check "compares identifiers only". That is inaccurate. `candidate_diff` in `src/auteur/beginner/studio_architecture_review.py` compares whole entries (`new[k] != old[k]`), so an entry counts as preserved only if its content is unchanged. The accurate limit is that unchanged entries are never checked against the changed entries they depend on. This was verified by running `build_architecture_review` on W2 against H1-from-W2: the product reports `eng_old_hand`, `ph_5_unmeasured`, `alt_b_allotted` and `alt_c_ratified_trigger` as preserved while they mention custody or Hall concepts that H1 changed. Whether they are still valid is what Stage B was asked to judge.

## 6. Packet construction limits

- The packets renumber the source files. Internal links in the causal construction still point at the original names (`02-finale-alternatives.md`, `05-consistency-record.md`), so some cross-references in the packet are stale. Stage A's reviewer noticed this and read the references as pointing to the renumbered files. Nothing in the content depends on the links.
- The packet files were built from committed source content (`git show aaae0eaa:…`) and written with LF line endings. Their hashes are the packet's own hashes, not the source files'.
