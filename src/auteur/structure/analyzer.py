from __future__ import annotations

from auteur.blueprint import StoryBlueprint
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)
from auteur.blueprint import SupportFunction


from auteur.bible import StoryBible
from auteur.structure.bible_audit import (
    BibleAuditDiagnostic,
    audit_bible_locations,
    as_structure_diagnostic,
)


def run_all_diagnostics(
    blueprint: StoryBlueprint,
    bible: StoryBible,
    *,
    outline: dict | None = None,
    cartographer_outline: object | None = None,
) -> list[StructureDiagnostic]:
    """Run all active diagnostic rules across all layers.

    Currently runs:
    - Layers 1-5: analyze_structure() for within-blueprint coherence (Structure Diagnostic)
    - Layer 6: audit_bible_locations() for Bible Audit carrier state consistency
    - Layer 7: audit_outline_carriers() for Scene Representation validation (requires outline)
    - Cross-layer: audit_outline_vs_story_engine() for Narrative Engine → Cartographer validation
      (requires cartographer_outline)

    Args:
        blueprint: The StoryBlueprint to validate.
        bible: The StoryBible event log to audit.
        outline: Optional parsed outline dict (from load_outline). When None, a
            Layer 7 WARNING is emitted noting that Scene Representation validation
            was skipped.
        cartographer_outline: Optional CartographerOutline Pydantic model for cross-layer
            validation against the story engine.

    Returns a single merged list of StructureDiagnostic findings.
    """
    from auteur.structure.outline_audit import audit_outline_carriers
    from auteur.structure.cartographer_audit import audit_outline_vs_story_engine

    diagnostics: list[StructureDiagnostic] = []
    diagnostics.extend(analyze_structure(blueprint))
    diagnostics.extend(
        as_structure_diagnostic(d) for d in audit_bible_locations(bible)
    )
    diagnostics.extend(
        as_structure_diagnostic(d) for d in audit_outline_carriers(outline, bible)
    )
    if cartographer_outline is not None:
        diagnostics.extend(
            audit_outline_vs_story_engine(blueprint, cartographer_outline)
        )
    return diagnostics


