"""Candidate-only Studio architecture handoff. No Story Identity or Structure mutation.

The browser cannot invoke an arbitrary parent coding agent. It creates a neutral
request that the active host may fulfill; the validated response stays working.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import yaml
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_serializer, model_validator

from auteur.narrative_ontology.architecture_preferences import (
    CausalDistributionPreference, ComplexityPreference, EngineHierarchyPreference,
)
from auteur.host_agent import (
    _atomic_json_write,
    HostAgentRequest,
    build_host_agent_request,
    build_host_agent_response,
    load_host_agent_request,
    model_output_contract,
    validate_host_agent_response,
    write_host_agent_request,
    write_host_agent_response,
)
from .persistence import BeginnerConcurrencyError, _FilesystemLock
from .studio_architecture_review import build_architecture_review, candidate_diff
from .studio_architecture_graph_intent import GraphIntent, resolve_graph_intent
from .studio_concepts import (
    ProvisionalNarrativeConcept, list_provisional_concepts,
    record_provisional_concept,
)
from .studio_ontology_context import build_relevant_ontology_context
from .studio_architecture_questions import identity_problems as question_identity_problems
from .studio_architecture_questions import question_changes
from .studio_store import CanvasStore

_candidate_diff = candidate_diff


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


class ArchitectureNode(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    title: str = Field(min_length=1, max_length=120)
    category: Literal[
        "reader_experience", "aesthetic", "genre", "trope", "engine",
        "thread", "structure", "theme", "character", "relationship", "other"
    ]
    summary: str = Field(min_length=1, max_length=2000)
    scope: str = Field(default="whole_story", max_length=100)
    parent_id: str | None = None


class ArchitectureLink(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    source: str
    target: str
    function: str = Field(min_length=1, max_length=120)


# Deliberately small, replaceable story-design vocabulary; not a neural measurement.
BasicEmotion = Literal["joy", "sadness", "fear", "anger", "disgust", "surprise"]


class EmotionTarget(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    emotion: BasicEmotion
    role: Literal["primary", "supporting", "contrasting", "local"]
    intended_effect: str = Field(min_length=1, max_length=450)
    eliciting_condition: str = Field(min_length=1, max_length=600)
    aesthetic_strategy: str = Field(min_length=1, max_length=600)
    provenance: Literal["author_declared", "agent_proposed"]


class ComplexEmotion(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    title: str = Field(min_length=1, max_length=120)
    basic_emotions: list[BasicEmotion] = Field(min_length=2, max_length=6)
    context: str = Field(min_length=1, max_length=600)

    @model_validator(mode="after")
    def distinct_components(self) -> "ComplexEmotion":
        if len(set(self.basic_emotions)) != len(self.basic_emotions):
            raise ValueError("complex-emotion components must be distinct")
        return self


class TropeFunctionRef(BaseModel):
    """Names the trope node whose conceptual identity one contextual trope function realises.

    The function stays local to its owner (a genre contract or a phase activation); the node
    stays the shared trope identity. The reference never makes the two equal.
    """
    model_config = ConfigDict(extra="forbid", strict=True)
    function_index: int = Field(ge=0, le=11)
    trope_node_id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")


class GenreContract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    genre_node_id: str
    role: Literal["governing", "supporting", "tertiary", "local"]
    emotion_target_ids: list[str] = Field(default_factory=list, max_length=20)
    complex_emotion_ids: list[str] = Field(default_factory=list, max_length=12)
    trope_functions: list[str] = Field(min_length=1, max_length=12)
    trope_function_refs: list[TropeFunctionRef] = Field(default_factory=list, max_length=12)

    @model_serializer(mode="wrap")
    def _omit_empty_trope_refs(self, handler):
        # Proposals without references serialize exactly as before, so revision diffs see no change.
        data = handler(self)
        if not data.get("trope_function_refs"):
            data.pop("trope_function_refs", None)
        return data
    narrative_engine: str = Field(min_length=1, max_length=1200)
    structural_pattern: str = Field(min_length=1, max_length=1200)
    aesthetic_strategies: list[str] = Field(default_factory=list, max_length=12)
    payoff_expectations: list[str] = Field(min_length=1, max_length=8)


class GenreInteraction(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    source_genre_id: str
    target_genre_id: str
    kind: Literal["reinforces", "enables", "constrains", "contrasts",
                  "creates_tension", "converges"]
    mechanism: str = Field(min_length=1, max_length=900)
    risk: str | None = Field(default=None, max_length=600)


class GenreActivation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    genre_node_id: str
    basic_emotions: list[BasicEmotion] = Field(default_factory=list, max_length=6)
    trope_functions: list[str] = Field(default_factory=list, max_length=8)
    trope_function_refs: list[TropeFunctionRef] = Field(default_factory=list, max_length=8)

    @model_serializer(mode="wrap")
    def _omit_empty_trope_refs(self, handler):
        data = handler(self)
        if not data.get("trope_function_refs"):
            data.pop("trope_function_refs", None)
        return data
    structural_function: str = Field(min_length=1, max_length=700)


class GenreParticipation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    genre: str = Field(min_length=1, max_length=120)
    role: Literal["governing", "locally_dominant", "supporting", "background"]


class NarrativePhase(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    title: str = Field(min_length=1, max_length=120)
    order: int = Field(ge=0, le=1000)
    scope: str = Field(default="whole_story", max_length=100)
    genres: list[GenreParticipation] = Field(default_factory=list, max_length=8)
    genre_activations: list[GenreActivation] = Field(default_factory=list, max_length=8)
    reader_experience: str | None = Field(default=None, max_length=400)
    aesthetic: str | None = Field(default=None, max_length=400)
    narrative_function: str = Field(min_length=1, max_length=1000)
    transition: str | None = Field(default=None, max_length=700)
    parallel_with: list[str] = Field(default_factory=list, max_length=12)


class ArchitectureOpportunity(BaseModel):
    """A bounded, incidental creative possibility noticed while doing requested work.

    It is not a defect, not a required author decision, and not narrative meaning.
    It exists so an author can see a promising possibility without it displacing
    the work they asked for.
    """

    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    title: str = Field(min_length=1, max_length=160)
    why_it_matters: str = Field(min_length=1, max_length=600)
    scope: Literal[
        "book", "series", "character", "relationship", "theme", "other"
    ] = "other"
    relationship: Literal[
        "deepens", "reinterprets", "replaces", "unclear"
    ] = "unclear"
    artistic_potential: str | None = Field(default=None, max_length=600)
    intention_fidelity: str | None = Field(default=None, max_length=600)
    requires_author_decision: bool = False
    provisional_primary: bool = False

    @model_validator(mode="after")
    def replacement_requires_author_decision(self) -> "ArchitectureOpportunity":
        if (
            self.relationship == "replaces"
            and not self.requires_author_decision
            and not self.provisional_primary
        ):
            raise ValueError(
                "replacing the author's expressed purpose must be flagged either as "
                "requiring an author decision or as a provisional primary direction "
                "under explicitly delegated goal discovery"
            )
        return self


class ArchitectureInterpretation(BaseModel):
    """A consequential working interpretation the agent is using as if it were given.

    It is not author-established. It exists so a load-bearing invention - a world
    rule, the meaning of an author commitment, or a proposed resolution of an
    author-reserved question - stays visible as a recommendation rather than being
    reported as settled narrative fact.
    """

    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    interpretation: str = Field(min_length=1, max_length=800)
    affects: list[str] = Field(min_length=1, max_length=12)
    consequences: str = Field(min_length=1, max_length=800)
    alternative: str | None = Field(default=None, max_length=800)
    author_decision_required: bool = False


def _validate_trope_refs(functions: list[str], refs: list[TropeFunctionRef], trope_ids: set[str]) -> None:
    indexes = [ref.function_index for ref in refs]
    if len(set(indexes)) != len(indexes):
        raise ValueError("a trope function is referenced more than once")
    for ref in refs:
        if ref.function_index >= len(functions):
            raise ValueError("trope function reference points past its function list")
        if ref.trope_node_id not in trope_ids:
            raise ValueError(f"trope function reference names no trope node: {ref.trope_node_id!r}")


class ArchitectureCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1, 2]
    summary: str = Field(min_length=1, max_length=3000)
    nodes: list[ArchitectureNode] = Field(min_length=1, max_length=80)
    links: list[ArchitectureLink] = Field(default_factory=list, max_length=180)
    phases: list[NarrativePhase] = Field(default_factory=list, max_length=32)
    open_questions: list[str] = Field(default_factory=list, max_length=16)
    # Stable identities for the open questions, in the same order. Absent in legacy candidates; a
    # revision may introduce them and must then keep each continuing question's id (see studio_architecture_questions).
    open_question_ids: list[str] | None = Field(default=None, max_length=16)
    opportunities: list[ArchitectureOpportunity] = Field(
        default_factory=list, max_length=3,
    )
    interpretations: list[ArchitectureInterpretation] = Field(
        default_factory=list, max_length=12,
    )
    emotion_targets: list[EmotionTarget] = Field(default_factory=list, max_length=30)
    complex_emotions: list[ComplexEmotion] = Field(default_factory=list, max_length=16)
    genre_contracts: list[GenreContract] = Field(default_factory=list, max_length=14)
    genre_interactions: list[GenreInteraction] = Field(default_factory=list, max_length=40)

    @model_validator(mode="after")
    def valid_graph(self, info: ValidationInfo) -> "ArchitectureCandidate":
        if info.context and info.context.get("new_host_agent_response") and self.schema_version != 2:
            raise ValueError("new Studio architecture responses must use schema_version 2")
        nodes = {node.id for node in self.nodes}
        if len({item.id for item in self.interpretations}) != len(self.interpretations):
            raise ValueError("duplicate interpretation id")
        for item in self.interpretations:
            missing = [identifier for identifier in item.affects if identifier not in nodes]
            if missing:
                raise ValueError(
                    f"interpretation {item.id!r} affects unknown nodes: {', '.join(missing)}"
                )
        phases = {phase.id for phase in self.phases}
        if len(nodes) != len(self.nodes) or len(phases) != len(self.phases):
            raise ValueError("duplicate candidate node or phase id")
        if len({link.id for link in self.links}) != len(self.links):
            raise ValueError("duplicate candidate link id")
        if sum(1 for item in self.opportunities if item.provisional_primary) > 1:
            raise ValueError(
                "at most one opportunity may be the provisional primary direction"
            )
        if any(link.source not in nodes or link.target not in nodes or link.source == link.target
               for link in self.links):
            raise ValueError("candidate connection references missing or identical nodes")
        parents = {node.id: node.parent_id for node in self.nodes}
        for node in self.nodes:
            visited: set[str] = set()
            current = node.id
            while current is not None:
                if current in visited:
                    raise ValueError("candidate node hierarchy has a cycle")
                visited.add(current)
                if current not in parents:
                    raise ValueError("candidate hierarchy references missing parent")
                current = parents[current]
        if any(ref not in phases or ref == phase.id
               for phase in self.phases for ref in phase.parallel_with):
            raise ValueError("phase parallel_with references missing or identical phase")
        # Trope references are checked for every version: a field accepted without checks would bypass them.
        trope_ids = {node.id for node in self.nodes if node.category == "trope"}
        for genre in self.genre_contracts:
            _validate_trope_refs(genre.trope_functions, genre.trope_function_refs, trope_ids)
        for phase in self.phases:
            for activation in phase.genre_activations:
                _validate_trope_refs(activation.trope_functions, activation.trope_function_refs, trope_ids)
        if self.schema_version == 2:
            # Architecture-only proposals carry mechanisms. Character and relationship instances belong to
            # other operations, so the shared category type stays broader than this validator allows.
            forbidden = {"character", "relationship"}
            if any(node.category in forbidden for node in self.nodes):
                raise ValueError("architecture-only proposals cannot instantiate characters or relationships")
            target_ids = {target.id for target in self.emotion_targets}
            complex_ids = {emotion.id for emotion in self.complex_emotions}
            contracts = {genre.genre_node_id for genre in self.genre_contracts}
            if len(target_ids) != len(self.emotion_targets) or len(complex_ids) != len(self.complex_emotions):
                raise ValueError("duplicate emotional design identifier")
            if len(contracts) != len(self.genre_contracts):
                raise ValueError("duplicate genre contract identifier")
            if any(genre.genre_node_id not in nodes or
                   next(n for n in self.nodes if n.id == genre.genre_node_id).category != "genre"
                   for genre in self.genre_contracts):
                raise ValueError("genre contracts must reference genre nodes")
            for genre in self.genre_contracts:
                if any(ref not in target_ids for ref in genre.emotion_target_ids):
                    raise ValueError("genre references unknown basic-emotion target")
                if any(ref not in complex_ids for ref in genre.complex_emotion_ids):
                    raise ValueError("genre references unknown complex emotion")
            if len({edge.id for edge in self.genre_interactions}) != len(self.genre_interactions):
                raise ValueError("duplicate genre interaction identifier")
            if any(edge.source_genre_id not in contracts or edge.target_genre_id not in contracts
                   or edge.source_genre_id == edge.target_genre_id for edge in self.genre_interactions):
                raise ValueError("genre interaction requires two distinct existing contracts")
            if any(activation.genre_node_id not in contracts
                   for phase in self.phases for activation in phase.genre_activations):
                raise ValueError("phase references unknown genre contract")
        return self


class SelectedCreativeAlternative(BaseModel):
    """Author-chosen alternative from a completed read-only inquiry; noncanonical working context only."""
    model_config = ConfigDict(extra="forbid", strict=True)
    inquiry_request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    hypothesis_id: str = Field(pattern=r"^h[1-9][0-9]{0,2}$")


class SelectedOpportunity(BaseModel):
    """An author-chosen opportunity from the current working candidate.

    It provides noncanonical working context only. Selecting one never accepts it
    and never replaces the governing architecture.
    """

    model_config = ConfigDict(extra="forbid", strict=True)
    candidate_request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    opportunity_id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")


def _root(store: CanvasStore) -> Path:
    return store.directory / "architecture"


def _read(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    if not isinstance(data, dict):
        raise ValueError("Studio architecture artifact must be an object")
    return data


def _candidate(store: CanvasStore) -> dict | None:
    return _read(_root(store) / "current.json")


_PROVISIONAL_CONCEPT_GROUP = "provisional-concepts"
_MAX_PROVISIONAL_CONCEPT_ITEMS = 16
_INTENTION_DIRECTIVE_LIMIT = 2000


def _intention_view(item, *, excerpt: bool = False) -> dict:
    """Author-directed continuing intention; working authority, never accepted canon."""
    entry = {
        "id": item.id,
        "title": item.title,
        "status": item.intention_status,
        "directive": item.content[:_INTENTION_DIRECTIVE_LIMIT] if excerpt else item.content,
        "source_ref": "canvas/items/" + item.id,
        "authority": "author_directed_working_intention",
    }
    if excerpt:
        entry["directive_characters"] = len(item.content)
        entry["directive_is_excerpt"] = len(item.content) > _INTENTION_DIRECTIVE_LIMIT
    if item.proposal_origin is not None:
        entry["provenance"] = item.proposal_origin.model_dump(mode="json")
    return entry


def _creative_intentions(store: CanvasStore) -> list[dict]:
    return [
        _intention_view(item)
        for item in store.load().items
        if item.intention_status is not None
    ]


def _source(
    store: CanvasStore, *, previous: dict | None = None, source_format: int = 2,
) -> dict:
    """Bound the agent-visible working source, without disguising omitted prose.

    Format 1 reproduces the exact historical projection for in-flight requests.
    Format 2 adds provenance metadata and content fingerprints for freshness;
    fingerprints never stand in for unavailable prose. Provisional concept notes
    are agent proposals, so they do not displace author working material.
    """
    if source_format not in (1, 2):
        raise ValueError("unsupported Studio working-source format")
    canvas = store.load()
    intention_items = [
        item for item in canvas.items if item.intention_status is not None
    ]
    all_items = [
        item for item in canvas.items
        if item.id != "story-vision" and item.group != _PROVISIONAL_CONCEPT_GROUP
        and item.intention_status is None
    ]
    provisional_items = [
        item for item in canvas.items if item.group == _PROVISIONAL_CONCEPT_GROUP
    ]
    selected = all_items[:24]
    visible_provisional = provisional_items[:_MAX_PROVISIONAL_CONCEPT_ITEMS]
    selected_ids = {item.id for item in selected}
    visible_ids = selected_ids | {item.id for item in visible_provisional}
    vision = next((item.content for item in canvas.items if item.id == "story-vision"), "")

    def project_item(item) -> dict:
        entry = {"id": item.id, "kind": item.kind, "title": item.title,
                 "group": item.group, "content": item.content[:1000]}
        if source_format == 2:
            entry["content_characters"] = len(item.content)
            entry["content_is_excerpt"] = len(item.content) > 1000
            if len(item.content) > 1000:
                entry["full_content_sha256"] = hashlib.sha256(
                    item.content.encode("utf-8")
                ).hexdigest()
        return entry

    items = [project_item(item) for item in selected]
    items.extend(project_item(item) for item in visible_provisional)
    included = [
        edge for edge in canvas.connections
        if edge.source in visible_ids and edge.target in visible_ids
    ][:80]
    result = {
        "vision": vision,
        "working_items": items,
        "working_connections": [
            {"source": edge.source, "target": edge.target, "label": edge.label}
            for edge in included
        ],
        "previous_candidate": previous,
    }
    if source_format == 2:
        excluded_items = all_items[24:]
        included_edge_ids = {edge.id for edge in included}
        excluded_edges = [
            edge for edge in canvas.connections if edge.id not in included_edge_ids
        ]
        result.update({
            "working_source_format": 2,
            "provisional_concept_item_count": len(visible_provisional),
            "omitted_provisional_concept_item_count": (
                len(provisional_items) - len(visible_provisional)
            ),
            "omitted_working_item_count": len(excluded_items),
            "omitted_working_connection_count": len(excluded_edges),
        })
        if excluded_items:
            result["omitted_working_items_sha256"] = _digest([
                item.model_dump(mode="json") for item in excluded_items
            ])
        if excluded_edges:
            result["omitted_working_connections_sha256"] = _digest([
                edge.model_dump(mode="json") for edge in excluded_edges
            ])
        if intention_items:
            # Author-directed intentions are always disclosed with their current status, never
            # silently filtered by recency. They bind in-flight requests through intention_sha256
            # without invalidating the applied candidate.
            result["creative_intentions"] = [
                _intention_view(item, excerpt=True) for item in intention_items
            ]
    return result


def _intention_fingerprint(store: CanvasStore) -> str:
    """Author-directed intentions bind in-flight requests without invalidating the applied candidate.

    An intention is guidance for the next revision, not evidence that the current architecture is wrong,
    so it never blocks realization. A pending request built while intentions differed is still stale.
    """
    return _digest(_creative_intentions(store))


_REALIZATION_COPY_KIND = "realization_element"
# A scene's manuscript and Quick Draft fields are downstream writing (owner decision A, #612);
# its identity (existence, kind, title, group, role) is what an architecture can depend on.
_SCENE_MANUSCRIPT_FIELDS = ("content", "scene_premise", "scene_intent", "quick_draft_session_id")


def _dependency_parts(
    store: CanvasStore, source_scene_ids: list[str] | None = None,
) -> tuple[dict[str, str], str]:
    """Freshness format 3: digest each governing dependency separately so staleness can name it.

    Governing: the Story Vision, accepted Identity, the author's own working notes,
    characters, places and questions with the connections among them, and the identity of
    each author scene the request was built from (``source_scene_ids``; ``None`` means every
    current author scene). Downstream, reported but never invalidating: every scene's
    manuscript and drafting fields, items copied from a Story Realization proposal, scenes
    created after the request, and connections touching them.
    Agent-proposed provisional concepts and continuing intentions keep their own handling.
    """
    canvas = store.load()
    governing, scenes, downstream = [], {}, []
    for item in canvas.items:
        if (item.id == "story-vision" or item.group == _PROVISIONAL_CONCEPT_GROUP
                or item.intention_status is not None):
            continue
        origin = item.proposal_origin
        if origin is not None and origin.source_kind == _REALIZATION_COPY_KIND:
            downstream.append(item.model_dump(mode="json"))
        elif item.kind == "scene":
            scenes[item.id] = {"kind": item.kind, "title": item.title, "group": item.group,
                               "architecture_role": item.architecture_role}
            downstream.append({"id": item.id, **{field: getattr(item, field) for field in _SCENE_MANUSCRIPT_FIELDS}})
        else:
            governing.append({"id": item.id, "kind": item.kind, "title": item.title, "group": item.group,
                              "content": item.content, "architecture_role": item.architecture_role})
    recorded = sorted(scenes) if source_scene_ids is None else source_scene_ids
    downstream.extend({"id": scene_id, **view} for scene_id, view in scenes.items() if scene_id not in recorded)
    governing_ids = {entry["id"] for entry in governing} | set(recorded)
    edges = [{"source": edge.source, "target": edge.target, "label": edge.label} for edge in canvas.connections]
    vision = next((item.content for item in canvas.items if item.id == "story-vision"), "")
    components = {
        "story_vision": _digest(vision),
        "accepted_identity": _digest(_accepted_story_design_context(store)),
        "working_sources": _digest({"items": governing, "connections": [
            edge for edge in edges if edge["source"] in governing_ids and edge["target"] in governing_ids
        ]}),
        **{"scene:" + scene_id: _digest(scenes.get(scene_id)) for scene_id in recorded},
    }
    return components, _digest({"items": downstream, "connections": [
        edge for edge in edges if edge["source"] not in governing_ids or edge["target"] not in governing_ids
    ]})


def _dependency_settings(store: CanvasStore) -> dict:
    components, downstream = _dependency_parts(store)
    return {
        "freshness_format": 3,
        "source_sha256": _digest(components),
        "source_components": components,
        "downstream_sha256": downstream,
    }


def _recorded_scene_ids(components: dict[str, str]) -> list[str]:
    return [name.removeprefix("scene:") for name in components if name.startswith("scene:")]


def _changed_dependencies(store: CanvasStore, settings: dict, request_user: str) -> list[str]:
    """Author-governed sources changed since a request was prepared, in its own recorded format."""
    if settings.get("freshness_format") == 3:
        recorded = settings["source_components"]
        now, _ = _dependency_parts(store, _recorded_scene_ids(recorded))
        return [name for name, digest in recorded.items() if now.get(name) != digest]
    if settings.get("freshness_format") == 2:
        changed = _author_source_fingerprint(store, json.loads(request_user)) != settings["source_sha256"]
    else:
        changed = _source_fingerprint(store, request_user) != settings["source_sha256"]
    return ["working_story"] if changed else []


def _downstream_changed(store: CanvasStore, settings: dict) -> bool:
    """Writing and copied proposals since the request: worth reconsidering, never invalidating."""
    if settings.get("freshness_format") != 3:
        return False
    return _dependency_parts(store, _recorded_scene_ids(settings["source_components"]))[1] != (
        settings["downstream_sha256"]
    )


def _guidance_changed(store: CanvasStore, settings: dict, request_user: str, expected: str | None = None) -> bool:
    if settings.get("freshness_format") not in (2, 3):
        return False
    expected = expected or settings.get("design_guidance_sha256")
    user = json.loads(request_user)
    return bool(expected) and _digest(
        _design_context_parts(store, _user_working_context(store, user))[1]
    ) != expected


def _stale_message(changed: list[str]) -> str:
    names = {"story_vision": "Story Vision", "accepted_identity": "accepted story identity",
             "working_sources": "working ideas that guide the architecture"}
    labels = sorted({names.get(name, "a source scene" if name.startswith("scene:") else "working story")
                     for name in changed})
    return ("the author's source vision or working story changed (" + ", ".join(labels)
            + "); response retained as stale evidence")


def _author_working_context(working: dict) -> dict:
    """Strip agent-proposed provisional notes and continuing intentions from the author-source fingerprint."""
    filtered = dict(working)
    filtered.pop("creative_intentions", None)
    filtered["working_items"] = [
        item for item in working.get("working_items", [])
        if item.get("group") != _PROVISIONAL_CONCEPT_GROUP
    ]
    visible_ids = {item["id"] for item in filtered["working_items"]}
    filtered["working_connections"] = [
        edge for edge in working.get("working_connections", [])
        if edge.get("source") in visible_ids and edge.get("target") in visible_ids
    ]
    filtered.pop("provisional_concept_item_count", None)
    filtered.pop("omitted_provisional_concept_item_count", None)
    return filtered


# A bounded, source-referenced projection of established narrative design rules.
# The source documents/models remain authoritative; this is generation context,
# not a competing ontology or a set of author-declared preferences.
_DESIGN_PRINCIPLES = (
    (
        "docs/narrative-architecture.md",
        "Ontology defines concept meaning; Identity owns accepted commitments, "
        "Structure owns plans, and Realization owns concrete events. "
        "Working Studio graphs never accept those commitments.",
    ),
    (
        "src/auteur/narrative_ontology/architecture_preferences.py",
        "Complexity, causal distribution and engine hierarchy are independent "
        "composition choices. Do not infer a declared value from another "
        "dimension or from the presence of many nodes.",
    ),
    (
        "docs/plans/story-discovery-intent-aware-architecture.md",
        "Identify the causal organizing principle: a single center, a primary "
        "engine with subordinate layers, or an ensemble of co-governing mechanisms. "
        "Make causal ownership, actor action patterns, pressures, reversals, payoff "
        "mechanics, and the hierarchy or its deliberate absence legible. Do not "
        "flatten mechanisms into an undifferentiated list.",
    ),
    (
        "docs/plans/story-discovery-intent-aware-architecture.md",
        "Explain craft propagation: causal strategy and ownership -> action/scene "
        "families and pressure -> texture and aesthetics -> reader experience -> "
        "thematic implications. Prefer causal interactions over decorative links.",
    ),
    (
        "docs/adr/008-rich-target-experience.md",
        "Distinguish the governing emotional promise, supporting/contrasting palette, "
        "avoided experience and macro trajectory. Rich TargetExperience is not "
        "equivalent to a count of basic-emotion labels.",
    ),
    (
        "data/ontology/base_ontology.yaml",
        "Use typed narrative relationships and their functions: conflict drives "
        "arcs, setups lead to payoffs, themes manifest through narrative change. "
        "Abstract Studio nodes are not concrete character, scene or beat instances.",
    ),
    (
        "docs/PRD.md",
        "Explain why this story's genre, trope, structure, aesthetic and emotional "
        "components affect each other. A flat label list is not enough; "
        "preserve unsupported dimensions as unknown.",
    ),
)

def _accepted_story_design_context(store: CanvasStore) -> dict | None:
    """Read a project's accepted Identity only, never a guessed author preference."""
    path = store.project_root / "story_identity.yaml"
    if not path.is_file():
        return None
    if not path.resolve().is_relative_to(store.project_root):
        raise ValueError("accepted Story Identity must remain inside the project root")
    # Avoid importing Identity in no-premise Studio sessions.
    from auteur.identity import StoryIdentity

    # Parse the exact bytes once; Pydantic's compatibility defaults are not
    # evidence that a missing field was explicitly committed by the author.
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    identity = StoryIdentity.model_validate(raw)
    preferences = identity.architecture_preferences
    context = {
        "source_ref": "story_identity.yaml",
        "authority": "accepted_story_identity",
        "title": identity.title,
        "core_answer": identity.core_answer,
        "central_engine": identity.central_engine.model_dump(mode="json"),
        "story_type": (
            identity.story_type.model_dump(
                mode="json", include=identity.story_type.model_fields_set,
                exclude_none=True,
            )
            if "story_type" in identity.model_fields_set else None
        ),
        "target_experience": (
            identity.target_experience.model_dump(
                mode="json", include=identity.target_experience.model_fields_set,
                exclude_none=True,
            )
            if "target_experience" in identity.model_fields_set else None
        ),
        "architecture_preferences": (
            preferences.model_dump(mode="json", exclude_none=True)
            if preferences is not None else None
        ),
        "hard_constraints": identity.hard_constraints,
        "not_this": identity.not_this,
    }
    if len(json.dumps(context, ensure_ascii=False).encode("utf-8")) > 65536:
        raise ValueError("accepted Story Identity exceeds the bounded Studio design context")
    return context


