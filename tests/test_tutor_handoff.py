from __future__ import annotations

import json
from pathlib import Path

from auteur.cli import main, parse_args
from auteur.story_design_packs.handoff import derive_decision_handoff
from auteur.story_design_packs.models import AuthorAction, source_fingerprint
from auteur.story_design_packs.session import TutorSessionStore, create_session
from auteur.story_design_packs.tutor import decision_card_from_guidance, tutor_recommend
from auteur.workflow.models import AuthorityLevel


def _card():
    guidance = tutor_recommend(
        ["superhero"],
        decision="power origin",
        premise="a reluctant municipal hero",
    )
    return decision_card_from_guidance(guidance, source_subject="a reluctant municipal hero")


def _resolved_structure_session(tmp_path: Path):
    blueprint = tmp_path / "blueprint.yaml"
    identity = tmp_path / "story_identity.yaml"
    blueprint.write_bytes(b"accepted blueprint\n")
    identity.write_bytes(b"accepted identity\n")
    fingerprints = {
        "blueprint=blueprint.yaml": source_fingerprint(blueprint.read_bytes()),
        "identity=story_identity.yaml": source_fingerprint(identity.read_bytes()),
    }
    store = TutorSessionStore(tmp_path)
    session = create_session(_card(), fingerprints)
    store.save(session)
    resolved = store.record_response(
        session.session_id,
        AuthorAction.CHOOSE,
        "Experimental accident",
        current_source_fingerprints=fingerprints,
    )
    return store, resolved, identity, blueprint


def test_structure_handoff_routes_to_existing_revision_workflow_without_mutation(tmp_path: Path):
    _store, session, identity, blueprint = _resolved_structure_session(tmp_path)
    before = {"identity": identity.read_bytes(), "blueprint": blueprint.read_bytes()}

    handoff = derive_decision_handoff(session)

    assert handoff.status == "route_identified"
    assert handoff.target_layer == "structure"
    assert handoff.affected_artifacts == ("blueprint.yaml",)
    assert handoff.workflow == "structure_revision"
    assert handoff.authority_status == "DERIVED / NOT CANON"
    assert handoff.mutates_story is False
    assert [step.kind for step in handoff.steps] == [
        "inspect",
        "prepare",
        "validate",
        "authority",
    ]
    assert [step.authority for step in handoff.steps] == [
        AuthorityLevel.READ_ONLY,
        AuthorityLevel.DERIVED_ARTIFACT,
        AuthorityLevel.READ_ONLY,
        AuthorityLevel.CANONICAL_MUTATION,
    ]
    assert handoff.steps[-1].command == (
        "auteur structure revision apply <plan_id> --confirm --project ."
    )
    assert all(step.executable_by_handoff is False for step in handoff.steps)
    assert "does not generate one" in handoff.prerequisites[-1]
    assert identity.read_bytes() == before["identity"]
    assert blueprint.read_bytes() == before["blueprint"]


def test_handoff_refuses_to_guess_for_active_or_identity_only_session(tmp_path: Path):
    identity = tmp_path / "story_identity.yaml"
    identity.write_bytes(b"accepted identity\n")
    fingerprints = {
        "identity=story_identity.yaml": source_fingerprint(identity.read_bytes()),
    }
    store = TutorSessionStore(tmp_path)
    session = create_session(_card(), fingerprints)
    store.save(session)

    active = derive_decision_handoff(session)
    assert active.status == "unresolved"
    assert active.steps == ()
    assert active.workflow is None

    resolved = store.record_response(
        session.session_id,
        AuthorAction.CHOOSE,
        "Experimental accident",
        current_source_fingerprints=fingerprints,
    )
    identity_only = derive_decision_handoff(resolved)
    assert identity_only.status == "unresolved"
    assert identity_only.target_layer is None
    assert identity_only.steps == ()
    assert "without guessing" in identity_only.rationale


def test_stale_session_is_inspectable_but_never_actionable(tmp_path: Path):
    store, session, _identity, blueprint = _resolved_structure_session(tmp_path)
    blueprint.write_bytes(b"changed blueprint\n")
    current = {
        "blueprint=blueprint.yaml": source_fingerprint(blueprint.read_bytes()),
        "identity=story_identity.yaml": session.source_fingerprints[
            "identity=story_identity.yaml"
        ],
    }
    stale = store.refresh_status(session.session_id, current)

    handoff = derive_decision_handoff(stale)
    assert handoff.status == "stale"
    assert handoff.workflow is None
    assert handoff.steps == ()
    assert handoff.mutates_story is False


def test_root_handoff_cli_exposes_route_and_keeps_canonical_files_byte_identical(
    tmp_path: Path,
    capsys,
):
    identity = tmp_path / "story_identity.yaml"
    blueprint = tmp_path / "blueprint.yaml"
    identity.write_bytes(b"accepted identity\n")
    blueprint.write_bytes(b"accepted blueprint\n")
    before = {"identity": identity.read_bytes(), "blueprint": blueprint.read_bytes()}

    common = [
        "--pack",
        "superhero",
        "--decision",
        "power origin",
        "--premise",
        "a reluctant municipal hero",
        "--project",
        str(tmp_path),
        "--source",
        "identity=story_identity.yaml",
        "--source",
        "blueprint=blueprint.yaml",
    ]
    assert main(["tutor", "next", *common, "--json"]) == 0
    session_id = json.loads(capsys.readouterr().out)["session_id"]

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
        ]
    ) == 0
    choose_output = capsys.readouterr().out
    assert f"auteur tutor handoff {session_id}" in choose_output

    assert main(
        [
            "tutor",
            "handoff",
            session_id,
            "--project",
            str(tmp_path),
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "route_identified"
    assert payload["workflow"] == "structure_revision"
    assert payload["authority_status"] == "DERIVED / NOT CANON"
    assert payload["mutates_story"] is False
    assert payload["steps"][-1]["authority"] == "canonical_mutation"
    assert payload["steps"][-1]["executable_by_handoff"] is False

    assert identity.read_bytes() == before["identity"]
    assert blueprint.read_bytes() == before["blueprint"]


def test_root_handoff_cli_refreshes_staleness_before_routing(tmp_path: Path, capsys):
    identity = tmp_path / "story_identity.yaml"
    blueprint = tmp_path / "blueprint.yaml"
    identity.write_bytes(b"accepted identity\n")
    blueprint.write_bytes(b"accepted blueprint\n")

    common = [
        "--pack",
        "superhero",
        "--decision",
        "power origin",
        "--project",
        str(tmp_path),
        "--source",
        "blueprint=blueprint.yaml",
    ]
    assert main(["tutor", "next", *common, "--json"]) == 0
    session_id = json.loads(capsys.readouterr().out)["session_id"]
    assert main(
        [
            "tutor",
            "choose",
            session_id,
            "choose",
            "--project",
            str(tmp_path),
            "--json",
        ]
    ) == 0
    capsys.readouterr()

    blueprint.write_bytes(b"new accepted blueprint state\n")
    assert main(
        ["tutor", "handoff", session_id, "--project", str(tmp_path), "--json"]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "stale"
    assert payload["steps"] == []
    assert payload["workflow"] is None


def test_handoff_parser_is_read_only_surface():
    args = parse_args(["tutor", "handoff", "0123456789abcdef", "--project", "."])
    assert args.command == "tutor"
    assert args.tutor_command == "handoff"
    assert args.session_id == "0123456789abcdef"
