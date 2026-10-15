"""Adversarial author-agent proxy replays. Not independently sampled model output.

These deliberately authored packets test mechanical handoff and source authority,
NOT originality or whether an actual author would enjoy the resulting mentorship.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.beginner.studio_mentor import MentorAdvice, complete_mentor, prepare_mentor
from auteur.beginner.studio_store import CanvasStore

FIXTURE = Path(__file__).parent / "fixtures" / "studio_mentor_proxy_author_cases.json"
CASES = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda x: x["id"])
def test_scripted_agent_advice_has_concrete_provisional_choices(case):
    advice = MentorAdvice.model_validate(case["advice"], strict=True)
    assert advice.focus_id == case["focus_id"]
    assert advice.kind in {"explore", "challenge", "question"}
    assert len(advice.directions) <= 3
    assert not advice.source_refs
    assert all(option.source_status == "agent_hypothesis" and not option.source_refs
               for option in advice.directions)
    if advice.directions:
        axes = {option.divergence_axis for option in advice.directions}
        assert len(axes) == len(advice.directions)
        assert all(option.distinguishing_factor.strip() for option in advice.directions)
        assert all(option.mechanism.strip() != option.consequence.strip()
                   for option in advice.directions)


@pytest.mark.parametrize("case", CASES, ids=lambda x: x["id"])
def test_scripted_host_agent_roundtrip_preserves_author_authority(tmp_path, case):
    root = tmp_path / case["id"]
    store = CanvasStore(root, "story")
    store.create()
    author_intention = case["author_intention"]
    store.apply(
        "create-item", expected_revision=0, command_id="vision",
        payload={"item": {"id": "story-vision", "kind": "note", "title": "Story Vision",
                          "content": author_intention},
                 "position": {"x": 40, "y": 80}},
    )
    store.apply(
        "create-item", expected_revision=1, command_id="focus",
        payload={"item": {"id": case["focus_id"], "kind": "note",
                          "title": "Narrative focus", "content": case["risk"]},
                 "position": {"x": 200, "y": 180}},
    )
    before = store.load().model_dump(mode="json")
    pending = prepare_mentor(store, case["focus_id"], "working",
                             case["purpose"], author_intention)
    assert pending["status"] == "awaiting_host_agent"
    raw = json.loads(pending["request"]["user"])
    assert raw["author_reply"] == author_intention
    assert raw["working_context"]["author_story_vision"] == author_intention
    assert raw["working_context"]["accepted_identity_status"] == "not_bound"
    response = build_host_agent_response(
        HostAgentRequest(**pending["request"]),
        json.dumps(case["advice"], ensure_ascii=False),
    ).model_dump()
    completed = complete_mentor(store, response)
    assert completed["status"] == "ready"
    assert completed["author_reply"] == author_intention
    assert completed["advice"]["focus_id"] == case["focus_id"]
    assert completed["advice"]["directions"] == case["advice"]["directions"]
    assert store.load().model_dump(mode="json") == before
    assert not (root / "story_identity.yaml").exists()


def test_proxy_cases_are_explicitly_non_human_and_not_model_sample_evidence():
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert raw["schema_note"].startswith("SCRIPTED proxy-author/agent")
    assert len(raw["cases"]) >= 3
