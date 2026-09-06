"""Executable engineering golden path for the V1 pack/tutor integration."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from auteur.blueprint import Genre, StoryMedium, StoryMode, TargetExperience
from auteur.cli_handlers import handle_identity_promote
from auteur.cli_serializers import serialize_identity_promote
from auteur.identity import HighLevelCentralEngine, StoryIdentity
from auteur.identity import compile_to_blueprint
from auteur.story_design_packs.composition import compose_packs
from auteur.story_design_packs.tutor import tutor_recommend, tutorize_diagnostic
from auteur.structure.analyzer import analyze_structure


@dataclass
class GoldenPathResult:
    premise: str
    candidate: StoryIdentity
    accepted_identity_path: Path
    structure_path: Path
    composition: dict
    tutor_guidance: dict
    diagnostic: dict
    diagnostic_tutor_guidance: dict


def build_story_identity_candidate(premise: str) -> StoryIdentity:
    """Create a story-specific proposal for offline integration testing.

    Pack options are deliberately not copied into this identity. The candidate
    contains only commitments derived from the premise and the author's
    selected direction.
    """
    return StoryIdentity(
        title="Forecast of Choice",
        core_answer=premise,
        target_experience=TargetExperience(primary="dread", progression="uncertainty -> dread -> resolve", avoid=[]),
        story_type={"medium": StoryMedium.NOVEL, "mode": StoryMode.TRAGIC, "genre": Genre.OTHER, "subgenres": ["superhero"]},
        central_engine=HighLevelCentralEngine(
            want="Use extraordinary power to prevent a predicted catastrophe.",
            resistance="A predictive institution and the protagonist's own certainty that resistance is futile.",
            conflict="The protagonist must choose whether to accept or defy a forecast of his own instrumental violence.",
            stakes="People's safety, public trust, and the protagonist's moral identity.",
            change="He learns to treat responsibility as a practice of choosing under causes rather than as proof of metaphysical freedom.",
        ),
        not_this=["A story where the philosophy is only stated in dialogue."],
        open_questions=["What consequence follows when the prediction is resisted?"],
        confidence=0.8,
        recommendation_mode="opinionated",
        best_basis="genre_aligned",
        why_this_is_best="This direction makes the premise's prediction and responsibility conflict visible through escalating choices.",
        alternatives=["Accept the forecast and become an efficient protector."],
        rejected_directions=["A purely philosophical debate without consequential action."],
    )


def run_golden_path(project_root: Path, premise: str, pack_ids: list[str]) -> GoldenPathResult:
    """Run packs → tutor → candidate → existing acceptance → Structure → tutor."""
    project_root.mkdir(parents=True, exist_ok=True)
    discovery = project_root / "story_discovery"
    discovery.mkdir(exist_ok=True)
    composition = compose_packs(pack_ids)
    guidance = tutor_recommend(pack_ids, decision="protagonist moral boundary", premise=premise)
    candidate = build_story_identity_candidate(premise)
    candidate_path = discovery / "candidate.yaml"
    candidate.to_yaml(candidate_path)
    identity_path = project_root / "story_identity.yaml"
    if identity_path.exists():
        raise FileExistsError(f"golden path refuses to overwrite existing identity: {identity_path}")

    validation = handle_identity_promote(candidate)
    if not validation.is_success:
        raise ValueError(validation.error or "story identity candidate failed validation")
    serialize_identity_promote(candidate, identity_path)
    accepted = StoryIdentity.from_yaml(identity_path)
    blueprint = compile_to_blueprint(accepted)
    structure_path = project_root / "blueprint.yaml"
    structure_path.write_text(
        yaml.safe_dump(blueprint.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    diagnostics = analyze_structure(blueprint)
    if not diagnostics:
        raise ValueError("golden path expected at least one deterministic diagnostic")
    diagnostic = diagnostics[0]
    return GoldenPathResult(
        premise=premise,
        candidate=candidate,
        accepted_identity_path=identity_path,
        structure_path=structure_path,
        composition=composition.model_dump(mode="json"),
        tutor_guidance=guidance.model_dump(mode="json"),
        diagnostic=diagnostic.model_dump(mode="json"),
        diagnostic_tutor_guidance=tutorize_diagnostic(diagnostic, story_context=candidate.title).model_dump(mode="json"),
    )
