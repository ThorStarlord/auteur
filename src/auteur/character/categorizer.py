"""Categorization engine — infers layered character identity from existing data."""

from __future__ import annotations

from auteur.blueprint import Character, CharacterRole, StoryBlueprint
from auteur.character.enums import (
    Archetype,
    DefenseMechanism,
    DramaticFunction,
    EssenceTraitSource,
    IntimacyAccess,
    MotifType,
    PhilosophyTag,
    RelationshipType,
    RelationshipArcStage,
    TropeTag,
    TrustProgressionType,
    ValidationSource,
    VulnerabilityFamily,
)
from auteur.character.models import (
    ArcChange,
    ArcEngine,
    ArchetypalLayer,
    CaregivingAccess,
    CharacterCategorization,
    CharacterIdentity,
    EssenceProfile,
    EssenceTrait,
    IdeologicalProfile,
    IntimacyRequirements,
    Motif,
    MotifProfile,
    PsychologicalLayer,
    RelationshipArc,
    RelationshipMesh,
    RelationshipSignature,
    RoleInference,
    RomanticAccess,
    SceneEnergySignature,
    StructuralRole,
    TextureLayer,
    TextureVoice,
)

CharacterIdentity.model_rebuild()


class CategorizationEngine:
    def __init__(self, blueprint: StoryBlueprint) -> None:
        self.blueprint = blueprint

    def propose_identity_for(self, char: Character) -> CharacterIdentity:
        return CharacterIdentity(
            narrative_role=self._propose_narrative_role(char),
            archetype=self._propose_archetype_layer(char),
            psychology=self._propose_psychology(char),
            texture=self._propose_texture(char),
            ideology=self._propose_ideology(char),
            essence=self._propose_essence(char),
            motifs=self._propose_motifs(char),
            arc=self._propose_arc(char),
            relationship_mesh=self._propose_relationship_mesh(char),
            personality_traits=self._suggest_personality_traits(char),
            trope_tags=self._suggest_trope_tags(char),
        )

    def propose_categorization_for(self, char: Character) -> CharacterCategorization:
        return CharacterCategorization(
            identity=self.propose_identity_for(char),
            relationship_signatures=self._infer_relationship_signatures(char),
            role_inferences=self._infer_roles(char),
            scene_energy=self._infer_scene_energy(char),
        )

    def _infer_scene_energy(self, char: Character) -> SceneEnergySignature | None:
        ident = self.propose_identity_for(char)
        if ident is None:
            return None
        role = char.role

        role_atmosphere: dict[CharacterRole, list[str]] = {
            CharacterRole.PROTAGONIST: ["earnest_pressure", "narrative_gravity"],
            CharacterRole.ANTAGONIST: ["executive_pressure", "emotional_distance", "unpredictable_tension"],
            CharacterRole.MENTOR: ["warm_authority", "reflective_calm"],
            CharacterRole.FOIL: ["unsettling_calm", "mirrored_tension"],
            CharacterRole.ALLY: ["reassuring_warmth"],
            CharacterRole.SUPPORTING: ["unremarkable_presence"],
            CharacterRole.DEUTERAGONIST: ["quiet_intensity", "secondary_gravity"],
        }

        role_pressure: dict[CharacterRole, list[str]] = {
            CharacterRole.PROTAGONIST: ["silent_expectation", "earnest_demand"],
            CharacterRole.ANTAGONIST: ["direct_command", "emotional_withholding", "silent_judgment"],
            CharacterRole.MENTOR: ["gentle_redirection", "question_based"],
            CharacterRole.FOIL: ["challenging_quiet", "indirect_prodding"],
            CharacterRole.ALLY: ["warm_encouragement", "supportive_silence"],
            CharacterRole.SUPPORTING: ["deferential_waiting"],
            CharacterRole.DEUTERAGONIST: ["steady_presence", "occasional_challenge"],
        }

        role_silence: dict[CharacterRole, list[str]] = {
            CharacterRole.PROTAGONIST: ["expectant", "charged"],
            CharacterRole.ANTAGONIST: ["heavy", "tense", "calculating"],
            CharacterRole.MENTOR: ["comfortable", "inviting"],
            CharacterRole.FOIL: ["uncomfortable", "questioning"],
            CharacterRole.ALLY: ["comfortable", "supportive"],
            CharacterRole.SUPPORTING: ["neutral", "invisible"],
            CharacterRole.DEUTERAGONIST: ["thoughtful", "patient"],
        }

        role_spatial: dict[CharacterRole, list[str]] = {
            CharacterRole.PROTAGONIST: ["occupies_center", "moves_through_spaces_assertively"],
            CharacterRole.ANTAGONIST: ["controls_thresholds", "occupies_territory", "restricts_access"],
            CharacterRole.MENTOR: ["occupies_controlled_spaces", "invites_others_in"],
            CharacterRole.FOIL: ["mirrors_protagonist_position", "hovers_at_edges"],
            CharacterRole.ALLY: ["stands_beside", "shares_space_easily"],
            CharacterRole.SUPPORTING: ["hovers_periphery", "fades_into_background"],
            CharacterRole.DEUTERAGONIST: ["claims_secondary_focus", "moves_independently"],
        }

        def add_or_none(mapping: dict[CharacterRole, list[str]]) -> list[str]:
            return mapping.get(role, [])

        atmosphere = add_or_none(role_atmosphere)
        pressure = add_or_none(role_pressure)
        silence = add_or_none(role_silence)
        spatial = add_or_none(role_spatial)

        if ident.archetype and ident.archetype.core:
            arch_val = ident.archetype.core.value
            if arch_val in ("avenger", "destroyer", "shadow"):
                atmosphere.append("suppressed_rage")
            elif arch_val in ("healer", "wise_elder", "oracle"):
                atmosphere.append("meditative_presence")
            elif arch_val in ("ruler", "guardian"):
                pressure.append("inevitable_authority")
            elif arch_val in ("trickster", "shapeshifter"):
                silence.append("playful_uncertainty")

        if ident.psychology and ident.psychology.defense_mechanisms:
            defense_labels = {d.value for d in ident.psychology.defense_mechanisms}
            if "intellectualization" in defense_labels:
                silence.append("analytic_pause")
                spatial.append("maintains_distance")
            if "compartmentalization" in defense_labels:
                pressure.append("controlled_transitions")
            if "grandiosity" in defense_labels:
                spatial.append("expands_to_fill_room")
            if "humor" in defense_labels:
                pressure.append("deflection_through_levity")
            if "emotional_filtering" in defense_labels:
                silence.append("filtered_stillness")

        return SceneEnergySignature(
            default_atmosphere=atmosphere[:4],
            pressure_style=pressure[:3],
            silence_quality=silence[:3],
            spatial_behavior=spatial[:3],
            interruption_pattern=self._infer_interruption_pattern(char, ident),
            gaze_control=self._infer_gaze_control(char, ident),
        )

    def _infer_interruption_pattern(self, char: Character, ident: CharacterIdentity) -> str | None:
        if char.role == CharacterRole.ANTAGONIST:
            return "frequent"
        if char.role == CharacterRole.PROTAGONIST:
            return "occasional"
        if char.role == CharacterRole.MENTOR:
            return "rare"
        if char.role == CharacterRole.SUPPORTING:
            return "never"
        if ident.psychology and any(d.value == "withdrawal" for d in ident.psychology.defense_mechanisms):
            return "never"
        if ident.psychology and any(d.value == "performative_competence" for d in ident.psychology.defense_mechanisms):
            return "strategic"
        return "deferential"

    def _infer_gaze_control(self, char: Character, ident: CharacterIdentity) -> str | None:
        if char.role == CharacterRole.ANTAGONIST:
            return "holding"
        if char.role == CharacterRole.PROTAGONIST:
            return "measuring"
        if char.role == CharacterRole.MENTOR:
            return "warm_steady"
        if char.role == CharacterRole.SUPPORTING:
            return "avoidant"
        if ident.psychology and any(d.value == "intellectualization" for d in ident.psychology.defense_mechanisms):
            return "observational"
        if ident.psychology and any(d.value == "grandiosity" for d in ident.psychology.defense_mechanisms):
            return "penetrating"
        return "occasional_contact"

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
        vulnerability = self._suggest_vulnerability_family(char)
        defenses = self._suggest_defense_mechanisms(char)
        validation = self._suggest_validation_sources(char)
        intimacy = self._suggest_intimacy(char)
        if not contradictions and not vulnerability and not defenses and not intimacy and not validation:
            return None
        return PsychologicalLayer(
            contradictions=contradictions,
            vulnerability_family=vulnerability,
            defense_mechanisms=defenses,
            validation_dependency=validation,
            intimacy=intimacy,
        )

    def _suggest_contradictions(self, char: Character) -> list[str]:
        contradictions: list[str] = []
        vuln = self._suggest_vulnerability_family(char)
        defenses = self._suggest_defense_mechanisms(char)

        role_tensions: dict[CharacterRole, list[str]] = {
            CharacterRole.PROTAGONIST: [
                "driven_but_vulnerable",
                "seeks_control_but_fears_exposure",
            ],
            CharacterRole.ANTAGONIST: [
                "purposeful_but_destructive",
                "craves_order_but_creates_chaos",
            ],
            CharacterRole.DEUTERAGONIST: [
                "loyal_but_emotionally_distant",
                "fears_connection_yet_needs_it",
            ],
            CharacterRole.MENTOR: [
                "wise_but_limited",
                "guides_others_cannot_save_self",
            ],
            CharacterRole.FOIL: [
                "mirrors_protagonist_but_chooses_differently",
                "competent_but_misdirected",
            ],
            CharacterRole.ALLY: [
                "supportive_but_has_own_limits",
                "brave_but_uncertain",
            ],
            CharacterRole.SUPPORTING: [
                "present_but_peripheral",
                "observes_more_than_acts",
            ],
        }
        contradictions.extend(role_tensions.get(char.role, []))

        if vuln is not None:
            vuln_contradictions: dict[VulnerabilityFamily, str] = {
                VulnerabilityFamily.STATUS_CONTROL: "needs_status_but_distrusts_approval",
                VulnerabilityFamily.ABANDONMENT: "fears_abandonment_yet_pushes_away",
                VulnerabilityFamily.SHAME: "craves_visibility_but_dreads_judgment",
                VulnerabilityFamily.POWERLESSNESS: "wants_power_but_avoids_responsibility",
                VulnerabilityFamily.INADEQUACY: "overcompensates_while_feeling_unworthy",
                VulnerabilityFamily.BETRAYAL: "longs_for_trust_but_expects_betrayal",
                VulnerabilityFamily.REJECTION: "seeks_connection_but_braces_for_rejection",
                VulnerabilityFamily.LOSS: "clings_to_control_fearing_loss",
                VulnerabilityFamily.ABSORPTION: "fears_losing_self_in_relationships",
                VulnerabilityFamily.ISOLATION: "craves_belonging_but_keeps_distance",
                VulnerabilityFamily.DISSOLUTION: "fears_falling_apart_so_holds_too_tight",
                VulnerabilityFamily.INVISIBILITY: "wants_to_matter_but_hides",
            }
            contradiction = vuln_contradictions.get(vuln)
            if contradiction and contradiction not in contradictions:
                contradictions.append(contradiction)

        if defenses:
            defense_labels = {d.value for d in defenses}
            if "intellectualization" in defense_labels:
                c = "feels_deeply_but_analyzes_instead"
                if c not in contradictions:
                    contradictions.append(c)
            if "compartmentalization" in defense_labels:
                c = "protects_self_by_fragmenting_identity"
                if c not in contradictions:
                    contradictions.append(c)
            if "altruism" in defense_labels or "performative_competence" in defense_labels:
                c = "cares_for_others_neglects_self"
                if c not in contradictions:
                    contradictions.append(c)
            if "grandiosity" in defense_labels:
                c = "feels_superior_yet_deeply_insecure"
                if c not in contradictions:
                    contradictions.append(c)

        return contradictions[:4]

    def _suggest_vulnerability_family(self, char: Character) -> VulnerabilityFamily | None:
        role_vulnerability: dict[CharacterRole, VulnerabilityFamily] = {
            CharacterRole.PROTAGONIST: VulnerabilityFamily.INADEQUACY,
            CharacterRole.ANTAGONIST: VulnerabilityFamily.STATUS_CONTROL,
            CharacterRole.MENTOR: VulnerabilityFamily.ISOLATION,
            CharacterRole.FOIL: VulnerabilityFamily.SHAME,
            CharacterRole.ALLY: VulnerabilityFamily.ABANDONMENT,
            CharacterRole.SUPPORTING: VulnerabilityFamily.POWERLESSNESS,
            CharacterRole.DEUTERAGONIST: VulnerabilityFamily.LOSS,
        }
        return role_vulnerability.get(char.role)

    def _suggest_defense_mechanisms(self, char: Character) -> list[DefenseMechanism]:
        role_defenses: dict[CharacterRole, list[DefenseMechanism]] = {
            CharacterRole.PROTAGONIST: [DefenseMechanism.INTELLECTUALIZATION, DefenseMechanism.SUPPRESSION],
            CharacterRole.ANTAGONIST: [DefenseMechanism.COMPARTMENTALIZATION, DefenseMechanism.TRANSACTIONAL_CONTAINMENT],
            CharacterRole.MENTOR: [DefenseMechanism.RATIONALIZATION, DefenseMechanism.SUBLIMATION],
            CharacterRole.FOIL: [DefenseMechanism.HUMOR, DefenseMechanism.PROJECTION],
            CharacterRole.ALLY: [DefenseMechanism.ALTRUISM],
            CharacterRole.SUPPORTING: [DefenseMechanism.DENIAL, DefenseMechanism.AVOIDANCE],
            CharacterRole.DEUTERAGONIST: [DefenseMechanism.INTELLECTUALIZATION],
        }
        return role_defenses.get(char.role, [])

    def _suggest_validation_sources(self, char: Character) -> list[ValidationSource]:
        role_validation: dict[CharacterRole, list[ValidationSource]] = {
            CharacterRole.PROTAGONIST: [ValidationSource.EXTERNAL_NEEDED, ValidationSource.SERVICE],
            CharacterRole.ANTAGONIST: [ValidationSource.STATUS, ValidationSource.AUTONOMY],
            CharacterRole.MENTOR: [ValidationSource.ACHIEVEMENT, ValidationSource.RELATIONSHIPS],
            CharacterRole.FOIL: [ValidationSource.PERFORMANCE, ValidationSource.EXTERNAL_NEEDED],
            CharacterRole.ALLY: [ValidationSource.RELATIONSHIPS, ValidationSource.SERVICE],
            CharacterRole.SUPPORTING: [ValidationSource.SELF_VALIDATION],
            CharacterRole.DEUTERAGONIST: [ValidationSource.SERVICE, ValidationSource.RELATIONSHIPS],
        }
        return role_validation.get(char.role, [])

    def _suggest_intimacy(self, char: Character) -> IntimacyRequirements | None:
        role_access: dict[CharacterRole, IntimacyAccess] = {
            CharacterRole.PROTAGONIST: IntimacyAccess.GUARDED_PROGRESSIVE,
            CharacterRole.ANTAGONIST: IntimacyAccess.TRANSACTIONAL,
            CharacterRole.DEUTERAGONIST: IntimacyAccess.OPEN_CAUTIOUS,
            CharacterRole.MENTOR: IntimacyAccess.RITUALISTIC,
            CharacterRole.FOIL: IntimacyAccess.CONTESTED,
        }
        access = role_access.get(char.role)
        if access is None:
            return None
        return IntimacyRequirements(
            access_pattern=access,
            caregiving=CaregivingAccess(
                openness=0.8 if char.role in (CharacterRole.PROTAGONIST, CharacterRole.MENTOR, CharacterRole.ALLY) else 0.5,
                safety_prerequisites=["emotional_safety"],
                trust_triggers=["witnessing_vulnerability"],
                trust_blocks=["betrayal", "public_exposure"],
            ),
            romantic=RomanticAccess(
                openness=0.1 if char.role == CharacterRole.PROTAGONIST else 0.3,
                dependency_willingness=0.1 if char.role == CharacterRole.PROTAGONIST else 0.4,
                safety_prerequisites=["proven_loyalty"],
                trust_triggers=["shared_sacrifice"],
                trust_blocks=["abandonment", "deception"],
            ),
        )

    # -- Texture layer --

    def _propose_texture(self, char: Character) -> TextureLayer | None:
        habits = self._suggest_habits(char)
        gestures = self._suggest_gestures(char)
        social_aura = self._suggest_social_aura(char)
        if not habits and not gestures and not social_aura:
            return None
        return TextureLayer(habits=habits, gestures=gestures, social_aura=social_aura)

    def _suggest_habits(self, char: Character) -> list[str]:
        if char.role == CharacterRole.PROTAGONIST:
            return ["obsessive note-taking"]
        if char.role == CharacterRole.ANTAGONIST:
            return ["arranges objects symmetrically"]
        if char.role == CharacterRole.MENTOR:
            return ["collects obscure artifacts"]
        return []

    def _suggest_gestures(self, char: Character) -> list[str]:
        if char.role == CharacterRole.PROTAGONIST:
            return ["rubs temples when thinking deeply"]
        if char.role == CharacterRole.ANTAGONIST:
            return ["steeples fingers during conversation"]
        if char.role == CharacterRole.MENTOR:
            return ["gestures with an unlit pipe"]
        return []

    def _suggest_social_aura(self, char: Character) -> list[str]:
        role_aura: dict[CharacterRole, list[str]] = {
            CharacterRole.PROTAGONIST: ["earnest_pressure"],
            CharacterRole.ANTAGONIST: ["executive_pressure", "emotional_distance"],
            CharacterRole.MENTOR: ["warm_authority"],
            CharacterRole.FOIL: ["unsettling_calm"],
            CharacterRole.ALLY: ["reassuring_warmth"],
            CharacterRole.SUPPORTING: ["unremarkable_presence"],
            CharacterRole.DEUTERAGONIST: ["quiet_intensity"],
        }
        return role_aura.get(char.role, [])

    # -- Ideology layer --

    def _propose_ideology(self, char: Character) -> IdeologicalProfile | None:
        tags = self._suggest_philosophy_tags(char)
        if not tags:
            return None
        worldview = tags[0].value.replace("_", " ").title()
        return IdeologicalProfile(
            worldview=worldview,
            philosophy_tags=tags,
        )

    def _suggest_philosophy_tags(self, char: Character) -> list[PhilosophyTag]:
        role_tags: dict[CharacterRole, list[PhilosophyTag]] = {
            CharacterRole.PROTAGONIST: [PhilosophyTag.SALVATION_THROUGH_KNOWLEDGE, PhilosophyTag.TRUTH_THROUGH_CONFRONTATION],
            CharacterRole.ANTAGONIST: [PhilosophyTag.ORDER_THROUGH_STRUCTURE, PhilosophyTag.CONTROL_THROUGH_CARE],
            CharacterRole.MENTOR: [PhilosophyTag.POWER_THROUGH_KNOWLEDGE],
            CharacterRole.FOIL: [PhilosophyTag.FREEDOM_THROUGH_AUTONOMY],
            CharacterRole.ALLY: [PhilosophyTag.JUSTICE_THROUGH_RULES],
            CharacterRole.SUPPORTING: [PhilosophyTag.SURVIVAL_THROUGH_ADAPTATION],
            CharacterRole.DEUTERAGONIST: [PhilosophyTag.LOYALTY_THROUGH_ALLEGIANCE],
        }
        return role_tags.get(char.role, [])

    # -- Essence layer --

    def _propose_essence(self, char: Character) -> EssenceProfile | None:
        return EssenceProfile(
            personal_traits=[
                EssenceTrait(name="curious", source=EssenceTraitSource.PERSONAL, description="Driven to understand hidden truths."),
            ],
        )

    # -- Motif layer --

    def _propose_motifs(self, char: Character) -> MotifProfile | None:
        motifs = self._suggest_motifs(char)
        return MotifProfile(motifs=motifs) if motifs else None

    def _suggest_motifs(self, char: Character) -> list[Motif]:
        role_motifs: dict[CharacterRole, list[Motif]] = {
            CharacterRole.PROTAGONIST: [
                Motif(behavior="pauses at thresholds before crossing", type=MotifType.RITUAL,
                      significance="Hesitation before commitment"),
            ],
            CharacterRole.ANTAGONIST: [
                Motif(behavior="traces patterns on surfaces while thinking", type=MotifType.GESTURE,
                      significance="Need for order and control"),
            ],
            CharacterRole.MENTOR: [
                Motif(behavior="offers cryptic half-answers", type=MotifType.VERBAL_TIC,
                      significance="Teaching through indirection"),
            ],
        }
        return role_motifs.get(char.role, [])

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

    # -- Relationship mesh --

    def _propose_relationship_mesh(self, char: Character) -> RelationshipMesh | None:
        sigs = self._infer_relationship_signatures(char)
        if not sigs:
            return None
        arcs = [
            RelationshipArc(
                other=sig.other,
                stages=self._suggest_relationship_stages(sig.type),
                trust_level=sig.intensity,
                progression_type=self._suggest_progression_type(sig.type),
                asymmetry_state=self._suggest_asymmetry_state(sig.type, char.role),
                asymmetry_trajectory=self._suggest_asymmetry_trajectory(sig.type),
            )
            for sig in sigs
        ]
        return RelationshipMesh(relationships=sigs, arcs=arcs)

    def _suggest_asymmetry_state(self, rel_type: RelationshipType, role: CharacterRole) -> str | None:
        mentor_roles = {CharacterRole.MENTOR, CharacterRole.PROTAGONIST}
        if rel_type in (RelationshipType.MENTORSHIP, RelationshipType.PROTEGE) and role in mentor_roles:
            return "mentor_protege"
        if rel_type in (RelationshipType.LOVE, RelationshipType.ROMANTIC_LOVE):
            return "mutual"
        if rel_type in (RelationshipType.OBSESSION, RelationshipType.MANIPULATION, RelationshipType.DECEPTION):
            return "pursuer_distance"
        if rel_type in (RelationshipType.DEPENDENCY, RelationshipType.LOYALTY, RelationshipType.ALLEGIANCE):
            return "nurturer_dependent"
        if rel_type in (RelationshipType.ENMITY, RelationshipType.HATE, RelationshipType.FEAR, RelationshipType.RIVALRY):
            return "adversarial"
        if rel_type in (RelationshipType.TRUST, RelationshipType.FRIENDSHIP):
            return "mutual"
        return None

    def _suggest_asymmetry_trajectory(self, rel_type: RelationshipType) -> str | None:
        if rel_type in (RelationshipType.MENTORSHIP, RelationshipType.PROTEGE):
            return "balancing"
        if rel_type in (RelationshipType.LOVE, RelationshipType.ROMANTIC_LOVE, RelationshipType.FRIENDSHIP, RelationshipType.TRUST):
            return "deepening"
        if rel_type in (RelationshipType.OBSESSION, RelationshipType.MANIPULATION):
            return "deepening"
        if rel_type in (RelationshipType.DEPENDENCY, RelationshipType.ALLEGIANCE):
            return "stuck"
        if rel_type in (RelationshipType.ENMITY, RelationshipType.HATE, RelationshipType.RIVALRY):
            return "dissolving"
        return None

    def _suggest_progression_type(self, rel_type: RelationshipType) -> str | None:
        mapping: dict[RelationshipType, str] = {
            RelationshipType.MENTORSHIP: "trust_based",
            RelationshipType.PROTEGE: "trust_based",
            RelationshipType.FRIENDSHIP: "trust_based",
            RelationshipType.LOVE: "trust_based",
            RelationshipType.ROMANTIC_LOVE: "trust_based",
            RelationshipType.PLATONIC_LOVE: "trust_based",
            RelationshipType.TRUST: "trust_based",
            RelationshipType.RIVALRY: "adversarial",
            RelationshipType.HATE: "adversarial",
            RelationshipType.ENMITY: "adversarial",
            RelationshipType.COMPETITION: "adversarial",
            RelationshipType.MANIPULATION: "coercive",
            RelationshipType.DECEPTION: "coercive",
            RelationshipType.OBSESSION: "coercive",
            RelationshipType.DEPENDENCY: "ritualistic",
            RelationshipType.ALLEGIANCE: "ritualistic",
            RelationshipType.LOYALTY: "ritualistic",
        }
        return mapping.get(rel_type)

    @staticmethod
    def _suggest_relationship_stages(rel_type: RelationshipType) -> list[str]:
        mapping: dict[RelationshipType, list[str]] = {
            RelationshipType.LOVE: [
                "initial_fascination",
                "vulnerability_discovery",
                "trust_formation",
                "deepening",
                "commitment",
            ],
            RelationshipType.ROMANTIC_LOVE: [
                "initial_fascination",
                "vulnerability_discovery",
                "trust_formation",
                "deepening",
                "commitment",
            ],
            RelationshipType.FRIENDSHIP: [
                "trust_formation",
                "safety_proving",
                "deepening",
            ],
            RelationshipType.TRUST: [
                "trust_formation",
                "safety_proving",
            ],
            RelationshipType.RIVALRY: [
                "initial_fascination",
                "crisis",
                "dissolution",
            ],
        }
        return mapping.get(rel_type, ["trust_formation"])

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