def _guidance_fields() -> dict:
    """Derived interpretive guidance; never author intent or accepted canon."""
    return {
        "kind": "source_referenced_narrative_design_guidance",
        "authority": "derived_guidance_not_author_intent",
        "source_principles": [
            {"source_ref": source, "principle": rule}
            for source, rule in _DESIGN_PRINCIPLES
        ],
        "architecture_preference_vocabulary": {
            "complexity": [value.value for value in ComplexityPreference],
            "causal_distribution": [value.value for value in CausalDistributionPreference],
            "engine_hierarchy": [value.value for value in EngineHierarchyPreference],
        },
        "unknown_policy": (
            "No accepted Identity or omitted preference means UNKNOWN, not an "
            "implicit focused/maximalist/causal default. The agent may propose "
            "a provisional composition with explicit rationale; it may not "
            "attribute that choice to the author."
        ),
    }


def _legacy_narrative_design_context(store: CanvasStore) -> dict:
    """Exact pre-ontology-context shape, for historical request packets."""
    context = _guidance_fields()
    context["accepted_story_identity"] = _accepted_story_design_context(store)
    return context


def _design_context_parts(
    store: CanvasStore, working: dict | None = None,
) -> tuple[dict | None, dict, dict]:
    """Return accepted Identity, derived guidance, and the packet projection."""
    accepted = _accepted_story_design_context(store)
    working = working if working is not None else _source(store)
    guidance = _guidance_fields()
    guidance["ontology_context"] = build_relevant_ontology_context(
        working.get("vision", ""), accepted,
    )
    return accepted, guidance, {**guidance, "accepted_story_identity": accepted}


