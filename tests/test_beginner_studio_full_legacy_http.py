"""Full Architecture's real HTTP evidence source is read-only and source-bound."""
from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import urlopen

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_store import CanvasStore


def test_missing_architecture_returns_empty_evidence_without_accepted_sources(tmp_path):
    canvas=CanvasStore(tmp_path,"fullsource")
    canvas.create()
    before=canvas.load().model_dump(mode="json")
    server=BeginnerWorkspaceServer(tmp_path,port=0)
    thread=server.start_in_thread()
    try:
        url=f"http://127.0.0.1:{server.port}/api/beginner/studio/canvases/fullsource/architecture/full-evidence"
        with urlopen(url,timeout=8) as result:
            assert result.status==200
            payload=json.load(result)
        assert payload["canvas_id"]=="fullsource"
        assert payload["candidate_request_sha256"] is None
        assert payload["legacyEvidence"]==[]
        assert payload["genreEvidence"]==[]
        assert payload["acceptedIdentity"] is None
        assert payload["acceptedStructure"] is None
        assert canvas.load().model_dump(mode="json")==before
    finally:
        server.stop()
        thread.join(timeout=3)
        assert not thread.is_alive()


def test_unknown_canvas_does_not_expose_genre_or_accepted_sources(tmp_path):
    server=BeginnerWorkspaceServer(tmp_path,port=0)
    thread=server.start_in_thread()
    try:
        url=f"http://127.0.0.1:{server.port}/api/beginner/studio/canvases/nonexistent/architecture/full-evidence"
        try:
            urlopen(url,timeout=8)
            assert False,"Unknown canvas returned evidence"
        except HTTPError as error:
            assert error.code==404
    finally:
        server.stop()
        thread.join(timeout=3)
