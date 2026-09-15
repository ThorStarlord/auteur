from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    return yaml.load(
        (WORKFLOWS / name).read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )


def test_development_validation_is_focused_and_not_release_qualification():
    workflow = _load("validation.yml")
    jobs = workflow["jobs"]
    assert set(jobs) == {"focused-validation"}
    rendered = (WORKFLOWS / "validation.yml").read_text(encoding="utf-8")
    assert "python -m pytest -q --tb=short" not in rendered
    assert "windows-latest" not in rendered
    assert "scripts/release_evidence.py" not in rendered


def test_stabilization_is_explicit_and_runs_full_regression():
    workflow = _load("stabilization.yml")
    assert set(workflow["on"]) == {"workflow_dispatch"}
    rendered = (WORKFLOWS / "stabilization.yml").read_text(encoding="utf-8")
    assert "python -m pytest -q --tb=short" in rendered
    assert "scripts/release_evidence.py" not in rendered
    assert "windows-latest" not in rendered


def test_release_qualification_is_explicit_exact_candidate_evidence():
    workflow = _load("release-qualification.yml")
    assert set(workflow["on"]) == {"workflow_dispatch"}
    candidate = workflow["on"]["workflow_dispatch"]["inputs"]["candidate_sha"]
    assert candidate["required"] == "true"
    rendered = (WORKFLOWS / "release-qualification.yml").read_text(encoding="utf-8")
    assert "scripts/release_evidence.py" in rendered
    assert "ref: ${{ inputs.candidate_sha }}" in rendered
    assert 'python-version: ["3.11", "3.13"]' in rendered
    assert "windows-latest" in rendered
    assert 'python-version: "3.12"' in rendered