def _narrative_design_context(store: CanvasStore) -> dict:
    """Compose the same small, auditable ontology guidance on develop and revise."""
    return _design_context_parts(store)[2]


def _user_working_context(store: CanvasStore, user: dict) -> dict:
    previous = user["working_context"]["previous_candidate"]
    source_format = 2 if user["working_context"].get("working_source_format") == 2 else 1
    return _source(store, previous=previous, source_format=source_format)


def _author_source_fingerprint(store: CanvasStore, user: dict) -> str:
    """Fingerprint only author-governed source: working material and accepted Identity."""
    return _digest({
        "working_context": _author_working_context(_user_working_context(store, user)),
        "accepted_story_identity": _accepted_story_design_context(store),
    })


def _design_guidance_fingerprint(store: CanvasStore, request_user: str) -> str:
    """Fingerprint only derived interpretive guidance, excluding accepted Identity."""
    user = json.loads(request_user)
    _, guidance, _ = _design_context_parts(store, _user_working_context(store, user))
    return _digest(guidance)


def _source_fingerprint(store: CanvasStore, request_user: str) -> str:
    """Preserve historical digests while exposing the new author-source fingerprint."""
    user = json.loads(request_user)
    working = _user_working_context(store, user)
    if user.get("freshness_format") == 2:
        return _author_source_fingerprint(store, user)
    if "narrative_design_context" not in user:
        return _digest(working)
    design_context = user["narrative_design_context"]
    current_design = (
        _narrative_design_context(store)
        if "ontology_context" in design_context
        else _legacy_narrative_design_context(store)
    )
    return _digest({
        "working_context": working,
        "narrative_design_context": current_design,
    })


