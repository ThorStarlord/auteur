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
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    def valid_graph(self) -> "ArchitectureCandidate":
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


def _source(store: CanvasStore, *, previous: dict | None = None) -> dict:
    canvas = store.load()
    selected = [item for item in canvas.items if item.id != "story-vision"][:24]
    selected_ids = {item.id for item in selected}
    vision = next((item.content for item in canvas.items if item.id == "story-vision"), "")
    return {
        "vision": vision,
        "working_items": [
            {"id": item.id, "kind": item.kind, "title": item.title,
             "group": item.group, "content": item.content[:1000]}
            for item in selected
        ],
        "working_connections": [
            {"source": edge.source, "target": edge.target, "label": edge.label}
            for edge in canvas.connections
            if edge.source in selected_ids and edge.target in selected_ids
        ][:80],
        "previous_candidate": previous,
    }


_SYSTEM = """You are Auteur's ABSTRACT NARRATIVE ARCHITECTURE agent, not its authority.
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
    return {
        "status": "review_ready" if review else "awaiting_host_agent" if pending
                  else "ready" if current else "not_started",
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
        source_sha = _digest(context)
        settings = {"canvas_id": store.canvas_id, "source_sha256": source_sha,
                    "operation": "revise" if instruction.strip() else "develop"}
        user = json.dumps({"working_context": context, "revision_instruction": instruction},
                          ensure_ascii=False, sort_keys=True)
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
        proposal = ArchitectureCandidate.model_validate_json(response.text)
        current = _candidate(store)
        prior_response = _read(base / "response.json")
        if prior_response:
            if prior_response != response.model_dump():
                raise BeginnerConcurrencyError("a different response already completed this request")
            return project_architecture(store)
        instruction = json.loads(request.user)["revision_instruction"]
        previous = current["candidate"] if instruction.strip() and current else None
        if _digest(_source(store, previous=previous)) != request.settings["source_sha256"]:
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
            if _digest(_source(store, previous=current["candidate"])) != request.settings["source_sha256"]:
                raise BeginnerConcurrencyError("story vision or working context changed; review again")
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
