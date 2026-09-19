"""Premise-to-architecture analysis services for the beginner flow."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Protocol

from pydantic import BaseModel, ConfigDict, ValidationError

from auteur.llm import LLMClient, LLMRequest, RetriableError
from auteur.story_design_packs.models import PackProvenance

from .architecture_models import (
    ArchitectureActivation,
    ArchitectureAlternative,
    ArchitectureCertainty,
    ArchitectureComponent,
    ArchitectureDerivation,
    ArchitectureEvidence,
    ArchitectureFacet,
    ArchitectureRole,
    NarrativeArchitectureAnalysis,
)


class ArchitectureAnalysisError(ValueError):
    """Raised when rich architecture analysis is malformed or unsupported."""


class ArchitectureAnalyzer(Protocol):
    def analyze(
        self,
        *,
        premise: str,
        source_provenance: tuple[PackProvenance, ...],
    ) -> NarrativeArchitectureAnalysis:
        raise NotImplementedError


def premise_fingerprint(premise: str) -> str:
    normalized = " ".join(premise.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def analysis_basis_fingerprint(analysis: NarrativeArchitectureAnalysis) -> str:
    payload = analysis.model_dump(mode="json", exclude={"analysis_id"})
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _normalized_concept(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def _component_id(facet: ArchitectureFacet, label: str) -> str:
    normalized = _normalized_text(label)
    digest = hashlib.sha256((facet.value + "\0" + normalized).encode("utf-8")).hexdigest()[:12]
    return f"{facet.value}:{digest}"


def _excerpt_occurs(premise: str, excerpt: str) -> bool:
    return _normalized_text(excerpt) in _normalized_text(premise)


def _provider_derivation(label: str, premise: str) -> ArchitectureDerivation:
    if _normalized_text(label) in _normalized_text(premise):
        return ArchitectureDerivation.PREMISE_EXPLICIT
    return ArchitectureDerivation.MODEL_INFERENCE


class _ProviderAlternative(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    rationale: str


class _ProviderEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    excerpt: str
    label: str = "premise"


class _ProviderComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    facet: ArchitectureFacet
    label: str
    role: ArchitectureRole
    certainty: ArchitectureCertainty
    rationale: str
    evidence: tuple[_ProviderEvidence, ...] = ()
    alternatives: tuple[_ProviderAlternative, ...] = ()


class _ProviderAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    components: tuple[_ProviderComponent, ...]


class ProviderArchitectureAnalyzer:
    """Ask an LLM for one coherent interpretation, then normalize deterministically."""

    def __init__(
        self,
        client: LLMClient,
        analyzer_id: str,
        analyzer_version: str,
        model_id: str,
        provider_id: str = "configured-provider",
    ) -> None:
        self.client = client
        self.analyzer_id = analyzer_id
        self.analyzer_version = analyzer_version
        self.model_id = model_id
        self.provider_id = provider_id

    def analyze(
        self,
        *,
        premise: str,
        source_provenance: tuple[PackProvenance, ...],
    ) -> NarrativeArchitectureAnalysis:
        if not premise.strip():
            raise ArchitectureAnalysisError("premise must not be blank")
        request = LLMRequest(
            system=(
                "You are Auteur's premise interpretation engine. Return JSON only. "
                "Produce exactly one coherent interpretation of the supplied premise. "
                "Components must use one of these facets: genre_constellation, narrative_engine, "
                "character_function, aesthetic_framing, trope_family, relationship_dynamic, "
                "setting_world, theme_motif. Each component must contain label, role "
                "(primary/supporting/flavor), certainty (clear/likely/uncertain), rationale, "
                "evidence as exact premise excerpts, and component-local alternatives only when "
                "certainty is uncertain. Do not assign IDs, canonical fields, authority, activation, "
                "review state, or epistemic/derivation status."
            ),
            user=(
                "Interpret this premise as narrative architecture without turning inference into canon.\n\n"
                f"PREMISE:\n{premise}"
            ),
            max_tokens=4096,
            temperature=0.2,
            model=self.model_id,
        )
        response = self.client.complete(request)
        try:
            raw = json.loads(response.text)
            draft = _ProviderAnalysis.model_validate(raw)
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            raise ArchitectureAnalysisError("malformed rich architecture analysis") from exc

        components: list[ArchitectureComponent] = []
        for item in draft.components:
            if item.alternatives and item.certainty is not ArchitectureCertainty.UNCERTAIN:
                raise ArchitectureAnalysisError("component alternatives require uncertain certainty")
            evidence: list[ArchitectureEvidence] = []
            for evidence_item in item.evidence:
                if not evidence_item.excerpt.strip() or not _excerpt_occurs(premise, evidence_item.excerpt):
                    raise ArchitectureAnalysisError("evidence excerpt must occur in premise")
                evidence.append(
                    ArchitectureEvidence(
                        source_kind="premise",
                        label=evidence_item.label,
                        excerpt=evidence_item.excerpt,
                    )
                )
            alternatives = tuple(
                ArchitectureAlternative(label=alternative.label, rationale=alternative.rationale)
                for alternative in item.alternatives[:3]
            )
            activation = (
                ArchitectureActivation.SUPPRESSED
                if item.certainty is ArchitectureCertainty.UNCERTAIN
                else ArchitectureActivation.ACTIVE
            )
            components.append(
                ArchitectureComponent(
                    component_id=_component_id(item.facet, item.label),
                    facet=item.facet,
                    label=item.label,
                    normalized_concept=_normalized_concept(item.label),
                    derivation=_provider_derivation(item.label, premise),
                    role=item.role,
                    certainty=item.certainty,
                    activation=activation,
                    rationale=item.rationale,
                    evidence=tuple(evidence),
                    alternatives=alternatives,
                    source_provenance=source_provenance,
                )
            )

        fingerprint = premise_fingerprint(premise)
        normalized_payload = json.dumps(
            draft.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        digest = hashlib.sha256(
            (fingerprint + "\0" + self.analyzer_id + "\0" + self.analyzer_version + "\0" + normalized_payload).encode(
                "utf-8"
            )
        ).hexdigest()[:16]
        try:
            return NarrativeArchitectureAnalysis(
                analysis_id=f"analysis:{digest}",
                premise_fingerprint=fingerprint,
                analyzer_id=self.analyzer_id,
                analyzer_version=self.analyzer_version,
                provider_id=self.provider_id,
                model_id=self.model_id,
                summary=draft.summary,
                components=tuple(components),
                source_provenance=source_provenance,
            )
        except ValidationError as exc:
            raise ArchitectureAnalysisError("invalid rich architecture analysis") from exc


_EXPLICIT_SIGNALS: dict[str, tuple[str, ...]] = {
    "mystery": ("investigate", "investigation", "clue", "mystery", "discover the truth"),
    "superhero fiction": ("superhero", "masked hero", "superhuman", "cape"),
    "relationship betrayal": ("partner", "lover", "spouse", "relationship", "betrayal", "affair"),
    "secret identity": ("secret identity", "masked identity", "public identity"),
}


def _first_signal(text: str, signals: tuple[str, ...]) -> str | None:
    lowered = text.casefold()
    return next((signal for signal in signals if signal in lowered), None)


class DeterministicArchitectureAnalyzer:
    """Bounded explicit-signal fallback used when rich interpretation is unavailable."""

    analyzer_id = "beginner-architecture-fallback"
    analyzer_version = "1"

    def analyze(
        self,
        *,
        premise: str,
        source_provenance: tuple[PackProvenance, ...],
    ) -> NarrativeArchitectureAnalysis:
        if not premise.strip():
            raise ArchitectureAnalysisError("premise must not be blank")
        components: list[ArchitectureComponent] = []

        mystery_signal = _first_signal(premise, _EXPLICIT_SIGNALS["mystery"])
        if mystery_signal is not None:
            components.append(
                ArchitectureComponent(
                    component_id=_component_id(ArchitectureFacet.GENRE_CONSTELLATION, "Mystery"),
                    facet=ArchitectureFacet.GENRE_CONSTELLATION,
                    label="Mystery",
                    normalized_concept="mystery",
                    derivation=ArchitectureDerivation.CURATED_MATCH,
                    role=ArchitectureRole.PRIMARY,
                    certainty=ArchitectureCertainty.CLEAR,
                    rationale="A deterministic premise signal matches mystery investigation.",
                    evidence=(
                        ArchitectureEvidence(
                            source_kind="premise",
                            label="explicit mystery signal",
                            excerpt=mystery_signal,
                        ),
                    ),
                    source_provenance=source_provenance,
                )
            )
            components.append(
                ArchitectureComponent(
                    component_id=_component_id(ArchitectureFacet.NARRATIVE_ENGINE, "Investigation and revelation"),
                    facet=ArchitectureFacet.NARRATIVE_ENGINE,
                    label="Investigation and revelation",
                    normalized_concept="investigation_revelation",
                    derivation=ArchitectureDerivation.CURATED_MATCH,
                    role=ArchitectureRole.PRIMARY,
                    certainty=ArchitectureCertainty.LIKELY,
                    rationale="Mystery investigation signals support a bounded investigation/revelation engine.",
                    evidence=(
                        ArchitectureEvidence(
                            source_kind="premise",
                            label="investigation signal",
                            excerpt=mystery_signal,
                        ),
                    ),
                    source_provenance=source_provenance,
                )
            )

        superhero_signal = _first_signal(premise, _EXPLICIT_SIGNALS["superhero fiction"])
        if superhero_signal is not None:
            components.append(
                ArchitectureComponent(
                    component_id=_component_id(ArchitectureFacet.GENRE_CONSTELLATION, "Superhero fiction"),
                    facet=ArchitectureFacet.GENRE_CONSTELLATION,
                    label="Superhero fiction",
                    normalized_concept="superhero",
                    derivation=ArchitectureDerivation.CURATED_MATCH,
                    role=ArchitectureRole.SUPPORTING,
                    certainty=ArchitectureCertainty.CLEAR,
                    rationale="A deterministic premise signal matches superhero fiction.",
                    evidence=(
                        ArchitectureEvidence(
                            source_kind="premise",
                            label="superhero signal",
                            excerpt=superhero_signal,
                        ),
                    ),
                    source_provenance=source_provenance,
                )
            )

        lowered = premise.casefold()
        relationship_present = any(token in lowered for token in ("partner", "lover", "spouse", "relationship"))
        betrayal_present = any(token in lowered for token in ("betrayal", "affair", "betray"))
        if relationship_present and betrayal_present:
            excerpt = "relationship" if "relationship" in lowered else next(
                token for token in ("partner", "lover", "spouse") if token in lowered
            )
            components.append(
                ArchitectureComponent(
                    component_id=_component_id(ArchitectureFacet.RELATIONSHIP_DYNAMIC, "Relationship betrayal"),
                    facet=ArchitectureFacet.RELATIONSHIP_DYNAMIC,
                    label="Relationship betrayal",
                    normalized_concept="relationship_betrayal",
                    derivation=ArchitectureDerivation.CURATED_MATCH,
                    role=ArchitectureRole.SUPPORTING,
                    certainty=ArchitectureCertainty.CLEAR,
                    rationale="Relationship and betrayal signals co-occur in the premise.",
                    evidence=(
                        ArchitectureEvidence(
                            source_kind="premise",
                            label="relationship signal",
                            excerpt=excerpt,
                        ),
                    ),
                    source_provenance=source_provenance,
                )
            )

        identity_signal = _first_signal(premise, _EXPLICIT_SIGNALS["secret identity"])
        if identity_signal is not None:
            components.append(
                ArchitectureComponent(
                    component_id=_component_id(ArchitectureFacet.TROPE_FAMILY, "Secret identity"),
                    facet=ArchitectureFacet.TROPE_FAMILY,
                    label="Secret identity",
                    normalized_concept="secret_identity",
                    derivation=ArchitectureDerivation.CURATED_MATCH,
                    role=ArchitectureRole.SUPPORTING,
                    certainty=ArchitectureCertainty.CLEAR,
                    rationale="A deterministic premise signal matches secret-identity story logic.",
                    evidence=(
                        ArchitectureEvidence(
                            source_kind="premise",
                            label="identity signal",
                            excerpt=identity_signal,
                        ),
                    ),
                    source_provenance=source_provenance,
                )
            )

        labels = [component.label for component in components]
        summary = "Detected premise signals: " + ", ".join(labels) + "." if labels else "No supported architecture signals detected."
        fingerprint = premise_fingerprint(premise)
        return NarrativeArchitectureAnalysis(
            analysis_id=f"analysis:fallback:{fingerprint[:16]}",
            premise_fingerprint=fingerprint,
            analyzer_id=self.analyzer_id,
            analyzer_version=self.analyzer_version,
            summary=summary,
            components=tuple(components),
            source_provenance=source_provenance,
            availability_note=(
                "Rich narrative interpretation was unavailable; showing the bounded explicit-signal fallback."
            ),
        )


class ResilientArchitectureAnalyzer:
    def __init__(
        self,
        *,
        primary: ArchitectureAnalyzer,
        fallback: ArchitectureAnalyzer,
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    def analyze(
        self,
        *,
        premise: str,
        source_provenance: tuple[PackProvenance, ...],
    ) -> NarrativeArchitectureAnalysis:
        try:
            return self.primary.analyze(premise=premise, source_provenance=source_provenance)
        except (ArchitectureAnalysisError, RetriableError):
            fallback = self.fallback.analyze(premise=premise, source_provenance=source_provenance)
            return fallback.model_copy(
                update={
                    "availability_note": (
                        "Rich narrative interpretation was unavailable; "
                        "showing the bounded explicit-signal fallback."
                    )
                }
            )
