# Phase E — Founder Creative Adjudication Findings

## Status

In progress. Three founder cases have been adjudicated. The research PR remains draft until the remaining cases are reviewed and the final pattern analysis is recorded.

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

## Protocol amendment after Case 3

Case 3 exposed a second missing condition: candidate alternatives can sound different while remaining too similar at the level of external causal action.

Phase E therefore adds a stronger **narrative-engine distinctness** criterion:

> Two candidates are not meaningfully distinct merely because they use different thematic framing, metaphors, institutional vocabulary, or stated advantages. A materially different narrative engine should change the causal strategy by which the protagonist pursues the central objective, and therefore imply different major actions, obstacles, reversals, and climax mechanics.

A useful diagnostic shorthand is:

> Different engine ≠ different interpretation. Different engine = different causal strategy producing meaningfully different scene pressure and resolution mechanics.

This does not require candidates to share no ingredients. It requires their **primary causal engines** to be separable enough that an author is choosing among genuinely different stories rather than differently framed versions of the same operational plan.

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

## Case 3 — no-stealing / no-lying museum heist

### Simulated author brief

- **Primary genre:** constraint-driven ensemble heist / caper.
- **Target audience:** adult readers who enjoy elaborate plans, specialized team roles, procedural ingenuity, reversals, and clever exploitation of rules.
- **Target emotion:** impossible constraint → fascination with the plan → escalating operational pressure → exhilarating public reversal.
- **Hard constraints:** nothing may be stolen or permanently removed; nobody on the crew knowingly makes a false statement; the crew must defeat the corrupt museum director through an orchestrated operation; the museum itself should be essential to the scheme.

### Simulated recommendation

`Nothing Missing` was recommended over `Open House` and `The Honest Con`.

### Founder response

The founder liked the overall idea but could not identify sufficiently concrete differences among the alternatives. The key question was whether the options differed in **actual external acts** or merely in aesthetic / interpretive framing.

The founder’s reading was especially that `Nothing Missing` and `Open House` could collapse into essentially the same operational chain:

> gain access → uncover or surface records → authenticate evidence → maneuver the institution into revealing it → expose the director publicly.

`The Honest Con` was somewhat more distinct because its external sequence could center on staging an exhibition, manipulating expectations without false statements, provoking the director, and causing self-exposure.

### Research classification

**PARTIAL FALSE CHOICE / SEARCH–CHOICE WEAKNESS.**

The candidate set is differentiated rhetorically more strongly than it is differentiated causally. This is not yet a clean three-way narrative-engine choice.

The recommendation itself may still be defensible, but the search space is too compressed for the founder to evaluate it as a strong comparative recommendation.

A stronger version of the candidate set would differ at the level of primary verbs and climax mechanics, for example:

1. **Evidence engine:** retrieve → authenticate → connect → disclose; climax is an irrefutable provenance proof.
2. **Systems engine:** schedule → trigger → constrain → force choice; climax is the director being trapped by mutually incompatible institutional obligations.
3. **Social-engineering engine:** stage → misdirect → provoke → expose; climax is the director incriminating himself through his response to a truthful operation.

Those options could still share the same premise and constraints while producing materially different major scenes, obstacle structures, and climax forms.

## Emerging Phase E signals

After three cases:

1. **Intent adequacy is a prerequisite for comparative “best.”** A sparse premise may support exploration, but not necessarily a justified author-intent-optimal recommendation.
2. **Narrative-engine diversity must be causal, not merely rhetorical.** Different labels, themes, or institutional framings are insufficient when the protagonist’s external strategy and major scene chain remain substantially the same.
3. **Meaningful alternatives can be composable rather than mutually exclusive.** Auteur may eventually benefit from a post-recommendation operation such as “keep this engine, borrow these mechanisms.”
4. **Strong recommendation and author authority remain compatible.** Cases 1 and 2 both showed that Auteur can sound opinionated without making disagreement feel wrong.
5. **No production change is justified yet.** The intent gap and causal-distinctness criterion are now strong research signals, while composition remains an opportunity. Phase E should complete the remaining high-information cases before routing implementation work.
