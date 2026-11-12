"""Integration boundaries for optional, read-only Studio architecture review."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from urllib.request import urlopen

import pytest

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


EVIDENCE = Path(__file__).resolve().parents[1] / "docs/qualification-evidence/agent-first-ontology-20261103"


#: The Story Vision that produced the recorded candidate. Its author_declared emotion labels
#: (wonder, dread, hope) must be named by the author's own text in the store, as the bridge requires.
RICH_VISION = (
    "A coastal city lives on maps drawn by the Cartographers Guild. Every accurate map erases one memory "
    "from the person who supplied the survey. A young surveyor discovers that the Guild is using the city "
    "founding archive to make a perfect map that will erase the shared memory of a massacre. She must "
    "choose between a truthful map that frees the city from a comforting lie and a merciful map that "
    "preserves belonging. Intended experience: wonder at the strangeness of the coast, mounting dread as "
    "the cost becomes personal, and earned hope about chosen remembrance. Genre: a literary mystery with "
    "fantasy and horror passages. No explicit violence on the page; the tone is intimate and reflective, "
    "not grimdark. Themes: memory, complicity, and the ethics of knowledge."
)


def _store(tmp_path):
    store = CanvasStore(tmp_path, "visual-review")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {"id": "story-vision", "kind": "note",
                          "title": "Story Vision", "content": RICH_VISION},
                 "position": {"x": 20, "y": 50}},
    )
    return store


def _complete(store, candidate, instruction=""):
    status = prepare_architecture(store, instruction)
    request = HostAgentRequest(**status["request"])
    response = build_host_agent_response(request, json.dumps(candidate), runtime="integration-test").model_dump()
    return complete_architecture(store, response)


def test_visual_review_uses_existing_before_and_after_without_applying(tmp_path):
    store = _store(tmp_path)
    before = json.loads((EVIDENCE / "rich-vision-candidate.json").read_text(encoding="utf-8"))
    current = _complete(store, before)
    after = copy.deepcopy(before)
    engine = next(node for node in after["nodes"] if node["id"] == "memory_economy")
    engine["summary"] = "Discovery creates both wonder and personal loss."
    pending = _complete(store, after, "Increase wonder while preserving loss.")
    assert pending["status"] == "review_ready"
    assert pending["candidate"] == current["candidate"]
    assert next(node for node in pending["review"]["candidate"]["nodes"] if node["id"] == "memory_economy")["summary"] == engine["summary"]
    assert pending["review"]["prior_request_sha256"] == current["candidate_request_sha256"]
    assert not (tmp_path / "story_identity.yaml").exists()
    applied = apply_architecture_review(store, pending["review"]["request_sha256"])
    assert next(node for node in applied["candidate"]["nodes"] if node["id"] == "memory_economy")["summary"] == engine["summary"]
    assert not (tmp_path / "story_identity.yaml").exists()


def test_old_review_cannot_apply_after_another_revision(tmp_path):
    store = _store(tmp_path)
    before = json.loads((EVIDENCE / "rich-vision-candidate.json").read_text(encoding="utf-8"))
    _complete(store, before)
    pending = _complete(store, copy.deepcopy(before), "Propose a revision without changing meaning.")
    assert pending["status"] == "review_ready"
    newer = prepare_architecture(store, "A different subsequent revision request.")
    assert newer["status"] == "awaiting_host_agent"
    with pytest.raises(BeginnerConcurrencyError):
        apply_architecture_review(store, pending["review"]["request_sha256"])


def test_optional_revision_browser_assets_are_served(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        for path in (
            "/studio_architecture_revision_compare.mjs",
            "/studio_architecture_revision_view.mjs",
            "/studio_architecture_revision_bridge.js",
            "/studio_architecture_revision.css",
        ):
            with urlopen(f"http://127.0.0.1:{server.port}{path}", timeout=5) as response:
                assert response.status == 200, path
                assert response.read(), path
        with urlopen(f"http://127.0.0.1:{server.port}/studio.html", timeout=5) as response:
            html = response.read().decode("utf-8")
            assert 'id="architecture-visual-review"' in html
            assert "/studio_architecture_revision_bridge.js" in html
    finally:
        server.stop()
        thread.join(timeout=3)
        assert not thread.is_alive()