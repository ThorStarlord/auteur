"""Focused characterization of intention-aware realization and source integrity."""
from __future__ import annotations

import json

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    _bounded_intention_guidance, main as architecture_main, project_architecture,
)
from auteur.beginner.studio_realization import (
    complete_realization, prepare_realization,
)
from test_beginner_studio_architecture_inquiry import seeded_store
from test_beginner_studio_architecture_review import response
from test_beginner_studio_creative_intentions import _exploration
from test_beginner_studio_realization_anchors import _scene


def _keep(store, tmp_path, capsys, item_id, status="active"):
    path = tmp_path / (item_id + ".txt")
    path.write_text("Keep the reader's experience of " + item_id + ".", encoding="utf-8")
    architecture_main([
        "--project", str(tmp_path), "--canvas", store.canvas_id, "keep-intention",
        "--id", item_id, "--title", item_id.replace("-", " ").title(),
        "--directive-file", str(path), "--status", status,
    ])
    capsys.readouterr()


def test_realization_receives_only_current_author_intentions(tmp_path, capsys):
    store = seeded_store(tmp_path)
    _keep(store, tmp_path, capsys, "hope-active")
    _keep(store, tmp_path, capsys, "hope-provisional", "provisional")
    _keep(store, tmp_path, capsys, "hope-withdrawn")
    architecture_main([
        "--project", str(tmp_path), "--canvas", store.canvas_id,
        "set-intention-status", "--id", "hope-withdrawn", "--status", "withdrawn",
    ])
    capsys.readouterr()
    assert project_architecture(store)["status"] == "ready"
    pending = prepare_realization(store, ["wonder-engine"])
    source = json.loads(pending["request"]["user"])["source"]
    assert source["intention_context_version"] == 1
    assert {row["id"]: row["status"] for row in source["creative_intentions"]} == {
        "hope-active": "active", "hope-provisional": "provisional",
    }
    assert "creative_intentions" in pending["request"]["system"]


def test_changing_active_intention_invalidates_only_inflight_realization(tmp_path, capsys):
    store = seeded_store(tmp_path)
    _keep(store, tmp_path, capsys, "restoration")
    pending = prepare_realization(store, ["wonder-engine"])
    architecture_main([
        "--project", str(tmp_path), "--canvas", store.canvas_id,
        "set-intention-status", "--id", "restoration", "--status", "withdrawn",
    ])
    capsys.readouterr()
    assert project_architecture(store)["status"] == "ready"
    with pytest.raises(BeginnerConcurrencyError, match="stale realization"):
        complete_realization(store, response(pending, _scene()))


def test_unreferenced_typed_anchor_is_reported_not_claimed_used(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_realization(
        store, [], "", [{"kind": "emotion_target", "id": "dread"}],
    )
    finished = complete_realization(store, response(pending, _scene()))
    assert finished["status"] == "ready"
    assert finished["creative_anchor_coverage"] == {
        "selected": ["emotion_target:dread"], "cited": [],
        "uncited": ["emotion_target:dread"],
        "authority": "citation_coverage_not_narrative_quality",
    }


def test_provenance_requires_a_real_inquiry_hypothesis(tmp_path, capsys):
    store = seeded_store(tmp_path)
    inquiry_sha = _exploration(store)
    directive = tmp_path / "origin.txt"
    directive.write_text("Keep the decision trace.", encoding="utf-8")
    cli = [
        "--project", str(tmp_path), "--canvas", store.canvas_id, "keep-intention",
        "--id", "origin-check", "--title", "Origin check",
        "--directive-file", str(directive), "--from-request", inquiry_sha,
    ]
    with pytest.raises(ValueError, match="hypothesis ID"):
        architecture_main(cli + ["--source-ref", "h99"])
    assert not any(item.id == "origin-check" for item in store.load().items)
    architecture_main(cli + ["--source-ref", "h1"])
    capsys.readouterr()
    item = next(i for i in store.load().items if i.id == "origin-check")
    assert item.proposal_origin.source_ref == "h1"


def test_intention_disclosure_is_bounded_but_resume_preserves_all(tmp_path, capsys):
    store = seeded_store(tmp_path)
    for i in range(15):
        _keep(store, tmp_path, capsys, "intention-%02d" % i)
    context = _bounded_intention_guidance(store)
    assert len(context["items"]) <= 10
    assert context["omitted_count"] >= 5
    assert sum(len(item["directive"]) for item in context["items"]) <= 6000
    from auteur.beginner.studio_architecture import project_architecture_resume
    assert len(project_architecture_resume(store)["creative_intentions"]) == 15
