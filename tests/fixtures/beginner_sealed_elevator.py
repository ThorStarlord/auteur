"""Deterministic sealed-elevator fixture factory (Task 8 qualification).

The sealed-elevator premise is test data, not application logic: a fixed
Mystery premise plus helpers that drive the Beginner workspace through its
documented command contracts. Replacing the premise with an author-supplied
Mystery premise must not change the interaction grammar.
"""

from __future__ import annotations

from pathlib import Path

from auteur.beginner.application import BeginnerWorkspaceApplication
from auteur.beginner.contracts import MutationCommand
from auteur.beginner.mystery_adapter import mystery_qualification_inventory

SEALED_ELEVATOR_PREMISE = "A sealed elevator opens on an empty shaft."
SEALED_WORKSPACE_ID = "sealed-elevator"
SEALED_PROJECT_ID = "project-sealed-elevator"
SEALED_GUIDANCE_GENRE = "mystery"


def create_app(
    tmp_path: Path,
    workspace_id: str = SEALED_WORKSPACE_ID,
) -> BeginnerWorkspaceApplication:
    """Create a Mystery workspace on the sealed-elevator premise."""
    app = BeginnerWorkspaceApplication(tmp_path, workspace_id)
    app.create_workspace(
        command_id=f"create-{workspace_id}",
        project_id=SEALED_PROJECT_ID,
        premise=SEALED_ELEVATOR_PREMISE,
        guidance_genre=SEALED_GUIDANCE_GENRE,
    )
    return app


def command_for(
    app: BeginnerWorkspaceApplication,
    command_id: str,
    payload: dict | None = None,
) -> MutationCommand:
    """Build the common MutationCommand envelope at the current version."""
    return MutationCommand(
        workspace_id=app.workspace_id,
        expected_session_version=app.projection().session_version,
        command_id=command_id,
        payload=dict(payload or {}),
    )


def choose_required_options(app: BeginnerWorkspaceApplication, prefix: str) -> None:
    """Answer every card of one stage with its guided recommendation, in order."""
    inventory = mystery_qualification_inventory()
    card_ids = [card.card_id for card in inventory.cards if card.card_id.startswith(prefix)]
    for position, card_id in enumerate(card_ids):
        card = inventory.card(card_id)
        app.select_working_option(
            card_id=card_id,
            option=card.recommendation,
            expected_session_version=app.projection().session_version,
        )
        if position + 1 < len(card_ids):
            app.continue_decision(
                card_id=card_id,
                expected_session_version=app.projection().session_version,
            )
