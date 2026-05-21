# Auteur Engine v1 — Plan → Draft → Critique → Iterate

## Goal

Make `auteur draft <project_dir> <chapter_index>` produce a chapter that has been:

1. Planned by the Cartographer (existing).
2. Drafted by the Bard from that outline plus relevant Bible context.
3. Validated by a fan-out of focused Critics (contract, arc, tension, slop, theme).
4. Either auto-accepted (all critics pass within `max_iterations`) or left on disk with a structured validation report for human review.

When accepted, the Bible records the chapter event and the realized tension score. No other Bible mutations happen in v1.

This is the smallest milestone after which the project produces *prose*, not prompts.

## Non-goals (deferred to later sub-projects)

- Bible auto-update beyond appending `events` and `realized_tension`. No automatic character state diffing, arc percentage advancement, or relationship updates.
- Cross-chapter context retrieval (RAG over prior `final.md` files). The Bard sees only the current outline plus structured Bible state.
- Streaming output.
- Streamlit / web UI / VS Code sidecar.
- RP runtime (different latency and persistence model — separate sub-project).
- skills.md distillation.
- Multi-chapter autonomous loops. v1 is one-chapter-at-a-time.

## Scope decisions (locked)

| Decision | Choice |
|---|---|
| LLM provider | Provider-agnostic adapter from day one. Anthropic + OpenAI clients. |
| Critic checks | Full validation pipeline — contract, arc, tension, slop, theme. |
| Loop termination | Max N iterations (default 3) followed by human gate. |
| Project layout | Project-as-directory, every artifact a versioned file. |
| Bible updates | Only on accept. Failed-out chapters leave Bible untouched. |
| Critic structure | Five focused critics in parallel, one aggregated `ValidationReport`, one consolidated rewrite-feedback bundle per iteration. |

## Architecture

```
src/auteur/
├── blueprint.py         (existing, unchanged)
├── bible.py             (existing — extended with append_event / append_tension helpers)
├── cartographer.py      (existing, unchanged)
├── llm/
│   ├── __init__.py      LLMClient Protocol, LLMRequest/LLMResponse dataclasses
│   ├── anthropic.py     AnthropicClient (uses anthropic SDK; prompt caching on system prompt)
│   ├── openai.py        OpenAIClient (uses openai SDK)
│   └── fake.py          FakeClient for tests — replays scripted responses
├── bard.py              outline + bible context → prose draft; rewrite mode accepts findings
├── critic/
│   ├── __init__.py      CriticFinding, ValidationReport, run_critics()
│   ├── base.py          Critic Protocol, render helpers
│   ├── contract.py
│   ├── arc.py
│   ├── tension.py
│   ├── slop.py
│   └── theme.py
├── project.py           Project — wraps a directory, owns blueprint + bible + chapter artifacts
├── pipeline.py          (extended) — adds draft_chapter(...)
└── cli.py               (extended) — adds `init`, `draft`, `accept`, `retry`
```

### Component contracts

#### `Project`

`Project(path: Path)` — represents a project directory.

```python
class Project:
    path: Path
    blueprint: StoryBlueprint
    bible: StoryBible

    @classmethod
    def init(cls, path: Path, blueprint: StoryBlueprint) -> "Project": ...
    @classmethod
    def load(cls, path: Path) -> "Project": ...

    def chapter_dir(self, n: int) -> Path           # path/chapters/{n:02d}/
    def next_draft_version(self, n: int) -> int     # scans chapter_dir for draft_v*.md
    def write_outline(self, n: int, outline: dict) -> Path
    def write_draft(self, n: int, version: int, prose: str) -> Path
    def write_validation(self, n: int, version: int, report: ValidationReport) -> Path
    def write_final(self, n: int, prose: str) -> Path
    def has_final(self, n: int) -> bool
```

Directory layout:

