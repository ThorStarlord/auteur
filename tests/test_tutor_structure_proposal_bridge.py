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

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _payload(field="structure", value=None):
    value = value or {"estimated_chapters": 48, "act_structure": "three_act", "subplot_budget": 3}
    return json.dumps({
        "summary": "Keep the selected origin structurally consequential.",
        "option": {
            "summary": "Extend runway so the pressure can recur.",
            "tradeoffs": "More escalation runway, less compression.",
            "data": {field: value},
        },
    })


def _client(text=None):
    return FakeClient([LLMResponse(text=text or _payload(), input_tokens=1, output_tokens=1)])


def _resolved(tmp_path: Path):
    blueprint, identity = tmp_path / "blueprint.yaml", tmp_path / "story_identity.yaml"
    blueprint.write_bytes(SAMPLE.read_bytes())
    identity.write_bytes(b"accepted identity sentinel\n")
    card = decision_card_from_guidance(
        tutor_recommend(["superhero"], decision="power origin", premise="a reluctant municipal hero"),
        source_subject="a reluctant municipal hero",
    )
    fps = {
        "blueprint=blueprint.yaml": source_fingerprint(blueprint.read_bytes()),
        "identity=story_identity.yaml": source_fingerprint(identity.read_bytes()),
    }
    store = TutorSessionStore(tmp_path)
    session = create_session(card, fps)
    store.save(session)
    session = store.record_response(
        session.session_id, AuthorAction.CHOOSE, "Experimental accident",
        current_source_fingerprints=fps,
    )
    return store, session, identity, blueprint


def test_bridge_persists_valid_unselected_noncanonical_candidate_without_story_mutation(tmp_path: Path):
    _store, session, identity, blueprint = _resolved(tmp_path)
    before = identity.read_bytes(), blueprint.read_bytes()
    client = _client()
    result = generate_structure_proposal_from_tutor(tmp_path, session, client)

    assert (result.authority_status, result.mutates_story) == ("DERIVED / NOT CANON", False)
    assert result.requires_author_selection and not result.ready_for_revision_plan
    path = tmp_path / result.proposal_path
    proposal = StructureProposal.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    assert path.is_file() and result.proposal_path.startswith(".auteur/structure/proposals/tutor_")
    assert proposal.selection.selected_option_id == "" and proposal.decision is None
    assert proposal.source_rule.startswith(f"tutor_session:{session.session_id}:")
    assert proposal.source_domain == f"tutor_card:{session.card_id}"
    assert proposal.options[0].data["structure"]["estimated_chapters"] == 48
    request = json.loads(client.calls[0].user)
    assert request["selected_tutor_value"] == "Experimental accident"
    assert "identity" not in request["allowed_top_level_fields"]
    assert "current_blueprint" in request
    assert (identity.read_bytes(), blueprint.read_bytes()) == before


@pytest.mark.parametrize(
    ("text", "error"),
    [
        ("not json", "not valid JSON"),
        (_payload("identity", {"title": "Hijack"}), "unsupported field"),
        (_payload("story_engine", {"main_thread": {}}), "valid complete replacement"),
    ],
)
def test_bridge_rejects_bad_model_output_without_artifact(tmp_path: Path, text: str, error: str):
    _store, session, _identity, _blueprint = _resolved(tmp_path)
    with pytest.raises(ValueError, match=error):
        generate_structure_proposal_from_tutor(tmp_path, session, _client(text))
    assert not (tmp_path / ".auteur" / "structure" / "proposals").exists()


def test_bridge_fails_closed_before_llm_for_stale_or_active_session(tmp_path: Path):
    store, resolved, _identity, blueprint = _resolved(tmp_path)

    class ExplodingClient:
        def complete(self, _request):
            raise AssertionError("LLM must not be called")

    blueprint.write_text("changed after choice\n", encoding="utf-8")
    with pytest.raises(ValueError, match="stale"):
        generate_structure_proposal_from_tutor(tmp_path, resolved, ExplodingClient())
    blueprint.write_bytes(SAMPLE.read_bytes())
    fps = {"blueprint=blueprint.yaml": source_fingerprint(blueprint.read_bytes())}
    active = create_session(resolved.card, fps)
    store.save(active)
    with pytest.raises(ValueError, match="resolved choose"):
        generate_structure_proposal_from_tutor(tmp_path, active, ExplodingClient())


def test_bridge_atomic_failure_cleans_partial_and_preserves_story(tmp_path: Path, monkeypatch):
    _store, session, identity, blueprint = _resolved(tmp_path)
    before = identity.read_bytes(), blueprint.read_bytes()
    original = Path.replace

    def fail(self: Path, target: Path):
        if self.name.endswith(".yaml.tmp"):
            raise OSError("simulated atomic replace failure")
        return original(self, target)

    monkeypatch.setattr(Path, "replace", fail)
    with pytest.raises(OSError, match="simulated atomic replace failure"):
        generate_structure_proposal_from_tutor(tmp_path, session, _client())
    proposals = tmp_path / ".auteur" / "structure" / "proposals"
    assert not proposals.exists() or not list(proposals.iterdir())
    assert (identity.read_bytes(), blueprint.read_bytes()) == before


def test_root_tutor_propose_returns_candidate_and_blocks_stale_before_client(tmp_path: Path, monkeypatch, capsys):
    _store, session, identity, blueprint = _resolved(tmp_path)
    before = identity.read_bytes(), blueprint.read_bytes()
    client = _client()
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model: client)

    command = ["tutor", "propose", session.session_id, "--project", str(tmp_path), "--json"]
    assert main(command) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["authority_status"] == "DERIVED / NOT CANON"
    assert payload["requires_author_selection"] and not payload["ready_for_revision_plan"]
    assert (tmp_path / payload["proposal_path"]).is_file() and len(client.calls) == 1
    assert (identity.read_bytes(), blueprint.read_bytes()) == before

    blueprint.write_text("changed source\n", encoding="utf-8")
    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("client must not build")),
    )
    assert main(command) == 2
    assert "current supported Structure authority route" in capsys.readouterr().err
