"""Tests for Structure reference system.

Tests cover:
- ID format validation (IdFormat utility)
- Reference base model validation
- Specific reference types (Arc, Chapter, Beat, Payoff, Setup)
- Reference resolution against artifact registry
- Reference graph construction and analysis
- Edge cases and error conditions
"""

import pytest
from auteur.narrative_orchestration.schema.references import (
    Reference,
    ArcReference,
    ChapterReference,
    BeatReference,
    PayoffReference,
    SetupReference,
    ReferenceType,
    ReferenceResolver,
    ReferenceGraph,
    IdFormat,
    ArtifactTypePrefix,
)


class TestIdFormat:
    """Test ID format validation and parsing."""

    def test_valid_id_formats(self):
        """Test that valid ID formats are accepted."""
        valid_ids = [
            "chapter_01",
            "book_001",
            "character_arc_01",
            "sequence_03",
            "beating_point_clara",
            "story_arc_mystery",
            "turning_point_001",
            "clara_distrust_deepens",
        ]

        for artifact_id in valid_ids:
            assert IdFormat.is_valid_id(artifact_id), f"Should accept: {artifact_id}"

    def test_invalid_id_formats(self):
        """Test that invalid ID formats are rejected."""
        invalid_ids = [
            "Chapter_01",  # Capital letter
            "chapter-01",  # Hyphen instead of underscore
            "chapter 01",  # Space
            "chapter",  # No underscore
            "001",  # No artifact type
            "_chapter_01",  # Leading underscore
            "chapter_",  # Trailing underscore
            "",  # Empty
            "chapter_01 extra",  # Space after
        ]

        for artifact_id in invalid_ids:
            assert (
                not IdFormat.is_valid_id(artifact_id)
            ), f"Should reject: {artifact_id}"

    def test_split_id_simple(self):
        """Test splitting simple IDs."""
        artifact_type, unique_id = IdFormat.split_id("chapter_07")
        assert artifact_type == "chapter"
        assert unique_id == "07"

    def test_split_id_compound_type(self):
        """Test splitting IDs with compound artifact types."""
        artifact_type, unique_id = IdFormat.split_id("character_arc_clara")
        assert artifact_type == "character_arc"
        assert unique_id == "clara"

    def test_split_id_invalid(self):
        """Test that splitting invalid IDs raises error."""
        with pytest.raises(ValueError, match="Invalid ID format"):
            IdFormat.split_id("InvalidID")

    def test_make_id_simple(self):
        """Test constructing simple IDs."""
        artifact_id = IdFormat.make_id("chapter", "07")
        assert artifact_id == "chapter_07"

    def test_make_id_compound_type(self):
        """Test constructing IDs with compound artifact types."""
        artifact_id = IdFormat.make_id("character_arc", "clara")
        assert artifact_id == "character_arc_clara"

    def test_make_id_invalid_type(self):
        """Test that make_id rejects invalid artifact types."""
        with pytest.raises(ValueError, match="lowercase letters and underscores"):
            IdFormat.make_id("Chapter", "01")

    def test_make_id_invalid_unique_id(self):
        """Test that make_id rejects invalid unique IDs."""
        with pytest.raises(ValueError, match="lowercase letters, numbers, and underscores"):
            IdFormat.make_id("chapter", "07-extra")