def analyze_structure(blueprint: StoryBlueprint) -> list[StructureDiagnostic]:
    diagnostics: list[StructureDiagnostic] = []
    engine = blueprint.story_engine

    medium_diagnostic: StructureDiagnostic | None = None
    if blueprint.identity.medium is None and blueprint.identity.medium_contract is None:
        medium_diagnostic = (
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.CONSTRAINTS,
                rule="medium_contract.missing",
                message="Blueprint has no declared medium contract.",
                evidence=[
                    "identity.medium is absent",
                    "identity.medium_contract is absent",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Declare identity.medium or identity.medium_contract so the delivery grammar is explicit."
                    ],
                    challenge_intent=[
                        "Keep the blueprint medium-agnostic only if downstream structure and drafting commands should not assume a delivery form."
                    ],
                ),
            )
        )
    elif (
        blueprint.identity.medium is not None
        and blueprint.identity.medium_contract is not None
        and blueprint.identity.medium != blueprint.identity.medium_contract.medium
    ):
        medium_diagnostic = (
            StructureDiagnostic(
                severity=DiagnosticSeverity.ERROR,
                layer=DiagnosticLayer.CONSTRAINTS,
                rule="medium_contract.medium_mismatch",
                message="The legacy medium shortcut conflicts with the richer medium contract.",
                evidence=[
                    f"identity.medium = {blueprint.identity.medium.value}",
                    f"identity.medium_contract.medium = {blueprint.identity.medium_contract.medium.value}",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Align identity.medium with identity.medium_contract.medium."
                    ],
                    challenge_intent=[
                        "Revise identity.medium_contract if identity.medium is the intended delivery form."
                    ],
                ),
            )
        )

    if engine is None:
        diagnostics.append(
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
        )
        if medium_diagnostic is not None:
            diagnostics.append(medium_diagnostic)
        return diagnostics

    if medium_diagnostic is not None:
        diagnostics.append(medium_diagnostic)

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

        # 1. Rule: Primary stack emotion mismatch
        if target_experience.genre_emotion_stack:
            primary_stack = target_experience.genre_emotion_stack.get("primary")
            if primary_stack:
                primary_promise = target_experience.primary_emotional_promise
                if primary_promise and primary_stack.emotion.casefold() != primary_promise.casefold():
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.ERROR,
                            layer=DiagnosticLayer.TARGET_EXPERIENCE,
                            rule="target_experience.genre_emotion_stack.primary_mismatch",
                            message=(
                                f"The primary genre-emotion in the stack '{primary_stack.emotion}' "
                                f"does not match the primary emotional promise '{primary_promise}'."
                            ),
                            evidence=[
                                f"identity.target_experience.primary_emotional_promise = {primary_promise}",
                                f"genre_emotion_stack.primary.emotion = {primary_stack.emotion}",
                            ],
                            repair_options=RepairOptions(
                                preserve_intent=[
                                    "Update the primary emotional promise to match the primary genre-emotion.",
                                    "Update the primary genre-emotion in the stack to match the primary emotional promise."
                                ],
                                challenge_intent=[
                                    "Remove or restructure the genre emotion stack."
                                ],
                            ),
                        )
                    )

        # 2. Rule: POV Experience Contract unknown character
        if target_experience.pov_experience_contracts:
            declared_names_and_roles = {char.name.casefold() for char in blueprint.characters} | {char.role.value.casefold() for char in blueprint.characters}
            for pov_key in target_experience.pov_experience_contracts:
                if pov_key.casefold() not in declared_names_and_roles:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.WARNING,
                            layer=DiagnosticLayer.TARGET_EXPERIENCE,
                            rule="target_experience.pov_contract.unknown_character",
                            message=(
                                f"POV contract declared for '{pov_key}', but no character "
                                "with that name or role exists in the blueprint."
                            ),
                            evidence=[
                                f"pov_experience_contracts key = {pov_key}",
                                f"declared characters = {[c.name for c in blueprint.characters]}",
                                f"declared roles = {[c.role.value for c in blueprint.characters]}",
                            ],
                            repair_options=RepairOptions(
                                preserve_intent=[
                                    f"Add a character named '{pov_key}' or with the role '{pov_key}' to the characters list.",
                                    f"Rename the POV contract key '{pov_key}' to match an existing character's name or role."
                                ],
                                challenge_intent=[
                                    "Remove this POV contract if it is no longer needed."
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

    # -------------------------------------------------------------------------
    # Genre Contract Constraints & Validation (Layer 2)
    # -------------------------------------------------------------------------
    contract_snap = blueprint.identity.genre_contract_snapshot
    if contract_snap is None:
        from auteur.genres.registry import load_genre_contract
        contract_snap = load_genre_contract(blueprint.identity.genre)

    # 1. Rule: Psychology Budget (avoid LLM therapy bias)
    if contract_snap.psychology_budget.level in ("archetypal", "functional"):
        therapeutic_words = {
            "trauma", "healing", "therapy", "inner wound", "repress",
            "identity crisis", "forgive myself", "forgiving himself",
            "forgiving herself", "forgiving oneself"
        }
        found_terms: set[str] = set()
        
        # Helper to scan text
        def scan_text(text: str) -> None:
            if not text:
                return
            normalized_text = text.casefold()
            for word in therapeutic_words:
                if word in normalized_text:
                    found_terms.add(word)

        # Scan blueprint text fields
        scan_text(blueprint.theme.thesis)
        scan_text(blueprint.theme.central_question)
        if engine is not None:
            scan_text(engine.main_thread.want.author_text)
            scan_text(engine.main_thread.change.author_text)
        for char in blueprint.characters:
            for milestone in char.key_milestones:
                scan_text(milestone.description)

        if found_terms:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.TARGET_EXPERIENCE,
                    rule="genre.psychology_budget.therapy_bias_trap",
                    message=(
                        f"The narrative or theme contains therapeutic phrasing that may conflict "
                        f"with the '{contract_snap.display_name}' genre contract. This genre runs on "
                        f"'{contract_snap.psychology_budget.level.value}' psychology: "
                        f"{contract_snap.psychology_budget.reason}"
                    ),
                    evidence=[
                        f"psychology_budget = {contract_snap.psychology_budget.level.value}",
                        f"found therapeutic terms = {sorted(list(found_terms))}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Keep character psychology lean and focused on external motive, using character texture for flavor.",
                            "Remove therapeutic concepts like trauma or healing unless load-bearing for the plot."
                        ],
                        challenge_intent=[
                            "Upgrade to a psychologically deep genre or select a different story mode if this psychological focus is intentional."
                        ],
                    ),
                )
            )

    # 2. Rule: Forbidden Mismatches (Ending Tone)
    ending_tone_str = blueprint.contract.mandatory_ending_tone.value
    override = blueprint.identity.genre_overrides.get("ending_tone")
    
    is_mismatch = False
    forbidden_type = ""
    if ending_tone_str == "tragic" and "tragic ending" in contract_snap.forbidden_mismatches:
        is_mismatch = True
        forbidden_type = "tragic ending"
    elif ending_tone_str == "hopeful" and "hopeful ending" in contract_snap.forbidden_mismatches:
        is_mismatch = True
        forbidden_type = "hopeful ending"

    if is_mismatch:
        if override is None:
            # Generate the recommendation flow
            rec_flow = {
                "selected_genre": contract_snap.genre_id.value if hasattr(contract_snap.genre_id, "value") else str(contract_snap.genre_id),
                "load_bearing_expectation": "ending_tone",
                "user_override": f"force_{ending_tone_str}_ending",
                "auteur_diagnosis": "genre_contract_risk",
                "consequence": f"Audience expecting the core product of {contract_snap.display_name} will be disappointed/alienated by a {ending_tone_str} ending.",
                "options": {
                    "preserve_genre": {
                        "recommendation": f"Change ending tone to bittersweet or one allowed by the contract."
                    },
                    "subvert_genre": {
                        "recommendation": f"Make the unexpected ending tone itself the focus (subvert expectations intentionally)."
                    },
                    "reclassify": {
                        "recommendation": f"Reclassify the story to another genre that supports tragic/hopeful ending tones."
                    },
                    "override_anyway": {
                        "recommendation": "Proceed, but mark genre confidence lower."
                    }
                }
            }
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    layer=DiagnosticLayer.CONSTRAINTS,
                    rule="genre.forbidden_mismatch.ending_tone",
                    message=f"Mandatory ending tone '{ending_tone_str}' is forbidden by the '{contract_snap.display_name}' contract.",
                    evidence=[
                        f"mandatory_ending_tone = {ending_tone_str}",
                        f"forbidden_mismatch = {forbidden_type}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=["Change ending tone to bittersweet, hopeful, or open."],
                        challenge_intent=["Select a different genre that supports tragic endings."],
                    ),
                    genre_recommendation_flow=rec_flow
                )
            )
        else:
            # Override is present: suppress error and warn of consequence
            rule_suffix = override.override_type.value
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.CONSTRAINTS,
                    rule=f"genre.forbidden_mismatch.ending_tone.{rule_suffix}",
                    message=(
                        f"The forbidden ending tone '{ending_tone_str}' is overridden via {override.override_type.value}: "
                        f"'{override.user_override}'."
                    ),
                    evidence=[
                        f"override_type = {override.override_type.value}",
                        f"user_override = {override.user_override}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[f"Handle the {ending_tone_str} ending with care to preserve/subvert reader trust."],
                        challenge_intent=["Remove the override and return to an allowed ending tone."]
                    )
                )
            )

    # -------------------------------------------------------------------------
    # Character Categorization Diagnostics (Cross-layer integration)
    # -------------------------------------------------------------------------
    from auteur.character.analyzer import analyze_character_categorization
    diagnostics.extend(analyze_character_categorization(blueprint))

    # -------------------------------------------------------------------------
    # Character-Story Engine Cross-Reference
    # -------------------------------------------------------------------------
    for char in blueprint.characters:
        identity = None
        if char.identity is not None:
            try:
                from auteur.character.models import CharacterIdentity
                identity = char.identity if isinstance(char.identity, CharacterIdentity) else CharacterIdentity.model_validate(char.identity)
            except Exception:
                pass

        if identity is not None and identity.psychology is not None:
            vuln = identity.psychology.vulnerability_family
            wound = (identity.psychology.wound or "").casefold()
            if vuln is not None and engine is not None:
                stake_text = engine.main_thread.stakes.author_text.casefold()
                if vuln.value.casefold() not in stake_text and wound not in stake_text:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.WARNING,
                            layer=DiagnosticLayer.STRUCTURAL_FORCES,
                            rule="character.psychology.stakes_disconnected",
                            message=(
                                f"Character '{char.name}' has vulnerability '{vuln.value}' "
                                f"but the main thread stakes do not reference it."
                            ),
                            evidence=[
                                f"character.name = {char.name}",
                                f"vulnerability_family = {vuln.value}",
                                f"wound = {identity.psychology.wound or 'none'}",
                                f"main_thread.stakes = {engine.main_thread.stakes.author_text}",
                            ],
                            repair_options=RepairOptions(
                                preserve_intent=[
                                    f"Rewrite main thread stakes to personally threaten '{char.name}'s {vuln.value} vulnerability."
                                ],
                                challenge_intent=[
                                    "Keep disconnected if the stakes are external and the vulnerability is for texture only."
                                ],
                            ),
                        )
                    )

    # -------------------------------------------------------------------------
    # Cross-Chapter Arc Progression Diagnostic
    # -------------------------------------------------------------------------
    if blueprint.structure.estimated_chapters:
        est_chapters = blueprint.structure.estimated_chapters
        for char in blueprint.characters:
            if char.arc_type.value == "flat":
                continue
            start_pct = char.arc_start_percentage
            end_pct = char.arc_end_percentage
            total_arc_pct = abs(end_pct - start_pct)
            if total_arc_pct > 0 and est_chapters > 0:
                pct_per_chapter = total_arc_pct / est_chapters
                if pct_per_chapter > 20:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.WARNING,
                            layer=DiagnosticLayer.SCOPE,
                            rule="character.arc.too_steep",
                            message=(
                                f"Character '{char.name}' arc covers {total_arc_pct}% "
                                f"over {est_chapters} chapters (~{pct_per_chapter:.0f}% per chapter). "
                                f"The arc may feel rushed."
                            ),
                            evidence=[
                                f"character.name = {char.name}",
                                f"arc_start_percentage = {start_pct}",
                                f"arc_end_percentage = {end_pct}",
                                f"estimated_chapters = {est_chapters}",
                            ],
                            repair_options=RepairOptions(
                                preserve_intent=[
                                    "Increase chapter count or adjust arc percentages for more gradual progression.",
                                    "Add intermediate milestones to ensure the arc does not skip stages.",
                                ],
                                challenge_intent=[
                                    "Keep steep arc if the transformation is meant to be abrupt or crisis-driven."
                                ],
                            ),
                        )
                    )
                if est_chapters >= 3:
                    milestone_pcts = {m.at_percentage for m in char.key_milestones}
                    key_structural_pcts = {25, 50, 75}
                    significant_missing = [p for p in key_structural_pcts if 10 <= p <= 90 and p not in milestone_pcts and start_pct < p < end_pct]
                    if len(significant_missing) >= 2:
                        diagnostics.append(
                            StructureDiagnostic(
                                severity=DiagnosticSeverity.WARNING,
                                layer=DiagnosticLayer.SCOPE,
                                rule="character.arc.milestone_gap",
                                message=(
                                    f"Character '{char.name}' is missing milestones at key percentages "
                                    f"({significant_missing}). Arc progression may lack intermediate checks."
                                ),
                                evidence=[
                                    f"character.name = {char.name}",
                                    f"existing milestones = {sorted(milestone_pcts)}",
                                    f"missing at = {significant_missing}",
                                ],
                                repair_options=RepairOptions(
                                    preserve_intent=[
                                        "Add milestones at significant missing percentages to track arc progression."
                                    ],
                                    challenge_intent=[
                                        "Keep existing milestones if the arc is designed to jump between stages."
                                    ],
                                ),
                            )
                        )

    # -------------------------------------------------------------------------
    # Emotional Chaos Diagnostic — arc regression / oscillation patterns
    # -------------------------------------------------------------------------
    from auteur.character.models import CharacterIdentity
    for char in blueprint.characters:
        if char.identity is None:
            continue
        cid = None
        try:
            cid = char.identity if isinstance(char.identity, CharacterIdentity) else CharacterIdentity.model_validate(char.identity)
        except Exception:
            pass
        if cid is None or cid.relationship_mesh is None:
            continue

        for arc in cid.relationship_mesh.arcs:
            if len(arc.stages) < 3:
                continue

            no_regression_labels = True
            for stage in arc.stages:
                st = stage.strip().lower()
                if st in ("crisis", "dissolution", "recovery", "setback", "regression", "relapse"):
                    no_regression_labels = False
                    break
            if no_regression_labels and arc.trust_level > 0.5:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.INFO,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="character.relationship.arc.no_regression",
                        message=(
                            f"Relationship arc '{char.name}' -> '{arc.other}' has {len(arc.stages)} stages "
                            f"but none suggest regression or setback. Pure forward progression can feel "
                            f"emotionally flat — consider adding a crisis or regression stage."
                        ),
                        evidence=[
                            f"character.name = {char.name}",
                            f"relationship.other = {arc.other}",
                            f"stages = {arc.stages}",
                            f"trust_level = {arc.trust_level}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                f"Add a crisis or regression stage between '{char.name}' and '{arc.other}' to introduce emotional oscillation."
                            ],
                            challenge_intent=[
                                "Keep pure forward progression if the relationship is intentionally stable or background."
                            ],
                        ),
                    )
                )

        if cid.psychology and len(cid.psychology.contradictions) >= 2:
            for arc in cid.relationship_mesh.arcs:
                if not arc.stages or len(arc.stages) < 3:
                    continue
                has_oscillation = any(
                    s.strip().lower() in ("crisis", "dissolution", "relapse", "recovery", "setback")
                    for s in arc.stages
                )
                if not has_oscillation:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.INFO,
                            layer=DiagnosticLayer.STRUCTURAL_FORCES,
                            rule="character.relationship.arc.contradiction_unexpressed",
                            message=(
                                f"Character '{char.name}' has {len(cid.psychology.contradictions)} contradictions "
                                f"but relationship arc with '{arc.other}' shows no oscillation. "
                                f"Contradictions suggest internal tension that should surface as relational instability."
                            ),
                            evidence=[
                                f"character.name = {char.name}",
                                f"contradictions = {cid.psychology.contradictions}",
                                f"relationship.other = {arc.other}",
                                f"stages = {arc.stages}",
                            ],
                            repair_options=RepairOptions(
                                preserve_intent=[
                                    f"Add a crisis or regression stage to the arc between '{char.name}' and '{arc.other}' to reflect their internal contradictions."
                                ],
                                challenge_intent=[
                                    "Keep stable arc if the contradictions are managed or suppressed rather than expressed."
                                ],
                            ),
                        )
                    )

    # -------------------------------------------------------------------------
    # Scene Energy Presence Diagnostic
    # -------------------------------------------------------------------------
    from auteur.character.analyzer import analyze_character_categorization
    char_diags = analyze_character_categorization(blueprint)
    has_scene_energy_diag = any(d.rule.startswith("character.psychology.scene_energy") for d in char_diags)
    if not has_scene_energy_diag:
        for char in blueprint.characters:
            if char.role.value not in ("protagonist", "antagonist", "deuteragonist"):
                continue
            if char.identity is None:
                continue
            try:
                cid2 = char.identity if isinstance(char.identity, CharacterIdentity) else CharacterIdentity.model_validate(char.identity)
            except Exception:
                continue
            has_texture = cid2.texture is not None and (cid2.texture.social_aura or cid2.texture.gestures or cid2.texture.voice)
            has_psych = cid2.psychology is not None
            if has_texture and has_psych and cid2.psychology and cid2.psychology.intimacy is None:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.INFO,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule="character.psychology.scene_energy_inferrable",
                        message=(
                            f"Character '{char.name}' ({char.role.value}) has texture and psychology data "
                            f"from which a SceneEnergySignature could be inferred. Run 'auteur character categorize' "
                            f"to generate atmospheric profile (pressure style, spatial behavior, silence quality)."
                        ),
                        evidence=[
                            f"character.name = {char.name}",
                            f"has_texture = {has_texture}",
                            f"has_psychology = {has_psych}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                f"Run 'auteur character categorize' to infer a SceneEnergySignature for '{char.name}'."
                            ],
                            challenge_intent=[
                                "Skip if the character's atmospheric impact is not needed for downstream scene generation."
                            ],
                        ),
                    )
                )

    # 3. Rule: Required Tropes Forbidden
    for trope in contract_snap.required_tropes:
        if trope in blueprint.contract.forbidden_tropes:
            override_key = f"trope.{trope.replace(' ', '_')}"
            override = blueprint.identity.genre_overrides.get(override_key)
            if override is None:
                rec_flow = {
                    "selected_genre": contract_snap.genre_id.value if hasattr(contract_snap.genre_id, "value") else str(contract_snap.genre_id),
                    "load_bearing_expectation": f"trope_{trope.replace(' ', '_')}",
                    "user_override": f"forbid_{trope.replace(' ', '_')}",
                    "auteur_diagnosis": "genre_contract_risk",
                    "consequence": f"Story lacks the '{trope}' trope required by '{contract_snap.display_name}'. The contract is incomplete.",
                    "options": {
                        "preserve_genre": {
                            "recommendation": f"Remove '{trope}' from the forbidden tropes list and integrate it."
                        },
                        "subvert_genre": {
                            "recommendation": f"Deliver a subverted alternative trope that serves the same emotional function."
                        },
                        "reclassify": {
                            "recommendation": f"Reclassify the story to a genre that does not require the '{trope}' trope."
                        },
                        "override_anyway": {
                            "recommendation": "Proceed, but mark genre confidence lower."
                        }
                    }
                }
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        layer=DiagnosticLayer.CONSTRAINTS,
                        rule="genre.forbidden_mismatch.required_trope_forbidden",
                        message=f"The trope '{trope}' is required by the '{contract_snap.display_name}' genre contract, but is listed as a forbidden trope.",
                        evidence=[
                            f"required_trope = {trope}",
                            f"forbidden_tropes = {blueprint.contract.forbidden_tropes}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[f"Remove '{trope}' from the forbidden tropes list."],
                            challenge_intent=["Change the genre to one that does not require this trope."],
                        ),
                        genre_recommendation_flow=rec_flow
                    )
                )
            else:
                rule_suffix = override.override_type.value
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.CONSTRAINTS,
                        rule=f"genre.forbidden_mismatch.required_trope_forbidden.{rule_suffix}",
                        message=(
                            f"The required trope '{trope}' is forbidden but overridden via {override.override_type.value}: "
                            f"'{override.user_override}'."
                        ),
                        evidence=[
                            f"override_type = {override.override_type.value}",
                            f"user_override = {override.user_override}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[f"Ensure the absence/subversion of '{trope}' is compensated for in prose."],
                            challenge_intent=["Remove the override to include the trope."]
                        )
                    )
                )

    # -------------------------------------------------------------------------
    # Subgenre Modifier Validation (Layer 2/3 cross-layer)
    # -------------------------------------------------------------------------
    subgenres = blueprint.identity.subgenres or []
    if subgenres:
        from auteur.genres.subgenres import load_subgenre_modifier
        for subgenre_id in subgenres:
            modifier = load_subgenre_modifier(subgenre_id)
            if modifier is None:
                # Unknown subgenre is flagged at identity level; skip repeat
                continue

            # 1. Subgenre scope compatibility
            if modifier.scope_biases:
                scope_bias_text = " ".join(modifier.scope_biases).lower()
                is_scope_aligned = True
                scope_mismatches: list[str] = []

                # Check subplot_budget against scope biases
                if "focus" in scope_bias_text and "few" not in scope_bias_text:
                    # This subgenre expects tight focus — verify subplot_budget is not too high
                    if blueprint.structure.subplot_budget and blueprint.structure.subplot_budget > 4:
                        scope_mismatches.append(
                            f"Subgenre '{subgenre_id}' biases toward focused scope "
                            f"(scope_biases suggest tight execution), but subplot_budget is "
                            f"{blueprint.structure.subplot_budget}."
                        )

                if "multiple" in scope_bias_text or "overlapping" in scope_bias_text:
                    # This subgenre expects multiple threads — verify subplot_budget is sufficient
                    if blueprint.structure.subplot_budget and blueprint.structure.subplot_budget < 2:
                        scope_mismatches.append(
                            f"Subgenre '{subgenre_id}' expects multiple overlapping threads "
                            f"(scope_biases suggest layered plotting), but subplot_budget is "
                            f"only {blueprint.structure.subplot_budget}."
                        )

                if scope_mismatches:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.WARNING,
                            layer=DiagnosticLayer.SCOPE,
                            rule=f"subgenre.{subgenre_id}.scope_mismatch",
                            message=(
                                f"The scope container may conflict with the '{subgenre_id}' subgenre's "
                                f"scope biases."
                            ),
                            evidence=scope_mismatches,
                            repair_options=RepairOptions(
                                preserve_intent=[
                                    "Adjust subplot_budget to match the subgenre's scope expectations.",
                                    "Add a GenreOverride if the scope mismatch is intentional.",
                                ],
                                challenge_intent=[
                                    "Remove the subgenre modifier if it does not fit the intended scope.",
                                ],
                            ),
                        )
                    )

            # 2. Subgenre setup biases — does the blueprint declare any setup?
            if modifier.setup_biases and blueprint.structure.scope_contract is None:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.CONSTRAINTS,
                        rule=f"subgenre.{subgenre_id}.setup_not_declared",
                        message=(
                            f"Subgenre '{subgenre_id}' has setup requirements that are not "
                            f"reflected in a declared scope_contract. The subgenre expects: "
                            f"{'; '.join(modifier.setup_biases)}."
                        ),
                        evidence=[
                            f"subgenre = {subgenre_id}",
                            "structure.scope_contract is absent",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                "Declare a scope_contract with narrative_runway and setup beats.",
                                "If the setup requirements are handled implicitly, document that in an author note.",
                            ],
                            challenge_intent=[
                                "Remove the subgenre if its setup requirements cannot be satisfied.",
                            ],
                        ),
                    )
                )

            # 3. Subgenre trope coverage — warn about common misuses
            if modifier.common_misuses:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.CONSTRAINTS,
                        rule=f"subgenre.{subgenre_id}.common_misuses",
                        message=(
                            f"Subgenre '{subgenre_id}' has documented common misuses. "
                            f"Review to ensure the story avoids them."
                        ),
                        evidence=[
                            f"subgenre = {subgenre_id}",
                            *[f"common_misuse: {m}" for m in modifier.common_misuses],
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                f"Review each misuse: {'; '.join(modifier.common_misuses)}",
                            ],
                            challenge_intent=[
                                "If a misuse is intentional, document as a GenreOverride.",
                            ],
                        ),
                    )
                )

    # 4. Rule: Setup Contract Runway vs. Scope Container Length
    setup_contract = contract_snap.setup_contract
    if setup_contract:
        runway_val = setup_contract.emotional_runway.value if hasattr(setup_contract.emotional_runway, "value") else setup_contract.emotional_runway
        length_val = blueprint.identity.length_class.value if hasattr(blueprint.identity.length_class, "value") else blueprint.identity.length_class

        is_mismatch = False
        if runway_val == "very_long" and length_val in ("short_story", "novella", "novel"):
            is_mismatch = True
        elif runway_val == "long" and length_val in ("short_story", "novella"):
            is_mismatch = True
        elif runway_val == "medium" and length_val == "short_story":
            is_mismatch = True
            
        if is_mismatch:
            # Check for override
            override = blueprint.identity.genre_overrides.get("emotional_runway")
            if override is None:
                # No override: raise standard warning with rich recommendation flow
                rec_flow = {
                    "selected_genre": contract_snap.genre_id.value if hasattr(contract_snap.genre_id, "value") else str(contract_snap.genre_id),
                    "load_bearing_expectation": "emotional_runway_before_betrayal",
                    "user_override": "remove_long_build_up",
                    "auteur_diagnosis": "genre_contract_risk",
                    "consequence": "Audience may not emotionally invest in the bond, weakening betrayal impact.",
                    "options": {
                        "preserve_genre": {
                            "recommendation": "Use compressed emotional runway instead of deleting setup."
                        },
                        "subvert_genre": {
                            "recommendation": "Make the suddenness itself the product: shock, destabilization, brutality."
                        },
                        "reclassify": {
                            "recommendation": "Treat this as betrayal vignette / dark transgression rather than full netorare."
                        },
                        "override_anyway": {
                            "recommendation": "Proceed, but mark genre confidence lower."
                        }
                    }
                }
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.SCOPE,
                        rule="genre.setup_contract.insufficient_runway",
                        message=(
                            f"The '{contract_snap.display_name}' genre contract requires a '{runway_val}' "
                            f"emotional runway, but the story container length is '{length_val}'."
                        ),
                        evidence=[
                            f"genre = {contract_snap.display_name}",
                            f"emotional_runway = {runway_val}",
                            f"length_class = {length_val}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                "Increase story container length to a longer format (e.g., novel or novella) to give the emotional runway sufficient scene budget.",
                                "Use compressed setup strategies to deliver the required emotional foundation in fewer scenes."
                            ],
                            challenge_intent=[
                                "Proceed with the short container but ensure maximum efficiency in establishing relationship/world baselines."
                            ],
                        ),
                        genre_recommendation_flow=rec_flow
                    )
                )
            else:
                # Override is present: suppress warning and output consequence warning/advice
                from auteur.blueprint import OverrideType
                if override.override_type in (OverrideType.SAFE_VARIATION, OverrideType.COMPRESSION):
                    rule_suffix = "compressed"
                    msg = (
                        f"The '{contract_snap.display_name}' runway expectation is overridden via compression: "
                        f"'{override.user_override}'. Use compressed setup strategies to deliver the "
                        f"required emotional foundation in fewer scenes."
                    )
                    preserve = ["Establish the relationship through high-density scene work."]
                elif override.override_type == OverrideType.SUBVERSION:
                    rule_suffix = "subverted"
                    msg = (
                        f"The '{contract_snap.display_name}' runway expectation is overridden via subversion: "
                        f"'{override.user_override}'. Make the suddenness itself the product: shock, "
                        f"destabilization, or brutality."
                    )
                    preserve = ["Deliver alternative transgressive products to satisfy the audience."]
                else: # RECLASSIFICATION
                    rule_suffix = "reclassified"
                    msg = (
                        f"The '{contract_snap.display_name}' runway expectation is overridden via reclassification: "
                        f"'{override.user_override}'. This breaks the standard Netorare contract."
                    )
                    preserve = [
                        "Treat this as betrayal vignette, dark transgression, or corruption snapshot.",
                        "Reclassify the story genre in the blueprint to a betrayal vignette / transgressive short."
                    ]

                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.SCOPE,
                        rule=f"genre.setup_contract.insufficient_runway.{rule_suffix}",
                        message=msg,
                        evidence=[
                            f"override_type = {override.override_type.value}",
                            f"user_override = {override.user_override}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=preserve,
                            challenge_intent=["Revert the override if you wish to write the standard runway."]
                        )
                    )
                )

    # -------------------------------------------------------------------------
    # Scope Fit Recommendation (Layer 3) — desired machinery vs container
    # -------------------------------------------------------------------------
    scope_contract = blueprint.structure.scope_contract
    scope_profile = contract_snap.scope_profile
    if engine is not None and scope_profile:
        _add_scope_fit_diagnostics(blueprint, diagnostics, scope_contract, scope_profile)

    # -------------------------------------------------------------------------
    # Genre-first adaptation cascade — summary check
    # -------------------------------------------------------------------------
    genre_errors = [
        d for d in diagnostics
        if d.severity == DiagnosticSeverity.ERROR
        and d.layer in {DiagnosticLayer.CONSTRAINTS, DiagnosticLayer.TARGET_EXPERIENCE}
        and d.rule.startswith("genre.")
    ]
    char_or_thread_warnings = [
        d for d in diagnostics
        if d.layer in {DiagnosticLayer.STRUCTURAL_FORCES, DiagnosticLayer.THREADS, DiagnosticLayer.THEME}
        and d.severity != DiagnosticSeverity.ERROR
    ]
    if genre_errors and char_or_thread_warnings:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.INFO,
                layer=DiagnosticLayer.CONSTRAINTS,
                rule="adaptation.genre_first_cascade",
                message=(
                    f"{len(genre_errors)} genre contract error(s) found. Character, thread, and theme "
                    f"diagnostics may be premature until genre contract violations are resolved."
                ),
                evidence=[
                    f"genre_contract_errors = {[d.rule for d in genre_errors]}",
                    f"downstream_diagnostics_affected = {len(char_or_thread_warnings)}",
                ],
                repair_options=RepairOptions(
                    preserve_intent=["Resolve genre contract violations first, then re-run structure diagnostics."],
                    challenge_intent=[
                        "Ignore this cascade warning if genre violations are intentional and downstream diagnostics remain independently valid."
                    ],
                ),
            )
        )

    # -------------------------------------------------------------------------
    # Narrative Runway cross-check (Medium x Genre)
    # -------------------------------------------------------------------------
    medium_contract = blueprint.identity.medium_contract
    if engine is not None and medium_contract and scope_profile:
        _add_medium_runway_diagnostics(blueprint, diagnostics, medium_contract, scope_profile, contract_snap, engine)

    # -------------------------------------------------------------------------
    # Layer 9 resonance expansion — beyond thesis_unrepresented
    # -------------------------------------------------------------------------
    if engine is not None:
        _add_layer9_resonance_diagnostics(blueprint, diagnostics, engine)

    # -------------------------------------------------------------------------
    # Coverage gaps — modulation layer
    # -------------------------------------------------------------------------
    if engine is not None and blueprint.structure.estimated_chapters:
        actual_counts = (
            sum(1 for c in blueprint.characters if c.role.value in ("protagonist", "antagonist", "deuteragonist")),
            len(blueprint.characters),
        )
        max_pov = blueprint.structure.max_pov_characters
        max_total = blueprint.structure.max_characters_total
        if max_pov and actual_counts[0] > 0 and actual_counts[0] < max_pov * 0.5:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.INFO,
                    layer=DiagnosticLayer.MODULATION,
                    rule="modulation.pov_underutilized",
                    message=(
                        f"Blueprint allows up to {max_pov} POV characters but only "
                        f"{actual_counts[0]} POV-eligible character(s) declared. "
                        f"The narrative may feel narrow for the scope."
                    ),
                    evidence=[
                        f"max_pov_characters = {max_pov}",
                        f"declared_pov_eligible = {actual_counts[0]}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Add a deuteragonist or secondary POV to broaden narrative modulation.",
                            "Reduce max_pov_characters if the tight POV is intentional.",
                        ],
                        challenge_intent=[
                            "Keep the narrow POV if the story demands a single tight perspective."
                        ],
                    ),
                )
            )

    return diagnostics


