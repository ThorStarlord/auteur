import json
from pathlib import Path

from auteur.beginner.post_draft import prepare_revision_handoff


def test_revision_handoff_is_derived_and_keeps_candidate_immutable(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    draft = chapter / "draft_v1.md"
    draft.write_text("candidate", encoding="utf-8")

    handoff = prepare_revision_handoff(
        tmp_path,
        1,
        command_id="revision-1",
        decision="preserve the reveal order",
        route="retry",
    )

    assert handoff.route == "retry"
    assert handoff.source_draft == "draft_v1.md"
    assert draft.read_text(encoding="utf-8") == "candidate"
    assert json.loads(handoff.path.read_text(encoding="utf-8"))["canonical"] is False
