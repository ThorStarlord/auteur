"""_CountingClient — LLMClient wrapper that tracks token consumption."""

from __future__ import annotations

from threading import Lock

from auteur.llm import LLMClient, LLMRequest, LLMResponse


class _CountingClient:
    """LLMClient wrapper that counts input/output tokens across calls.

    Attaches to PipelineRunner for per-draft token accounting.
    """

    def __init__(self, inner: LLMClient):
        self._inner = inner
        self._lock = Lock()
        self.input_tokens = 0
        self.output_tokens = 0

    def complete(self, req: LLMRequest) -> LLMResponse:
        resp = self._inner.complete(req)
        with self._lock:
            self.input_tokens += resp.input_tokens
            self.output_tokens += resp.output_tokens
        return resp
