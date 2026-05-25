from __future__ import annotations

from collections import Counter

from auteur.blueprint import Character, StoryBlueprint
from auteur.character.enums import (
    Archetype,
    DefenseMechanism,
    PhilosophyTag,
)
from auteur.character.models import (
    CharacterIdentity,
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
    diagnostics.extend(_diagnose_vulnerability_presence(blueprint))
    diagnostics.extend(_diagnose_defense_presence(blueprint))
    diagnostics.extend(_diagnose_social_aura_presence(blueprint))
    diagnostics.extend(_diagnose_relationship_arcs(blueprint))
    diagnostics.extend(_diagnose_texture_uniqueness(blueprint))
    diagnostics.extend(_diagnose_defense_controlled(blueprint))
    diagnostics.extend(_diagnose_intimacy_presence(blueprint))
    diagnostics.extend(_diagnose_relationship_arc_progression(blueprint))
    diagnostics.extend(_diagnose_contradiction_depth(blueprint))
    diagnostics.extend(_diagnose_adaptation_divergence(blueprint))

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
    return diagnostics


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


def _diagnose_vulnerability_presence(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        identity = _load_identity(char)
        if char.role.value not in ("protagonist", "antagonist", "deuteragonist"):
            continue
        if identity is None:
            continue
        if identity.psychology is None or identity.psychology.vulnerability_family is None:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.psychology.vulnerability_missing",
                    message=f"Character '{char.name}' ({char.role.value}) has no vulnerability family defined.",
                    evidence=[f"character.name = {char.name}", "psychology.vulnerability_family is absent"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Assign a VulnerabilityFamily to '{char.name}' (e.g. 'status_control', 'abandonment')."],
                        challenge_intent=["Omit if the character's emotional drivers are intentionally ambiguous."],
                    ),
                )
            )

    return diagnostics


def _diagnose_defense_presence(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        identity = _load_identity(char)
        if char.role.value not in ("protagonist", "antagonist", "deuteragonist"):
            continue
        if identity is None or identity.psychology is None:
            continue
        if not identity.psychology.defense_mechanisms:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.psychology.defense_missing",
                    message=f"Character '{char.name}' has a psychology layer but no defense mechanisms defined.",
                    evidence=[f"character.name = {char.name}", "psychology.defense_mechanisms is empty"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Add defense mechanisms for '{char.name}' (e.g. 'compartmentalization', 'transactional_containment')."],
                        challenge_intent=["Omit if the character does not employ patterned stress responses."],
                    ),
                )
            )

    return diagnostics


def _diagnose_social_aura_presence(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        identity = _load_identity(char)
        if char.role.value not in ("protagonist", "antagonist", "deuteragonist"):
            continue
        if identity is None or identity.texture is None:
            continue
        if not identity.texture.social_aura:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.texture.social_aura_missing",
                    message=f"Character '{char.name}' has a texture layer but no social aura defined.",
                    evidence=[f"character.name = {char.name}", "texture.social_aura is empty"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Add social aura entries for '{char.name}' (e.g. 'executive_pressure', 'warm_authority')."],
                        challenge_intent=["Omit if the character's social atmosphere is not yet specified."],
                    ),
                )
            )

    return diagnostics


def _diagnose_relationship_arcs(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity is None or identity.relationship_mesh is None:
            continue
        mesh = identity.relationship_mesh
        if mesh.relationships and not mesh.arcs:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.relationship.arcs_missing",
                    message=f"Character '{char.name}' has relationship signatures but no relationship arcs defined.",
                    evidence=[f"character.name = {char.name}", f"has {len(mesh.relationships)} relationship(s), 0 arcs"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Add RelationshipArc entries for '{char.name}' to track progression stages and trust evolution."],
                        challenge_intent=["Omit arcs if relationships are static or purely functional."],
                    ),
                )
            )

    return diagnostics


def _diagnose_texture_uniqueness(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    texture_fields = ["gestures", "rituals", "social_habits", "behavioral_tells"]
    for field in texture_fields:
        by_item: dict[str, list[str]] = {}
        for char in blueprint.characters:
            identity = _load_identity(char)
            if identity is None or identity.texture is None:
                continue
            items = getattr(identity.texture, field, None)
            if not items:
                continue
            for item in items:
                key = item.strip().lower()
                by_item.setdefault(key, []).append(char.name)

        for item_text, char_names in by_item.items():
            if len(char_names) > 1:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule=f"character.texture.{field}.duplicate",
                        message=f"Duplicate {field} ('{item_text}') across characters: {', '.join(char_names)}.",
                        evidence=[
                            f"characters = {char_names}",
                            f"duplicate_{field} = {item_text}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[f"Differentiate the '{item_text}' {field} for each character, or assign unique behavioral details."],
                            challenge_intent=["Keep duplicate if the behavior is intentionally shared (cultural or group trait)."],
                        ),
                    )
                )

    return diagnostics