def _scope_complexity_order(c: object) -> int:
    order = {"micro": 1, "focused": 2, "standard": 3, "expanded": 4, "series": 5}
    val = c.value if hasattr(c, "value") else str(c)
    return order.get(val, 3)


def _mechanical_load_order(m: object) -> int:
    order = {"low": 1, "medium": 2, "high": 3}
    val = m.value if hasattr(m, "value") else str(m)
    return order.get(val, 2)


def _add_scope_fit_diagnostics(
    blueprint: StoryBlueprint,
    diagnostics: list[StructureDiagnostic],
    scope_contract: object,
    scope_profile: object,
) -> None:
    from auteur.genres.models import ScopeProfile

    if not isinstance(scope_profile, ScopeProfile):
        return
    length_class = blueprint.identity.length_class

    # 1. Complexity fit
    if scope_contract is not None:
        sc_complexity = getattr(scope_contract, "recommended_complexity", None)
        if sc_complexity and hasattr(sc_complexity, "value"):
            prof_complexity = scope_profile.recommended_complexity
            if _scope_complexity_order(prof_complexity) > _scope_complexity_order(sc_complexity):
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.SCOPE,
                        rule="scope.fit.complexity_mismatch",
                        message=(
                            f"The '{scope_profile.recommended_complexity}' complexity "
                            f"recommended by the genre exceeds the '{sc_complexity.value}' "
                            f"complexity declared in the scope contract. "
                            f"The story machinery may not fit the container."
                        ),
                        evidence=[
                            f"genre.recommended_complexity = {prof_complexity.value if hasattr(prof_complexity, 'value') else prof_complexity}",
                            f"scope_contract.recommended_complexity = {sc_complexity.value if hasattr(sc_complexity, 'value') else sc_complexity}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                "Increase scope_contract.recommended_complexity to match the genre contract.",
                                "Scale back the narrative machinery (fewer threads, simpler arcs).",
                            ],
                            challenge_intent=[
                                "Keep the compressed container if the author intends a tight, focused execution of a complex genre."
                            ],
                        ),
                    )
                )

        # 2. Mechanical load fit
        sc_mechanical = getattr(scope_contract, "mechanical_load", None)
        if sc_mechanical and hasattr(sc_mechanical, "value"):
            prof_mechanical = scope_profile.mechanical_load
            if _mechanical_load_order(prof_mechanical) > _mechanical_load_order(sc_mechanical):
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.SCOPE,
                        rule="scope.fit.mechanical_overload",
                        message=(
                            f"The genre recommends '{prof_mechanical}' mechanical load "
                            f"but the scope contract allows '{sc_mechanical.value}'. "
                            f"This may create pacing or complexity problems."
                        ),
                        evidence=[
                            f"genre.mechanical_load = {prof_mechanical.value if hasattr(prof_mechanical, 'value') else prof_mechanical}",
                            f"scope_contract.mechanical_load = {sc_mechanical.value if hasattr(sc_mechanical, 'value') else sc_mechanical}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                "Increase scope_contract.mechanical_load to match the genre's recommended machinery.",
                                "Simplify the narrative mechanics to fit within the container.",
                            ],
                            challenge_intent=[
                                "Keep the lower mechanical load if the story focuses on character over plot machinery."
                            ],
                        ),
                    )
                )

    # 3. Length outside natural range
    natural_lengths = scope_profile.natural_lengths
    if natural_lengths and length_class not in natural_lengths:
        natural_names = [l.value if hasattr(l, "value") else str(l) for l in natural_lengths]
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.SCOPE,
                rule="scope.fit.length_outside_natural_range",
                message=(
                    f"The declared length '{length_class.value if hasattr(length_class, 'value') else length_class}' "
                    f"is outside the genre's natural length range ({', '.join(natural_names)}). "
                    f"The story may feel compressed or stretched."
                ),
                evidence=[
                    f"length_class = {length_class.value if hasattr(length_class, 'value') else length_class}",
                    f"genre.natural_lengths = {natural_names}",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        f"Change length_class to one of the natural lengths: {', '.join(natural_names)}.",
                        "Use compression or expansion strategies from the genre's scope profile to adapt.",
                    ],
                    challenge_intent=[
                        "Keep the current length if the genre adaptation is intentional and accounted for."
                    ],
                ),
            )
        )

    # 4. Cast load fit
    if scope_contract is not None:
        sc_cast = getattr(scope_contract, "cast_load", None)
        if sc_cast and hasattr(sc_cast, "value"):
            prof_cast = scope_profile.cast_load
            if prof_cast and _mechanical_load_order(prof_cast) > _mechanical_load_order(sc_cast):
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.SCOPE,
                        rule="scope.fit.cast_overload",
                        message=(
                            f"The genre recommends '{prof_cast}' cast load "
                            f"but the scope contract allows '{sc_cast.value}'. "
                            f"The character roster may be insufficient."
                        ),
                        evidence=[
                            f"genre.cast_load = {prof_cast.value if hasattr(prof_cast, 'value') else prof_cast}",
                            f"scope_contract.cast_load = {sc_cast.value if hasattr(sc_cast, 'value') else sc_cast}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                "Increase scope_contract.cast_load to match the genre's cast requirements.",
                                "Add characters to serve the required narrative functions."
                            ],
                            challenge_intent=[
                                "Keep the smaller cast if the story focuses tightly on a few characters."
                            ],
                        ),
                    )
                )

        # 5. Worldbuilding load fit
        sc_world = getattr(scope_contract, "worldbuilding_load", None)
        if sc_world and hasattr(sc_world, "value"):
            prof_world = scope_profile.worldbuilding_load
            if prof_world and _mechanical_load_order(prof_world) > _mechanical_load_order(sc_world):
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.SCOPE,
                        rule="scope.fit.worldbuilding_overload",
                        message=(
                            f"The genre recommends '{prof_world}' worldbuilding load "
                            f"but the scope contract allows '{sc_world.value}'. "
                            f"The world may feel underdeveloped for this genre."
                        ),
                        evidence=[
                            f"genre.worldbuilding_load = {prof_world.value if hasattr(prof_world, 'value') else prof_world}",
                            f"scope_contract.worldbuilding_load = {sc_world.value if hasattr(sc_world, 'value') else sc_world}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                "Increase scope_contract.worldbuilding_load to match the genre.",
                                "Keep worldbuilding efficient if the story is character-driven."
                            ],
                            challenge_intent=[
                                "Keep the lower worldbuilding load if the story emphasizes character over setting."
                            ],
                        ),
                    )
                )