_SYSTEM = """You are Auteur's ABSTRACT NARRATIVE ARCHITECTURE agent, not its authority.
Read narrative_design_context in the user request BEFORE composing an architecture.
Its ontology_context contains the shared definitions and relationship directions
you must use for narrative concepts; those meanings are not author commitments.
Its source-linked design principles are guidance, not invented author choices.
The accepted_story_identity, when present, is authoritative;
the current Story Vision and previous candidate are working material.
Working item content can be just the first 1,000 characters of a longer
scene, and working items/connections can be omitted by context limits.
Use working_source_format, content_is_excerpt, content_characters and
omitted_working_* counts to distinguish visible evidence from missing text.
Working items in group "provisional-concepts" are project-scoped agent proposals,
not shared ontology definitions and not author commitments. Reuse them for this
story provisionally; never present them as accepted general vocabulary.
Working items listed in realization_copy_item_ids were copied by the author from
Story Realization proposals built on an earlier architecture. They are downstream
development, not new architectural direction, unless the revision instruction says so.
creative_intentions are the author's own continuing creative directions. They are
working and noncanonical: active and provisional intentions direct the current
design work, while superseded and withdrawn intentions are history and must not be
treated as current direction. An intention never authorizes accepting canon,
rewriting accepted Identity, or inventing concrete story facts.
A SHA-256 fingerprint identifies source freshness, NOT readable story facts.
For manuscript-first input, cite working item IDs in relevant summaries and
open questions. Separate observed prose from alternative interpretations;
never assert missing passages, motives or outcomes from a truncated excerpt.
If working intent conflicts with accepted Identity, surface the tension as
an unresolved proposal; never silently change the accepted story.

A first architecture must be a COMPLETE abstract proposal built directly from
the Story Vision. Create it without an interview, questionnaire or blocking
author answers. Cover the governing audience emotional
experience and its progression, genre roles and interactions, functional trope
choices, renewable narrative mechanisms and causal organization, abstract
structural progression, and the meaningful relationships among those systems.
Name consequential provisional choices instead of hiding them as certainty.
A revision must reconsider every materially affected emotion, genre, trope
function, engine and structural phase and preserve unrelated author
decisions and accepted constraints. Explain coordinated consequences, not
isolated label changes, and distinguish necessary changes from optional ideas.
Do not invent concrete scenes, chapter numbers or plot events to fill gaps.
If selected_creative_alternative is present, the author chose that noncanonical
alternative from an earlier read-only inquiry about this exact baseline. Develop
it coherently across every materially affected element, keep unrelated author
decisions and accepted constraints, and never present it as accepted canon.
If selected_opportunity is present, the author asked to deepen that incidental
opportunity into a working alternative. Compare it honestly against the governing
architecture: say what would be gained, what would be lost, what remains
uncertain, and whether further investigation is worth the cost. Keep the original
direction available; never present the alternative as accepted canon or as an
automatic replacement.
When the author's instruction is broad but has not delegated replacing their
expressed artistic purpose, keep that purpose as the governing working direction.
If a conflicting direction seems stronger, record it in opportunities with a
relationship of deepens, reinterprets or replaces. Say separately what artistic
potential it has and how faithful it is to the author's expressed intention, and
set requires_author_decision for anything that would replace that purpose. Do not
rank a direction merely because it was expressed first, and never present a
replacement as the governing architecture. Darker events may deepen an optimistic
purpose; that is not the same as a governing goal that negates it.
When the author explicitly delegates discovering the best artistic purpose, you
may select a provisional primary working direction that differs from their
initial sketch. Develop at least two meaningfully different directions, mark one
opportunity provisional_primary, and explain the difference from the sketch, the
alternatives you set aside and what remains uncertain. That is a working
selection only: it never accepts Story Identity and the author can change it.
If collaboration.initiative is focused, deliver the requested work with minimal
unsolicited diversion. If it is exploration_intensive, invite more alternatives
or discussion when genuinely relevant. If collaboration.emphasis is teaching,
explain the craft and tradeoffs behind a discovery; if architecture, relate it to
causal long-horizon consequences; if unconventional, you may challenge stated
assumptions. These are assistance preferences only. None grants canon, none
replaces the delegated objective, and every one of them may still notice an
opportunity.

First honor an accepted engine_hierarchy preference. When it is UNKNOWN, choose
a provisional causal organization supported by the material—a single center,
a primary engine with subordinate layers, or an ensemble of co-governing
mechanisms—and label that organization as an agent proposal. Never manufacture
a dominant engine the material does not support. Make causal ownership,
actor action patterns, pressures, reversals, payoff mechanics, reader experience
and thematic consequences legible, including a deliberate absence of hierarchy
when that is the supported organization. Then project that composition as schema-v2 nodes,
functional links, parent_id hierarchy, genre contracts and phase activations.
A set of plausible disconnected category labels is not an architecture.
Do not invent links merely to satisfy graph connectivity. Explain why each
meaningful mechanism matters and how the parts interact.
Explicitly declared architecture preferences constrain working interpretation;
missing preferences remain UNKNOWN, even when the agent proposes a working
composition. Separate primary emotional promise from supporting palette and
temporal movement; do not replace rich emotion design with a basic-label count.

Generate narrative MECHANISMS, not a fictional cast, setting or plotted storyline.
Never invent names of characters, places, factions, events, plot acts or scenes.
You may refer to concrete proper nouns explicitly supplied by the author, and in a
revision also proper nouns already present in the current working architecture, but
do not elaborate them into fictional content. Generic archetypes may illustrate
a structural function without inventing story facts. Never add new proper nouns.

Use the six chosen basic-emotion labels exactly: joy, sadness, fear, anger,
disgust, surprise. Name concrete intended reader-directed effects and
narrative eliciting conditions, and explain how aesthetic strategies help.
Use complex emotions ONLY when useful; each must cite 2+ distinct basic labels,
with a contextual interpretation, never a scientific/causal guarantee.
Distinguish explicit author declarations from your own working hypotheses. Label an emotion target
author_declared only when its id names an emotion the author's Story Vision or working items state
in their own words (every significant word of the id must appear there). Label every other target
agent_proposed. Its elaboration is never author acceptance, and a label on an unsupported id is rejected.

Build contextual genre contracts with emotional target references, trope
functions, renewable narrative engines, structural patterns and payoff
expectations. Explain typed genre interactions: reinforces, enables,
constrains, contrasts, creates_tension, converges. Only include interactions
that actually explain a mechanism. Propose abstract temporal phases and
genre_activations, including overlaps, genuine pivots and unknown durations.
One architecture may accommodate many different concrete realizations.

Return EXACTLY one JSON candidate with:
schema_version=2, summary, nodes, links, phases, open_questions,
emotion_targets, complex_emotions, genre_contracts, genre_interactions.
node: {id,title,category,summary,scope,parent_id}; category: reader_experience,
aesthetic,genre,trope,engine,thread,structure,theme,other (never character/relationship).
link: {id,source,target,function}; endpoints must exist.
ArchitectureLink.function must contain 1–120 characters and concisely describe
the relation from source to target. Put longer explanatory prose in appropriate
narrative description fields, not in this short relationship label.
emotion_target: {id,emotion,role,intended_effect,eliciting_condition,
aesthetic_strategy,provenance}; emotion one of six basics;
role primary/supporting/contrasting/local; provenance author_declared (author-stated, see above)/agent_proposed.
complex_emotion: {id,title,basic_emotions,context}; 2+ distinct basic labels.
genre_contract: {genre_node_id,role,emotion_target_ids,complex_emotion_ids,
trope_functions,trope_function_refs,narrative_engine,structural_pattern,aesthetic_strategies,
payoff_expectations}; genre_node_id identifies one genre node.
trope_function_refs (optional): [{function_index,trope_node_id}] names the trope node (category
trope) that one entry of trope_functions realises. Only when the trope node clearly is that
conceptual trope; the function text stays local to this genre. Never guess a link by name.
genre_interaction: {id,source_genre_id,target_genre_id,kind,mechanism,risk}.
phase: {id,title,order,scope,genres,genre_activations,reader_experience,
aesthetic,narrative_function,transition,parallel_with}.
genre: {genre,role}; role governing/locally_dominant/supporting/background.
genre_activation: {genre_node_id,basic_emotions,trope_functions,trope_function_refs,structural_function}.
Unknown lengths stay unknown; phase order is NOT a chapter or act number.
Do not fabricate genre commitments when the brief does not establish them.
Keep stable IDs across revisions, preserve unaffected choices, explain uncertainty.
open_question_ids (optional, parallel to open_questions, same length and order): give each open question a
stable id q-<slug>. Keep an existing question's id when it continues, even if you reword it or move it;
mint a new id only for a genuinely new question. Never reuse an id of a question that was removed. Equal or
similar wording does not make two questions the same; say so by keeping or changing ids deliberately.
Resolve story-mechanics questions with coherent, revisable provisional defaults
when the supplied vision supports them. Put those defaults in the architecture
and identify them as agent proposals; do not turn them into required author
questions. Reserve open_questions for genuinely authorial preferences or
commitments that cannot be responsibly inferred. A proposal never waits for
answers before it can be developed or revised.
You may also notice a consequential creative possibility nobody asked about and
that is not a defect in this proposal. Record at most one or two in
opportunities, each with a short reason it might matter. Omit opportunities
entirely when nothing consequential appears: never manufacture novelty, never let
an opportunity replace the requested work, and never treat one as accepted.
When you must invent something the author did not establish in order to make this
architecture work - a world rule, the meaning of one of the author's commitments,
or a proposed resolution of a question the author reserved - record it in
interpretations. State the reading you are using, which nodes it determines, its
major consequences, and any credible alternative. Set author_decision_required
when the choice would materially redirect the series. Make the recommendation
confidently; just do not report your reading as something the author already
established.
All material is a noncanonical proposal; never accept Identity, Structure or prose."""



def _candidate_freshness(store: CanvasStore, current: dict) -> dict:
    """Distinguish governing-source change from guidance change and from downstream writing."""
    request = load_host_agent_request(
        _root(store) / "requests" / current["request_sha256"] / "request.json"
    )
    settings = request.settings
    changed = _changed_dependencies(store, settings, request.user)
    if changed:
        return {"status": "stale", "changed_sources": changed}
    if _guidance_changed(store, settings, request.user, current.get("design_guidance_sha256")):
        return {"status": "guidance_changed"}
    return {"status": "ready", "downstream_changed": _downstream_changed(store, settings)}


def _current_candidate_freshness(store: CanvasStore, current: dict) -> str:
    return _candidate_freshness(store, current)["status"]


def _current_candidate_is_stale(store: CanvasStore, current: dict | None) -> bool:
    """Only author-source drift blocks downstream realization; guidance drift does not."""
    return bool(current) and _current_candidate_freshness(store, current) == "stale"


