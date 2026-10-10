"""Read-only source-bound graph projection for the Living Story Studio.

A graph projection is not a replacement for relations.yaml or StoryIdentity.
Missing or invalid sources are reported, not fabricated.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from auteur.relations.models import RelationMap
from auteur.relations.serializers import load_relation_change_sets


def project_studio_graph(
    project_root: Path,
    *,
    workspace_id: str | None = None,
    session_version: int | None = None,
    story_orientation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    warnings: list[str] = []
    relation_sha: str | None = None
    changed_by_chapter: dict[str, list[str]] = {}

    if story_orientation:
        lenses = story_orientation.get("story_lenses") or []
        active_lenses = {lens["lens_id"] for lens in lenses if lens.get("lens_id")}
        for lens in lenses:
            lens_id = lens.get("lens_id")
            if not lens_id:
                continue
            nodes.append({
                "id": f"lens:{lens_id}", "kind": "lens", "title": lens.get("title") or lens_id,
                "detail": lens.get("summary") or "No interpretation established",
                "status": lens.get("state") or "unestablished",
                "authority": "DERIVED / NOT CANON",
                "source_ref": f"workspace:{workspace_id}:lens:{lens_id}",
                "source_component_ids": lens.get("source_component_ids") or [],
            })
            for target in lens.get("related_lens_ids") or []:
                if target in active_lenses:
                    edges.append({
                        "id": f"lens-link:{lens_id}:{target}", "source": f"lens:{lens_id}",
                        "target": f"lens:{target}", "label": "related lens",
                        "source_ref": f"workspace:{workspace_id}:lens:{lens_id}",
                        "authority": "DERIVED / NOT CANON",
                    })

    path = Path(project_root) / "relations.yaml"
    if path.exists():
        try:
            raw = path.read_bytes()
            relation_map = RelationMap.model_validate(yaml.safe_load(raw.decode("utf-8")) or {}, strict=True)
            relation_sha = hashlib.sha256(raw).hexdigest()
        except (OSError, UnicodeError, ValueError, yaml.YAMLError):
            warnings.append("relations.yaml could not be read or validated; relationship evidence is unavailable.")
        else:
            by_character: dict[str, str] = {}
            try:
                change_sets = load_relation_change_sets(Path(project_root))
            except (OSError, UnicodeError, ValueError, yaml.YAMLError):
                warnings.append("Chapter relationship change history is unavailable or malformed.")
                change_sets = []
            known_relations = {relation.id for relation in relation_map.relations}
            for change in change_sets:
                chapter = "chapter_" + str(change.chapter).zfill(2)
                changed_by_chapter.setdefault(chapter, [])
                for record in change.relation_changes:
                    if record.relation in known_relations and record.relation not in changed_by_chapter[chapter]:
                        changed_by_chapter[chapter].append(record.relation)
            for i, relation in enumerate(relation_map.relations):
                for name in (relation.from_character, relation.to_character):
                    if name not in by_character:
                        node_id = "character:" + hashlib.sha256(name.encode("utf-8")).hexdigest()[:24]
                        by_character[name] = node_id
                        nodes.append({
                            "id": node_id, "kind": "character", "title": name, "detail": "Declared character in relationship map",
                            "status": "declared", "authority": "RELATIONS SOURCE",
                            "source_ref": f"relations.yaml#/relations/{i}",
                            "source_sha256": relation_sha,
                        })
                edges.append({
                    "id": f"relation:{relation.id}", "source": by_character[relation.from_character],
                    "target": by_character[relation.to_character],
                    "label": relation.public_role or "declared relationship",
                    "detail": relation.private_truth, "status": "declared",
                    "source_ref": f"relations.yaml#/relations/{i}", "source_sha256": relation_sha,
                    "authority": "RELATIONS SOURCE",
                })
    return {
        "schema_version": 1, "workspace_id": workspace_id,
        "session_version": session_version, "relations_sha256": relation_sha,
        "nodes": nodes, "edges": edges, "warnings": warnings,
        "relationship_changes": changed_by_chapter,
    }
