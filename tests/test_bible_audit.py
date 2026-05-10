"""Tests for Bible audit diagnostics — Slice 1 (enrich accept), Slice 2 (data
model), and Slice 3 (detector).

Uses the "before-matching" rule: a location change is only a teleportation
when the "before" field in event N does not match the "after" field from
the same character's last appearance in a prior event.
"""

from pathlib import Path

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient
from auteur.pipeline import PipelineRunner
from auteur.project import Project
from auteur.structure.diagnostics import DiagnosticSeverity
from auteur.structure.bible_audit import BibleAuditDiagnostic, audit_bible_locations

SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


# ============================================================================
# Slice 1 — Enrich Bible event recording during accept
# ============================================================================


def _cartographer_outline_with_state_changes() -> str:
    return """
scope: chapter
chapter_index: 1
chapter_summary: Kael returns to the tavern.
scenes:
  - scene_id: s1
    pov_character: Kael
    location: taverntown
    summary: He nurses a drink and surveys the room.
    key_events: []
    character_state_changes:
      - character: Kael
        field: location
        before: null
        after: Tavern
      - character: Kael
        field: emotional
        before: null
        after: brooding
    arc_advancements: []
    estimated_tension: 4
    emotional_tone: subtle unease
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided:
  - chosen_one_prophecy
  - resurrected_hero
  - deus_ex_machina_rescue
estimated_chapter_tension: 4
thematic_reinforcement: redemption costs more than Kael wants to pay
conflict_report: null
"""


def _scripted_pass_iteration() -> list[LLMResponse]:
    """Bard draft + 5 critics all passing."""
    return [
        LLMResponse(text="The prose of Kael at the tavern.", input_tokens=20, output_tokens=10),
        *[LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(5)],
    ]


def test_accept_records_character_state_changes_in_bible_events(tmp_path):
    """When a chapter is accepted, the Bible event must contain
    character_state_changes extracted from the Cartographer outline, and
    character records must be upserted with the new state."""
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "novel", blueprint)

    cartographer = LLMResponse(
        text=_cartographer_outline_with_state_changes(),
        input_tokens=50,
        output_tokens=80,
    )
    client = FakeClient([cartographer, *_scripted_pass_iteration()])

    runner = PipelineRunner(blueprint, bible=project.bible)
    result = runner.draft_chapter(1, llm=client, project=project, max_iterations=3)

    assert result.accepted is True

    # --- Bible event must contain the state changes ---
    events = project.bible.data["events"]
    assert len(events) == 1
    event = events[0]
    deltas = event.get("deltas", {})

    # The key assertion that should FAIL: character_state_changes is missing.
    assert "character_state_changes" in deltas, (
        "Bible event deltas should contain character_state_changes from the outline"
    )
    changes = deltas["character_state_changes"]
    assert len(changes) == 2

    by_field = {c["field"]: c for c in changes}
    assert by_field["location"] == {
        "character": "Kael",
        "field": "location",
        "before": None,
        "after": "Tavern",
    }
    assert by_field["emotional"] == {
        "character": "Kael",
        "field": "emotional",
        "before": None,
        "after": "brooding",
    }

    # --- Character records must be upserted ---
    chars = project.bible.data["characters"]
    assert "Kael" in chars, "Character 'Kael' should be upserted in the Bible"
    assert chars["Kael"]["location"] == "Tavern"
    assert chars["Kael"]["emotional"] == "brooding"

    # --- Existing fields must still be recorded ---
    assert project.bible.data["realized_tension"] == [4]


# ============================================================================
# Slice 3 — Location teleportation detector
# ============================================================================


