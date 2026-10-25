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
from .studio_store import CanvasStore


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


def _source(
    store: CanvasStore, *, previous: dict | None = None, source_format: int = 2,
) -> dict:
    """Bound the agent-visible working source, without disguising omitted prose.

    Format 1 reproduces the exact historical projection for in-flight requests.
    Format 2 adds provenance metadata and content fingerprints for freshness;
    fingerprints never stand in for unavailable prose.
    """
    if source_format not in (1, 2):
        raise ValueError("unsupported Studio working-source format")
    canvas = store.load()
    all_items = [item for item in canvas.items if item.id != "story-vision"]
    selected = all_items[:24]
    selected_ids = {item.id for item in selected}
    vision = next((item.content for item in canvas.items if item.id == "story-vision"), "")
    items = []
    for item in selected:
        entry = {"id": item.id, "kind": item.kind, "title": item.title,
                 "group": item.group, "content": item.content[:1000]}
        if source_format == 2:
            entry["content_characters"] = len(item.content)
            entry["content_is_excerpt"] = len(item.content) > 1000
            if len(item.content) > 1000:
                entry["full_content_sha256"] = hashlib.sha256(
                    item.content.encode("utf-8")
                ).hexdigest()
        items.append(entry)
    included = [
        edge for edge in canvas.connections
        if edge.source in selected_ids and edge.target in selected_ids
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
    return result


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


def _narrative_design_context(store: CanvasStore) -> dict:
    """Compose the same small, auditable ontology guidance on develop and revise."""
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
        "accepted_story_identity": _accepted_story_design_context(store),
        "unknown_policy": (
            "No accepted Identity or omitted preference means UNKNOWN, not an "
            "implicit focused/maximalist/causal default. The agent may propose "
            "a provisional composition with explicit rationale; it may not "
            "attribute that choice to the author."
        ),
    }


def _source_fingerprint(store: CanvasStore, request_user: str) -> str:
    """Preserve the original digest for pre-context request/artifact reopens."""
    user = json.loads(request_user)
    previous = user["working_context"]["previous_candidate"]
    source_format = 2 if user["working_context"].get("working_source_format") == 2 else 1
    working = _source(store, previous=previous, source_format=source_format)
    if "narrative_design_context" not in user:
        return _digest(working)
    return _digest({
        "working_context": working,
        "narrative_design_context": _narrative_design_context(store),
    })


