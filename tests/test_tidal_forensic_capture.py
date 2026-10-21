"""The forensic capture kit reads a Studio project without changing it and keeps private text private."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_request, build_host_agent_response, write_host_agent_request

ROOT = Path(__file__).resolve().parents[1]
VISION = "PRIVATE-VISION: a drowned library keeps rewriting its readers."
CANDIDATE = {
    "schema_version": 2, "summary": "SECRET-SUMMARY about the Drowned Library.",
    "nodes": [
        {"id": "tide", "title": "Drowned Library tide", "category": "engine", "summary": "SECRET-ENGINE text."},
        {"id": "mystery", "title": "Speculative Mystery", "category": "genre", "summary": "Questions."},
        {"id": "loss", "title": "Loss", "category": "theme", "summary": "Unlinked theme."},
    ],
    "links": [{"id": "l1", "source": "tide", "target": "mystery", "function": "drives each investigation"}],
    "genre_contracts": [{"genre_node_id": "mystery", "role": "governing", "trope_functions": ["Clue trail"],
                         "narrative_engine": "Each tide hides a clue.", "structural_pattern": "Recurring search.",
                         "payoff_expectations": ["The pattern is understood."]}],
}


def _kit():
    spec = importlib.util.spec_from_file_location("tidal_forensic_capture", ROOT / "scripts" / "tidal_forensic_capture.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    store = CanvasStore(root, "story-one")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={
        "item": {"id": "story-vision", "kind": "note", "title": "Story Vision", "content": VISION},
        "position": {"x": 0, "y": 0}})
    waiting = prepare_architecture(store)
    request = HostAgentRequest(**waiting["request"])
    complete_architecture(store, build_host_agent_response(request, json.dumps(CANDIDATE)).model_dump())
    return root


def _tree(root: Path) -> dict[str, tuple[str, int]]:
    return {p.relative_to(root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*")) if p.is_file()}


def _run(kit, project: Path, out: Path, *extra: str) -> Path:
    assert kit.main(["--project", str(project), "--out", str(out), *extra]) == 0
    (captured,) = out.iterdir()
    return captured


def _shareable_text(captured: Path) -> str:
    return "".join(p.read_text(encoding="utf-8") for p in (captured / "shareable").iterdir())


def test_capture_leaves_project_unchanged_and_copies_are_identical(tmp_path):
    kit, project = _kit(), _project(tmp_path)
    before = _tree(project)
    captured = _run(kit, project, tmp_path / "out")
    assert _tree(project) == before
    raw = captured / "private" / "raw"
    assert {k: v[0] for k, v in _tree(raw).items()} == {k: v[0] for k, v in before.items()}
    evidence = json.loads((captured / "shareable" / "evidence.json").read_text(encoding="utf-8"))
    assert evidence["capture"]["stable"] is True
    assert evidence["requests"][0]["request_sha256_recomputes"] is True
    initial = evidence["candidates"]["Initial candidate"]["analysis"]
    assert initial["themes"]["unlinked"] == ["loss"]
    assert initial["presentation_pre471"]["nodes_drawn_with_no_line"] == ["loss"]
    listed = (captured / "SHA256SUMS.txt").read_text(encoding="utf-8")
    assert "shareable/report.md" in listed and "private/report-full.md" in listed


def test_output_inside_project_is_refused_without_writing(tmp_path):
    kit, project = _kit(), _project(tmp_path)
    before = _tree(project)
    with pytest.raises(SystemExit, match="outside the project"):
        kit.main(["--project", str(project), "--out", str(project / "forensics")])
    assert _tree(project) == before and not (project / "forensics").exists()


def test_unrecognized_prompt_is_a_provenance_question(tmp_path):
    kit, project = _kit(), _project(tmp_path)
    canvas = project / ".auteur" / "beginner" / "studio" / "canvases" / "story-one"
    user = json.dumps({"revision_instruction": "", "working_context": {"vision": VISION}}, sort_keys=True)
    local = build_host_agent_request(candidate_id="studio-local", role="studio_architecture",
                                     system="A locally edited prompt.", user=user,
                                     settings={"operation": "develop", "source_sha256": "0" * 64})
    write_host_agent_request(canvas / "architecture" / "requests" / local.request_sha256 / "request.json", local)
    captured = _run(kit, project, tmp_path / "out")
    evidence = json.loads((captured / "shareable" / "evidence.json").read_text(encoding="utf-8"))
    entry = next(r for r in evidence["requests"] if r["request_sha256"] == local.request_sha256)
    assert entry["request_sha256_recomputes"] is True
    assert "provenance question, not evidence of modification" in entry["system_version"]
    assert "tamper" not in _shareable_text(captured).lower()


def test_shareable_output_keeps_private_text_out(tmp_path):
    kit, project = _kit(), _project(tmp_path)
    default = _run(kit, project, tmp_path / "default")
    shared = _shareable_text(default)
    assert "PRIVATE-VISION" not in shared and "SECRET-" not in shared and "Drowned" not in shared
    assert "PRIVATE-VISION" in (default / "private" / "report-full.md").read_text(encoding="utf-8")
    texty = _run(kit, project, tmp_path / "text", "--share-text", "--redact", "drowned library")
    shared = _shareable_text(texty)
    assert "SECRET-ENGINE" in shared and "[REDACTED-1]" in shared
    assert "PRIVATE-VISION" not in shared and "Drowned Library" not in shared


def test_change_during_capture_is_reported(tmp_path, monkeypatch, capsys):
    kit, project = _kit(), _project(tmp_path)
    real_copy = kit._copy

    def copy_then_touch(src, dst):
        real_copy(src, dst)
        if src.name == "current.json":
            src.write_text(src.read_text(encoding="utf-8") + " ", encoding="utf-8")

    monkeypatch.setattr(kit, "_copy", copy_then_touch)
    captured = _run(kit, project, tmp_path / "out")
    evidence = json.loads((captured / "shareable" / "evidence.json").read_text(encoding="utf-8"))
    assert evidence["capture"]["stable"] is False
    assert any(path.endswith("architecture/current.json") for path in evidence["capture"]["changed_during_capture"])
    assert "project changed during capture" in capsys.readouterr().out


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_local_git_history_identifies_an_unpushed_prompt(tmp_path):
    kit, repo = _kit(), tmp_path / "auteur"
    module = repo / "src" / "auteur" / "beginner" / "studio_architecture.py"
    module.parent.mkdir(parents=True)
    module.write_text('_SYSTEM = """A locally edited prompt."""\n', encoding="utf-8")
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "local prompt"], check=True)
    found = kit.system_prompts_from_git(repo)
    digest = hashlib.sha256("A locally edited prompt.".encode("utf-8")).hexdigest()
    assert "local prompt" in found[digest]
