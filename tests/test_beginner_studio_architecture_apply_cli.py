"""The bridge's apply-review action: reviewed working revisions, applied and recovered through the CLI.

These tests drive the real command-line entry point. They reuse the apply function's protections
rather than restating them: a completed review, the latest-request pointer, the baseline identity,
freshness of vision, intentions and design context, and the lock. Accepted story authority is not
written by any of these paths.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import ArchitectureCandidate, main
from auteur.beginner.studio_store import CanvasStore

SRC = Path(__file__).resolve().parents[1] / "src"
CANVAS = "story-one"


def working_store(tmp_path, vision="A long fantasy: awe, mystery, romance, local horror, and hope."):
    store = CanvasStore(tmp_path, CANVAS)
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision-created",
                payload={"item": {"id": "story-vision", "kind": "note", "title": "Story Vision",
                                  "content": vision}, "position": {"x": 20, "y": 50}})
    return store


def candidate(summary="Discovery creates new costs and choices."):
    return {
        "schema_version": 2,
        "summary": "Wonder survives shifting genres.",
        "nodes": [
            {"id": "engine", "title": "Discovery engine", "category": "engine", "summary": summary},
            {"id": "emotion", "title": "Awe", "category": "reader_experience",
             "summary": "Keep discovery wondrous."},
        ],
        "links": [{"id": "link", "source": "engine", "target": "emotion", "function": "supports"}],
        "phases": [
            {"id": "investigation", "title": "Investigation", "order": 1,
             "genres": [{"genre": "mystery", "role": "locally_dominant"}],
             "narrative_function": "Establish the central question."},
        ],
        "open_questions": ["What makes the discovery costly?"],
        "emotion_targets": [{"id": "et_awe", "emotion": "surprise", "role": "primary",
                             "intended_effect": "awe at the discovery",
                             "eliciting_condition": "the first discovery",
                             "aesthetic_strategy": "cold, clear light",
                             "provenance": "agent_proposed"}],
    }


def bridge(capsys, project, *args):
    capsys.readouterr()
    code = main(["--project", str(project), "--canvas", CANVAS, *args])
    return code, json.loads(capsys.readouterr().out)


def write_candidate(tmp_path, name, data):
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def baseline(capsys, tmp_path):
    """Prepare and complete the baseline working architecture through the bridge."""
    code, _ = bridge(capsys, tmp_path, "prepare")
    assert code == 0
    code, done = bridge(capsys, tmp_path, "complete-file",
                        "--candidate", write_candidate(tmp_path, "base.json", candidate()))
    assert code == 0 and done["status"] == "ready"
    return done


def pending_revision(capsys, tmp_path, summary="Discovery now costs a household's trust."):
    """Prepare a revision with an instruction, complete it, and return its review's request SHA."""
    code, prepared = bridge(capsys, tmp_path, "prepare", "--instruction", "Make discovery costly.")
    assert code == 0 and prepared["status"] == "awaiting_host_agent"
    code, reviewed = bridge(capsys, tmp_path, "complete-file",
                            "--candidate", write_candidate(tmp_path, "rev.json", candidate(summary)))
    assert code == 0 and reviewed["status"] == "review_ready"
    return reviewed["review"]["request_sha256"]


def current_record(tmp_path):
    return CanvasStore(tmp_path, CANVAS).directory / "architecture" / "current.json"


def current_sha(tmp_path):
    current = json.loads(current_record(tmp_path).read_text(encoding="utf-8"))
    return current["request_sha256"]


def test_cli_applies_completed_revision_and_resume_recovers_it_in_a_fresh_process(tmp_path, capsys):
    working_store(tmp_path)
    baseline(capsys, tmp_path)
    sha = pending_revision(capsys, tmp_path)
    assert current_sha(tmp_path) != sha

    code, applied = bridge(capsys, tmp_path, "apply-review", "--request-sha256", sha)

    assert code == 0
    assert applied["application"] == {"result": "applied", "request_sha256": sha, "authority": "working_only"}
    assert applied["candidate"]["nodes"][0]["summary"] == "Discovery now costs a household's trust."
    assert current_sha(tmp_path) == sha
    assert not (tmp_path / "story_identity.yaml").exists()

    env = dict(os.environ, PYTHONPATH=str(SRC), PYTHONUTF8="1")
    fresh = subprocess.run(
        [sys.executable, "-m", "auteur.beginner.studio_architecture", "--project", str(tmp_path),
         "--canvas", CANVAS, "resume"],
        capture_output=True, text=True, env=env, check=True,
    )
    resumed = json.loads(fresh.stdout)
    assert resumed["architecture"]["nodes"][0]["summary"] == "Discovery now costs a household's trust."
    assert resumed["architecture_status"] == "ready"
    assert resumed["pending_review"] is None


def test_apply_is_idempotent_and_does_not_advance_the_canvas(tmp_path, capsys):
    working_store(tmp_path)
    baseline(capsys, tmp_path)
    sha = pending_revision(capsys, tmp_path)
    assert bridge(capsys, tmp_path, "apply-review", "--request-sha256", sha)[0] == 0
    revision_before = CanvasStore(tmp_path, CANVAS).load().revision

    code, again = bridge(capsys, tmp_path, "apply-review", "--request-sha256", sha)

    assert code == 0
    assert again["application"]["result"] == "already_applied"
    assert CanvasStore(tmp_path, CANVAS).load().revision == revision_before


