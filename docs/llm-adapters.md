# Generation Backends and LLM Adapters

Auteur's product boundary is **backend-agnostic generation**, not a particular
LLM provider. ADR 022 makes the active host coding agent the preferred backend
when Auteur is already running inside a capable coding-agent environment.

Engine v1 currently implements direct model calls through the provider-agnostic
`LLMClient` interface. Those adapters remain supported for standalone/headless
execution and compatibility, but they are no longer the intended product
identity.

## Protocol

`src/auteur/llm/__init__.py` defines:

```python
class LLMRequest(BaseModel):
    system: str
    user: str
    max_tokens: int
    temperature: float
    model: str | None = None


class LLMResponse(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int


class LLMClient(Protocol):
    def complete(self, req: LLMRequest) -> LLMResponse: ...
```

The current pipeline depends only on `LLMClient`. Provider-specific SDK code
stays outside the pipeline. During ADR-022 migration, the same principle extends
to a broader generation-capability boundary so product workflows do not need to
know whether a response came from the active coding agent, a direct provider, or
a deterministic test/replay backend.

## Active Coding-Agent Backend

When Auteur is invoked from a capable coding agent, the preferred execution path
is:

```text
Auteur builds a bounded generation request
-> active host coding agent fulfills the request with its current model/session
-> response returns through a structured handoff
-> Auteur validates, records provenance, and continues
```

This is deliberately **host-mediated**, not vendor-detected. Auteur must not
reach into Claude Code, Codex, ChatGPT, Cursor, OpenCode, or another agent's
private session protocol. A coding-agent integration may wrap the CLI, exchange
request/response artifacts, use stdin/stdout, or provide another neutral bridge,
but core product semantics cannot depend on one agent vendor.

Rules:

- do not require a second provider API key when the active host agent can supply
  the needed generation capability;
- do not silently switch from the host agent to a paid provider backend;
- direct provider execution is an explicit standalone/compatibility choice;
- record backend/runtime/model identity when observable and `UNAVAILABLE` when
  it is not;
- preserve the exact request and returned output when evidence or replay matters;
- all author-acceptance and canonical-mutation rules remain unchanged.

## Built-In Providers

Anthropic:

```powershell
python -m pip install -e ".[anthropic]"
$env:ANTHROPIC_API_KEY = "sk-ant-..."
auteur draft .\tmp\shattered_crown 1 --provider anthropic
```

The current default model in code is `claude-sonnet-4-6`.

OpenAI:

```powershell
python -m pip install -e ".[openai]"
$env:OPENAI_API_KEY = "sk-..."
auteur draft .\tmp\shattered_crown 1 --provider openai --model gpt-4o
```

The current default model in code is `gpt-4o`.

## Token Accounting

`PipelineRunner` wraps the selected client with a counting client. The returned `DraftResult` includes:

- `total_input_tokens`
- `total_output_tokens`

These are summed across Cartographer, Bard, and critic calls. They are token counts, not cost estimates.

## Test Client

`FakeClient` replays scripted `LLMResponse` objects. Tests use it to exercise the engine without network calls or token spend.

## Adding A Provider

To add a provider:

1. Create `src/auteur/llm/<provider>.py`.
2. Implement a class with `complete(self, req: LLMRequest) -> LLMResponse`.
3. Translate `req.system`, `req.user`, `req.temperature`, `req.max_tokens`, and `req.model` into that provider's SDK call.
4. Return response text and token counts.
5. Add a CLI branch in `_build_client()`.
6. Add an optional dependency in `pyproject.toml`.
7. Add tests using `FakeClient` where possible; avoid network calls in pytest.

## Current Limitations

- The ADR-022 host-agent handoff is not yet integrated across production
  generation paths on `main`. Draft PR #327 contains a bounded Quick Draft
  host-agent candidate; broader production paths still use direct adapters.
- Provider is selected for the whole draft run, not per agent.
- No automatic fallback provider.
- No retry/backoff wrapper for transient API failures.
- No currency cost model.

