"""Categorization engine — infers character identity from existing data.

The CategorizationEngine provides:
- Default archetype suggestions based on CharacterRole and ArcType
- Relationship signature inference from character states
- Automatic trope tagging based on arc/milestone patterns
- Role inference from graph-like relationship analysis
- Identity proposal generation (for manual review)
"""

from __future__ import annotations

from auteur.blueprint import Character, CharacterRole, StoryBlueprint
from auteur.character.enums import (
    Archetype,
    DramaticFunction,
    MoralAlignment,
    RelationshipType,
    TropeTag,
)
from auteur.character.models import (
    CharacterCategorization,
    CharacterIdentity,
    RelationshipSignature,
    RoleInference,
)


class CategorizationEngine:
    def __init__(self, blueprint: StoryBlueprint) -> None:
        self.blueprint = blueprint

    def propose_identity_for(self, char: Character) -> CharacterIdentity:
        return CharacterIdentity(
            archetype=self._suggest_archetype(char),
            moral_alignment=self._suggest_alignment(char),
            dramatic_functions=self._suggest_dramatic_functions(char),
            trope_tags=self._suggest_trope_tags(char),
        )

    def propose_categorization_for(self, char: Character) -> CharacterCategorization:
        identity = self.propose_identity_for(char)
        return CharacterCategorization(
            identity=identity,
            relationship_signatures=self._infer_relationship_signatures(char),
            role_inferences=self._infer_roles(char),
        )

    def categorize_all(self) -> dict[str, CharacterCategorization]:
        result: dict[str, CharacterCategorization] = {}
        for char in self.blueprint.characters:
            result[char.name] = self.propose_categorization_for(char)
        return result

    def _suggest_archetype(self, char: Character) -> Archetype | None:
        role_archetypes: dict[CharacterRole, Archetype] = {
            CharacterRole.PROTAGONIST: Archetype.HERO,
            CharacterRole.ANTAGONIST: Archetype.VILLAIN,
            CharacterRole.MENTOR: Archetype.MENTOR,
            CharacterRole.ALLY: Archetype.ALLY,
            CharacterRole.DEUTERAGONIST: Archetype.ALLY,
            CharacterRole.FOIL: Archetype.FOIL,
            CharacterRole.SUPPORTING: Archetype.EVERYMAN,
        }
        return role_archetypes.get(char.role)

    def _suggest_alignment(self, char: Character) -> MoralAlignment | None:
        role_alignments: dict[CharacterRole, MoralAlignment] = {
            CharacterRole.PROTAGONIST: MoralAlignment.NEUTRAL_GOOD,
            CharacterRole.ANTAGONIST: MoralAlignment.NEUTRAL_EVIL,
            CharacterRole.MENTOR: MoralAlignment.LAWFUL_GOOD,
            CharacterRole.ALLY: MoralAlignment.NEUTRAL_GOOD,
            CharacterRole.FOIL: MoralAlignment.TRUE_NEUTRAL,
        }
        return role_alignments.get(char.role)

    def _suggest_dramatic_functions(self, char: Character) -> list[DramaticFunction]:
        role_functions: dict[CharacterRole, list[DramaticFunction]] = {
            CharacterRole.PROTAGONIST: [DramaticFunction.EMOTIONAL_ANCHOR, DramaticFunction.AUDIENCE_SURROGATE],
            CharacterRole.DEUTERAGONIST: [DramaticFunction.EMOTIONAL_ANCHOR],
            CharacterRole.ANTAGONIST: [DramaticFunction.IDEOLOGICAL_OPPOSITION, DramaticFunction.CATALYST],
            CharacterRole.MENTOR: [DramaticFunction.MENTOR, DramaticFunction.VOICE_OF_REASON],
            CharacterRole.ALLY: [DramaticFunction.LOYAL_COMPANION],
            CharacterRole.FOIL: [DramaticFunction.SHADOW],
            CharacterRole.SUPPORTING: [DramaticFunction.COMIC_RELIEF],
        }
        return role_functions.get(char.role, [])

    def _suggest_trope_tags(self, char: Character) -> list[TropeTag]:
        tags: list[TropeTag] = []

        arc_trope_map = {
            "redemption": TropeTag.REDEMPTION_ARC,
            "corruption": TropeTag.CORRUPTION_ARC,
            "fall": TropeTag.FALLEN_HERO,
            "disillusionment": TropeTag.FALLEN_HERO,
        }
        if char.arc_type.value in arc_trope_map:
            tags.append(arc_trope_map[char.arc_type.value])

        if char.role == CharacterRole.PROTAGONIST:
            if any("fear" in (m.description or "").lower() for m in char.key_milestones):
                tags.append(TropeTag.HERO_WITH_FEAR)

        has_betrayal = any("betray" in (m.description or "").lower() for m in char.key_milestones)
        if has_betrayal:
            tags.append(TropeTag.BETRAYAL)

        return tags

    def _infer_relationship_signatures(self, char: Character) -> list[RelationshipSignature]:
        signatures: list[RelationshipSignature] = []

        for rel in char.current_state.relationships:
            rel_type = self._map_relationship_kind(rel.kind)
            signatures.append(
                RelationshipSignature(
                    other=rel.other,
                    type=rel_type,
                    intensity=rel.intensity,
                )
            )

        return signatures

    def _map_relationship_kind(self, kind: str) -> RelationshipType:
        kind_lower = kind.strip().lower()
        mapping: dict[str, RelationshipType] = {
            "trust": RelationshipType.TRUST,
            "fear": RelationshipType.FEAR,
            "rivalry": RelationshipType.RIVALRY,
            "love": RelationshipType.LOVE,
            "hate": RelationshipType.HATE,
            "friendship": RelationshipType.FRIENDSHIP,
            "ally": RelationshipType.ALLIANCE,
            "alliance": RelationshipType.ALLIANCE,
            "loyalty": RelationshipType.LOYALTY,
            "respect": RelationshipType.RESPECT,
            "mentor": RelationshipType.MENTORSHIP,
            "mentorship": RelationshipType.MENTORSHIP,
            "betrayal": RelationshipType.BETRAYAL,
            "deception": RelationshipType.DECEPTION,
            "manipulation": RelationshipType.MANIPULATION,
            "obsession": RelationshipType.OBSESSION,
            "rival": RelationshipType.RIVALRY,
            "enemy": RelationshipType.ENMITY,
            "friend": RelationshipType.FRIENDSHIP,
            "family": RelationshipType.FAMILIAL_LOVE,
            "parent": RelationshipType.FAMILIAL_LOVE,
            "sibling": RelationshipType.FAMILIAL_LOVE,
            "romance": RelationshipType.ROMANTIC_LOVE,
            "lover": RelationshipType.ROMANTIC_LOVE,
            "protege": RelationshipType.PROTEGE,
        }
        return mapping.get(kind_lower, RelationshipType.ALLIANCE)

    def _infer_roles(self, char: Character) -> list[RoleInference]:
        inferences: list[RoleInference] = []

        if char.role == CharacterRole.PROTAGONIST:
            inferences.append(
                RoleInference(
                    inferred_role="primary_pov",
                    confidence=0.9,
                    evidence=["Character has protagonist role assigned."],
                    reasoning="Protagonist is the primary POV and emotional anchor by convention.",
                )
            )

        outgoing = [r for r in char.current_state.relationships if r.intensity > 0.5]
        if outgoing and len(outgoing) >= 2:
            inferences.append(
                RoleInference(
                    inferred_role="social_hub",
                    confidence=min(0.7, len(outgoing) * 0.15),
                    evidence=[f"Has {len(outgoing)} high-intensity relationships."],
                    reasoning="Characters with many strong relationships act as social hubs.",
                )
            )

        return inferences
