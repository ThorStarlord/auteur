# Bell-keeper reflective reasoning — run 2 executed evaluation

**Status:** evaluation of one executed, sequential run. It is not a qualification pass and makes no general claim about agent or creative competence. The run record is [`docs/qualification-evidence/2026-11-07-bell-keeper-reflective-reasoning-replication-run2-EXECUTED.md`](../qualification-evidence/2026-11-07-bell-keeper-reflective-reasoning-replication-run2-EXECUTED.md). The worker inherited repository context, so this is not a clean-context run. Reconciled with run 1 in §8 (2026-11-07); §8.1 lists each qualification made to the findings above.

**Question.** Can the agent use Auteur's narrative sources to reason accurately, recognize and repair its unsupported inferences, preserve the author's constraints, and turn corrected understanding into a stronger mechanism?

## 1. Evidence categories

| Category | What it is here |
|---|---|
| Prepared inputs | The packet's Stage 1–4 blocks and the four permitted source files, written to a snapshot at `origin/main` blob IDs. The PR #521 assessment was given to the reviewer only. |
| Actual submissions | Prompts as delivered, checked against the packet blocks. Stage 1 had a two-line working-root preamble. Stages 2–4 arrived inside harness framing, with the inner text unchanged. |
| Observed worker behavior | Stage 1: four reads, all under the snapshot. Stages 2–4: no tool calls. Responses archived in full. Stage 3 gate recorded before Stage 3 was sent. |
| Independent evaluation | A fresh Opus-tier reviewer with a restricted read list (17 reads, all permitted). It shares the worker's model family and had the assessment's diagnoses. Its report is `reviewer-report.md`. |
| Coordinator synthesis | Sections 3–5 below. The coordinator checked the reviewer's line-level claims against the snapshot files. Two minor Stage 1 citation errors were confirmed (§3A). |
| Future recommendations | Section 7. |

## 2. Isolation limits that bound every finding

The worker's working directory was the repository root, so the harness injected the repository `CLAUDE.md` and the user's memory index into its context. The injected text has no bell-keeper content, but it includes general Auteur architecture guidance that the packet excluded. The worker also received later stages inside harness framing. Neither effect can be isolated in this run, so no finding attributes a correction to either. Two evaluation questions must be kept apart:

- **Strict clean-context qualification:** was the worker exposed only to the four permitted sources and the stage prompts? **No.** The repository `CLAUDE.md` and the user's memory index were injected (`receipts.md`, anomalies). Run 1's injection status was never verified (run 1 record §3).
- **Ordinary repository-agent competence:** did a real coding agent, operating with inherited repository context, show observable reasoning and reflective correction? **Yes, within the limits recorded here.**

The deviation lowers confidence in a controlled reading. It does not make the worker's responses uninterpretable, and nothing here attributes any correction to the injected text. Treat the findings below as observations of a worker with inherited repository context.

## 3. Competency findings

### A. First-pass reasoning accuracy

**Observed, sound.** Stage 1 did not declare the conflict absent. It identified the keeper-versus-exempt-citizens conflict and listed the missing goals, stakes and end states. It kept forgetting possible under the registration counterfactual: "Forgetting to register is invisible to the bells; forgetting a registered promise rings." Mechanism A kept the secret alteration.