def _add_medium_runway_diagnostics(
    blueprint: StoryBlueprint,
    diagnostics: list[StructureDiagnostic],
    medium_contract: object,
    scope_profile: object,
    contract_snap: object,
    engine: object,
) -> None:
    from auteur.genres.models import ScopeProfile
    from auteur.blueprint import MediumContract, StoryEngine

    if not isinstance(scope_profile, ScopeProfile) or not isinstance(medium_contract, MediumContract):
        return

    failure_modes_text = " ".join(medium_contract.medium_failure_modes).lower()
    length_class = blueprint.identity.length_class
    length_name = length_class.value if hasattr(length_class, "value") else str(length_class)
    medium_name = medium_contract.medium.value if hasattr(medium_contract.medium, "value") else str(medium_contract.medium)
    genre_name = getattr(contract_snap, "display_name", "Unknown")
    genre_mechanical = (
        scope_profile.mechanical_load
    )

    # Check 1: Medium failure mode warns about "too many threads" and genre expects many threads
    thread_count = len(engine.threads) if isinstance(engine, StoryEngine) else 0
    if "too many threads" in failure_modes_text and thread_count > 2:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.SCOPE,
                rule="medium.genre_runway_mismatch.too_many_threads",
                message=(
                    f"The '{medium_name}' medium warns against too many threads, but "
                    f"the '{genre_name}' genre has {thread_count} subordinate thread(s). "
                    f"The medium may lack runway to develop them all."
                ),
                evidence=[
                    f"medium = {medium_name}",
                    f"medium_failure_modes = {medium_contract.medium_failure_modes}",
                    f"thread_count = {thread_count}",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Reduce the number of subordinate threads to fit the medium's capacity.",
                        "Switch to a longer medium (e.g., novel instead of short story) that accommodates more threads.",
                    ],
                    challenge_intent=[
                        "Keep the thread count if the medium's representation units can handle rapid thread-switching."
                    ],
                ),
            )
        )

    # Check 2: Medium warns about "novel-scale machinery" and genre has high mechanical load
    if "novel-scale machinery" in failure_modes_text and genre_mechanical:
        if _mechanical_load_order(ml) >= 2:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.SCOPE,
                    rule="medium.genre_runway_mismatch.machinery_overload",
                    message=(
                        f"The '{medium_name}' medium warns against novel-scale machinery, "
                        f"but the '{genre_name}' genre requires '{ml}' mechanical load. "
                        f"The medium may be too short for the genre's machinery."
                    ),
                    evidence=[
                        f"medium = {medium_name}",
                        f"genre.mechanical_load = {ml.value if hasattr(ml, 'value') else ml}",
                        f"length_class = {length_name}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Compress the narrative machinery significantly to fit the shorter medium.",
                            "Select a longer medium that can support the genre's mechanical demands.",
                        ],
                        challenge_intent=[
                            "Keep the short medium if the machinery is delivered through compression strategies."
                        ],
                    ),
                )
            )


