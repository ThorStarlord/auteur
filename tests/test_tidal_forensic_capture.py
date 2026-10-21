"""The forensic capture kit reads one Studio canvas without changing it and shares no identifying detail."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_request, build_host_agent_response, write_host_agent_request

ROOT = Path(__file__).resolve().parents[1]
CANARY = "zqxsecret"
VISION = f"A drowned library keeps rewriting its readers. {CANARY}-vision"
CANDIDATE = {
    "schema_version": 2, "summary": f"{CANARY} summary.",
    "nodes": [{"id": f"{CANARY}-tide", "title": f"{CANARY} tide", "category": "engine", "summary": f"{CANARY} engine."},
              {"id": f"{CANARY}-mystery", "title": f"{CANARY} Mystery", "category": "genre", "summary": "Q."},
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


def _canvas(root: Path, canvas_id: str, revise: bool = True) -> Path:
    store = CanvasStore(root, canvas_id)
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={
        "item": {"id": "story-vision", "kind": "note", "title": "Story Vision", "content": VISION},
        "position": {"x": 0, "y": 0}})
    revised = json.loads(json.dumps(CANDIDATE))
    revised["nodes"][0]["summary"] = "Sharper tide."
    for instruction, candidate in [("", CANDIDATE)] + ([("Sharpen the tide.", revised)] if revise else []):
        waiting = prepare_architecture(store, instruction)
        response = build_host_agent_response(HostAgentRequest(**waiting["request"]), json.dumps(candidate))
        complete_architecture(store, response.model_dump())
    return store.directory


def _tree(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink()}


def _capture(kit, project: Path, out: Path, *extra: str, code: int = 0) -> tuple[Path, dict]:
    assert kit.main(["--project", str(project), "--out", str(out), *extra]) == code
    (captured,) = out.iterdir()
    return captured, json.loads((captured / "shareable" / "evidence.json").read_text(encoding="utf-8"))


@pytest.fixture
def setup(tmp_path):
    (tmp_path / "project").mkdir()
    return _kit(), tmp_path / "project", _canvas(tmp_path / "project", f"{CANARY}-canvas")


def test_capture_is_read_only_byte_identical_and_valid(setup, tmp_path):
    kit, project, _ = setup
    before = _tree(project)
    captured, evidence = _capture(kit, project, tmp_path / "out")
    assert _tree(project) == before
    assert {k: v[0] for k, v in _tree(captured / "private" / "raw").items()} == {k: v[0] for k, v in before.items()}
    assert evidence["forensic_status"] == "VALID" and evidence["requests"][0]["recomputes"] is True
    assert evidence["contains_creative_material"] is False and not (captured / "DISQUALIFIED.txt").exists()
    assert [c["source"] for c in evidence["candidates"]] == ["response.json"] * 2 + ["staged revision", "current working"]
    assert "private/" not in (captured / "shareable" / "SHA256SUMS.txt").read_text(encoding="utf-8")


def test_refuses_output_in_project_and_ambiguous_canvas_without_writing(setup, tmp_path):
    kit, project, _ = setup
    with pytest.raises(SystemExit, match="outside the project"):
        kit.main(["--project", str(project), "--out", str(project / "forensics")])
    _canvas(project, "second")
    with pytest.raises(SystemExit, match="exactly one canvas"):
        kit.main(["--project", str(project), "--out", str(tmp_path / "out")])
    assert not (project / "forensics").exists() and not (tmp_path / "out").exists()
    assert len(_capture(kit, project, tmp_path / "out", "--canvas", "second")[1]["requests"]) == 2


def test_windows_junctions_are_detected_on_every_supported_python(monkeypatch):
    kit = _kit()
    monkeypatch.delattr(os.path, "isjunction", raising=False)  # absent before Python 3.12
    tags = {0xA0000003: True, 0xA000000C: True, 0xA000001D: True,  # junction, symlink, WSL link
            0x9000001A: False, 0: False}  # OneDrive placeholder, plain directory
    for tag, expected in tags.items():
        fake = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_reparse_tag=tag)
        assert kit._is_link(Path("x"), lstat=lambda _: fake) is expected, hex(tag)


def test_changed_or_new_files_disqualify_the_capture(setup, tmp_path, monkeypatch):
    kit, project, canvas = setup
    real_copy = kit._copy

    def copy_then_disturb(src, dst):
        real_copy(src, dst)
        if src.name == "current.json":
            src.write_text(src.read_text(encoding="utf-8") + " ", encoding="utf-8")
            (canvas / "late.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(kit, "_copy", copy_then_disturb)
    captured, evidence = _capture(kit, project, tmp_path / "out", code=3)
    assert evidence["forensic_status"].startswith("DISQUALIFIED")
    assert (captured / "shareable" / "report.md").read_text(encoding="utf-8").startswith("# Auteur Studio forensic capture: DISQUALIFIED")
    marker = (captured / "DISQUALIFIED.txt").read_text(encoding="utf-8")
    assert "source changed or vanished during capture" in marker and "appeared during capture" in marker


def test_shareable_output_discloses_no_identifiers_hashes_paths_or_text(setup, tmp_path):
    kit, project, canvas = setup
    (canvas / f"{CANARY}-notes.txt").write_text("private", encoding="utf-8")
    outside = tmp_path / f"{CANARY}-outside"
    outside.mkdir()
    (outside / "elsewhere.txt").write_text(CANARY, encoding="utf-8")
    try:
        os.symlink(outside, canvas / "linked", target_is_directory=True)
    except OSError:  # unprivileged Windows
        pass
    captured, evidence = _capture(kit, project, tmp_path / "out", "--share-labels", "--redact", CANARY)
    files = sorted((captured / "shareable").rglob("*"))
    shared = "\n".join([p.name for p in files] + [p.read_text(encoding="utf-8") for p in files]).lower()
    requests = [json.loads(p.read_text(encoding="utf-8")) for p in canvas.glob("architecture/requests/*/request.json")]
    secrets = [CANARY, hashlib.sha256(VISION.encode("utf-8")).hexdigest()]
    secrets += [r["request_sha256"] for r in requests] + [r["settings"]["source_sha256"] for r in requests]
    assert not [s for s in secrets if s.lower() in shared]
    assert CANARY in (captured / "private" / "evidence-full.json").read_text(encoding="utf-8")
    assert not list((captured / "private" / "raw").rglob("elsewhere.txt"))
    assert evidence["contains_creative_material"] is True and "creative material" in shared
    by_source = {c["source"]: c["candidate"] for c in evidence["candidates"]}
    initial, staged = evidence["candidates"][0]["candidate"], by_source["staged revision"]
    nodes = {n["category"]: n["id"] for n in initial["nodes"]}
    assert initial["links"][0]["source"] == nodes["engine"] and initial["links"][0]["target"] == nodes["genre"]
    assert initial["genre_contracts"][0]["genre_node_id"] == nodes["genre"]
    assert initial["genre_contracts"][0]["emotion_target_ids"] == [initial["emotion_targets"][0]["id"]]
    assert [a["id"] for a, b in zip(initial["nodes"], staged["nodes"]) if a != b] == [nodes["engine"]]
    assert initial["nodes"][0]["summary"].startswith("[masked") and "[REDACTED-1]" in initial["nodes"][0]["title"]


def test_unknown_prompt_is_a_provenance_question_and_local_subjects_stay_private(setup, tmp_path):
    kit, project, canvas = setup
    user = json.dumps({"revision_instruction": "", "working_context": {"vision": VISION}}, sort_keys=True)
    local = build_host_agent_request(candidate_id="studio-local", role="studio_architecture",
                                     system="A locally edited prompt.", user=user, settings={"operation": "local"})
    write_host_agent_request(canvas / "architecture" / "requests" / local.request_sha256 / "request.json", local)
    entry = next(r for r in _capture(kit, project, tmp_path / "a")[1]["requests"] if r["operation"] == "local")
    assert entry["recomputes"] is True and "provenance question, not evidence of modification" in entry["prompt"]
    if shutil.which("git") is None:
        pytest.skip("git is not installed")
    repo = tmp_path / "auteur"
    module = repo / "src" / "auteur" / "beginner" / "studio_architecture.py"
    module.parent.mkdir(parents=True)
    module.write_text('_SYSTEM = """A locally edited prompt."""\n', encoding="utf-8")
    for args in (["init", "-q"], ["add", "."], ["commit", "-q", "-m", f"{CANARY} subject"]):
        subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args], check=True)
    captured, evidence = _capture(kit, project, tmp_path / "b", "--auteur-repo", str(repo))
    assert next(r for r in evidence["requests"] if r["operation"] == "local")["prompt"].startswith("local commit ")
    assert CANARY not in "".join(p.read_text(encoding="utf-8") for p in (captured / "shareable").iterdir())
