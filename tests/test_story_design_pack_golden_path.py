from pathlib import Path

from auteur.story_design_packs.golden_path import run_golden_path
from auteur.story_design_packs.integration import build_discovery_tutor_guidance


PACKS = ["superhero", "anti_hero", "hard_determinism", "corporate_superhuman_metropolis"]
PREMISE = (
    "A government-contracted superhero discovers that a predictive system can forecast his choices "
    "with near-perfect accuracy. He uses determinism to justify increasingly instrumental actions."
)


def test_v1_golden_path_uses_existing_acceptance_and_structure(tmp_path: Path):
    identity_path = tmp_path / "story_identity.yaml"
    structure_path = tmp_path / "blueprint.yaml"
    assert not identity_path.exists()
    assert not structure_path.exists()

    result = run_golden_path(tmp_path, PREMISE, PACKS)

    assert result.accepted_identity_path == identity_path
    assert result.structure_path == structure_path
    assert identity_path.exists()
    assert structure_path.exists()
    assert len(result.composition["selected_packs"]) == 4
    assert result.composition["productive_tensions"]
    assert result.tutor_guidance["authority_status"] == "DERIVED / NOT CANON"
    assert result.diagnostic_tutor_guidance["authority_status"] == "DERIVED / NOT CANON"
    assert result.tutor_guidance["recommendation"] not in result.candidate.open_questions
    assert "experimental_accident" not in str(result.candidate.model_dump())
    assert len(result.tutor_guidance["pack_sources"]) == 4


def test_golden_path_refuses_canonical_overwrite(tmp_path: Path):
    run_golden_path(tmp_path, PREMISE, PACKS)
    import pytest
    with pytest.raises(FileExistsError):
        run_golden_path(tmp_path, PREMISE, PACKS)


def test_tutor_boundary_consumes_synthetic_interactions_not_just_pack_lists():
    single = build_discovery_tutor_guidance(["superhero"], premise=PREMISE, decision="power origin")
    composed = build_discovery_tutor_guidance(PACKS, premise=PREMISE, decision="power origin")
    assert single["authority_status"] == composed["authority_status"] == "DERIVED / NOT CANON"
    assert len(single["pack_sources"]) == 1
    assert len(composed["pack_sources"]) == 4
    assert composed["tradeoffs"] != single["tradeoffs"] or composed["story_application"] != single["story_application"]
