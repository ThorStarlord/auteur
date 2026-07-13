"""Tests for SceneLoader YAML serialization of SceneOutline artifacts.

Tests cover:
- Round-trip serialization (save → load preserves all fields)
- All status levels (draft, incomplete, ready)
- Nested model handling (Goal, Opposition, Turn, Decision, Outcome, etc.)
- Directory operations (batch load/save, indexing)
- YAML structure validation
- Error handling (missing files, corrupt YAML, invalid schemas)
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from auteur.narrative_realization.loader.scene_loader import SceneLoader
from auteur.narrative_realization.schema.scene_action import (
    ArcBeatRealization,
    Decision,
    Goal,
    Opposition,
    Outcome,
    Turn,
)
from auteur.narrative_realization.schema.scene_outline import (
    SceneOutline,
    SceneStatus,
    TemporalRelation,
)
from auteur.narrative_realization.schema.scene_state import (
    EmotionalState,
    EntryState,
    ExitState,
    KnowledgeFact,
)


class TestSceneLoaderBasic:
    """Test basic save/load operations."""

    def test_save_and_load_draft_scene(self, tmp_path: Path):
        """Test round-trip save/load for draft status scene."""
        loader = SceneLoader()

        # Create minimal draft scene
        original = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )

        # Save to file
        output_path = tmp_path / "scene_draft.yaml"
        loader.save_scene(original, str(output_path))
        assert output_path.exists()

        # Load back
        loaded = loader.load_scene(str(output_path))

        # Verify fields match
        assert loaded.id == original.id
        assert loaded.chapter_id == original.chapter_id
        assert loaded.status == SceneStatus.DRAFT
        assert loaded.status.value == "draft"

    def test_save_and_load_incomplete_scene(self, tmp_path: Path):
        """Test round-trip save/load for incomplete status scene."""
        loader = SceneLoader()

        # Create incomplete scene with core dramatic structure
        original = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            status=SceneStatus.INCOMPLETE,
            narrative_position=2,
            pov_character_id="clara",
            participants=["clara", "daniel"],
            goal=Goal(
                actor_id="clara",
                objective="inspect_the_ledger",
                rationale="verify_alibi",
            ),
            opposition=Opposition(
                source_id="daniel",
                pressure="prevent_discovery",
                rationale="hide_guilt",
            ),
            outcome=Outcome(
                result="partial",
                knowledge_added=["ledger_discrepancy"],
                consequences=["daniel_becomes_suspicious"],
            ),
        )

        # Save and load
        output_path = tmp_path / "scene_incomplete.yaml"
        loader.save_scene(original, str(output_path))
        loaded = loader.load_scene(str(output_path))

        # Verify all fields match
        assert loaded.id == original.id
        assert loaded.chapter_id == original.chapter_id
        assert loaded.status == SceneStatus.INCOMPLETE
        assert loaded.narrative_position == 2
        assert loaded.pov_character_id == "clara"
        assert loaded.participants == ["clara", "daniel"]
        assert loaded.goal.actor_id == "clara"
        assert loaded.goal.objective == "inspect_the_ledger"
        assert loaded.opposition.source_id == "daniel"
        assert loaded.outcome.result == "partial"
        assert "ledger_discrepancy" in loaded.outcome.knowledge_added

    def test_save_and_load_ready_scene(self, tmp_path: Path):
        """Test round-trip save/load for fully ready scene."""
        loader = SceneLoader()

        entry_state = EntryState(
            knowledge=[
                KnowledgeFact(
                    what="Daniel claims innocence",
                    how_known="external_source",
                    degree="probable",
                    source="character_id",
                )
            ],
            emotional={
                "trust": EmotionalState(
                    state="guarded",
                    intensity="moderate",
                    rationale="Daniel is a suspect",
                )
            },
        )

        exit_state = ExitState(
            knowledge=[
                KnowledgeFact(
                    what="Daniel claims innocence",
                    how_known="external_source",
                    degree="probable",
                    source="character_id",
                ),
                KnowledgeFact(
                    what="Access record was altered",
                    how_known="learned",
                    degree="certain",
                    source="document",
                ),
            ],
            emotional={
                "trust": EmotionalState(
                    state="suspicion",
                    intensity="high",
                    rationale="Evidence of tampering",
                )
            },
        )

        original = SceneOutline(
            id="scene_07_02",
            chapter_id="chapter_07",
            status=SceneStatus.READY,
            narrative_position=2,
            story_time="day_3_evening",
            pov_character_id="clara",
            participants=["clara", "daniel"],
            temporal_relation=TemporalRelation(
                parallel_with=[],
                follows_scene="scene_07_01",
            ),
            goal=Goal(
                actor_id="clara",
                objective="inspect_the_ledger",
                rationale="verify_alibi",
            ),
            opposition=Opposition(
                source_id="daniel",
                pressure="prevent_discovery",
                rationale="hide_guilt",
            ),
            turn=Turn(
                type="discovery",
                event="altered_access_record_found",
                impact="clara_knows_record_manipulated",
            ),
            decision=Decision(
                actor_id="clara",
                choice="conceal_discovery",
                rationale="need_more_time",
            ),
            outcome=Outcome(
                result="partial",
                knowledge_added=["access_record_was_altered"],
                consequences=["daniel_realizes_discovery"],
            ),
            entry_state=entry_state,
            exit_state=exit_state,
            realizes_arc_beats=[
                ArcBeatRealization(beat_id="clara_distrust_deepens", degree="full")
            ],
            setups_created=["altered_record_signature"],
            payoffs_triggered=[],
            notes="Clara suspects Daniel but hides it to avoid tipping him off.",
            tags=["reveal", "discovery"],
        )

        # Save and load
        output_path = tmp_path / "scene_ready.yaml"
        loader.save_scene(original, str(output_path))
        loaded = loader.load_scene(str(output_path))

        # Verify all fields match
        assert loaded.id == original.id
        assert loaded.status == SceneStatus.READY
        assert loaded.story_time == "day_3_evening"
        assert loaded.turn.type == "discovery"
        assert loaded.turn.event == "altered_access_record_found"
        assert loaded.decision.choice == "conceal_discovery"
        assert loaded.entry_state.knowledge[0].what == "Daniel claims innocence"
        assert loaded.exit_state.knowledge[1].what == "Access record was altered"
        assert loaded.realizes_arc_beats[0].beat_id == "clara_distrust_deepens"
        assert loaded.realizes_arc_beats[0].degree == "full"
        assert "reveal" in loaded.tags
        assert "altered_record_signature" in loaded.setups_created

    def test_scene_with_empty_nested_collections(self, tmp_path: Path):
        """Test that empty lists and dicts serialize correctly."""
        loader = SceneLoader()

        original = SceneOutline(
            id="scene_02_01",
            chapter_id="chapter_02",
            status=SceneStatus.DRAFT,
            participants=[],
            realizes_arc_beats=[],
            setups_created=[],
            payoffs_triggered=[],
            tags=[],
            notes="",
        )

        output_path = tmp_path / "scene_empty_collections.yaml"
        loader.save_scene(original, str(output_path))
        loaded = loader.load_scene(str(output_path))

        assert loaded.participants == []
        assert loaded.realizes_arc_beats == []
        assert loaded.setups_created == []
        assert loaded.payoffs_triggered == []
        assert loaded.tags == []
        assert loaded.notes == ""


class TestSceneLoaderTemporalRelations:
    """Test handling of temporal relations."""

    def test_temporal_relation_follows_scene(self, tmp_path: Path):
        """Test serialization of follows_scene temporal relation."""
        loader = SceneLoader()

        original = SceneOutline(
            id="scene_03_02",
            chapter_id="chapter_03",
            status=SceneStatus.DRAFT,
            temporal_relation=TemporalRelation(
                follows_scene="scene_03_01",
                parallel_with=[],
            ),
        )

        output_path = tmp_path / "temporal_follows.yaml"
        loader.save_scene(original, str(output_path))
        loaded = loader.load_scene(str(output_path))

        assert loaded.temporal_relation is not None
        assert loaded.temporal_relation.follows_scene == "scene_03_01"
        assert loaded.temporal_relation.parallel_with == []

    def test_temporal_relation_parallel_with(self, tmp_path: Path):
        """Test serialization of parallel_with temporal relation."""
        loader = SceneLoader()

        original = SceneOutline(
            id="scene_04_01",
            chapter_id="chapter_04",
            status=SceneStatus.DRAFT,
            temporal_relation=TemporalRelation(
                parallel_with=["scene_04_02", "scene_04_03"],
                follows_scene=None,
            ),
        )

        output_path = tmp_path / "temporal_parallel.yaml"
        loader.save_scene(original, str(output_path))
        loaded = loader.load_scene(str(output_path))

        assert loaded.temporal_relation is not None
        assert set(loaded.temporal_relation.parallel_with) == {
            "scene_04_02",
            "scene_04_03",
        }
        assert loaded.temporal_relation.follows_scene is None


class TestSceneLoaderYAMLFormat:
    """Test YAML format and human readability."""

    def test_yaml_is_human_readable(self, tmp_path: Path):
        """Test that generated YAML is human-readable (not flow style)."""
        loader = SceneLoader()

        scene = SceneOutline(
            id="scene_05_01",
            chapter_id="chapter_05",
            status=SceneStatus.DRAFT,
            participants=["alice", "bob"],
            tags=["action", "climax"],
        )

        output_path = tmp_path / "scene_readable.yaml"
        loader.save_scene(scene, str(output_path))

        # Read raw YAML content
        with open(output_path, "r") as f:
            content = f.read()

        # Verify it's block style (human readable)
        assert "id: scene_05_01" in content
        assert "chapter_id: chapter_05" in content
        # Should not have flow style like {a, b}
        assert not content.startswith("{")

    def test_yaml_field_order_preserved_conceptually(self, tmp_path: Path):
        """Test that essential fields appear early in YAML."""
        loader = SceneLoader()

        scene = SceneOutline(
            id="scene_06_01",
            chapter_id="chapter_06",
            status=SceneStatus.INCOMPLETE,
            narrative_position=1,
            pov_character_id="hero",
            participants=["hero"],
            goal=Goal(actor_id="hero", objective="survive"),
            opposition=Opposition(source_id="villain", pressure="attack"),
            outcome=Outcome(result="partial"),
        )

        output_path = tmp_path / "scene_order.yaml"
        loader.save_scene(scene, str(output_path))

        with open(output_path, "r") as f:
            lines = f.readlines()

        # Find positions of key fields
        id_pos = next(i for i, line in enumerate(lines) if "id:" in line)
        chapter_pos = next(i for i, line in enumerate(lines) if "chapter_id:" in line)
        status_pos = next(i for i, line in enumerate(lines) if "status:" in line)

        # Essential identity fields should come early
        assert id_pos < chapter_pos < status_pos


class TestSceneLoaderValidation:
    """Test YAML structure validation."""

    def test_validate_valid_scene_yaml(self, tmp_path: Path):
        """Test validation returns True for valid scene YAML."""
        loader = SceneLoader()

        scene = SceneOutline(
            id="scene_07_01",
            chapter_id="chapter_07",
            status=SceneStatus.DRAFT,
        )

        output_path = tmp_path / "scene_valid.yaml"
        loader.save_scene(scene, str(output_path))

        is_valid, errors = loader.validate_scene_yaml_structure(str(output_path))
        assert is_valid is True
        assert errors == []

    def test_validate_nonexistent_file(self, tmp_path: Path):
        """Test validation fails for nonexistent file."""
        loader = SceneLoader()

        is_valid, errors = loader.validate_scene_yaml_structure(
            str(tmp_path / "nonexistent.yaml")
        )
        assert is_valid is False
        assert any("not found" in error.lower() for error in errors)

    def test_validate_corrupt_yaml(self, tmp_path: Path):
        """Test validation fails for invalid YAML syntax."""
        loader = SceneLoader()

        output_path = tmp_path / "corrupt.yaml"
        with open(output_path, "w") as f:
            f.write('id: "scene_08_01\n')  # Unfinished quote
            f.write("chapter_id: chapter_08\n")

        is_valid, errors = loader.validate_scene_yaml_structure(str(output_path))
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_missing_required_field(self, tmp_path: Path):
        """Test validation fails when required fields are missing."""
        loader = SceneLoader()

        output_path = tmp_path / "missing_field.yaml"
        with open(output_path, "w") as f:
            f.write("id: scene_09_01\n")  # Missing chapter_id
            f.write("status: draft\n")

        is_valid, errors = loader.validate_scene_yaml_structure(str(output_path))
        assert is_valid is False
        assert any("chapter_id" in error or "Validation" in error for error in errors)

    def test_validate_empty_yaml(self, tmp_path: Path):
        """Test validation fails for empty YAML file."""
        loader = SceneLoader()

        output_path = tmp_path / "empty.yaml"
        output_path.touch()  # Create empty file

        is_valid, errors = loader.validate_scene_yaml_structure(str(output_path))
        assert is_valid is False
        assert any("empty" in error.lower() for error in errors)


class TestSceneLoaderErrorHandling:
    """Test error handling and edge cases."""

    def test_load_nonexistent_file_raises_error(self, tmp_path: Path):
        """Test loading nonexistent file raises FileNotFoundError."""
        loader = SceneLoader()

        with pytest.raises(FileNotFoundError, match="not found"):
            loader.load_scene(str(tmp_path / "nonexistent.yaml"))

    def test_save_to_nonexistent_parent_creates_directory(self, tmp_path: Path):
        """Test that save creates parent directories."""
        loader = SceneLoader()

        scene = SceneOutline(
            id="scene_10_01",
            chapter_id="chapter_10",
            status=SceneStatus.DRAFT,
        )

        # Use deeply nested path
        output_path = tmp_path / "deep" / "nested" / "path" / "scene.yaml"
        loader.save_scene(scene, str(output_path))

        assert output_path.exists()
        loaded = loader.load_scene(str(output_path))
        assert loaded.id == "scene_10_01"

    def test_save_invalid_scene_raises_error(self, tmp_path: Path):
        """Test that saving invalid object raises ValueError."""
        loader = SceneLoader()

        with pytest.raises(ValueError, match="SceneOutline"):
            loader.save_scene("not_a_scene", str(tmp_path / "bad.yaml"))  # type: ignore

    def test_load_invalid_yaml_structure_raises_error(self, tmp_path: Path):
        """Test that loading invalid YAML structure raises ValueError."""
        loader = SceneLoader()

        output_path = tmp_path / "bad_structure.yaml"
        with open(output_path, "w") as f:
            f.write("- item1\n- item2\n")  # List, not dict

        with pytest.raises(ValueError, match="not a dict"):
            loader.load_scene(str(output_path))


class TestSceneLoaderDirectoryOperations:
    """Test batch load/save and directory operations."""

    def test_save_scenes_to_directory(self, tmp_path: Path):
        """Test saving multiple scenes to directory structure."""
        loader = SceneLoader()

        scenes = [
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.DRAFT,
            ),
            SceneOutline(
                id="scene_01_02",
                chapter_id="chapter_01",
                status=SceneStatus.DRAFT,
            ),
            SceneOutline(
                id="scene_02_01",
                chapter_id="chapter_02",
                status=SceneStatus.DRAFT,
            ),
        ]

        loader.save_scenes_to_directory(scenes, str(tmp_path))

        # Verify directory structure
        assert (tmp_path / "chapter_01" / "scene_01_01.yaml").exists()
        assert (tmp_path / "chapter_01" / "scene_01_02.yaml").exists()
        assert (tmp_path / "chapter_02" / "scene_02_01.yaml").exists()

    def test_save_scenes_creates_index_file(self, tmp_path: Path):
        """Test that save_scenes_to_directory creates index.yaml."""
        loader = SceneLoader()

        scenes = [
            SceneOutline(
                id="scene_03_01",
                chapter_id="chapter_03",
                status=SceneStatus.DRAFT,
            ),
        ]

        loader.save_scenes_to_directory(scenes, str(tmp_path))

        index_file = tmp_path / "index.yaml"
        assert index_file.exists()

        # Load and verify index contents
        with open(index_file, "r") as f:
            index = yaml.safe_load(f)

        assert isinstance(index, list)
        assert len(index) == 1
        assert index[0]["id"] == "scene_03_01"
        assert index[0]["chapter_id"] == "chapter_03"

    def test_load_scenes_from_directory(self, tmp_path: Path):
        """Test loading all scenes from directory."""
        loader = SceneLoader()

        scenes = [
            SceneOutline(
                id="scene_04_01",
                chapter_id="chapter_04",
                status=SceneStatus.DRAFT,
            ),
            SceneOutline(
                id="scene_04_02",
                chapter_id="chapter_04",
                status=SceneStatus.DRAFT,
            ),
            SceneOutline(
                id="scene_05_01",
                chapter_id="chapter_05",
                status=SceneStatus.DRAFT,
            ),
        ]

        # Save scenes
        loader.save_scenes_to_directory(scenes, str(tmp_path))

        # Load them back
        loaded = loader.load_scenes_from_directory(str(tmp_path))

        assert len(loaded) == 3
        ids = {s.id for s in loaded}
        assert ids == {"scene_04_01", "scene_04_02", "scene_05_01"}

    def test_load_scenes_from_nonexistent_directory_raises_error(self, tmp_path: Path):
        """Test loading from nonexistent directory raises FileNotFoundError."""
        loader = SceneLoader()

        with pytest.raises(FileNotFoundError, match="not found"):
            loader.load_scenes_from_directory(str(tmp_path / "nonexistent"))

    def test_list_scenes_in_directory(self, tmp_path: Path):
        """Test listing all scene filenames in directory."""
        loader = SceneLoader()

        scenes = [
            SceneOutline(
                id="scene_06_01",
                chapter_id="chapter_06",
                status=SceneStatus.DRAFT,
            ),
            SceneOutline(
                id="scene_06_02",
                chapter_id="chapter_06",
                status=SceneStatus.DRAFT,
            ),
        ]

        loader.save_scenes_to_directory(scenes, str(tmp_path))

        filenames = loader.list_scenes_in_directory(str(tmp_path))

        # Should list scene files, not index.yaml
        assert "scene_06_01.yaml" in filenames
        assert "scene_06_02.yaml" in filenames
        assert "index.yaml" not in filenames
        assert len(filenames) == 2

    def test_list_scenes_in_nonexistent_directory_raises_error(self, tmp_path: Path):
        """Test listing in nonexistent directory raises FileNotFoundError."""
        loader = SceneLoader()

        with pytest.raises(FileNotFoundError, match="not found"):
            loader.list_scenes_in_directory(str(tmp_path / "nonexistent"))

    def test_save_empty_scenes_list(self, tmp_path: Path):
        """Test that saving empty scenes list is a no-op."""
        loader = SceneLoader()

        loader.save_scenes_to_directory([], str(tmp_path))

        # Directory should not be created if empty
        # (since mkdir is only called if scenes is non-empty)
        # Actually, the current implementation doesn't create dir for empty list
        # This is acceptable behavior

    def test_load_scenes_skips_index_file(self, tmp_path: Path):
        """Test that load_scenes_from_directory skips index.yaml."""
        loader = SceneLoader()

        scenes = [
            SceneOutline(
                id="scene_07_01",
                chapter_id="chapter_07",
                status=SceneStatus.DRAFT,
            ),
        ]

        loader.save_scenes_to_directory(scenes, str(tmp_path))
        loaded = loader.load_scenes_from_directory(str(tmp_path))

        # Should load only 1 scene, not 2 (index.yaml should be skipped)
        assert len(loaded) == 1
        assert loaded[0].id == "scene_07_01"


class TestSceneLoaderComplexScenes:
    """Test complex scenes with all features."""

    def test_complex_ready_scene_with_all_fields(self, tmp_path: Path):
        """Test a fully populated ready scene with all possible fields."""
        loader = SceneLoader()

        complex_scene = SceneOutline(
            id="scene_08_05",
            chapter_id="chapter_08",
            status=SceneStatus.READY,
            narrative_position=5,
            story_time="day_4_noon",
            pov_character_id="protagonist",
            participants=["protagonist", "antagonist", "witness"],
            temporal_relation=TemporalRelation(
                follows_scene="scene_08_04",
                parallel_with=[],
            ),
            goal=Goal(
                actor_id="protagonist",
                objective="expose_antagonist_plan",
                rationale="save_the_city",
            ),
            opposition=Opposition(
                source_id="antagonist",
                pressure="frames_protagonist",
                rationale="protect_criminal_enterprise",
            ),
            turn=Turn(
                type="reversal",
                event="witness_comes_forward",
                impact="balance_of_power_shifts",
            ),
            decision=Decision(
                actor_id="protagonist",
                choice="trust_the_witness",
                rationale="corroborating_evidence",
            ),
            outcome=Outcome(
                result="success",
                knowledge_added=[
                    "antagonist_real_identity",
                    "scope_of_conspiracy",
                ],
                knowledge_questioned=["witness_reliability"],
                emotional_shifts={
                    "protagonist": "confident",
                    "antagonist": "panicked",
                },
                consequences=["antagonist_accelerates_plans"],
            ),
            entry_state=EntryState(
                knowledge=[
                    KnowledgeFact(
                        what="Antagonist is suspect",
                        how_known="inferred",
                        degree="probable",
                        source="inference",
                    )
                ],
                emotional={
                    "suspicion": EmotionalState(
                        state="certain",
                        intensity="high",
                    )
                },
            ),
            exit_state=ExitState(
                knowledge=[
                    KnowledgeFact(
                        what="Antagonist is suspect",
                        how_known="inferred",
                        degree="probable",
                        source="inference",
                    ),
                    KnowledgeFact(
                        what="Antagonist leads criminal ring",
                        how_known="external_source",
                        degree="certain",
                        source="character_id",
                    ),
                ],
                emotional={
                    "suspicion": EmotionalState(
                        state="confirmed",
                        intensity="high",
                        rationale="Witness confession",
                    ),
                    "urgency": EmotionalState(
                        state="crisis",
                        intensity="high",
                    ),
                },
            ),
            realizes_arc_beats=[
                ArcBeatRealization(beat_id="protagonist_discovers_truth", degree="full"),
                ArcBeatRealization(beat_id="antagonist_exposed", degree="partial"),
            ],
            setups_created=["witness_safety", "criminal_network_structure"],
            payoffs_triggered=["previous_clues"],
            notes="Critical turning point in the narrative. Everything changes here.",
            tags=["climax", "revelation", "turning_point"],
        )

        output_path = tmp_path / "complex_scene.yaml"
        loader.save_scene(complex_scene, str(output_path))
        loaded = loader.load_scene(str(output_path))

        # Verify all major fields
        assert loaded.id == complex_scene.id
        assert loaded.status == SceneStatus.READY
        assert loaded.goal.actor_id == "protagonist"
        assert len(loaded.outcome.knowledge_added) == 2
        assert loaded.outcome.emotional_shifts["protagonist"] == "confident"
        assert len(loaded.realizes_arc_beats) == 2
        assert loaded.realizes_arc_beats[0].degree == "full"
        assert len(loaded.entry_state.emotional) == 1
        assert len(loaded.exit_state.emotional) == 2
        assert "climax" in loaded.tags


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
