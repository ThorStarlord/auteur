"""A mentor follow-up must be answerable from the request itself, without conversation memory.

Prior advice travels with a follow-up only while its source is still current. A changed source makes the
earlier advice stale, so it is not carried forward as present reasoning.
"""
from __future__ import annotations

import json

from auteur.beginner.studio_mentor import complete_mentor, prepare_mentor

from test_studio_mentor_agent import packet, working


def _two_directions():
    return [
        {"id": "social", "title": "Community restoration",
         "mechanism": "Help scales through shared institutions.",
         "consequence": "New people can help others.",
         "tradeoff": "The hero must share agency.",
         "distinguishing_factor": "An institutional ripple instead of personal strength.",
         "divergence_axis": "social_scale",
         "source_status": "agent_hypothesis", "source_refs": []},
        {"id": "solitude", "title": "Earned solitude",
         "mechanism": "Independence is proven by refusing rescue at the crisis.",
         "consequence": "The hero's agency becomes visible through absence.",
         "tradeoff": "Generosity can read as withdrawal.",
         "distinguishing_factor": "Agency through refusal rather than through institutions.",
         "divergence_axis": "character_agency",
         "source_status": "agent_hypothesis", "source_refs": []},
    ]


def test_followup_carries_the_fresh_advice_it_replies_to(tmp_path):
    store = working(tmp_path)
    request = prepare_mentor(store, "hero", "working", "explore")["request"]
    complete_mentor(store, packet(request, kind="explore", directions=_two_directions()))
    follow = prepare_mentor(
        store, "hero", "working", "followup",
        "Develop the second direction. What does it cost the hero?",
    )
    user = json.loads(follow["request"]["user"])
    prior = user["prior_exchange"]
    assert prior is not None
    assert prior["advice"]["kind"] == "explore"
    assert [d["title"] for d in prior["advice"]["directions"]] == [
        "Community restoration", "Earned solitude",
    ]
    assert user["author_reply"].startswith("Develop the second direction")


def test_followup_drops_prior_advice_once_its_source_changed(tmp_path):
    store = working(tmp_path)
    request = prepare_mentor(store, "hero", "working", "explore")["request"]
    complete_mentor(store, packet(request, kind="explore", directions=_two_directions()))
    canvas = store.load()
    hero = next(item for item in canvas.items if item.id == "hero").model_dump(mode="json")
    hero["content"] += " A new scene changed the hero's situation."
    store.apply("update-item", expected_revision=canvas.revision,
                command_id="change-hero-before-followup", payload={"item": hero})
    follow = prepare_mentor(store, "hero", "working", "followup", "Develop the second direction.")
    assert json.loads(follow["request"]["user"])["prior_exchange"] is None


def test_first_request_has_no_prior_exchange_to_invent(tmp_path):
    store = working(tmp_path)
    first = prepare_mentor(store, "hero", "working", "explore")
    assert json.loads(first["request"]["user"])["prior_exchange"] is None


def test_fresh_resume_recovers_prior_advice_while_a_followup_is_pending(tmp_path):
    from auteur.beginner.studio_architecture import project_architecture_resume

    store = working(tmp_path)
    request = prepare_mentor(store, "hero", "working", "explore")["request"]
    complete_mentor(store, packet(request, kind="explore", directions=_two_directions()))
    prepare_mentor(store, "hero", "working", "followup", "Develop the second direction.")
    creative = project_architecture_resume(store)["creative_deliberation"]
    assert creative["mentor_advice"] is None
    titles = [d["title"] for d in creative["mentor_prior_advice"]["advice"]["directions"]]
    assert titles == ["Community restoration", "Earned solitude"]
    assert creative["mentor_prior_advice"]["advice"]["kind"] == "explore"
