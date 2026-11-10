# Auteur — Stage 4J Execution Provenance

**Operation:** Bounded literary correction and authorial-direction preparation.  
**Date:** 2026-11-10. No wall-clock timestamps were recorded; the order below is reconstructable from the tool calls and commits.  
**Model/runtime:** `opencode` CLI on Windows (`win32`), PowerShell 5.1; model identified by the runtime as `opencode/deepseek-v4.1-flash`.  
**Reader evidence:** No new independent reader was launched or consulted. The Stage 4I fresh-reader response remains the reader evidence and was not reapplied to the corrected text.

## 1. Verified starting point

- **Repository:** `ThorStarlord/auteur`.
- **Workspace:** `H:/GithubRepositories/auteur`; `git rev-parse --git-common-dir` returned `.git`, a standalone repository.
- **Parent head:** `2fd983282c26ae29d0ab6131214e178a56f8a880`, verified as the head of PR #539 (`OPEN`, draft) and as the current workspace HEAD before branching.
- **Parent branch:** `research/wandering-islands-stage4i-independent-reader-completion-20261110`.
- **New branch:** `research/wandering-islands-stage4j-targeted-literary-correction-20261110`, created directly from the verified parent head.
- **Research directory:** `docs/qualification-evidence/2026-11-07-wandering-islands-12-book-exercise/`.

## 2. Source identities

All source blobs were verified at the parent head before any change:

| Source | Git blob SHA-1 | Role |
| --- | --- | --- |
| `stage4h-original-book11-realization.md` | `483478814c2f7222143cd9df3cc942ed43aa157a` | Frozen original manuscript; not modified |
| `stage4i-fresh-reader-initial-response.md` | `2c32c219810bb55d9fcdaadb03cf8de4d63aaf9a` | Frozen fresh-reader response; not modified |
| `stage4i-fresh-reader-reconciliation.md` | `f53ccae3c1abad6613981834763ec70a222512c6` | Post-freeze reconciliation; not modified |
| `stage4i-reader-handoff.md` | `82f6ca486387b9982724659f24b766a27cb3ae78` | Neutral reading handoff; not modified |

## 3. Exact textual substitution

**Old sentence:**

`Nemi thought of the crowd that had greeted their earlier Book 5 news of Larkhome.`

**New sentence:**

`Nemi thought of the crowd that had greeted them when they brought word that Larkhome was alive.`

The substitution was performed once in the Stage 4I neutral literary payload. No other literary wording, punctuation, spacing, paragraph break, or scene order was changed.

## 4. Baseline extraction and verification

The Stage 4I neutral reading payload was reconstructed from the frozen Stage 4H source using the Stage 4I extraction rule:

- Include the literal title `# Beyond the Written Sea` and one blank line.
- Include the original source substring from `### I. The Place Where the Rain Went` through the end of Scene V.
- Stop immediately before the separator introducing `## Experimental continuity note`.
- Exclude the subtitle, the research/noncanonical status line, the separator preceding Scene I, and the complete continuity note.

The reconstructed baseline was 36,132 characters (36,132 UTF-16 code units in the .NET string) and had SHA-256:

`3C2C937D96BD0C9C29C25CE1E68970AE4F15410D9E9A3CE5462099222415AE20`

This matches the prepared neutral payload SHA-256 recorded in the Stage 4I provenance. The Stage 4I handoff's reader-only manuscript block was inspected and contains the same title and five scenes; its final blank line before the closing fence accounts for the final LF.

Baseline checks:

- Old sentence occurrences: **1**.
- New sentence occurrences: **0**.
- Five scene headings present: **5**, in order I–V.
- No CR characters; LF line endings.
- UTF-8 source read and written without a BOM.

## 5. Derivative construction and verification

The derivative was produced by a single in-memory replacement of the old sentence with the new sentence in the baseline, then written as UTF-8 without BOM.

Checks performed:

1. Old sentence occurs **0** times in the derivative.
2. New sentence occurs **1** time in the derivative.
3. Reversing the substitution (`new` → `old`) reproduces the baseline **exactly**.
4. The derivative's unchanged prefix and suffix are character-identical to the baseline. The first differing character is at index 27,805; the old span is 33 characters and the new span is 47 characters because the sentences share leading and trailing context. The only changed material is the specified sentence.
5. Five scene headings remain present and ordered I–V.
6. No CR characters; UTF-8 punctuation is preserved because all material outside the replacement is byte-for-byte/character-identical, and the replacement itself is ASCII.
7. No editorial annotations, provenance headers, or explanations appear in the reading copy.

**Derivative content:**

- Path: `stage4j-corrected-book11-reading-copy.md`
- Characters: **36,146**.
- Bytes: **36,852**.
- SHA-256: `B1F515F211422C405C32A369628853BF93F0A81960EC283D5B2896322DC0A69D`.
- Git blob (raw file): `b72a69a7ef6fb1bb0edbe130ee39f00cff3f1ee4`.

**Authorial-direction brief:**

- Path: `stage4j-authorial-direction.md`
- Bytes: **8,352**.
- SHA-256: `B3F40B34775239B3B2AA875000FD0A443AA13A3F5797BE5E54CA31B04C1680FF`.
- Git blob (raw file): `98e51fff08455d018eeb37bb520769cf80ef76ba`.

This provenance file's own final blob is recorded in the final report after the preservation commit, to avoid a self-referential hash.

## 6. What the correction establishes

**Supported:** A specific extradiegetic phrase identified during the Stage 4I first reading has been corrected in a separately identified derivative text, with the original and the reader response preserved unchanged.

**Not supported:** The corrected text has now been independently validated as more engaging, more suspenseful, or more literarily successful. No reader evaluated the derivative. The Stage 4I response evaluated the earlier version. The derivative is a proposed working revision, not a replacement for the research record or accepted canon.

## 7. Scope and repository boundaries

- The original manuscript `stage4h-original-book11-realization.md` remains byte-identical at blob `483478814c2f7222143cd9df3cc942ed43aa157a`.
- The fresh-reader response remains byte-identical at blob `2c32c219810bb55d9fcdaadb03cf8de4d63aaf9a`.
- The reconciliation and handoff remain unchanged.
- No accepted canon, Narrative Ontology, Studio, Series schema, production code, application prompt, or application test was modified.
- No new reader experiment, broader literary revision, scene outline, or canon promotion was performed.
- No prior PR was modified or merged.

## 8. Post-creation verification

*This section was completed after the preservation commit and draft PR creation; it does not alter the derivative or any frozen artifact.*