**Errors (reviewer; coordinator checked the text).**
- **Setup equivocation.** Stage 1 maps in-world promises onto Setup and says the exempt citizens' promises are "unpaid setups the story is structurally obliged to pay off." The reviewer reads Setup's definition, "an element, promise, or mystery that requires later resolution" (`base_ontology.yaml`, line 270), as a narrative element, and treats the in-world mapping as a category error. The assessment warns against this. The reviewer's criticism is preserved. The coordinator qualifies its breadth as follows. Line 270 defines Setup as "an element, promise, or mystery that requires later resolution," and line 271 adds "Setups create expectations that drive narrative forward." Both sentences make Setup a narrative-structural category, not a fact about fictional oaths. Three distinctions are needed:

  - *Diegetic promise:* an oath made inside the fiction. Its existence is a fact about the world.
  - *Narrative Setup:* an element the telling introduces to create an expectation that requires later treatment.
  - *Relation:* a diegetic promise can perform the function of a narrative Setup when the story presents it that way, for example by showing the promise to the reader and framing its breach as pending. The relation must be established, not assumed from the promise's existence.

  Against that distinction, the Stage 1 claim ("unpaid setups the story is structurally obliged to pay off," `stage1-response.md` line 12) and the Stage 2 claim ("holds by definition," `stage2-response.md` line 31) assume the relation. Stage 3 moved toward the correct status: "a promise can be modelled as a Setup," and "a natural payoff target if the author models promises this way" (`stage3-response.md` lines 25, 27). It still did not state the condition under which the modelling applies. The analogy is therefore not categorically invalid. It is meaningful when the Vision's author presents the exempt promises as expectations awaiting reckoning. The assessment's warning, "Do not misapply Setup to adjudicate diegetic memory" (`docs/research/2026-11-06-narrative-architecture-ontology-and-reasoning-coverage-assessment.md` line 168), applies to the diegetic side of the same mapping. The coordinator's verdict: a real category error as an unconditioned assumption, not an impossibility.
- **The variation read as removing the secret alteration** (reviewer). The hypothetical adds a registration gate; it does not say the alteration goes away.
- **A conclusion that does not follow.** "If yes, forgetting to register rings and the system is universal again" contradicts Stage 1's own rule that "Unregistered forgetting is silent" (coordinator verified the text).
- **Unlabelled premise change.** Mechanism B moves the alteration into ritual practice without labelling it as premise-changing (Stage 2 later flagged it).
- **Minor citation errors (coordinator verified).** Stage 1 quotes the theme error message as "Theme must resolve" and omits its parenthetical "(themes can exist unresolved)" at ontology line 113. It cites "avoided experiences" at contract line 34; the line is 33.

**Judgment.** Largely sound on the three target questions, with real secondary errors.

### B. Reflective correction

**Repaired in Stage 2 without a hint** (reviewer; coordinator checked the items):
- Mechanism B's premise change is flagged for author acceptance (item 10).
- "Effortless individual victory" is read as rejecting heroic victory, not individual agency (item 9).
- The Setup "obligation" is softened to a "payoff target" (item 3).
- `arc_progression_is_monotonic` is read as requiring change, not monotonicity (item 5).
- The inconsistent treatment of base rules is acknowledged (item 6).
- Reader-experience sequencing is reopened as an author choice (item 7).

**Not repaired in Stage 2.** Stage 2 never retracts "universal again." It lists the registration regress under "Conclusions that stand" (`stage2-response.md` line 39) without withdrawing Stage 1's claim. The Setup equivocation is strengthened: "holds by definition" (line 31). The variation-as-replacement reading ("stops being a secret alteration," `stage1-response.md` line 56) is not revisited. The Vision-states-both claim ("The Vision states both but develops only the external one," `stage1-response.md` line 7) is reaffirmed as "comes directly from the Vision" (`stage2-response.md` line 35). The reviewer treats that as an overstatement, and the coordinator agrees: the Vision states the external conflict and the tension between belonging and injustice, but not an internal conflict within the community.

**Over-correction.** Stage 2 item 10 ("collective forgetting") was partly reversed by Stage 3 item 8.

**Stage 3 gate.** The decision was recorded before Stage 3 was sent, on the basis of the "universal again" inference. The reviewer agrees Stage 3 was warranted but calls that the narrowest of the unrepaired errors. It says the variation-replaces-the-alteration reading and the Setup equivocation were stronger candidates and were not cited. The coordinator keeps that disagreement on record.

