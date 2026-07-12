"""Integration test for netorara genre - proves zero special-casing works.

This test validates that all outline artifacts (BookOutline, ChapterOutline,
CharacterArc, StoryArc) work end-to-end with netorara genre using the same
validator infrastructure as mystery and gentlefemdom, proving the architecture
requires zero genre-specific infrastructure changes.
"""

import pytest
from datetime import datetime

from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_blueprint.schema.outline_types import PhaseRange, ContainerArtifact
from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator
from auteur.narrative_blueprint.validator.arc_validator import ArcValidator


class TestNetorareFullOutlineWorkflow:
    """Comprehensive integration test for netorara genre outline workflow."""

    def test_netorara_full_outline_workflow(self):
        """Validate all outline artifacts work end-to-end for netorara genre.

        This test proves that:
        1. BookOutline supports netorara with 9-phase summary
        2. ChapterOutline works for multiple netorara chapters
        3. CharacterArc captures Michael's humiliation journey
        4. StoryArc tracks the taboo discovery arc
        5. ContainerValidator ensures consistency across all artifacts
        6. ArcValidator enforces netorara-specific themes
        All using identical infrastructure as mystery and gentlefemdom.
        """
        now = datetime.now()

        # 1. Create BookOutline for "The Surrender" - 20-chapter netorara story
        netorara_phases = {
            1: "Michael's confidence - marriage is perfect, total control",
            2: "Sarah's suggestion - first proposal for exploration",
            3: "Preparations - couple discusses boundaries and logistics",
            4: "Anticipation - Michael experiences first doubts about control",
            5: "First encounter begins - Michael witnesses vulnerability",
            6: "Humiliation peak - Michael discovers arousal in helplessness",
            7: "New understanding - willing participation emerges",
            8: "Integration - couple accepts new dynamic with tenderness",
            9: "New equilibrium - deeper intimacy through surrender",
        }

        book_outline = BookOutline(
            genre="netorare",
            story_id="netorara_surrender_001",
            name="The Surrender Book Outline",
            description="Complete outline for The Surrender, exploring a couple's journey into humiliation play",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="The Surrender",
            chapter_estimate=20,
            structure="3-act",
            phases_summary=netorara_phases,
        )

        # 2. Create ChapterOutline objects (3 chapters across different phases)
        chapter_1 = ChapterOutline(
            genre="netorare",
            story_id="netorara_surrender_001",
            name="Chapter 1 Outline",
            description="Introduction to Michael's confident marriage",
            created_at=now,
            modified_at=now,
            parent_id=book_outline.story_id,
            chapter_number=1,
            phase=1,
            title="Our Perfect Marriage",
            goal="Establish Michael's belief in complete marital control",
            conflict="Sarah seems content but restless",
            turning_point="Sarah hints at desire for more exploration",
            emotional_beat="confidence → curiosity → unease",
            arc_progressions={
                "michael_humiliation_arc": "Believes marriage is complete and perfect",
                "taboo_discovery_arc": "No awareness of taboo desires",
            },
        )

        chapter_6 = ChapterOutline(
            genre="netorare",
            story_id="netorara_surrender_001",
            name="Chapter 6 Outline",
            description="First encounter reaches climax of humiliation",
            created_at=now,
            modified_at=now,
            parent_id=book_outline.story_id,
            chapter_number=6,
            phase=6,
            title="The First Night",
            goal="Michael experiences peak humiliation and arousal conflict",
            conflict="Michael's control illusion shatters; new sensation overwhelms",
            turning_point="Michael realizes humiliation is arousing him",
            emotional_beat="horror → denial → surrender → arousal",
            arc_progressions={
                "michael_humiliation_arc": "Humiliation creates unexpected arousal",
                "taboo_discovery_arc": "The taboo desire is real and mutual",
            },
        )

        chapter_15 = ChapterOutline(
            genre="netorare",
            story_id="netorara_surrender_001",
            name="Chapter 15 Outline",
            description="Willing participation becomes integrated reality",
            created_at=now,
            modified_at=now,
            parent_id=book_outline.story_id,
            chapter_number=15,
            phase=8,
            title="Willingness",
            goal="Michael actively chooses participation; shame transforms to belonging",
            conflict="Reconciling old identity with new desires",
            turning_point="Michael initiates intimacy with acknowledgment of desire",
            emotional_beat="acceptance → agency → intimacy → belonging",
            arc_progressions={
                "michael_humiliation_arc": "Willing participation deepens connection",
                "taboo_discovery_arc": "Shared vulnerability creates deeper trust",
            },
        )

        # 3. Create CharacterArc for Michael's humiliation journey
        michael_turning_points = [
            TurningPoint(
                chapter=1,
                moment="Sarah's suggestion",
                belief_shift="From: 'My wife is mine alone' → To: 'Maybe there's more to explore'",
            ),
            TurningPoint(
                chapter=6,
                moment="First encounter climax",
                belief_shift="From: 'I control everything' → To: 'Humiliation creates arousal'",
            ),
            TurningPoint(
                chapter=15,
                moment="Willing initiation",
                belief_shift="From: 'Shame is humiliation' → To: 'Sharing creates deeper intimacy'",
            ),
        ]

        michael_arc = CharacterArc(
            genre="netorare",
            story_id="netorara_surrender_001",
            name="Michael's Humiliation Journey",
            description="Michael's transformation from control-focused husband to willing participant in humiliation play",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            character_name="Michael",
            initial_belief="My wife is mine alone",
            final_belief="Sharing creates deeper intimacy",
            turning_points=michael_turning_points,
            genre_themes=["humiliation", "cuckoldry", "shame", "arousal"],
        )

        # 4. Create StoryArc for The Taboo Discovery
        taboo_checkpoints = [
            ArcCheckpoint(
                phase=1,
                moment="Sarah mentions desire for exploration",
            ),
            ArcCheckpoint(
                phase=3,
                moment="Couple discusses and plans the encounter",
            ),
            ArcCheckpoint(
                phase=6,
                moment="The taboo encounter reveals mutual desire",
            ),
            ArcCheckpoint(
                phase=9,
                moment="Taboo fully integrated into shared intimacy",
            ),
        ]

        taboo_arc = StoryArc(
            genre="netorare",
            story_id="netorara_surrender_001",
            name="The Taboo Discovery Arc",
            description="Discovery and integration of shared taboo desires within the marriage",
            created_at=now,
            modified_at=now,
            arc_name="The Taboo Discovery",
            arc_category="mystery",
            phase_range=PhaseRange(start=1, peak=6, end=9),
            checkpoints=taboo_checkpoints,
        )

        # 5. Validate all artifacts together with ContainerValidator
        all_outlines: list[ContainerArtifact] = [
            book_outline,
            chapter_1,
            chapter_6,
            chapter_15,
        ]

        container_validator = ContainerValidator()
        is_consistent, consistency_errors = container_validator.validate_consistency(
            all_outlines
        )

        assert is_consistent is True, (
            f"Container validation failed for netorara workflow: {consistency_errors}"
        )
        assert consistency_errors == [], (
            f"Expected no consistency errors, got: {consistency_errors}"
        )

        # 6. Validate CharacterArc themes match netorara genre
        arc_validator = ArcValidator()

        michael_themes_valid, michael_theme_errors = arc_validator.validate_arc_themes(
            michael_arc, "netorare"
        )

        assert michael_themes_valid is True, (
            f"Michael's arc themes don't match netorara genre: {michael_theme_errors}"
        )
        assert michael_theme_errors == [], (
            f"Expected no theme errors for Michael's arc, got: {michael_theme_errors}"
        )

        # 7. Validate StoryArc phases are valid
        story_arc_valid, story_arc_errors = (
            arc_validator.validate_story_arc_phases(
                taboo_arc, num_chapters=book_outline.chapter_estimate
            )
        )

        assert story_arc_valid is True, (
            f"Taboo arc phases invalid: {story_arc_errors}"
        )
        assert story_arc_errors == [], (
            f"Expected no phase errors for taboo arc, got: {story_arc_errors}"
        )

        # 8. Verify all artifacts maintain genre consistency
        assert book_outline.genre == "netorare"
        assert chapter_1.genre == "netorare"
        assert chapter_6.genre == "netorare"
        assert chapter_15.genre == "netorare"
        assert michael_arc.genre == "netorare"
        assert taboo_arc.genre == "netorare"

        # 9. Verify story_id linkage is consistent
        story_id = "netorara_surrender_001"
        assert book_outline.story_id == story_id
        assert chapter_1.story_id == story_id
        assert chapter_6.story_id == story_id
        assert chapter_15.story_id == story_id
        assert michael_arc.story_id == story_id
        assert taboo_arc.story_id == story_id

        # 10. Verify artifact types
        assert book_outline.artifact_type() == "book_outline"
        assert chapter_1.artifact_type() == "chapter_outline"
        assert chapter_6.artifact_type() == "chapter_outline"
        assert chapter_15.artifact_type() == "chapter_outline"
        assert michael_arc.artifact_type() == "character_arc"
        assert taboo_arc.artifact_type() == "story_arc"

        # 11. Verify CharacterArc captures Michael's journey
        assert michael_arc.character_name == "Michael"
        assert michael_arc.initial_belief == "My wife is mine alone"
        assert michael_arc.final_belief == "Sharing creates deeper intimacy"
        assert len(michael_arc.turning_points) == 3
        assert michael_arc.turning_points[0].chapter == 1
        assert michael_arc.turning_points[1].chapter == 6
        assert michael_arc.turning_points[2].chapter == 15

        # 12. Verify StoryArc tracks taboo discovery across 9-phase structure
        assert taboo_arc.arc_name == "The Taboo Discovery"
        assert taboo_arc.arc_category == "mystery"
        assert taboo_arc.phase_range.start == 1
        assert taboo_arc.phase_range.peak == 6
        assert taboo_arc.phase_range.end == 9
        assert len(taboo_arc.checkpoints) == 4

        # 13. Verify netorara-specific themes are present
        assert "humiliation" in michael_arc.genre_themes
        assert "cuckoldry" in michael_arc.genre_themes
        assert "shame" in michael_arc.genre_themes
        assert "arousal" in michael_arc.genre_themes

    def test_netorara_uses_identical_infrastructure_as_mystery_and_gentlefemdom(self):
        """Verify that netorara uses the same outline classes without special-casing.

        This test proves that:
        - BookOutline, ChapterOutline, CharacterArc, StoryArc are genre-agnostic
        - ContainerValidator and ArcValidator handle netorara identically to other genres
        - No special-case code exists in the infrastructure layer
        """
        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        # Create identical structure for all three genres
        genres = ["netorare", "mystery", "gentlefemdom"]
        outlines = {}

        for genre in genres:
            book = BookOutline(
                genre=genre,
                story_id=f"test_{genre}",
                name=f"{genre.title()} Book",
                description=f"Test outline for {genre}",
                created_at=now,
                modified_at=now,
                parent_id=None,
                title=f"{genre.title()} Book",
                chapter_estimate=10,
                structure="3-act",
                phases_summary=phases,
            )

            chapter = ChapterOutline(
                genre=genre,
                story_id=f"test_{genre}",
                name=f"{genre.title()} Chapter",
                description="Test chapter",
                created_at=now,
                modified_at=now,
                parent_id=book.story_id,
                chapter_number=1,
                phase=1,
                title="Chapter One",
                goal="Test goal",
                conflict="Test conflict",
                turning_point="Test turning point",
                emotional_beat="Test beat",
            )

            outlines[genre] = [book, chapter]

        # All three genres should pass identical validation
        validator = ContainerValidator()

        for genre, outline_list in outlines.items():
            is_valid, errors = validator.validate_consistency(outline_list)
            assert is_valid is True, (
                f"Validation failed for {genre}: {errors}"
            )
            assert errors == [], f"Unexpected errors for {genre}: {errors}"

        # This proves no special-casing: same code path handles all genres
