"""Read-only hypothetical dependency preview for already registered artifacts.

An impact path is evidence of possible downstream review, not a forecast that a
particular story fact changes; no accepted source is mutated here.
"""
from __future__ import annotations

from pathlib import Path

from auteur.impact.analyzer import ImpactAnalyzer
from auteur.impact.graph import DependencyGraph


def preview_studio_impact(project_root: Path, artifact_id: str, *, graph: DependencyGraph | None = None) -> dict:
    graph = graph if graph is not None else ImpactAnalyzer(project_root).build_graph()
    source = graph.get_node(artifact_id)
    if source is None:
        raise ValueError("artifact is not in registered provenance graph")

    affected: list[dict] = []
    for target_id, path in sorted(graph.transitive_dependents(artifact_id).items()):
        ref = graph.get_node(target_id)
        if ref is None:
            continue
        hops = []
        for src, dst in zip(path, path[1:]):
            edge = next((edge for edge in graph.direct_dependents(src) if edge.target_id == dst), None)
            hops.append({"source": src, "target": dst,
                         "kind": edge.kind if edge else "unknown",
                         "evidence": edge.source if edge else "unknown"})
        affected.append({
            "artifact_id": ref.artifact_id,
            "artifact_type": ref.artifact_type,
            "accepted": ref.accepted,
            "authority": ref.authority,
            "source_ref": ref.file_path,
            "dependency_path": path,
            "direct": len(path) == 2,
            "hops": hops,
            "explanation": (
                "This registered artifact depends on the selected source"
                + (" directly." if len(path) == 2 else " through intermediate artifacts.")
                + " A proposed change may require review; no story change has been applied."
            ),
        })
    return {
        "schema_version": 1, "source": source.to_dict(),
        "mode": "HYPOTHETICAL / READ ONLY",
        "affected": affected,
        "warning": "Dependency paths do not establish a narrative consequence or authorize a revision.",
    }
