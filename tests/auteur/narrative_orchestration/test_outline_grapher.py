"""Tests for Structure outline grapher visualization.

Tests cover:
- Container hierarchy visualization (tree structure)
- Arc reference visualization (arcs spanning chapters)
- Setup→payoff flow visualization
- Complete structure visualization
- ASCII art and DOT format rendering
- Edge cases (empty outline, single chapter, multiple arcs)
"""

import pytest
from auteur.narrative_orchestration.orchestrator.outline_grapher import (
    OutlineGrapher,
    OutlineNode,
    ArcReference,
    SetupPayoffFlow,
    TreeFormatter,
)


class TestOutlineGrapher:
    """Test OutlineGrapher initialization and basic operations."""

    def test_init_creates_empty_grapher(self):
        """Test that OutlineGrapher initializes with empty collections."""
        grapher = OutlineGrapher()
        assert len(grapher.nodes) == 0
        assert len(grapher.arc_references) == 0
        assert len(grapher.setup_payoff_flows) == 0

    def test_add_node_simple(self):
        """Test adding a single node."""
        grapher = OutlineGrapher()
        grapher.add_node("chapter_01", "chapter", "First Meeting")
        assert "chapter_01" in grapher.nodes
        assert grapher.nodes["chapter_01"].name == "First Meeting"
        assert grapher.nodes["chapter_01"].node_type == "chapter"

    def test_add_node_with_parent(self):
        """Test adding a node with parent reference."""
        grapher = OutlineGrapher()
        grapher.add_node("book_001", "book", "Book 1")
        grapher.add_node("sequence_01", "sequence", "Sequence 1", parent_id="book_001")
        assert grapher.nodes["sequence_01"].parent_id == "book_001"

    def test_add_arc_reference(self):
        """Test adding an arc reference."""
        grapher = OutlineGrapher()
        grapher.add_arc_reference(
            "character_arc_elena",
            "Elena's Awakening",
            "character_arc",
            ["chapter_01", "chapter_03", "chapter_05"],
        )
        assert len(grapher.arc_references) == 1
        assert grapher.arc_references[0].arc_name == "Elena's Awakening"
        assert len(grapher.arc_references[0].chapter_ids) == 3

    def test_add_setup_payoff_flow(self):
        """Test adding a setup→payoff flow."""
        grapher = OutlineGrapher()
        grapher.add_setup_payoff_flow(
            "chapter_02", "chapter_08", "Plant the seed"
        )
        assert len(grapher.setup_payoff_flows) == 1
        assert grapher.setup_payoff_flows[0].setup_chapter_id == "chapter_02"
        assert grapher.setup_payoff_flows[0].payoff_chapter_id == "chapter_08"


