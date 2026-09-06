from auteur.story_design_packs.tutor import tutor_recommend
from auteur.story_design_packs.integration import build_diagnostic_tutor_guidance, build_story_design_context
from auteur.structure.diagnostics import DiagnosticLayer, DiagnosticSeverity, RepairOptions, StructureDiagnostic


def test_tutor_guidance_contains_teaching_and_author_boundary():
    guidance = tutor_recommend(
        ["superhero", "anti_hero", "hard_determinism"],
        decision="protagonist moral boundary",
        premise="a hero who believes free will is an illusion",
    )
    assert guidance.recommendation
    assert guidance.plain_language_explanation
    assert guidance.story_application.startswith("In ")
    assert guidance.tradeoffs
    assert guidance.alternatives
    assert guidance.question_for_author
    assert guidance.authority_status == "DERIVED / NOT CANON"


def test_diagnostic_tutor_is_derived_and_preserves_repair_boundary():
    diagnostic = StructureDiagnostic(
        severity=DiagnosticSeverity.WARNING,
        layer=DiagnosticLayer.STRUCTURAL_FORCES,
        rule="structure.setup_without_payoff",
        message="A prominent setup has no visible payoff.",
        repair_options=RepairOptions(preserve_intent=["Add or transform the payoff."], challenge_intent=["Remove the setup."]),
    )
    guidance = build_diagnostic_tutor_guidance(diagnostic, story_context="the current novel")
    assert guidance["diagnostic_rule"] == "structure.setup_without_payoff"
    assert guidance["repair_options"] == ["Add or transform the payoff.", "Remove the setup."]
    assert guidance["authority_status"] == "DERIVED / NOT CANON"


def test_story_discovery_context_is_none_without_packs_and_serializable_with_packs():
    assert build_story_design_context(None) is None
    context = build_story_design_context(["superhero", "anti_hero"])
    assert context["selected_packs"][0]["pack_id"] == "superhero"
    assert context["productive_tensions"]
