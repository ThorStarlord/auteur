from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import auteur.beginner.chapter_generation as generation
from auteur.host_agent import build_host_agent_response, load_host_agent_request
from auteur.identity import HighLevelCentralEngine, StoryIdentity, compile_to_blueprint
from auteur.project import Project


def project(tmp_path: Path) -> Path:
    identity = StoryIdentity(
        title="The Glass Archive",
        core_answer="Truth survives only when uncertainty is preserved honestly.",
        central_engine=HighLevelCentralEngine(
            want="preserve the archive and its history",
            resistance="damaged trust and uncertain provenance",
            conflict="institutional stability conflicts with honest disclosure",
            stakes="the archive may preserve a manufactured history",
            change="choose transparent uncertainty over a clean official story",
        ),
    )
    root = tmp_path / "book"
    Project.init(root, compile_to_blueprint(identity))
    chapter = root / "chapters" / "06"
    chapter.mkdir(parents=True, exist_ok=True)
    (chapter / "outline.yaml").write_text(
        "chapter_index: 6\nchapter_summary: Resolve the archive\n"
        "scenes:\n  - scene_id: s6\n    summary: Mara decides what to disclose\n",
        encoding="utf-8",
    )
    return root


def install_context(monkeypatch, state: dict[str, str]) -> None:
    def contextual_plan(project_root: Path, chapter_index: int):
        return SimpleNamespace(
            draft_handoff_ready=True,
            context={
                "author_context": {
                    "accepted_history": [{"chapter_index": chapter_index - 1}],
                    "token": state["token"],
                }
            },
        )

    monkeypatch.setattr(generation, "build_contextual_chapter_plan", contextual_plan)


def test_prepare_binds_context_without_writing_draft(tmp_path, monkeypatch):
    root = project(tmp_path)
    state = {"token": "A"}
    install_context(monkeypatch, state)
    prepared = generation.prepare_chapter_generation(root, 6, command_id="cmd-a")
    assert not (root / "chapters" / "06" / "draft_v1.md").exists()
    request = load_host_agent_request(prepared.request_path)
    assert '"token": "A"' in request.user
    receipt = json.loads(prepared.receipt_path.read_text())
    assert receipt["status"] == "awaiting_host_agent"
    assert receipt["source_fingerprint"] == prepared.source_fingerprint


def test_completion_writes_working_only_and_preserves_unknown_latency(tmp_path, monkeypatch):
    root = project(tmp_path)
    state = {"token": "A"}
    install_context(monkeypatch, state)
    prepared = generation.prepare_chapter_generation(root, 6, command_id="cmd")
    request = load_host_agent_request(prepared.request_path)
    response = build_host_agent_response(
        request,
        "# Chapter 6\n\nMara opens the ledger.",
        runtime="ChatGPT",
        model="GPT-5.6 Sol",
    )
    result = generation.complete_chapter_generation(
        root,
        6,
        command_id="cmd",
        response_payload=response,
    )
    assert result.draft_path.name == "draft_v1.md"
    assert result.elapsed_seconds is None
    metadata = json.loads(result.metadata_path.read_text())
    assert metadata["status"] == "working"
    assert "generation_elapsed_seconds" not in metadata
    assert not (root / "chapters" / "06" / "final.md").exists()


def test_changed_context_rejects_old_response_before_writing(tmp_path, monkeypatch):
    root = project(tmp_path)
    state = {"token": "A"}
    install_context(monkeypatch, state)
    prepared = generation.prepare_chapter_generation(root, 6, command_id="cmd")
    response = build_host_agent_response(
        load_host_agent_request(prepared.request_path),
        "Old response",
    )
    state["token"] = "B"
    with pytest.raises(ValueError, match="stale"):
        generation.complete_chapter_generation(
            root,
            6,
            command_id="cmd",
            response_payload=response,
        )
    assert not (root / "chapters" / "06" / "draft_v1.md").exists()


