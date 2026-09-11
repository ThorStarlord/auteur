from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from auteur.cli import main
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient
from auteur.story_design_packs.models import AuthorAction, source_fingerprint
from auteur.story_design_packs.proposal_bridge import generate_structure_proposal_from_tutor
from auteur.story_design_packs.session import TutorSessionStore, create_session
from auteur.story_design_packs.tutor import decision_card_from_guidance, tutor_recommend
from auteur.structure.proposal_models import StructureProposal


SAMPLE_BLUEPRINT = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _payload(*, field: str = "structure", value=None) -> str:
    if value is None:
        value = {
            "estimated_chapters": 48,
            "act_structure": "three_act",
            "subplot_budget": 3,
        }
    return json.dumps(
        {
            "summary": "Make the selected origin keep producing structural consequences.",
            "option": {
                "summary": "Extend the structural runway so the chosen pressure can recur.",
                "tradeoffs": "More runway supports escalation but delays compression.",
                "data": {field: value},
            },
        }
    )


def _resolved_project(tmp_path: Path):
    blueprint = tmp_path / "blueprint.yaml"
    identity = tmp_path / "story_identity.yaml"
    blueprint.write_bytes(SAMPLE_BLUEPRINT.read_bytes())
    identity.write_bytes(b"accepted identity sentinel\n")

    card = decision_card_from_guidance(
        tutor_recommend(
            ["superhero"],
            decision="power origin",
            premise="a reluctant municipal hero",
        ),
        source_subject="a reluctant municipal hero",
    )
    fingerprints = {
        "blueprint=blueprint.yaml": source_fingerprint(blueprint.read_bytes()),
        "identity=story_identity.yaml": source_fingerprint(identity.read_bytes()),
    }
    store = TutorSessionStore(tmp_path)
    session = create_session(card, fingerprints)
    store.save(session)
    session = store.record_response(
        session.session_id,
        AuthorAction.CHOOSE,
        "Experimental accident",
        current_source_fingerprints=fingerprints,
    )
    return store, session, identity, blueprint


def test_bridge_generates_valid_unselected_noncanonical_proposal_without_story_mutation(
    tmp_path: Path,
):
    _store, session, identity, blueprint = _resolved_project(tmp_path)
    before = {"identity": identity.read_bytes(), "blueprint": blueprint.read_bytes()}
    client = FakeClient([LLMResponse(text=_payload(), input_tokens=7, output_tokens=5)])

    result = generate_structure_proposal_from_tutor(tmp_path, session, client)

    assert result.authority_status == "DERIVED / NOT CANON"
    assert result.mutates_story is False
    assert result.requires_author_selection is True
    assert result.ready_for_revision_plan is False
    assert result.proposal_path.startswith(".auteur/structure/proposals/tutor_")
    proposal_path = tmp_path / result.proposal_path
    assert proposal_path.is_file()

    raw = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    proposal = StructureProposal.model_validate(raw)
    assert proposal.proposal_id == result.proposal_id
    assert proposal.selection.selected_option_id == ""
    assert proposal.decision is None
    assert proposal.source_rule.startswith(f"tutor_session:{session.session_id}:")
    assert proposal.source_domain == f"tutor_card:{session.card_id}"
    assert "Experimental accident" in proposal.summary
    assert proposal.options[0].data["structure"]["estimated_chapters"] == 48
    assert result.next_command_after_selection.endswith(f"--proposal {result.proposal_path} --project .")

    request_payload = json.loads(client.calls[0].user)
    assert request_payload["selected_tutor_value"] == "Experimental accident"
    assert "identity" not in request_payload["allowed_top_level_fields"]
    assert "current_blueprint" in request_payload

    assert identity.read_bytes() == before["identity"]
    assert blueprint.read_bytes() == before["blueprint"]