def _diagnose_defense_controlled(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    valid_values = {v.value for v in DefenseMechanism}
    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity is None or identity.psychology is None:
            continue
        for dm in identity.psychology.defense_mechanisms:
            dm_str = dm.value if hasattr(dm, "value") else str(dm)
            if dm_str not in valid_values:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="character.psychology.defense_not_controlled",
                        message=f"Character '{char.name}' has defense mechanism '{dm_str}' which is not in the controlled vocabulary.",
                        evidence=[f"character.name = {char.name}", f"defense_mechanism = {dm_str}"],
                        repair_options=RepairOptions(
                            preserve_intent=[f"Replace '{dm_str}' with a DefenseMechanism enum value from {sorted(valid_values)}."],
                            challenge_intent=["Keep free-text if the controlled vocabulary lacks the needed term."],
                        ),
                    )
                )

    return diagnostics


def _diagnose_intimacy_presence(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        if char.role.value not in ("protagonist", "antagonist", "deuteragonist"):
            continue
        identity = _load_identity(char)
        if identity is None or identity.psychology is None:
            continue
        if identity.psychology.intimacy is None:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.psychology.intimacy_missing",
                    message=f"Character '{char.name}' ({char.role.value}) has no intimacy requirements defined.",
                    evidence=[f"character.name = {char.name}", "psychology.intimacy is absent"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Add intimacy requirements for '{char.name}' with access pattern, safety prerequisites, and trust triggers/blocks."],
                        challenge_intent=["Omit if the character's emotional access patterns are not central to the story."],
                    ),
                )
            )
            continue
        intimacy = identity.psychology.intimacy
        if intimacy.caregiving.openness <= 0.1:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.psychology.caregiving_closed",
                    message=f"Character '{char.name}' ({char.role.value}) has very low caregiving openness ({intimacy.caregiving.openness}). Consider whether this is intentional.",
                    evidence=[f"character.name = {char.name}", f"caregiving.openness = {intimacy.caregiving.openness}"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Set caregiving openness higher if '{char.name}' is meant to provide nurture."],
                        challenge_intent=["Keep low if the character is emotionally closed even in caregiving contexts."],
                    ),
                )
            )
        if intimacy.romantic.openness <= 0.1 and intimacy.romantic.dependency_willingness <= 0.1:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.psychology.romantic_closed",
                    message=f"Character '{char.name}' ({char.role.value}) has very low romantic openness and dependency willingness. They may resist intimacy that requires emotional need.",
                    evidence=[f"character.name = {char.name}", f"romantic.openness = {intimacy.romantic.openness}", f"romantic.dependency_willingness = {intimacy.romantic.dependency_willingness}"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Adjust romantic openness or dependency willingness if '{char.name}' is meant to form close bonds."],
                        challenge_intent=["Keep low if the character's arc involves learning to depend on others."],
                    ),
                )
            )

    return diagnostics


def _diagnose_relationship_arc_progression(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity is None or identity.relationship_mesh is None:
            continue
        mesh = identity.relationship_mesh
        for arc in mesh.arcs:
            if not arc.stages and arc.trust_level > 0:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="character.relationship.arc.stages_missing",
                        message=f"Relationship arc for '{char.name}' -> '{arc.other}' has a trust level ({arc.trust_level}) but no stages defined.",
                        evidence=[f"character.name = {char.name}", f"relationship.other = {arc.other}", f"trust_level = {arc.trust_level}"],
                        repair_options=RepairOptions(
                            preserve_intent=[f"Add RelationshipArcStage entries to the arc between '{char.name}' and '{arc.other}'."],
                            challenge_intent=["Keep if the relationship arc is intentionally simple or background."],
                        ),
                    )
                )

            if arc.trust_level <= 0.3 and arc.progression_type and arc.progression_type in ("trust_based", "gradual"):
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="character.relationship.arc.trust_progression_mismatch",
                        message=f"Relationship arc for '{char.name}' -> '{arc.other}' has low trust ({arc.trust_level}) but a trust-building progression type. Consider aligning them.",
                        evidence=[f"character.name = {char.name}", f"relationship.other = {arc.other}", f"trust_level = {arc.trust_level}", f"progression_type = {arc.progression_type}"],
                        repair_options=RepairOptions(
                            preserve_intent=["Increase trust level or change progression type to match the current trust state."],
                            challenge_intent=["Keep if low trust with trust-building progression represents an early-stage arc."],
                        ),
                    )
                )

            if arc.stages and len(arc.stages) <= 2 and arc.trust_level > 0.7:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="character.relationship.arc.few_stages_high_trust",
                        message=f"Relationship arc for '{char.name}' -> '{arc.other}' has high trust ({arc.trust_level}) but only {len(arc.stages)} stage(s). High-trust relationships typically need more stages to feel earned.",
                        evidence=[f"character.name = {char.name}", f"relationship.other = {arc.other}", f"stages = {[str(s) for s in arc.stages]}", f"trust_level = {arc.trust_level}"],
                        repair_options=RepairOptions(
                            preserve_intent=[f"Add intermediary stages to the arc between '{char.name}' and '{arc.other}' to show how trust was built."],
                            challenge_intent=["Keep if the relationship achieved high trust quickly (shared crisis, lifelong bond)."],
                        ),
                    )
                )

    return diagnostics


