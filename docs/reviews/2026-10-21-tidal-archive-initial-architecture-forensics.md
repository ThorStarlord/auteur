# Tidal Archive — Initial Narrative Architecture Forensic Analysis

Repository `ThorStarlord/auteur` · `main` at `a635783` (after #474/#475) · 2026-10-21
Mode: read-only investigation. No story project was modified, no generation was run, and no ontology or schema was changed.

**Status: source investigation complete; candidate assessment blocked on access.** The capture kit ships separately (PR #476) so each change stays within the 500-line review cap.
The Tidal Archive project exists only on the owner's Windows machine. This
environment cannot reach it: it is not in the repository, any branch, PR or
issue, and no session on that machine is connected. The candidate-content
assessment (§5–§6) is therefore **not performed**. No synthetic project stands
in for the missing artifact.

To unblock it, run the read-only capture kit
[`scripts/tidal_forensic_capture.py`](../../scripts/tidal_forensic_capture.py)
on that machine (§11). Alternatively, continue in a session that runs on that
computer (Claude Desktop, or `claude remote-control` started in the project
folder).

---

## 1. Evidence boundary

| Evidence | Result |
|---|---|
| Tidal Archive files in the repository (all branches) | **None.** Only `STATUS.md` mentions it. |
| PR records | #472: "that Windows-only artifact is not available to this environment". #471/#473 record behaviour, not content. |
| Facts about the initial candidate that survive | PR #471, commit `8d4db52c` (2026-10-20 06:34 −03:00), observed before #472 changed the prompt (06:49): **12 nodes**, a genre node titled **"Speculative Mystery"**, **two directed genre interactions** that both touch it (consistent with a reciprocal pair), so **≥2 genre contracts**. No earlier revision is recorded, so this was almost certainly the initial candidate. |
| Model / runtime identity | **Probably not recorded.** `HostAgentResponse.runtime/model` default to `UNAVAILABLE`, and the documented `complete-file` path passes neither. Treat it as unknown unless `response.json` says otherwise. |
| Reasoning trace | Not part of the contract. Only the candidate JSON is stored. |

---

## 2. Narrative knowledge in the repository at generation time

All of these existed before the Studio module was created (2026-10-14), and none changed before generation.

| Source (last change) | What it establishes |
|---|---|
| `data/ontology/base_ontology.yaml` (09-27) | 12 Layer 0 concepts (Character, Arc, Theme, Goal, Conflict, Payoff, Symbol, Relationship, Beat, Setup, Revelation, Reversal), with definitions, relationships, cardinalities and rules. |
| Genre ontology YAMLs (09-27) | Genre-specific concepts (e.g. MysteryProblem, Clue, RedHerring, InvestigativeArc). |
| `src/auteur/identity.py` `HighLevelCentralEngine` (09-27) | The story-level engine summary: `want`, `resistance`, `conflict`, `stakes`, `change`. |
| `architecture_preferences.py` (09-27) | Complexity / causal distribution / engine hierarchy (`single_center`, `primary_with_layers`, `ensemble`). |
| Phase F design (10-03) | Causal profile (`primary_strategy`, `causal_owner` incl. `ensemble`, `external_action_pattern`, `pressure_system`, `climax_mechanic`), craft propagation, primary/subordinate borrowing. |
| ADR 008 (09-27) | Primary promise, palette, avoided experience, trajectory. |
| Theme & motif contract (09-28) | Theme as a tested commitment; may stay unresolved; motif ≠ theme. |
| Emotional trajectory contract (09-28) | Reader emotion ≠ character emotion. |
| Detailed Narrative Architecture V1 (09-27) | Declared vs deterministic vs interpretive claims. |
| `docs/narrative-architecture.md`, `docs/PRD.md` | Five-layer ownership; components must function together. |

---

## 3. Exactly what the original HostAgentRequest delivered

The Studio module was created at `031eb693` (2026-10-14) and unchanged on
`main` until #472 (2026-10-20 06:49). The only other prompt that could have
produced the initial request is the #471 branch head `8d4db52c`: the original
plus one provisional-defaults paragraph, still without design context. The
original module imports no ontology code at all: `narrative_ontology`,
`OntologyLoader` and `OntologyValidator` are never referenced.

| Prompt version | `sha256(_SYSTEM)` |
|---|---|
| Original `031eb693` | `b3756886fa119ed827903b0d864b3cfa4836d3f9c2e7786c43a742edd76e21f8` |
| #471 branch head `8d4db52c` | `42274805af64323f7e0c76d7b18edb2d2a7f485fbf442838b7197f6d10b4d76c` |
| #472 `5ecf597e` | `53dcb696…` |
| #473 `2260609` (used for the Tidal revision) | `e33e64e1…` |
| `main` `a635783` | `35b1f340…` |

**System prompt, 292 words:**

| Share | Content |
|---|---|
| 21% | Role, "Generate narrative MECHANISMS", never invent names or facts |
| 19% | Six basic-emotion labels, effects, conditions, strategies, complex emotions |
| 19% | Genre contracts (incl. "renewable narrative engines"), typed genre interactions, phases |
| 38% | Field-by-field JSON listing |
| **0%** | **Causal composition, engine definition, link meaning, hierarchy, theme, conflict** |

**User message:** `{"revision_instruction": "", "working_context": {"previous_candidate": null, "vision": …, "working_connections": [≤80], "working_items": [≤24]}}`.
There was no design context, no Identity and no preferences.

**Schema:** the `ArchitectureCandidate` class definitions at `031eb693` are
byte-identical to those at `2260609`.

---

## 4. Crosswalk: ontology → original prompt → current prompt → schema slot

"Incidental" means the word occurs but not as narrative guidance (verified in context).

| Concept / principle | Original request (`031eb693`) | Current request (`main`) | Schema slot |
|---|---|---|---|
| Five-layer ownership | "never accept Identity, Structure or prose" only | Principle 1 | n/a |
| Character (agency) | Forbidden category only | "not concrete character … instances" | Forbidden in v2 (correct) |
| Arc | — | "conflict drives arcs" | None |
| Theme | Category enum value only | "thematic consequences"; "themes manifest through narrative change" | `theme` node; untyped links |
| Goal / want; stakes; resistance | — | "actor action patterns" only | None |
| Conflict | — | "conflict drives arcs" | None |
| Setup → payoff | "payoff expectations" in contracts only | "setups lead to payoffs"; "payoff mechanics" | `payoff_expectations` strings |
| Revelation | — | — | None |
| Reversal | — | Among the causal elements | None |
| Symbol / motif | — | — | `aesthetic` nodes only |
| Relationship (abstract) | Forbidden category only | "typed narrative relationships and their functions" | `ArchitectureLink.function` free text |
| What an engine is | "renewable narrative engines" **inside genre contracts only** | Organization (single / primary+layers / ensemble), ownership, action patterns, pressures, reversals, payoff; Identity's engine summary **only with an accepted `story_identity.yaml`** | `engine` node **and** `GenreContract.narrative_engine`, both free text, with no reference between them |
| Hierarchy | Field name `parent_id` only | Hierarchy "or its deliberate absence" legible | `parent_id`, meaning undefined |
| Link meaning | Field name only | "functional links", "causal interactions over decorative links" | Free text |
| Craft propagation; preferences; rich target experience | — | Principles 2, 4, 5; enum vocabulary | Emotion fields |
| Reader vs character emotion | — | "temporal movement" (partial) | Phase `reader_experience` |
| Claim epistemics | Author declarations vs hypotheses (emotions only) | Same + unknown policy | `EmotionTarget.provenance` only |
| Genre ontologies; cardinalities; rules | — | — (correctly) | n/a |

Before #472 the request carried **no** narrative ontology, only a
genre/emotion form and a JSON schema. The earlier adversarial reviews' "curated
summary" describes the post-#472 request.

---

## 5. Comparisons to perform on the actual artifact (not yet performed)

The capture kit only collects. The analysis below is computed in the
assessment step from `shareable/evidence.json`. Every reference there is a
consistent pseudonym, so links, hierarchy, contracts, interactions and
revision diffs survive anonymization.

| Comparison | Evidence used | Question it answers |
|---|---|---|
| Story Vision vs initial request | Vision text (owner's `private/` only); shared `story_vision_chars`, `story_vision_equals_canvas_now`, working items delivered | Was the agent working from a thin or a mechanism-rich Vision? |
| Initial request vs prompt history | Prompt hash → version; `recomputes`; `delivered` block | Confirms or refutes §3 for this exact request. |
| Initial candidate | The develop request's `response.json` candidate: structure always, labels/text at the chosen sharing level | Q4/Q5: architecture or labels? |
| Initial vs ontology-grounded revision | Revise request's `delivered` block; its response, staged review and current candidate, canonicalized so default-filled dumps compare equal to raw responses | Did delivered knowledge change the weaknesses? (Corroborating, confounded, free.) |
| Knowledge available vs delivered | §2/§4 plus each request's `delivered` block | Which absent distinctions show up as defects. |
| Causal coherence vs presentation | Pre-#471 rendering recomputed from structure: lines drawn (links + unique genre-interaction pairs), reciprocal pairs collapsed, undrawn `parent_id` relations; nodes drawn without a line vs nodes semantically unconnected | Did the graph look scattered because the candidate was, or because of the renderer? |

**Predictions to test.** These follow from the original prompt and schema. They are hypotheses, not observations.

| # | Prediction | Evidence fields (minimum sharing level) |
|---|---|---|
| P1 | Engine meaning sits in contract `narrative_engine` text; engine nodes are not referenced by contracts or linked to genres | `nodes[].category`, `links[]` endpoints (none); `genre_contracts[].narrative_engine` (text) |
| P2 | Link functions are mostly generic or "support" | `links[].function` (labels) |
| P3 | Hierarchy sparse or used as grouping | `nodes[].parent_id` (none) |
| P4 | Theme nodes are unlinked labels | `nodes[].category` + `links[]` endpoints (none) |
| P5 | Emotion/genre detail exceeds mechanism detail | counts (none); text for depth |
| P6 | Story mechanics deferred to `open_questions` (#471 added the provisional-defaults instruction on a Tidal-named branch) | count (none); content (text) |

**Assessment criteria.** The candidate counts as genuine architecture to the degree it has:

1. a mechanism with an owner, a pressure, and a reason it recurs;
2. directed links that name an operation;
3. genre contracts running on shared mechanisms;
4. a theme that a mechanism tests;
5. phases that change which mechanism dominates;
6. a reader experience that follows from (1)–(5).

**Attribution rule.** Each observed defect is filed under exactly one cause:

- **Knowledge delivery:** the distinction is absent from §4's original column, and the revision reduced the defect.
- **Schema limitation:** the schema cannot express the missing thing.
- **Unsupported inference:** the candidate claims what the Vision doesn't support.
- **Story Vision:** the Vision supplies no mechanism.
- **Presentation:** the defect is visual only.

---

## 6. Findings

### Confirmed (from source and history)

- **C1 — No ontology in the original request.** It held 0 words of causal composition. Every ontology term was incidental: `theme`/`relationship` as category names, "causal" only in "never a scientific/causal guarantee", "engine" only inside genre contracts.
- **C2** — All the relevant knowledge already existed in the repository (§2).
- **C3 — Schema unchanged since generation, with three gaps:**
  - no field ties a genre contract to an engine node;
  - `link.function` is untyped while `GenreInteraction.kind` is typed;
  - `parent_id` has no defined meaning.
- **C4 — The renderer at observation time** (`studio.js` before #471, unchanged since 2026-10-15) made any candidate look scattered:
  - nodes placed on a grid sorted by category and title (5 columns for 12 nodes);
  - `parent_id` never drawn;
  - a reciprocal genre-interaction pair drawn as one undirected line;
  - per #471, the start panel shown over a populated graph.
- **C5** — Model/runtime identity is probably absent from the artifact.
- **C6 — The engine summary is gated on Identity.** The current request delivers Identity's engine summary only when an accepted `story_identity.yaml` exists. STATUS/#473 say no Identity was created for Tidal Archive, so probably none exists; the kit records it.
- **C7 — The five-field engine contract is a single story-level summary, not a per-mechanism definition.** `StoryIdentity.central_engine` is required, singular, and all five fields are mandatory. `architecture_preferences.engine_hierarchy` may still be `ensemble` alongside it. Whether that pairing is a tension or an intended whole-story summary is an **open question** (§7.1, R13).

### Plausible hypotheses (need the capture)

- **H1** — The engine-locus split (P1) plus untyped links (P2) produced a weakly connected candidate.
- **H2** — Story mechanics were deferred into `open_questions` (P6).
- **H3** — The "scattered" perception came mainly from presentation (C4). It can coexist with H1.
- **H4** — Emotion/genre weighting produced a label-rich, mechanism-poor candidate (P5).
- **H5** — Revelation/reversal or setup/payoff conflation. Neither prompt defines these; there is no evidence of it yet.

### Falsified or unsupported

- **X1** — "The original request carried compressed ontology summaries." **False:** it carried none.
- **X2** — "Unenforced ontology validator rules affected initial generation." **False:** that code path was never reached.
- **X3** — "The single-governing-engine wording biased the initial candidate." **False:** the wording first appeared in #472, and #475 has since repaired it.
- **X4** — "Full ontology loading is needed." **Unsupported:**
  - the gaps are a few definitions;
  - Layer 0 cardinalities and rules don't fit abstract Studio nodes;
  - the YAML contains contradictory text (`base_ontology.yaml:113`).
- **X5 (new)** — "The five-field engine contract can define every engine node." **False** (§7).
- **Not reopened:** schema-v1 acceptance (#474); the kit records `schema_version`.

---

## 7. Design tests for the candidate remedies

### 7.1 Is the five-field engine contract compatible with ensemble architectures?

**No, not as a universal definition.**

- **It is singular by design.** `StoryIdentity` has exactly one required
  `HighLevelCentralEngine`. An Identity whose `engine_hierarchy` is `ensemble`
  must still state one `want` / `resistance` / `conflict` / `stakes` /
  `change`. That works as a whole-story summary of what the ensemble adds up
  to. Used as an instruction for building the architecture, it would push the
  agent back toward a single center, the bias #475 removed.
- **It presumes an agent.** As a per-mechanism template, each engine node
  would need a `want`. That fits mechanisms driven by an agent: a character, a
  faction, an institution acting deliberately. It does not fit non-agent
  mechanisms such as environmental change, an information economy, ritual
  recurrence, or atmospheric accumulation. Review 2's counterexamples A
  (contemplative recurrence) and B (institutional pressure + intimate loyalty
  + environmental change) both include mechanisms with no want. Forcing one
  would anthropomorphize them.
- **A compatible vocabulary already exists.** Phase F's causal profile
  (`causal_owner` incl. `ensemble`, `external_action_pattern`,
  `pressure_system`, `climax_mechanic`) describes agent and non-agent
  mechanisms, and multi-owner causation.

**Revised remedy.** If engine semantics are delivered, describe each mechanism
with the causal-profile terms. Offer want / resistance / stakes / change only
as an optional lens for mechanisms driven by an agent. Leave the five-field
summary where it is, in accepted Identity.

**Open architectural question (R13).** A single required `central_engine`
alongside an `ensemble` preference may be a genuine tension. It may also be
intended: one whole-story summary of what an ensemble produces. This review
does not decide which. It is an owner-reserved Identity question, not a prompt
fix. Evidence that would settle it: an ensemble story whose single summary
visibly distorts its architecture, or the owner's statement of intent.

### 7.2 Can a genre-to-engine reference be expressed with existing schema fields?

| Option | Coherent? | Why |
|---|---|---|
| Name engine node IDs inside `GenreContract.narrative_engine` prose | **No** | Not validated, not machine-readable, can silently dangle. It is a mention, not a reference. |
| `parent_id` of the genre node = engine node | **No** | Single parent cannot express a genre running on several engines (ensembles). It also asserts that a genre is a sub-part of an engine, and the hierarchy's meaning is undefined. |
| An `ArchitectureLink` between the engine node and the genre node | **Yes, as an untyped association** | Endpoints are validated, and the genre node stands for its contract (contracts are unique per `genre_node_id`). It supports many-to-many, so it is ensemble-compatible, and the current renderer draws it. Its meaning lives only in `function` prose, so it is not a typed reference. |

So a **prompt-only** change can coherently ask for "a link from each engine
node to every genre node whose contract depends on it, with a function naming
the dependency". It **cannot** provide a typed reference.

A **typed** reference needs a schema change:
- an optional `GenreContract.engine_node_ids: list[str]` (default `[]`),
  validated to reference existing `engine` nodes;
- the prompt field listing updated;
- inspector/graph rendering of it (`_candidate_diff` already diffs contracts
  whole);
- an owner decision on versioning. The model is strict (`extra="forbid"`): old
  v2 artifacts stay valid, but older readers would reject new ones.

Not proposed for implementation now (R1).

### 7.3 Smallest justified generation-context change

**Not warranted yet.** It becomes admissible when the capture confirms a defect
in the **initial** candidate, and that defect traces to knowledge the
**current develop request still omits or compresses** (§4, current column).

Whether the defect persists in the ontology-grounded revision is corroborating
evidence, not a prerequisite. The revision also received the previous
candidate and a targeted instruction, so it is not a clean test of
initial-generation context.

If P1/P2 are confirmed on those terms, the candidate change is about 60–100
words, prompt-only:

1. Describe each mechanism with Phase F causal-profile terms; use want /
   resistance / stakes / change only where a mechanism is driven by an agent
   (§7.1).
2. Link each engine node to the genre nodes whose contracts depend on it
   (§7.2, untyped).
3. State each link's operation (causes, constrains, tests, reveals, reverses),
   with source → target as causal direction.
4. **Only if H5 is observed:** one sentence separating revelation (changes
   understanding) from reversal (inverts the trajectory).

Placement: items 2–4 go in `_SYSTEM`, which doesn't change the fingerprint.
Item 1 is ontology content and goes in `_DESIGN_PRINCIPLES`, staling saved work
once, as #475 did.

**Not recommended:** a YAML dump, cardinalities or rules, genre ontologies, the
five-field contract as a universal definition, or schema v3.

---

## 8. Prioritized ontology/schema findings register

### Initial-generation path

| ID | Finding | Kind | Priority | Admission evidence |
|---|---|---|---|---|
| R1 | No typed contract → engine reference; engine meaning split across four places. Schema change specified in §7.2 | Schema | **P1** | P1 confirmed, and the untyped-link convention proves insufficient |
| R2 | Mechanism semantics (causal-profile terms) not delivered per mechanism; Identity's engine summary only with accepted Identity | Context | **P1** | P1/P2 confirmed in the initial candidate and traced to an omission still present in the current develop request |
| R3 | `parent_id` meaning undefined and not drawn | Schema + presentation | P1 | Hierarchy misread or misused |
| R4 | Untyped `ArchitectureLink.function` vs typed `GenreInteraction.kind` | Schema | P2 | Prose functions cannot carry a needed distinction |
| R5 | Three unreconciled "governing" notions (contract role, phase participation role, `engine_hierarchy`) | Schema | P2 | Contradiction observed |
| R6 | Model/runtime not captured by the documented handoff | Evidence process | P2 | Needed before any comparison |
| R7 | Structural validity ≠ adequacy; no advisory semantic diagnostics | Validation | P2 | Repeated narrow failure class |
| R8 | `GenreContract.narrative_engine` required, pushing atmospheric genres into engines | Schema | P3 | Observed forced engine |
| R9 | Theme & motif and emotional trajectory contracts not delivered | Context | P3 | Persisting theme or trajectory failure |
| R10 | Per-node provenance absent; `author_declared` unvalidated | Schema | P3 | Misattribution observed |
| R11 | One phase `order` for both chronology and disclosure | Schema | Deferred | Nonlinear Vision needing it |
| R12 | Guidance edits stale all saved work | Process | Deferred | Frequent guidance changes |
| **R13** | **Open question: Identity requires one `central_engine` while allowing `engine_hierarchy = ensemble`. Tension or intended whole-story summary?** | **Identity (owner-reserved)** | **Open** | **An ensemble story whose single summary distorts it, or a statement of owner intent** |

### Outside the initial-generation path (separate legacy lane; do not mix)

| ID | Finding |
|---|---|
| L1 | Mystery concepts named differently in YAML and Python; `many-to-one` cardinality not in the typed schema |
| L2 | `OntologyValidator.enforce_validation_rules()` evaluates no rules; only tests call it |
| L3 | Self-contradictory rule text (`base_ontology.yaml:113`) |

---

## 9. Would a bounded model comparison add information?

**No, not now.**

- **Inspection can test P1–P6 and attribute each defect.** A comparison only
  answers the counterfactual "would a context slice change the output?"
- **A free comparison already exists.** The capture holds the initial and
  revised candidates: confounded by the revision instruction, but costless.
- **Re-running the original prompt would only re-measure #472.**
- **Model identity is uncontrolled (C5).** With one sample per condition, a
  small slice's effect cannot be told apart from noise.

**Admit one bounded comparison only if all of these hold:**

1. a defect is confirmed in the initial candidate;
2. it traces to an omission still present in the current develop request
   (persistence in the revision corroborates but is not required);
3. a slice of ≤100 words targets it;
4. model and runtime will be recorded.

Then run one develop per condition (current `main` vs `main` + slice) on the
same Vision and judge qualitatively against §5.

---

## 10. Capture kit review

[`scripts/tidal_forensic_capture.py`](../../scripts/tidal_forensic_capture.py)
is standard library only (Python 3.10+) and needs no Auteur install. It
collects evidence and does no narrative analysis; analysis happens in the
assessment step (§5), so the tool that touches the private project stays small.

| Guarantee | How |
|---|---|
| Read-only | Writes only to a new `auteur-capture-<UTC>` folder under `--out`; refuses an `--out` inside the project (`realpath` + `normcase` + `commonpath`); never follows symlinks or Windows junctions, detected by `os.lstat` and the reparse-tag name-surrogate bit on every supported Python (3.10 and 3.11 lack `os.path.isjunction`); refuses Python < 3.10 |
| One canvas per capture | With several architecture canvases and no `--canvas`, it refuses before writing anything |
| Integrity | Hashes each source before copying, hashes the copy, rehashes the source afterwards, and re-inventories the canvas. A file that changes, vanishes or appears, or a copy that differs from a stable source, makes the capture **DISQUALIFIED**: status in both reports, `DISQUALIFIED.txt`, exit code 3. Files are kept for diagnosis only. Detection compares before and after, so a change undone in between is invisible; close Studio first. |
| Provenance without accusation | Known prompt versions are named. An unknown hash, or a request hash that does not recompute, is reported as a provenance question. `--auteur-repo` identifies local or unpushed prompts by commit and date; commit subjects are never recorded. |
| Shareable privacy | All node, link, phase, emotion, interaction, request and canvas IDs, and unknown path segments, become consistent per-capture pseudonyms (`N01`, `R01`, `F01`, …). The table stays in `private/`. No hashes of private content are shared (an unkeyed hash of short text lets a guesser confirm it). Link targets are never recorded, even privately, and file hashes are not shared. Candidate text is masked unless `--share-labels` (titles, link functions, genre labels) or `--share-text`; `--redact` masks names in shared text. **Those two levels expose the author's creative material**: pseudonyms hide identifiers, not content. The help text, both reports, `evidence.json` and the console all say so. The Story Vision, working items and revision instructions are never shared, only their lengths. |
| Comparable candidates | Shared candidates are canonicalized (schema defaults dropped), so a raw response and a stored model dump of the same content compare equal. Without this, the earlier draft reported every node of a revision as changed. |

**Tests** (`tests/test_tidal_forensic_capture.py`, 6 passed):
- the project is unchanged (bytes and mtimes) and the copies are identical;
- an output folder inside the project, and an ambiguous canvas choice, are refused before writing;
- junction, symlink and WSL-link reparse tags are excluded and cloud placeholders kept, with `os.path.isjunction` removed;
- a changed file and a newly appearing file each disqualify the capture;
- adversarial privacy: a canary placed in the canvas ID, every ID kind, titles, genre labels, an extra filename, a symlinked directory holding a canary file and a local commit subject appears nowhere in `shareable/`, filenames included. Neither do raw Vision, request or source hashes. Pseudonyms still connect links, contracts, emotion references and the revision diff, and the private side does hold the canary;
- unknown-prompt provenance.

Mutations that each make a test fail: no inside-project refusal, real IDs shared,
no post-copy rehash, no canonicalization, several canvases allowed, Vision hash
shared, reparse tag ignored, no re-inventory, creative-material flag always off.
The kit's command line also ran on Python 3.10, 3.11, 3.12 and 3.13 with
identical shareable evidence. These fixtures test the tool only; none is evidence about Tidal Archive.

---

## 11. Next action (owner)

1. Close Auteur Studio.
2. On the Windows machine, from a checkout that includes the script, run:

   ```powershell
   python scripts\tidal_forensic_capture.py --project "C:\path\to\tidal-archive" --out "D:\tidal-forensics" --canvas <canvas-id> --auteur-repo . --share-labels
   ```

   Add `--redact "Name"` for proper nouns to mask. Exit code 3 means the capture
   is disqualified: close Studio and run it again.
3. Share `shareable\evidence.json` and `shareable\report.md`. Keep `private\` to yourself.
4. The narrative judgment (§5 criteria) needs candidate prose. If you are
   willing, rerun with `--share-text`; the Vision is still withheld.
5. The actual-candidate assessment (§5–§6, the attribution rule and §7.3)
   follows from those files.
