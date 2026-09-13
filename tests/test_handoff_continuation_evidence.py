from __future__ import annotations

from pathlib import Path

from auteur.story_design_packs.handoff import derive_decision_handoff
from auteur.story_design_packs.models import AuthorAction, source_fingerprint
from auteur.story_design_packs.session import TutorSessionStore, create_session
from auteur.story_design_packs.tutor import decision_card_from_guidance, tutor_recommend


def test_handoff_reaches_existing_structure_workflow_but_requires_uncreated_proposal(
    tmp_path: Path,
):
    """Capture the first post-handoff product discontinuity without inventing a repair."""
    blueprint = tmp_path / "blueprint.yaml"
    identity = tmp_path / "story_identity.yaml"
    blueprint.write_bytes(b"accepted blueprint\n")
    identity.write_bytes(b"accepted identity\n")
    before = {"blueprint": blueprint.read_bytes(), "identity": identity.read_bytes()}

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
    resolved = store.record_response(
        session.session_id,
        AuthorAction.CHOOSE,
        "Experimental accident",
        current_source_fingerprints=fingerprints,
    )

    handoff = derive_decision_handoff(resolved)

    assert handoff.status == "route_identified"
    assert handoff.workflow == "structure_revision"
    prepare = next(step for step in handoff.steps if step.kind == "prepare")
    assert prepare.command == "auteur structure revision plan --proposal <proposal.yaml> --project ."
    assert "does not generate one" in handoff.prerequisites[-1]

    # The handoff successfully identifies the owning workflow, but no concrete
    # StructureProposal representing the Tutor choice exists yet. A beginner
    # cannot run the prepare step until some other surface authors that proposal.
    assert not (tmp_path / "proposal.yaml").exists()
    assert not (tmp_path / "structure" / "proposals").exists()
    assert not (tmp_path / ".auteur" / "structure" / "proposals").exists()

    assert blueprint.read_bytes() == before["blueprint"]
    assert identity.read_bytes() == before["identity"]
