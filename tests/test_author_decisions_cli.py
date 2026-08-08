"""CLI regression tests: `auteur decision create|accept|evaluate|view`.

The read-only artifact view is `view` because the existing decision workspace
already owns `decision inspect` (verb collision — flagged in the design report).
All commands run via subprocess against the feature worktree import path.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import yaml as _yaml
import pytest

PY = sys.executable
FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
D_DECISION = "nine-chairs-structure"
E_DECISION = "salt-of-the-earth-subplot-cut"


def run(args, cwd):
    r = subprocess.run([PY, "-m", "auteur.cli", *args], cwd=str(cwd),
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr


def make_project(tmp_path, case, decision_id):
    proj = tmp_path / "project"
    proj.mkdir(parents=True)
    src = FIXTURES / case
    shutil.copy(src / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(src / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(src / f"{decision_id}.yaml", ad / f"{decision_id}.yaml")
    return proj


def file_hashes(root: Path) -> dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def test_import_path_is_feature_worktree():
    import auteur
    assert "auteur-author-decisions" in str(Path(auteur.__file__).resolve())


def test_create_never_extracts_alternatives_from_prose(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    # No alternatives supplied: must fail even though the question contains "or".
    rc, out, err = run(["decision", "create", "prose-test", "--question",
                        "Should it be A or B?", "--criterion", "pick one", "--project", "."], proj)
    assert rc != 0
    assert "never derived from prose" in err
    # With alternatives: options are exactly the authored ones.
    rc, out, err = run(["decision", "create", "d1", "--question", "Should it be A or B?",
                        "--alternative", "X", "--alternative", "Y", "--criterion", "C", "--project", "."], proj)
    assert rc == 0
    data = _yaml.safe_load((proj / "author_decisions" / "d1.yaml").read_text(encoding="utf-8"))
    assert data["unresolved_choice"]["options"] == ["X", "Y"]


def test_create_does_not_accept_automatically(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    rc, out, err = run(["decision", "create", "d2", "--question", "Q?",
                        "--alternative", "A", "--alternative", "B", "--criterion", "C", "--project", "."], proj)
    assert rc == 0
    assert not (proj / "author_decisions" / ".acceptance" / "d2.yaml").exists()


def test_accept_fails_on_stale_constraint_snapshots(tmp_path):
    proj = make_project(tmp_path, "case-d", D_DECISION)
    idp = proj / "story_identity.yaml"
    data = _yaml.safe_load(idp.read_text(encoding="utf-8"))
    data["not_this"][0] = "CHANGED constraint text"
    idp.write_text(_yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    rc, out, err = run(["decision", "accept", D_DECISION, "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert rc != 0
    assert "snapshot mismatch" in err


def test_accept_fails_on_missing_blocked_provenance(tmp_path):
    proj = make_project(tmp_path, "case-d", D_DECISION)
    bp = proj / "blueprint.yaml"
    data = _yaml.safe_load(bp.read_text(encoding="utf-8"))
    data["identity_propagation"] = {"outcomes": []}
    bp.write_text(_yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    rc, out, err = run(["decision", "accept", D_DECISION, "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert rc != 0
    assert "blocked provenance" in err


def test_accept_resolves_current_product_default_not_authored_value(tmp_path):
    proj = make_project(tmp_path, "case-e", E_DECISION)
    bp = proj / "blueprint.yaml"
    data = _yaml.safe_load(bp.read_text(encoding="utf-8"))
    data["contract"]["mandatory_ending_tone"] = "open"  # product now says "open"
    bp.write_text(_yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    rc, out, err = run(["decision", "accept", E_DECISION, "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert rc == 0
    record = _yaml.safe_load((proj / "author_decisions" / ".acceptance" / f"{E_DECISION}.yaml")
                             .read_text(encoding="utf-8"))
    # The artifact never contains the tone value; the record carries the CURRENT product value.
    assert record["resolved_defaults"]["contract.mandatory_ending_tone"] == "open"


def test_view_is_read_only(tmp_path):
    proj = make_project(tmp_path, "case-d", D_DECISION)
    before = file_hashes(proj)
    rc, out, err = run(["decision", "view", D_DECISION, "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert rc == 0
    assert file_hashes(proj) == before


def test_evaluate_d_two_alternatives_e_three_combinations(tmp_path):
    proj_d = make_project(tmp_path, "case-d", D_DECISION)
    rc, out, err = run(["decision", "evaluate", D_DECISION, "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", ".", "--json"], proj_d)
    assert rc == 0
    report = _yaml.safe_load(out)
    assert report["enumerated_combinations"] == [["nine_parallel_arcs"], ["one_structural_spine"]]
    proj_e = make_project(tmp_path / "e", "case-e", E_DECISION)
    rc, out, err = run(["decision", "evaluate", E_DECISION, "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", ".", "--json"], proj_e)
    assert rc == 0
    report = _yaml.safe_load(out)
    assert len(report["enumerated_combinations"]) == 3
    assert all(len(c) == 2 for c in report["enumerated_combinations"])


def test_evaluate_contains_no_recommendation_or_verdict(tmp_path):
    proj = make_project(tmp_path, "case-e", E_DECISION)
    rc, out, err = run(["decision", "evaluate", E_DECISION, "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", ".", "--json"], proj)
    assert rc == 0
    report = _yaml.safe_load(out)
    for banned in ("verdict", "recommended", "best"):
        assert banned not in report


def test_no_command_mutates_identity_or_blueprint(tmp_path):
    proj = make_project(tmp_path, "case-e", E_DECISION)
    id_hash = hashlib.sha256((proj / "story_identity.yaml").read_bytes()).hexdigest()
    bp_hash = hashlib.sha256((proj / "blueprint.yaml").read_bytes()).hexdigest()
    run(["decision", "create", "extra", "--question", "Q?", "--alternative", "A", "--alternative", "B",
         "--criterion", "C", "--project", "."], proj)
    run(["decision", "accept", E_DECISION, "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."], proj)
    run(["decision", "evaluate", E_DECISION, "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."], proj)
    run(["decision", "view", E_DECISION, "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert hashlib.sha256((proj / "story_identity.yaml").read_bytes()).hexdigest() == id_hash
    assert hashlib.sha256((proj / "blueprint.yaml").read_bytes()).hexdigest() == bp_hash


def test_no_command_writes_to_decision_workspace_state(tmp_path):
    proj = make_project(tmp_path, "case-e", E_DECISION)
    before = set(file_hashes(proj))
    run(["decision", "create", "extra2", "--question", "Q?", "--alternative", "A", "--alternative", "B",
         "--criterion", "C", "--project", "."], proj)
    run(["decision", "accept", E_DECISION, "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."], proj)
    run(["decision", "evaluate", E_DECISION, "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."], proj)
    after = set(file_hashes(proj))
    changed = after - before
    assert changed, "expected at least the acceptance record to appear"
    for rel in changed:
        assert Path(rel).parts[0] == "author_decisions", f"wrote outside author_decisions/: {rel}"


def test_unknown_fields_rejected_through_cli(tmp_path):
    proj = make_project(tmp_path, "case-e", E_DECISION)
    bad = proj / "author_decisions" / "bad.yaml"
    bad.write_text(_yaml.safe_dump({
        "decision_id": "bad",
        "unresolved_choice": {"choice_id": "bad", "question": "Q?", "options": ["A", "B"]},
        "alternative_ids": ["A", "B"],
        "combination": {"rule": "one_of"},
        "criterion": {"text": "C", "evaluator": "author_or_consumer"},
        "sneaky_extra": "x",
    }), encoding="utf-8")
    rc, out, err = run(["decision", "accept", "bad", "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert rc != 0
    assert "invalid author decision artifact" in err


def test_missing_alternatives_never_repaired_from_open_questions(tmp_path):
    proj = make_project(tmp_path, "case-e", E_DECISION)
    bad = proj / "author_decisions" / "noalts.yaml"
    artifact = {
        "decision_id": "noalts",
        "unresolved_choice": {"choice_id": "noalts", "question": "A or B?", "options": ["only one"]},
        "alternative_ids": ["only_one"],
        "combination": {"rule": "one_of"},
        "criterion": {"text": "C", "evaluator": "author_or_consumer"},
    }
    bad.write_text(_yaml.safe_dump(artifact), encoding="utf-8")
    before = bad.read_bytes()
    rc, out, err = run(["decision", "accept", "noalts", "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert rc != 0
    assert "at least 2" in err
    # No repair: the artifact is byte-identical after the failed accept.
    assert bad.read_bytes() == before
# ---------------------------------------------------------------------------
# Review fixes — F1: decision_id path safety (persistence-level invariant)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_id", [
    "..\\evil", "../evil", "a/b", "C:\\abs_evil", ".leading_dot", "a b", "a..b/evil",
])
def test_create_rejects_path_unsafe_decision_ids(tmp_path, bad_id):
    proj = tmp_path / "p"
    proj.mkdir()
    rc, out, err = run(["decision", "create", bad_id, "--question", "Q?",
                        "--alternative", "A", "--alternative", "B", "--criterion", "C",
                        "--project", "."], proj)
    assert rc != 0
    assert "decision_id" in err


def test_valid_decision_id_allows_dots_dashes_underscores(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    rc, out, err = run(["decision", "create", "my.decision_1-x", "--question", "Q?",
                        "--alternative", "A", "--alternative", "B", "--criterion", "C",
                        "--project", "."], proj)
    assert rc == 0
    assert (proj / "author_decisions" / "my.decision_1-x.yaml").exists()


def test_persistence_path_helpers_reject_invalid_ids(tmp_path):
    from auteur.author_decisions import persistence as store
    from auteur.author_decisions.models import DecisionValidationError
    for bad in ("..\\evil", "../evil", "C:\\abs_evil", ".dot", "a b"):
        with pytest.raises(DecisionValidationError):
            store.artifact_path(tmp_path, bad)
        with pytest.raises(DecisionValidationError):
            store.acceptance_path(tmp_path, bad)


def test_accept_rejects_artifact_with_invalid_internal_decision_id(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    (proj / "author_decisions").mkdir()
    bad = proj / "author_decisions" / "x.yaml"
    bad.write_text(_yaml.safe_dump({
        "decision_id": "..\\evil",
        "unresolved_choice": {"choice_id": "x", "question": "Q?", "options": ["A", "B"]},
        "alternative_ids": ["A", "B"],
        "combination": {"rule": "one_of"},
        "criterion": {"text": "C", "evaluator": "author_or_consumer"},
    }), encoding="utf-8")
    shutil.copy(FIXTURES / "case-e" / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(FIXTURES / "case-e" / "blueprint.yaml", proj / "blueprint.yaml")
    rc, out, err = run(["decision", "accept", "x", "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert rc != 0


# ---------------------------------------------------------------------------
# Review fixes — F4: decision_id must match filename stem (fail closed)
# ---------------------------------------------------------------------------

def test_accept_requires_decision_id_matches_filename_stem(tmp_path):
    proj = make_project(tmp_path, "case-e", E_DECISION)
    renamed = proj / "author_decisions" / "other-name.yaml"
    shutil.copy(proj / "author_decisions" / f"{E_DECISION}.yaml", renamed)
    rc, out, err = run(["decision", "accept", "other-name", "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert rc != 0
    assert "filename" in err


# ---------------------------------------------------------------------------
# Review fixes — F3: create --force must not overwrite an accepted artifact
# ---------------------------------------------------------------------------

def test_create_force_refuses_overwrite_of_accepted_artifact(tmp_path):
    proj = make_project(tmp_path, "case-e", E_DECISION)
    rc, out, err = run(["decision", "accept", E_DECISION, "--identity", "story_identity.yaml",
                        "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert rc == 0
    rc, out, err = run(["decision", "create", E_DECISION, "--force", "--question", "NEW?",
                        "--alternative", "Z1", "--alternative", "Z2", "--criterion", "C",
                        "--project", "."], proj)
    assert rc != 0
    assert "accepted" in err
    # acceptance record preserved; artifact not overwritten
    assert (proj / "author_decisions" / ".acceptance" / f"{E_DECISION}.yaml").exists()
    data = _yaml.safe_load((proj / "author_decisions" / f"{E_DECISION}.yaml").read_text(encoding="utf-8"))
    assert data["unresolved_choice"]["question"].startswith("Which subplot")
