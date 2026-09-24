"""Adapter from existing Story Discovery into the beginner journey."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Protocol

from auteur.blueprint import Genre, StoryMode, TargetExperience
from auteur.cli_handlers import RecommendOpenEndedData, handle_identity_recommend
from auteur.identity import (
    HighLevelCentralEngine,
    RecommendationMode,
    StoryIdentity,
    StoryType,
)
from auteur.llm import LLMClient, RetriableError
from auteur.story_discovery_recommend import recommend_candidate_outputs

from .architecture_analysis import analysis_basis_fingerprint
from .architecture_models import (
    ArchitectureActivation,
    ArchitectureCertainty,
    ArchitectureFacet,
    ArchitectureRole,
    NarrativeArchitectureAnalysis,
)
from .contracts import WorkingComposition
from .discovery_models import (
    DiscoveryDirection,
    DiscoveryRecommendation,
    DiscoveryRecommendationStatus,
)


def discovery_basis_fingerprint(
    analysis: NarrativeArchitectureAnalysis,
    composition: WorkingComposition | None,
) -> str:
    """Fingerprint only material inputs that may change Discovery guidance."""
    dimensions = []
    if composition is not None:
        dimensions = [
            {
                "dimension_id": item.dimension_id,
                "category": item.category.value,
                "origin": item.origin.value,
                "status": item.status.value,
                "activation": item.activation.value,
                "label": item.label,
                "author_rationale": item.author_rationale,
                "source_provenance": [
                    source.model_dump(mode="json")
                    for source in item.source_provenance
                ],
            }
            for item in sorted(
                composition.dimensions,
                key=lambda dimension: dimension.dimension_id,
            )
        ]
    payload = {
        "analysis_id": analysis.analysis_id,
        "analysis_basis": analysis_basis_fingerprint(analysis),
        "dimensions": dimensions,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class DiscoveryRecommender(Protocol):
    def recommend(
        self,
        *,
        premise: str,
        analysis: NarrativeArchitectureAnalysis,
    ) -> DiscoveryRecommendation:
        raise NotImplementedError


class UnavailableDiscoveryRecommender:
    def __init__(self, reason: str = "No reasoning provider configured.") -> None:
        self.reason = reason

    def recommend(
        self,
        *,
        premise: str,
        analysis: NarrativeArchitectureAnalysis,
    ) -> DiscoveryRecommendation:
        del premise
        basis = analysis_basis_fingerprint(analysis)
        return DiscoveryRecommendation(
            recommendation_id=f"discovery:unavailable:{basis[:16]}",
            source_analysis_id=analysis.analysis_id,
            source_basis_fingerprint=basis,
            status=DiscoveryRecommendationStatus.UNAVAILABLE,
            recommended_direction_id=None,
            rationale=self.reason,
            directions=(),
        )


def _design_context(analysis: NarrativeArchitectureAnalysis) -> dict[str, object]:
    active = [
        {
            "component_id": component.component_id,
            "facet": component.facet.value,
            "label": component.label,
            "role": component.role.value,
            "certainty": component.certainty.value,
            "derivation": component.derivation.value,
            "rationale": component.rationale,
            "evidence": [
                {
                    "label": evidence.label,
                    "excerpt": evidence.excerpt,
                    "source_kind": evidence.source_kind,
                }
                for evidence in component.evidence
            ],
        }
        for component in analysis.components
        if component.activation is ArchitectureActivation.ACTIVE
    ]
    unresolved = [
        {
            "component_id": component.component_id,
            "facet": component.facet.value,
            "label": component.label,
            "alternatives": [alternative.label for alternative in component.alternatives],
            "rationale": component.rationale,
        }
        for component in analysis.components
        if component.certainty is ArchitectureCertainty.UNCERTAIN
    ]
    return {
        "architecture_summary": analysis.summary,
        "active_interpretation": active,
        "consequential_unresolved_interpretation": unresolved,
        "instruction": (
            "Treat active interpretation as derived working guidance, not canon. "
            "When unresolved components are coupled and materially change the engine, target experience, "
            "payoff, or Story Identity, resolve them as distinct coherent directions rather than independent checkboxes."
        ),
    }


def _architecture_summary(analysis: NarrativeArchitectureAnalysis) -> str:
    primary = [
        component.label
        for component in analysis.components
        if component.activation is ArchitectureActivation.ACTIVE and component.role.value == "primary"
    ]
    supporting = [
        component.label
        for component in analysis.components
        if component.activation is ArchitectureActivation.ACTIVE and component.role.value == "supporting"
    ]
    pieces: list[str] = []
    if primary:
        pieces.append("Primary: " + ", ".join(primary))
    if supporting:
        pieces.append("Supporting: " + ", ".join(supporting))
    return "; ".join(pieces) if pieces else analysis.summary


def _recommendation_id(
    basis: str,
    directions: tuple[DiscoveryDirection, ...],
    recommended_direction_id: str | None,
) -> str:
    payload = json.dumps(
        {
            "basis": basis,
            "directions": [direction.direction_id for direction in directions],
            "recommended": recommended_direction_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"discovery:{digest}"


class StoryDiscoveryRecommender:
    """Reuse Story Discovery search and judgment without writing files or canon."""

    def __init__(self, *, client: LLMClient, requested_candidates: int = 3) -> None:
        if requested_candidates < 2:
            raise ValueError("beginner Discovery requires at least two requested candidates")
        self.client = client
        self.requested_candidates = requested_candidates

    def recommend(
        self,
        *,
        premise: str,
        analysis: NarrativeArchitectureAnalysis,
    ) -> DiscoveryRecommendation:
        basis = analysis_basis_fingerprint(analysis)
        try:
            result = handle_identity_recommend(
                client=self.client,
                premise_text=premise,
                recommend_mode="open_ended",
                candidates_count=self.requested_candidates,
                strict_candidate_count=False,
                design_context=_design_context(analysis),
            )
        except RetriableError:
            result = None

        if result is None or not result.is_success or not isinstance(result.data, RecommendOpenEndedData):
            return DiscoveryRecommendation(
                recommendation_id=f"discovery:unavailable:{basis[:16]}",
                source_analysis_id=analysis.analysis_id,
                source_basis_fingerprint=basis,
                status=DiscoveryRecommendationStatus.UNAVAILABLE,
                recommended_direction_id=None,
                rationale="Rich story-direction search is temporarily unavailable.",
                directions=(),
            )

        candidate_outputs = result.data.candidates
        if not candidate_outputs:
            return DiscoveryRecommendation(
                recommendation_id=f"discovery:unavailable:{basis[:16]}",
                source_analysis_id=analysis.analysis_id,
                source_basis_fingerprint=basis,
                status=DiscoveryRecommendationStatus.UNAVAILABLE,
                recommended_direction_id=None,
                rationale="Rich story-direction search is temporarily unavailable.",
                directions=(),
            )

        try:
            judgment = recommend_candidate_outputs(
                client=self.client,
                premise_text=premise,
                candidate_outputs=candidate_outputs,
                requested_candidates=self.requested_candidates,
                genre=None,
                medium=None,
                mode=None,
            )
        except (RetriableError, ValueError):
            return DiscoveryRecommendation(
                recommendation_id=f"discovery:unavailable:{basis[:16]}",
                source_analysis_id=analysis.analysis_id,
                source_basis_fingerprint=basis,
                status=DiscoveryRecommendationStatus.UNAVAILABLE,
                recommended_direction_id=None,
                rationale="Rich story-direction search is temporarily unavailable.",
                directions=(),
            )

        candidate_to_direction = {
            candidate.candidate_id: f"direction:{candidate.candidate_id}"
            for candidate in candidate_outputs
        }
        architecture_summary = _architecture_summary(analysis)
        source_component_ids = tuple(component.component_id for component in analysis.components)
        directions = tuple(
            DiscoveryDirection(
                direction_id=candidate_to_direction[candidate.candidate_id],
                title=candidate.identity.title,
                summary=candidate.identity.core_answer,
                identity_candidate=candidate.identity,
                architecture_summary=architecture_summary,
                tradeoffs=tuple(candidate.candidate.tradeoffs),
                risks=tuple(candidate.candidate.risks),
                source_analysis_id=analysis.analysis_id,
                source_component_ids=source_component_ids,
            )
            for candidate in candidate_outputs
        )
        recommended_direction_id = (
            candidate_to_direction[judgment.recommended_candidate_id]
            if judgment.recommended_candidate_id is not None
            else None
        )
        status = (
            DiscoveryRecommendationStatus.READY
            if judgment.status == "recommended"
            else DiscoveryRecommendationStatus.NEEDS_AUTHOR_CHOICE
        )
        recommendation_id = _recommendation_id(
            basis,
            directions,
            recommended_direction_id,
        )
        return DiscoveryRecommendation(
            recommendation_id=recommendation_id,
            source_analysis_id=analysis.analysis_id,
            source_basis_fingerprint=basis,
            status=status,
            recommended_direction_id=recommended_direction_id,
            rationale=judgment.rationale,
            directions=directions,
        )


_GENRE_BY_LABEL: dict[str, Genre] = {
    "Mystery": Genre.MYSTERY,
    "Thriller": Genre.THRILLER,
    "Horror": Genre.HORROR,
    "Romance": Genre.ROMANCE,
    "Superhero fiction": Genre.OTHER,
    "Speculative fiction": Genre.OTHER,
}


@dataclass(frozen=True)
class _DirectionTemplate:
    title: str
    core_answer: str
    target_experience: str
    want: str
    resistance: str
    conflict: str
    stakes: str
    change: str
    genre: Genre


_ENGINE_TEMPLATES: dict[str, _DirectionTemplate] = {
    "Investigation and revelation": _DirectionTemplate(
        title="The unraveling case",
        core_answer="The truth will surface, and knowing it will cost the protagonist something.",
        target_experience="dread",
        want="Uncover what actually happened.",
        resistance="The truth is buried under misdirection and self-protection.",
        conflict="The need for certainty against the cost of exposure.",
        stakes="The protagonist's judgment of someone they trusted.",
        change="The protagonist accepts an unwelcome truth and acts on it.",
        genre=Genre.MYSTERY,
    ),
    "Escalating danger and pursuit": _DirectionTemplate(
        title="The closing net",
        core_answer="Survival depends on staying ahead of a threat that keeps getting closer.",
        target_experience="suspense",
        want="Escape or stop the threat before it reaches them.",
        resistance="The pursuer anticipates every move.",
        conflict="Flight against the need to turn and fight.",
        stakes="The protagonist's life and the safety of those with them.",
        change="The protagonist stops running and confronts the threat.",
        genre=Genre.THRILLER,
    ),
    "Dread and confrontation with the monstrous": _DirectionTemplate(
        title="What waits in the dark",
        core_answer="The horror must be faced, and facing it will change who the protagonist is.",
        target_experience="dread",
        want="Survive and understand the horror.",
        resistance="The horror exploits the protagonist's fear and denial.",
        conflict="Denial against the necessity of confrontation.",
        stakes="The protagonist's sanity and the safety of the community.",
        change="The protagonist confronts the horror and is remade by it.",
        genre=Genre.HORROR,
    ),
    "Desire, courtship, and commitment": _DirectionTemplate(
        title="The choice of the heart",
        core_answer="Love becomes real only when it is chosen against something that matters.",
        target_experience="longing",
        want="Win or keep the love that matters.",
        resistance="Circumstance, pride, or a rival blocks the union.",
        conflict="Desire against the cost of commitment.",
        stakes="The protagonist's chance at lasting intimacy.",
        change="The protagonist chooses love with open eyes.",
        genre=Genre.ROMANCE,
    ),
    "Public/private identity pressure": _DirectionTemplate(
        title="The double life at the breaking point",
        core_answer="The public self and the private self can no longer both be protected.",
        target_experience="tension",
        want="Protect the people and the identity that depend on the protagonist.",
        resistance="Every choice exposes one self to save the other.",
        conflict="Public duty against private truth.",
        stakes="The protagonist's identity and the trust of those closest.",
        change="The protagonist accepts that the two selves must become one.",
        genre=Genre.OTHER,
    ),
    "Wonder, rules of the fantastic, and consequence": _DirectionTemplate(
        title="The price of the impossible",
        core_answer="The fantastic obeys rules, and every use of it demands a price.",
        target_experience="wonder",
        want="Master or survive the rules of the fantastic.",
        resistance="The rules exact costs the protagonist cannot foresee.",
        conflict="Ambition against the consequences of power.",
        stakes="The protagonist's world and the order that holds it together.",
        change="The protagonist accepts the price and chooses what to spend it on.",
        genre=Genre.OTHER,
    ),
}

_GENERIC_INNER_TEMPLATE = _DirectionTemplate(
    title="The inward cost",
    core_answer="The real battle is what the protagonist must become to see it through.",
    target_experience="dread",
    want="Resolve the pressure without losing themselves.",
    resistance="The protagonist's own fear and self-protection.",
    conflict="The need to act against the fear of what acting will cost.",
    stakes="The protagonist's sense of who they are.",
    change="The protagonist accepts a changed self to move forward.",
    genre=Genre.OTHER,
)

_GENERIC_OUTWARD_TEMPLATE = _DirectionTemplate(
    title="The outward reckoning",
    core_answer="The pressure must be answered in the world, not only inside the protagonist.",
    target_experience="tension",
    want="Change the situation that is closing in.",
    resistance="The world pushes back harder with every move.",
    conflict="The cost of acting against the cost of doing nothing.",
    stakes="The protagonist's place in the world they are trying to change.",
    change="The protagonist acts and accepts the consequences in the open.",
    genre=Genre.OTHER,
)

_RELATIONSHIP_TEMPLATE = _DirectionTemplate(
    title="Trust on trial",
    core_answer="The relationship cannot survive without the truth, and the truth may end it.",
    target_experience="jealous uncertainty",
    want="Know whether the person they love can be trusted.",
    resistance="Evidence and doubt keep reinterpreting every intimacy.",
    conflict="Love against the demand for certainty.",
    stakes="The relationship and the protagonist's ability to trust again.",
    change="The protagonist chooses what to believe and lives with the cost.",
    genre=Genre.OTHER,
)

_IDENTITY_TEMPLATE = _DirectionTemplate(
    title="The exposed self",
    core_answer="The hidden self cannot stay hidden, and exposure rewrites every relationship.",
    target_experience="tension",
    want="Control when and how the truth about them comes out.",
    resistance="The world is already closing in on the secret.",
    conflict="Secrecy against the freedom of being known.",
    stakes="The protagonist's safety and the people tied to the secret.",
    change="The protagonist chooses to be known rather than protected.",
    genre=Genre.OTHER,
)


def _identity_from_template(
    template: _DirectionTemplate,
    genre: Genre,
    experience_override: str | None = None,
) -> StoryIdentity:
    return StoryIdentity(
        title=template.title,
        core_answer=template.core_answer,
        story_type=StoryType(genre=genre, mode=StoryMode.OTHER),
        target_experience=TargetExperience(
            primary=experience_override or template.target_experience,
            progression="rising",
            avoid=[],
        ),
        central_engine=HighLevelCentralEngine(
            want=template.want,
            resistance=template.resistance,
            conflict=template.conflict,
            stakes=template.stakes,
            change=template.change,
        ),
        recommendation_mode=RecommendationMode.OPEN_ENDED,
    )


class DeterministicDiscoveryRecommender:
    """Bounded curated story directions used when rich search is unavailable.

    Deterministic Curated Mode: directions are derived from the active working
    architecture with curated templates, never from model inference. No
    recommendation is manufactured; the author chooses the direction.
    """

    def recommend(
        self,
        *,
        premise: str,
        analysis: NarrativeArchitectureAnalysis,
    ) -> DiscoveryRecommendation:
        del premise
        basis = analysis_basis_fingerprint(analysis)
        active = tuple(
            component
            for component in analysis.components
            if component.activation is ArchitectureActivation.ACTIVE
        )
        engine_component = next(
            (
                component
                for component in active
                if component.facet is ArchitectureFacet.NARRATIVE_ENGINE
                and component.role is ArchitectureRole.PRIMARY
            ),
            None,
        )
        genre_component = next(
            (
                component
                for component in active
                if component.facet is ArchitectureFacet.GENRE_CONSTELLATION
                and component.role is ArchitectureRole.PRIMARY
            ),
            None,
        )
        relationship_component = next(
            (component for component in active if component.facet is ArchitectureFacet.RELATIONSHIP_DYNAMIC),
            None,
        )
        identity_component = next(
            (
                component
                for component in active
                if component.facet in (ArchitectureFacet.SETTING_WORLD, ArchitectureFacet.TROPE_FAMILY)
            ),
            None,
        )

        engine_template = _ENGINE_TEMPLATES.get(engine_component.label) if engine_component else None
        primary_genre = engine_template.genre if engine_template is not None else Genre.OTHER
        if genre_component is not None:
            primary_genre = _GENRE_BY_LABEL.get(genre_component.label, primary_genre)

        frames: list[tuple[object | None, _DirectionTemplate]] = []
        if engine_component is not None:
            frames.append((engine_component, engine_template or _GENERIC_OUTWARD_TEMPLATE))
        if relationship_component is not None:
            frames.append((relationship_component, _RELATIONSHIP_TEMPLATE))
        if identity_component is not None:
            frames.append((identity_component, _IDENTITY_TEMPLATE))
        if len(frames) < 2:
            frames.append((None, _GENERIC_INNER_TEMPLATE))
        if len(frames) < 2:
            frames.append((None, _GENERIC_OUTWARD_TEMPLATE))

        architecture_summary = _architecture_summary(analysis)
        # When a relationship dynamic is active it supplies the emotional
        # promise, matching the composition rule in mapping.py so the
        # synthesized candidate integrates instead of raising a spurious
        # composition tension.
        experience_override = (
            "jealous uncertainty" if relationship_component is not None else None
        )
        directions: list[DiscoveryDirection] = []
        for component, template in frames:
            source_ids = (
                tuple(item.component_id for item in active)
                if component is None
                else (component.component_id,)
            )
            digest = hashlib.sha256(f"{basis}|{template.title}".encode("utf-8")).hexdigest()[:16]
            directions.append(
                DiscoveryDirection(
                    direction_id=f"direction:{digest}",
                    title=template.title,
                    summary=template.core_answer,
                    identity_candidate=_identity_from_template(
                        template, primary_genre, experience_override
                    ),
                    architecture_summary=architecture_summary,
                    tradeoffs=(template.resistance,),
                    risks=(template.conflict,),
                    source_analysis_id=analysis.analysis_id,
                    source_component_ids=source_ids,
                )
            )

        return DiscoveryRecommendation(
            recommendation_id=_recommendation_id(basis, tuple(directions), None),
            source_analysis_id=analysis.analysis_id,
            source_basis_fingerprint=basis,
            status=DiscoveryRecommendationStatus.NEEDS_AUTHOR_CHOICE,
            recommended_direction_id=None,
            rationale=(
                "Deterministic curated directions derived from the current working "
                "architecture; choose the direction this story should take."
            ),
            directions=tuple(directions),
        )