def _add_layer9_resonance_diagnostics(
    blueprint: StoryBlueprint,
    diagnostics: list[StructureDiagnostic],
    engine: object,
) -> None:
    from auteur.blueprint import StoryEngine

    if not isinstance(engine, StoryEngine):
        return

    # 1. Motif alignment — do motifs appear in the story engine or character data?
    motifs = blueprint.theme.motifs
    if motifs:
        engine_text = " ".join(
            [
                engine.main_thread.want.author_text,
                engine.main_thread.change.author_text,
                engine.main_thread.thematic_function,
                *(t.thematic_function for t in engine.threads),
            ]
        ).casefold()
        char_text = " ".join(
            [c.name for c in blueprint.characters]
            + [
                m.description for c in blueprint.characters for m in c.key_milestones
            ]
        ).casefold()
        combined_text = engine_text + " " + char_text
        missing_motifs = [
            m for m in motifs if m.casefold() not in combined_text
        ]
        if missing_motifs and len(missing_motifs) == len(motifs):
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.THEME,
                    rule="theme.motifs_unrepresented",
                    message=(
                        f"None of the declared motifs ({', '.join(motifs)}) appear in the "
                        f"story engine or character data. Motifs that never surface in the "
                        f"narrative machinery may feel decorative."
                    ),
                    evidence=[
                        f"theme.motifs = {motifs}",
                        "No motif terms found in story engine author_text, thematic functions, or character data.",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Incorporate one or more motifs into thread thematic_functions or character milestones.",
                            "Revise the motif list to match the actual thematic levers of the story.",
                        ],
                        challenge_intent=[
                            "Keep motifs abstract if they function as author-guiding themes rather than explicit narrative signals."
                        ],
                    ),
                )
            )
        elif missing_motifs:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.INFO,
                    layer=DiagnosticLayer.THEME,
                    rule="theme.motifs_partially_unrepresented",
                    message=(
                        f"Some motifs ({', '.join(missing_motifs)}) do not appear in the "
                        f"story engine or character data."
                    ),
                    evidence=[
                        f"theme.motifs = {motifs}",
                        f"missing_from_narrative = {missing_motifs}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            f"Incorporate '{', '.join(missing_motifs)}' into a thread thematic_function or character milestone."
                        ],
                        challenge_intent=[
                            "Keep absent motifs as tonal references if they do not need explicit narrative expression."
                        ],
                    ),
                )
            )

    # 2. Central question echoing — does the emotional arc engage the central question?
    central_q = blueprint.theme.central_question
    if central_q and blueprint.emotional_design.per_act_tones:
        tone_text = " ".join(
            f"{t.label} {t.tone}" for t in blueprint.emotional_design.per_act_tones
        ).casefold()
        q_terms = set(
            w for w in central_q.casefold().split()
            if len(w) > 3 and w not in _STOP_WORDS
        )
        if q_terms and not any(term in tone_text for term in q_terms):
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.INFO,
                    layer=DiagnosticLayer.THEME,
                    rule="theme.central_question_disconnected",
                    message=(
                        "The emotional act tones do not reference the central thematic question. "
                        "The dramatic arc may feel disconnected from the thematic inquiry."
                    ),
                    evidence=[
                        f"theme.central_question = {central_q}",
                        f"per_act_tones = {[f'{t.label}: {t.tone}' for t in blueprint.emotional_design.per_act_tones]}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Integrate a reference to the central question into one or more act tone descriptions.",
                            "Ensure each act's emotional work serves the thematic question.",
                        ],
                        challenge_intent=[
                            "Keep act tones independent if the thematic question operates at a meta level above act emotion."
                        ],
                    ),
                )
            )

    # 3. Target experience connection — does thesis connect to target experience?
    thesis = blueprint.theme.thesis
    target_exp = blueprint.identity.target_experience
    if thesis and target_exp and target_exp.primary:
        thesis_lower = thesis.casefold()
        primary_lower = target_exp.primary.casefold()
        conflict_lower = engine.main_thread.conflict.author_text.casefold()
        if primary_lower not in thesis_lower and primary_lower not in conflict_lower:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.INFO,
                    layer=DiagnosticLayer.THEME,
                    rule="theme.target_experience_disconnected",
                    message=(
                        f"The primary target experience ('{target_exp.primary}') is not echoed "
                        f"in the theme thesis or the main thread conflict. The emotional promise "
                        f"may feel disconnected from the thematic argument."
                    ),
                    evidence=[
                        f"target_experience.primary = {target_exp.primary}",
                        f"theme.thesis = {thesis}",
                        f"main_thread.conflict = {engine.main_thread.conflict.author_text}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Reference the target experience emotion in the theme thesis or main conflict.",
                            "Align the central question to interrogate the promised experience.",
                        ],
                        challenge_intent=[
                            "Keep disconnected if the thesis operates as a philosophical counterpoint to the emotional promise."
                        ],
                    ),
                )
            )

    # 4. Auto-generated thesis detection
    thesis = blueprint.theme.thesis
    if thesis:
        thesis_lower = thesis.casefold()
        auto_signals = 0
        if thesis_lower.startswith("the pursuit of"):
            auto_signals += 1
        if "leads to" in thesis_lower:
            auto_signals += 1
        if "resulting in" in thesis_lower:
            auto_signals += 1
        if auto_signals >= 2:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.THEME,
                    rule="theme.thesis_looks_auto_generated",
                    message=(
                        "The theme thesis appears to be auto-generated from template fields "
                        "(contains 'pursuit of' + 'leads to' + 'resulting in'). Auto-generated "
                        "theses are structurally correct but read as filler. Replace with a "
                        "purpose-written thesis that argues the story's actual stance."
                    ),
                    evidence=[
                        f"theme.thesis = {thesis}",
                        "thesis matches the auto-compile template pattern",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Rewrite the thesis as a direct, opinionated statement of the story's argument.",
                            "Use the central question and motifs as raw material for the thesis.",
                        ],
                        challenge_intent=[
                            "Keep the generated thesis if it genuinely captures the intended argument."
                        ],
                    ),
                )
            )


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