def project_architecture(store: CanvasStore) -> dict:
    store.load()
    pointer = _read(_root(store) / "latest_request.json")
    current = _candidate(store)
    req = None
    if pointer:
        sha = pointer.get("request_sha256", "")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError("invalid architecture request pointer")
        req = load_host_agent_request(_root(store) / "requests" / sha / "request.json")
    pending = bool(req and (not current or current["request_sha256"] != req.request_sha256))
    review = _read(_root(store) / "requests" / req.request_sha256 / "review.json") if pending else None
    freshness = {}
    if review:
        status = "review_ready"
    elif pending:
        status = "awaiting_host_agent"
    elif current:
        freshness = _candidate_freshness(store, current)
        status = freshness["status"]
    else:
        status = "not_started"
    return {
        "status": status,
        # Which governing dependency made the candidate stale, and whether downstream writing changed since.
        "changed_sources": freshness.get("changed_sources", []),
        "downstream_changed": freshness.get("downstream_changed", False),
        "request": req.model_dump() if pending and not review else None,
        "candidate": current["candidate"] if current else None,
        "candidate_request_sha256": current["request_sha256"] if current else None,
        "review": _review_with_book_evidence(store, review),
        "governing_objective": (current or {}).get("governing_objective"),
        "premise_status": (current or {}).get("premise_status"),
        "collaboration": (
            review.get("collaboration")
            if review and review.get("collaboration")
            else (current or {}).get("collaboration")
        ),
        "opportunities": opportunities_projection(
            current["candidate"] if current else None,
        ),
        "working_interpretations": interpretations_projection(
            current["candidate"] if current else None,
        ),
        "author_emotion_grounding": (current or {}).get("author_emotion_grounding"),
        "question_changes": (review or {}).get("question_changes") if review else (
            (_read(_root(store) / "requests" / current["request_sha256"] / "review.json") or {}).get("question_changes")
            if current else None
        ),
    }


def interpretations_projection(candidate: dict | None) -> dict:
    """Surface consequential working interpretations as recommendations, not facts."""
    items = list((candidate or {}).get("interpretations") or [])
    return {
        "authority": "agent_interpretation",
        "count": len(items),
        "items": items,
        "requires_author_decision": [
            item.get("id") for item in items if item.get("author_decision_required")
        ],
        "note": (
            "Consequential readings the agent is using while proposing this "
            "architecture. They are recommendations, not author-established "
            "commitments, and none becomes canon without the existing acceptance path."
        ),
    }


def opportunities_projection(candidate: dict | None) -> dict:
    """Surface incidental creative possibilities without granting them authority."""
    items = list((candidate or {}).get("opportunities") or [])
    alternatives = [
        {
            "id": item.get("id"),
            "relationship": item.get("relationship") or "unclear",
            "requires_author_decision": bool(item.get("requires_author_decision")),
            "provisional_primary": bool(item.get("provisional_primary")),
        }
        for item in items
    ]
    provisional = next(
        (item["id"] for item in alternatives if item["provisional_primary"]), None,
    )
    return {
        "authority": "noncanonical_opportunity",
        "count": len(items),
        "items": items,
        "comparison": {
            "governing_purpose_authority": "author_expressed",
            "alternative_count": len(alternatives),
            "alternatives": alternatives,
            "requires_author_decision": [
                item["id"] for item in alternatives if item["requires_author_decision"]
            ],
            "provisional_primary": provisional,
            "working_selection_is_not_acceptance": True,
            "note": (
                "Artistic potential and intention fidelity are separate claims. An "
                "alternative is not better because it is more developed, and the "
                "expressed direction is not superior because it came first. Any "
                "alternative that would replace the author's purpose requires an "
                "explicit author decision. A provisional primary direction is a "
                "working selection under delegated goal discovery, never accepted "
                "Story Identity."
            ),
        },
        "note": (
            "Incidental creative possibilities the agent noticed while doing the "
            "requested work. They are not defects, not required author decisions, "
            "and not accepted narrative meaning. Ignoring them is a complete "
            "response."
        ),
    }


_ACCEPTED_COMMITMENT_KEYS = (
    "central_engine", "target_experience", "story_type",
    "architecture_preferences", "hard_constraints", "not_this",
)


def governing_objective(user: dict) -> dict:
    """Name the author's expressed objective for this working proposal.

    Derived only from author-visible source already sent to the host agent. It is
    never accepted Story Identity, and reporting it here never makes it canon.
    """
    working = user.get("working_context") or {}
    vision = working.get("vision")
    instruction = user.get("revision_instruction") or ""
    return {
        "authority": "author_expressed",
        "story_vision": vision if isinstance(vision, str) and vision.strip() else None,
        "instruction": (
            instruction if isinstance(instruction, str) and instruction.strip() else None
        ),
        "note": (
            "The author's expressed creative objective for this working proposal. "
            "It is not accepted Story Identity, and the candidate summary is an "
            "interpretation of it rather than the objective itself."
        ),
    }


def premise_status(candidate: dict, accepted_identity: dict | None = None) -> dict:
    """Classify what kind of claim each part of the working proposal is.

    The four buckets are the ones an author must be able to tell apart. Every
    node, link and the summary stay noncanonical working material no matter how
    thoroughly the agent developed them.
    """
    author_targets = sorted(
        str(target.get("id")) for target in candidate.get("emotion_targets", [])
        if target.get("provenance") == "author_declared"
    )
    commitments: dict = {}
    if isinstance(accepted_identity, dict):
        for key in _ACCEPTED_COMMITMENT_KEYS:
            value = accepted_identity.get(key)
            if value not in (None, [], {}):
                commitments[key] = value
    return {
        "authority": "working_architecture_not_canon",
        "author_expressed": {
            "source": "story_vision_and_author_named_emotion_targets",
            "emotion_targets": author_targets,
            "note": (
                "A source-origin claim only: the author's own text names this "
                "emotion. It is not acceptance of the agent's elaboration."
            ),
        },
        "accepted": {
            "source": "accepted_story_identity" if commitments else None,
            "commitments": commitments,
        },
        "provisional_agent_interpretation": {
            "summary": True,
            "nodes": sorted(str(node.get("id")) for node in candidate.get("nodes", [])),
            "links": sorted(str(link.get("id")) for link in candidate.get("links", [])),
            "note": (
                "Every node, link and the summary are noncanonical working "
                "material proposed by the agent."
            ),
        },
        "unresolved": {
            "open_questions": list(candidate.get("open_questions", [])),
        },
    }


def _provisional_concepts(store: CanvasStore) -> list[dict]:
    return [
        concept.model_dump(mode="json")
        for concept in list_provisional_concepts(store)
    ]


def _resume_ontology_guidance(
    store: CanvasStore, request_sha256: str | None, vision: str,
    accepted_identity: dict | None,
) -> dict:
    if request_sha256:
        request = load_host_agent_request(
            _root(store) / "requests" / request_sha256 / "request.json"
        )
        captured = json.loads(request.user).get(
            "narrative_design_context", {},
        ).get("ontology_context")
        if captured:
            return {**captured, "origin": "request", "request_sha256": request_sha256}
        current = build_relevant_ontology_context(vision, accepted_identity)
        return {
            **current,
            "origin": "current_derived_not_original_request",
            "request_sha256": request_sha256,
        }
    current = build_relevant_ontology_context(vision, accepted_identity)
    return {**current, "origin": "current_derived", "request_sha256": None}


def _review_with_book_evidence(store: CanvasStore, review: dict | None) -> dict | None:
    """A pending review, with its selected alternative's Book evidence read again now (presentation only)."""
    selected = (review or {}).get("selected_creative_alternative") or {}
    if not selected.get("book_evidence"):
        return review
    return {**review, "selected_creative_alternative": {
        **selected, "book_evidence": {**selected["book_evidence"],
                                      "status_now": _inquiry_book_evidence_status(store, selected)}}}


def _inquiry_book_evidence_status(store: CanvasStore, selected: dict) -> str:
    """Whether a selected alternative's Book evidence is still the Book's current record, read now."""
    from .studio_architecture_inquiry import _book_evidence_status
    try:
        request = load_host_agent_request(
            _root(store) / "inquiries" / "requests" / selected["inquiry_request_sha256"] / "request.json")
    except (OSError, ValueError, KeyError):
        return "unreadable"
    return _book_evidence_status(store, request.settings)


def _adoption_lineage(store: CanvasStore, current: dict | None) -> list[dict]:
    """Every alternative an author adopted along the current revision chain, newest first.

    Each applied revision records its prior request SHA, so the decisions that produced the current
    working architecture are recoverable without a second store. A later unrelated revision therefore
    does not erase the visibility of an earlier adopted direction.
    """
    if not current:
        return []
    rows: list[dict] = []
    sha = current.get("request_sha256")
    seen: set[str] = set()
    for _ in range(40):
        if not isinstance(sha, str) or sha in seen:
            break
        seen.add(sha)
        folder = _root(store) / "requests" / sha
        try:
            request = load_host_agent_request(folder / "request.json")
        except (FileNotFoundError, ValueError):
            break
        submitted = json.loads(request.user).get("selected_creative_alternative")
        if submitted:
            row = {"adopted_in_request_sha256": sha, **submitted}
            if submitted.get("book_evidence"):
                row["book_evidence"] = {**submitted["book_evidence"],
                                        "status_now": _inquiry_book_evidence_status(store, submitted)}
            rows.append(row)
        review = _read(folder / "review.json")
        if not review or not review.get("prior_request_sha256"):
            break
        sha = review["prior_request_sha256"]
    return rows


def architecture_revision_chain(store: CanvasStore, limit: int = 200) -> dict:
    """Read-only: the applied working Architecture requests, newest first, and whether the chain is whole.

    Each applied revision's review names the request it revised. ``complete`` is True only when the walk
    reached the first version (one with no recorded prior); a review that cannot be read, a loop or the
    limit leaves it False, so a caller can say "cannot be told" instead of "not on the chain".
    """
    current = _candidate(store)
    if not current:
        return {"requests": [], "complete": False}
    sha, chain = current["request_sha256"], [current["request_sha256"]]
    for _ in range(limit):
        try:
            review = _read(_root(store) / "requests" / sha / "review.json")
        except (OSError, ValueError):
            return {"requests": chain, "complete": False}
        prior = (review or {}).get("prior_request_sha256")
        if prior is None:
            # Only the first version has no review naming a prior; an applied revision always has one, so a
            # missing review on a revision leaves the chain incomplete rather than ending it.
            return {"requests": chain, "complete": review is None and _is_first_version(store, sha)}
        if not isinstance(prior, str) or prior in chain:
            return {"requests": chain, "complete": False}
        chain.append(prior)
        sha = prior
    return {"requests": chain, "complete": False}


