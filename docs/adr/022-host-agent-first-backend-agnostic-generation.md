# ADR 022: Host-Agent-First, Backend-Agnostic Generation

**Status:** Accepted  
**Date:** 2026-10-05

## Context

Auteur is frequently developed and operated from capable coding-agent
environments. Requiring Auteur to configure a second OpenAI, Anthropic, or other
provider API inside that environment duplicates model access, credentials,
billing, and failure modes even though a capable model is already executing the
workflow.

At the same time, tying Auteur directly to one coding-agent product would create
a different form of lock-in. A child CLI process also cannot assume its parent
agent exposes a callable SDK or private session API.

The durable boundary therefore needs to describe a capability, not a vendor.

## Decision

Auteur is **host-agent-first and backend-agnostic** for nondeterministic
generation/reasoning.

When Auteur runs inside a capable coding-agent environment, the active host
coding agent is the preferred generation backend. Auteur should not require a
separate provider credential merely to access a model capability the current
host agent can already supply.

The portable integration contract is a bounded request/response handoff:

```text
Auteur deterministic core
-> exact generation/reasoning request
-> active host coding agent
-> structured response
-> Auteur validation / provenance / existing authority owner
```

The handoff may be implemented through CLI orchestration, request/response
artifacts, stdin/stdout, or another neutral bridge. Core product behavior must
not depend on a private Claude Code, Codex, ChatGPT, Cursor, OpenCode, or other
vendor-specific session protocol.

Direct provider adapters remain supported as explicit standalone,
headless/automation, compatibility, and research backends. They are not removed
and do not become the product identity.

## Invariants

- Deterministic Auteur code continues to own canonical state, persistence,
  validation, provenance, and authority boundaries.
- Host-agent output is working/generated evidence until existing owners accept or
  promote it; using a coding agent grants no additional canonical authority.
- No author-facing feature may require a particular coding-agent vendor.
- No author-facing feature may require a second provider API key when the active
  host agent can satisfy the same capability through the neutral handoff.
- Backend changes are explicit. Auteur must not silently fall back from a host
  agent to a paid provider.
- Backend/runtime/model identity is recorded when observable. If the host does
  not expose model identity, record `UNAVAILABLE` rather than guessing.
- Exact requests and outputs are preserved when required for evaluation,
  replay, or evidence.
- For asynchronous generation against mutable story state, request/response
  identity is necessary but not sufficient. The request must also bind to the
  decision-relevant source-state fingerprint from which it was derived; a valid
  response to a now-stale request must fail closed before entering current
  Working state.
- Deterministic fake/replay implementations remain valid test backends.
- Existing author-acceptance and no-silent-mutation contracts are unchanged.

## Asynchronous freshness

Host-agent handoff creates two separate validity questions:

```text
Does this response belong to this exact request?
!=
Does this request still describe the current story state?
```

The first question is answered by request/response identity and request
fingerprints. The second is answered by a source-state fingerprint over the
decision-relevant mutable inputs used to construct the request.

For long-running operations, Auteur must re-evaluate that source-state
fingerprint before applying the returned result. If current planning, accepted
history, accepted Expression/state, or other decision-relevant upstream evidence
has changed, the old response remains valid evidence for the old request but is
**stale for the current Book**. It must not silently become the current Working
draft.

This keeps asynchronous intelligence subordinate to Auteur's existing
freshness, provenance, and author-authority boundaries rather than creating a
second authority model.

## Current implementation status

This ADR selects the target boundary; it does not claim the migration is
complete.

Current `main` generation primarily uses the provider-agnostic `LLMClient`
protocol with direct Anthropic/OpenAI adapters. Draft PR #327 contains a bounded
neutral host-agent request/response implementation for Quick Draft, but it is
not yet integrated into `main`; broader production generation paths therefore
remain on direct adapters. Continued migration should retain `LLMClient` as an
explicit standalone backend.

## Evidence implication

Product dogfood should test the execution path users are expected to rely on.

Therefore a direct-provider Quick Draft run can establish provider-adapter
compatibility, but once the host-agent path exists it is not sufficient by
itself to qualify the intended default product runtime. Live Quick Draft
evidence should preferentially exercise the active coding-agent backend and
record the host/runtime/model identity to the extent observable.
