from __future__ import annotations

from auteur.relations.models import RELATION_METRICS, RelationChangeSet, RelationMap


def build_relation_graph(relation_map: RelationMap, change_sets: list[RelationChangeSet] | None = None) -> dict:
    characters = sorted(
        {relation.from_character for relation in relation_map.relations}
        | {relation.to_character for relation in relation_map.relations}
    )
    nodes = [
        {"id": f"character:{character}", "type": "character", "label": character}
        for character in characters
    ]
    nodes.extend(
        {
            "id": f"relation:{relation.id}",
            "type": "relation",
            "label": relation.id,
            "metrics": {metric: getattr(relation, metric) for metric in RELATION_METRICS},
        }
        for relation in sorted(relation_map.relations, key=lambda item: item.id)
    )
    edges = []
    for relation in sorted(relation_map.relations, key=lambda item: item.id):
        edges.append(
            {
                "source": f"character:{relation.from_character}",
                "target": f"relation:{relation.id}",
                "type": "directed_relation",
            }
        )
        edges.append(
            {
                "source": f"relation:{relation.id}",
                "target": f"character:{relation.to_character}",
                "type": "directed_relation",
            }
        )
    changed_by_chapter: dict[str, list[str]] = {}
    for change_set in change_sets or []:
        changed_by_chapter[f"chapter_{change_set.chapter:02d}"] = [
            change.relation for change in change_set.relation_changes
        ]
    return {"nodes": nodes, "edges": edges, "changed_by_chapter": changed_by_chapter}

