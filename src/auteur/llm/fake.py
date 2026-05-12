"""FakeClient — replays scripted responses and exceptions for tests.

Items in the scripted list can be:
- LLMResponse: returned as-is.
- Exception: raised (used to simulate RetriableError for retry tests).
"""

from __future__ import annotations

from typing import Any

from auteur.llm import LLMRequest, LLMResponse


class FakeClient:
    def __init__(self, scripted: list[Any]):
        self._queue: list[Any] = list(scripted)
        self.calls: list[LLMRequest] = []

    def complete(self, req: LLMRequest) -> LLMResponse:
        self.calls.append(req)
        if not self._queue:
            raise RuntimeError(
                f"FakeClient exhausted after {len(self.calls)} calls; "
                "no more scripted responses."
            )
        item = self._queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item
