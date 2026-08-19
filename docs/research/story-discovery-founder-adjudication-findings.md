# Phase E — Founder Creative Adjudication Findings

## Status

In progress. Two founder cases have been adjudicated. The research PR remains draft until the remaining cases are reviewed and the final pattern analysis is recorded.

## Evidence boundary

This phase evaluates controlled, coding-agent-simulated Story Discovery recommendation experiences grounded in the qualified Phase D synthetic corpus. It does not establish live-provider generation quality, live-model comparative-judge quality, broad writer usability, or population-level preference.

## Protocol amendment after Case 1

Case 1 exposed a missing condition in the original founder-review protocol: a recommendation cannot be meaningfully adjudicated as “best” if the author has not supplied enough intent to define what “best” should optimize for.

The Phase D naturalistic fixtures supplied a premise while leaving the CLI-level `genre`, `medium`, and `mode` constraints unset. Candidate outputs could propose genre, audience, and target experience, but those proposal fields are not equivalent to prior author intent.

Phase E therefore adds an **intent-adequacy gate** before recommendation adjudication.

For the remaining cases, the founder is given a clearly labeled **simulated author brief** containing:

- primary genre;
- target audience;
- target emotion / reader experience;
- hard story constraints.

These briefs are research scaffolding. They are not evidence that the current Story Discovery front door collects these fields.

A fifth valid first-pass outcome is added:

- **Not adjudicable — insufficient author intent**: the directions may be distinct and the recommendation may be understandable, but there is not enough declared author intent to justify ranking one direction as best.

This is distinct from **False choice**, which is reserved for cases where the directions are not meaningfully different stories.

A new failure class is therefore recognized:

- **CONTEXT / INTENT FAILURE** — the recommendation problem is under-specified relative to the author’s desired genre promise, audience, target experience, or hard constraints.

## Case 1 — retired astronaut / mission-control chatter

### Original premise

> A retired astronaut hears mission-control chatter in her empty apartment.

### Simulated recommendation

`Dead Channel` was recommended over `One More Orbit` and `Ground Loop`.

### Founder response

- **Literal reaction:** False choice.
- **Meaningful choice:** Yes; the three directions are genuinely different stories worth choosing between.
- **Recommendation clarity:** Yes; the founder understood why `Dead Channel` was presented as superior.
- **Insight:** The founder asked for the initial premise and the baseline story intent needed to compare the options.
- **Alternative fairness:** Yes; both alternatives remained attractive.
- **Authority feel:** Yes; Auteur was opinionated without making disagreement feel wrong.
- **Choice:** No choice was possible because the baseline primary genre, target audience, and target emotion were absent.

### Research classification

**CONTEXT / INTENT FAILURE**, not search-diversity failure.

The case demonstrates that meaningful option diversity and a coherent rationale are insufficient by themselves to justify a “best” recommendation. Comparative judgment needs a declared optimization target or must explicitly frame itself as exploratory rather than author-intent-optimal.

## Case 2 — impossible murder in one elevator

### Simulated author brief

- **Primary genre:** fair-play impossible-crime / closed-circle mystery.
- **Target audience:** adult mystery readers who enjoy deduction, clueing, and reconstructing an apparently impossible crime.
- **Target emotion:** claustrophobic suspicion → mounting puzzle pressure → satisfying reconstructive revelation.
- **Hard constraints:** six strangers remain within the elevator; no supernatural explanation; the killer never leaves; final solution should be physically possible and retrospectively fair.

### Simulated recommendation

`Between Floors` was recommended over `Sixth Passenger` and `All Doors Closed` because it makes the physical impossibility and elevator mechanics the primary mystery engine.

### Founder response

- **Intent adequacy:** Yes.
- **Reaction:** Strong agreement.
- **Baseline fit:** Yes; all three directions reasonably fit the brief.
- **Meaningful choice:** Yes.
- **Recommendation clarity:** Yes.
- **Insight:** Yes; the comparison clarified what kind of mystery the author was choosing.
- **Alternative fairness:** Yes.
- **Authority feel:** Yes.
- **Founder preference:** keep `Between Floors` as the primary engine, but—given a personal preference for maximalism and mixed causation—integrate compatible identity and concealment mechanisms from the two alternatives if that can be done without violating the original genre/audience/emotion promise.

### Research classification

**CLEAR SUCCESS with COMPOSITION OPPORTUNITY.**

The recommendation correctly identifies the primary engine relative to the declared author brief. The founder’s desire to combine alternatives is not evidence that the recommendation failed. Instead it reveals a distinct post-recommendation interaction:

> Keep the recommended primary engine, then selectively borrow compatible mechanisms from alternatives without allowing them to displace the primary reader promise.

For this case, a coherent composition would be:

1. `Between Floors` supplies the physical-opportunity / fair-play engine.
2. `Sixth Passenger` supplies motive and identity complexity.
3. `All Doors Closed` supplies epistemic obstruction through independent concealment.

The hierarchy matters. Treating all three as equal centers could blur the fair-play impossible-crime promise; treating the latter two as subordinate causal layers preserves the brief while supporting a more maximalist story.

## Emerging Phase E signals

After two cases:

1. **Intent adequacy is a prerequisite for comparative “best.”** A sparse premise may support exploration, but not necessarily a justified author-intent-optimal recommendation.
2. **Meaningful alternatives can be composable rather than mutually exclusive.** Auteur may eventually benefit from a post-recommendation operation such as “keep this engine, borrow these mechanisms.”
3. **Strong recommendation and author authority are compatible.** In both cases the founder found the recommendation understandable and non-coercive.
4. **No production change is justified yet.** The intent gap is a strong signal from Case 1, and composition is an opportunity from Case 2, but Phase E should complete the remaining high-information cases before routing implementation work.
