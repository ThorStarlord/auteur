"""Opt-in trusted host port. HTTP never supplies an executable or credentials."""
from pathlib import Path
from typing import Protocol
import threading

from auteur.host_agent import HostAgentRequest
from .persistence import BeginnerConcurrencyError, _FilesystemLock
from .studio_architecture import _digest, _source, project_architecture
from .studio_store import CanvasStore
import json


class StudioArchitectureExecutor(Protocol):
    def enqueue(self, project_root: Path, canvas_id: str, request: HostAgentRequest) -> None:
        """Submit nonblocking work; completion must use complete_architecture."""
        ...


class HostSubmissionError(RuntimeError):
    pass


class StudioHostDispatch:
    """One server's submission ownership; no new persisted story lifecycle."""
    def __init__(self, executor: StudioArchitectureExecutor):
        self.executor = executor
        self._lock = threading.Lock()
        self._submitted: set[tuple[str, str]] = set()

    def submit(self, store: CanvasStore, request_sha256: str) -> dict:
        with self._lock, _FilesystemLock(store._path('.canvas.lock')):
            projection = project_architecture(store)
            packet = projection.get('request')
            if (projection['status'] != 'awaiting_host_agent' or not packet
                    or packet['request_sha256'] != request_sha256):
                raise BeginnerConcurrencyError('No matching pending architecture request; prepare again')
            request = HostAgentRequest(**packet)
            previous = json.loads(request.user)['working_context']['previous_candidate']
            if _digest(_source(store, previous=previous)) != request.settings['source_sha256']:
                raise BeginnerConcurrencyError('Story Vision or working context changed; prepare again')
            key = (store.canvas_id, request.request_sha256)
            if key not in self._submitted:
                try:
                    self.executor.enqueue(store.project_root, store.canvas_id, request)
                except RuntimeError as error:
                    raise HostSubmissionError('Host executor could not submit this request') from error
                self._submitted.add(key)
        return {'request_sha256': request.request_sha256, 'state': 'submitted'}
