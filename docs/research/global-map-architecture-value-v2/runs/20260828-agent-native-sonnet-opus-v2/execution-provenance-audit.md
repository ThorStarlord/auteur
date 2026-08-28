# Architecture Value Experiment V2 — Agent-Native Replication — Execution Provenance Audit

**Run ID:** `20260828-agent-native-sonnet-opus-v2`
**Execution base:** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (frozen V2 source revision, PR #143 merge)
**Orchestration branch:** `claude/auteur-architecture-v2-replication-uwlko2`
**Auditor:** the orchestrator itself, mechanically, immediately after each phase (self-audit; no independent human review has occurred yet)

This document supersedes the *method* used by `20260827-muse-spark-v2` (SYNTHETIC / SIMULATED EXECUTION, provenance class C — see that run's own `execution-provenance-audit.md`) with a genuine model-invocation mechanism. It does not use, reproduce, or contradict that run's illustrative pattern.

## 1. Phase 0 — inference backend qualification

Candidate mechanisms inspected: the Claude Code Agent tool (`Agent`, spawns an isolated sub-agent with `model` and `subagent_type` parameters), and no other explicit inference mechanism was available in this session (no direct provider API key/tooling was present; the Agent tool was the only qualified isolated-inference mechanism found).

Properties checked against the frozen requirements (see task instructions §5):

| requirement | finding |
|---|---|
| fresh inference context per invocation | CONFIRMED — canary test below showed zero cross-contamination between two parallel invocations with distinct secret nonces |
| no hidden inheritance of parent's experimental reasoning | CONFIRMED as far as testable — canary agents had no knowledge of each other's nonce or of any prior conversation; each of the 90 subsequent invocations (45 generation + 45 evaluation) was a new `Agent` call with no `to:`/resume parameter |
| exact control over the input supplied to the worker | CONFIRMED, via a stronger mechanism than inlined prompt text: each worker was instructed to make exactly one `Read` call against a single frozen packet file written by the orchestrator before any worker ran; packet content is therefore byte-exact and hash-verifiable, not paraphrased into the prompt |
| no exposure to A/B/C identity for generator workers | CONFIRMED by construction (generator packets contain no condition label) and by leakage audit (`scripts/build_packets.py` packets scanned) |
| no exposure to the evaluator rubric for generator workers | CONFIRMED — generator packets contain only `decision-probes.md`-equivalent content (horizon facts/intent/question/options/generic contract); rubric and hidden must-not-miss/forbidden text never appear in any of the 15 generator packet files |
| exact capture of the returned response | CONFIRMED — each `Agent` tool result was captured verbatim into `raw-outputs/{opaque_id}.md` (generation) or `blind-evaluation/{opaque_id}.json` (evaluation), then SHA-256 hashed |
| distinct invocation, distinguishable from parent prose | CONFIRMED — each `Agent` result carries a distinct `agentId` and `subagent_tokens`/`tool_uses`/`duration_ms` usage block, structurally separate from orchestrator output |
| model identity as far as exposed | The orchestrator supplied `model: "sonnet"` (generator) and `model: "opus"` (evaluator) as explicit parameters on every call; the tool does not additionally echo back a resolved model-version string in its result. This is the limit of what the runtime exposes to the orchestrator — recorded as `RUNTIME-REPORTED` (the request-side parameter), not `PROVIDER-REPORTED` (no response-side confirmation string was returned) |
| stable model selection across required calls | CONFIRMED — `model` parameter was identical (`sonnet`) across all 45 generation calls and identical (`opus`) across all 45 evaluation calls |
| fresh-context / no-carry-over across invocations | CONFIRMED by canary and by the absence of any `to:`/resume parameter in any of the 90 calls |
| tool restriction | PARTIAL / DOCUMENTED LIMITATION — the `Agent` tool schema exposes no explicit tool-allowlist parameter; `general-purpose` sub-agents have full tool access by definition. Isolation was instead enforced by instruction ("use Read exactly once on this path, no other tool") and verified post hoc: every one of the 90 invocation results reported `tool_uses: 1`, meaning no worker used any tool beyond the single instructed `Read` call. This is an instruction-enforced, not sandbox-enforced, restriction — logged as a limitation, not silently assumed |
| invocation metadata sufficient for audit | CONFIRMED — `agentId`, `subagent_tokens`, `tool_uses`, `duration_ms` are present per invocation; raw invocation logs are the tool-call transcript of this orchestration session (not separately exported, since this session's own transcript is the provenance record) |

## 2. Canary (non-experimental) evidence

Two canary sub-agents were spawned in parallel before any experimental packet existed, each given a distinct secret nonce (`CANARY-ALPHA-7f3d9`, `CANARY-BETA-2c8e1`) and told not to use any tool. Results:

- Each agent returned only its own nonce; neither mentioned or leaked the other's nonce — confirms fresh, isolated context.
- `tool_uses: 0` for both — confirms instruction-based tool restriction is followed when no file access is required.
- The two agents were run on different `model` values (`sonnet`, `opus`) and produced stylistically distinct answers, consistent with genuine distinct model invocations rather than templated/deterministic output.
- Distinct `agentId`s (`a639edb4bfdd01ac3`, `a7b59b2e8e6a41cef`) confirm invocation-level distinguishability.

Qualification verdict: **Agent-tool sub-agent spawning is qualified as the isolated inference mechanism for this replication**, with the tool-restriction limitation above disclosed rather than assumed away.

## 3. Selected backends (frozen for this run)

- **Generator:** Agent tool, `subagent_type: general-purpose`, `model: sonnet` (claude-sonnet-5). Frozen for all 45 generation invocations.
- **Evaluator:** Agent tool, `subagent_type: general-purpose`, `model: opus` (claude-opus-5). Frozen for all 45 evaluation invocations. Distinct from the generator model per the frozen preference.

## 4. Known limitations of this mechanism (disclosed, not hidden)

1. **Sampling parameters not controllable.** The Agent tool exposes no `temperature`/`top_p`/`seed`/`max_output_tokens` parameter. The frozen V2 control variables (`temperature 0.2, top_p 1.0, max_output_tokens 1200, tools none`) could not be applied or verified. This is recorded as a material deviation in `post-unblind/invalidation-audit.json`; it is uniform across A/B/C so it is not a between-condition confound, but it does mean the 3 repetitions per cell are not temperature-pinned repeats.
2. **Tool restriction is instruction-enforced, not sandboxed.** No hard mechanism prevents a worker from calling other tools; compliance was verified after the fact via `tool_uses` counts (all 90 invocations showed exactly 1), not guaranteed in advance. A future replication with a stricter no-tools sub-agent type, if one becomes available, would remove this limitation.
3. **No provider-side response ID or token-usage confirmation.** `subagent_tokens` reflects the sub-agent's own context usage, not a provider request/response ID in the sense of a raw HTTP API call. This is disclosed as `RUNTIME-REPORTED`, not `PROVIDER-REPORTED`.
4. **Single orchestration session.** All 90 invocations were issued from one orchestrator session/transcript; that transcript is the provenance record for invocation timing and exact prompts, rather than a separately exported log file.

None of these limitations were treated as blockers per the frozen instruction ("if it fails because context isolation, model stability, output capture, or auditability cannot be established: do not force it") — the properties that matter most (fresh context, no A/B/C exposure to generators, no rubric exposure to generators, exact input control via frozen files, verbatim output capture, distinct model freezing) were all confirmed. The sampling-parameter and tool-sandboxing limitations are real but do not defeat treatment isolation or auditability; they are disclosed so a human reader can weigh them.
