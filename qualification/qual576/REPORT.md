# #576 — Long-horizon host-agent architecture creation: qualification record

**Date:** 2026-11-16
**Canonical base:** `8793733b2a477629d00824f59696c3ff7d912936`
**Status:** executed. One scenario, one model family, one independent AI reader. No human author.

## What ran

A genuine Studio request was prepared through `prepare_architecture`, not a fixture:

| Item | Value |
|---|---|
| Workspace | `qual576/ws` (CanvasStore, canvas `qualification-576`) |
| Request SHA-256 | `2cb6b29d2cad08c7666cabf476739dbabab2a94ea9ed1093c227934116892786` |
| Host agent | a fresh general-purpose subagent, given only `system.txt` and `user.json` |
| Model | `deepseek-v4.1-flash` via the `opencode` general subagent |
| Runtime recorded in the response | `opencode-general-subagent` |

The host agent was explicitly barred from reading Auteur's source, tests, or fixtures, so the candidate is a response to the request rather than to the validator.

## Attempt 1 — rejected

`candidate-rejected.json` (154,077 bytes, `sha256:7cdc3716…`) failed validation with **8 errors**:

- `opportunities[0..1].description` and `.faithfulness_to_author_intent` — extra inputs; `why_it_matters` missing
- `opportunities[0..1].why_it_matters` — required field absent
- `genre_contracts[1].role` — `locally_dominant` is not one of `governing|supporting|tertiary|local`
- `genre_contracts[7].role` — `background` is not in that set

Exact error preserved at `artifacts/validation-error-attempt-1.txt` (`sha256:fb6c9c01…`).

**This is a finding about the host-agent contract, not about creative capability.** The request describes the schema in prose; the agent invented plausible field names and plausible enum values. No repository test could surface this because every fixture supplies a hand-written candidate.

## Attempt 2 — admitted

After one repair loop carrying the validator's own error text (what an author would see), the candidate was admitted:

| Item | Value |
|---|---|
| Artifact | `candidate-admitted.json` (154,048 bytes, `sha256:214acaa4…`) |
| Status | `ready` |
| Nodes / links / phases | 71 / 82 / 12 |
| Open questions | 12 |
| Opportunities | 2 |

Boundaries held: no `story_identity.yaml`, no `blueprint.yaml`. `premise_status.authority = working_architecture_not_canon`, `accepted.source = null`, all 71 nodes classified as provisional agent interpretation.

The agent used the T02/T04 opportunity contract unprompted and correctly: one `deepens`, one `reinterprets` with `requires_author_decision: true`, and `artistic_potential` ("very high") separated from `intention_fidelity` ("moderate to high but not assumed").

## Independent evaluation

A fresh reader received only the Story Vision and a rendered view of the architecture, with no provenance and no knowledge of what produced it.

The decisive judgements, quoted:

**Purpose fidelity — mostly strong, with two real drifts.**

> "Mostly yes, and the fidelity is unusually literal where it matters most."

> "The good becomes a budget … over seventy Books that is not an economy of hope; it is an economy in which nothing is ever free and every improvement is collateral … That is dignified depletion, not optimism."

> "'Never resolve the central question' is widened into 'never resolve anything' … over seventy Books it will read as evasion."

**Causal substance — one genuine mechanism, an inverted hierarchy.**

> "the engine does not generate evidence or antagonists; it converts whatever the other layers produce into cost … The thing called the primary engine is the accounting; the things called subordinate layers are the generators. The hierarchy is upside down."

> "Strongest mechanism: Self-narration … it *reproduces the structure of the founding conflict out of virtue* … the one mechanism that could carry seventy Books on its own … and it is **not** in the summary's five subordinate layers."

**Long-horizon reasoning — partly decorative.**

> "Four phases are genuine question-relocations … Phase 10, 'Repair at scale,' is the clearest deletion … That leaves Phases 8, 9 and 10 as three consecutive low-variance movements immediately after the document's 'deepest pivot.'"

> "The largest omission is structural … it has no phase in which the institution *is* honest and the series asks what that honesty is worth. The second half of the author's sentence is handled as a terminal condition, not as territory."

**Epistemic hygiene — notably good.**

> "The boundary is unusually legible … This is better epistemic hygiene than most human proposals manage."

**Intelligibility — summary yes, inventory no.**

> "The single most confusing element is the word 'engine.' The summary claims 'One primary engine with five subordinate layers' and names five. The node inventory tags **thirteen** items `(engine)`."

**Overall.**

> "An author could take this, delete Phase 10, promote self-narration to primary, add one phase about the price of an actually-honest institution, and have something that would hold. That is a genuinely useful document to have been given, and it is not yet a series."

## What this establishes

**Demonstrated.** A capable host agent, given only the real Studio request, produced a substantial abstract 70-Book architecture with 71 components, 82 typed relationships, a 12-phase horizon, correct noncanonical framing, honest provenance for its own inventions, and unprompted, correctly-classified creative opportunities. An independent reader could summarise it in ordinary language and found its epistemic hygiene better than typical human proposals.

**Not demonstrated.** That the architecture is artistically sound. The same independent reader found the optimism converted into depletion, the causal hierarchy inverted, four of twelve phases decorative, and the second half of the author's question unanswered. One scenario, one model, one AI reader, no human author: none of this generalises.

## Defects exposed by authentic execution

1. **Host-agent schema is prose-only.** Two independent executions (this one and the T10 Auteur arm) failed first-pass validation on enum guesses and type shapes. Recorded; not repaired during the qualification.
2. **`project_architecture_resume` omits the governing objective and premise status.** A fresh session recovers opportunities (T08) but not the author's artistic purpose (T01). See `resume.json`: `governing_objective` and `premise_status` are absent, while `working_opportunities` is present.
3. **`engine` is both a node category and a hierarchy role.** The model permits 13 nodes tagged `engine` while the summary claims five subordinate layers, and nothing reconciles them.
