# Provenance authority: what `author_declared` means and what is now enforced

**Date:** 2026-11-12. **Baseline:** `origin/main` at `8b53b32f`. **Change:** commit `58a88e15` on `feat/working-book-architecture`.

## 1. The question

The working Studio architecture labels each emotion target `author_declared` or `agent_proposed`. Before this change, the validator accepted either label from any agent response. A blanket rejection of `author_declared` would break the recorded behaviour in [the agent-first evidence](../agent-first-ontology-20261103/README.md): the agent labelled `wonder`, `dread` and `hope` as author-declared because the author's Story Vision names those experiences.

## 2. What the label meant before, and what it could not show

| Question | Before this change |
|---|---|
| Source origin | Not checked. The label was whatever the agent wrote. |
| Agent interpretation | Not distinguished. The intended effect, eliciting condition and aesthetic strategy of an `author_declared` target were agent prose under an author label. |
| Author acceptance | Not representable. No command or field records that the author accepted a working interpretation. |
| New claim in a revision | Accepted silently. A new `author_declared` id appeared in the review's changed components with no author-origin flag. |
| Promotion (`agent_proposed` to `author_declared`) | Visible only as a generic field change. |
| Removal of an author claim | Visible only as a generic removal. |

The instruction to writers said to "distinguish explicit author declarations from your own working hypotheses". The bridge guide said agent-written candidates must use `agent_proposed`. Those two instructions contradicted each other, and neither was executable.

## 3. The correction

`author_declared` now means a **source-origin claim**: the author's own visible text names the emotion. It does not record author acceptance of the agent's elaboration.

Enforced at `complete-file` (`src/auteur/beginner/studio_architecture.py`, `_validate_author_provenance`):

- A target may be `author_declared` only if every significant word of its `id` (three letters or more, not a function word) appears in the author-visible text the request showed: the Story Vision and the non-concept working items. Agent working notes, the previous candidate and the revision instruction do not count.
- A target the baseline already carried as `author_declared` is preserved without new proof. Its changes stay visible in the review.
- Anything else is rejected before any response is persisted, with the id named in the message.

Reported by the review (`src/auteur/beginner/studio_architecture_review.py`), under `preserved.author_declared_emotion_changes`:

- `new_author_claim`: a new id labelled `author_declared`.
- `promoted_to_author_declared`: an existing agent target relabelled.
- `changed`: a baseline claim whose fields changed.
- `label_removed`: a baseline claim whose label was removed.
- `removed`: a baseline claim that is absent.

`preserved.author_declared_label_meaning` states the source-origin meaning in the review output itself.

Schema, the `EmotionTarget` provenance enum, and apply semantics are unchanged. Existing candidates remain readable.

## 4. Replay against recorded evidence

`replay_historical_labels.py` runs the rule against the recorded requests and candidates from the agent-first evidence, using each request's exact packet. Output: [replay-output.json](replay-output.json).

| Recorded pair | `author_declared` ids | Verdict |
|---|---|---|
| Rich Vision develop | `wonder`, `dread`, `hope` | admitted |
| Revision of the rich Vision | `wonder`, `dread`, `hope` | admitted |
| Concept-aware revision | `wonder`, `dread`, `hope` | admitted |
| Sparse Vision develop | `trust` | admitted (the Vision says "learning to trust each other again") |

Mutation checks on the same revision packet:

| Mutation | Verdict |
|---|---|
| Promote agent-proposed `grief` to `author_declared` | rejected: not named in author text |
| Add a new `author_declared` target `awe`, not in the Vision | rejected: not named in author text |

## 5. Tests

`tests/test_beginner_studio_architecture_provenance.py` (16 tests): develop admits a named target and rejects an unnamed one with nothing persisted; agent interpretations are admitted; grounding requires every significant term and ignores stopwords and agent notes; revision cannot introduce or promote an unsupported claim; a grounded promotion is admitted and reported; a historical baseline claim survives revision without its source in the packet; relabelling and removal are reported; the review states the label's meaning.

`tests/test_beginner_studio_architecture_visual_review.py`: the fixture now uses the Story Vision that produced its recorded candidate. Before the fixture change, its author labels named terms the store's Vision did not contain, which the rule correctly rejects.

Studio regression slice at this change: 226 passed across `tests/test_beginner_studio_architecture*.py`, host-agent handoff, Studio API, authority integration, inquiry, realization, concepts and creative intentions. Node Studio architecture tests: 11 passed.

## 6. Remaining boundaries (not changed here)

- **Grounding is lexical.** It establishes that the author's own words name the emotion. It does not establish that the author endorsed the agent's elaboration, and the system cannot tell whether an earlier agent typed a working item. The review says so.
- **Develop over an existing candidate has no review.** A develop request replaces the working architecture without a baseline in its packet, so prior author claims can drop out without a review entry. This is existing behaviour, not changed here. Revision is reviewed.
- **No author-only operation sets `author_declared`** (design O2). The label remains a source-origin claim that an agent may make only when the author's text names the term.
- **The writer prompt** now states the rule. The rule itself is enforced by the validator, not by the prompt.
