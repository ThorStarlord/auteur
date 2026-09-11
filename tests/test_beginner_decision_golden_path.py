from __future__ import annotations

import json
from pathlib import Path

from auteur.cli import main
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


PREMISE = (
    "A young municipal engineer survives a reactor accident, gains dangerous powers, "
    "and must decide whether to become the public protector of a city that helped cause it."
)

CANDIDATE_ONE = """
title: "Fault Line Hero"
core_answer: "A superhero story about an engineer whose powers make the city's negligence impossible to ignore."
target_experience:
  primary: "moral pressure"
  progression: "wonder -> responsibility -> costly resolve"
  avoid: []
story_type:
  medium: "novel"
  mode: "dramatic"
  genre: "other"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The engineer wants to protect the city without becoming its property."
  resistance: "Officials need the accident and its causes to remain politically containable."
  conflict: "Every public rescue increases both trust in the engineer and institutional pressure to control them."
  stakes: "Lives, public legitimacy, and the truth about the accident."
  change: "The engineer accepts public responsibility while refusing institutional ownership."
not_this: []
open_questions: []
confidence: 0.9
recommendation_mode: "open_ended"
best_basis: "genre_aligned"
why_this_is_best: "The power origin remains an ongoing source of responsibility and conflict."
rejected_directions: []
author_overrides: []
"""

CANDIDATE_TWO = """
title: "Invisible Liability"
core_answer: "A suspense story about an engineer hiding powers while investigating the accident that created them."
target_experience:
  primary: "paranoia"
  progression: "secrecy -> pursuit -> exposure"
  avoid: []
story_type:
  medium: "novel"
  mode: "dramatic"
  genre: "other"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The engineer wants to identify who caused the accident before anyone learns what happened to them."
  resistance: "The investigation itself reveals traces of the engineer's new abilities."
  conflict: "Finding the truth makes secrecy progressively less possible."
  stakes: "Freedom, public safety, and proof of institutional wrongdoing."
  change: "The engineer gives up secrecy to expose the cause of the disaster."
not_this: []
open_questions: []
confidence: 0.8
recommendation_mode: "open_ended"
best_basis: "genre_aligned"
why_this_is_best: "The origin drives a secrecy-and-investigation engine."
rejected_directions: []
author_overrides: []
"""


def _discovery_client() -> FakeClient:
    summary_one = json.dumps(
        {
            "summary": "Public responsibility turns the origin into continuing pressure.",
            "tradeoffs": ["Less room for a prolonged secret-identity mystery."],
            "risks": ["Institutional conflict can crowd out personal relationships."],
            "best_for": ["A responsibility-centered superhero story."],
        }
    )
    summary_two = json.dumps(
        {
            "summary": "Secrecy turns the origin into an investigation engine.",
            "tradeoffs": ["Public accountability arrives later."],
            "risks": ["The power itself can become secondary to the mystery."],
            "best_for": ["A paranoid superhero suspense story."],
        }
    )
    return FakeClient(
        [
            LLMResponse(text=f"```yaml\n{CANDIDATE_ONE}\n```", input_tokens=1, output_tokens=1),
            LLMResponse(text=f"```yaml\n{CANDIDATE_TWO}\n```", input_tokens=1, output_tokens=1),
            LLMResponse(text=summary_one, input_tokens=1, output_tokens=1),
            LLMResponse(text=summary_two, input_tokens=1, output_tokens=1),
        ]
    )


def test_beginner_decision_golden_path_reaches_safe_choice_but_no_authority_handoff(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    """Exercise the post-M1 beginner path and make the observed product gap executable."""
    client = _discovery_client()
    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda provider, model, **kwargs: client,
    )

    discovery = tmp_path / "story_discovery"
    assert main(
        [
            "story-discovery",
            "run",
            PREMISE,
            "--candidates",
            "2",
            "--output",
            str(discovery),
            "--project",
            str(tmp_path),
        ]
    ) == 0
    capsys.readouterr()
    assert (discovery / "candidate_1.yaml").is_file()
    assert (discovery / "candidate_2.yaml").is_file()
    assert (discovery / "comparison.md").is_file()

    identity = tmp_path / "story_identity.yaml"
    assert main(
        [
            "story-discovery",
            "accept",
            str(discovery / "candidate_1.yaml"),
            "--output",
            str(identity),
            "--keep-candidates",
        ]
    ) == 0
    capsys.readouterr()
    assert identity.is_file()

    blueprint = tmp_path / "blueprint.yaml"
    assert main(
        [
            "blueprint",
            "seed",
            str(identity),
            "--output",
            str(blueprint),
        ]
    ) == 0
    capsys.readouterr()
    assert blueprint.is_file()

    accepted_before = {
        "identity": identity.read_bytes(),
        "blueprint": blueprint.read_bytes(),
    }

    common = [
        "--pack",
        "superhero",
        "--decision",
        "power origin",
        "--premise",
        PREMISE,
        "--project",
        str(tmp_path),
        "--source",
        "identity=story_identity.yaml",
        "--source",
        "blueprint=blueprint.yaml",
    ]

    assert main(["tutor", "next", *common, "--json"]) == 0
    next_payload = json.loads(capsys.readouterr().out)
    session_id = next_payload["session_id"]
    assert next_payload["card"]["recommendation"] == "Experimental accident"
    assert next_payload["card"]["authority_status"] == "DERIVED / NOT CANON"

    assert main(["tutor", "explain", *common, "--json"]) == 0
    explained = json.loads(capsys.readouterr().out)
    assert explained["card"]["card_id"] == next_payload["card"]["card_id"]

    assert main(
        [
            "tutor",
            "choose",
            session_id,
            "choose",
            "--value",
            "Experimental accident",
            "--project",
            str(tmp_path),
            "--json",
        ]
    ) == 0
    resolved = json.loads(capsys.readouterr().out)

    assert resolved["status"] == "resolved"
    assert resolved["response_action"] == "choose"
    assert resolved["response_value"] == "Experimental accident"
    assert resolved["authority_status"] == "LOCAL / NONCANONICAL"
    assert resolved["card"]["authority_status"] == "DERIVED / NOT CANON"

    # M1 correctly stops before authority. The integration gap is that the
    # resolved response contains no structured route to the existing workflow
    # that would enact the chosen design direction.
    assert "handoff" not in resolved
    assert "authority_handoff" not in resolved
    assert "next_authority_action" not in resolved

    assert identity.read_bytes() == accepted_before["identity"]
    assert blueprint.read_bytes() == accepted_before["blueprint"]
