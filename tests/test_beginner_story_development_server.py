from auteur.beginner.server import _COMMAND_HANDLERS, projection_to_dict


def test_server_routes_explicit_continuation_commands() -> None:
    assert _COMMAND_HANDLERS["propose-outline"] == "propose_outline"
    assert _COMMAND_HANDLERS["accept-chapter-plan"] == "accept_chapter_plan"
    assert _COMMAND_HANDLERS["prepare-draft-handoff"] == "prepare_draft_handoff"


def test_server_projection_contract_includes_continuation() -> None:
    from auteur.beginner.contracts import SessionEnvelope
    from auteur.beginner.projections import build_workspace_projection
    from auteur.beginner.mystery_adapter import mystery_qualification_inventory

    session = SessionEnvelope.new("project", "mystery", "A locked room")
    projection = build_workspace_projection(
        session=session,
        inventory=mystery_qualification_inventory(),
        answers={},
    )

    assert projection_to_dict(projection, workspace_id="workspace-1")["continuation"] is None
