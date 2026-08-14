"""Additional tests: acceptance provenance for `chosen` (review control-8 gap)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml as _yaml

PY = sys.executable
FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE = FIXTURES / "case-goal-significance"


def _project(tmp_path, chosen: list[str] | None):
    proj = tmp_path / "p"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(CASE / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(CASE / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    data = _yaml.safe_load((CASE / "absent.yaml").read_text(encoding="utf-8"))
    data.pop("goal_significance", None)
    if chosen is not None:
        data["chosen"] = chosen
    (ad / "goal-significance-absent.yaml").write_text(
        _yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return proj


def _accept(proj: Path):
    return subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "accept", "goal-significance-absent",
         "--identity", "story_identity.yaml", "--blueprint", "blueprint.yaml",
         "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120)


def _record(proj: Path) -> dict:
    path = proj / "author_decisions" / ".acceptance" / "goal-significance-absent.yaml"
    assert path.exists(), "acceptance record should exist"
    return _yaml.safe_load(path.read_text(encoding="utf-8"))


def test_accept_records_chosen(tmp_path):
    proj = _project(tmp_path, ["signe_marriage"])
    r = _accept(proj)
    assert r.returncode == 0, r.stderr
    record = _record(proj)
    assert record["chosen"] == ["signe_marriage"]


def test_accept_open_decision_record_unchanged_no_chosen_key(tmp_path):
    proj = _project(tmp_path, None)
    r = _accept(proj)
    assert r.returncode == 0, r.stderr
    record = _record(proj)
    assert "chosen" not in record