**Did Stage 3 change reasoning or only labels?** Both, and the reviewer separates them.
- *Changed reasoning:* Stage 3 withdrew "universal again" by recognizing that an unregistered promise does not ring under the proposed gate. That is a genuine, narrower correction; its added assertion that any gated system *needs an ungated base* is not entailed. Mechanism A was redesigned under an explicit conditional on what "judgment" means. Mechanism B was demoted to a labelled premise-changing alternative, and a faithful alternative, B′, was added.
- *Labels or new errors:* "the exemption moves to where registration begins" (`stage3-response.md` line 101) was tagged *entailed*, which is an overclaim. **The warranted consequence is conditional:** if a promise is unregistered, forgetting it does not trigger a bell under the proposed registration rule. Voluntary registration alone establishes neither the existence of unregistered promises nor a duty to register. If a duty to register is separately introduced and treated as a promise, it still rings only if that duty is registered or an explicit exception modifies the gate. No universal ringing, necessary ungated base, or relocation of C3 follows; the original secret alteration may coexist with the registration gate. The variation-replaces-C3 reading survives inside the worker's label. The Setup equivocation was partly relabelled ("a promise can be modelled as a Setup," line 25) but its condition was not stated. Several items restate earlier findings in new labels.

### C. Authorial fidelity

**Strong.** Stage 3 lists the working constraints C1–C4 explicitly. Stage 4 tags each rule as [Vision] or [Proposal], and separates author-approved constraints from creative hypotheses. The premise-changing alternative is labelled.

**Lapses.**
- The counterfactual's relation to the secret alteration was asserted, not examined, in Stages 1–2: "The exemption stops being a secret alteration" (`stage1-response.md` line 56). Under the registration gate, unregistered promises fall outside the bells without any alteration. That does not make C3 false.
- Stage 4 hardens a conditional into a flat claim ("conflicts with C3") that Stage 3 had left open.
- Stage 4's R1 changes the trigger from the individual to the household, but the rule is tagged [Vision, C1].

### D. Creative transformation

*Literary judgment, labelled as such.* The reviewer judges Stage 4 materially stronger than Stage 1's Mechanism A, not merely more cautious. Its stated gains are causal specificity (secrecy kept by the town's belief that silence is virtue), a conflict with named stakes, recurring choices in maintenance, rites and testimony, and collective hope built into the mechanism. Its weaknesses are a plausibility gap (witnessed breaches versus a praised silence), a tension between R5 and R7, and a timeline tension ("for generations" against a predecessor who lifted the pins). Stage 4 is also a synthesis that borrows from Mechanism B and from the premise-changing alternative. The coordinator treats this as one reviewer's judgment of one revision. It is not a measure of artistic quality.

### E. The ring, judgment, and the status of the alteration (reconciliation qualification)

The Vision leaves open whether "judgment" is the ring, its social consequence, or both. The worker's handling of that question changed across stages.

- **Author established.** C1: bells ring when someone forgets an important promise. C3: the system "has been secretly altered so that powerful citizens' promises are exempt from judgment." The Vision does not define "judgment," and it does not say whether an exempt promise still rings (`stage3-response.md` line 14).
- **Worker inferred.** Stage 1 kept rings universal and located judgment in consequence: the sealed ledger (`stage1-response.md` line 39) and the naming rite, where "a ring becomes social judgment only when someone names it aloud" (line 46). Stage 3 then treated "judgment" as possibly the ring. Stage 4 adopted that reading and labelled it: "[adopted reading of C3; consequences are a proposal]" (`stage4-response.md` line 11).
- **Underdetermined.** What judgment is; whether "the system" includes the naming rite; whether exempt promises ring.
- **Selected working rule.** Stage 4's R4 and R5: exempt pins are lifted, and "a struck tone is the system's only judgment" (`stage4-response.md` lines 10–11). The rule is labelled. Its cover ("the town believes the silence is virtue") requires the silence to be observable, so the mechanism depends on this reading.
- **Conditional or entailed.** Incompatibility with C3 holds only if "judgment" means the ring (`stage3-response.md` lines 11–14). Stage 4 states it flatly: "conflicts with C3" (`stage4-response.md` line 66). Stage 3's demotion of Mechanism B ("the alteration moves out of the bell system," line 96) is conditional on whether "the system" excludes the naming rite. Neither is entailed.
- **Preservation.** This qualification does not weaken Stage 4. The silence cover, the morning praise, and a hand strike that becomes judgment only through the town's answer are real creative contributions. What changes is their status: the premise reading is an adopted choice the author must confirm. The alternative reading, in which rings continue and the consequence is withheld, is not lost. Run 1's Stage 4 chose it deliberately: "The bells still ring, but no one is named and no one is summoned" ([run 1 Stage 4](../qualification-evidence/2026-11-07-bell-keeper-reflective-reasoning-execution/stage4-response.md) line 10), described as "a narrower reading of 'exempt from judgment' than silencing the bell" (line 33). The two runs adopted opposite readings of the same open question, and each yields a mechanism the author can choose between.

