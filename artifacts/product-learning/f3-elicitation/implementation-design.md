# Implementation Design — F3: consequence-focused elicitation for genuinely unsettled cross-goal significance

> Phase: implementation design. Mechanism **M1 — `decision elicit` subcommand**,
> agent-selected under delegated product authority (human brief 2026-08-11; discovery
> evidence @ 95bb30b on `discovery/f3-elicitation`). Human-demonstrated interaction
> pattern (zero-code test @ fd12ced + ed02cd8): consequence-focused elicitation helped
> the author discover a preference; continue-undecided is a required non-coercive
> outcome; provisional Auteur position (F4) added no distinct value. Base SHA: a21bb43
> (origin/main, PR #68 merged). Production source read-only until construction begins.

## 0. Design hypothesis (binding)

A genuinely unsettled author — "I care about both goals and don't know which loss
matters more" — can be helped by an interaction that puts the **already-composed
concrete consequences** in front of them and asks which concrete loss they would regret
more, rather than asking for an abstract goal ranking. Recording the outcome must reuse
the existing F1 `goal_significance` representation and must never manufacture a
preference, never infer from prose, and never convert uncertainty into non-precedence.

## 0.1 Claim language (binding)

- **human-demonstrated:** the consequence-focused elicitation pattern helped in the
  frozen F3 case (one case; not generalized).
- **agent-selected/validated:** M1 as the production mechanism and its qualification.
- **post-merge observed:** behavior of the shipped implementation in continued use.
- No claim of human approval for intermediate mechanism/design choices.

## 1. Mechanism (binding): `decision elicit` — one command, two modes

New subcommand under the existing `decision` namespace (registered in
`register_author_decision_subcommands`):

```
auteur decision elicit <decision_id> --identity <identity.yaml> --blueprint <blueprint.yaml> [--project .]
auteur decision elicit <decision_id> --identity ... --blueprint ... --record ordered <REF1> <REF2>
auteur decision elicit <decision_id> --identity ... --blueprint ... --record unranked
auteur decision elicit <decision_id> --identity ... --blueprint ... --record undecided
```

### 1.1 Render mode (default; read-only; no mutation)

Builds the decision context (existing `build_decision_context` + `build_report`) and
renders:

1. **Concrete consequences (verbatim, grouped):** for each cut alternative, its
   composed `nature_consequence` "removes" findings, rendered as "If you CUT
   `<alt>`, you remove:" followed by the verbatim lines. Rendered ONLY from the
   shipped composed report — no new inference, no prose parsing.
2. **The consequence-focused question:** "Which of these concrete losses would you
   regret more?" — consequence-anchored, never an abstract goal ranking.
3. **Valid outcomes block:** the three valid author states with the exact record
   commands (ordered / unranked / undecided).

Render is deterministic and identical for fixtures differing only in question/criterion
prose (anti-inference control).

### 1.2 Record mode (`--record`; explicit author action; atomic; auditable)

- **`--record ordered <REF1> <REF2>`** — validates the pair through the existing F1
  fail-closed path (`AuthorDecision.from_dict` with `goal_significance` set:
  explicit-root grammar, exactly-2 distinct refs, participation in this decision's
  `bears_on` tradeoff), then writes `goal_significance: {ordered: [REF1, REF2]}` via
  `persistence.atomic_write_yaml`.
- **`--record unranked`** — writes `goal_significance: {unranked: true}` (affirmative
  intentional non-precedence, F1 semantics).
- **`--record undecided`** — writes NOTHING; prints an explicit acknowledgment that the
  decision remains genuinely undecided and may be revisited later. Never converts to
  `unranked`.
- Record is refused (file unchanged) when `goal_significance` is already present —
  authored significance is not silently overwritten (mirrors the `create --force`
  refusal posture; author may edit YAML directly to change it).
- The record write goes through `AuthorDecision.from_dict` round-trip before writing —
  schema fail-closed is inherited, not reimplemented.

## 2. Binding behavior (from the delegation brief)

1. Helps the unsettled author examine **concrete consequences already known by Auteur**
   — never an abstract goal ranking.
2. Valid outcomes ONLY:
   - discover A > B → may explicitly record existing F1 `ordered`;
   - discover intentional non-precedence → may explicitly record existing F1 `unranked`;
   - still does not know → remains genuinely undecided (valid; nothing written).
3. Never silently convert uncertainty into non-precedence.
4. Never infer author significance from prose.
5. Never manufacture a ranking or recommendation.
6. Reuse F1 `goal_significance` as the destination; no parallel preference state.

## 3. Controls and golden discriminators (binding for qualification)

1. **Render golden** — competing-goals case (`case-goal-significance` fixtures):
   per-cut loss grouping + consequence-focused question + valid outcomes; exit 0.
2. **Anti-inference render** — `unsettled-prose.yaml` and `absent.yaml` render
   **byte-identical** (prose never parsed).
3. **Directionless one_of** — no composed losses exist; render says so honestly
   (no manufactured losses; no composition without authored direction).
4. **Record ordered** — YAML gains `goal_significance.ordered`; reload via
   `AuthorDecision.from_yaml` shows it; subsequent evaluate emits the F1 observation.
5. **Record unranked** — YAML gains `goal_significance.unranked`.
6. **Record undecided** — YAML byte-identical before/after; message states undecided.
7. **Record fail-closed** — invalid refs (non-participating, duplicate, 3 refs,
   non-explicit-root) rejected; file unchanged.
8. **Record refusal when present** — already-declared significance not overwritten.
9. **Nonexistent decision** — clean error, exit != 0.
10. **Central invariant** — consequences byte-identical with/without the recorded
    field (F1 invariant preserved); elicitation adds only the render + explicit record.

## 4. Out of scope (binding)

F4 provisional Auteur recommendation; numeric weights / preference machinery;
product-generated ranking; new LLM dependency; canonical/global priority; new substantial
story ontology; 3+ goal significance semantics; preference inference from prose;
parallel preference state beyond F1; interactive multi-turn prompting; proposal artifact
flow.

## 5. Verification plan

- TDD: RED tests first (render, anti-inference, records, fail-closed, refusal,
  undecided no-op, existing goldens unchanged).
- Full verification stack on the merge path: pytest (categories reported separately),
  ruff, `scripts/check.py` — per `docs/engineering/release-qualification.md`.
- Independent review before PR; autonomous merge only when: scope matches initiative,
  all CI passes, review has no unresolved substantive finding, backward-compat +
  anti-inference controls pass, exact reviewed head == merged head.

## 6. Stop point

None (delegated authority). Proceed to construction after this design is recorded on
the feature branch; no human stop is required unless an escalation trigger is hit
(none identified).
