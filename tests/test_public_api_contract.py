"""Regression guard for the supported package-root import contract."""

from auteur import __all__


EXPECTED_ROOT_EXPORTS = {
    "ActStructure", "ArcType", "AuthorAudienceContract", "BestBasis", "Character",
    "CharacterState", "ConsequenceScale", "DiagnosticLayer", "DiagnosticSeverity",
    "EmotionalBlueprint", "EndingTone", "Genre", "LengthClass", "MainThread",
    "MechanicalLoad", "MediumContract", "MediumFormat", "NarrativeRunway",
    "PipelineRunner", "PlanningCall", "PlanningScope", "ProjectIdentity",
    "InteractionModel", "ReleaseModel", "ScopeComplexity", "ScopeContract",
    "SettingFootprint", "RepairOptions", "RecommendationMode", "StoryBible",
    "StoryBlueprint", "StoryEngine", "StoryMedium", "StoryMode", "StoryThread",
    "StoryTimeframe", "StructuralClaim", "StructuralConstants", "StructureDiagnostic",
    "SupportFunction", "TargetAudience", "TargetExperience", "ThreadType",
    "TensionTarget", "TensionWaveform", "ThematicCore", "TropeLoad", "UnitOfDelivery",
    "StoryIdentity", "compile_to_blueprint", "analyze_structure", "render_cartographer_prompt",
}


def test_package_root_exports_are_frozen_for_1x() -> None:
    assert set(__all__) == EXPECTED_ROOT_EXPORTS
    assert len(__all__) == len(EXPECTED_ROOT_EXPORTS)