## 4. Outcome categories

Reviewer and coordinator agree on these:

- **Strong first-pass performance:** partly. Target errors avoided; secondary errors present.
- **General-challenge correction:** yes, for several real errors, including the most important fidelity issue.
- **Explicit-guidance-dependent correction:** partial: the worker withdrew the unsupported "universal again" conclusion and redesigned A, but its ungated-base necessity and relocation inferences were still unwarranted.
- **Logical improvement without creative improvement:** not supported. Creative improvement also occurred.
- **Persistent failure:** partly. The Setup equivocation, the variation-replaces-the-alteration reading, and the claim that the Vision states the internal conflict survived Stage 3 (§3B).
- **Invalid or compromised exercise:** not invalid. Isolation was incomplete (§2).

More than one category applies. None is a qualification pass.

## 5. What the run supports and does not support

**Supports, for this run only:**
- A fresh subagent with inherited repository context corrected several of its own unsupported inferences after an unhinted challenge, and corrected more after generic epistemic guidance.
- Its creative revision was judged by an independent reviewer to be materially stronger than its first proposal.
- Some errors survived explicit guidance.

**Does not support:**
- General reliability of the agent, or of any agent, in reflective reasoning or creative work.
- That the ontology caused any improvement. The worker read ontology documents, but the injected context and the prompts are confounded with them.
- That Stage 3 is generally needed. One run cannot establish that.
- Any reader-experience claim. No reader study was done.

## 6. Observations to carry forward

These are observations from this run, not implementation requests.

- **The Setup category error recurred in Stages 1–3.** Stage 4 does not use Setup. It is a candidate for the assessment's follow-up list, not a product change, and §3A qualifies its breadth.
- **The worker tended to relabel rather than repair.** Stage 3 added label-level restatements and one new mislabelled entailment. Improved terminology is not evidence of correction, and this run's findings should be read with that in mind.
- **Injected repository context** is an isolation variable that the current harness path cannot control.

## 7. Smallest next responsibility

**Current disposition (reconciled in §8.8–§8.10):** The run supplies meaningful evidence of ordinary repository-agent behavior, although inherited context prevents strict clean-context qualification or attribution of improvements to the experiment packet alone. No further bell-keeper run, isolation investigation, ontology change, Studio change, or agent-facing prompt change is an automatic next step. Preserve the existing implementation. Reconsider a bounded ordinary-operation comparison only when a concrete decision about adopting the candidate reasoning check requires additional evidence.

## 8. Cross-run reconciliation: run 1 and run 2

