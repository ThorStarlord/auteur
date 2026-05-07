"""FakeClient — replays scripted LLMResponse objects for tests."""

from __future__ import annotations

from auteur.llm import LLMRequest, LLMResponse


class FakeClient:
    def __init__(self, scripted: list[LLMResponse]):
        self._queue: list[LLMResponse] = list(scripted)
        self.calls: list[LLMRequest] = []

    def complete(self, req: LLMRequest) -> LLMResponse:
        self.calls.append(req)
        if not self._queue:
            raise RuntimeError(
                f"FakeClient exhausted after {len(self.calls)} calls; "
                "no more scripted responses."
            )
        return self._queue.pop(0)