def test_bridge_rejects_malformed_or_unsafe_model_output_without_proposal_artifact(tmp_path: Path):
    _store, session, _identity, _blueprint = _resolved_project(tmp_path)
    proposals = tmp_path / ".auteur" / "structure" / "proposals"

    malformed = FakeClient([LLMResponse(text="not json", input_tokens=1, output_tokens=1)])
    with pytest.raises(ValueError, match="not valid JSON"):
        generate_structure_proposal_from_tutor(tmp_path, session, malformed)
    assert not proposals.exists()

    identity_edit = FakeClient(
        [LLMResponse(text=_payload(field="identity", value={"title": "Hijack"}), input_tokens=1, output_tokens=1)]
    )
    with pytest.raises(ValueError, match="unsupported field"):
        generate_structure_proposal_from_tutor(tmp_path, session, identity_edit)
    assert not proposals.exists()

    incomplete = FakeClient(
        [LLMResponse(text=_payload(field="story_engine", value={"main_thread": {}}), input_tokens=1, output_tokens=1)]
    )
    with pytest.raises(ValueError, match="valid complete replacement"):
        generate_structure_proposal_from_tutor(tmp_path, session, incomplete)
    assert not proposals.exists()


def test_bridge_fails_closed_on_stale_or_unresolved_session_before_llm_call(tmp_path: Path):
    store, resolved, _identity, blueprint = _resolved_project(tmp_path)

    class ExplodingClient:
        def complete(self, _request):
            raise AssertionError("LLM must not be called for ineligible Tutor state")

    blueprint.write_text("changed after Tutor choice\n", encoding="utf-8")
    with pytest.raises(ValueError, match="stale"):
        generate_structure_proposal_from_tutor(tmp_path, resolved, ExplodingClient())

    blueprint.write_bytes(SAMPLE_BLUEPRINT.read_bytes())
    fingerprints = {
        "blueprint=blueprint.yaml": source_fingerprint(blueprint.read_bytes()),
    }
    active = create_session(resolved.card, fingerprints)
    store.save(active)
    with pytest.raises(ValueError, match="resolved choose"):
        generate_structure_proposal_from_tutor(tmp_path, active, ExplodingClient())


def test_bridge_atomic_replace_failure_leaves_no_partial_proposal(tmp_path: Path, monkeypatch):
    _store, session, identity, blueprint = _resolved_project(tmp_path)
    before = {"identity": identity.read_bytes(), "blueprint": blueprint.read_bytes()}
    client = FakeClient([LLMResponse(text=_payload(), input_tokens=1, output_tokens=1)])
    original_replace = Path.replace

    def fail_proposal_replace(self: Path, target: Path):
        if self.name.endswith(".yaml.tmp"):
            raise OSError("simulated atomic replace failure")
        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", fail_proposal_replace)
    with pytest.raises(OSError, match="simulated atomic replace failure"):
        generate_structure_proposal_from_tutor(tmp_path, session, client)

    proposals = tmp_path / ".auteur" / "structure" / "proposals"
    assert not list(proposals.glob("*.yaml")) if proposals.exists() else True
    assert not list(proposals.glob("*.tmp")) if proposals.exists() else True
    assert identity.read_bytes() == before["identity"]
    assert blueprint.read_bytes() == before["blueprint"]


def test_root_tutor_propose_uses_configured_client_and_returns_candidate(tmp_path: Path, monkeypatch, capsys):
    _store, session, identity, blueprint = _resolved_project(tmp_path)
    before = {"identity": identity.read_bytes(), "blueprint": blueprint.read_bytes()}
    client = FakeClient([LLMResponse(text=_payload(), input_tokens=3, output_tokens=2)])
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model: client)

    assert main(
        [
            "tutor",
            "propose",
            session.session_id,
            "--project",
            str(tmp_path),
            "--provider",
            "anthropic",
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["session_id"] == session.session_id
    assert payload["selected_tutor_value"] == "Experimental accident"
    assert payload["authority_status"] == "DERIVED / NOT CANON"
    assert payload["mutates_story"] is False
    assert payload["requires_author_selection"] is True
    assert payload["ready_for_revision_plan"] is False
    assert (tmp_path / payload["proposal_path"]).is_file()
    assert len(client.calls) == 1
    assert identity.read_bytes() == before["identity"]
    assert blueprint.read_bytes() == before["blueprint"]


def test_root_tutor_propose_blocks_stale_before_client_construction(tmp_path: Path, monkeypatch, capsys):
    _store, session, _identity, blueprint = _resolved_project(tmp_path)
    blueprint.write_text("changed source\n", encoding="utf-8")

    def explode(*_args, **_kwargs):
        raise AssertionError("provider client must not be built for stale advice")

    monkeypatch.setattr("auteur.llm.factory.build_client", explode)
    assert main(
        ["tutor", "propose", session.session_id, "--project", str(tmp_path), "--json"]
    ) == 2
    assert "current supported Structure authority route" in capsys.readouterr().err
