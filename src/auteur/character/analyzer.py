from __future__ import annotations

from collections import Counter

from auteur.blueprint import Character, StoryBlueprint
from auteur.character.enums import Archetype, PhilosophyTag
from auteur.character.models import (
    ArchetypalLayer,
    CharacterIdentity,
    TextureLayer,
    TextureVoice,
)
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
                    preserve_intent=["Add at least a protagonist character to the blueprint."],
                    challenge_intent=["Keep character list empty only if this is a pre-characterization draft."],
                ),
            )
        )
        return diagnostics

    for char in blueprint.characters:
        diagnostics.extend(_diagnose_identity_missing(char))
        diagnostics.extend(_diagnose_layer_gaps(char))

    diagnostics.extend(_diagnose_archetype_redundancy(blueprint))
    diagnostics.extend(_diagnose_archetype_shadow_inversion(blueprint))
    diagnostics.extend(_diagnose_mentor_contrast(blueprint))
    diagnostics.extend(_diagnose_voice_convergence(blueprint))
    diagnostics.extend(_diagnose_character_roles(blueprint))
    diagnostics.extend(_diagnose_character_consistency(blueprint))
    diagnostics.extend(_diagnose_ideological_contrast(blueprint))
    diagnostics.extend(_diagnose_motif_presence(blueprint))
    diagnostics.extend(_diagnose_essence_completeness(blueprint))
    diagnostics.extend(_diagnose_texture_depth(blueprint))

    return diagnostics


def _load_identity(char: Character) -> CharacterIdentity | None:
    if char.identity is None:
        return None
    try:
        return (
            char.identity
            if isinstance(char.identity, CharacterIdentity)
            else CharacterIdentity.model_validate(char.identity)
        )
    except Exception:
        return None


def _diagnose_identity_missing(char: Character) -> list[StructureDiagnostic]:
    if char.identity is not None:
        return []
    return [
        StructureDiagnostic(
            severity=DiagnosticSeverity.WARNING,
            layer=DiagnosticLayer.STRUCTURAL_FORCES,
            rule="character.identity.missing",
            message=f"Character '{char.name}' has no character identity defined.",
            evidence=[f"character.name = {char.name}", "character.identity is absent"],
            repair_options=RepairOptions(
                preserve_intent=[f"Define a CharacterIdentity for '{char.name}' with archetype and psychology layers."],
                challenge_intent=["Skip identity for minor characters with no significant dramatic function."],
            ),
        )
    ]


def _diagnose_layer_gaps(char: Character) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []
    identity = _load_identity(char)
    if identity is None:
        return diagnostics

    if identity.archetype is None or identity.archetype.core is None:
        if char.role.value in ("protagonist", "antagonist", "deuteragonist"):
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.archetype.core_missing",
                    message=f"Character '{char.name}' has a primary role ({char.role.value}) but no core archetype.",
                    evidence=[f"character.name = {char.name}", f"character.role = {char.role.value}"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Assign a core archetype to '{char.name}'."],
                        challenge_intent=["Keep unset if the character defies easy classification."],
                    ),
                )
            )

    if identity.narrative_role is not None and not identity.narrative_role.secondary:
        if char.role.value in ("protagonist", "antagonist", "deuteragonist"):
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.narrative_role.no_secondary",
                    message=f"Character '{char.name}' has a narrative_role layer but no secondary dramatic functions.",
                    evidence=[f"character.name = {char.name}"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Add secondary dramatic functions to '{char.name}'."],
                        challenge_intent=["Leave empty if the character serves only their primary role."],
                    ),
                )
            )

    return diagnostics