class TestReferenceValidation:
    """Test Reference base model validation."""

    def test_reference_creation_minimal(self):
        """Test creating a reference with minimal required fields."""
        ref = Reference(
            source_id="chapter_01",
            target_id="chapter_02",
            reference_type=ReferenceType.CHAPTER_TO_PARENT,
        )

        assert ref.source_id == "chapter_01"
        assert ref.target_id == "chapter_02"
        assert ref.reference_type == ReferenceType.CHAPTER_TO_PARENT
        assert ref.optional is False
        assert ref.context is None

    def test_reference_creation_with_context(self):
        """Test creating a reference with context."""
        ref = Reference(
            source_id="chapter_03",
            target_id="chapter_01",
            reference_type=ReferenceType.PAYOFF_TO_SETUP,
            context="Clara's distrust planted in ch1, deepens in ch3",
        )

        assert ref.context == "Clara's distrust planted in ch1, deepens in ch3"

    def test_reference_invalid_source_id(self):
        """Test that invalid source_id raises validation error."""
        with pytest.raises(ValueError, match="source_id must follow format"):
            Reference(
                source_id="InvalidID",
                target_id="chapter_02",
                reference_type=ReferenceType.CHAPTER_TO_PARENT,
            )

    def test_reference_invalid_target_id(self):
        """Test that invalid target_id raises validation error."""
        with pytest.raises(ValueError, match="target_id must follow format"):
            Reference(
                source_id="chapter_01",
                target_id="InvalidID",
                reference_type=ReferenceType.CHAPTER_TO_PARENT,
            )

    def test_reference_optional_without_target(self):
        """Test creating an optional reference without target."""
        ref = Reference(
            source_id="chapter_01",
            target_id=None,
            reference_type=ReferenceType.SETUP_TO_PAYOFF,
            optional=True,
        )

        assert ref.target_id is None
        assert ref.optional is True

    def test_reference_required_without_target_fails(self):
        """Test that a required reference without target is still created but invalid."""
        ref = Reference(
            source_id="chapter_01",
            target_id=None,
            reference_type=ReferenceType.CHAPTER_TO_PARENT,
            optional=False,
        )

        # Model can be created, but validation fails
        is_valid, error = ref.validate_resolution()
        assert not is_valid
        assert "no target" in error

    def test_reference_is_resolved(self):
        """Test is_resolved() method."""
        ref_resolved = Reference(
            source_id="chapter_01",
            target_id="chapter_02",
            reference_type=ReferenceType.CHAPTER_TO_PARENT,
        )

        ref_unresolved = Reference(
            source_id="chapter_01",
            target_id=None,
            reference_type=ReferenceType.SETUP_TO_PAYOFF,
            optional=True,
        )

        assert ref_resolved.is_resolved() is True
        assert ref_unresolved.is_resolved() is False

    def test_reference_can_be_unresolved(self):
        """Test can_be_unresolved() method."""
        # Optional reference can be unresolved
        ref_optional = Reference(
            source_id="chapter_01",
            target_id=None,
            reference_type=ReferenceType.SETUP_TO_PAYOFF,
            optional=True,
        )

        assert ref_optional.can_be_unresolved() is True

        # Required reference cannot be unresolved
        ref_required = Reference(
            source_id="chapter_01",
            target_id=None,
            reference_type=ReferenceType.CHAPTER_TO_PARENT,
            optional=False,
        )

        assert ref_required.can_be_unresolved() is False

        # Any reference can be unresolved if it has a target
        ref_resolved = Reference(
            source_id="chapter_01",
            target_id="chapter_02",
            reference_type=ReferenceType.CHAPTER_TO_PARENT,
        )

        assert ref_resolved.can_be_unresolved() is True


class TestArcReference:
    """Test ArcReference specific behavior."""

    def test_arc_reference_creation(self):
        """Test creating an ArcReference."""
        ref = ArcReference(
            source_id="character_arc_clara",
            target_id="chapter_02",
        )

        assert ref.source_id == "character_arc_clara"
        assert ref.target_id == "chapter_02"
        assert ref.reference_type == ReferenceType.ARC_TO_CHAPTER
        assert ref.optional is False

    def test_arc_reference_cannot_be_optional(self):
        """Test that arc references must be required."""
        with pytest.raises(ValueError, match="must be required"):
            ArcReference(
                source_id="character_arc_clara",
                target_id="chapter_02",
                optional=True,
            )


class TestChapterReference:
    """Test ChapterReference specific behavior."""

    def test_chapter_reference_creation(self):
        """Test creating a ChapterReference."""
        ref = ChapterReference(
            source_id="chapter_03",
            target_id="sequence_02",
        )

        assert ref.source_id == "chapter_03"
        assert ref.target_id == "sequence_02"
        assert ref.reference_type == ReferenceType.CHAPTER_TO_PARENT
        assert ref.optional is False

    def test_chapter_reference_cannot_be_optional(self):
        """Test that chapter references must be required."""
        with pytest.raises(ValueError, match="must be required"):
            ChapterReference(
                source_id="chapter_03",
                target_id="sequence_02",
                optional=True,
            )


