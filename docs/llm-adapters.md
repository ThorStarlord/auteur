# LLM Adapters

Auteur uses a provider-agnostic LLM interface internally. This is independent from how a user invokes Auteur.

A user may run the CLI directly, ask a coding agent to run the CLI, or later call a web API. In all cases, Engine v1 calls LLMs through the same adapter interface.

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

The pipeline depends only on `LLMClient`. Provider-specific SDK code stays outside the pipeline.

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

- Provider is selected for the whole draft run, not per agent.
- No automatic fallback provider.
- No retry/backoff wrapper for transient API failures.
- No currency cost model.

