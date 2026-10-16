"""Opt-in trusted host port. HTTP never supplies an executable or credentials."""
from pathlib import Path
from typing import Protocol

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


def dispatch_architecture(store: CanvasStore, request_sha256: str,
                          executor: StudioArchitectureExecutor) -> dict:
    with _FilesystemLock(store._path('.canvas.lock')):
        projection = project_architecture(store)
        packet = projection.get('request')
        if (projection['status'] != 'awaiting_host_agent' or not packet
                or packet['request_sha256'] != request_sha256):
            raise BeginnerConcurrencyError('No matching pending architecture request; prepare again')
        request = HostAgentRequest(**packet)
        previous = json.loads(request.user)['working_context']['previous_candidate']
        if _digest(_source(store, previous=previous)) != request.settings['source_sha256']:
            raise BeginnerConcurrencyError('Story Vision or working context changed; prepare again')
        try:
            executor.enqueue(store.project_root, store.canvas_id, request)
        except RuntimeError as error:
            raise HostSubmissionError('Host executor could not submit this request') from error
    return {'request_sha256': request.request_sha256, 'state': 'submitted'}