```
my_novel/
  blueprint.yaml
  bible.json
  chapters/
    01/
      outline.yaml
      draft_v1.md
      validation_v1.json
      draft_v2.md
      validation_v2.json
      final.md
    02/
      ...
```

#### `LLMClient` (Protocol)

```python
class LLMRequest(BaseModel):
    system: str
    user: str
    max_tokens: int = 4096
    temperature: float = 0.7
    model: str | None = None  # provider-default if None

class LLMResponse(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int

class LLMClient(Protocol):
    def complete(self, req: LLMRequest) -> LLMResponse: ...
```

- `AnthropicClient` reads `ANTHROPIC_API_KEY`, defaults to `claude-sonnet-4-6`, caches the system prompt (the Cartographer / Bard / Critic system prompts are large and reused across iterations).
- `OpenAIClient` reads `OPENAI_API_KEY`, defaults to `gpt-4o`.
- `FakeClient` takes a list of `LLMResponse` objects and returns them in order; raises if the list is exhausted. Used in tests so we never hit real LLMs.

The clients are instantiated at the CLI boundary and passed down. Nothing inside `auteur/` imports `anthropic` or `openai` directly.

#### `Bard`

```python
def render_bard_prompt(
    outline: dict,
    bible: StoryBible,
    blueprint: StoryBlueprint,
    chapter_index: int,
    prior_draft: str | None = None,
    findings: list[CriticFinding] | None = None,
) -> tuple[str, str]: ...
```

System prompt gives the Bard:
- POV mode and style guidance derived from `blueprint.identity`.
- Hard contract rules (flattened, identical to Cartographer).
- Output format: pure prose, Markdown. No commentary, no headings beyond chapter title. Word-count target derived from `estimated_word_count / estimated_chapters`, with ±20% tolerance.

User message includes:
- The full outline (YAML).
- A compact Bible context: characters mentioned in the outline with their `current_state`, plus locations referenced.
- If `prior_draft` and `findings` are provided: a "REWRITE TASK" section with the prior draft and the consolidated findings, instructing the Bard to revise without breaking the outline.

Two modes (`draft` and `rewrite`) share the same renderer; rewrite simply appends extra sections.

Post-processing on the Bard's response: strip leading/trailing whitespace; if the entire response is wrapped in a Markdown code fence (```` ```markdown ```` or `````` ``` ``````), unwrap it. No further parsing — prose is stored verbatim. The contract critic catches structural deviations (e.g. the Bard accidentally narrated commentary) as findings, not parse failures.

#### Critic system

```python
class CriticFinding(BaseModel):
    critic: Literal["contract", "arc", "tension", "slop", "theme"]
    severity: Literal["error", "warning"]
    rule: str                         # short identifier, e.g. "forbidden_trope:chosen_one_prophecy"
    evidence: str                     # short quote or paraphrase from the draft
    requested_change: str             # imperative: "remove the prophecy reveal in scene 2"

class ValidationReport(BaseModel):
    chapter_index: int
    iteration: int
    findings: list[CriticFinding]
    passed: bool                      # computed once at construction by run_critics: not any(f.severity=="error" for f in findings). Stored on the model so the on-disk JSON is self-describing.

def run_critics(
    draft: str,
    outline: dict,
    blueprint: StoryBlueprint,
    bible: StoryBible,
    chapter_index: int,
    iteration: int,
    llm: LLMClient,
) -> ValidationReport: ...
```

`run_critics` fans the five critics out via `concurrent.futures.ThreadPoolExecutor`, each returning `list[CriticFinding]`. Findings are concatenated in the order of the critics list (deterministic). `passed = not any(f.severity == "error" for f in findings)`.

`base.py` defines the `Critic` Protocol (a callable taking the standard kwargs and returning `list[CriticFinding]`) plus shared rendering helpers (e.g. compact bible-context formatting, draft truncation if the chapter exceeds a token budget). Each of the five critic modules owns its own system prompt, temperature, and parser; `run_critics` imports and calls them by name. The Protocol exists for typing and for future user-defined critics; v1 hard-codes the five built-ins.