def test_detects_location_teleportation_when_before_does_not_match_previous_after(
    tmp_path,
):
    """Event 1 ends with Aldric at Throne Room. Event 2 starts with Aldric at
    Dungeon — no explanation for the jump. Should produce an error."""
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)

    bible.record_event(
        chapter_index=1,
        summary="Aldric confronts the king.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": None,
                    "after": "Throne Room",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")

    bible.record_event(
        chapter_index=2,
        summary="Aldric wakes in the dungeon.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": "Dungeon",
                    "after": "Dungeon",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Dungeon")

    bible.save()

    diagnostics = audit_bible_locations(bible)

    assert len(diagnostics) == 1
    d = diagnostics[0]
    assert d.severity == DiagnosticSeverity.ERROR
    assert d.rule == "carriers.location_teleportation"
    assert "Aldric" in d.message
    assert "Throne Room" in d.message
    assert "Dungeon" in d.message


def test_no_diagnostic_when_intermediate_event_explains_the_move(tmp_path):
    """Event 1: Aldric at Throne Room. Event 2: dedicated move from Throne Room
    to Road (before matches previous after). Event 3: Aldric at Road with no
    further move. All transitions are explained — no diagnostic expected."""
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)

    bible.record_event(
        chapter_index=1,
        summary="Aldric confronts the king in the throne room.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": None,
                    "after": "Throne Room",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")

    bible.record_event(
        chapter_index=2,
        summary="Aldric rides north along the King's Road.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": "Throne Room",
                    "after": "Road",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Road")

    bible.record_event(
        chapter_index=3,
        summary="Aldric reaches the border outpost.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": "Road",
                    "after": "Road",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Road")

    bible.save()

    diagnostics = audit_bible_locations(bible)

    assert diagnostics == []


def test_no_diagnostic_on_first_appearance_in_later_event(tmp_path):
    """A character who first appears in event 2 (or any non-first event)
    has no prior location to compare against — no diagnostic expected."""
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)

    bible.record_event(
        chapter_index=1,
        summary="Aldric confronts the king.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": None,
                    "after": "Throne Room",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")

    bible.record_event(
        chapter_index=2,
        summary="Mara arrives at the capital.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Mara",
                    "field": "location",
                    "before": None,
                    "after": "Capital",
                }
            ]
        },
    )
    bible.upsert_character("Mara", location="Capital")

    bible.save()

    diagnostics = audit_bible_locations(bible)

    assert diagnostics == []


def test_no_diagnostic_when_character_stays_at_same_location(tmp_path):
    """A character who stays at the same location across multiple events
    should not produce any teleportation diagnostic."""
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)

    bible.record_event(
        chapter_index=1,
        summary="Aldric enters the throne room.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": None,
                    "after": "Throne Room",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")

    bible.record_event(
        chapter_index=2,
        summary="Aldric waits as the court deliberates.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": "Throne Room",
                    "after": "Throne Room",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")

    bible.record_event(
        chapter_index=3,
        summary="Aldric hears the verdict.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": "Throne Room",
                    "after": "Throne Room",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")

    bible.save()

    diagnostics = audit_bible_locations(bible)

    assert diagnostics == []


def test_detects_teleportation_per_character_independently(tmp_path):
    """Two characters each teleport in the same project. The audit should
    produce exactly two diagnostics, one per character, with correct
    attribution."""
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)

    bible.record_event(
        chapter_index=1,
        summary="Aldric and Mara meet at court.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": None,
                    "after": "Throne Room",
                },
                {
                    "character": "Mara",
                    "field": "location",
                    "before": None,
                    "after": "Tavern",
                },
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")
    bible.upsert_character("Mara", location="Tavern")

    bible.record_event(
        chapter_index=2,
        summary="Aldric wakes in the dungeon; Mara is lost in the forest.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": "Dungeon",
                    "after": "Dungeon",
                },
                {
                    "character": "Mara",
                    "field": "location",
                    "before": "Forest",
                    "after": "Forest",
                },
            ]
        },
    )
    bible.upsert_character("Aldric", location="Dungeon")
    bible.upsert_character("Mara", location="Forest")

    bible.save()

    diagnostics = audit_bible_locations(bible)

    assert len(diagnostics) == 2

    for d in diagnostics:
        assert d.severity == DiagnosticSeverity.ERROR
        assert d.rule == "carriers.location_teleportation"

    aldr_diags = [d for d in diagnostics if "Aldric" in d.message]
    mara_diags = [d for d in diagnostics if "Mara" in d.message]
    assert len(aldr_diags) == 1
    assert len(mara_diags) == 1

    assert "Throne Room" in aldr_diags[0].message
    assert "Dungeon" in aldr_diags[0].message
    assert "Tavern" in mara_diags[0].message
    assert "Forest" in mara_diags[0].message
