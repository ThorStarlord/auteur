# Implementation Design — A2: surface F3 elicitation availability in `decision view`

> Phase: implementation design. Mechanism **M1 — elicitation-availability hint in
> `decision view`**, agent-selected under the standing delegated-authority envelope
> (`docs/engineering/delegated-authority.md`; A2 selected by the human 2026-08-13).
> Discovery evidence @ `030e190` on `discovery/f3-elicitation`. Base SHA: 2ee0081
> (origin/main, PR #69 + #70 merged). Reuse/extension of shipped F3 behavior; no
> escalation triggers. Production source read-only until construction begins.

## 0. Design hypothesis (binding)

The author inspects a decision artifact with `decision view`. When the decision is
genuinely unsettled (no `goal_significance`) and composed consequences exist, the view
currently prints `Goal significance (authored, decision-scoped): None` but gives no
indication that F3 `decision elicit` exists, what it does, or how to invoke it. M1
surfaces that capability at the moment of inspection — nothing more, no new semantics.

## 1. Mechanism (binding): elicitation state in `handle_view`

### 1.1 Eligibility state (deterministic, from the resolved report + F1 field)

Computed ONLY when `--identity` and `--blueprint` are given (i.e., when the resolved
report — and thus the composed `combinations` — is available). Without them, no
elicitation section is rendered (authored-only view stays as-is).

| State | Condition | Render |
|---|---|---|
| `unsettled` | `goal_significance is None` AND report has composed combinations | Text hint + JSON `state: unsettled` + `command` |
| `no_composed_consequences` | `goal_significance is None` AND no combinations | Honest note "no composed consequences to elicit against" (mirrors the elicit render) + JSON `state` |
| `declared` | `goal_significance` present | Text: no extra hint (F1 field line already shows it); JSON `state: declared` |

### 1.2 Text render (non-JSON)

After the existing `Goal significance (authored, decision-scoped): ...` line:

```
Elicitation (F3): available — examine the concrete tradeoff:
  auteur decision elicit <id> --identity <identity> --blueprint <blueprint> --project <project>
```

- `unsettled` → the hint above with the exact invocation (actual paths as passed).
- `no_composed_consequences` → `Elicitation (F3): not applicable — no composed consequences yet (an authored combination_direction is required to compose them).`
- `declared` → no additional line (the significance line already communicates it; F1 is the destination).

### 1.3 JSON render

Add to the `authored` object:

```json
"elicitation": {
  "state": "unsettled|no_composed_consequences|declared",
  "command": "auteur decision elicit <id> --identity ... --blueprint ..."  // unsettled only
}
```

`command` present iff `state == "unsettled"`. The `declared` state omits `command`.

## 2. Binding behavior (from the envelope + F3 semantics)

1. Surfacing only: no new schema, no new state, no change to `elicit`'s behavior.
2. The hint never ranks, never recommends, never infers from prose — it states
   availability and the invocation, exactly as the F3 interaction demonstrated.
3. `unsettled` is never conflated with `unranked` (intentional non-precedence):
   `unranked` is a declared state → `declared`, no hint.
4. Directionless one_of (no composed consequences) is honest: "not applicable",
   matching the `elicit` render's own honest surface.
5. Backward compatible: `view` output for settled/absent-without-resolution cases is
   unchanged (no elicitation section when `--identity/--blueprint` absent).

## 3. Controls and golden discriminators (binding for qualification)

1. **Unsettled + composed** (`case-goal-significance/absent.yaml` with identity+blueprint):
   text shows the `Elicitation (F3): available` hint + exact invocation; JSON has
   `state: unsettled` and a `command`.
2. **Unranked (declared)** (`unranked.yaml`): no elicitation hint in text; JSON
   `state: declared`, no `command`.
3. **Ordered (declared)** (`ordered-ab.yaml`): same as control 2.
4. **Directionless one_of** (`case-one-of/one-of-directionless.yaml`): text shows the
   honest "not applicable — no composed consequences" note; JSON `state:
   no_composed_consequences`.
5. **No identity/blueprint** (`view` without resolution): no elicitation section —
   authored-only output unchanged (regression).
6. **JSON determinism**: `state` values are from the closed set; `command` present iff
   unsettled.
7. **Anti-inference**: unsettled prose (`unsettled-prose.yaml`) vs `absent.yaml` — both
   `unsettled`; the hint text is identical (prose never parsed).
8. **Existing goldens**: `view` tests in the author-decisions suite unchanged for
   declared/absent-without-resolution cases.

## 4. Out of scope (binding)

Workspace-surface integration (status/list/inspect — rejected in discovery M2); new
aggregate command (M3); any change to `elicit` behavior; F4; weights/ranking/LLM/
ontology/3+ goals/prose inference; proposal artifact flow.

## 5. Verification plan

- TDD: RED tests first (controls 1–8); run the full author-decisions view tests for
  regression.
- Full verification stack on the merge path: pytest (categories separately), ruff,
  `scripts/check.py`.
- Independent review; autonomous merge when scope matches, CI passes, review has no
  unresolved substantive finding, backward-compat + anti-inference controls pass,
  exact reviewed head == merged head.

## 6. Stop point

None (delegated authority). Proceed to construction after this design is recorded on the
feature branch; no human stop unless an escalation trigger is hit (none identified).