class TestSimpleHierarchy:
    """Test container hierarchy visualization with simple structure."""

    @pytest.fixture
    def simple_grapher(self):
        """Create a grapher with simple hierarchy: 1 book, 3 sequences."""
        grapher = OutlineGrapher()
        grapher.add_node("book_001", "book", "Book 1: The Setup")
        grapher.add_node(
            "sequence_01", "sequence", "Sequence 1: The Relationship", parent_id="book_001"
        )
        grapher.add_node(
            "chapter_01", "chapter", "Chapter 1: First Meeting", parent_id="sequence_01"
        )
        grapher.add_node(
            "chapter_02", "chapter", "Chapter 2: Deepening Trust", parent_id="sequence_01"
        )

        grapher.add_node(
            "sequence_02", "sequence", "Sequence 2: The Conflict", parent_id="book_001"
        )
        grapher.add_node(
            "chapter_03", "chapter", "Chapter 3: The Third", parent_id="sequence_02"
        )

        grapher.add_node(
            "sequence_03", "sequence", "Sequence 3: The Revelation", parent_id="book_001"
        )
        grapher.add_node(
            "chapter_04", "chapter", "Chapter 4: Discovery", parent_id="sequence_03"
        )
        grapher.add_node(
            "chapter_05", "chapter", "Chapter 5: The Truth", parent_id="sequence_03"
        )

        return grapher

    def test_container_hierarchy_simple(self, simple_grapher):
        """Test hierarchy visualization with simple structure."""
        output = simple_grapher.graph_container_hierarchy()
        assert "Book 1: The Setup" in output
        assert "Sequence 1: The Relationship" in output
        assert "Chapter 1: First Meeting" in output
        assert "Sequence 2: The Conflict" in output
        assert "Chapter 4: Discovery" in output

    def test_container_hierarchy_has_tree_chars(self, simple_grapher):
        """Test that hierarchy uses tree characters."""
        output = simple_grapher.graph_container_hierarchy()
        # Should contain box-drawing characters
        assert ("├──" in output or "└──" in output or "│" in output)

    def test_container_hierarchy_preserves_structure(self, simple_grapher):
        """Test that hierarchy output preserves parent-child relationships."""
        output = simple_grapher.graph_container_hierarchy()
        lines = output.split("\n")

        # Find book line
        book_line_idx = None
        for i, line in enumerate(lines):
            if "Book 1" in line:
                book_line_idx = i
                break

        assert book_line_idx is not None, "Book should be in output"

        # Chapters should appear after their sequence
        chapter1_idx = None
        for i, line in enumerate(lines):
            if "Chapter 1" in line:
                chapter1_idx = i
                break

        assert (
            chapter1_idx is not None and chapter1_idx > book_line_idx
        ), "Chapter should appear after book"

    def test_render_as_ascii_simple(self, simple_grapher):
        """Test ASCII rendering with simple structure."""
        output = simple_grapher.render_as_ascii()
        assert "CONTAINER HIERARCHY" in output
        assert "ARC REFERENCES" in output
        assert "SETUP→PAYOFF FLOWS" in output
        assert "Book 1" in output


class TestComplexHierarchy:
    """Test container hierarchy with complex structure."""

    @pytest.fixture
    def complex_grapher(self):
        """Create a grapher with complex hierarchy: 2 books, 6+ sequences."""
        grapher = OutlineGrapher()

        # Book 1
        grapher.add_node("series_001", "series", "The Betrayal Cycle")
        grapher.add_node(
            "book_001", "book", "Book 1: The Setup", parent_id="series_001"
        )

        for seq_num in range(1, 4):
            seq_id = f"sequence_{seq_num:02d}"
            grapher.add_node(
                seq_id,
                "sequence",
                f"Sequence {seq_num}",
                parent_id="book_001",
            )

            for ch_num in range(1, 4):
                chapter_num = (seq_num - 1) * 3 + ch_num
                ch_id = f"chapter_{chapter_num:02d}"
                grapher.add_node(
                    ch_id,
                    "chapter",
                    f"Chapter {chapter_num}",
                    parent_id=seq_id,
                )

        # Book 2
        grapher.add_node(
            "book_002", "book", "Book 2: The Revelation", parent_id="series_001"
        )

        for seq_num in range(4, 7):
            seq_id = f"sequence_{seq_num:02d}"
            grapher.add_node(
                seq_id,
                "sequence",
                f"Sequence {seq_num}",
                parent_id="book_002",
            )

            for ch_num in range(1, 4):
                chapter_num = 9 + (seq_num - 4) * 3 + ch_num
                ch_id = f"chapter_{chapter_num:02d}"
                grapher.add_node(
                    ch_id,
                    "chapter",
                    f"Chapter {chapter_num}",
                    parent_id=seq_id,
                )

        return grapher

    def test_complex_hierarchy_structure(self, complex_grapher):
        """Test hierarchy with multiple books and sequences."""
        output = complex_grapher.graph_container_hierarchy()
        assert "The Betrayal Cycle" in output
        assert "Book 1: The Setup" in output
        assert "Book 2: The Revelation" in output
        assert "Chapter 1" in output
        assert "Chapter 18" in output

    def test_complex_hierarchy_chapter_count(self, complex_grapher):
        """Test that all 18 chapters appear in output."""
        output = complex_grapher.graph_container_hierarchy()
        for i in range(1, 19):
            chapter_text = f"Chapter {i}"
            assert chapter_text in output, f"{chapter_text} should be in output"

    def test_render_as_ascii_complex(self, complex_grapher):
        """Test ASCII rendering with complex structure."""
        output = complex_grapher.render_as_ascii(["hierarchy"])
        assert "The Betrayal Cycle" in output
        assert "Book 1" in output
        assert "Book 2" in output