def _diagnose_archetype_redundancy(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    core_archetypes: list[str] = []
    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity and identity.archetype and identity.archetype.core:
            core_archetypes.append(identity.archetype.core.value)

    duplicates = {arch for arch, count in Counter(core_archetypes).items() if count > 1}
    if duplicates:
        dup_chars = [
            c.name for c in blueprint.characters
            if _load_identity(c) and _load_identity(c).archetype
            and _load_identity(c).archetype.core.value in duplicates
        ]
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.STRUCTURAL_FORCES,
                rule="characters.archetype_redundancy",
                message=f"Archetype redundancy detected: {duplicates} appear on multiple characters.",
                evidence=[f"characters = {dup_chars}", f"duplicate archetypes = {sorted(duplicates)}"],
                repair_options=RepairOptions(
                    preserve_intent=["Ensure duplicated archetypes serve distinct dramatic functions."],
                    challenge_intent=["Diversify core archetypes so each character occupies unique mythic territory."],
                ),
            )
        )

    return diagnostics


def _diagnose_archetype_shadow_inversion(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity and identity.archetype:
            arch = identity.archetype
            if arch.core and arch.shadow and arch.core.value == arch.shadow.value:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="character.archetype.shadow_matches_core",
                        message=f"Character '{char.name}' has the same archetype for core and shadow.",
                        evidence=[f"character.name = {char.name}", f"core = {arch.core.value}", f"shadow = {arch.shadow.value}"],
                        repair_options=RepairOptions(
                            preserve_intent=["Choose a shadow archetype that inverts or complicates the core."],
                            challenge_intent=["Omit shadow if the character lacks a dark inversion."],
                        ),
                    )
                )

    return diagnostics


def _diagnose_mentor_contrast(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    mentors = [
        c for c in blueprint.characters
        if _load_identity(c) and _load_identity(c).archetype
        and _load_identity(c).archetype.core in (Archetype.MENTOR, Archetype.WISE_ELDER, Archetype.FALSE_MENTOR)
    ]
    protagonists = [
        c for c in blueprint.characters
        if c.role.value == "protagonist"
    ]

    if mentors and protagonists:
        for mentor in mentors:
            mentor_arch = _load_identity(mentor).archetype.core.value if _load_identity(mentor) and _load_identity(mentor).archetype else ""
            for prot in protagonists:
                prot_arch = _load_identity(prot).archetype.core.value if _load_identity(prot) and _load_identity(prot).archetype else ""
                if mentor_arch and prot_arch and mentor_arch == prot_arch:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.WARNING,
                            layer=DiagnosticLayer.STRUCTURAL_FORCES,
                            rule="character.mentor_no_ideological_contrast",
                            message=f"Mentor '{mentor.name}' shares the same core archetype as protagonist '{prot.name}'.",
                            evidence=[f"mentor = {mentor.name}", f"protagonist = {prot.name}", f"shared archetype = {mentor_arch}"],
                            repair_options=RepairOptions(
                                preserve_intent=["Give the mentor a contrasting archetype so they challenge rather than mirror the protagonist."],
                                challenge_intent=["Keep shared archetype if the mentor reinforces the protagonist's path."],
                            ),
                        )
                    )

    return diagnostics


def _diagnose_voice_convergence(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    voices: list[tuple[str, TextureVoice | None]] = []
    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity and identity.texture and identity.texture.voice:
            voices.append((char.name, identity.texture.voice))

    for i in range(len(voices)):
        for j in range(i + 1, len(voices)):
            name_a, voice_a = voices[i]
            name_b, voice_b = voices[j]
            if voice_a and voice_b:
                match_count = 0
                total = 0
                if voice_a.cadence and voice_b.cadence:
                    total += 1
                    if voice_a.cadence.strip().lower() == voice_b.cadence.strip().lower():
                        match_count += 1
                if voice_a.vocabulary and voice_b.vocabulary:
                    total += 1
                    if voice_a.vocabulary.strip().lower() == voice_b.vocabulary.strip().lower():
                        match_count += 1
                if total > 0 and match_count == total:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.WARNING,
                            layer=DiagnosticLayer.STRUCTURAL_FORCES,
                            rule="characters.voice_cadence_convergence",
                            message=f"Voice convergence detected between '{name_a}' and '{name_b}'.",
                            evidence=[
                                f"character_a = {name_a} (cadence={voice_a.cadence}, vocabulary={voice_a.vocabulary})",
                                f"character_b = {name_b} (cadence={voice_b.cadence}, vocabulary={voice_b.vocabulary})",
                            ],
                            repair_options=RepairOptions(
                                preserve_intent=["Differentiate at least one of cadence or vocabulary between these characters."],
                                challenge_intent=["Keep if intentional for characters from the same background."],
                            ),
                        )
                    )

    return diagnostics


