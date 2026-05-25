from __future__ import annotations

from auteur.blueprint import Character, StoryBlueprint
from auteur.character.models import CharacterIdentity
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)


def analyze_character_categorization(
    blueprint: StoryBlueprint,
) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    if not blueprint.characters:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.STRUCTURAL_FORCES,
                rule="characters.missing",
                message="Blueprint has no declared characters.",
                evidence=["characters list is empty"],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Add at least a protagonist character to the blueprint."
                    ],
                    challenge_intent=[
                        "Keep character list empty only if this is a pre-characterization draft."
                    ],
                ),
            )
        )
        return diagnostics

    for char in blueprint.characters:
        diagnostics.extend(_diagnose_character_identity(blueprint, char))
        diagnostics.extend(_diagnose_character_roles(blueprint, char))
        diagnostics.extend(_diagnose_character_consistency(blueprint, char))

    return diagnostics


def _diagnose_character_identity(
    blueprint: StoryBlueprint, char: Character
) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    if char.identity is None:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.STRUCTURAL_FORCES,
                rule="character.identity.missing",
                message=(
                    f"Character '{char.name}' has no character identity defined. "
                    "Identity provides archetype, alignment, personality, and dramatic function."
                ),
                evidence=[f"character.name = {char.name}", "character.identity is absent"],
                repair_options=RepairOptions(
                    preserve_intent=[
                        f"Define a CharacterIdentity for '{char.name}' with archetype and alignment."
                    ],
                    challenge_intent=[
                        "Skip identity for minor characters with no significant dramatic function."
                    ],
                ),
            )
        )
    else:
        try:
            identity = (
                char.identity
                if isinstance(char.identity, CharacterIdentity)
                else CharacterIdentity.model_validate(char.identity)
            )
        except Exception as exc:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.identity.invalid",
                    message=f"Character '{char.name}' has an invalid identity: {exc}",
                    evidence=[f"character.name = {char.name}", f"error = {exc}"],
                    repair_options=RepairOptions(
                        preserve_intent=["Fix the character identity to match the CharacterIdentity schema."],
                        challenge_intent=["Remove the identity field if categorization is not needed."],
                    ),
                )
            )
            return diagnostics
        if identity.archetype is None and char.role.value in ("protagonist", "antagonist"):
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.archetype.missing_for_primary_role",
                    message=(
                        f"Character '{char.name}' has a primary narrative role ({char.role.value}) "
                        "but no archetype. Archetype clarifies thematic function."
                    ),
                    evidence=[f"character.name = {char.name}", f"character.role = {char.role.value}"],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            f"Assign an archetype to '{char.name}' (e.g. tragic_hero, mentor, shadow)."
                        ],
                        challenge_intent=[
                            "Keep archetype unset if the character defies easy classification."
                        ],
                    ),
                )
            )

        if not identity.dramatic_functions and char.role.value in ("protagonist", "antagonist", "deuteragonist"):
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.dramatic_functions.missing",
                    message=(
                        f"Character '{char.name}' has no declared dramatic functions. "
                        "Dramatic functions explain how the character serves the story."
                    ),
                    evidence=[f"character.name = {char.name}"],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            f"Add dramatic functions to '{char.name}' (e.g. emotional_anchor, catalyst, moral_compass)."
                        ],
                        challenge_intent=[
                            "Omit dramatic functions for walk-on or background characters."
                        ],
                    ),
                )
            )

    return diagnostics


def _diagnose_character_roles(
    blueprint: StoryBlueprint, char: Character
) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    protagonists = [c for c in blueprint.characters if c.role.value == "protagonist"]
    antagonists = [c for c in blueprint.characters if c.role.value == "antagonist"]

    if char.role.value == "protagonist" and len(protagonists) > 1:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.STRUCTURAL_FORCES,
                rule="characters.multiple_protagonists",
                message=(
                    f"Multiple protagonists declared ({[c.name for c in protagonists]}). "
                    "Each protagonist splits POV and emotional investment."
                ),
                evidence=[f"protagonists = {[c.name for c in protagonists]}"],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Ensure each protagonist has a distinct want, arc, and theme to justify the split focus."
                    ],
                    challenge_intent=[
                        "Promote one protagonist and reclassify others as deuteragonists."
                    ],
                ),
            )
        )

    if not antagonists:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.STRUCTURAL_FORCES,
                rule="characters.no_antagonist",
                message="No antagonist character declared. Conflict may lack a personal face.",
                evidence=["No character with role=antagonist in characters list."],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Add an antagonist character to personify the central resistance.",
                        "Use an antagonist_force archetype if the resistance is impersonal (nature, society, self)."
                    ],
                    challenge_intent=[
                        "Keep antagonist-free if conflict is entirely internal or environmental."
                    ],
                ),
            )
        )

    return diagnostics


def _diagnose_character_consistency(
    blueprint: StoryBlueprint, char: Character
) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    engine = blueprint.story_engine
    if engine is not None:
        thread_names = {t.name.casefold() for t in engine.threads}
        main_thread_want_lower = engine.main_thread.want.author_text.casefold()
        char_name_lower = char.name.casefold()

        if char_name_lower not in main_thread_want_lower and char.role.value == "protagonist":
            mentioned_in_threads = any(char_name_lower in t.name.casefold() or char_name_lower in t.want.author_text.casefold() for t in engine.threads)
            if not mentioned_in_threads:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.THREADS,
                        rule="character.not_referenced_in_threads",
                        message=(
                            f"Protagonist '{char.name}' is not mentioned in any story thread "
                            "want or name text. The character may be disconnected from the story engine."
                        ),
                        evidence=[f"character.name = {char.name}"],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                f"Reference '{char.name}' in at least one thread's want or name."
                            ],
                            challenge_intent=[
                                "Keep thread references abstract if the protagonist is not a named entity."
                            ],
                        ),
                    )
                )

    return diagnostics
