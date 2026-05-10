from __future__ import annotations

from auteur.blueprint import StoryBlueprint
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)
from auteur.blueprint import SupportFunction


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

    target_experience = blueprint.identity.target_experience
    ending_tone = blueprint.contract.mandatory_ending_tone.value
    if target_experience is not None:
        avoided_ending = _matching_avoidance(target_experience.avoid, ending_tone)
        if avoided_ending is not None:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    layer=DiagnosticLayer.TARGET_EXPERIENCE,
                    rule="target_experience.ending_tone_avoided",
                    message=(
                        "The mandatory ending tone conflicts with the target "
                        "experience the story says to avoid."
                    ),
                    evidence=[
                        "identity.target_experience.avoid",
                        f"avoid item = {avoided_ending}",
                        f"contract.mandatory_ending_tone = {ending_tone}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Choose an ending tone that does not appear in the target experience avoid list."
                        ],
                        challenge_intent=[
                            "Revise the target experience avoid list if this ending tone is intentional."
                        ],
                    ),
                )
            )

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

    for thread in engine.threads:
        support_functions = {support_function.value for support_function in thread.supports_main_by}
        if support_functions.isdisjoint({SupportFunction.ESCALATES.value, SupportFunction.PRESSURES_CHANGE.value}):
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.THREADS,
                    rule="thread.supports_main_by.lacks_escalation_or_pressure",
                    message=(
                        "The subordinate thread is declared, but its support functions do not appear to move the main thread."
                    ),
                    evidence=[
                        f"thread.name = {thread.name}",
                        f"thread.supports_main_by = {[support_function.value for support_function in thread.supports_main_by]}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Add one or more support functions that escalate pressure on the main thread, such as escalates or pressures_change."
                        ],
                        challenge_intent=[
                            "Remove or defer the thread if it is not materially supporting the main thread's movement."
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


def _matching_avoidance(avoid: list[str], ending_tone: str) -> str | None:
    normalized_tone = _normalize(ending_tone.replace("_", " "))
    for item in avoid:
        if normalized_tone in _normalize(item):
            return item
    return None


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
