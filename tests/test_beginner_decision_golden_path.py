from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.cli import main
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient
from auteur.ui.dashboard import build_dashboard


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
  mode: "adventure"
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
  mode: "adventure"
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


def _proposal_client(blueprint: Path) -> FakeClient:
    raw = yaml.safe_load(blueprint.read_text(encoding="utf-8"))
    replacement = dict(raw["structure"])
    replacement["estimated_chapters"] = 48
    payload = json.dumps(
        {
            "summary": "Keep the selected origin consequential across the whole book.",
            "option": {
                "summary": "Give the origin pressure more structural runway.",
                "tradeoffs": "More escalation room, less compression.",
                "data": {"structure": replacement},
            },
        }
    )
    return FakeClient([LLMResponse(text=payload, input_tokens=1, output_tokens=1)])


def test_beginner_decision_golden_path_closes_safe_authority_loop(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    """Exercise one beginner project from raw premise through explicit revision authority."""
    discovery_client = _discovery_client()
    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda provider, model, **kwargs: discovery_client,
    )

    discovery = tmp_path / "story_discovery"
    assert main(
        [
            "story-discovery", "run", PREMISE,
            "--candidates", "2", "--output", str(discovery), "--project", str(tmp_path),
        ]
    ) == 0
    capsys.readouterr()
    assert (discovery / "candidate_1.yaml").is_file()
    assert (discovery / "candidate_2.yaml").is_file()
    assert (discovery / "comparison.md").is_file()

    identity = tmp_path / "story_identity.yaml"
    assert main(
        [
            "story-discovery", "accept", str(discovery / "candidate_1.yaml"),
            "--output", str(identity), "--keep-candidates",
        ]
    ) == 0
    capsys.readouterr()

    blueprint = tmp_path / "blueprint.yaml"
    assert main(["blueprint", "seed", str(identity), "--output", str(blueprint)]) == 0
    capsys.readouterr()
    identity_before = identity.read_bytes()
    blueprint_before = blueprint.read_bytes()

    common = [
        "--pack", "superhero",
        "--decision", "power origin",
        "--premise", PREMISE,
        "--project", str(tmp_path),
        "--source", "identity=story_identity.yaml",
        "--source", "blueprint=blueprint.yaml",
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
            "tutor", "choose", session_id, "choose", "--value", "Experimental accident",
            "--project", str(tmp_path), "--json",
        ]
    ) == 0
    resolved = json.loads(capsys.readouterr().out)
    assert resolved["status"] == "resolved"
    assert resolved["authority_status"] == "LOCAL / NONCANONICAL"

    assert main(["tutor", "handoff", session_id, "--project", str(tmp_path), "--json"]) == 0
    handoff = json.loads(capsys.readouterr().out)
    assert handoff["status"] == "route_identified"
    assert handoff["target_layer"] == "structure"
    assert handoff["workflow"] == "structure_revision"
    assert handoff["affected_artifacts"] == ["blueprint.yaml"]
    assert handoff["steps"][-1]["executable_by_handoff"] is False
    assert handoff["authority_status"] == "DERIVED / NOT CANON"
    assert identity.read_bytes() == identity_before
    assert blueprint.read_bytes() == blueprint_before

    proposal_client = _proposal_client(blueprint)
    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda provider, model, **kwargs: proposal_client,
    )
    assert main(["tutor", "propose", session_id, "--project", str(tmp_path), "--json"]) == 0
    proposed = json.loads(capsys.readouterr().out)
    proposal_path = proposed["proposal_path"]
    assert proposed["requires_author_selection"] is True
    assert proposed["ready_for_revision_plan"] is False
    assert identity.read_bytes() == identity_before
    assert blueprint.read_bytes() == blueprint_before

    assert main([
        "structure", "proposal", "inspect", proposal_path,
        "--project", str(tmp_path), "--json",
    ]) == 0
    inspected = json.loads(capsys.readouterr().out)
    option_id = inspected["options"][0]["id"]
    assert inspected["authority_status"] == "NONCANONICAL PROPOSAL / NOT APPLIED"
    assert inspected["selected_option_id"] is None

    assert main([
        "structure", "proposal", "select", proposal_path, "--option", option_id,
        "--author", "Golden Path Author", "--project", str(tmp_path), "--json",
    ]) == 0
    selected = json.loads(capsys.readouterr().out)
    assert selected["ready_for_revision_plan"] is True
    assert blueprint.read_bytes() == blueprint_before

    assert main([
        "structure", "revision", "plan", "--proposal", proposal_path,
        "--project", str(tmp_path), "--json",
    ]) == 0
    planned = json.loads(capsys.readouterr().out)
    plan_id = planned["plan_id"]
    assert planned["operation_count"] == 1
    assert planned["mutates_story"] is False

    assert main([
        "structure", "revision", "validate", plan_id,
        "--project", str(tmp_path), "--json",
    ]) == 0
    validated = json.loads(capsys.readouterr().out)
    assert validated["state"] == "ready"
    assert validated["ready_for_application"] is True

    assert main([
        "structure", "revision", "preview", plan_id,
        "--project", str(tmp_path), "--json",
    ]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview["authority_status"] == "DERIVED PREVIEW / NOT APPLIED"
    assert preview["currentness"] == "current"
    assert preview["ready_for_authority_action"] is True
    assert preview["mutates_story"] is False
    assert identity.read_bytes() == identity_before
    assert blueprint.read_bytes() == blueprint_before

    assert main([
        "structure", "revision", "apply", plan_id,
        "--confirm", "--project", str(tmp_path), "--json",
    ]) == 0
    application = json.loads(capsys.readouterr().out)
    assert application["state"] == "applied"
    application_id = application["application_id"]
    assert identity.read_bytes() == identity_before
    assert blueprint.read_bytes() != blueprint_before
    changed_blueprint = yaml.safe_load(blueprint.read_text(encoding="utf-8"))
    assert changed_blueprint["structure"]["estimated_chapters"] == 48

    assert main([
        "structure", "revision", "reassess", application_id,
        "--project", str(tmp_path), "--json",
    ]) == 0
    reassessed = json.loads(capsys.readouterr().out)
    assert reassessed["authority_status"] == "DERIVED REASSESSMENT / READ ONLY"
    assert reassessed["assessment_status"] == "not_assessable"
    assert reassessed["quality_score"] is None
    assert reassessed["mutates_story"] is False

    dashboard = build_dashboard(tmp_path)
    attention = dashboard["author_attention"]
    assert attention
    assert attention[0]["kind"] == "tutor_session"
    assert attention[0]["state"] == "stale"
    assert attention[0]["authority_status"] == "LOCAL / NONCANONICAL"
    assert identity.read_bytes() == identity_before