class TestBeatReference:
    """Test BeatReference specific behavior."""

    def test_beat_reference_creation(self):
        """Test creating a BeatReference."""
        ref = BeatReference(
            source_id="turning_point_clara_distrust",
            target_id="chapter_05",
        )

        assert ref.source_id == "turning_point_clara_distrust"
        assert ref.target_id == "chapter_05"
        assert ref.reference_type == ReferenceType.ARC_BEAT_TO_CHAPTER
        assert ref.optional is False

    def test_beat_reference_cannot_be_optional(self):
        """Test that beat references must be required."""
        with pytest.raises(ValueError, match="must be required"):
            BeatReference(
                source_id="turning_point_clara_distrust",
                target_id="chapter_05",
                optional=True,
            )


class TestPayoffReference:
    """Test PayoffReference specific behavior."""

    def test_payoff_reference_creation(self):
        """Test creating a PayoffReference."""
        ref = PayoffReference(
            source_id="chapter_15",
            target_id="chapter_03",
            context="Clara's distrust payoff",
        )

        assert ref.source_id == "chapter_15"
        assert ref.target_id == "chapter_03"
        assert ref.reference_type == ReferenceType.PAYOFF_TO_SETUP
        assert ref.optional is False

    def test_payoff_reference_cannot_be_optional(self):
        """Test that payoff references must be required."""
        with pytest.raises(ValueError, match="must be required"):
            PayoffReference(
                source_id="chapter_15",
                target_id="chapter_03",
                optional=True,
            )


class TestSetupReference:
    """Test SetupReference specific behavior."""

    def test_setup_reference_creation_optional_default(self):
        """Test that SetupReference defaults to optional."""
        ref = SetupReference(
            source_id="chapter_03",
            target_id="chapter_15",
        )

        assert ref.source_id == "chapter_03"
        assert ref.target_id == "chapter_15"
        assert ref.reference_type == ReferenceType.SETUP_TO_PAYOFF
        assert ref.optional is True

    def test_setup_reference_can_be_required(self):
        """Test that SetupReference can be explicitly required."""
        ref = SetupReference(
            source_id="chapter_03",
            target_id="chapter_15",
            optional=False,
        )

        assert ref.optional is False

    def test_setup_reference_can_be_unresolved(self):
        """Test that SetupReference can be created without target."""
        ref = SetupReference(
            source_id="chapter_03",
            target_id=None,
        )

        assert ref.target_id is None
        assert ref.optional is True
        assert ref.is_resolved() is False