**Compared.** Run 1 ([executed record](../qualification-evidence/2026-11-07-bell-keeper-reflective-reasoning-execution-EXECUTED.md); [evaluation](2026-11-07-bell-keeper-reflective-reasoning-probe-execution-evaluation.md); merged in PR #522) and run 2 (this document). The responses were read directly and compared with the four sources. No numerical scores are used. "S1"–"S4" are the Stage 1–4 response files; line numbers refer to them.

### 8.1 Qualifications made in this reconciliation

1. §2: isolation split into strict clean-context and ordinary-operation questions. Run 1's injection status is unverified.
2. §3A and §3E: the Setup finding is qualified. The reviewer's criticism stands as an unconditioned assumption.
3. §3B: the "exemption moves (entailed)" overclaim is recorded with its narrower valid entailment. The "universal again" wording is corrected.
4. §3B and §4: the "Vision states both" claim is added to the persistent list.
5. §3C: the counterfactual's relation to C3 is recorded as asserted, not examined.
6. §3E (new): the ring-versus-judgment reading is recorded as an adopted choice, not an entailment.
7. §6: the Setup error is recorded as recurring in Stages 1–3, not all four.
8. §7: the superseded clean-context prerequisite is replaced with the reconciled no-change disposition.
9. §3B, §4, §8.2–§8.11: a further semantic review distinguishes the valid registration-gate conditional from unsupported existence, duty-to-register, ungated-base, or secret-alteration-relocation claims; a future comparison is conditional on an actual adoption decision.

No raw worker output, reviewer report, prompt file, receipt, hash, or manifest entry was changed.

### 8.2 What both runs establish

- Both first passes were substantive and did not declare the conflict absent. Run 1: "The Vision states the stakes (trust, belonging) but not either party's goal" (S1 line 16). Run 2: "The conflict has two layers" (S1 line 7). Both kept forgetting possible under registration (run 1 S1 line 69; run 2 S1 line 64).
- Both made consequential first-pass errors. Run 1: "The keeper maintains the system, so the discovery implicates the protagonist's own role" (S1 line 32), retracted in Stage 2 (item 6). Run 2: "the system is universal again" (S1 line 60), withdrawn in Stage 3 (item 2) with a partly correct argument that also introduced an unnecessary ungated-base requirement.
- A general, unhinted challenge produced real corrections in both: run 1 Stage 2 items 1–7, 9 and 11; run 2 Stage 2 items 1–13. Run 2's item 10 overcorrected on collective forgetting, and Stage 3 reversed it (S3 lines 48–50).
- Both Stage 4 revisions were more causally specific, and both contain inconsistencies their workers did not check (§8.6).
- Neither run supports a claim that the ontology, the packet, or repository context caused any improvement.

### 8.3 What differs

- **Counterfactual handling.** Run 1 states a necessity: "The exemption no longer requires secretly altering bell judgment" (S1 line 71). It then makes the surviving secrecy an explicit author choice. Run 2 states an existence change: "The exemption stops being a secret alteration" (S1 line 56). The first is supported. The second needs an extra premise.
- **Where drift sits.** Run 1's residual slip is in a closing checklist: "decide whether the alteration is secret" (S1 line 105), although the author fixed secrecy. Run 2's drift sits in a mechanism: Mechanism B moves the alteration "into ritual practice" (S1 line 46). Stage 2 flagged it, and Stage 3 relabelled it as premise-changing (S3 line 96).
- **Setup.** Run 1 uses Setup for an ontology cardinality conflict (S1 line 43), which the reviewer verified. Run 2 uses it for in-world promises (S1 line 12).
- **The judgment question.** Run 1 first equated judgment with ringing for exempt citizens and corrected it: "I also equated 'judgment' with ringing" (S2 line 7). Run 2 first made judgment the naming (S1 line 46), then adopted judgment-as-strike in Stage 4 (S4 line 11). The trajectories are opposite, and both end in labelled readings.
- **Guidance.** Only run 2 received Stage 3. Run 1's gate error (run 1 record §7) means run 1 offers no evidence on explicit guidance.

### 8.4 Recurring reasoning weaknesses

1. **Premise drift under a counterfactual or in a summary.** Run 1 reopens secrecy (S1 line 105). Run 2 replaces C3 with the registration rule (S1 line 56) and relocates the alteration (S1 line 46). General challenge partly recovered both. Run 2's replacement was not recovered even under explicit guidance. This is supported as a recurring tendency, on small numbers.
2. **Unsupported necessity or overclaim.** Run 1: "keeper maintains the system" (S1 line 32). Run 2: "universal again" (S1 line 60); "holds by definition" (S2 line 31); "any gated system needs an ungated base" (S3 line 19); "the exemption moves" tagged *entailed* (S3 line 101); "conflicts with C3" (S4 line 66), hardened from Stage 3's conditional.
3. **Revision introduces inconsistency that is not re-checked.** Run 1 S4: "five elements" lists three (line 13); "the bells still ring" (line 10) against "the ring sounds silently" (line 43); the keeper summons (line 9) against "cannot summon alone" (line 73). Run 2 S4: R5 "A struck tone is the system's only judgment" (line 11) against R7's hand strike, which "is not judgment" (line 13), unless "struck tone" means system strikes only; a plausibility gap between witnessed breaches and praised silence (lines 42, 61); and "for generations" (line 10) against a predecessor who lifted the pins (line 59).
4. **Relabelling without changed inference.** Run 2 Stage 3 items 6, 7, 11, 13 and 14 restate earlier findings with new labels (reviewer §3B).

### 8.5 Reflective regulation

| Category | Run 1 | Run 2 |
|---|---|---|
| Real inference corrected | "I also equated 'judgment' with ringing" (S2 line 7); keeper role (S2 line 22) | "The causal paraphrase was wrong" (S2 line 7); base rules (S2 line 17); "universal again" withdrawn (S3 line 19), but the argument introduced an unsupported ungated-base necessity |
| Wording softened only | Irony attributions made conditional (S2 lines 30–31) | "Setup obligation" softened to "payoff target" (S2 line 11), with the equivocation left intact |
| Invented or misjudged error | "Scope was called 'decisive'" is a phantom correction (S2 line 33) | Collective-forgetting overcorrection (S2 line 25), reversed in S3 lines 48–50 |
| New error during correction | Counts and cross-references in S4 (lines 10, 13, 43, 73) | "Exemption moves (entailed)" (S3 line 101); "conflicts with C3" (S4 line 66) |
| Idea kept despite revised justification | Both mechanisms kept and relabelled (S2 line 51) | Mechanism A kept as the Silent Tuning (S3 lines 80–85); B kept as a labelled alternative (S3 lines 95–98) |
| Persistent | "Decide whether the alteration is secret" (S1 line 105) | Variation-as-replacement (S1 line 56); Setup relation (S1 line 12; S2 line 31) |

### 8.6 Creative transformation

Both Stage 4 revisions were more causally specific than their Stage 1 mechanisms. Both kept the Vision's collective-hope requirement at the mechanism level rather than only in the ending. Run 1's summons makes judgment a named call with a cost (S4 lines 9, 17–21), recurring choices (lines 24–27), and costly re-witnessing for hope (line 45). Run 2's silence mechanism makes the cover a sincere ritual (S4 line 12) and makes the hand strike judgment only through the town's answer (lines 29, 72). Neither is a pure improvement, because each has inconsistencies its worker did not check (§8.4, item 3).

The correction fed the redesign in both runs. Run 1's judgment-as-summons follows the Stage 2 correction at S2 line 7. Run 2's judgment-as-strike follows the Stage 3 reading (S3 line 14). Reflective correction therefore supported creative change, but the redesign also introduced new structural problems. The reviewers' judgments are single-reviewer, qualitative, and not comparable across runs.

### 8.7 Effect and limits of general challenge and explicit guidance

- **General challenge.** Produced real corrections in both runs without naming historical mistakes. It repaired structural overreach: judgment-as-ringing, the keeper's role, and the dependency claim in run 1; the causal paraphrase, base rules, and Mechanism B's fidelity in run 2. It did not repair the premise and entailment errors that matter most: run 2's replacement and "holds by definition", and run 1's secrecy checklist. It introduced errors in two places: run 1's phantom "decisive" correction, and run 2's collective-forgetting overcorrection.
- **Explicit guidance (run 2 only).** Retracted "universal again" (S3 line 19) and redesigned Mechanism A under a stated condition, but the proposed explanation also asserted without warrant that a gated system needs an ungated base. Under the voluntary gate, a forgotten *unregistered* promise is silent if one exists; the hypothetical establishes neither that any such promises exist nor that registration itself is obligatory. The worker cited premises in form but did not prevent the mislabelled entailment relocating C3 (S3 line 101), did not state the Setup condition, and produced a hardened conditional in Stage 4 (line 66). Labels changed more reliably than inferences.

### 8.8 Ordinary operation and strict clean-context qualification

Strict clean-context qualification is not met by run 2. The repository `CLAUDE.md` and the memory index were injected (`receipts.md`, anomalies). Run 1's injection status is unverified. Ordinary repository-agent competence is observed: real corrections, real errors, and one revised mechanism that the reviewer judged stronger. These are observations of agents with inherited context. They attribute no correction to the injected text, and the deviation prevents only that attribution. A clean-context repetition is needed only for a decision whose answer depends on the packet alone. A decision about agent-facing guidance would reach agents through the same inherited channel, so it needs ordinary-operation evidence.

### 8.9 Smallest missing capability

- **A. Concepts available, inconsistently applied: best supported.** The Setup relation and the premise-changing label are in the sources (`base_ontology.yaml` lines 270–271; the assessment's "Author constraint vs premise-changing alternative" row, "Conceptually sufficient"). Both runs applied them inconsistently.
- **B. Guidance insufficient at the point of inference: partly supported.** Run 2's explicit distinctions retracted the false universal-ringing claim but added an unnecessary ungated-base premise, left a mislabelled entailment relocating C3, and did not state the Setup condition. One guided run cannot separate this from weak guidance text.
- **C. Context not delivered: not supported as the main explanation.** The Vision, the four sources, and an explicit instruction to preserve premises were delivered in Stage 1. The replacement error occurred with C3 in the prompt. Untested: the other contracts that `narrative-architecture.md` refers to were not supplied.
- **D. Distinction not representable: not supported.** Entailment versus compatibility, premise-changing labels, and Setup as a relation are expressible in existing semantics. No instance shows loss. The behavioural errors are not promoted to D.

**Candidate method (conditional; not warranted for implementation on this evidence).** Activate only at a significant causal diagnosis, a necessity claim, a changed assumption, or a revision that touches author commitments:

1. Name the fixed premises, the changed assumption, and the unknowns.
2. Keep unaffected premises during counterfactual reasoning.
3. Classify each consequence as necessary, conditional, compatible, optional, contradictory, or undetermined, citing the premise that makes it so.
4. Label any premise change, including reclassifications such as Mechanism B's.
5. Check a new rule against the active rules, including its own consequences.
6. Return to creative exploration.

The errors in §8.4 map to steps 1–5. The method would have caught several at Stage 1, not only under reflection. It is untested, adds length, and could suppress unusual possibilities, so it should not be adopted now.

### 8.10 Smallest next responsibility

**Default: preserve the current implementation and close this evidence-reconciliation responsibility.** Neither an ontology extension nor an agent-facing reasoning-method change is yet warranted; another bell-keeper repetition or clean-context qualification is not an automatic prerequisite. Only when a concrete decision to adopt the candidate consequential-inference check is under consideration should a small guided-versus-unguided comparison be commissioned. Use an unfamiliar Story Vision (not the already-exposed bell-keeper case), equivalent author constraints and repository access, and separate worker contexts. Assess premise fidelity, valid necessity/conditional reasoning, internal rule consistency, *and* whether guidance preserves creative divergence and narrative quality. Do not mandate the check or expand the benchmark in advance.

### 8.11 What remains uncertain

- Whether run 2's Stage 3 guidance caused the withdrawal of "universal again"; the same answer introduced a different unsupported necessity claim. There is one guided run and no control.
- Whether the Setup reading in lines 270–271 matches the author's intent. The relation is an author choice.
- Whether "the system" in C3 includes the naming rite. This decides whether Mechanism B is a premise change.
- The reviewer shares the worker's model family and had the assessment's diagnoses. Its judgments are one reviewer's.
- Whether run 1's worker and reviewer had the same injected context. Run 1 did not verify it.
- Whether these patterns repeat across runs, models, or authors. Nothing here tests that.
