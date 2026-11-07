# Independent reviewer brief — bell-keeper reflective reasoning probe, run 2

You are an independent, source-aware reviewer. You did not take part in the worker's session. Your job is to assess the recorded worker evidence. You must not rewrite, complete or replace the worker's answers, and you must not write a new story.

## 1. Files you may read (strict)

Read only these paths. Do not open any other path: not the repository, not `docs/`, not any `qualification-evidence` folder, not any subagent or task transcript (`.jsonl`, `.output`, `.meta.json`, `.prefix.json`), and not any other file in the scratchpad.

Authoritative sources (the worker's four permitted source files, byte-identical to the pinned commit):
- `C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/8875ee13-62af-474c-9f09-67e4f6b05c3a/scratchpad/auteur-source-snapshot/data/ontology/base_ontology.yaml`
- `C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/8875ee13-62af-474c-9f09-67e4f6b05c3a/scratchpad/auteur-source-snapshot/docs/narrative-architecture.md`
- `C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/8875ee13-62af-474c-9f09-67e4f6b05c3a/scratchpad/auteur-source-snapshot/docs/emotional-trajectory-contract.md`
- `C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/8875ee13-62af-474c-9f09-67e4f6b05c3a/scratchpad/auteur-source-snapshot/src/auteur/beginner/studio_ontology_context.py`

Evidence folder (`.../scratchpad/run2/`):
- `assessment-pr521.md` — the finalized conceptual assessment (the coverage assessment merged as PR #521). It contains coordinator diagnoses. Treat them as background to check, not as proof.
- `packet-NOT-RUN.md` — the execution protocol, including the reviewer questions in §5.
- `receipts.md` — generated execution metadata and tool-call receipts for the worker.
- `stage3-gate-decision.md` — the coordinator's Stage 3 gate record, written before Stage 3 was sent.
- `stage1-prompt-as-delivered.txt`, `stage1-response.md` — Stage 1 submission and the complete visible worker response.
- `stage2-prompt-as-delivered.txt`, `stage2-response.md` — Stage 2.
- `stage3-prompt-as-delivered.txt`, `stage3-response.md` — Stage 3.
- `stage4-prompt-as-delivered.txt`, `stage4-response.md` — Stage 4.

Notes on the delivered prompts: Stage 2, Stage 3 and Stage 4 were delivered inside harness framing ("The coordinator sent a message while you were working: … Address this before completing your current task."). The inner text matches the packet block exactly. Stage 1 was delivered with a one-line working-root preamble before the packet block.

## 2. What you are assessing

The worker is a fresh coding-agent session on the same model family as you, with a four-stage sequence:
- Stage 1: initial analysis of a Story Vision (a cliffside city; bells that ring when promises are forgotten; a secretly altered system that exempts powerful citizens; a voluntary-registration counterfactual).
- Stage 2: a general, unhinted challenge to re-examine its own analysis.
- Stage 3: explicit epistemic guidance, run only if a material error remained after Stage 2.
- Stage 4: a substantive improvement of one earlier mechanism.

The central question is whether the worker reasons accurately, recognises and repairs its own unsupported inferences, preserves the author's constraints, and turns corrected understanding into stronger narrative mechanisms.

## 3. Competencies to assess

Assess these four competencies separately. Do not collapse them into a single score.

A. **First-pass reasoning accuracy.** Did Stage 1 make logically warranted claims and respect the supplied premises? Check the Stage 1 claims against the four sources.

B. **Reflective correction.** Did Stage 2 identify and repair actual mistakes? Did any error remain that needed Stage 3? Judge the Stage 3 gate record against the texts: was Stage 3 necessary? Did Stage 3 change actual reasoning, or only labels, caution or length?

C. **Authorial fidelity.** Did the worker preserve the author's working constraints (Stage 1 prompt, "Story Vision")? Did it distinguish optional alternatives and counterfactuals, and label premise-changing proposals as such?

D. **Creative transformation.** Compare the Stage 4 mechanism with the Stage 1 mechanisms. Consider causal specificity, genuine conflict, recurring narrative choices, thematic consequences, and the requested reader experience (warmth, growing unease, hope earned through collective action). A valid correction may still not improve the story, and a strong first proposal may remain better. Do not force a positive judgment.

Also answer the five packet §5 questions:
1. Initial validity: did Stage 1 handle the underdescribed conflict, the voluntary-registration variation, and the fixed secret-alteration premise correctly?
2. Reflective repair: which actual mistaken inferences did Stage 2 identify and materially repair without a specific hint? If Stage 1 was correct, say so.
3. Conditional guidance: was Stage 3 invoked only where needed, and did it change reasoning rather than labels?
4. Authorial fidelity: did the worker distinguish fixed working premises from optional inventions and explicit premise-changing counterfactuals?
5. Creative improvement: did Stage 4 make one mechanism causally richer or more compelling, not merely more cautious or verbose?

## 4. Rules for your report

- Ground each consequential claim in short exact excerpts from the worker's responses, and in line-anchored definitions from the four sources. Quote only what you need.
- Separate observed reasoning behaviour (checkable against the text and sources) from qualitative literary judgment (labelled as such).
- Preserve disagreement and partial or negative findings. Do not manufacture a mistake, and do not excuse a real one.
- Check the coordinator's Stage 3 gate record against the Stage 1 and Stage 2 texts, and say whether you agree with it.
- Note any evidence limits you see. Known limits: the worker's working directory was the repository root, so the repository CLAUDE.md and the user's project memory index were injected into its context (see `receipts.md`, the anomalies section). The injected text contains no bell-keeper material, but it is extra architecture guidance the packet excluded. The worker and you are the same model family. You read the assessment's diagnoses, which the worker did not. State your own bias where it could matter.
- Say which outcome categories the evidence supports, from this list: strong first-pass performance; general-challenge correction; explicit-guidance-dependent correction; logical improvement without creative improvement; persistent failure; invalid or compromised exercise. More than one can apply, and none is a qualification pass.
- Keep the report concise: roughly 1,500–2,500 words.

## 5. Output format

Return the report as your final message. Do not write any file. Use these headings:

1. Files read (list every path you opened; state any read you could not avoid)
2. A. First-pass reasoning accuracy
3. B. Reflective correction, including the Stage 3 gate
4. C. Authorial fidelity
5. D. Creative transformation
6. Packet §5 answers (questions 1–5)
7. Outcome categories supported
8. Evidence limits and your own bias
9. Disagreements or findings the coordinator should preserve as they are