class TestReferenceResolver:
    """Test reference resolution against artifact registry."""

    def test_resolver_artifact_exists(self):
        """Test checking if artifact exists in registry."""
        registry = {
            "chapter_01": {"type": "chapter"},
            "chapter_02": {"type": "chapter"},
            "book_001": {"type": "book"},
        }

        resolver = ReferenceResolver(registry)

        assert resolver.artifact_exists("chapter_01") is True
        assert resolver.artifact_exists("chapter_02") is True
        assert resolver.artifact_exists("book_001") is True
        assert resolver.artifact_exists("chapter_99") is False

    def test_resolver_get_artifact(self):
        """Test retrieving artifacts from registry."""
        chapter_01 = {"type": "chapter", "number": 1}
        registry = {"chapter_01": chapter_01}

        resolver = ReferenceResolver(registry)

        assert resolver.get_artifact("chapter_01") == chapter_01
        assert resolver.get_artifact("chapter_99") is None

    def test_resolver_resolve_valid_reference(self):
        """Test resolving a valid reference."""
        registry = {
            "chapter_01": {"type": "chapter"},
            "chapter_02": {"type": "chapter"},
        }

        resolver = ReferenceResolver(registry)
        ref = Reference(
            source_id="chapter_01",
            target_id="chapter_02",
            reference_type=ReferenceType.CHAPTER_TO_PARENT,
        )

        is_valid, error = resolver.resolve_reference(ref)
        assert is_valid is True
        assert error is None

    def test_resolver_resolve_broken_reference(self):
        """Test resolving a reference with non-existent target."""
        registry = {"chapter_01": {"type": "chapter"}}

        resolver = ReferenceResolver(registry)
        ref = Reference(
            source_id="chapter_01",
            target_id="chapter_99",
            reference_type=ReferenceType.CHAPTER_TO_PARENT,
        )

        is_valid, error = resolver.resolve_reference(ref)
        assert is_valid is False
        assert "not found" in error

    def test_resolver_resolve_optional_reference(self):
        """Test resolving an optional reference without target."""
        registry = {"chapter_01": {"type": "chapter"}}

        resolver = ReferenceResolver(registry)
        ref = Reference(
            source_id="chapter_01",
            target_id=None,
            reference_type=ReferenceType.SETUP_TO_PAYOFF,
            optional=True,
        )

        is_valid, error = resolver.resolve_reference(ref)
        assert is_valid is True
        assert error is None

    def test_resolver_resolve_multiple_references(self):
        """Test resolving multiple references at once."""
        registry = {
            "chapter_01": {"type": "chapter"},
            "chapter_02": {"type": "chapter"},
            "sequence_01": {"type": "sequence"},
        }

        resolver = ReferenceResolver(registry)

        refs = [
            Reference(
                source_id="chapter_01",
                target_id="sequence_01",
                reference_type=ReferenceType.CHAPTER_TO_PARENT,
            ),
            Reference(
                source_id="chapter_02",
                target_id="chapter_99",
                reference_type=ReferenceType.PAYOFF_TO_SETUP,
            ),
        ]

        all_valid, errors = resolver.resolve_references(refs)
        assert all_valid is False
        assert len(errors) == 1
        assert "chapter_99" in errors[0]


class TestReferenceGraph:
    """Test reference graph construction and analysis."""

    def test_graph_add_reference(self):
        """Test adding references to the graph."""
        graph = ReferenceGraph()

        ref1 = Reference(
            source_id="chapter_01",
            target_id="chapter_02",
            reference_type=ReferenceType.PAYOFF_TO_SETUP,
        )

        graph.add_reference(ref1)

        assert len(graph.references) == 1
        assert ref1 in graph.references

    def test_graph_get_outgoing(self):
        """Test retrieving outgoing references."""
        graph = ReferenceGraph()

        ref1 = Reference(
            source_id="chapter_01",
            target_id="chapter_02",
            reference_type=ReferenceType.PAYOFF_TO_SETUP,
        )

        ref2 = Reference(
            source_id="chapter_01",
            target_id="chapter_03",
            reference_type=ReferenceType.SETUP_TO_PAYOFF,
        )

        graph.add_reference(ref1)
        graph.add_reference(ref2)

        outgoing = graph.get_outgoing("chapter_01")
        assert len(outgoing) == 2
        assert ref1 in outgoing
        assert ref2 in outgoing

        # No outgoing references for chapter_02
        assert len(graph.get_outgoing("chapter_02")) == 0

    def test_graph_get_incoming(self):
        """Test retrieving incoming references."""
        graph = ReferenceGraph()

        ref1 = Reference(
            source_id="chapter_15",
            target_id="chapter_03",
            reference_type=ReferenceType.PAYOFF_TO_SETUP,
        )

        ref2 = Reference(
            source_id="chapter_20",
            target_id="chapter_03",
            reference_type=ReferenceType.PAYOFF_TO_SETUP,
        )

        graph.add_reference(ref1)
        graph.add_reference(ref2)

        incoming = graph.get_incoming("chapter_03")
        assert len(incoming) == 2
        assert ref1 in incoming
        assert ref2 in incoming

    def test_graph_get_references_by_type(self):
        """Test filtering references by type."""
        graph = ReferenceGraph()

        ref1 = Reference(
            source_id="chapter_01",
            target_id="chapter_02",
            reference_type=ReferenceType.PAYOFF_TO_SETUP,
        )

        ref2 = Reference(
            source_id="chapter_03",
            target_id="sequence_01",
            reference_type=ReferenceType.CHAPTER_TO_PARENT,
        )

        ref3 = Reference(
            source_id="chapter_05",
            target_id="chapter_04",
            reference_type=ReferenceType.PAYOFF_TO_SETUP,
        )

        graph.add_reference(ref1)
        graph.add_reference(ref2)
        graph.add_reference(ref3)

        payoff_refs = graph.get_references_by_type(ReferenceType.PAYOFF_TO_SETUP)
        assert len(payoff_refs) == 2
        assert ref1 in payoff_refs
        assert ref3 in payoff_refs

        parent_refs = graph.get_references_by_type(ReferenceType.CHAPTER_TO_PARENT)
        assert len(parent_refs) == 1
        assert ref2 in parent_refs

    def test_graph_complex_structure(self):
        """Test graph with complex reference structure."""
        graph = ReferenceGraph()

        # Build a more complex reference structure
        # Book contains sequences
        graph.add_reference(
            Reference(
                source_id="book_001",
                target_id="sequence_01",
                reference_type=ReferenceType.BOOK_TO_SEQUENCE,
            )
        )

        # Sequence contains chapters
        graph.add_reference(
            Reference(
                source_id="sequence_01",
                target_id="chapter_01",
                reference_type=ReferenceType.SEQUENCE_TO_CHAPTER,
            )
        )

        graph.add_reference(
            Reference(
                source_id="sequence_01",
                target_id="chapter_02",
                reference_type=ReferenceType.SEQUENCE_TO_CHAPTER,
            )
        )

        # Arc spans chapters
        graph.add_reference(
            ArcReference(
                source_id="character_arc_clara",
                target_id="chapter_01",
            )
        )

        # Setup/payoff relationship
        graph.add_reference(
            PayoffReference(
                source_id="chapter_02",
                target_id="chapter_01",
            )
        )

        # Verify structure
        assert len(graph.references) == 5

        book_outgoing = graph.get_outgoing("book_001")
        assert len(book_outgoing) == 1

        sequence_outgoing = graph.get_outgoing("sequence_01")
        assert len(sequence_outgoing) == 2

        chapter_01_incoming = graph.get_incoming("chapter_01")
        assert len(chapter_01_incoming) == 3  # sequence, arc, payoff

        chapter_02_incoming = graph.get_incoming("chapter_02")
        assert len(chapter_02_incoming) == 1  # sequence


