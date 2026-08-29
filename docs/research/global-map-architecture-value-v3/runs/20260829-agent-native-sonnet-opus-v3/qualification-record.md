# V3 Run 20260829-agent-native-sonnet-opus-v3 — Backend Qualification Record

Per execution-contract.md §3 + §8. Recorded BEFORE any experimental probe call.

## Backend / interface (both roles)

- backend/runtime: Claude Code `Agent` tool
- inference interface: sub-agent spawn (`subagent_type: general-purpose`, `run_in_background: false`)
- packet delivery mechanism: direct prompt (content inlined in the spawn `prompt` field — no `Read` tool required; matches §4.A "direct prompt" option)
- tool/capability policy: sub-agent restricted by explicit prompt instruction to answer only from the delivered packet content, no other tool use; audited per invocation via reported tool_uses
- fresh-context mechanism: each invocation is a new `Agent` call with no `to:`/resume parameter — per the Agent tool's own description, "Each spawn starts cold and re-derives context you already have"

## A. RUNTIME / BACKEND CONTRACT EVIDENCE (documentation-derived, not from observing one run)

1. **Fresh context per spawn:** documented in the Agent tool's own description: "Each spawn starts cold." No resume/continuation parameter was used for any generator or evaluator invocation in this run — this is a structural absence of the resume capability, not merely an instruction not to use it.
2. **No inheritance of another worker's conversation:** each `Agent` invocation is an independent tool call with its own `prompt` field; the harness's own documentation states agents "start cold" with no shared state between separate spawns (distinct from resuming a named agent via `to:`, which was never used).
3. **Startup context — CLAUDE.md is loaded, content directly audited:** this repository's `/home/user/auteur/CLAUDE.md` ("Auteur Development Guidelines") is standard Claude Code repository-instruction scaffolding, loaded for every sub-agent operating in this repository regardless of task. Its full text was directly grepped for any reference to this experiment (`architecture value`, `global map`, `V1`/`V2`/`V3`, probe IDs `P01`-`P05`, `golden ledger`, `archive of lies`, and specific fixture facts `monastery`/`falsifier`) — **zero matches**. CLAUDE.md is therefore confirmed, by direct content audit (not inference), to be: (a) stable/identical across every generator and evaluator invocation in this run (it is a single static repository file, unmodified during the run); (b) not treatment-specific (identical regardless of A/B/C); (c) free of this experiment's outcomes, evaluator secrets, expected winner, or condition mapping.
4. **Remaining startup-context component (base agent system prompt, tool schema definitions):** not independently inspectable by the orchestrator, but documented as standardized per-subagent-type scaffolding (`general-purpose` agent description: "General-purpose agent for researching complex questions... Tools: *") identical for every `general-purpose` spawn regardless of the prompt content given to it — this is generic runtime scaffolding, not repository- or experiment-specific, and cannot plausibly vary by A/B/C treatment or encode this experiment's mapping/outcome/rubric secrets since it is fixed independent of the calling prompt.
5. **Tool-use auditability:** the Agent tool result reports the tools the sub-agent actually used; this is a structural feature of the harness, not a per-invocation claim.

## Startup-context classification (per §3 strict table)

**PARTIALLY OBSERVABLE.** Basis: the CLAUDE.md component of startup context is directly known and audited (item 3 above, equivalent to KNOWN for that component). The unobserved remainder (base system prompt, tool schema definitions) is established by runtime/backend contract evidence (item 4) to be standardized, invocation-generic scaffolding — not repository- or experiment-specific — and therefore cannot plausibly contain treatment/outcome/evaluator/mapping material. Per §3's strict table, this satisfies the `PARTIALLY OBSERVABLE` → acceptable condition ("the observable runtime contract or backend documentation is sufficient to establish that the unobserved remainder is standardized, generic runtime scaffolding... This determination and its basis must be recorded, not assumed" — recorded here).

This is a genuine tightening relative to PR #147, which recorded this as bare `UNAVAILABLE` without auditing CLAUDE.md content or citing the Agent tool's own "starts cold" documentation.