- **Correction commit:** `318ff5189a2a87ad5bb66ca6323f038cbf78392e`.
- **Draft PR:** [#540](https://github.com/ThorStarlord/auteur/pull/540), `OPEN`, `isDraft: true`.
- **PR base:** `research/wandering-islands-stage4i-independent-reader-completion-20261110`.
- **PR head:** `research/wandering-islands-stage4j-targeted-literary-correction-20261110`.
- **Verified PR head at creation:** `318ff5189a2a87ad5bb66ca6323f038cbf78392e`.
- **Diff:** `git diff --name-status 2fd983282c26ae29d0ab6131214e178a56f8a880..HEAD` shows only the three new Stage 4J files. `gh pr view 540` reports exactly those three added files.
- **Frozen-artifact verification:** the original manuscript remains blob `483478814c2f7222143cd9df3cc942ed43aa157a`; the fresh-reader response remains blob `2c32c219810bb55d9fcdaadb03cf8de4d63aaf9a`; the reconciliation remains `f53ccae3c1abad6613981834763ec70a222512c6`; the handoff remains `82f6ca486387b9982724659f24b766a27cb3ae78`.
- **Derivative blob at HEAD:** `b72a69a7ef6fb1bb0edbe130ee39f00cff3f1ee4`.
- **Authorial-direction blob at HEAD:** `98e51fff08455d018eeb37bb520769cf80ef76ba`.
- **Provenance blob before this post-creation update:** `042fe163ac86ffe586a90bf8462e4d60c44ea062`. The final provenance blob after this update is recorded in the final report, because a file cannot contain its own post-write hash.
- **Parent PR #539:** verified `OPEN`, `isDraft: true`, head `2fd983282c26ae29d0ab6131214e178a56f8a880`; unchanged.
- **Post-update note:** committing this verification creates a later branch head. The final head is recorded in the final report and in PR #540. No frozen artifact or derivative text is modified by this update.

---

## Preserved task instruction

The complete visible Stage 4J instruction is preserved below. It was supplied as a single block in the user message; no duplicate was present.

````text
# Auteur — Stage 4J: Targeted Literary Correction and Authorial Direction

## Task identity

**Repository:** `ThorStarlord/auteur`

**Operation:** Bounded creative revision and author-facing literary decision preparation.

**Starting point:** Stage 4I fresh-reader completion, PR #539.

**Guiding question:** Can we correct one independently identified immersion break while preserving the frozen experimental manuscript and separating objective textual repair from unresolved artistic direction?

**Expected outcome:** One corrected, noncanonical derivative reading copy and one concise authorial decision brief.

**Authority:** Documentation-only research artifacts and a draft PR.

**Execution:** Proceed autonomously. No new independent reader or fresh model session is required.

**Stop boundary:** One textual substitution. No broader manuscript revision, new reader experiment, ontology development, canon promotion or PR merge.

---

## 1. Mission

The Wandering Islands experiment has produced a substantial five-scene Book 11 excerpt, *Beyond the Written Sea*.

Stage 4H's same-context GPT-6 assessment found credible local literary realization.

Stage 4I subsequently obtained a fresh-context reading from `opencode/deepseek-v4.1-flash`.

That response confirmed several strengths but qualified the earlier positive judgment.

The reader especially appreciated:

- The domestic life aboard *Kindling Tide*.
- Ivo's conflict with Nemi.
- Ivo and Marra's collaborative craftwork.
- Pera's warmth and practicality.
- The wooden bird's recurring significance.
- The sealed letter's narrative hook.

The reader also reported:

- Limited emotional intensity despite strong literary craft.
- A crossing that felt more procedural than suspenseful.
- A chart dispute that became overly discursive.
- Nemi feeling less developed than Ivo and Pera.
- Some under-explained series terminology.
- A clear immersion break caused by an extradiegetic reference to “Book 5.”

The recommended next responsibility is **not a comprehensive literary rewrite**.

It is to correct the single concrete immersion break and preserve the larger artistic questions for the author's decision.

---

## 2. Verify the repository baseline

PR #539:

https://github.com/ThorStarlord/auteur/pull/539

Expected head:

`2fd983282c26ae29d0ab6131214e178a56f8a880`

Expected branch:

`research/wandering-islands-stage4i-independent-reader-completion-20261110`

Research directory:

`docs/qualification-evidence/2026-11-07-wandering-islands-12-book-exercise/`

### Frozen Stage 4H manuscript

File:

`stage4h-original-book11-realization.md`

Expected Git blob SHA-1:

`483478814c2f7222143cd9df3cc942ed43aa157a`

### Frozen fresh-reader response

File:

`stage4i-fresh-reader-initial-response.md`

Expected Git blob:

`2c32c219810bb55d9fcdaadb03cf8de4d63aaf9a`

### Post-reader reconciliation

File:

`stage4i-fresh-reader-reconciliation.md`

Expected Git blob:

`f53ccae3c1abad6613981834763ec70a222512c6`

### Neutral reading handoff

File:

`stage4i-reader-handoff.md`

Expected Git blob:

`82f6ca486387b9982724659f24b766a27cb3ae78`

Verify the actual source identities.

Preserve all existing artifacts unchanged.

No new literary assessment is needed before making the narrowly specified correction.

---

## 3. The exact textual defect

The frozen manuscript contains this sentence in Scene IV:

> Nemi thought of the crowd that had greeted their earlier Book 5 news of Larkhome.

The phrase “Book 5” belongs to the series' structural documentation.

Within Nemi's thoughts, it breaks the fictional frame.

The fresh reader identified this spontaneously before seeing the previous editorial assessment.

### Authorized replacement

Replace the sentence with:

> Nemi thought of the crowd that had greeted them when they brought word that Larkhome was alive.

This preserves:

- Nemi's earlier journey.
- Their role in carrying verified news of Larkhome's survival.
- Their complicated relationship with public gratitude.
- The psychological motivation for accepting limited letter custody.
- The surrounding narrative chronology.

It removes the external book-numbering terminology.

### Strict edit boundary

Change this sentence **once and only once**.

Do not alter the following sentences.

Do not revise the dialogue.

Do not strengthen the emotional passage.

Do not change any other literary wording, punctuation, spacing, paragraphs or scene ordering.

Do not opportunistically correct other perceived stylistic issues.

Even a potentially beneficial second correction is outside this assignment.

---

## 4. Produce a separate derivative reading copy

**Do not modify `stage4h-original-book11-realization.md`.**

That file is frozen creative evidence and must remain byte-identical.

Instead, create a new, explicitly identified derivative reading copy.

Suggested file:

`stage4j-corrected-book11-reading-copy.md`

The corrected reading copy should contain:

- The literary title.
- All five original scenes, in their original order.
- The exact authorized replacement sentence.
- No other changes to the literary prose.

As with the Stage 4I neutral reading payload, exclude the preliminary research-status notice and final Experimental continuity note.

The reader-facing file should not contain editorial annotations, explanations of the revision or provenance headers.

Put those explanations in a separate evidence document.

### Mechanical verification

Use the Stage 4I neutral reading payload as the baseline for comparison.

Verify that:

1. The original reader-only payload matches the frozen Stage 4H literary source.
2. The old sentence occurs exactly once.
3. The replacement sentence is present exactly once.
4. Reversing the one substitution in the derivative produces the original reader-only payload exactly.
5. All five scenes remain present and ordered.
6. UTF-8 punctuation is preserved correctly.
7. No unrelated literary characters have changed.

Calculate and record the derivative's actual content hash.

Do not invent hash values.

This is a focused textual verification task. A full application test suite is unnecessary.

---

## 5. Preserve the fresh-reader findings

The original fresh-reader response must remain unchanged.

Do not reinterpret its original opinion as though the reader evaluated the corrected text.

The reader evaluated the earlier version.

Therefore:

**Supported claim:** A specific extradiegetic phrase identified during the first reading has been corrected in a derivative text.

**Unsupported claim:** The corrected text has now been independently validated as more engaging.

Do not launch another reader round.

Do not generate a new positive literary verdict.

Do not change the historical Stage 4H or Stage 4I dispositions.

The corrected copy is a proposed working revision, not a replacement for the research record.

---

## 6. Prepare the authorial creative decision

The fresh reader raised a larger uncertainty that cannot be resolved by correcting one sentence.

The excerpt is coherent, humane, and rich in everyday detail, but its emotional experience may be quieter than the intended Book 11 experience.

Prepare a concise decision brief addressing:

**What kind of emotional intensity should Book 11 primarily pursue?**

Present three coherent directions, with their merits, risks and implications for a later substantial revision.

### Direction A — Restorative everyday fantasy

Prioritize belonging, craftsmanship, community life, mutual discovery and emotionally satisfying ordinary achievements.

**Potential advantage:** Preserves the excerpt's strongest demonstrated qualities.

**Potential risk:** Restrained conflict may leave some readers admiring the narrative more than emotionally invested in its outcomes.

### Direction B — Hopeful adventure with stronger dramatic pressure

Retain warmth and generosity while increasing suspense, wonder, difficult choices and the emotional consequences of the crossing and encounter.

**Potential advantage:** Could strengthen momentum without sacrificing the story's optimistic identity.

**Potential risk:** Artificial danger or manufactured catastrophes could undermine the established world and tonal vision.

### Direction C — Deeper interpersonal and social consequences

Develop Nemi's internal contradictions, Ivo's grievances, Pell's competing economic interests and the costs of relationships that cannot be immediately reconciled.

**Potential advantage:** Could increase character depth and emotional transformation without requiring spectacular external danger.

**Potential risk:** Excessive argument or unresolved friction could make the story heavier or more didactic.

### Evaluation

Compare these directions against:

- The original Story Vision.
- The strongest scenes of the frozen excerpt.
- The fresh reader's spontaneous reactions.
- The needs of Book 11 within a twelve-Book series.

The directions are **not necessarily mutually exclusive**.

Identify a reasonable possible combination if it emerges naturally, but do not treat your preference as an author-approved decision.

Do not choose a binding new artistic thesis.

Do not create a revised scene outline.

Do not rewrite Nemi, Pell, Tava or Ivo.

The purpose is to expose the genuine creative choice before undertaking more substantial work.

Keep this brief. It should be a useful author-facing decision, not another lengthy experimental report.

---

## 7. Repository changes

Start a new branch directly from the verified PR #539 head:

`2fd983282c26ae29d0ab6131214e178a56f8a880`

Suggested branch:

`research/wandering-islands-stage4j-targeted-literary-correction-20261110`

Create three new Markdown files in the existing evidence directory.

### 1. `stage4j-corrected-book11-reading-copy.md`

The clean five-scene derivative text with exactly one authorized sentence replacement.

### 2. `stage4j-authorial-direction.md`

A concise document containing:

- The identified original sentence and corrected sentence.
- The reason for the bounded change.
- The evidence supporting it.
- A statement that no independent reader has evaluated the derivative.
- The three possible directions for future dramatic development.
- Their merits and trade-offs.
- The precise authorial decision remaining open.

### 3. `stage4j-execution-provenance.md`

Record:

- Actual model/runtime.
- Verified starting revision.
- Relevant original and reader-response Git blobs.
- Exact textual substitution.
- Verification that this was the sole literary change.
- Clean-reading-copy extraction boundaries.
- New file hashes.
- Branch, commits and PR status.
- Scope and limitations.

Preserve the complete task instruction in the provenance document or as a clearly identified referenced instruction if repository conventions require it; do not create additional files merely for procedural ceremony.

### Draft PR

Open one draft stacked PR targeting:

`research/wandering-islands-stage4i-independent-reader-completion-20261110`

Verify that the diff contains only the three authorized new files.

Leave PR #539 and all preceding experimental PRs open, draft and unmerged.

Do not modify any previously frozen artifact.

Do not modify accepted author canon, the Narrative Ontology, Studio, Series schemas, production code, application prompts or application tests.

Do not merge this PR.

---

## 8. Final report

Report:

1. Verified parent SHA and source identities.
2. The exact sentence before and after correction.
3. The corrected reading copy's Git blob.
4. Evidence that this was the only literary change.
5. Confirmation that the original manuscript and reader response remain unchanged.
6. The three authorial dramatic directions and their principal trade-offs.
7. The authorial decision still outstanding.
8. What is and is not established by the correction.
9. The new draft PR URL, head SHA and verification results.
10. One smallest warranted continuation.

Do not start the continuation.

Do not perform another reader experiment.

Do not undertake a broader literary revision.

Do not promote the derivative into canon.

Stop after completing the bounded correction and preparing the authorial choice.

---

## Governing principles

1. **It is not rewriting the evidence; it is actually preserving the original while creating a traceable corrected derivative.**

2. **It is not maximizing spectacle and is not minimizing conflict; it is actually selecting the kind of emotional intensity that serves the story's intended experience.**

3. **Creative revision is actually the transformation of specific evidence into deliberate artistic choices.**
````
