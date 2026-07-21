"""Tests for DependencyGraph — construction, traversal, cycle detection, serialization."""

from __future__ import annotations

from auteur.impact.graph import DependencyGraph
from auteur.impact.models import ArtifactRef, DependencyEdge


class TestGraphConstruction:
    def test_empty_graph(self) -> None:
        g = DependencyGraph()
        assert g.nodes() == {}
        assert g.edges() == []
        assert g.missing_nodes() == []

    def test_add_node(self) -> None:
        g = DependencyGraph()
        ref = ArtifactRef(artifact_id="identity", artifact_type="story_identity")
        g.add_node(ref)
        assert g.has_node("identity")
        assert g.get_node("identity") == ref

    def test_add_edge(self) -> None:
        g = DependencyGraph()
        g.add_node(ArtifactRef(artifact_id="a"))
        g.add_node(ArtifactRef(artifact_id="b"))
        edge = g.add_edge("a", "b", kind="structural", rule_id="R001")
        assert edge.source_id == "a"
        assert edge.target_id == "b"
        assert edge.kind == "structural"
        assert edge.rule_id == "R001"

    def test_linear_graph(self) -> None:
        g = DependencyGraph()
        for aid in ("a", "b", "c"):
            g.add_node(ArtifactRef(artifact_id=aid))
        g.add_edge("a", "b")
        g.add_edge("b", "c")

        assert g.direct_dependent_ids("a") == ["b"]
        assert g.direct_dependent_ids("b") == ["c"]
        assert g.direct_dependent_ids("c") == []

        transitive = g.transitive_dependents("a")
        assert "b" in transitive
        assert "c" in transitive
        assert transitive["b"] == ["a", "b"]
        assert transitive["c"] == ["a", "b", "c"]

    def test_branching_graph(self) -> None:
        g = DependencyGraph()
        for aid in ("root", "a", "b", "c"):
            g.add_node(ArtifactRef(artifact_id=aid))
        g.add_edge("root", "a")
        g.add_edge("root", "b")
        g.add_edge("a", "c")

        deps = g.direct_dependent_ids("root")
        assert sorted(deps) == ["a", "b"]
        transitive = g.transitive_dependents("root")
        assert "a" in transitive
        assert "b" in transitive
        assert "c" in transitive

    def test_shared_dependency(self) -> None:
        g = DependencyGraph()
        for aid in ("a", "b", "c", "shared"):
            g.add_node(ArtifactRef(artifact_id=aid))
        g.add_edge("a", "shared")
        g.add_edge("b", "shared")

        assert sorted(g.direct_dependents("shared")) == []
        assert sorted(g.direct_dependent_ids("a")) == ["shared"]
        assert sorted(g.direct_dependent_ids("b")) == ["shared"]

    def test_duplicate_edge(self) -> None:
        g = DependencyGraph()
        for aid in ("a", "b"):
            g.add_node(ArtifactRef(artifact_id=aid))
        g.add_edge("a", "b")
        g.add_edge("a", "b")  # duplicate is allowed (edge list)
        assert len(g.edges()) == 2  # duplicates are normalized by consumer


class TestCycleDetection:
    def test_acyclic(self) -> None:
        g = DependencyGraph()
        for aid in ("a", "b", "c"):
            g.add_node(ArtifactRef(artifact_id=aid))
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        assert not g.has_cycle()

    def test_simple_cycle(self) -> None:
        g = DependencyGraph()
        for aid in ("a", "b"):
            g.add_node(ArtifactRef(artifact_id=aid))
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        assert g.has_cycle()

    def test_cycle_members(self) -> None:
        g = DependencyGraph()
        for aid in ("a", "b", "c", "d"):
            g.add_node(ArtifactRef(artifact_id=aid))
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        g.add_edge("c", "a")  # cycle a→b→c→a
        g.add_edge("c", "d")  # d downstream of cycle

        members = g.find_cycle_members()
        assert "a" in members
        assert "b" in members
        assert "c" in members
        assert "d" not in members  # d is downstream but not part of cycle

    def test_no_cycle_raises(self) -> None:
        g = DependencyGraph()
        for aid in ("a", "b"):
            g.add_node(ArtifactRef(artifact_id=aid))
        g.add_edge("a", "b")
        try:
            g.find_cycle_members()
            assert False, "Expected ValueError"
        except ValueError:
            pass


class TestMissingDependencies:
    def test_missing_dependency_reported(self) -> None:
        g = DependencyGraph()
        g.add_node(ArtifactRef(artifact_id="a"))
        g.add_edge("a", "b")  # b not added as a node
        missing = g.missing_nodes()
        assert "b" in missing

    def test_no_missing_when_all_present(self) -> None:
        g = DependencyGraph()
        for aid in ("a", "b", "c"):
            g.add_node(ArtifactRef(artifact_id=aid))
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        assert g.missing_nodes() == []


class TestDeterministicSerialization:
    def test_to_dict_stable(self) -> None:
        g = DependencyGraph()
        g.add_node(ArtifactRef(artifact_id="b", artifact_type="test"))
        g.add_node(ArtifactRef(artifact_id="a", artifact_type="test"))
        g.add_edge("a", "b", kind="structural")
        d1 = g.to_dict()
        d2 = g.to_dict()
        assert d1 == d2

    def test_to_json_stable(self) -> None:
        g = DependencyGraph()
        g.add_node(ArtifactRef(artifact_id="b", artifact_type="test"))
        g.add_node(ArtifactRef(artifact_id="a", artifact_type="test"))
        g.add_edge("a", "b")
        j1 = g.to_json()
        j2 = g.to_json()
        assert j1 == j2

    def test_roundtrip(self) -> None:
        g = DependencyGraph()
        for aid in ("a", "b", "c"):
            g.add_node(ArtifactRef(artifact_id=aid, artifact_type="test"))
        g.add_edge("a", "b", kind="structural", rule_id="R001")
        g.add_edge("b", "c", kind="semantic", rule_id="R002")

        d = g.to_dict()
        g2 = DependencyGraph.from_dict(d)
        assert g2.has_node("a")
        assert g2.has_node("b")
        assert g2.has_node("c")
        edges = g2.edges()
        assert len(edges) == 2
        assert edges[0].source_id == "a"
        assert edges[0].target_id == "b"
        assert edges[0].rule_id == "R001"


class TestWorkflowEdges:
    def test_standard_workflow_edges(self) -> None:
        g = DependencyGraph()
        g.add_standard_workflow_edges()
        # Standard edges should not cause errors even without nodes
        # But we can check no cycle in abstract edges
        assert not g.has_cycle()  # Should be a DAG if we check abstractly (no self-loops)

    def test_workflow_chain(self) -> None:
        g = DependencyGraph()
        g.add_standard_workflow_edges()
        # Add some nodes that match
        for aid in ("story_identity", "blueprint", "chapter_outline", "scene_realization",
                     "scene_expression", "chapter_expression", "book_expression",
                     "published_output"):
            g.add_node(ArtifactRef(artifact_id=aid))
        # Check the chain is valid
        transitive = g.transitive_dependents("story_identity")
        assert "blueprint" in transitive
        assert "chapter_outline" in transitive
        assert "published_output" in transitive