def test_unreviewed_request_is_rejected_and_working_state_is_unchanged(tmp_path, capsys):
    working_store(tmp_path)
    baseline(capsys, tmp_path)
    before = current_sha(tmp_path)
    code, prepared = bridge(capsys, tmp_path, "prepare", "--instruction", "Make discovery costly.")
    sha = prepared["request"]["request_sha256"]

    code, outcome = bridge(capsys, tmp_path, "apply-review", "--request-sha256", sha)

    assert code == 1
    assert outcome["application"]["result"] == "rejected"
    assert "not been completed" in outcome["application"]["error"]
    assert current_sha(tmp_path) == before


def test_superseded_review_cannot_overwrite_a_newer_request(tmp_path, capsys):
    working_store(tmp_path)
    baseline(capsys, tmp_path)
    old = pending_revision(capsys, tmp_path, summary="The first revision.")
    code, _ = bridge(capsys, tmp_path, "prepare", "--instruction", "A newer revision.")
    assert code == 0
    before = current_sha(tmp_path)

    code, outcome = bridge(capsys, tmp_path, "apply-review", "--request-sha256", old)

    assert code == 1
    assert outcome["application"]["result"] == "rejected"
    assert "superseded" in outcome["application"]["error"]
    assert current_sha(tmp_path) == before


def test_changed_baseline_is_rejected(tmp_path, capsys):
    working_store(tmp_path)
    baseline(capsys, tmp_path)
    sha = pending_revision(capsys, tmp_path)
    record_path = current_record(tmp_path)
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["request_sha256"] = "f" * 64
    record_path.write_text(json.dumps(record), encoding="utf-8")

    code, outcome = bridge(capsys, tmp_path, "apply-review", "--request-sha256", sha)

    assert code == 1
    assert outcome["application"]["result"] == "rejected"
    assert "baseline architecture changed" in outcome["application"]["error"]


def test_changed_story_vision_after_review_is_rejected(tmp_path, capsys):
    store = working_store(tmp_path)
    baseline(capsys, tmp_path)
    sha = pending_revision(capsys, tmp_path)
    before = current_sha(tmp_path)
    canvas = store.load()
    vision = next(item for item in canvas.items if item.id == "story-vision")
    store.apply("update-item", expected_revision=canvas.revision, command_id="vision-changed",
                payload={"item": vision.model_copy(update={"content": "A different author vision."}).model_dump(mode="json")})

    code, outcome = bridge(capsys, tmp_path, "apply-review", "--request-sha256", sha)

    assert code == 1
    assert outcome["application"]["result"] == "rejected"
    assert "working context changed" in outcome["application"]["error"]
    assert current_sha(tmp_path) == before


def test_malformed_and_unknown_identifiers_fail_cleanly(tmp_path, capsys):
    working_store(tmp_path)
    baseline(capsys, tmp_path)

    code, malformed = bridge(capsys, tmp_path, "apply-review", "--request-sha256", "not-a-sha")
    assert code == 1 and "64-character" in malformed["application"]["error"]

    code, unknown = bridge(capsys, tmp_path, "apply-review", "--request-sha256", "a" * 64)
    assert code == 1 and "no architecture request has this identity" in unknown["application"]["error"]


def test_apply_requires_an_explicit_request_identity(tmp_path, capsys):
    working_store(tmp_path)
    baseline(capsys, tmp_path)
    with pytest.raises(SystemExit) as exit_info:
        main(["--project", str(tmp_path), "--canvas", CANVAS, "apply-review"])
    assert exit_info.value.code == 2


def test_applying_a_working_revision_leaves_accepted_authority_and_provenance_alone(tmp_path, capsys):
    store = working_store(tmp_path)
    baseline(capsys, tmp_path)
    sha = pending_revision(capsys, tmp_path)
    before_items = {item.id: item.model_dump(mode="json") for item in store.load().items}

    code, applied = bridge(capsys, tmp_path, "apply-review", "--request-sha256", sha)

    assert code == 0
    after_items = {item.id: item.model_dump(mode="json") for item in store.load().items}
    assert after_items == before_items
    assert all(target["provenance"] == "agent_proposed" for target in applied["candidate"]["emotion_targets"])
    assert not list(tmp_path.glob("*.yaml"))
    ArchitectureCandidate.model_validate(applied["candidate"])


def test_architecture_only_candidates_reject_character_instances(tmp_path, capsys):
    working_store(tmp_path)
    code, _ = bridge(capsys, tmp_path, "prepare")
    bad = candidate()
    bad["nodes"][0]["category"] = "character"
    with pytest.raises(Exception, match="architecture-only proposals cannot instantiate characters"):
        main(["--project", str(tmp_path), "--canvas", CANVAS, "complete-file",
              "--candidate", write_candidate(tmp_path, "bad.json", bad)])


def test_revision_prompt_keeps_category_rule_and_allows_only_existing_proper_nouns(tmp_path, capsys):
    working_store(tmp_path)
    baseline(capsys, tmp_path)
    _, prepared = bridge(capsys, tmp_path, "prepare", "--instruction", "Make discovery costly.")
    system = prepared["request"]["system"]
    assert "never character/relationship" in system
    assert "in a\nrevision also proper nouns already present in the current working architecture" in system
    assert "Never add new proper nouns." in system