Per-critic implementation pattern (one file each):

```python
SYSTEM_PROMPT = """..."""
TEMPERATURE = 0.0   # deterministic-ish for validation

def render(...) -> tuple[str, str]: ...
def parse(text: str) -> list[CriticFinding]: ...
def run(draft, outline, blueprint, bible, chapter_index, llm) -> list[CriticFinding]:
    sys, usr = render(...)
    resp = llm.complete(LLMRequest(system=sys, user=usr, temperature=TEMPERATURE, max_tokens=2000))
    return parse(resp.text)
```

Each critic asks for a YAML response with one top-level key `findings:`, list of objects matching `CriticFinding` minus the auto-filled `critic` field. Parsing is strict; a malformed response raises and surfaces as a `CriticError` in the report (severity=error, rule="critic_parse_failure"). This is intentional — we want to know when a critic misfires, not paper over it.

**What each critic checks:**

- **contract** — every flattened contract rule, every forbidden trope, every expected element (recorded as warning if not touched in this chapter; error only if outright violated). Also: character state continuity by cross-referencing `bible.characters[name].current_state` against the draft (e.g. "Kael has broken_arm in bible — is he wielding a two-handed weapon?"). Word-count tolerance is enforced here too: a chapter outside `(target_word_count / chapters) * (1 ± 0.20)` produces a warning (`pacing:word_count_drift`); 50%+ deviation is an error.
- **arc** — given the outline's `arc_advancements` for this chapter and each character's `next_milestone` from the blueprint, does the prose support the advancement? Errors when a milestone is claimed but unsupported by prose.
- **tension** — given `outline.estimated_chapter_tension` and `blueprint.tension_waveform.target_for(chapter_index)`, does the prose feel like it actually hit that score? Errors only on `|realized − target| > 2` (we trust the Cartographer's plan; the critic catches drafting drift).
- **slop** — clichés, AI-tells ("a testament to", "in the realm of"), repetition, abstract emotion-naming instead of showing. Mostly warnings; errors only for hard signals (e.g. five clichés in one paragraph).
- **theme** — central question echoed somewhere; at least one motif present. Warnings only — theme is a long-game concern, not a per-chapter gate.

#### `PipelineRunner.draft_chapter`

```python
@dataclass
class DraftResult:
    chapter_index: int
    accepted: bool                   # True if any iteration passed
    iterations: int                  # how many drafts were produced
    final_path: Path | None          # set iff accepted
    last_validation: ValidationReport
    cost: TokenAccounting            # sum of input+output across all calls

def draft_chapter(
    self,
    chapter_index: int,
    *,
    llm: LLMClient,
    max_iterations: int = 3,
    on_iteration: Callable[[int, ValidationReport], None] | None = None,
) -> DraftResult: ...
```

Behavior:

1. Run the Cartographer (existing). If the response includes a non-null `conflict_report`, write `outline.yaml` with the conflict, do not draft, return `accepted=False, iterations=0`. The CLI prints the conflict and exits non-zero.
2. Else, write `outline.yaml`. Initialize `prior_draft=None, findings=None`.
3. Loop `i` from 1 to `max_iterations`:
   - Render Bard prompt (draft or rewrite mode based on whether `prior_draft` is set).
   - LLM call → prose. Write `draft_v{i}.md`.
   - `run_critics(...)` → `ValidationReport`. Write `validation_v{i}.json`.
   - Call `on_iteration(i, report)` if supplied (CLI uses this to print progress).
   - If `report.passed`: write `final.md` from this draft, append event + realized_tension to bible.json, break with `accepted=True`.
   - Else: set `prior_draft = this_draft`, `findings = report.findings`, continue.
4. If loop exits without acceptance: return `accepted=False, iterations=max_iterations`. Final not written. Bible unchanged.

#### CLI surface

```
auteur init <path> --from <blueprint.yaml>
    Create a new project directory. Copies blueprint.yaml in,
    initialises bible.json with the default skeleton from
    bible._INITIAL, and creates chapters/.

auteur plan <blueprint.yaml> <chapter_index>
    (Existing, unchanged.) Renders Cartographer prompt from a raw
    blueprint file. Kept for prompt debugging without requiring a
    project directory and without burning LLM tokens.

auteur draft <project_dir> <chapter_index>
    [--max-iterations N]            default 3
    [--provider anthropic|openai]   default anthropic
    [--model NAME]                  provider default if omitted
    Runs the full plan→draft→critique loop.
    Exit codes: 0 accepted, 1 unexpected error, 2 iterations exhausted (artifacts on disk),
                3 conflict_report (outline contradicts itself).

auteur accept <project_dir> <chapter_index>
    Promotes the latest draft_v*.md to final.md and updates bible.json.
    Used after a human edits a draft that didn't pass automatically.

auteur retry <project_dir> <chapter_index>
    Continues iteration past the previous max-iterations cap.
    Picks up from the highest existing draft_v* + its validation.
```

`auteur init` is intentionally simple — no scaffolding wizard, no `auteur configure`. The user authors the blueprint YAML directly. (Wizardry is a UI concern; we deferred UI.)

## Workflow walkthroughs

### Happy path

```
$ auteur draft ./shattered_crown 1
Cartographer planning chapter 1...
  outline.yaml written.
Bard drafting (iteration 1)...
  draft_v1.md written (3,847 words).
Running 5 critics in parallel...
  validation_v1.json written.
  contract:  3 ok / 1 warning
  arc:       ok
  tension:   ok (target 4, estimated 5)
  slop:      2 warnings
  theme:     ok
ACCEPTED on iteration 1.
  final.md written.
  bible.json updated (+1 event, +1 realized_tension).
Cost: 12,450 in / 4,210 out tokens.
```

### Validation failure → rewrite → accept

```
$ auteur draft ./shattered_crown 7
...
Bard drafting (iteration 1)...
Running 5 critics in parallel...
  contract: 1 ERROR (forbidden_trope:chosen_one_prophecy used in scene 2)
ITERATION 1 FAILED. Rewriting...
Bard rewriting (iteration 2)...
Running 5 critics in parallel...
  all critics: ok
ACCEPTED on iteration 2.
```

### Iterations exhausted

```
$ auteur draft ./shattered_crown 22
...
ITERATION 1 FAILED (2 errors).
ITERATION 2 FAILED (1 error).
ITERATION 3 FAILED (1 error).
NOT ACCEPTED.
  draft_v3.md kept; validation_v3.json describes remaining errors.
  Edit draft manually then run:  auteur accept ./shattered_crown 22
  Or to keep iterating:          auteur retry ./shattered_crown 22
exit 2
```

### Cartographer conflict_report

```
$ auteur draft ./shattered_crown 23
Cartographer planning chapter 23...
CONFLICT: tension_target=3 but arc requires Kael to commit a major betrayal.
  See ./shattered_crown/chapters/23/outline.yaml for details.
exit 3
```

## Data shapes

### `validation_v{n}.json`

```json
{
  "chapter_index": 7,
  "iteration": 1,
  "passed": false,
  "findings": [
    {
      "critic": "contract",
      "severity": "error",
      "rule": "forbidden_trope:chosen_one_prophecy",
      "evidence": "scene 2: 'the prophecy named him the chosen heir'",
      "requested_change": "remove all prophecy framing; reattribute Kael's selection to political maneuvering."
    }
  ]
}
```

### `bible.json` mutations on accept

```python
bible.record_event(
    chapter_index=N,
    summary=outline["chapter_summary"],
    deltas={"draft_iterations": result.iterations}
)
bible.record_tension(N, outline["estimated_chapter_tension"])
bible.save()
```

No character state mutation in v1. That comes with the long-form runtime sub-project, where a dedicated Bible Updater agent diffs `current_state` against the chapter prose.

## Testing strategy

Tests are Pytest-only (already declared in `pyproject.toml` dev extras). No real LLM calls.

Three layers:

1. **Unit tests** for each module against `FakeClient`:
   - `test_blueprint.py` — already implicit in current code; add tests for the new `Project` class and helpers.
   - `test_bard.py` — `render_bard_prompt` produces the expected sections for draft-mode and rewrite-mode.
   - `test_critic_<name>.py` — feed canned drafts + scripted FakeClient responses; assert findings are parsed correctly.
   - `test_pipeline_runner.py` — `draft_chapter` happy path, failure-then-rewrite path, exhaustion path, conflict-report path. Uses `FakeClient` with a scripted sequence of LLM responses (one Cartographer, then alternating Bard / 5 critics per iteration).

2. **One golden integration test** (`test_engine_v1_smoke.py`) using `examples/sample_blueprint.yaml`:
   - Two characters, three chapters, one hard rule (e.g. forbidden trope).
   - Scripted FakeClient responses where iteration 1 violates the rule and iteration 2 fixes it.
   - Asserts: iteration 2 accepted, `final.md` exists, `bible.json` has one event and one realized_tension entry.

3. **A make-real-call script** in `scripts/smoke_real_llm.py` (not a pytest), gated on `ANTHROPIC_API_KEY`. Runs one chapter end-to-end against the actual API. Used manually before releases — not in CI.

## Risks and open questions

- **Critic LLM calls are expensive.** Five parallel calls per iteration × up to three iterations = up to 15 critic calls per chapter on top of plan + drafts. For a 45-chapter book, that's ~700 critic LLM calls. Mitigation: per-critic `max_tokens` capped at 2000, system prompts cached, temperature 0. Worth tracking real cost in the smoke script before scaling.
- **Critic-induced thrash.** A critic could demand a fix that another critic dislikes (slop critic says "less abstract emotion", theme critic says "more thematic resonance"). v1 accepts this risk and prints all findings; the rewrite prompt warns the Bard to balance them. If thrash is real in practice, v1.1 introduces a meta-critic that resolves contradictions before sending findings to the Bard.
- **LLM YAML parsing.** YAML from LLMs is famously unreliable. Mitigation: each critic's parser is a strict Pydantic load, and parse failure becomes its own surfaced finding rather than an exception. The Bard returns Markdown prose, which has no parse risk.
- **`forbidden_tropes` are semantic, not literal.** A critic LLM is required even for "forbidden trope detection" — substring search on `chosen_one_prophecy` won't find a chapter that *enacts* a chosen-one prophecy without naming it. The contract critic's prompt explicitly demands paraphrase-aware detection.
- **Bible compactness.** The Bard's user message embeds Bible context for characters mentioned in the outline. For a 45-chapter project with rich state, this could grow large. v1 sends `current_state` only; a later sub-project introduces summarization.
- **What about chapter-1 cold start?** No prior chapters exist, so `recent_tension_scores` is empty and `bible.events` is empty. The pipeline already handles this — Cartographer and critics tolerate empty history. Smoke test must cover chapter 1 explicitly.
- **Concurrency.** `ThreadPoolExecutor` is fine for I/O-bound LLM calls. If a provider client is not threadsafe (Anthropic's is, OpenAI's is) we wrap calls in a per-client lock. Not anticipating issues.

## What this design *does not* commit to

- A specific token budget per chapter. Will be measured during smoke tests.
- A specific retry policy on transient LLM errors. The clients raise; v1 surfaces the error to the CLI and the user re-runs. v1.1 adds backoff if it hurts in practice.
- An on-disk schema version for `bible.json`. v1 uses the existing flat schema. A `schema_version` field gets added when the Bible Updater sub-project lands.
