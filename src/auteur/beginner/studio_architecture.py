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

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator

from auteur.narrative_ontology.architecture_preferences import (
    CausalDistributionPreference, ComplexityPreference, EngineHierarchyPreference,
)
from auteur.host_agent import (
    _atomic_json_write,
    HostAgentRequest,
    build_host_agent_request,
    build_host_agent_response,
    load_host_agent_request,
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


class GenreContract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    genre_node_id: str
    role: Literal["governing", "supporting", "tertiary", "local"]
    emotion_target_ids: list[str] = Field(default_factory=list, max_length=20)
    complex_emotion_ids: list[str] = Field(default_factory=list, max_length=12)
    trope_functions: list[str] = Field(min_length=1, max_length=12)
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


class ArchitectureCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1, 2]
    summary: str = Field(min_length=1, max_length=3000)
    nodes: list[ArchitectureNode] = Field(min_length=1, max_length=80)
    links: list[ArchitectureLink] = Field(default_factory=list, max_length=180)
    phases: list[NarrativePhase] = Field(default_factory=list, max_length=32)
    open_questions: list[str] = Field(default_factory=list, max_length=16)
    emotion_targets: list[EmotionTarget] = Field(default_factory=list, max_length=30)
    complex_emotions: list[ComplexEmotion] = Field(default_factory=list, max_length=16)
    genre_contracts: list[GenreContract] = Field(default_factory=list, max_length=14)
    genre_interactions: list[GenreInteraction] = Field(default_factory=list, max_length=40)

    @model_validator(mode="after")
    def valid_graph(self, info: ValidationInfo) -> "ArchitectureCandidate":
        if info.context and info.context.get("new_host_agent_response") and self.schema_version != 2:
            raise ValueError("new Studio architecture responses must use schema_version 2")
        nodes = {node.id for node in self.nodes}
        phases = {phase.id for phase in self.phases}
        if len(nodes) != len(self.nodes) or len(phases) != len(self.phases):
            raise ValueError("duplicate candidate node or phase id")
        if len({link.id for link in self.links}) != len(self.links):
            raise ValueError("duplicate candidate link id")
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
        if self.schema_version == 2:
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
You may refer to concrete proper nouns explicitly supplied by the author, but
do not elaborate them into fictional content. Generic archetypes may illustrate
a structural function without inventing story facts.

