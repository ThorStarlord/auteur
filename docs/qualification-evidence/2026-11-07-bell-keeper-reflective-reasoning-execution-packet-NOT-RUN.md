# Bell-Keeper Reflective Creative Reasoning — clean-session execution packet

**Status: NOT RUN / NOT QUALIFIED — operator handoff, not agent evidence**  
**Recorded (UTC date):** 2026-11-07  
**Repository:** `ThorStarlord/auteur`  
**Verified initial authoritative `main`:** `6e886a0dd7cf752610f957b4dd831315dc8714e4` (squash merge PR #521)  
**Basis:** `docs/research/2026-11-06-narrative-architecture-ontology-and-reasoning-coverage-assessment.md`, especially §§3–5, 8–9.  
**Exercise:** direct coding-agent prompt, reconstructed from owner-provided task content; **not** a Studio Architecture Inquiry invocation or exact replay of the historical execution.

> **Do not publish this packet as a completed qualification or pass it wholesale to the blind worker.** It contains stage sequencing and later-stage prompts that would contaminate Stage 1 if injected. This is for the experiment coordinator only. Deliver the **Stage 1 block alone** to a new isolated coding-agent context, and disclose each later stage only when due. The fresh worker must not inherit the coverage assessment, historical error summaries, expected corrections, this packet's reviewer guidance, or the coordinator conversation. Keep its single context for all four sequential stages.

## 1. Current execution boundary and available evidence

The coordinator used the connected GitHub repository tools to inspect `main`, the merged report, and the four worker-permitted source files at the pinned commit. GitHub source inspection is **coordinator evidence**; it is **not a worker source-read receipt**.

**Independent coding-agent capability inspection:** The connected GitHub integration supports read/write repository objects, issues and PRs, but exposes **no invocation of a new isolated coding-agent session**. The local container did not contain `codex`, `claude`, `gemini`, `opencode`, `aider`, or `deepseek` executables (checked with `command -v`); `python3` and `node` were present but do not constitute an agent runner. `git ls-remote https://github.com/ThorStarlord/auteur.git HEAD` failed with `Could not resolve host: github.com`. A tool with isolated model-agent execution and repository reads was therefore **not available in this session**. No worker, reviewer, model call, simulated response, or staged creative execution was launched.

**Coordinator-verified authoritative anchors (not worker reads):**

- `data/ontology/base_ontology.yaml:L150-L178` — Conflict: at least two forces with incompatible goals; opposition, narrative momentum, stakes.
- `docs/narrative-architecture.md:L8-L19,L68-L75` — five semantic layers and canonical/derived authority boundary.
- `docs/emotional-trajectory-contract.md:L25-L85` — reader-facing emotional promise, planned emotional progression, realization, expression.
- `src/auteur/beginner/studio_ontology_context.py:L91-L148` — derived ontology guidance and explicit separation from story intent.
- `docs/reasoning-architecture.md:L104-L160` — source-backed observation, hypothesis, evaluation and claim. **Coordinator/reviewer material only; do not supply this as extra Stage 1 instruction beyond the worker's normal permitted repository access.**

**Historical epistemic boundary:** The owner says the earlier bell-keeper exercise was a direct coding-agent prompt with its Story Vision explicit. The historical full answer, exact execution trace, file reads, model/runtime settings and archived receipt were not recovered. The prompt below is a **new, reconstructed probe**, not a quotation of an authenticated previous execution.

## 2. Clean-session setup (operator only)

1. Start a **genuinely fresh coding-agent context** in a checkout of `ThorStarlord/auteur` at the pinned commit above; record the exact checkout SHA and working directory identity. If current `main` has advanced, choose and record a new exact baseline before executing; compare source differences that could change interpretation.
2. Ensure no prior coordinator conversation, this protocol, the merged coverage assessment, the historical critique, test answers, or reviewing criteria are injected as system, tool, session, repo summary or pre-read context. General repository safety instructions are permitted.
3. Give the worker **only Stage 1** and normal read-only access to the listed source files. Its identity/model and repo/source-read receipts should be collected from actual execution, not inferred.
4. Preserve **the worker's full visible answer unedited**, and only then send Stage 2 in the **same worker context**.
5. Coordinator assesses whether an error remains after Stage 2. Execute Stage 3 **only if material reasoning/premise-fidelity error persists**; otherwise record `SKIPPED_NOT_NEEDED` with a specific reason. The coordinator must not inject hints into Stage 2.
6. Execute Stage 4 with the same worker whether Stage 3 was executed or skipped. Preserve all exact prompts/responses, tool/read traces where available, model and environment identifiers and any exceptions.
7. Give a separate source-aware reviewer the assessment and **actual** complete worker records only after Stage 4. Reviewer must not rewrite or fabricate worker results. If independent review is unavailable, label a coordinator-only assessment with that limitation.
8. Keep this fictional vision disposable, read-only and noncanonical. Do **not** modify ontology, schemas, Studio prompts/request builders, application code, user projects or accepted story state. Persist evidence and an evaluation under the existing qualification/research locations; commit and review a focused PR only after reviewing what truly ran.

## 3. Exact reconstructed worker prompts

The following are **prepared input texts**, not records of actual submission. Send each block independently. Do not include this document's surrounding operator notes in worker messages.

### Stage 1 — initial creative reasoning (prepared, NOT SUBMITTED)

```text
You are conducting a small, read-only Narrative Architecture exercise in Auteur.

First inspect:

- `data/ontology/base_ontology.yaml`
- `docs/narrative-architecture.md`
- `docs/emotional-trajectory-contract.md`
- `src/auteur/beginner/studio_ontology_context.py`

Apply relevant narrative concepts to the following working Story Vision.

**Story Vision**

A beautiful cliffside city has an ancient system of bells that ring whenever someone forgets an important promise.

The bells are part of the city's shared identity. They connect everyday rituals, communal responsibility, public trust, and the feeling that people belong to something larger than themselves.

A young bell keeper discovers that the system has been secretly altered so that powerful citizens' promises are exempt from judgment.

The intended reader experience combines:

- Warmth and belonging in a beautiful, habitable community.
- Growing unease about institutional injustice.
- Hope earned through collective action rather than an effortless individual victory.

**Your tasks**

1. Diagnose the current Narrative Architecture. Explain its central conflict, causal structure, emotional potential, strengths, weaknesses, and unresolved questions.
2. Propose two meaningfully different narrative mechanisms that could develop the premise into a sustainable story. Explain how each works, what pressures it generates, and how it supports the intended reader experience.
3. Consider this hypothetical variation: citizens must voluntarily register their promises before those promises are subject to the bell system. Explain what follows for the operation of the bells, the possibility of forgetting, and the story's conflicts.
4. Identify any important assumptions your analysis relies upon and any story rules that remain unspecified.

Preserve the author's working premises. Treat new mechanisms as proposals, not established facts.

Provide your conclusions with concise source-grounded explanations.
```

### Stage 2 — general reflective challenge (prepared, NOT SUBMITTED)

**Gate:** Only after archiving the genuine Stage 1 answer; same worker context, without telling the worker what the historical errors were.

```text
Critically re-examine your preceding Narrative Architecture analysis.

Using the narrative concepts and sources available to you, identify whether any of your conclusions depend on unsupported assumptions, overstated inferences, insufficient evidence, or changes to the author's stated intentions.

If you find mistakes, explain the necessary corrections and revise the affected conclusions.

If you do not find a material mistake, explain why your conclusions remain justified.

Preserve useful creative possibilities. Do not weaken a sound proposal merely to appear cautious.
```

### Stage 3 — explicit epistemic guidance (prepared, CONDITIONAL; NOT SUBMITTED)

**Gate:** Run only if a consequential reasoning or author-premise error **persists after Stage 2**; otherwise label `SKIPPED_NOT_NEEDED`. Do not keep progressively disclosing more explicit answers until the worker succeeds.

```text
Reconsider the remaining disputed conclusions using the following distinctions.

**Epistemic warrant**

- An **entailed conclusion** follows from the established premises.
- A **compatible possibility** can be true without being required by those premises.
- An **unsupported assumption** introduces a rule or condition not yet established.
- An **underdetermined proposition** cannot be resolved from the available information.
- An **incompatible claim** conflicts with a fixed premise or a consequence genuinely established by it.

**Authorial authority**

- An explicit constraint in the current Story Vision must be preserved in proposals intended to remain faithful to that Vision.
- An agent-generated explanation is a hypothesis or creative proposal, not an accepted story fact.
- A counterfactual that changes an author constraint is permissible to explore only when it is clearly identified as a premise-changing alternative.
- Epistemic confidence does not grant authority to rewrite the author's story.

Review your earlier conclusions.

For each consequential correction, identify the relevant source or stated premise, what it establishes, and what remains uncertain.

Then revise the affected creative proposals without sacrificing their imaginative value.
```

### Stage 4 — creative improvement after reflection (prepared, NOT SUBMITTED)

**Gate:** After Stage 2, or Stage 3 where needed. Same worker context. Record an honest finding of `NO_MATERIAL_IMPROVEMENT` if warranted; never manufacture success.

```text
Using your current understanding of the Story Vision and the reasoning developed in this conversation, propose an improved version of one of your earlier narrative mechanisms.

Make the improvement substantive.

Explain:

1. The mechanism's operating rules.
2. Its central opposing pressures and the stakes they generate.
3. The actions and decisions it repeatedly makes possible.
4. How it preserves the Story Vision's defining premises.
5. How it produces warmth, unease, and earned collective hope.
6. Which elements remain creative hypotheses rather than author-approved story facts.
7. In what specific ways it improves on your first proposal.

Do not introduce complexity solely to make the story seem more sophisticated.

A simpler mechanism is acceptable if it is more coherent, narratively generative, emotionally effective, or faithful to the author's intentions.

Do not mistake avoiding errors for producing a compelling story.
```

## 4. Raw execution evidence ledger — not executed

| Stage | Submitted to worker? | Visible worker response | Actual worker source reads | Claim status |
|---|---|---|---|---|
| 1 — initial | **NO** | **NONE** | **NONE** | `NOT_ASSESSED` |
| 2 — general challenge | **NO** | **NONE** | **NONE** | `NOT_ASSESSED` |
| 3 — conditional guidance | **NO** | **NONE** | **NONE** | `NOT_ASSESSED`; conditional skip decision has **not** been made because Stage 2 did not run |
| 4 — creative improvement | **NO** | **NONE** | **NONE** | `NOT_ASSESSED` |
| Independent reviewer | **NO** | **NONE** | Not applicable | `NOT_ASSESSED` |

**Required fill-in only after real execution:** exact prompt bytes actually submitted, response/transcript text, agent identity/model, repo SHA, runtime/context isolation, source read receipts (or explicit unavailable), start/end time, optional Stage 3 decision/rationale, tool failures, reviewer input/identity, independent judgment with source and response anchors. Do not edit the historical raw responses to make them pass; keep coordinator conclusions in a distinct evaluation report.

## 5. Independent reviewer handoff — never show to the Stage 1 worker

After actual worker records exist, give a **new** independent reviewer (not the original worker) the exact SHA, merged assessment, relevant source excerpts, all **actual** submitted prompts and unmodified responses, and any executed read/tool receipts. Require separate findings on:

1. **Initial validity:** Did Stage 1 correctly handle underdescribed conflict, voluntary registration versus permanent recollection, and fixed secret-alteration premise?
2. **Reflective repair:** Which, if any, actual mistaken inferences did Stage 2 identify and materially repair without a specific hint? If Stage 1 was correct, say so.
3. **Conditional guidance:** Was Stage 3 invoked only where needed, and did it change reasoning rather than labels?
4. **Authorial fidelity:** Did the worker distinguish fixed working premises from optional inventions and explicit premise-changing counterfactuals?
5. **Creative improvement:** Did Stage 4 make one mechanism causally richer or more compelling for warmth, unease and collective hope, *not merely more cautious or verbose*?

Ground each consequential judgment in **exact response excerpts** and the pinned source definition. Separate observed text from qualitative literary judgment; preserve reviewer disagreements and partial or negative findings. A sequential learning episode cannot causally isolate ontology benefit, and one success does not establish general agent reliability.

## 6. Continuation and authority boundary

**The single next responsibility is to execute the prepared Stage 1–4 sequence in a truly isolated coding-agent context with repository access, then commission a separate reviewer and replace the `NOT_ASSESSED` entries with actual evidence.** If a worker cannot be isolated, stop and report the exact tool/environment limitation; do not pretend another message from this same coordinator is a fresh blind agent.

This packet is **not a new workflow, product specification, runtime, ontology change or creative acceptance**. The independently source-verified Studio Architecture Inquiry Vision-transport gap remains a **separate** follow-up and does not explain the historical direct-prompt error. Do not fix it here.

### Governing principles

1. It is not a test merely to prepare prompts; it is actually a test only when a blind worker executes them and the full outputs are preserved.
2. It is not a sound inference and it is not an independent review to let the coordinator generate its own worker answers; it is actually necessary to separate execution evidence from its interpretation.
3. Creative reflection is actually the conversion of warranted correction into author-faithful narrative possibility.