def _is_first_version(store: CanvasStore, sha: str) -> bool:
    """A version developed from no earlier one: its request carries no revision instruction."""
    try:
        request = load_host_agent_request(_root(store) / "requests" / sha / "request.json")
        return not str(json.loads(request.user).get("revision_instruction") or "").strip()
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def _stored_shape(candidate: dict) -> dict:
    """The candidate as it is stored. A version without identities carries no identity key at all, exactly as
    before identities existed: the digest a Working Book binds to depends on this shape, so every reader that
    rebuilds a version from its response must normalise it the same way the writer does."""
    if candidate.get("open_question_ids") is None:
        candidate.pop("open_question_ids", None)
    return candidate


def _version_candidate(store: CanvasStore, sha: str) -> dict | None:
    """One applied version's candidate: from its review, or for the first version its stored response,
    validated the way it was when it was completed. None when it cannot be read."""
    folder = _root(store) / "requests" / sha
    try:
        review = _read(folder / "review.json")
        if review and isinstance(review.get("candidate"), dict):
            return review["candidate"]
        response = _read(folder / "response.json")
        return _stored_shape(ArchitectureCandidate.model_validate_json(
            response["text"], context={"new_host_agent_response": True}).model_dump(mode="json"))
    except (OSError, TypeError, KeyError, ValueError):
        return None


def architecture_versions(store: CanvasStore, limit: int = 200, requests: list[str] | None = None):
    """Read-only: ``(request_sha256, candidate)`` along the applied revision chain, newest first.

    ``candidate`` is None for a version whose record cannot be read; the walk still continues by identity.
    ``requests`` is a chain the caller already read with ``architecture_revision_chain``.
    """
    current = _candidate(store)
    if not current:
        return
    chain = requests if requests is not None else architecture_revision_chain(store, limit)["requests"]
    for index, sha in enumerate(chain):
        yield sha, current["candidate"] if index == 0 else _version_candidate(store, sha)


def project_architecture_resume(store: CanvasStore) -> dict:
    """Read-only packet a fresh coding agent can use without chat history."""
    canvas = store.load()
    projection = project_architecture(store)
    current = _candidate(store)
    vision = next(
        (item.content for item in canvas.items if item.id == "story-vision"), "",
    )
    working = _source(
        store,
        previous=current["candidate"] if current else None,
        source_format=2,
    )
    accepted = _accepted_story_design_context(store)
    source_visibility = {
        "working_item_count": len(working["working_items"]),
        "omitted_working_item_count": working.get("omitted_working_item_count", 0),
        "omitted_working_connection_count": working.get(
            "omitted_working_connection_count", 0,
        ),
        "truncated_items": [
            {
                "id": item["id"],
                "content_characters": item.get("content_characters"),
                "content_is_excerpt": item.get("content_is_excerpt", False),
                "full_content_sha256": item.get("full_content_sha256"),
            }
            for item in working["working_items"] if item.get("content_is_excerpt")
        ],
        "provisional_concept_item_count": working.get(
            "provisional_concept_item_count", 0,
        ),
        "omitted_provisional_concept_item_count": working.get(
            "omitted_provisional_concept_item_count", 0,
        ),
        "vision_characters": len(working["vision"]),
    }
    for key in ("omitted_working_items_sha256", "omitted_working_connections_sha256"):
        if key in working:
            source_visibility[key] = working[key]
    guidance_sha = (
        current["request_sha256"] if current
        else projection["review"]["request_sha256"] if projection["review"]
        else projection["request"]["request_sha256"] if projection["request"]
        else None
    )
    pending_sha = (
        projection["review"]["request_sha256"] if projection["review"]
        else projection["request"]["request_sha256"] if projection["request"]
        else None
    )
    candidate = projection["candidate"]
    # Local imports avoid a circular module import: these owners import this module.
    from .studio_architecture_inquiry import project_architecture_inquiry
    from .studio_mentor import project_mentor

    inquiry = project_architecture_inquiry(store)
    mentor = project_mentor(store)
    creative_deliberation = {
        "authority": "noncanonical_working_deliberation",
        "inquiry_history": inquiry.get("history", []),
        "superseded_inquiry_history": inquiry.get("superseded_history", []),
        "mentor_advice": (
            {
                "focus_id": mentor["focus_id"],
                "focus_kind": mentor["focus_kind"],
                "author_reply": mentor.get("author_reply", ""),
                "advice": mentor["advice"],
            }
            if mentor.get("status") == "ready" else None
        ),
        # While a follow-up is pending, the completed advice it replies to is carried only in that request.
        "mentor_prior_advice": (
            json.loads(mentor["request"]["user"]).get("prior_exchange")
            if mentor.get("status") == "awaiting_host_agent" and mentor.get("request") else None
        ),
    }
    adoption_lineage = _adoption_lineage(store, current)
    retained = opportunities_projection(candidate)
    # A saved idea is not current merely because it was saved.
    withheld = projection["status"] in {"stale", "guidance_changed"}
    working_opportunities = {
        "authority": "noncanonical_opportunity",
        "freshness": projection["status"],
        "withheld": withheld,
        "items": [] if withheld else retained["items"],
        "retained_item_count": retained["count"],
        "comparison": retained["comparison"],
        "note": (
            "Ideas retained from earlier working proposals. They are not accepted "
            "narrative meaning, they are distinguishable from accepted Story "
            "Identity and current commitments, and they are not promoted because "
            "they were saved. When the author's source or guidance changed they are "
            "withheld rather than presented as current."
        ),
    }
    return {
        "kind": "studio_architecture_resume",
        "authority": "working_noncanonical",
        "canvas_id": store.canvas_id,
        "canvas_revision": canvas.revision,
        "story_vision": vision,
        "architecture": candidate,
        "architecture_status": projection["status"],
        "candidate_request_sha256": projection["candidate_request_sha256"],
        # T01's distinction must survive a fresh session, not only the live projection.
        "governing_objective": projection.get("governing_objective"),
        "premise_status": projection.get("premise_status"),
        "collaboration": projection.get("collaboration"),
        "working_interpretations": projection.get("working_interpretations"),
        "working_opportunities": working_opportunities,
        "pending_request_sha256": pending_sha,
        "pending_review": projection["review"],
        "open_questions": candidate.get("open_questions", []) if candidate else [],
        "ontology_guidance": _resume_ontology_guidance(
            store, guidance_sha, vision, accepted,
        ),
        "accepted_story_identity": accepted,
        "source_visibility": source_visibility,
        "provisional_concepts": _provisional_concepts(store),
        "creative_deliberation": creative_deliberation,
        # Most recent adoption along the current revision chain; earlier ones remain in the lineage.
        "adopted_creative_alternative": adoption_lineage[0] if adoption_lineage else None,
        "creative_adoption_lineage": adoption_lineage,
        "creative_intentions": _creative_intentions(store),
    }


def _selected_alternative_context(store: CanvasStore, current: dict, selection: SelectedCreativeAlternative) -> dict:
    """Resolve an author-chosen inquiry alternative against the exact current baseline; never by title."""
    inquiry = _read(
        _root(store) / "inquiries" / "requests" / selection.inquiry_request_sha256 / "result.json"
    )
    if inquiry is None:
        raise ValueError("selected inquiry not found")
    if inquiry.get("baseline_candidate_request_sha256") != current["request_sha256"]:
        raise BeginnerConcurrencyError("selected inquiry belongs to a superseded architecture baseline")
    alternatives = [
        {"id": row.get("id") or f"h{index}", "title": row["title"], "description": row["description"],
         "divergence_axis": row.get("divergence_axis")}
        for index, row in enumerate(inquiry.get("hypotheses") or [], start=1)
    ]
    match = next((row for row in alternatives if row["id"] == selection.hypothesis_id), None)
    if match is None:
        raise ValueError("selected alternative not found in the selected inquiry")
    intent = inquiry.get("intent") or {}
    book_evidence = None
    if inquiry.get("book_evidence"):
        from .studio_architecture_inquiry import _book_evidence_status
        request = load_host_agent_request(
            _root(store) / "inquiries" / "requests" / selection.inquiry_request_sha256 / "request.json")
        status = _book_evidence_status(store, request.settings)
        book_evidence = {
            **inquiry["book_evidence"],
            "status_at_revision": status,
            "status_note": ("The working Book element as the inquiry read it; it was still the Book's current "
                            "record when this revision was prepared." if status == "current" else
                            "Historical: the working Book or this element had changed or could not be read when this "
                            "revision was prepared; this is the evidence as the inquiry read it, not the Book's record."),
        }
    return {
        **({"book_evidence": book_evidence} if book_evidence else {}),
        "inquiry_request_sha256": selection.inquiry_request_sha256,
        "hypothesis_id": match["id"],
        "title": match["title"],
        "description": match["description"],
        "divergence_axis": match["divergence_axis"],
        "operation": intent.get("operation"),
        "author_question": intent.get("author_text", ""),
        "authority": "noncanonical_creative_alternative",
    }


_SELECTED_BOOK_EVIDENCE_GUIDANCE = (
    "selected_creative_alternative.book_evidence is the working Book element the inquiry was asked with. It is a "
    "noncanonical Book-level working proposal, not an author-declared Architecture fact, an author intention or an "
    "accepted commitment, and it is historical when status_at_revision is not current. Revise the Architecture as "
    "the instruction asks; do not write the Book's element into the Architecture as fact."
)

INITIATIVE_POSTURES = ("focused", "balanced", "exploration_intensive")
INTELLECTUAL_EMPHASES = ("teaching", "architecture", "unconventional")


def _collaboration(initiative: str | None, emphasis: str | None) -> dict | None:
    """Per-request assistance preferences. They are never persisted authority."""
    if initiative is not None and initiative not in INITIATIVE_POSTURES:
        raise ValueError(
            "initiative must be focused, balanced or exploration_intensive"
        )
    if emphasis is not None and emphasis not in INTELLECTUAL_EMPHASES:
        raise ValueError(
            "emphasis must be teaching, architecture or unconventional"
        )
    if initiative is None and emphasis is None:
        return None
    return {"initiative": initiative, "emphasis": emphasis}