## B. EMPIRICAL CANARY EVIDENCE (executed)

Two fresh, parallel, distinct-nonce, non-experimental canary invocations. No Archive of Lies content, no probe content, no rubric, no A/B/C treatment content, no expected winner.

| worker | requested model alias | nonce sent | nonce echoed | tool_uses | duration_ms | raw artifact | sha256 |
|---|---|---|---|---|---|---|---|
| alpha | `sonnet` | `CANARY-ALPHA-7f3e9c` | `CANARY-ALPHA-7f3e9c` (exact match) | 0 | 2029 | `canary/alpha.raw.txt` | `6fbe60ce9fbd3ce9bcfc7310581ce2bc17ce7ca6119efc3bfe7abe77d868cc1b` |
| beta | `opus` | `CANARY-BETA-4d1a82` | `CANARY-BETA-4d1a82` (exact match) | 0 | 2120 | `canary/beta.raw.txt` | `795986db88eec6352faaec103798d7ec15d327eaa4a1c61ff245da31cf4b48fd` |

Findings:
- **No cross-worker contamination:** each worker echoed only its own nonce; neither response contains the other worker's nonce or any content from the other invocation.
- **Fresh-worker behavior:** both workers stated (in their own words, not scripted) they have no memory of any other conversation/worker/prior instruction — consistent with, not proof beyond, the category-A "starts cold" documentation.
- **Tool-use observability:** `tool_uses: 0` recorded for both, confirming the harness reports actual tool use per invocation and that neither worker used a tool when none was authorized.
- **Requested-model-identifier recording mechanics:** both `sonnet` and `opus` requested aliases were accepted and produced a response (`resolved_model_identifier` remains `UNAVAILABLE`/`PROVIDER-REPORTED` not observable — no change from PR #147's backend limitation on this point, see qualification decision below).
- **Raw-output capture mechanics:** exact raw response captured and hashed for both, before any parsing.
- **Packet delivery mechanics:** direct-prompt delivery (§4.A) worked as preregistered for both roles.

## Qualification decision (per §3 + §8, both roles)

| field | GENERATOR (sonnet) | EVALUATOR (opus) |
|---|---|---|
| `runtime_contract_evidence_refs` | category A items 1-5 above | category A items 1-5 above (same backend/runtime for both roles) |
| `runtime_contract_qualification` | PASS | PASS |
| `empirical_canary_evidence_refs` | `canary/alpha.raw.txt` (sha256 above) | `canary/beta.raw.txt` (sha256 above) |
| `empirical_canary_result` | PASS (observable checks only, per §8) | PASS (observable checks only, per §8) |
| `startup_context_classification` | PARTIALLY OBSERVABLE (basis recorded above) | PARTIALLY OBSERVABLE (basis recorded above) |
| `resolved_model_identifier` / `resolved_model_version` | UNAVAILABLE / UNAVAILABLE (backend does not expose; same limitation as PR #147, honestly disclosed per §2, not laundered) | UNAVAILABLE / UNAVAILABLE |
| `temperature`/`top_p`/`seed`/`max_output_tokens` | UNAVAILABLE (not exposed by this backend) | UNAVAILABLE |
| `backend_qualification_result` | **PASS** — every §3 hard requirement (fresh context, no resume, no cross-worker inheritance, no orchestrator-hidden-reasoning inheritance) has sufficient evidence under the combination of §8.A (documented "starts cold" + audited CLAUDE.md content + standardized subagent-type scaffolding) and §8.B (empirical canary showing no cross-nonce leakage, 0 unauthorized tool use) | **PASS** — same basis |
| `strict_v3_conformance_status` | **ELIGIBLE** | **ELIGIBLE** |

Per §9, the preferred requested aliases `sonnet` (generator) and `opus` (evaluator) are both available on this backend at qualification time — no substitution required.

**Both roles are ELIGIBLE. Proceeding to run configuration freeze and experimental execution.**
