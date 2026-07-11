"""Integration tests for Series CLI commands with Group 3 continuity validators."""

from auteur.series.models import (
    SeriesIdentity, SeriesType, GlobalArc, BookPlan, SeriesFunction,
    ThematicArc, CharacterState, Relationship, LoreEntry, TimelineEvent, NarrativeSetup
)
from auteur.series.handlers import (
    handle_series_validate,
    handle_series_compile,
    handle_series_diagnose,
)
from auteur.blueprint import Genre, StoryMode
from auteur.identity import HighLevelCentralEngine, StoryType, TargetExperience


def make_valid_trilogy():
    """Create a valid trilogy series with continuity data."""
    engine = HighLevelCentralEngine(
        want="Discover the truth",
        resistance="Fear of revelation",
        conflict="Trust vs. doubt",
        stakes="Everything they know",
        change="Understanding of the world"
    )
    
    books = [
        BookPlan(
            book_number=i,
            title=f"Book {i}",
            series_function=SeriesFunction.QUESTION if i == 1 else (SeriesFunction.COMPLICATION if i == 2 else SeriesFunction.RESOLUTION),
            core_answer=f"Answer {i}",
            target_experience=TargetExperience(primary="wonder", progression="wonder -> awe -> knowing"),
            story_type=StoryType(genre=Genre.NETORARE, mode=StoryMode.TRAGIC),
            central_engine=engine,
        )
        for i in range(1, 4)
    ]

    return SeriesIdentity(
        title="Test Trilogy",
        series_type=SeriesType.TRILOGY,
        core_question="Will truth be revealed?",
        target_experience=TargetExperience(primary="wonder", progression="wonder -> awe -> knowing"),
        global_arc=GlobalArc(beginning="Start", midpoint="Middle", ending="End"),
        book_plans=books,
        thematic_arcs=[
            ThematicArc(
                id="arc1",
                theme="Power corrupts",
                books=[1, 2, 3],
                progression={1: "introduces", 2: "deepens", 3: "resolves"}
            )
        ],
        character_states=[
            CharacterState(character_id="hero", book=1, state={"status": "naive"}),
            CharacterState(character_id="hero", book=2, state={"status": "learning"}),
            CharacterState(character_id="hero", book=3, state={"status": "wise"}),
        ],
        relationships=[
            Relationship(id="rel1", party_a="hero", party_b="mentor", book=1, state="trust", notes=""),
            Relationship(id="rel1", party_a="hero", party_b="mentor", book=2, state="conflict", notes="Mentor betrays"),
            Relationship(id="rel1", party_a="hero", party_b="mentor", book=3, state="reconciliation", notes="Understanding"),
        ],
        lore_entries=[
            LoreEntry(id="magic", book=1, content="Magic requires sacrifice"),
            LoreEntry(id="magic", book=2, content="Magic requires sacrifice", consistency_notes="consistent"),
            LoreEntry(id="magic", book=3, content="Magic requires sacrifice", consistency_notes="consistent"),
        ],
        timeline_events=[
            TimelineEvent(id="event1", relative_book=1, relative_position="start"),
            TimelineEvent(id="event2", relative_book=2, relative_position="midpoint"),
            TimelineEvent(id="event3", relative_book=3, relative_position="end"),
        ],
        narrative_setups=[
            NarrativeSetup(
                id="mystery",
                book_introduced=1,
                description="Discover the artifact",
                expected_payoff_by_book=3,
                status="unresolved"
            )
        ],
    )


class TestSeriesCLIValidate:
    """Test series validate command integration."""

    def test_validate_accepts_valid_series(self):
        """Validate command accepts a valid series."""
        series = make_valid_trilogy()
        result = handle_series_validate(series)
        assert result.is_success
        assert result.exit_code == 0


class TestSeriesCLIDiagnose:
    """Test series diagnose command integration."""

    def test_diagnose_runs_continuity_validators(self):
        """Diagnose includes continuity diagnostics."""
        series = make_valid_trilogy()
        result = handle_series_diagnose(series)
        assert result.is_success
        assert result.data.diagnostics is not None


class TestSeriesCLICompile:
    """Test series compile command integration."""

    def test_compile_accepts_valid_series(self):
        """Compile accepts valid series."""
        series = make_valid_trilogy()
        result = handle_series_compile(series)
        assert result is not None
        assert result.is_success
