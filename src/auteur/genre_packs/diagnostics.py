"""Genre-aware structural diagnostics (Layer 2 read-only analysis).

Composition order (stable, no duplicates):
  1. Generic structural diagnostics from analyze_structure()
  2. Accepted-profile diagnostics (D-RES-001/002/003)
  3. Pack-specific diagnostics (erotica rules, etc.)

The canonical analyzer (analyze_structure) is the sole source of
D-RES-001/002/003. Pack-specific rules live here.
"""

from typing import TYPE_CHECKING
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)

if TYPE_CHECKING:
    from auteur.identity import StoryIdentity
    from auteur.blueprint import StoryBlueprint


def run_genre_diagnostics(
    identity: "StoryIdentity",
    blueprint: "StoryBlueprint | None" = None,
) -> list[StructureDiagnostic]:
    """Run genre-aware structural evaluations on StoryIdentity and optional StoryBlueprint.

    Diagnostics are strictly read-only and return explicit findings.

    When a blueprint is provided, canonical structural diagnostics from
    analyze_structure() are included first, then pack-specific rules.
    Duplicate diagnostics (same rule ID) are suppressed in favour of the
    first occurrence.
    """
    from auteur.structure.analyzer import analyze_structure

    diagnostics: list[StructureDiagnostic] = []

    # 1. Generic structural + profile diagnostics (D-RES-001/002/003)
    # Deduplicate by rule ID: first occurrence wins.
    seen_rules: set[str] = set()
    # Pack-specific tests and callers may provide a lightweight blueprint-like
    # object that has acts but is not a complete StoryBlueprint.  Keep those
    # callers on the pack-specific path; canonical analysis requires the
    # complete structural model.
    if blueprint is not None and hasattr(blueprint, "story_engine"):
        for d in analyze_structure(blueprint):
            if d.rule not in seen_rules:
                diagnostics.append(d)
                seen_rules.add(d.rule)

    # 2. Pack-specific diagnostics
    if not identity.genre_profile:
        return diagnostics

    gp = identity.genre_profile
    if gp.primary_pack_id != "erotic_fiction":
        return diagnostics

    # 1. desire_affects_decisions
    rule_desire = "genre.erotic_fiction.desire_affects_decisions"
    if rule_desire not in seen_rules:
        want_text = identity.central_engine.want.casefold()
        if not any(word in want_text for word in ["desire", "intimacy", "attraction", "passion", "longing", "bond", "seduction"]):
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule=rule_desire,
                    message="Central engine 'want' does not explicitly incorporate erotic desire or intimate motivation.",
                    evidence=[f"central_engine.want = {identity.central_engine.want}"],
                    repair_options=RepairOptions(
                        preserve_intent=["Connect the central desire directly to the protagonist's core want."],
                        challenge_intent=[],
                    ),
                )
            )

    # 2. Evaluation on StoryBlueprint if provided
    rule_scene_state = "genre.erotic_fiction.intimate_scenes_change_state"
    rule_scene_func = "genre.erotic_fiction.scene_function_diversity"
    rule_erotic_arc = "genre.erotic_fiction.resolution_addresses_erotic_arc"
    if blueprint is not None and hasattr(blueprint, "acts"):
        # Check scene function diversity and intimate scene state change
        intimate_scenes = []
        scene_functions_used = []

        for act in blueprint.acts:
            for chapter in act.chapters:
                for scene in chapter.scenes:
                    st_lower = scene.summary.casefold()
                    if any(w in st_lower for w in ["intimate", "attraction", "boundary", "seduction", "embrace", "passion"]):
                        intimate_scenes.append(scene)
                        if hasattr(scene, "scene_function") and scene.scene_function:
                            scene_functions_used.append(scene.scene_function)

        # Rule 2: Intimate scenes change state
        if rule_scene_state not in seen_rules:
            for idx, sc in enumerate(intimate_scenes):
                if not getattr(sc, "state_change", None) and "changes" not in sc.summary.casefold():
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.WARNING,
                            layer=DiagnosticLayer.REPRESENTATION,
                            rule=rule_scene_state,
                            message=f"Intimate scene '{sc.title or f'Scene {idx+1}'}' does not record a clear narrative state change.",
                            evidence=[f"scene_summary = {sc.summary}"],
                            repair_options=RepairOptions(
                                preserve_intent=["Add explicit knowledge, power, or relational state change to this scene."],
                                challenge_intent=[],
                            ),
                        )
                    )

        # Rule 3: Scene function diversity
        if rule_scene_func not in seen_rules and len(scene_functions_used) >= 2 and len(set(scene_functions_used)) == 1:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.REPRESENTATION,
                    rule=rule_scene_func,
                    message="Consecutive intimate scenes repeat the exact same scene function without structural variation.",
                    evidence=[f"repeated_function = {scene_functions_used[0]}"],
                    repair_options=RepairOptions(
                        preserve_intent=["Vary scene functions (e.g. alternate test_boundary with expose_vulnerability)."],
                        challenge_intent=[],
                    ),
                )
            )

        # Rule 4: Resolution addresses erotic arc
        if rule_erotic_arc not in seen_rules and blueprint.acts and len(blueprint.acts) >= 3:
            act3_text = " ".join([sc.summary for ch in blueprint.acts[-1].chapters for sc in ch.scenes]).casefold()
            if not any(w in act3_text for w in ["desire", "intimacy", "love", "bond", "surrender", "fulfillment", "transformation"]):
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        layer=DiagnosticLayer.STRUCTURAL_FORCES,
                        rule=rule_erotic_arc,
                        message="The Act 3 climax/resolution fails to address the accepted erotic arc or intimacy commitment.",
                        evidence=[f"act3_summary_sample = {act3_text[:120]}"],
                        repair_options=RepairOptions(
                            preserve_intent=["Integrate the erotic arc payoff directly into Act 3 resolution scenes."],
                            challenge_intent=[],
                        ),
                    )
                )

    return diagnostics
