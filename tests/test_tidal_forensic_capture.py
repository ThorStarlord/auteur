"""The forensic capture kit reads one Studio canvas without changing it and shares no identifying detail."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_request, build_host_agent_response, write_host_agent_request

ROOT = Path(__file__).resolve().parents[1]
CANARY = "zqxsecret"
VISION = f"A drowned library keeps rewriting its readers. {CANARY}-vision"
NODE = {"id": f"{CANARY}-tide", "title": f"{CANARY} tide", "category": "engine", "summary": f"{CANARY} engine text."}
CANDIDATE = {
    "schema_version": 2, "summary": f"{CANARY} summary.",
    "nodes": [NODE, {"id": f"{CANARY}-mystery", "title": f"{CANARY} Mystery", "category": "genre", "summary": "Q."},
              {"id": f"{CANARY}-loss", "title": "Loss", "category": "theme", "summary": "Unlinked."}],
    "links": [{"id": f"{CANARY}-l1", "source": f"{CANARY}-tide", "target": f"{CANARY}-mystery",
               "function": f"drives {CANARY} investigation"}],
    "phases": [{"id": f"{CANARY}-p1", "title": "Opening", "order": 1, "narrative_function": "Begin.",
                "genres": [{"genre": f"{CANARY} label", "role": "governing"}]}],
    "emotion_targets": [{"id": f"{CANARY}-e1", "emotion": "fear", "role": "primary", "intended_effect": "x",
                         "eliciting_condition": "y", "aesthetic_strategy": "z", "provenance": "agent_proposed"}],
    "genre_contracts": [{"genre_node_id": f"{CANARY}-mystery", "role": "governing", "trope_functions": ["Clue"],
                         "emotion_target_ids": [f"{CANARY}-e1"], "narrative_engine": "Each tide hides a clue.",
                         "structural_pattern": "Search.", "payoff_expectations": ["Understood."]}],
}


def _kit():
    spec = importlib.util.spec_from_file_location("tidal_forensic_capture", ROOT / "scripts" / "tidal_forensic_capture.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _canvas(root: Path, canvas_id: str, revise: bool = False) -> CanvasStore:
    store = CanvasStore(root, canvas_id)
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={
        "item": {"id": "story-vision", "kind": "note", "title": "Story Vision", "content": VISION},
        "position": {"x": 0, "y": 0}})
    for instruction, candidate in [("", CANDIDATE)] + ([("Sharpen the tide.", _revised())] if revise else []):
        waiting = prepare_architecture(store, instruction)
        response = build_host_agent_response(HostAgentRequest(**waiting["request"]), json.dumps(candidate))
        complete_architecture(store, response.model_dump())
    return store


def _revised() -> dict:
    revised = copy.deepcopy(CANDIDATE)
    revised["nodes"][0]["summary"] = "Sharper tide."
    return revised


def _project(tmp_path: Path, revise: bool = False) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    _canvas(root, f"{CANARY}-canvas", revise)
    return root


def _tree(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink()}


def _capture(kit, project: Path, out: Path, *extra: str, code: int = 0) -> Path:
    assert kit.main(["--project", str(project), "--out", str(out), *extra]) == code
    (captured,) = out.iterdir()
    return captured


def _shared(captured: Path) -> str:
    files = sorted((captured / "shareable").rglob("*"))
    return "\n".join([p.name for p in files] + [p.read_text(encoding="utf-8") for p in files if p.is_file()])


def test_capture_is_read_only_byte_identical_and_valid(tmp_path):
    kit, project = _kit(), _project(tmp_path)
    before = _tree(project)
    captured = _capture(kit, project, tmp_path / "out")
    assert _tree(project) == before
    assert {k: v[0] for k, v in _tree(captured / "private" / "raw").items()} == {k: v[0] for k, v in before.items()}
    evidence = json.loads((captured / "shareable" / "evidence.json").read_text(encoding="utf-8"))
    assert evidence["forensic_status"] == "VALID" and evidence["requests"][0]["recomputes"] is True
    assert [c["source"] for c in evidence["candidates"]] == ["response.json", "current working"]
    assert not (captured / "DISQUALIFIED.txt").exists()
    assert "private/" not in (captured / "shareable" / "SHA256SUMS.txt").read_text(encoding="utf-8")


def test_output_inside_project_is_refused_without_writing(tmp_path):
    kit, project = _kit(), _project(tmp_path)
    before = _tree(project)
    with pytest.raises(SystemExit, match="outside the project"):
        kit.main(["--project", str(project), "--out", str(project / "forensics")])
    assert _tree(project) == before and not (project / "forensics").exists()


def test_several_canvases_require_an_explicit_choice(tmp_path):
    kit, project = _kit(), _project(tmp_path)
    _canvas(project, "second")
    with pytest.raises(SystemExit, match="exactly one canvas"):
        kit.main(["--project", str(project), "--out", str(tmp_path / "out")])
    assert not (tmp_path / "out").exists()
    captured = _capture(kit, project, tmp_path / "out", "--canvas", "second")
    assert len(json.loads((captured / "shareable" / "evidence.json").read_text(encoding="utf-8"))["requests"]) == 1


def test_source_change_during_capture_disqualifies_the_evidence(tmp_path, monkeypatch):
    kit, project = _kit(), _project(tmp_path)
    real_copy = kit._copy

    def copy_then_touch(src, dst):
        real_copy(src, dst)
        if src.name == "current.json":
            src.write_text(src.read_text(encoding="utf-8") + " ", encoding="utf-8")

    monkeypatch.setattr(kit, "_copy", copy_then_touch)
    captured = _capture(kit, project, tmp_path / "out", code=3)
    evidence = json.loads((captured / "shareable" / "evidence.json").read_text(encoding="utf-8"))
    assert evidence["forensic_status"].startswith("DISQUALIFIED")
    assert (captured / "shareable" / "report.md").read_text(encoding="utf-8").startswith("# Auteur Studio forensic capture: DISQUALIFIED")
    assert "current.json" in (captured / "DISQUALIFIED.txt").read_text(encoding="utf-8")


def test_shareable_output_discloses_no_identifiers_hashes_paths_or_text(tmp_path):
    kit, project = _kit(), _project(tmp_path, revise=True)
    canvas = project / ".auteur" / "beginner" / "studio" / "canvases" / f"{CANARY}-canvas"
    (canvas / f"{CANARY}-notes.txt").write_text("private", encoding="utf-8")
    if hasattr(os, "symlink"):
        try:
            os.symlink(f"/home/{CANARY}/elsewhere", canvas / "linked")
        except OSError:
            pass
    captured = _capture(kit, project, tmp_path / "out", "--share-labels", "--redact", CANARY)
    shared = _shared(captured).lower()
    requests = [json.loads(p.read_text(encoding="utf-8")) for p in canvas.glob("architecture/requests/*/request.json")]
    secrets = [CANARY, hashlib.sha256(VISION.encode("utf-8")).hexdigest()]
    secrets += [r["request_sha256"] for r in requests] + [r["settings"]["source_sha256"] for r in requests]
    assert not [s for s in secrets if s.lower() in shared]
    assert CANARY in (captured / "private" / "evidence-full.json").read_text(encoding="utf-8")
    evidence = json.loads((captured / "shareable" / "evidence.json").read_text(encoding="utf-8"))
    by_source = {c["source"]: c["candidate"] for c in evidence["candidates"]}
    initial, staged = evidence["candidates"][0]["candidate"], by_source["staged revision"]
    nodes = {n["category"]: n["id"] for n in initial["nodes"]}
    assert initial["links"][0]["source"] == nodes["engine"] and initial["links"][0]["target"] == nodes["genre"]
    assert initial["genre_contracts"][0]["genre_node_id"] == nodes["genre"]
    assert initial["genre_contracts"][0]["emotion_target_ids"] == [initial["emotion_targets"][0]["id"]]
    changed = [a["id"] for a, b in zip(initial["nodes"], staged["nodes"]) if a != b]
    assert changed == [nodes["engine"]]  # raw response vs stored model dump compare equal after canon()
    assert initial["nodes"][0]["summary"].startswith("[masked")
    assert "[redacted-1]" in initial["nodes"][0]["title"].lower()


def test_unknown_prompt_is_a_provenance_question_and_local_subjects_stay_private(tmp_path):
    kit, project = _kit(), _project(tmp_path)
    canvas = next((project / ".auteur" / "beginner" / "studio" / "canvases").iterdir())
    user = json.dumps({"revision_instruction": "", "working_context": {"vision": VISION}}, sort_keys=True)
    local = build_host_agent_request(candidate_id="studio-local", role="studio_architecture",
                                     system="A locally edited prompt.", user=user, settings={"operation": "revise"})
    write_host_agent_request(canvas / "architecture" / "requests" / local.request_sha256 / "request.json", local)
    plain = json.loads((_capture(kit, project, tmp_path / "a") / "shareable" / "evidence.json").read_text(encoding="utf-8"))
    entry = next(r for r in plain["requests"] if r["operation"] == "revise")
    assert entry["recomputes"] is True and "provenance question, not evidence of modification" in entry["prompt"]
    if shutil.which("git") is None:
        pytest.skip("git is not installed")
    repo = tmp_path / "auteur"
    module = repo / "src" / "auteur" / "beginner" / "studio_architecture.py"
    module.parent.mkdir(parents=True)
    module.write_text('_SYSTEM = """A locally edited prompt."""\n', encoding="utf-8")
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "-q", "-m", f"{CANARY} subject"], check=True)
    captured = _capture(kit, project, tmp_path / "b", "--auteur-repo", str(repo))
    resolved = json.loads((captured / "shareable" / "evidence.json").read_text(encoding="utf-8"))
    assert next(r for r in resolved["requests"] if r["operation"] == "revise")["prompt"].startswith("local commit ")
    assert CANARY not in _shared(captured)