def _diagnose_contradiction_depth(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    for char in blueprint.characters:
        if char.role.value not in ("protagonist", "antagonist", "deuteragonist"):
            continue
        identity = _load_identity(char)
        if identity is None:
            continue
        if identity.psychology is None or not identity.psychology.contradictions:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.psychology.contradictions_missing",
                    message=f"Character '{char.name}' ({char.role.value}) has no contradictions defined. Contradictions prevent characters from feeling procedurally assembled.",
                    evidence=[f"character.name = {char.name}", "psychology.contradictions is empty"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Add 2-3 contradictions for '{char.name}' that create tension between their vulnerability, defenses, and role. E.g. 'driven_but_vulnerable', 'fears_connection_yet_needs_it'."],
                        challenge_intent=["Omit if the character is intentionally simple or archetypal."],
                    ),
                )
            )
            continue

        if len(identity.psychology.contradictions) < 2:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.INFO,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="character.psychology.contradictions_few",
                    message=f"Character '{char.name}' has only {len(identity.psychology.contradictions)} contradiction(s). Primary characters benefit from 2-3 to feel layered.",
                    evidence=[f"character.name = {char.name}", f"psychology.contradictions = {identity.psychology.contradictions}"],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Add additional contradictions for '{char.name}' that create richer internal tension."],
                        challenge_intent=["Keep minimal if the character's simplicity is intentional."],
                    ),
                )
            )

        safe_patterns = {"nice_but_polite", "kind_but_firm", "strong_but_gentle", "smart_but_humble"}
        for c in identity.psychology.contradictions:
            if c.strip().lower() in safe_patterns:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.INFO,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="character.psychology.contradiction_safe",
                        message=f"Character '{char.name}' has a contradiction '{c}' that does not create meaningful tension. Contradictions should pull the character in opposing directions.",
                        evidence=[f"character.name = {char.name}", f"contradiction = {c}"],
                        repair_options=RepairOptions(
                            preserve_intent=[f"Replace '{c}' with a contradiction that creates real internal conflict, e.g. 'driven_but_vulnerable' or 'fears_connection_yet_needs_it'."],
                            challenge_intent=["Keep if the safe contradiction is ironic or contextually meaningful."],
                        ),
                    )
                )

    return diagnostics


def _diagnose_adaptation_divergence(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []

    by_vulnerability: dict[str, list[tuple[str, Character]]] = {}
    for char in blueprint.characters:
        identity = _load_identity(char)
        if identity is None or identity.psychology is None or identity.psychology.vulnerability_family is None:
            continue
        vuln = identity.psychology.vulnerability_family.value
        by_vulnerability.setdefault(vuln, []).append((char.name, char))

    for vuln, chars in by_vulnerability.items():
        if len(chars) < 2:
            continue

        pairs_checked: set[tuple[str, str]] = set()
        for i, (name_a, char_a) in enumerate(chars):
            for j, (name_b, char_b) in enumerate(chars):
                if i >= j:
                    continue
                key = tuple(sorted([name_a, name_b]))
                if key in pairs_checked:
                    continue
                pairs_checked.add(key)

                id_a = _load_identity(char_a)
                id_b = _load_identity(char_b)
                if id_a is None or id_b is None:
                    continue
                defenses_a = {d.value for d in id_a.psychology.defense_mechanisms} if id_a.psychology else set()
                defenses_b = {d.value for d in id_b.psychology.defense_mechanisms} if id_b.psychology else set()

                if not defenses_a or not defenses_b:
                    continue

                intersection = defenses_a & defenses_b
                min_defenses = min(len(defenses_a), len(defenses_b))
                overlap_ratio = len(intersection) / min_defenses if min_defenses > 0 else 0

                if overlap_ratio > 0.5:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.INFO,
                            layer=DiagnosticLayer.STRUCTURAL_FORCES,
                            rule="character.adaptation.convergence",
                            message=f"'{name_a}' and '{name_b}' share vulnerability '{vuln}' but use very similar defense mechanisms ({overlap_ratio:.0%} overlap). Consider differentiating their adaptations to the same wound.",
                            evidence=[
                                f"vulnerability = {vuln}",
                                f"character_a = {name_a} defenses = {sorted(defenses_a)}",
                                f"character_b = {name_b} defenses = {sorted(defenses_b)}",
                                f"overlap = {len(intersection)}/{min_defenses}",
                            ],
                            repair_options=RepairOptions(
                                preserve_intent=[f"Differentiate '{name_a}' and '{name_b}' by giving at least one divergent defense mechanism so they represent different adaptations to the same vulnerability."],
                                challenge_intent=["Keep convergence if the shared adaptation is intentional (cultural, familial, or organizational)."],
                            ),
                        )
                    )

    return diagnostics
