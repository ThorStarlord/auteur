"""Categorization engine — infers layered character identity from existing data."""

from __future__ import annotations

from auteur.blueprint import Character, CharacterRole, StoryBlueprint
from auteur.character.enums import (
    Archetype,
    DramaticFunction,
    RelationshipType,
    TropeTag,
)
from auteur.character.models import (
    ArcChange,
    ArcEngine,
    ArchetypalLayer,
    CharacterCategorization,
    CharacterIdentity,
    PsychologicalLayer,
    RelationshipMesh,
    RelationshipSignature,
    RoleInference,
    StructuralRole,
    TextureLayer,
    TextureVoice,
)


class CategorizationEngine:
    def __init__(self, blueprint: StoryBlueprint) -> None:
        self.blueprint = blueprint

    def propose_identity_for(self, char: Character) -> CharacterIdentity:
        return CharacterIdentity(
            narrative_role=self._propose_narrative_role(char),
            archetype=self._propose_archetype_layer(char),
            psychology=self._propose_psychology(char),
            arc=self._propose_arc(char),
            personality_traits=self._suggest_personality_traits(char),
            trope_tags=self._suggest_trope_tags(char),
        )

    def propose_categorization_for(self, char: Character) -> CharacterCategorization:
        return CharacterCategorization(
            identity=self.propose_identity_for(char),
            relationship_signatures=self._infer_relationship_signatures(char),
            role_inferences=self._infer_roles(char),
        )

    def categorize_all(self) -> dict[str, CharacterCategorization]:
        return {
            char.name: self.propose_categorization_for(char)
            for char in self.blueprint.characters
        }

    # -- Narrative Role layer --

    def _propose_narrative_role(self, char: Character) -> StructuralRole | None:
        secondary = self._suggest_dramatic_functions(char)
        return StructuralRole(secondary=secondary) if secondary else None

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

    # -- Archetype layer --

    def _propose_archetype_layer(self, char: Character) -> ArchetypalLayer | None:
        core = self._suggest_archetype(char)
        return ArchetypalLayer(core=core) if core else None

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

    # -- Psychology layer --

    def _propose_psychology(self, char: Character) -> PsychologicalLayer | None:
        contradictions = self._suggest_contradictions(char)
        return PsychologicalLayer(contradictions=contradictions) if contradictions else None

    def _suggest_contradictions(self, char: Character) -> list[str]:
        contradictions: list[str] = []
        if char.role == CharacterRole.PROTAGONIST:
            contradictions.append("driven_but_vulnerable")
        if char.role == CharacterRole.ANTAGONIST:
            contradictions.append("purposeful_but_destructive")
        if char.role == CharacterRole.MENTOR:
            contradictions.append("wise_but_limited")
        return contradictions

    # -- Arc layer --

    def _propose_arc(self, char: Character) -> ArcEngine | None:
        change = self._suggest_arc_change(char)
        return ArcEngine(positive_change=change) if change else None

    def _suggest_arc_change(self, char: Character) -> ArcChange | None:
        arc_from: dict[str, tuple[str, str]] = {
            "growth": ("naivety", "wisdom"),
            "redemption": ("guilt", "peace"),
            "healing": ("broken", "whole"),
            "disillusionment": ("idealistic", "grounded"),
            "corruption": ("driven", "consumed"),
            "fall": ("proud", "fallen"),
        }
        pair = arc_from.get(char.arc_type.value)
        if pair:
            return ArcChange(from_=pair[0], to=pair[1])
        return None

    # -- Personality / alignment (legacy) --

    def _suggest_personality_traits(self, char: Character) -> list[str]:
        return []

    # -- Trope tags --

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
        if any("betray" in (m.description or "").lower() for m in char.key_milestones):
            tags.append(TropeTag.BETRAYAL)
        return tags

    # -- Relationship inference --

    def _infer_relationship_signatures(self, char: Character) -> list[RelationshipSignature]:
        signatures: list[RelationshipSignature] = []
        for rel in char.current_state.relationships:
            signatures.append(
                RelationshipSignature(
                    other=rel.other,
                    type=self._map_relationship_kind(rel.kind),
                    intensity=rel.intensity,
                )
            )
        return signatures

    def _map_relationship_kind(self, kind: str) -> RelationshipType:
        kind_lower = kind.strip().lower()
        mapping: dict[str, RelationshipType] = {
            "trust": RelationshipType.TRUST, "fear": RelationshipType.FEAR,
            "rivalry": RelationshipType.RIVALRY, "love": RelationshipType.LOVE,
            "hate": RelationshipType.HATE, "friendship": RelationshipType.FRIENDSHIP,
            "ally": RelationshipType.ALLIANCE, "alliance": RelationshipType.ALLIANCE,
            "loyalty": RelationshipType.LOYALTY, "respect": RelationshipType.RESPECT,
            "mentor": RelationshipType.MENTORSHIP, "mentorship": RelationshipType.MENTORSHIP,
            "betrayal": RelationshipType.BETRAYAL, "deception": RelationshipType.DECEPTION,
            "manipulation": RelationshipType.MANIPULATION, "obsession": RelationshipType.OBSESSION,
            "rival": RelationshipType.RIVALRY, "enemy": RelationshipType.ENMITY,
            "friend": RelationshipType.FRIENDSHIP, "family": RelationshipType.FAMILIAL_LOVE,
            "parent": RelationshipType.FAMILIAL_LOVE, "sibling": RelationshipType.FAMILIAL_LOVE,
            "romance": RelationshipType.ROMANTIC_LOVE, "lover": RelationshipType.ROMANTIC_LOVE,
            "protege": RelationshipType.PROTEGE,
        }
        return mapping.get(kind_lower, RelationshipType.ALLIANCE)

    # -- Role inference --

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
        if len(outgoing) >= 2:
            inferences.append(
                RoleInference(
                    inferred_role="social_hub",
                    confidence=min(0.7, len(outgoing) * 0.15),
                    evidence=[f"Has {len(outgoing)} high-intensity relationships."],
                    reasoning="Characters with many strong relationships act as social hubs.",
                )
            )
        return inferences
