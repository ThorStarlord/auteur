# V1 LLM Provider Failure Contract

Anthropic and OpenAI remain optional production adapters over the same Auteur `LLMClient` contract. V1 normalizes operational failures so workflows do not need to branch on provider SDK exception classes.

| Category | Code | Retry | Canonical mutation permitted because of failure? | Safe action |
| --- | --- | --- | --- | --- |
| credential absent | `auth_missing` | no | no | supply the provider credential |
| credential rejected / forbidden | `auth_invalid` | no | no | replace/fix credential or access |
| rate limited | `rate_limited` | yes | no | retry within configured budget; report exhaustion |
| timeout | `timeout` | yes | no | retry within configured budget |
| connection/network failure | `connection_failure` | yes | no | retry within configured budget |
| provider 5xx/unavailable | `provider_5xx` | yes | no | retry within configured budget |
| malformed provider response | `malformed_response` | no | no | preserve prior state and surface provider response failure |
| consuming workflow schema rejection | `structured_output_invalid` | workflow-specific bounded repair/retry | no | repair/regenerate candidate; never promote invalid structure |
| retry budget exhausted | `retry_exhausted` | no automatic retry at this layer | no | surface the final normalized cause and let the author retry later |
| user interruption | `user_interrupted` | no automatic retry | no | leave accepted state unchanged; preserve durable candidates already completed |
| unknown provider transport failure | `provider_error` | yes for backward-compatible V1 transport behavior | no | exhaust bounded retries, then report failure |

`RetryExhaustedError` remains a `RetriableError` subclass for compatibility with existing callers while exposing the stable `retry_exhausted` code and original normalized cause.

## Claim boundary

This contract qualifies operational behavior, not creative quality. A live-provider release smoke proves that an adapter can authenticate, execute a bounded request, return a valid Auteur response, and fail safely; it does not prove that the provider writes good fiction.