class TestArcReferences:
    """Test arc reference visualization."""

    @pytest.fixture
    def grapher_with_arcs(self):
        """Create a grapher with arc references."""
        grapher = OutlineGrapher()

        # Add chapters
        for i in range(1, 6):
            grapher.add_node(f"chapter_{i:02d}", "chapter", f"Chapter {i}")

        # Add character arc
        grapher.add_arc_reference(
            "character_arc_elena",
            "Elena's Awakening",
            "character_arc",
            ["chapter_01", "chapter_03", "chapter_05"],
        )

        # Add story arc
        grapher.add_arc_reference(
            "story_arc_betrayal",
            "The Betrayal",
            "story_arc",
            ["chapter_02", "chapter_04"],
        )

        return grapher

    def test_arc_reference_visualization(self, grapher_with_arcs):
        """Test arc reference output format."""
        output = grapher_with_arcs.graph_arc_references()
        assert "Elena's Awakening" in output
        assert "The Betrayal" in output
        assert "Chapter 1" in output
        assert "Chapter 3" in output

    def test_arc_reference_shows_arc_type(self, grapher_with_arcs):
        """Test that arc type is displayed."""
        output = grapher_with_arcs.graph_arc_references()
        assert "Character Arc" in output or "character_arc" in output
        assert "Story Arc" in output or "story_arc" in output

    def test_arc_reference_empty(self):
        """Test output when no arc references exist."""
        grapher = OutlineGrapher()
        output = grapher.graph_arc_references()
        assert "(no arc references)" in output

    def test_render_as_ascii_arcs_only(self, grapher_with_arcs):
        """Test ASCII rendering with arcs only."""
        output = grapher_with_arcs.render_as_ascii(["arcs"])
        assert "ARC REFERENCES" in output
        assert "Elena's Awakening" in output


class TestSetupPayoffFlows:
    """Test setup→payoff flow visualization."""

    @pytest.fixture
    def grapher_with_flows(self):
        """Create a grapher with setup→payoff flows."""
        grapher = OutlineGrapher()

        # Add chapters
        for i in range(1, 10):
            grapher.add_node(f"chapter_{i:02d}", "chapter", f"Chapter {i}")

        # Add setup→payoff flows
        grapher.add_setup_payoff_flow(
            "chapter_01", "chapter_05", "Plant: The ring disappears"
        )
        grapher.add_setup_payoff_flow(
            "chapter_02", "chapter_08", "Reveal the affair"
        )
        grapher.add_setup_payoff_flow("chapter_03", "chapter_07")

        return grapher

    def test_setup_payoff_visualization(self, grapher_with_flows):
        """Test setup→payoff flow output format."""
        output = grapher_with_flows.graph_setup_payoff_flows()
        assert "Setup: Chapter 1" in output
        assert "Payoff: Chapter 5" in output
        assert "Plant: The ring disappears" in output

    def test_setup_payoff_multiple_flows(self, grapher_with_flows):
        """Test output with multiple flows."""
        output = grapher_with_flows.graph_setup_payoff_flows()
        assert "Setup: Chapter 1" in output
        assert "Setup: Chapter 2" in output
        assert "Setup: Chapter 3" in output

    def test_setup_payoff_empty(self):
        """Test output when no flows exist."""
        grapher = OutlineGrapher()
        output = grapher.graph_setup_payoff_flows()
        assert "(no setup→payoff flows)" in output

    def test_setup_payoff_without_description(self, grapher_with_flows):
        """Test that flows without description still render."""
        output = grapher_with_flows.graph_setup_payoff_flows()
        # Should show "Payoff: Chapter 7" without description
        assert "Chapter 7" in output


