# Product use: Auteur Studio architecture bridge

All calls used:

    PYTHONPATH=H:/GithubRepositories/auteur-consolidated/src PYTHONUTF8=1 python -m auteur.beginner.studio_architecture --project "<...>/consolidated/proj" --canvas spring-ledger-consolidated <action>

The raw JSON output of each call is saved under `agent-output/raw/`.

## Operations run, in order

### 1. `resume` (read-only)
- **Exit:** 0.
- **Output:** `raw/resume-before.json`, about 66 KB.
- **What it returned:**
  - `canvas_revision` 10 and `architecture_status` "ready".
  - The story vision.
  - The W6 candidate: 32 nodes, 34 links, 5 phases, 16 open questions, 7 emotion targets (all `agent_proposed`), 2 complex emotions, 4 genre contracts and 5 genre interactions.
  - 5 provisional concepts: Book 15 surfeit mechanism, Compact grain-labour, Gate Table, Harrow Lowe lower gate and Hollow Gate.
  - The 4 author intentions, all `active`.
  - Empty creative deliberation and adoption lineage.
  - A generic `ontology_guidance` block of 12 base concepts.
- **How I judged the ontology guidance:** it is generic and correct, but it added nothing specific to this task. I used it only as a check that the Book has a Conflict, a Goal-bearing set of characters, and a Setup with a later Payoff.
- **What I relied on:**
  - `ph_5_unmeasured`, `ph_4_settled_water`, `ph_3_old_hand` and `ph_1_reckoned_water`.
  - `str_long_return`, `str_lowfen_channel`, `str_unmeasured_return`, `th_maintenance` and `th_hands_and_draw`.
  - `inst_lineage_crews` and `inst_reading_hall`.
  - `eng_source` and `eng_old_hand`.
  - The links `l_longreturn_needs_hands`, `l_conversion_sets_draw`, `l_lineage_right_on_draw` and `l_reading_separate_schedule`.

### 2. `show` and `intentions` (read-only)
- **Exit:** both returned JSON with no error. I piped their output through `head`, so I did not capture their exit codes.
- **`show`:** returned `"status": "ready"`, `"request": null` and the same candidate as `resume`.
- **`intentions`:** returned the same 4 intentions, with `"authority": "author_directed_working_intention"`.
- **Outcome:** neither call added information beyond `resume`.

### 3. `prepare --instruction "<text>"` (write)
- **Exit:** 0.
- **Output:** `raw/prepare.json`.
- **Instruction:** add the Book 24 function as Book-scoped nodes, links and one agent-proposed emotion target, and keep every existing element unchanged.
- **What it returned:**
  - `"status": "awaiting_host_agent"` and `request_id` `studio-b69a1d28a1a4b474fa1b3033:07ae948ac8321987`.
  - `settings.operation` "revise" and `request_sha256` `07ae948a…5108`.
  - A system prompt for the host agent, and a user payload of about 59 KB, which I did not read in full.

The system prompt contains two directives that are stricter than the packet's contract (03-auteur-operations.md):
- Quoted exactly: "node: {id,title,category,summary,scope,parent_id}; category: reader_experience, aesthetic,genre,trope,engine,thread,structure,theme,other (never character/relationship)." The packet lists `character` and `relationship` as allowed categories, so the two documents disagree. I did not add character nodes.
- Quoted exactly: "Never invent names of characters, places, factions, events, plot acts or scenes." In the candidate, my new terms "the uncounted crew" and "capability mark" therefore appear as descriptive titles. The coined label "craft-mark" is not in any node. It does appear in my `--instruction` text, which the product stores as `requested_change`. The node summaries name Hesper Sallow and Ysa Trant. Both names are supplied by the existing architecture: Ysa Trant in `inst_lineage_crews`, and Hesper in open question 10 and in 01 §4. The crewmate whose terrace silts is left unnamed.

