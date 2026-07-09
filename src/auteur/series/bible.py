from __future__ import annotations

from auteur.series.graph import build_dependency_graph
from auteur.series.models import SeriesIdentity


def compile_series_bible(series: SeriesIdentity) -> dict:
    graph = build_dependency_graph(series)
    return {
        "title": series.title,
        "core_question": series.core_question,
        "characters": [
            {
                "name": arc.character,
                "arc_id": arc.id,
                "start_state": arc.start_state,
                "end_state": arc.end_state,
                "book_states": arc.book_states,
            }
            for arc in series.character_arcs
        ],
        "relationships": [
            {
                "id": arc.id,
                "participants": arc.participants,
                "start_state": arc.start_state,
                "end_state": arc.end_state,
                "book_states": arc.book_states,
            }
            for arc in series.relationship_arcs
        ],
        "factions": [
            {
                "name": arc.faction,
                "arc_id": arc.id,
                "start_state": arc.start_state,
                "end_state": arc.end_state,
                "book_states": arc.book_states,
            }
            for arc in series.faction_arcs
        ],
        "mysteries": [m.model_dump(mode="json") for m in series.mysteries],
        "timeline": [
            {
                "book": book.book_number,
                "title": book.title,
                "series_function": book.series_function,
                "scope": book.scope,
                "setups": book.required_setups,
                "payoffs": book.required_payoffs,
            }
            for book in series.book_plans
        ],
        "recurring_symbols": series.recurring_symbols,
        "continuity_facts": [
            f"{book.title}: {book.core_answer}"
            for book in series.book_plans
        ],
        "dependency_index": graph.impact_metadata,
    }
