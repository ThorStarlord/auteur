from __future__ import annotations

from auteur.series.graph import build_dependency_graph
from auteur.series.models import SeriesIdentity
from auteur.series.continuity_validators import (
    ThematicProgressionValidator,
    CharacterContinuityValidator,
    RelationshipContinuityValidator,
    LoreConsistencyValidator,
    ChronologyValidator,
    SetupPayoffValidator,
)


def compile_series_bible(series: SeriesIdentity) -> dict:
    graph = build_dependency_graph(series)
    book_numbers = [str(book.book_number) for book in series.book_plans]
    payoff_schedule = {
        str(book.book_number): list(book.required_payoffs)
        for book in series.book_plans
    }

    # Run Group 3 continuity validators
    continuity_diagnostics = []
    continuity_diagnostics.extend(ThematicProgressionValidator().validate(series))
    continuity_diagnostics.extend(CharacterContinuityValidator().validate(series))
    continuity_diagnostics.extend(RelationshipContinuityValidator().validate(series))
    continuity_diagnostics.extend(LoreConsistencyValidator().validate(series))
    continuity_diagnostics.extend(ChronologyValidator().validate(series))
    continuity_diagnostics.extend(SetupPayoffValidator().validate(series))
    mystery_status_by_book: dict[str, list[dict]] = {number: [] for number in book_numbers}
    for mystery in series.mysteries:
        for number in book_numbers:
            book_number = int(number)
            if book_number < mystery.introduced_book:
                status = "not_introduced"
            elif mystery.actual_payoff_book == book_number:
                status = "paid_off"
            elif mystery.actual_payoff_book is not None and book_number > mystery.actual_payoff_book:
                status = "resolved"
            else:
                status = "active"
            mystery_status_by_book[number].append({"id": mystery.id, "status": status})

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
                "series_function": book.series_function.value,
                "scope": book.scope.value,
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
        "character_state_matrix": {
            arc.character: arc.book_states for arc in series.character_arcs
        },
        "relationship_state_matrix": {
            arc.id: arc.book_states for arc in series.relationship_arcs
        },
        "faction_state_matrix": {
            arc.faction: arc.book_states for arc in series.faction_arcs
        },
        "mystery_status_by_book": mystery_status_by_book,
        "payoff_schedule": payoff_schedule,
        "unresolved_threads": [
            mystery.id for mystery in series.mysteries if mystery.actual_payoff_book is None
        ],
        "book_context_packets": {
            str(book.book_number): {
                "title": book.title,
                "series_function": book.series_function.value,
                "scope": book.scope.value,
                "threads_carried": book.series_threads_carried,
                "setups": book.required_setups,
                "payoffs": book.required_payoffs,
                "core_answer": book.core_answer,
            }
            for book in series.book_plans
        },
        "continuity_diagnostics": [
            {
                "id": d.id,
                "severity": d.severity,
                "constraint": d.constraint,
                "source": d.source,
                "conflict": d.conflict,
                "conflict_source": d.conflict_source,
                "explanation": d.explanation,
            }
            for d in continuity_diagnostics
        ],
    }