Use the six chosen basic-emotion labels exactly: joy, sadness, fear, anger,
disgust, surprise. Name concrete intended reader-directed effects and
narrative eliciting conditions, and explain how aesthetic strategies help.
Use complex emotions ONLY when useful; each must cite 2+ distinct basic labels,
with a contextual interpretation, never a scientific/causal guarantee.
Distinguish explicit author declarations from your own working hypotheses.

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
role primary/supporting/contrasting/local; provenance author_declared/agent_proposed.
complex_emotion: {id,title,basic_emotions,context}; 2+ distinct basic labels.
genre_contract: {genre_node_id,role,emotion_target_ids,complex_emotion_ids,
trope_functions,narrative_engine,structural_pattern,aesthetic_strategies,
payoff_expectations}; genre_node_id identifies one genre node.
genre_interaction: {id,source_genre_id,target_genre_id,kind,mechanism,risk}.
phase: {id,title,order,scope,genres,genre_activations,reader_experience,
aesthetic,narrative_function,transition,parallel_with}.
genre: {genre,role}; role governing/locally_dominant/supporting/background.
genre_activation: {genre_node_id,basic_emotions,trope_functions,structural_function}.
Unknown lengths stay unknown; phase order is NOT a chapter or act number.
Do not fabricate genre commitments when the brief does not establish them.
Keep stable IDs across revisions, preserve unaffected choices, explain uncertainty.
Resolve story-mechanics questions with coherent, revisable provisional defaults
when the supplied vision supports them. Put those defaults in the architecture
and identify them as agent proposals; do not turn them into required author
questions. Reserve open_questions for genuinely authorial preferences or
commitments that cannot be responsibly inferred. A proposal never waits for
answers before it can be developed or revised.
All material is a noncanonical proposal; never accept Identity, Structure or prose."""



def _current_candidate_freshness(store: CanvasStore, current: dict) -> str:
    """Distinguish author-source change from an interpretive-guidance change."""
    request = load_host_agent_request(
        _root(store) / "requests" / current["request_sha256"] / "request.json"
    )
    settings = request.settings
    if settings.get("freshness_format") == 2:
        user = json.loads(request.user)
        if _author_source_fingerprint(store, user) != current["source_sha256"]:
            return "stale"
        expected_guidance = current.get(
            "design_guidance_sha256", settings.get("design_guidance_sha256"),
        )
        if expected_guidance and _digest(_design_context_parts(
            store, _user_working_context(store, user),
        )[1]) != expected_guidance:
            return "guidance_changed"
        return "ready"
    return "stale" if _source_fingerprint(store, request.user) != current["source_sha256"] else "ready"


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
    if review:
        status = "review_ready"
    elif pending:
        status = "awaiting_host_agent"
    elif current:
        status = _current_candidate_freshness(store, current)
    else:
        status = "not_started"
    return {
        "status": status,
        "request": req.model_dump() if pending and not review else None,
        "candidate": current["candidate"] if current else None,
        "candidate_request_sha256": current["request_sha256"] if current else None,
        "review": review,
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
            rows.append({"adopted_in_request_sha256": sha, **submitted})
        review = _read(folder / "review.json")
        if not review or not review.get("prior_request_sha256"):
            break
        sha = review["prior_request_sha256"]
    return rows


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
    return {
        "kind": "studio_architecture_resume",
        "authority": "working_noncanonical",
        "canvas_id": store.canvas_id,
        "canvas_revision": canvas.revision,
        "story_vision": vision,
        "architecture": candidate,
        "architecture_status": projection["status"],
        "candidate_request_sha256": projection["candidate_request_sha256"],
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
    return {
        "inquiry_request_sha256": selection.inquiry_request_sha256,
        "hypothesis_id": match["id"],
        "title": match["title"],
        "description": match["description"],
        "divergence_axis": match["divergence_axis"],
        "operation": intent.get("operation"),
        "author_question": intent.get("author_text", ""),
        "authority": "noncanonical_creative_alternative",
    }


def prepare_architecture(
    store: CanvasStore, instruction: str = "", graph_intent: dict | None = None,
    selected_alternative: dict | None = None,
) -> dict:
    if not isinstance(instruction, str) or len(instruction) > 4000:
        raise ValueError("revision instruction must be text under 4000 characters")
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
            resolved_graph_intent = resolve_graph_intent(
                current["candidate"], current["request_sha256"], typed_intent,
            )
        if instruction.strip() and not current:
            raise ValueError("nothing to revise; develop an initial architecture first")
        previous = current["candidate"] if instruction.strip() and current else None
        context = _source(store, previous=previous)
        if not context["vision"].strip() and not context["working_items"]:
            raise ValueError("write a Story Vision or a working idea first")
        accepted, guidance, design_context = _design_context_parts(store, context)
        source_sha = _digest({
            "working_context": _author_working_context(context),
            "accepted_story_identity": accepted,
        })
        guidance_sha = _digest(guidance)
        settings = {
            "canvas_id": store.canvas_id,
            "source_sha256": source_sha,
            "design_guidance_sha256": guidance_sha,
            "intention_sha256": _intention_fingerprint(store),
            "freshness_format": 2,
            "operation": "revise" if instruction.strip() else "develop",
        }
        user = json.dumps({
            "freshness_format": 2,
            "working_context": context,
            "narrative_design_context": design_context,
            "revision_instruction": instruction,
            **({"graph_intent": resolved_graph_intent} if resolved_graph_intent else {}),
            **({"selected_creative_alternative": selected_context} if selected_context else {}),
        }, ensure_ascii=False, sort_keys=True)
        request = build_host_agent_request(
            candidate_id="studio-" + _digest({"settings": settings, "user": user})[:24],
            role="studio_architecture", system=_SYSTEM, user=user, settings=settings,
        )
        base = _root(store)
        write_host_agent_request(base / "requests" / request.request_sha256 / "request.json", request)
        _atomic_json_write(base / "latest_request.json",
                           {"request_sha256": request.request_sha256})
    return project_architecture(store)


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
        instruction = json.loads(request.user)["revision_instruction"]
        settings = request.settings
        if settings.get("freshness_format") == 2:
            user = json.loads(request.user)
            author_changed = _author_source_fingerprint(store, user) != settings["source_sha256"]
            guidance_changed = (
                _digest(_design_context_parts(
                    store, _user_working_context(store, user),
                )[1]) != settings["design_guidance_sha256"]
            )
        else:
            author_changed = _source_fingerprint(store, request.user) != settings["source_sha256"]
            guidance_changed = False
        if author_changed:
            write_host_agent_response(base / "stale_response.json", response)
            raise BeginnerConcurrencyError(
                "the author's source vision or working story changed; response retained as stale evidence"
            )
        if guidance_changed:
            write_host_agent_response(base / "stale_response.json", response)
            raise BeginnerConcurrencyError(
                "the narrative design guidance changed; response retained as stale evidence"
            )
        if settings.get("intention_sha256") and _intention_fingerprint(store) != settings["intention_sha256"]:
            write_host_agent_response(base / "stale_response.json", response)
            raise BeginnerConcurrencyError(
                "the author's creative intentions changed; response retained as stale evidence"
            )
        write_host_agent_response(base / "response.json", response)
        candidate = proposal.model_dump(mode="json")
        record = {
            "request_sha256": sha,
            "source_sha256": settings["source_sha256"],
            "candidate": candidate,
        }
        if settings.get("freshness_format") == 2:
            record["design_guidance_sha256"] = settings["design_guidance_sha256"]
        if instruction.strip():
            accepted_identity = json.loads(request.user)[
                "narrative_design_context"
            ].get("accepted_story_identity")
            record.update(build_architecture_review(
                current["candidate"], candidate, instruction,
                accepted_identity=accepted_identity,
            ))
            record["prior_request_sha256"] = current["request_sha256"]
            submitted = json.loads(request.user)
            if submitted.get("graph_intent"):
                record["graph_intent_receipt"] = submitted["graph_intent"]
            if submitted.get("selected_creative_alternative"):
                record["selected_creative_alternative"] = submitted["selected_creative_alternative"]
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
            if settings.get("freshness_format") == 2:
                user = json.loads(request.user)
                changed = (
                    _author_source_fingerprint(store, user) != settings["source_sha256"]
                    or _digest(_design_context_parts(
                        store, _user_working_context(store, user),
                    )[1]) != settings["design_guidance_sha256"]
                    or (
                        settings.get("intention_sha256")
                        and _intention_fingerprint(store) != settings["intention_sha256"]
                    )
                )
            else:
                changed = _source_fingerprint(store, request.user) != settings["source_sha256"]
            if changed:
                raise BeginnerConcurrencyError(
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