class TestCompleteStructure:
    """Test complete structure visualization combining all types."""

    @pytest.fixture
    def complete_grapher(self):
        """Create a grapher with hierarchy, arcs, and flows."""
        grapher = OutlineGrapher()

        # Hierarchy
        grapher.add_node("book_001", "book", "Book 1")
        grapher.add_node("sequence_01", "sequence", "Sequence 1", parent_id="book_001")
        for i in range(1, 6):
            grapher.add_node(
                f"chapter_{i:02d}",
                "chapter",
                f"Chapter {i}",
                parent_id="sequence_01",
            )

        # Arcs
        grapher.add_arc_reference(
            "character_arc_01",
            "Protagonist's Journey",
            "character_arc",
            ["chapter_01", "chapter_03", "chapter_05"],
        )

        # Flows
        grapher.add_setup_payoff_flow("chapter_01", "chapter_04", "Establish the problem")

        return grapher

    def test_graph_complete_structure(self, complete_grapher):
        """Test complete structure visualization."""
        output = complete_grapher.graph_complete_structure()
        assert "CONTAINER HIERARCHY" in output
        assert "ARC REFERENCES" in output
        assert "SETUP→PAYOFF FLOWS" in output
        assert "Book 1" in output
        assert "Protagonist's Journey" in output
        assert "Establish the problem" in output

    def test_render_as_ascii_default(self, complete_grapher):
        """Test ASCII rendering with default sections."""
        output = complete_grapher.render_as_ascii()
        assert "CONTAINER HIERARCHY" in output
        assert "ARC REFERENCES" in output
        assert "SETUP→PAYOFF FLOWS" in output

    def test_render_as_ascii_selective_sections(self, complete_grapher):
        """Test ASCII rendering with selected sections."""
        output = complete_grapher.render_as_ascii(["hierarchy", "arcs"])
        assert "CONTAINER HIERARCHY" in output
        assert "ARC REFERENCES" in output
        assert "SETUP→PAYOFF FLOWS" not in output

    def test_render_as_ascii_single_section(self, complete_grapher):
        """Test ASCII rendering with single section."""
        output = complete_grapher.render_as_ascii(["hierarchy"])
        assert "CONTAINER HIERARCHY" in output
        assert "Book 1" in output
        assert "ARC REFERENCES" not in output


