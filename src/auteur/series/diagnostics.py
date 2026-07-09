from __future__ import annotations

from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)
from auteur.series.models import SeriesIdentity


_SCOPE_ORDER = {
    "personal": 1,
    "village": 2,
    "city": 3,
    "national": 4,
    "civilizational": 5,
    "cosmic": 6,
}


def _diag(rule: str, message: str, evidence: list[str], severity: DiagnosticSeverity = DiagnosticSeverity.WARNING) -> StructureDiagnostic:
    return StructureDiagnostic(
        severity=severity,
        layer=DiagnosticLayer.THREADS,
        rule=rule,
        message=message,
        evidence=evidence,
        repair_options=RepairOptions(preserve_intent=[], challenge_intent=[]),
    )


def diagnose_series(series: SeriesIdentity) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []
    book_count = len(series.book_plans)

    for arc in series.character_arcs:
        for current in range(2, book_count + 1):
            previous_state = arc.book_states.get(str(current - 1), "")
            current_state = arc.book_states.get(str(current), "")
            transition_key = f"{current - 1}->{current}"
            if current_state and previous_state and current_state != previous_state and transition_key not in arc.transitions:
                diagnostics.append(_diag(
                    "series.character.regression_without_transition",
                    f"Character arc '{arc.id}' changes state between Book {current - 1} and Book {current} without a declared transition.",
                    [f"Book {current - 1}: {previous_state}", f"Book {current}: {current_state}"],
                ))
                break
        for book_number, state in arc.book_states.items():
            if int(book_number) < arc.planned_completion_book and state == arc.end_state:
                diagnostics.append(_diag(
                    "series.character.completed_too_early",
                    f"Character arc '{arc.id}' reaches its final state before the planned completion book.",
                    [f"planned_completion_book = {arc.planned_completion_book}", f"Book {book_number}: {state}"],
                ))
                break

    scopes = [_SCOPE_ORDER.get(book.scope, 0) for book in series.book_plans]
    stakes = [book.central_engine.stakes.casefold().strip() for book in series.book_plans]
    if len(set(stakes)) == 1 or all(scopes[i] <= scopes[i - 1] for i in range(1, len(scopes))):
        diagnostics.append(_diag(
            "series.scope.flat_stakes",
            "Series escalation is weak because stakes or scope remain flat across books.",
            [f"scopes = {[book.scope for book in series.book_plans]}"],
        ))

    for mystery in series.mysteries:
        if mystery.actual_payoff_book is None:
            diagnostics.append(_diag(
                "series.mystery.missing_payoff",
                f"Mystery '{mystery.id}' has no actual payoff book.",
                [f"expected_payoff_book = {mystery.expected_payoff_book}"],
            ))
        elif mystery.actual_payoff_book < mystery.expected_payoff_book:
            diagnostics.append(_diag(
                "series.mystery.premature_payoff",
                f"Mystery '{mystery.id}' pays off before its expected climax.",
                [
                    f"expected_payoff_book = {mystery.expected_payoff_book}",
                    f"actual_payoff_book = {mystery.actual_payoff_book}",
                ],
            ))
        elif mystery.actual_payoff_book > mystery.expected_payoff_book:
            diagnostics.append(_diag(
                "series.mystery.late_payoff",
                f"Mystery '{mystery.id}' pays off later than expected.",
                [
                    f"expected_payoff_book = {mystery.expected_payoff_book}",
                    f"actual_payoff_book = {mystery.actual_payoff_book}",
                ],
            ))

    if series.series_type.value == "trilogy":
        middle = series.book_plans[1].series_function.casefold()
        if not any(term in middle for term in ("complication", "collapse", "escalation")):
            diagnostics.append(_diag(
                "series.trilogy.weak_middle_function",
                "Book 2 of a trilogy should complicate, collapse, or escalate the series engine.",
                [f"book_2.series_function = {series.book_plans[1].series_function}"],
            ))

    intensities = [book.climax_intensity for book in series.book_plans]
    for index in range(1, len(intensities)):
        function = series.book_plans[index].series_function.casefold()
        if intensities[index] < intensities[index - 1] and "cooldown" not in function:
            diagnostics.append(_diag(
                "series.tension.regression",
                "A later book climax is less intense than the previous book without an explicit cooldown role.",
                [f"Book {index}: {intensities[index - 1]}", f"Book {index + 1}: {intensities[index]}"],
            ))
            break

    return diagnostics