def prepare_architecture(
    store: CanvasStore, instruction: str = "", graph_intent: dict | None = None,
    selected_alternative: dict | None = None,
    selected_opportunity: dict | None = None,
    initiative: str | None = None,
    emphasis: str | None = None,
) -> dict:
    if not isinstance(instruction, str) or len(instruction) > 4000:
        raise ValueError("revision instruction must be text under 4000 characters")
    collaboration = _collaboration(initiative, emphasis)
    with _FilesystemLock(store._path(".canvas.lock")):
        current = _candidate(store)
        selected_context = None
        if selected_alternative is not None:
            if not instruction.strip():
                raise ValueError("a selected alternative requires a revision instruction")
            selection = SelectedCreativeAlternative.model_validate(selected_alternative)
            if not current or _current_candidate_freshness(store, current) != "ready":
                raise BeginnerConcurrencyError("selected alternative source or guidance is stale")
            selected_context = _selected_alternative_context(store, current, selection)
        opportunity_context = None
        if selected_opportunity is not None:
            if not instruction.strip():
                raise ValueError("a selected opportunity requires a revision instruction")
            choice = SelectedOpportunity.model_validate(selected_opportunity)
            if not current or _current_candidate_freshness(store, current) != "ready":
                raise BeginnerConcurrencyError("selected opportunity source or guidance is stale")
            if current["request_sha256"] != choice.candidate_request_sha256:
                raise BeginnerConcurrencyError(
                    "selected opportunity belongs to a superseded working candidate"
                )
            match = next(
                (
                    item for item in current["candidate"].get("opportunities", [])
                    if item.get("id") == choice.opportunity_id
                ),
                None,
            )
            if match is None:
                raise ValueError("selected opportunity is not present on the current candidate")
            opportunity_context = {
                "authority": "noncanonical_opportunity",
                "source": "current_working_candidate",
                "candidate_request_sha256": current["request_sha256"],
                "opportunity": match,
                "note": (
                    "The author asked to deepen this incidental opportunity as a "
                    "working alternative. It remains noncanonical and the governing "
                    "architecture stays available for continuation."
                ),
            }
        resolved_graph_intent = None
        if graph_intent is not None:
            typed_intent = GraphIntent.model_validate(graph_intent)
            if typed_intent.operation != "revise":
                raise ValueError("only an explicit Revise action may prepare a working architecture")
            if typed_intent.target != "current":
                raise ValueError("a revision must target the current working architecture")
            if typed_intent.canvas_id != store.canvas_id:
                raise ValueError("graph intent belongs to another canvas")
            if typed_intent.author_text != instruction:
                raise ValueError("graph intent author text must exactly match the revision instruction")
            if not current or _current_candidate_freshness(store, current) != "ready":
                raise BeginnerConcurrencyError("graph-selected architecture source or guidance is stale")
            active_pointer = _read(_root(store) / "latest_request.json")
            if active_pointer and active_pointer.get("request_sha256") != current["request_sha256"]:
                raise BeginnerConcurrencyError("an outstanding architecture request supersedes this graph context")
            evidence = (selected_context or {}).get("book_evidence")
            if evidence:
                recorded = {c["node_id"] for c in evidence.get("cited_architecture_concepts", []) if c.get("present")}
                stray = [a.id for a in typed_intent.anchors if a.kind != "node" or a.id not in recorded]
                if stray:
                    book = (evidence.get("book") or {}).get("book_number")
                    raise ValueError(
                        f"this alternative was asked with Book {book}'s element, which records "
                        f"{', '.join(sorted(recorded)) or 'no current concept'}; anchor the revision on a concept it "
                        "records (not " + ", ".join(stray) + ")")
            resolved_graph_intent = resolve_graph_intent(
                current["candidate"], current["request_sha256"], typed_intent,
            )
        if instruction.strip() and not current:
            raise ValueError("nothing to revise; develop an initial architecture first")
        previous = current["candidate"] if instruction.strip() and current else None
        context = _source(store, previous=previous)
        if not context["vision"].strip() and not context["working_items"]:
            raise ValueError("write a Story Vision or a working idea first")
        _, guidance, design_context = _design_context_parts(store, context)
        settings = {
            "canvas_id": store.canvas_id,
            **_dependency_settings(store),
            "design_guidance_sha256": _digest(guidance),
            "intention_sha256": _intention_fingerprint(store),
            "operation": "revise" if instruction.strip() else "develop",
        }
        copied = [
            item.id for item in store.load().items
            if item.proposal_origin is not None and item.proposal_origin.source_kind == _REALIZATION_COPY_KIND
        ]
        user = json.dumps({
            "freshness_format": 3,
            **({"realization_copy_item_ids": copied} if copied else {}),
            "working_context": context,
            "narrative_design_context": design_context,
            "revision_instruction": instruction,
            **({"graph_intent": resolved_graph_intent} if resolved_graph_intent else {}),
            **({"selected_creative_alternative": selected_context} if selected_context else {}),
            **({"selected_opportunity": opportunity_context} if opportunity_context else {}),
            **({"collaboration": collaboration} if collaboration else {}),
        }, ensure_ascii=False, sort_keys=True)
        request = build_host_agent_request(
            candidate_id="studio-" + _digest({"settings": settings, "user": user})[:24],
            role="studio_architecture", user=user, settings=settings,
            system=_SYSTEM + ("\n" + _SELECTED_BOOK_EVIDENCE_GUIDANCE
                              if selected_context and selected_context.get("book_evidence") else ""),
            output_contract=model_output_contract(ArchitectureCandidate),
        )
        base = _root(store)
        write_host_agent_request(base / "requests" / request.request_sha256 / "request.json", request)
        _atomic_json_write(base / "latest_request.json",
                           {"request_sha256": request.request_sha256})
    return project_architecture(store)


_AUTHOR_TERM_STOPWORDS = frozenset({
    "the", "and", "for", "with", "that", "this", "from", "into", "over", "its", "are", "was", "but",
})


def _author_visible_words(packet: dict) -> set[str]:
    """Words of the author-supplied text this request actually showed the writer.

    Agent-proposed provisional notes, the previous candidate and the revision instruction are excluded:
    none of them is author-supplied material the writer can be shown to have been given.
    """
    context = packet["working_context"]
    texts = [str(context.get("vision") or "")]
    texts.extend(
        str(item.get("content") or "")
        for item in context.get("working_items", [])
        if item.get("group") != _PROVISIONAL_CONCEPT_GROUP
    )
    return {word for text in texts for word in re.findall(r"[a-z]+", text.lower())}


def _author_term_grounded(identifier: str, words: set[str]) -> bool:
    """Every significant term of the emotion identifier must appear in the author-visible text."""
    terms = [
        part for part in re.split(r"[^a-z]+", identifier.lower())
        if len(part) >= 3 and part not in _AUTHOR_TERM_STOPWORDS
    ]
    return bool(terms) and all(term in words for term in terms)


def _validate_author_provenance(proposal: ArchitectureCandidate, packet: dict) -> None:
    """Admit `author_declared` only where author text names the emotion, or the baseline already did.

    An unchanged or already-declared baseline claim is preserved without re-proof; the review reports
    any change to it. A new or promoted author claim must be named by author-visible text. The check
    is lexical and deterministic: it establishes that the author's own words name the emotion, not that
    the author accepted the agent's elaboration of it.
    """
    previous = packet["working_context"].get("previous_candidate") or {}
    baseline_claims = {
        target.get("id") for target in previous.get("emotion_targets", [])
        if target.get("provenance") == "author_declared"
    }
    words = _author_visible_words(packet)
    for target in proposal.emotion_targets:
        if target.provenance != "author_declared" or target.id in baseline_claims:
            continue
        if not _author_term_grounded(target.id, words):
            raise ValueError(
                f"author_declared emotion target {target.id!r} is not named in the author's source "
                "text shown in this request; label an agent interpretation agent_proposed"
            )


def _author_emotion_grounding(
    proposal: ArchitectureCandidate, packet: dict,
) -> list[dict]:
    """Distinguish an author-named emotion from an author-described experience.

    `author_declared` means the author's words name the experience the target
    stands for. It does not mean the author named the basic-emotion label: an
    author who writes "earned trust" described an experience, and joy is the
    agent's classification of it.
    """
    words = _author_visible_words(packet)
    rows = []
    for target in proposal.emotion_targets:
        if target.provenance != "author_declared":
            continue
        rows.append({
            "id": target.id,
            "emotion": target.emotion,
            "experience_named_by_author": _author_term_grounded(target.id, words),
            "emotion_named_by_author": _author_term_grounded(target.emotion, words),
        })
    return rows


def complete_architecture(store: CanvasStore, payload: dict) -> dict:
    with _FilesystemLock(store._path(".canvas.lock")):
        pointer = _read(_root(store) / "latest_request.json")
        if not pointer:
            raise ValueError("no Studio architecture request exists")
        sha = pointer["request_sha256"]
        base = _root(store) / "requests" / sha
        request = load_host_agent_request(base / "request.json")
        response = validate_host_agent_response(request, payload)
        current = _candidate(store)
        prior_response = _read(base / "response.json")
        if prior_response:
            if prior_response != response.model_dump():
                raise BeginnerConcurrencyError("a different response already completed this request")
            return project_architecture(store)
        proposal = ArchitectureCandidate.model_validate_json(
            response.text, context={"new_host_agent_response": True}
        )
        submitted = json.loads(request.user)
        instruction = submitted["revision_instruction"]
        settings = request.settings
        author_changed = _changed_dependencies(store, settings, request.user)
        if author_changed:
            write_host_agent_response(base / "stale_response.json", response)
            raise BeginnerConcurrencyError(
                _stale_message(author_changed) if settings.get("freshness_format") == 3 else
                "the author's source vision or working story changed; response retained as stale evidence"
            )
        if _guidance_changed(store, settings, request.user):
            write_host_agent_response(base / "stale_response.json", response)
            raise BeginnerConcurrencyError(
                "the narrative design guidance changed; response retained as stale evidence"
            )
        if settings.get("intention_sha256") and _intention_fingerprint(store) != settings["intention_sha256"]:
            write_host_agent_response(base / "stale_response.json", response)
            raise BeginnerConcurrencyError(
                "the author's creative intentions changed; response retained as stale evidence"
            )
        _validate_author_provenance(proposal, submitted)
        identity_check = proposal.model_dump(mode="json")
        chain = architecture_revision_chain(store)
        identity_history = [version for _sha, version in architecture_versions(store, requests=chain["requests"])]
        if current is not None and not chain["complete"]:
            # An unreadable or unfinished history cannot rule out a retired identity, so new identities are refused.
            # With no earlier Architecture there is no history to rule out.
            identity_history.append(None)
        identity_issues = question_identity_problems(
            identity_check, current["candidate"] if current else None, identity_history,
        )
        if identity_issues:
            raise ValueError("open question identities: " + "; ".join(identity_issues))
        write_host_agent_response(base / "response.json", response)
        candidate = _stored_shape(proposal.model_dump(mode="json"))
        accepted_identity = (submitted.get("narrative_design_context") or {}).get(
            "accepted_story_identity"
        )
        record = {
            "request_sha256": sha,
            "source_sha256": settings["source_sha256"],
            "candidate": candidate,
            "governing_objective": governing_objective(submitted),
            "premise_status": premise_status(candidate, accepted_identity),
            "working_interpretations": interpretations_projection(candidate),
            "author_emotion_grounding": _author_emotion_grounding(proposal, submitted),
            "question_changes": question_changes(current["candidate"] if current else None, candidate),
        }
        if submitted.get("collaboration"):
            record["collaboration"] = submitted["collaboration"]
        if settings.get("freshness_format") in (2, 3):
            record["design_guidance_sha256"] = settings["design_guidance_sha256"]
        if instruction.strip():
            record.update(build_architecture_review(
                current["candidate"], candidate, instruction,
                accepted_identity=accepted_identity,
            ))
            record["prior_request_sha256"] = current["request_sha256"]
            if submitted.get("graph_intent"):
                record["graph_intent_receipt"] = submitted["graph_intent"]
            if submitted.get("selected_creative_alternative"):
                record["selected_creative_alternative"] = submitted["selected_creative_alternative"]
            if submitted.get("selected_opportunity"):
                record["selected_opportunity"] = submitted["selected_opportunity"]
            _atomic_json_write(base / "review.json", record)
        else:
            _atomic_json_write(_root(store) / "current.json", record)
    return project_architecture(store)