def _diagnose_character_roles(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    protagonists = [c for c in blueprint.characters if c.role.value == "protagonist"]
    antagonists = [c for c in blueprint.characters if c.role.value == "antagonist"]

    if len(protagonists) > 1:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.STRUCTURAL_FORCES,
                rule="characters.multiple_protagonists",
                message=f"Multiple protagonists declared ({[c.name for c in protagonists]}).",
                evidence=[f"protagonists = {[c.name for c in protagonists]}"],
                repair_options=RepairOptions(
                    preserve_intent=["Ensure each protagonist has distinct want, arc, and theme."],
                    challenge_intent=["Promote one protagonist and reclassify others as deuteragonists."],
                ),
            )
        )

    if not antagonists:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.STRUCTURAL_FORCES,
                rule="characters.no_antagonist",
                message="No antagonist character declared.",
                evidence=["No character with role=antagonist in characters list."],
                repair_options=RepairOptions(
                    preserve_intent=["Add an antagonist character to personify the central resistance."],
                    challenge_intent=["Keep antagonist-free if conflict is entirely internal or environmental."],
                ),
            )
        )

    return diagnostics


def _diagnose_character_consistency(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    engine = blueprint.story_engine
    if engine is None:
        return diagnostics

    main_want = engine.main_thread.want.author_text.casefold()
    for char in blueprint.characters:
        if char.role.value == "protagonist" and char.name.casefold() not in main_want:
            mentioned = any(
                char.name.casefold() in t.name.casefold() or char.name.casefold() in t.want.author_text.casefold()
                for t in engine.threads
            )
            if not mentioned:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.THREADS,
                        rule="character.not_referenced_in_threads",
                        message=f"Protagonist '{char.name}' is not mentioned in any story thread.",
                        evidence=[f"character.name = {char.name}"],
                        repair_options=RepairOptions(
                            preserve_intent=[f"Reference '{char.name}' in at least one thread's want or name."],
                            challenge_intent=["Keep threads abstract if protagonist is not a named entity."],
                        ),
                    )
                )

    return diagnostics


# ---------------------------------------------------------------------------
# Ideological contrast analysis
# ---------------------------------------------------------------------------


def _collect_philosophy_tags(blueprint: StoryBlueprint) -> dict[str, list[PhilosophyTag]]:
    result: dict[str, list[PhilosophyTag]] = {}
    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity and identity.ideology and identity.ideology.philosophy_tags:
            result[char.name] = identity.ideology.philosophy_tags
    return result


def _opposed_tags(tag_a: PhilosophyTag, tag_b: PhilosophyTag) -> bool:
    opposition_pairs = [
        (PhilosophyTag.PROTECTION_THROUGH_HIERARCHY, PhilosophyTag.SALVATION_THROUGH_REBELLION),
        (PhilosophyTag.ORDER_THROUGH_STRUCTURE, PhilosophyTag.CHANGE_THROUGH_DESTRUCTION),
        (PhilosophyTag.CONTROL_THROUGH_CARE, PhilosophyTag.FREEDOM_THROUGH_AUTONOMY),
        (PhilosophyTag.JUSTICE_THROUGH_RULES, PhilosophyTag.TRUTH_THROUGH_CONFRONTATION),
        (PhilosophyTag.POWER_THROUGH_KNOWLEDGE, PhilosophyTag.SALVATION_THROUGH_KNOWLEDGE),
        (PhilosophyTag.PEACE_THROUGH_WITHDRAWAL, PhilosophyTag.SALVATION_THROUGH_REBELLION),
        (PhilosophyTag.MEANING_THROUGH_SACRIFICE, PhilosophyTag.SURVIVAL_THROUGH_ADAPTATION),
    ]
    return (tag_a, tag_b) in opposition_pairs or (tag_b, tag_a) in opposition_pairs


