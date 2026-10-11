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
    reader_experience: str | None = Field(default=None, max_length=400)
    aesthetic: str | None = Field(default=None, max_length=400)
    narrative_function: str = Field(min_length=1, max_length=1000)
    transition: str | None = Field(default=None, max_length=700)
    parallel_with: list[str] = Field(default_factory=list, max_length=12)


class ArchitectureCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    summary: str = Field(min_length=1, max_length=3000)
    nodes: list[ArchitectureNode] = Field(min_length=1, max_length=80)
    links: list[ArchitectureLink] = Field(default_factory=list, max_length=180)
    phases: list[NarrativePhase] = Field(default_factory=list, max_length=32)
    open_questions: list[str] = Field(default_factory=list, max_length=16)

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


_SYSTEM = """You are Auteur's narrative-architecture proposing agent, not its authority.
Use the author's declared experience, aesthetic, tropes, genre hierarchy and
structure as the highest-priority inputs. Never invent declared author intent.
Build a legible *candidate*, describing story engines, trope functions, reader
experience, aesthetic framing and structural relationships, not just labels.
For revisions, preserve stable node/phase IDs and untouched creative decisions.
Represent optional genre alternation, overlap, genuine pivots and uncertainty.
Return one JSON object only with exactly:
schema_version=1, summary, nodes, links, phases, open_questions.
node: {id,title,category,summary,scope,parent_id}; category in
reader_experience,aesthetic,genre,trope,engine,thread,structure,theme,character,
relationship,other. scope is a human-readable story/book/arc/chapter focus.
link: {id,source,target,function}, where endpoints are node IDs.
phase: {id,title,order,scope,genres,reader_experience,aesthetic,
narrative_function,transition,parallel_with}; genre: {genre,role}, role in
governing,locally_dominant,supporting,background.
Unknown phase duration must stay unknown; order is not a chapter number.
Keep 1-80 nodes, <=180 links, <=32 phases and <=16 open questions.
Everything is noncanonical working proposal. No auto-acceptance or prose."""



def _candidate_diff(previous: dict, proposed: dict) -> dict:
    """Explain a revision without confusing proposal changes with accepted-story impact."""
    categories: dict[str, dict] = {}
    for field in ("nodes", "links", "phases"):
        old = {entry["id"]: entry for entry in previous.get(field, [])}
        new = {entry["id"]: entry for entry in proposed.get(field, [])}
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