_SYSTEM = """You are Auteur's ABSTRACT NARRATIVE ARCHITECTURE agent, not its authority.
Read narrative_design_context in the user request BEFORE composing an architecture.
Its source-linked ontology principles are design guidance, not invented author
commitments. The accepted_story_identity, when present, is authoritative;
the current Story Vision and previous candidate are working material.
Working item content can be just the first 1,000 characters of a longer
scene, and working items/connections can be omitted by context limits.
Use working_source_format, content_is_excerpt, content_characters and
omitted_working_* counts to distinguish visible evidence from missing text.
A SHA-256 fingerprint identifies source freshness, NOT readable story facts.
For manuscript-first input, cite working item IDs in relevant summaries and
open questions. Separate observed prose from alternative interpretations;
never assert missing passages, motives or outcomes from a truncated excerpt.
If working intent conflicts with accepted Identity, surface the tension as
an unresolved proposal; never silently change the accepted story.

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



def _candidate_diff(previous: dict, proposed: dict) -> dict:
    """Explain a revision without confusing proposal changes with accepted-story impact."""
    categories: dict[str, dict] = {}
    for field, key in (
        ("nodes", "id"), ("links", "id"), ("phases", "id"),
        ("emotion_targets", "id"), ("complex_emotions", "id"),
        ("genre_contracts", "genre_node_id"), ("genre_interactions", "id"),
    ):
        old = {entry[key]: entry for entry in previous.get(field, [])}
        new = {entry[key]: entry for entry in proposed.get(field, [])}
        categories[field] = {
            "added": sorted(new.keys() - old.keys()),
            "removed": sorted(old.keys() - new.keys()),
            "changed": sorted(k for k in new.keys() & old.keys() if new[k] != old[k]),
        }
    categories["summary_changed"] = previous.get("summary") != proposed.get("summary")
    categories["note"] = (
        "Working architecture proposal only. Accepted Identity, Structure, Book, "
        "relations and prose remain unchanged. Any real downstream impact needs "
        "the existing source-backed impact/revision workflows."
    )
    return categories

def _current_candidate_is_stale(store: CanvasStore, current: dict | None) -> bool:
    """A saved working architecture stays readable after its input intent changes."""
    if not current:
        return False
    request = load_host_agent_request(
        _root(store) / "requests" / current["request_sha256"] / "request.json"
    )
    return _source_fingerprint(store, request.user) != current["source_sha256"]


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
    stale = _current_candidate_is_stale(store, current) if current and not pending else False
    return {
        "status": "review_ready" if review else "awaiting_host_agent" if pending
                  else "stale" if stale else "ready" if current else "not_started",
        "request": req.model_dump() if pending and not review else None,
        "candidate": current["candidate"] if current else None,
        "candidate_request_sha256": current["request_sha256"] if current else None,
        "review": review,
    }


def prepare_architecture(store: CanvasStore, instruction: str = "") -> dict:
    if not isinstance(instruction, str) or len(instruction) > 4000:
        raise ValueError("revision instruction must be text under 4000 characters")
    with _FilesystemLock(store._path(".canvas.lock")):
        current = _candidate(store)
        if instruction.strip() and not current:
            raise ValueError("nothing to revise; develop an initial architecture first")
        previous = current["candidate"] if instruction.strip() and current else None
        context = _source(store, previous=previous)
        if not context["vision"].strip() and not context["working_items"]:
            raise ValueError("write a Story Vision or a working idea first")
        design_context = _narrative_design_context(store)
        source_sha = _digest({
            "working_context": context,
            "narrative_design_context": design_context,
        })
        settings = {"canvas_id": store.canvas_id, "source_sha256": source_sha,
                    "operation": "revise" if instruction.strip() else "develop"}
        user = json.dumps({
            "working_context": context,
            "narrative_design_context": design_context,
            "revision_instruction": instruction,
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
        if _source_fingerprint(store, request.user) != request.settings["source_sha256"]:
            write_host_agent_response(base / "stale_response.json", response)
            raise BeginnerConcurrencyError(
                "the author's source vision or working story changed; response retained as stale evidence"
            )
        write_host_agent_response(base / "response.json", response)
        candidate = proposal.model_dump(mode="json")
        if instruction.strip():
            _atomic_json_write(base / "review.json", {
                "request_sha256": sha, "source_sha256": request.settings["source_sha256"],
                "prior_request_sha256": current["request_sha256"],
                "candidate": candidate, "changes": _candidate_diff(current["candidate"], candidate),
            })
        else:
            _atomic_json_write(_root(store) / "current.json", {
                "request_sha256": sha, "source_sha256": request.settings["source_sha256"],
                "candidate": candidate,
            })
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
            if _source_fingerprint(store, request.user) != request.settings["source_sha256"]:
                raise BeginnerConcurrencyError(
                    "working context changed: story vision or design context changed; review again"
                )
            _atomic_json_write(_root(store) / "current.json", {
                "request_sha256": request_sha256, "source_sha256": review["source_sha256"],
                "candidate": review["candidate"],
            })
        elif not current:
            raise ValueError("there is no current working architecture to revise")
    return project_architecture(store)


def main(argv: list[str] | None = None) -> int:
    """Portable operator bridge: the active coding agent supplies raw candidate JSON."""
    parser = argparse.ArgumentParser(description="Auteur Studio host-agent architecture bridge")
    parser.add_argument("--project", required=True, help="Local Auteur project root")
    parser.add_argument("--canvas", required=True, help="Canvas id from Studio URL")
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("show", help="Show current proposal or exact host-agent request")
    prepare = actions.add_parser("prepare", help="Prepare a new architecture request")
    prepare.add_argument("--instruction", default="", help="Optional revision request")
    submit = actions.add_parser("complete-file", help="Validate candidate JSON written by host agent")
    submit.add_argument("--candidate", required=True, help="Path to raw candidate JSON file")
    args = parser.parse_args(argv)
    store = CanvasStore(Path(args.project), args.canvas)
    if args.action == "prepare":
        result = prepare_architecture(store, args.instruction)
    elif args.action == "complete-file":
        pending = project_architecture(store)
        if pending["status"] != "awaiting_host_agent" or not pending["request"]:
            raise ValueError("no pending host-agent architecture request to complete")
        request = HostAgentRequest(**pending["request"])
        candidate_text = Path(args.candidate).read_text(encoding="utf-8")
        response = build_host_agent_response(request, candidate_text)
        result = complete_architecture(store, response.model_dump())
    else:
        result = project_architecture(store)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
