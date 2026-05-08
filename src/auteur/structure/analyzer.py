from __future__ import annotations

from auteur.blueprint import StoryBlueprint
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)


def analyze_structure(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []
    engine = blueprint.story_engine

    if engine is None:
        return [
            StructureDiagnostic(
                severity=DiagnosticSeverity.ERROR,
                layer=DiagnosticLayer.STRUCTURAL_FORCES,
                rule="story_engine.missing",
                message="Blueprint has no whole-story engine.",
                evidence=["story_engine is absent"],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Generate a story_engine from the existing author intent, theme, characters, and contract."
                    ],
                    challenge_intent=[
                        "Keep this blueprint as a chapter-drafting-only artifact and skip structure diagnosis."
                    ],
                ),
            )
        ]

    thread_count = len(engine.threads)
    subplot_budget = blueprint.structure.subplot_budget
    if thread_count and subplot_budget is None:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.SCOPE,
                rule="structure.subplot_budget.missing",
                message="Subordinate threads exist, but structure.subplot_budget is not declared.",
                evidence=[
                    f"story_engine.threads count = {thread_count}",
                    "structure.subplot_budget is absent",
                ],
                repair_options=RepairOptions(
                    preserve_intent=["Declare a subplot_budget that matches the intended story scale."],
                    challenge_intent=["Remove subordinate threads if the story should remain tightly focused."],
                ),
            )
        )
    elif subplot_budget is not None and thread_count > subplot_budget:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.ERROR,
                layer=DiagnosticLayer.SCOPE,
                rule="threads.exceeds_subplot_budget",
                message=f"Declared {thread_count} subordinate threads but subplot_budget is {subplot_budget}.",
                evidence=[
                    f"structure.subplot_budget = {subplot_budget}",
                    f"story_engine.threads count = {thread_count}",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Merge threads that serve the same structural function.",
                        "Increase subplot_budget if this scope is intentional.",
                    ],
                    challenge_intent=[
                        "Reduce the design to a more focused story with fewer subordinate threads."
                    ],
                ),
            )
        )

    want = _normalize(engine.main_thread.want.author_text)
    change = _normalize(engine.main_thread.change.author_text)
    if want == change:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.ERROR,
                layer=DiagnosticLayer.STRUCTURAL_FORCES,
                rule="main_thread.change_duplicates_want",
                message="The main thread change repeats the want instead of describing transformation.",
                evidence=[
                    f"main_thread.want.author_text = {engine.main_thread.want.author_text}",
                    f"main_thread.change.author_text = {engine.main_thread.change.author_text}",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Rewrite change as the protagonist's end-state transformation, not the external goal."
                    ],
                    challenge_intent=[
                        "Use a flat arc intentionally and describe what the protagonist changes in the world instead."
                    ],
                ),
            )
        )

    thesis_terms = _meaningful_terms(blueprint.theme.thesis)
    thematic_text = " ".join(
        [engine.main_thread.thematic_function, *(thread.thematic_function for thread in engine.threads)]
    )
    thematic_terms = _meaningful_terms(thematic_text)
    if thesis_terms and not thesis_terms.intersection(thematic_terms):
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.THEME,
                rule="theme.thesis_unrepresented",
                message="The theme thesis is not echoed by any thread thematic_function.",
                evidence=[
                    f"theme.thesis = {blueprint.theme.thesis}",
                    "No meaningful thesis terms appear in story_engine thematic functions.",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Revise one thread thematic_function to explicitly test the thesis."
                    ],
                    challenge_intent=[
                        "Revise the thesis if the threads are already expressing the real thematic argument."
                    ],
                ),
            )
        )

    return diagnostics


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "through",
    "to",
    "what",
    "when",
    "whether",
    "with",
}


def _meaningful_terms(text: str) -> set[str]:
    normalized = "".join(char if char.isalnum() else " " for char in text.casefold())
    return {word for word in normalized.split() if len(word) > 3 and word not in _STOP_WORDS}