class TestReferenceIntegration:
    """Integration tests combining reference system components."""

    def test_complete_reference_validation_workflow(self):
        """Test complete workflow: create references, build graph, resolve against registry."""
        # Build artifact registry
        registry = {
            "book_001": {"type": "book"},
            "sequence_01": {"type": "sequence"},
            "chapter_01": {"type": "chapter"},
            "chapter_02": {"type": "chapter"},
            "character_arc_clara": {"type": "character_arc"},
        }

        # Create references
        refs = [
            Reference(
                source_id="book_001",
                target_id="sequence_01",
                reference_type=ReferenceType.BOOK_TO_SEQUENCE,
            ),
            Reference(
                source_id="sequence_01",
                target_id="chapter_01",
                reference_type=ReferenceType.SEQUENCE_TO_CHAPTER,
            ),
            ArcReference(
                source_id="character_arc_clara",
                target_id="chapter_02",
            ),
            PayoffReference(
                source_id="chapter_02",
                target_id="chapter_01",
            ),
        ]

        # Build graph
        graph = ReferenceGraph()
        for ref in refs:
            graph.add_reference(ref)

        # Resolve references
        resolver = ReferenceResolver(registry)
        all_valid, errors = resolver.resolve_references(refs)

        assert all_valid is True
        assert len(errors) == 0

    def test_broken_reference_detection(self):
        """Test detection of broken references."""
        registry = {
            "chapter_01": {"type": "chapter"},
        }

        refs = [
            Reference(
                source_id="chapter_01",
                target_id="chapter_99",
                reference_type=ReferenceType.PAYOFF_TO_SETUP,
            ),
        ]

        resolver = ReferenceResolver(registry)
        all_valid, errors = resolver.resolve_references(refs)

        assert all_valid is False
        assert len(errors) == 1
        assert "chapter_99" in errors[0]