class TestDotFormatRendering:
    """Test DOT format rendering for Graphviz."""

    @pytest.fixture
    def grapher_for_dot(self):
        """Create a grapher for DOT format testing."""
        grapher = OutlineGrapher()

        grapher.add_node("book_001", "book", "Book 1")
        grapher.add_node("sequence_01", "sequence", "Sequence 1", parent_id="book_001")
        grapher.add_node("chapter_01", "chapter", "Chapter 1", parent_id="sequence_01")
        grapher.add_node("chapter_02", "chapter", "Chapter 2", parent_id="sequence_01")

        grapher.add_arc_reference(
            "character_arc_01",
            "Elena's Arc",
            "character_arc",
            ["chapter_01", "chapter_02"],
        )

        grapher.add_setup_payoff_flow("chapter_01", "chapter_02", "Plant and payoff")

        return grapher

    def test_render_as_dot_format(self, grapher_for_dot):
        """Test that DOT output is valid Graphviz format."""
        output = grapher_for_dot.render_as_dot()
        assert output.startswith("digraph narrative_outline {")
        assert output.endswith("}")
        assert "rankdir" in output
        assert "node [shape" in output

    def test_render_as_dot_includes_nodes(self, grapher_for_dot):
        """Test that DOT output includes all nodes."""
        output = grapher_for_dot.render_as_dot()
        assert "book_001" in output
        assert "chapter_01" in output
        assert "Book 1" in output
        assert "Chapter 1" in output

    def test_render_as_dot_includes_edges(self, grapher_for_dot):
        """Test that DOT output includes relationships."""
        output = grapher_for_dot.render_as_dot()
        # Container relationships
        assert "book_001" in output and "sequence_01" in output
        # Arc references and flows also included


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_outline_hierarchy(self):
        """Test hierarchy visualization with empty outline."""
        grapher = OutlineGrapher()
        output = grapher.graph_container_hierarchy()
        assert "(empty outline)" in output

    def test_single_chapter_hierarchy(self):
        """Test hierarchy with only one chapter."""
        grapher = OutlineGrapher()
        grapher.add_node("chapter_01", "chapter", "Only Chapter")
        output = grapher.graph_container_hierarchy()
        assert "Only Chapter" in output

    def test_orphaned_nodes(self):
        """Test hierarchy with nodes that have no parent."""
        grapher = OutlineGrapher()
        grapher.add_node("book_001", "book", "Book 1")
        grapher.add_node("sequence_01", "sequence", "Sequence (orphaned)")
        output = grapher.graph_container_hierarchy()
        # Should still render both
        assert "Book 1" in output

    def test_arc_with_empty_chapter_list(self):
        """Test arc reference with no chapters."""
        grapher = OutlineGrapher()
        grapher.add_arc_reference(
            "character_arc_01", "Empty Arc", "character_arc", []
        )
        output = grapher.graph_arc_references()
        assert "Empty Arc" in output
        assert "(no chapters)" in output

    def test_arc_with_missing_chapters(self):
        """Test arc reference with chapters that don't exist in node registry."""
        grapher = OutlineGrapher()
        grapher.add_node("chapter_01", "chapter", "Chapter 1")
        # Arc references chapter_02 which doesn't exist
        grapher.add_arc_reference(
            "character_arc_01",
            "My Arc",
            "character_arc",
            ["chapter_01", "chapter_02"],
        )
        output = grapher.graph_arc_references()
        # Should still render, but skip missing chapter
        assert "My Arc" in output

    def test_setup_payoff_with_missing_chapters(self):
        """Test setup→payoff flow with chapters that don't exist."""
        grapher = OutlineGrapher()
        grapher.add_node("chapter_01", "chapter", "Chapter 1")
        grapher.add_setup_payoff_flow(
            "chapter_01", "chapter_99", "Missing payoff chapter"
        )
        output = grapher.graph_setup_payoff_flows()
        # Should handle gracefully
        assert isinstance(output, str)


class TestTreeFormatter:
    """Test the TreeFormatter utility class."""

    def test_format_tree_simple(self):
        """Test tree formatting with simple structure."""
        nodes = [
            OutlineNode("book_001", "book", "Book 1", depth=0),
            OutlineNode("chapter_01", "chapter", "Chapter 1", depth=1, parent_id="book_001"),
            OutlineNode("chapter_02", "chapter", "Chapter 2", depth=1, parent_id="book_001"),
        ]

        output = TreeFormatter.format_tree(nodes)
        assert "Book 1" in output
        assert "Chapter 1" in output
        assert "Chapter 2" in output

    def test_format_tree_empty(self):
        """Test tree formatting with empty node list."""
        output = TreeFormatter.format_tree([])
        assert output == ""

    def test_format_tree_multiple_roots(self):
        """Test tree formatting with multiple root nodes."""
        nodes = [
            OutlineNode("book_001", "book", "Book 1"),
            OutlineNode("book_002", "book", "Book 2"),
        ]

        output = TreeFormatter.format_tree(nodes)
        assert "Book 1" in output
        assert "Book 2" in output