### 4. `complete-file --candidate agent-output/book-24-candidate.json` (write)
- **Exit:** 0, with no validation error.
- **Output:** `raw/complete-file.json`.
- **The submitted candidate is the W6 candidate unchanged, plus these additions:**
  - **Nodes:** `str_b24_uncounted_crew` (structure, scope "book 24", parent `str_long_return`; summary 1,548 characters) and `str_b24_capability_mark` (structure, scope "book 24", parent `str_b24_uncounted_crew`; summary 839 characters).
  - **Links (8):** `l_b24_oldhand_refusal`, `l_b24_crew_maintenance`, `l_b24_crew_gauge`, `l_b24_crew_conversion`, `l_b24_reading_hall_declines`, `l_b24_mark_right`, `l_b24_mark_variable` and `l_b24_mark_long_return`.
  - **Emotion target:** `et_b24_seen_by_water` (surprise, local, `agent_proposed`).
  - **Summary:** one sentence appended that labels the revision as agent-proposed.
- **What it returned:** `"status": "review_ready"`, with a `review` object containing:
  - `authority`: "working_architecture_comparison_not_story_impact".
  - `changes`: 2 nodes, 8 links and 1 emotion target added. Nothing was removed or changed, apart from `summary_changed: true`.
  - A `preserved` list of all 32 original node IDs.
  - `note`: "This is a review of a noncanonical working proposal. It does not change accepted Identity, Structure, Realization, Expression or shared ontology."

### 5. `resume` again (read-only, to confirm the state)
- **Output:** `raw/resume-after.json`.
- **What it showed:**
  - `architecture_status` "review_ready".
  - `canvas_revision` still 10.
  - `pending_review` holds my revision.
  - The live `architecture` does **not** contain the Book 24 nodes.
- **Outcome:** the revision is stored as a reviewed revision waiting for application. As 03-auteur-operations.md states, the bridge has no command to apply it. I did not try to apply it by any other means. Applying it is a decision for the author or a later process.

### Not used
- `record-concept`. The capability mark could be a provisional concept. I kept it in the candidate revision only, to avoid adding canvas state that sits outside the reviewable revision.
- `keep-intention` and `set-intention-status`. The author gave no new directive, and the second is an author action.

## What I could and could not express

**Could express:**
- Book 24's question, conditions, choice, consequence and changed state, as a Book-scoped structure node. Its 2,000-character summary was enough for a compressed version of the function.
- The capability mark, as a node.
- The causal relations, as short link functions: Old Hand to the cohort's refusal, the crew to the gauge, the crew to the conversion, the mark to the Right, the mark to the Long Return.
- One local emotion target, with `agent_proposed` provenance.

**Could not express, or only lossily:**
- **No Book node.** Book 24 had to be typed as `structure`, with the scope string "book 24".
- **Phase narrative full.** The Arc V phase (`ph_5_unmeasured`) narrative is already at exactly 1,000 of its 1,000 characters, so Book 24 could not be added to it without deleting existing text. I left the phase unchanged.
- **Open questions full.** There are already 16 of 16. I could not add the Book's new open questions, for example whether craft-marks can be falsified, or the length of the Long Return's lead time, without dropping an existing one. Several existing ones are author-reserved, so I added none.
- **No provenance outside emotion targets.** The [Agent] and [Derived] labels on nodes and links are carried only in prose inside summaries. Links have no provenance field.
- **No character category.** The product request forbids the character category, so Hesper, Idrun, Ysa Trant, Oona Brisk and the hand-light households' motives appear only inside the node summary, compressed. The independent motivations in §4 of `book-24-function.md` are not structurally represented.
- **No place for alternatives, provisional assumptions P1–P10, or missing information.** These live only in `book-24-function.md`.

**My judgement:** the product holds a faithful skeleton of the function: the question, the causal chain, the choice and its cost, and the new record. It does not hold the full function. The authoritative statement remains `book-24-function.md`.

## Errors

None. `resume`, `prepare` and `complete-file` exited 0, `show` and `intentions` returned JSON with no error, and `complete-file` returned no validation error.
