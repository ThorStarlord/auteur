"""Outline grapher for visualizing narrative structure relationships.

This module provides ASCII art visualization of outline relationships, showing:
- Container hierarchy (Series → Book → Sequence → Chapter as tree)
- Arc references (how arcs span and reference chapters)
- Setup→payoff flows (narrative cause-effect chains)
- Complete structure (combining all visualizations)

Visualizations are suitable for terminal display and documentation.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class OutlineNode:
    """Represents a single node in the outline structure.

    Attributes:
        node_id: Unique identifier (e.g., "chapter_07", "book_001")
        node_type: Type of node (series, book, sequence, chapter, arc)
        name: Display name (title, name, etc.)
        depth: Nesting depth for tree visualization
        parent_id: Parent container ID (for hierarchy)
    """

    node_id: str
    node_type: str
    name: str
    depth: int = 0
    parent_id: Optional[str] = None


@dataclass
class ArcReference:
    """Represents a reference from an arc to chapters it spans.

    Attributes:
        arc_id: Arc identifier
        arc_name: Display name of the arc
        arc_type: Type of arc (character_arc, story_arc, theme_arc)
        chapter_ids: List of chapter IDs this arc references
    """

    arc_id: str
    arc_name: str
    arc_type: str
    chapter_ids: List[str]


@dataclass
class SetupPayoffFlow:
    """Represents a setup→payoff narrative relationship.

    Attributes:
        setup_chapter_id: Chapter ID where setup occurs
        payoff_chapter_id: Chapter ID where payoff occurs
        description: Optional description of the relationship
    """

    setup_chapter_id: str
    payoff_chapter_id: str
    description: Optional[str] = None


class TreeFormatter:
    """Formats tree structures with ASCII art (box-drawing characters)."""

    # Box-drawing characters for tree structure
    BRANCH = "├── "
    LAST_BRANCH = "└── "
    VERTICAL = "│   "
    SPACE = "    "

    @staticmethod
    def format_tree(
        nodes: List[OutlineNode], root_id: Optional[str] = None
    ) -> str:
        """Format a tree of nodes as ASCII art.

        Args:
            nodes: List of nodes to format (should be sorted by tree order)
            root_id: ID of root node (optional, for filtering)

        Returns:
            String containing ASCII art tree
        """
        if not nodes:
            return ""

        lines = []
        # Build a map of parent → children for efficient traversal
        children_map: Dict[Optional[str], List[OutlineNode]] = {}
        for node in nodes:
            parent = node.parent_id
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(node)

        # Find root nodes (nodes with no parent, or specified root)
        if root_id:
            root_nodes = [n for n in nodes if n.node_id == root_id]
        else:
            root_nodes = [n for n in nodes if n.parent_id is None]

        def format_subtree(
            node: OutlineNode, prefix: str = "", is_last: bool = True
        ) -> List[str]:
            """Recursively format a subtree.

            Args:
                node: Node to format
                prefix: Prefix for this line
                is_last: Whether this is the last child of parent

            Returns:
                List of formatted lines
            """
            result = []

            # Format current node
            connector = TreeFormatter.LAST_BRANCH if is_last else TreeFormatter.BRANCH
            result.append(f"{prefix}{connector}{node.name}")

            # Format children
            children = children_map.get(node.node_id, [])
            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                next_prefix = prefix + (
                    TreeFormatter.SPACE if is_last else TreeFormatter.VERTICAL
                )
                result.extend(format_subtree(child, next_prefix, is_last_child))

            return result

        # Format all root nodes
        for i, root in enumerate(root_nodes):
            if i > 0:
                lines.append("")  # Blank line between roots
            if len(root_nodes) > 1 or root.parent_id is not None:
                # If multiple roots or explicit root, show it
                lines.append(root.name)
                children = children_map.get(root.node_id, [])
                for j, child in enumerate(children):
                    is_last = j == len(children) - 1
                    lines.extend(format_subtree(child, "", is_last))
            else:
                # Single root, no explicit prefix
                children = children_map.get(root.node_id, [])
                if children:
                    lines.append(root.name)
                    for j, child in enumerate(children):
                        is_last = j == len(children) - 1
                        lines.extend(format_subtree(child, "", is_last))
                else:
                    lines.append(root.name)

        return "\n".join(lines)


class OutlineGrapher:
    """Visualizes outline relationships in ASCII art format.

    Accepts complete outline artifacts and produces various visualizations
    of container hierarchy, arc references, and setup→payoff flows.

    Attributes:
        nodes: Dictionary mapping node_id → OutlineNode
        arc_references: List of arc references
        setup_payoff_flows: List of setup→payoff relationships
    """

    def __init__(self):
        """Initialize an empty outline grapher."""
        self.nodes: Dict[str, OutlineNode] = {}
        self.arc_references: List[ArcReference] = []
        self.setup_payoff_flows: List[SetupPayoffFlow] = []

    def add_node(
        self,
        node_id: str,
        node_type: str,
        name: str,
        parent_id: Optional[str] = None,
    ) -> None:
        """Add a node to the outline.

        Args:
            node_id: Unique identifier for this node
            node_type: Type of node (series, book, sequence, chapter, etc.)
            name: Display name
            parent_id: Optional parent container ID
        """
        # Calculate depth based on type
        depth = self._calculate_depth(node_type)
        self.nodes[node_id] = OutlineNode(
            node_id=node_id, node_type=node_type, name=name, depth=depth, parent_id=parent_id
        )

    def add_arc_reference(
        self,
        arc_id: str,
        arc_name: str,
        arc_type: str,
        chapter_ids: List[str],
    ) -> None:
        """Add an arc reference spanning multiple chapters.

        Args:
            arc_id: Unique identifier for the arc
            arc_name: Display name of the arc
            arc_type: Type (character_arc, story_arc, theme_arc)
            chapter_ids: List of chapter IDs this arc references
        """
        self.arc_references.append(
            ArcReference(
                arc_id=arc_id,
                arc_name=arc_name,
                arc_type=arc_type,
                chapter_ids=chapter_ids,
            )
        )

    def add_setup_payoff_flow(
        self,
        setup_chapter_id: str,
        payoff_chapter_id: str,
        description: Optional[str] = None,
    ) -> None:
        """Add a setup→payoff narrative relationship.

        Args:
            setup_chapter_id: Chapter where setup occurs
            payoff_chapter_id: Chapter where payoff occurs
            description: Optional description of the relationship
        """
        self.setup_payoff_flows.append(
            SetupPayoffFlow(
                setup_chapter_id=setup_chapter_id,
                payoff_chapter_id=payoff_chapter_id,
                description=description,
            )
        )

    def graph_container_hierarchy(self, root_id: Optional[str] = None) -> str:
        """Generate tree visualization of container hierarchy.

        Shows Series → Book → Sequence → Chapter relationships as a tree.

        Args:
            root_id: Optional root node ID (defaults to all roots)

        Returns:
            ASCII art tree visualization
        """
        if not self.nodes:
            return "(empty outline)"

        # Filter to container nodes only
        container_types = {"series", "book", "sequence", "chapter"}
        container_nodes = [
            node
            for node in self.nodes.values()
            if node.node_type in container_types
        ]

        if not container_nodes:
            return "(no container nodes)"

        # Sort by tree order: root first, then children
        container_nodes = self._sort_by_tree_order(container_nodes)

        formatter = TreeFormatter()
        return formatter.format_tree(container_nodes, root_id)

    def graph_arc_references(self) -> str:
        """Generate visualization of arc→chapter references.

        Shows which arcs reference which chapters, with arc types indicated.

        Returns:
            ASCII art showing arc-to-chapter connections
        """
        if not self.arc_references:
            return "(no arc references)"

        lines = []

        for arc_ref in self.arc_references:
            arc_type_display = arc_ref.arc_type.replace("_", " ").title()
            lines.append(f"{arc_type_display}: {arc_ref.arc_name}")

            if arc_ref.chapter_ids:
                # Show chapters this arc references
                chapters = [
                    self.nodes.get(cid, None) for cid in arc_ref.chapter_ids
                ]
                chapters = [c for c in chapters if c is not None]
                chapters = sorted(chapters, key=lambda x: x.node_id)

                for i, chapter in enumerate(chapters):
                    is_last = i == len(chapters) - 1
                    prefix = "  └─→ " if is_last else "  ├─→ "
                    lines.append(f"{prefix}{chapter.name}")
            else:
                lines.append("  (no chapters)")

        return "\n".join(lines)

    def graph_setup_payoff_flows(self) -> str:
        """Generate visualization of setup→payoff narrative flows.

        Shows cause-effect chains where setups lead to payoffs.

        Returns:
            ASCII art showing setup→payoff connections
        """
        if not self.setup_payoff_flows:
            return "(no setup→payoff flows)"

        lines = []

        # Group flows by setup chapter
        flows_by_setup: Dict[str, List[SetupPayoffFlow]] = {}
        for flow in self.setup_payoff_flows:
            if flow.setup_chapter_id not in flows_by_setup:
                flows_by_setup[flow.setup_chapter_id] = []
            flows_by_setup[flow.setup_chapter_id].append(flow)

        # Sort by setup chapter order
        sorted_setups = sorted(flows_by_setup.keys())

        for setup_id in sorted_setups:
            setup_node = self.nodes.get(setup_id)
            if setup_node is None:
                continue

            lines.append(f"Setup: {setup_node.name}")

            flows = flows_by_setup[setup_id]
            for i, flow in enumerate(flows):
                is_last = i == len(flows) - 1
                payoff_node = self.nodes.get(flow.payoff_chapter_id)
                if payoff_node is None:
                    continue

                prefix = "  └→ " if is_last else "  ├→ "
                payoff_text = f"Payoff: {payoff_node.name}"
                if flow.description:
                    payoff_text += f" ({flow.description})"

                lines.append(f"{prefix}{payoff_text}")

        return "\n".join(lines)

    def graph_complete_structure(self, root_id: Optional[str] = None) -> str:
        """Generate complete visualization combining all structure types.

        Shows container hierarchy, arc references, and setup→payoff flows.

        Args:
            root_id: Optional root node ID for container hierarchy

        Returns:
            Complete ASCII art visualization with all components
        """
        sections = []

        # Container hierarchy
        hierarchy = self.graph_container_hierarchy(root_id)
        sections.append("CONTAINER HIERARCHY")
        sections.append("=" * 40)
        sections.append(hierarchy)
        sections.append("")

        # Arc references
        arcs = self.graph_arc_references()
        sections.append("ARC REFERENCES")
        sections.append("=" * 40)
        sections.append(arcs)
        sections.append("")

        # Setup→payoff flows
        flows = self.graph_setup_payoff_flows()
        sections.append("SETUP→PAYOFF FLOWS")
        sections.append("=" * 40)
        sections.append(flows)

        return "\n".join(sections)

    def render_as_ascii(
        self, include_sections: Optional[List[str]] = None
    ) -> str:
        """Render the complete outline as ASCII art suitable for terminal/docs.

        Args:
            include_sections: Optional list of sections to include
                ("hierarchy", "arcs", "flows"). Defaults to all.

        Returns:
            Complete ASCII art visualization
        """
        if include_sections is None:
            include_sections = ["hierarchy", "arcs", "flows"]

        sections = []

        if "hierarchy" in include_sections:
            hierarchy = self.graph_container_hierarchy()
            sections.append("CONTAINER HIERARCHY\n" + "=" * 40)
            sections.append(hierarchy)

        if "arcs" in include_sections:
            arcs = self.graph_arc_references()
            sections.append("ARC REFERENCES\n" + "=" * 40)
            sections.append(arcs)

        if "flows" in include_sections:
            flows = self.graph_setup_payoff_flows()
            sections.append("SETUP→PAYOFF FLOWS\n" + "=" * 40)
            sections.append(flows)

        return "\n\n".join(sections)

    def render_as_dot(self) -> str:
        """Render the outline as Graphviz DOT format.

        Useful for generating more sophisticated visualizations with
        graphviz tools.

        Returns:
            DOT format string (can be saved to .dot file)
        """
        lines = ["digraph narrative_outline {", '    rankdir="LR";']
        lines.append('    node [shape=box, style=rounded];')
        lines.append("")

        # Add all nodes
        for node_id, node in self.nodes.items():
            label = node.name.replace('"', '\\"')
            shape = self._get_dot_shape(node.node_type)
            lines.append(f'    "{node_id}" [label="{label}", shape={shape}];')

        lines.append("")

        # Add container relationships
        for node in self.nodes.values():
            if node.parent_id:
                lines.append(f'    "{node.parent_id}" -> "{node.node_id}";')

        lines.append("")

        # Add arc references (as dotted lines)
        for arc_ref in self.arc_references:
            for chapter_id in arc_ref.chapter_ids:
                lines.append(
                    f'    "{arc_ref.arc_id}" -> "{chapter_id}" '
                    '[style=dotted, color=blue];'
                )

        lines.append("")

        # Add setup→payoff flows (as dashed lines)
        for flow in self.setup_payoff_flows:
            lines.append(
                f'    "{flow.setup_chapter_id}" -> "{flow.payoff_chapter_id}" '
                '[style=dashed, color=green];'
            )

        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def _calculate_depth(node_type: str) -> int:
        """Calculate nesting depth based on node type.

        Args:
            node_type: Type of node

        Returns:
            Depth value (0 for series, 1 for book, etc.)
        """
        depth_map = {"series": 0, "book": 1, "sequence": 2, "chapter": 3}
        return depth_map.get(node_type, 4)

    @staticmethod
    def _get_dot_shape(node_type: str) -> str:
        """Get Graphviz DOT shape for node type.

        Args:
            node_type: Type of node

        Returns:
            DOT shape name
        """
        shape_map = {
            "series": "box3d",
            "book": "box",
            "sequence": "folder",
            "chapter": "note",
            "character_arc": "oval",
            "story_arc": "oval",
            "theme_arc": "oval",
        }
        return shape_map.get(node_type, "box")

    @staticmethod
    def _sort_by_tree_order(nodes: List[OutlineNode]) -> List[OutlineNode]:
        """Sort nodes in tree traversal order (depth-first).

        Args:
            nodes: Unsorted list of nodes

        Returns:
            List sorted in tree traversal order
        """
        # Build parent→children map
        children_map: Dict[Optional[str], List[OutlineNode]] = {}
        for node in nodes:
            parent = node.parent_id
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(node)

        # Sort children by node_id
        for children in children_map.values():
            children.sort(key=lambda x: x.node_id)

        # Depth-first traversal
        result = []

        def traverse(node_id: Optional[str]) -> None:
            """Recursively traverse from node."""
            for child in children_map.get(node_id, []):
                result.append(child)
                traverse(child.node_id)

        # Find roots and traverse
        roots = [n for n in nodes if n.parent_id is None]
        roots.sort(key=lambda x: x.node_id)
        for root in roots:
            result.append(root)
            traverse(root.node_id)

        return result