def _diagnose_ideological_contrast(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []
    char_tags = _collect_philosophy_tags(blueprint)

    names = list(char_tags.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            name_a = names[i]
            name_b = names[j]
            a_tags = char_tags[name_a]
            b_tags = char_tags[name_b]
            if any(_opposed_tags(ta, tb) for ta in a_tags for tb in b_tags):
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="characters.ideological_contrast_detected",
                        message=f"Ideological contrast between '{name_a}' and '{name_b}' based on philosophy tags.",
                        evidence=[f"character_a = {name_a} tags = {[t.value for t in a_tags]}",
                                  f"character_b = {name_b} tags = {[t.value for t in b_tags]}"],
                        repair_options=RepairOptions(
                            preserve_intent=["Ensure the story dramatizes this ideological conflict."],
                            challenge_intent=["Reduce contrasting tags if characters are not intended to conflict."],
                        ),
                    )
                )
            if set(a_tags) == set(b_tags):
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="characters.ideological_convergence",
                        message=f"'{name_a}' and '{name_b}' share identical philosophy tags.",
                        evidence=[f"character_a = {name_a} tags = {[t.value for t in a_tags]}",
                                  f"character_b = {name_b} tags = {[t.value for t in b_tags]}"],
                        repair_options=RepairOptions(
                            preserve_intent=["Differentiate at least one philosophy tag between these characters."],
                            challenge_intent=["Keep identical tags if they share the same worldview."],
                        ),
                    )
                )

    return diagnostics


# ---------------------------------------------------------------------------
# Motif presence analysis
# ---------------------------------------------------------------------------


def _diagnose_motif_presence(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        identity = _load_identity(char)
        if char.role.value not in ("protagonist", "antagonist", "deuteragonist"):
            continue
        if identity is None:
            continue
        if identity.motifs is None or not identity.motifs.motifs:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.motifs.missing",
                    message=f"Character '{char.name}' ({char.role.value}) has no motif profile. Motifs anchor character behavior in reader memory.",
                    evidence=[f"character.name = {char.name}", "character.motifs is empty"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Add at least 2-3 recurring motifs for '{char.name}'."],
                        challenge_intent=["Omit if the character's behavior is intentionally transparent."],
                    ),
                )
            )

    return diagnostics


# ---------------------------------------------------------------------------
# Essence completeness analysis
# ---------------------------------------------------------------------------


def _diagnose_essence_completeness(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity is None or identity.essence is None:
            continue
        essence = identity.essence
        if not essence.personal_traits and not essence.bond_traits:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.essence.empty",
                    message=f"Character '{char.name}' has an essence profile but no traits defined.",
                    evidence=[f"character.name = {char.name}", "essence.personal_traits and essence.bond_traits are empty"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Add personal traits, bond traits, or both for '{char.name}'."],
                        challenge_intent=["Remove the essence profile if it is not needed."],
                    ),
                )
            )

    return diagnostics


# ---------------------------------------------------------------------------
# Texture depth analysis
# ---------------------------------------------------------------------------


def _diagnose_texture_depth(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity is None or identity.texture is None:
            continue
        texture = identity.texture
        if not texture.gestures and not texture.rituals and not texture.social_habits and not texture.behavioral_tells:
            if char.role.value in ("protagonist", "antagonist", "deuteragonist"):
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="character.texture.shallow",
                        message=f"Character '{char.name}' has a texture layer but no behavioral depth fields (gestures, rituals, social_habits, behavioral_tells).",
                        evidence=[f"character.name = {char.name}", "All behavioral texture fields are empty"],
                        repair_options=RepairOptions(
                            preserve_intent=[f"Add at least one of gestures, rituals, social_habits, or behavioral_tells for '{char.name}'."],
                            challenge_intent=["Keep shallow if voice and aesthetic are sufficient."],
                        ),
                    )
                )

    return diagnostics