def test_cross_request_response_rejected(tmp_path, monkeypatch):
    root = project(tmp_path)
    state = {"token": "A"}
    install_context(monkeypatch, state)
    first = generation.prepare_chapter_generation(root, 6, command_id="one")
    second = generation.prepare_chapter_generation(root, 6, command_id="two")
    wrong = build_host_agent_response(
        load_host_agent_request(second.request_path),
        "Wrong candidate",
    )
    with pytest.raises(ValueError, match="different request|different candidate|fingerprint"):
        generation.complete_chapter_generation(
            root,
            6,
            command_id="one",
            response_payload=wrong,
        )
    assert not (root / "chapters" / "06" / "draft_v1.md").exists()


def test_exact_replay_idempotent_but_different_second_response_rejected(tmp_path, monkeypatch):
    root = project(tmp_path)
    state = {"token": "A"}
    install_context(monkeypatch, state)
    prepared = generation.prepare_chapter_generation(root, 6, command_id="cmd")
    request = load_host_agent_request(prepared.request_path)
    response = build_host_agent_response(request, "Stable response")
    first = generation.complete_chapter_generation(
        root,
        6,
        command_id="cmd",
        response_payload=response,
    )
    second = generation.complete_chapter_generation(
        root,
        6,
        command_id="cmd",
        response_payload=response,
    )
    assert first.candidate_sha256 == second.candidate_sha256
    with pytest.raises(ValueError, match="different response"):
        generation.complete_chapter_generation(
            root,
            6,
            command_id="cmd",
            response_payload=build_host_agent_response(request, "Different response"),
        )


def test_corrupt_or_tampered_receipt_fails_closed(tmp_path, monkeypatch):
    root = project(tmp_path)
    state = {"token": "A"}
    install_context(monkeypatch, state)
    prepared = generation.prepare_chapter_generation(root, 6, command_id="cmd")
    prepared.receipt_path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid Chapter generation artifact"):
        generation.prepare_chapter_generation(root, 6, command_id="cmd")

    prepared.receipt_path.unlink()
    prepared = generation.prepare_chapter_generation(root, 6, command_id="cmd")
    receipt = json.loads(prepared.receipt_path.read_text())
    receipt["request_sha256"] = "0" * 64
    prepared.receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ValueError, match="receipt does not match request"):
        generation.prepare_chapter_generation(root, 6, command_id="cmd")


def test_outline_identity_must_match_requested_chapter(tmp_path, monkeypatch):
    root = project(tmp_path)
    state = {"token": "A"}
    install_context(monkeypatch, state)
    (root / "chapters" / "06" / "outline.yaml").write_text(
        "chapter_index: 5\nchapter_summary: Wrong\nscenes: []\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="different Chapter"):
        generation.prepare_chapter_generation(root, 6, command_id="cmd")


def test_prepare_requires_existing_accepted_bible_without_creating_one(tmp_path, monkeypatch):
    root = project(tmp_path)
    state = {"token": "A"}
    install_context(monkeypatch, state)
    (root / "bible.json").unlink()
    with pytest.raises(FileNotFoundError, match="accepted story state"):
        generation.prepare_chapter_generation(root, 6, command_id="cmd")
    assert not (root / "bible.json").exists()


def test_completion_does_not_mutate_existing_accepted_artifacts(tmp_path, monkeypatch):
    root = project(tmp_path)
    state = {"token": "A"}
    install_context(monkeypatch, state)
    for index in range(1, 6):
        directory = root / "chapters" / f"{index:02d}"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "final.md").write_text(
            f"Accepted Chapter {index}\n",
            encoding="utf-8",
        )
    tracked = [
        root / "blueprint.yaml",
        root / "bible.json",
        *(root / "chapters" / f"{index:02d}" / "final.md" for index in range(1, 6)),
    ]
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked}
    prepared = generation.prepare_chapter_generation(root, 6, command_id="cmd")
    request = load_host_agent_request(prepared.request_path)
    generation.complete_chapter_generation(
        root,
        6,
        command_id="cmd",
        response_payload=build_host_agent_response(request, "Working Chapter 6"),
    )
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked}
    assert before == after
