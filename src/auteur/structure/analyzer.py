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
) -> list[StructureDiagnostic]:
    """Run all active diagnostic rules across all layers.

    Currently runs:
    - Layers 1-5: analyze_structure() for within-blueprint coherence (Structure Diagnostic)
    - Layer 6: audit_bible_locations() for Bible Audit carrier state consistency
    - Layer 7: audit_outline_carriers() for Scene Representation validation (requires outline)

    Args:
        blueprint: The StoryBlueprint to validate.
        bible: The StoryBible event log to audit.
        outline: Optional parsed outline dict (from load_outline). When None, a
            Layer 7 WARNING is emitted noting that Scene Representation validation
            was skipped.

    Returns a single merged list of StructureDiagnostic findings.
    """
    from auteur.structure.outline_audit import audit_outline_carriers

    diagnostics: list[StructureDiagnostic] = []
    diagnostics.extend(analyze_structure(blueprint))
    diagnostics.extend(
        as_structure_diagnostic(d) for d in audit_bible_locations(bible)
    )
    diagnostics.extend(
        as_structure_diagnostic(d) for d in audit_outline_carriers(outline, bible)
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