def apply_architecture_review(store: CanvasStore, request_sha256: str) -> dict:
    """Apply a reviewed *working* revision; accepted story owners are untouched."""
    if not isinstance(request_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", request_sha256):
        raise ValueError("valid request_sha256 is required")
    with _FilesystemLock(store._path(".canvas.lock")):
        pointer = _read(_root(store) / "latest_request.json")
        if not pointer or pointer["request_sha256"] != request_sha256:
            raise BeginnerConcurrencyError("a newer architecture request superseded this review")
        current = _candidate(store)
        if current and current["request_sha256"] != request_sha256:
            review = _read(_root(store) / "requests" / request_sha256 / "review.json")
            if not review:
                raise ValueError("architecture revision has not been completed")
            if current["request_sha256"] != review["prior_request_sha256"]:
                raise BeginnerConcurrencyError("the baseline architecture changed; review again")
            request = load_host_agent_request(
                _root(store) / "requests" / request_sha256 / "request.json"
            )
            settings = request.settings
            changed = bool(
                _changed_dependencies(store, settings, request.user)
                or _guidance_changed(store, settings, request.user)
                or (
                    settings.get("freshness_format") in (2, 3) and settings.get("intention_sha256")
                    and _intention_fingerprint(store) != settings["intention_sha256"]
                )
            )
            if changed:
                named = _changed_dependencies(store, settings, request.user)
                raise BeginnerConcurrencyError(
                    "working context changed: " + _stale_message(named).replace(
                        "; response retained as stale evidence", "; review again")
                    if settings.get("freshness_format") == 3 and named else
                    "working context changed: story vision, intentions or design context changed; review again"
                )
            record = {
                "request_sha256": request_sha256,
                "source_sha256": review["source_sha256"],
                "candidate": review["candidate"],
            }
            if "design_guidance_sha256" in review:
                record["design_guidance_sha256"] = review["design_guidance_sha256"]
            _atomic_json_write(_root(store) / "current.json", record)
        elif not current:
            raise ValueError("there is no current working architecture to revise")
    return project_architecture(store)


def _free_position(canvas) -> dict:
    taken = {(round(point.x), round(point.y)) for point in canvas.positions.values()}
    for row in range(6):
        for column in range(5):
            slot = (40 + column * 260, 40 + row * 170)
            if slot not in taken:
                return {"x": slot[0], "y": slot[1]}
    return {"x": 40, "y": 40}


def _apply_review_cli(store: CanvasStore, request_sha256: str) -> dict:
    """Bridge wrapper for apply_architecture_review: explicit identity, one machine-readable outcome.

    The existing apply function keeps every protection (latest-request pointer, completed review,
    baseline identity, freshness of vision, intentions and design context, and the lock). This wrapper
    only checks the identity is well formed and names an existing request, reports whether the
    candidate was already applied, and turns refusals into a structured result. It writes working
    state only, through the apply function. It never accepts canon and never selects a request.
    """
    refused = {"result": "rejected", "request_sha256": request_sha256, "authority": "working_only"}
    if not isinstance(request_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", request_sha256):
        return {"application": {**refused, "error": "request_sha256 must be a 64-character lowercase SHA-256"}}
    if not (_root(store) / "requests" / request_sha256 / "request.json").exists():
        return {"application": {**refused, "error": "no architecture request has this identity in this canvas"}}
    already = (_candidate(store) or {}).get("request_sha256") == request_sha256
    try:
        projection = apply_architecture_review(store, request_sha256)
    except (BeginnerConcurrencyError, ValueError) as exc:
        return {"application": {**refused, "error": str(exc)}}
    result = "already_applied" if already else "applied"
    return {**projection, "application": {
        "result": result, "request_sha256": request_sha256, "authority": "working_only",
    }}


def main(argv: list[str] | None = None) -> int:
    """Portable operator bridge: the active coding agent supplies raw candidate JSON."""
    parser = argparse.ArgumentParser(description="Auteur Studio host-agent architecture bridge")
    parser.add_argument("--project", required=True, help="Local Auteur project root")
    parser.add_argument("--canvas", required=True, help="Canvas id from Studio URL")
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("show", help="Show current proposal or exact host-agent request")
    actions.add_parser(
        "resume", help="Emit a read-only working re-entry packet for a new coding agent",
    )
    prepare = actions.add_parser("prepare", help="Prepare a new architecture request")
    prepare.add_argument("--instruction", default="", help="Optional revision request")
    submit = actions.add_parser("complete-file", help="Validate candidate JSON written by host agent")
    submit.add_argument("--candidate", required=True, help="Path to raw candidate JSON file")
    record = actions.add_parser(
        "record-concept", help="Record a provisional project-level narrative concept",
    )
    record.add_argument(
        "--concept", required=True, help="Path to ProvisionalNarrativeConcept JSON",
    )
    record.add_argument("--command-id", default=None, help="Optional idempotency id")
    keep = actions.add_parser(
        "keep-intention", help="Record an author-directed continuing creative intention",
    )
    keep.add_argument("--id", default=None, help="Stable intention id; derived when omitted")
    keep.add_argument("--title", required=True)
    keep.add_argument("--directive-file", required=True, help="Author-written directive text")
    keep.add_argument("--status", choices=("provisional", "active"), default="active")
    keep.add_argument("--from-request", default=None,
                      help="Request SHA of the adopted alternative this intention continues")
    keep.add_argument("--source-ref", default=None,
                      help="Recorded source reference inside that request, e.g. h2")
    keep.add_argument("--focus-id", default=None)
    revise = actions.add_parser(
        "set-intention-status", help="Keep, supersede or withdraw an author-directed intention",
    )
    revise.add_argument("--id", required=True)
    revise.add_argument(
        "--status", required=True,
        choices=("provisional", "active", "superseded", "withdrawn"),
    )
    apply_review = actions.add_parser(
        "apply-review",
        help="Apply one completed, reviewed working revision, identified by its request SHA-256",
    )
    apply_review.add_argument(
        "--request-sha256", required=True,
        help="Exact reviewed request SHA-256. The latest request is never applied by default.",
    )
    actions.add_parser("intentions", help="Show author-directed creative intentions and status")
    args = parser.parse_args(argv)
    store = CanvasStore(Path(args.project), args.canvas)
    if args.action == "prepare":
        result = prepare_architecture(store, args.instruction)
    elif args.action == "resume":
        result = project_architecture_resume(store)
    elif args.action == "complete-file":
        pending = project_architecture(store)
        if pending["status"] != "awaiting_host_agent" or not pending["request"]:
            raise ValueError("no pending host-agent architecture request to complete")
        request = HostAgentRequest(**pending["request"])
        candidate_text = Path(args.candidate).read_text(encoding="utf-8")
        response = build_host_agent_response(request, candidate_text)
        result = complete_architecture(store, response.model_dump())
    elif args.action == "record-concept":
        raw = json.loads(Path(args.concept).read_text(encoding="utf-8"))
        concept = ProvisionalNarrativeConcept.model_validate(raw)
        command_id = args.command_id or "concept-" + _digest(raw)[:16]
        canvas = store.load()
        updated = record_provisional_concept(
            store, concept, expected_revision=canvas.revision,
            command_id=command_id,
        )
        result = {
            "status": "provisional",
            "authority": "working_noncanonical",
            "canvas_id": store.canvas_id,
            "canvas_revision": updated.revision,
            "concept": concept.model_dump(mode="json"),
        }
    elif args.action == "apply-review":
        outcome = _apply_review_cli(store, args.request_sha256)
        print(json.dumps(outcome, indent=2, ensure_ascii=False))
        return 0 if outcome["application"]["result"] in {"applied", "already_applied"} else 1
    elif args.action == "keep-intention":
        directive = Path(args.directive_file).read_text(encoding="utf-8").strip()
        item = {
            "id": args.id or "intention-" + _digest({"title": args.title, "directive": directive})[:12],
            "kind": "note",
            "title": args.title,
            "group": "Creative intentions",
            "content": directive,
            "intention_status": args.status,
        }
        if args.from_request:
            if not re.fullmatch(r"[0-9a-f]{64}", args.from_request):
                raise ValueError("from-request must be a 64-character request SHA")
            item["proposal_origin"] = {
                "request_sha": args.from_request,
                "source_ref": args.source_ref or "selected_alternative",
                "source_kind": "creative_alternative",
                "focus_id": args.focus_id or "architecture",
            }
        canvas = store.load()
        command_id = "intention-" + _digest(item)[:16]
        updated = store.apply(
            "create-item", expected_revision=canvas.revision,
            command_id=command_id, payload={"item": item, "position": _free_position(canvas)},
        )
        result = {
            "status": "recorded",
            "authority": "author_directed_working_intention",
            "canvas_id": store.canvas_id,
            "canvas_revision": updated.revision,
            "intention": next(
                entry for entry in _creative_intentions(store) if entry["id"] == item["id"]
            ),
        }
    elif args.action == "set-intention-status":
        canvas = store.load()
        item = next((row for row in canvas.items if row.id == args.id), None)
        if item is None or item.intention_status is None:
            raise ValueError("creative intention not found")
        updated_item = item.model_dump(mode="json")
        updated_item["intention_status"] = args.status
        command_id = "intention-status-" + _digest({"id": args.id, "status": args.status})[:16]
        updated = store.apply(
            "update-item", expected_revision=canvas.revision,
            command_id=command_id, payload={"item": updated_item},
        )
        result = {
            "status": args.status,
            "authority": "author_directed_working_intention",
            "canvas_id": store.canvas_id,
            "canvas_revision": updated.revision,
            "intention": next(
                entry for entry in _creative_intentions(store) if entry["id"] == args.id
            ),
        }
    elif args.action == "intentions":
        result = {
            "authority": "author_directed_working_intention",
            "canvas_id": store.canvas_id,
            "intentions": _creative_intentions(store),
        }
    else:
        result = project_architecture(store)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
