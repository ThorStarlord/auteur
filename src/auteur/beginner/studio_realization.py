"""Noncanonical Story Realization proposals linked to established *working architecture*.

Story Realization is an author-facing workspace, not the canonical Realization layer.
No Scene/Identity/Structure/Bible data is created or accepted here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from auteur.host_agent import (
    _atomic_json_write, build_host_agent_request, load_host_agent_request,
    validate_host_agent_response, write_host_agent_request, write_host_agent_response,
)
from .persistence import BeginnerConcurrencyError, _FilesystemLock
from .studio_store import CanvasStore
from .studio_architecture import _candidate as architecture_current, _digest, _read, _source


class RealizationElement(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    kind: Literal["character", "location", "faction", "world_system",
                  "plot_arc", "event", "scene"]
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    scope: str = Field(default="whole_story", max_length=100)
    architecture_refs: list[str] = Field(min_length=1, max_length=12)


class RealizationLink(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    source: str
    target: str
    function: str = Field(min_length=1, max_length=120)


class ArchitectureFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    architecture_node_id: str
    observation: str = Field(min_length=1, max_length=900)
    proposed_change: str = Field(min_length=1, max_length=900)


class RealizationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    summary: str = Field(min_length=1, max_length=3000)
    elements: list[RealizationElement] = Field(min_length=1, max_length=48)
    links: list[RealizationLink] = Field(default_factory=list, max_length=120)
    architecture_feedback: list[ArchitectureFeedback] = Field(default_factory=list, max_length=12)
    open_questions: list[str] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def coherent_candidate(self) -> "RealizationCandidate":
        ids = {element.id for element in self.elements}
        if len(ids) != len(self.elements) or len({link.id for link in self.links}) != len(self.links):
            raise ValueError("duplicate realization element or link id")
        if any(edge.source not in ids or edge.target not in ids or edge.source == edge.target
               for edge in self.links):
            raise ValueError("realization link references missing or identical elements")
        if len({item.id for item in self.architecture_feedback}) != len(self.architecture_feedback):
            raise ValueError("duplicate architecture feedback id")
        return self


_SYSTEM = """You are Auteur's STORY REALIZATION agent. Create optional concrete
fictional elements ONLY when the author requests realization. Use the source-bound
Narrative Architecture as design guidance, not as a ready-made plot.
Return candidates for characters, locations, factions, world systems, plot arcs,
events or scenes, with explicit architecture_refs for EVERY concrete element.
Construct causally different alternatives if appropriate. Do not assume a
specific realization has already been accepted or exists in canon.
If concrete discoveries suggest changing the governing architecture, put them
in architecture_feedback as proposed changes, not silent accepted edits.
Do not revise the architecture proposal yourself. Preserve stable IDs in a revision.
Return ONLY JSON {schema_version:1,summary,elements,links,
architecture_feedback,open_questions}.
element:{id,kind,title,description,scope,architecture_refs};
kind: character/location/faction/world_system/plot_arc/event/scene.
link:{id,source,target,function}; endpoints must be realization element IDs.
architecture_feedback:{id,architecture_node_id,observation,proposed_change}.
All elements are working proposals. Never accept story Identity, Structure,
Realization, Expression or relationship state."""


def _root(store: CanvasStore) -> Path:
    return store.directory / "realization"


def _current(store: CanvasStore) -> dict | None:
    return _read(_root(store) / "current.json")


def _source_snapshot(store: CanvasStore, focus_ids: list[str], previous: dict | None) -> dict:
    architecture = architecture_current(store)
    if not architecture:
        raise ValueError("develop Narrative Architecture before generating Story Realization")
    nodes = architecture["candidate"]["nodes"]
    known_ids = {node["id"] for node in nodes}
    if len(focus_ids) > 12 or len(set(focus_ids)) != len(focus_ids) or any(
        not isinstance(ref, str) or ref not in known_ids for ref in focus_ids
    ):
        raise ValueError("realization focus must contain distinct existing architecture IDs")
    working = _source(store)
    return {
        "architecture_request_sha256": architecture["request_sha256"],
        "architecture": architecture["candidate"],
        "focus_ids": focus_ids,
        "working_vision": working["vision"],
        "working_items": working["working_items"][:12],
        "previous_realization": previous,
    }


def _diff(old: dict, new: dict) -> dict:
    result = {}
    for field in ("elements", "links", "architecture_feedback"):
        before = {x["id"]: x for x in old.get(field, [])}
        after = {x["id"]: x for x in new.get(field, [])}
        result[field] = {
            "added": sorted(after.keys() - before.keys()),
            "removed": sorted(before.keys() - after.keys()),
            "changed": sorted(k for k in before.keys() & after.keys() if before[k] != after[k]),
        }
    result["summary_changed"] = old["summary"] != new["summary"]
    return result


def project_realization(store: CanvasStore) -> dict:
    store.load()
    pointer = _read(_root(store) / "latest_request.json")
    current = _current(store)
    request = None
    if pointer:
        sha = pointer.get("request_sha256")
        if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{64}", sha):
            raise ValueError("invalid realization request identity")
        request = load_host_agent_request(_root(store) / "requests" / sha / "request.json")
    pending = bool(request and (not current or current["request_sha256"] != request.request_sha256))
    review = _read(_root(store) / "requests" / request.request_sha256 / "review.json") if pending else None
    return {
        "status": "review_ready" if review else "awaiting_host_agent" if pending
                  else "ready" if current else "not_started",
        "request": request.model_dump() if pending and not review else None,
        "candidate": current["candidate"] if current else None,
        "candidate_request_sha256": current["request_sha256"] if current else None,
        "review": review,
    }


def prepare_realization(
    store: CanvasStore, focus_ids: list[str] | None = None, instruction: str = ""
) -> dict:
    if not isinstance(instruction, str) or len(instruction) > 4000:
        raise ValueError("realization instruction must be text under 4000 characters")
    if not isinstance(focus_ids or [], list):
        raise ValueError("focus_ids must be a list of architecture identifiers")
    with _FilesystemLock(store._path(".canvas.lock")):
        current = _current(store)
        if instruction.strip() and not current:
            raise ValueError("no existing realization candidate to revise")
        previous = current["candidate"] if instruction.strip() and current else None
        context = _source_snapshot(store, focus_ids or [], previous)
        sha = _digest(context)
        user = json.dumps({"source": context, "revision_instruction": instruction},
                          sort_keys=True, ensure_ascii=False)
        request = build_host_agent_request(
            candidate_id="realization-" + _digest({"source": sha, "user": user})[:24],
            role="studio_realization", system=_SYSTEM, user=user,
            settings={"canvas_id": store.canvas_id, "source_sha256": sha,
                      "operation": "revise" if instruction.strip() else "develop"},
        )
        path = _root(store)
        write_host_agent_request(path / "requests" / request.request_sha256 / "request.json", request)
        _atomic_json_write(path / "latest_request.json",
                           {"request_sha256": request.request_sha256})
    return project_realization(store)


def _assert_refs(proposal: RealizationCandidate, source: dict) -> None:
    valid = {node["id"] for node in source["architecture"]["nodes"]}
    if any(ref not in valid for item in proposal.elements for ref in item.architecture_refs):
        raise ValueError("realization elements must link to existing architecture nodes")
    if any(x.architecture_node_id not in valid for x in proposal.architecture_feedback):
        raise ValueError("architecture feedback must reference an existing architecture node")


def complete_realization(store: CanvasStore, payload: dict) -> dict:
    with _FilesystemLock(store._path(".canvas.lock")):
        pointer = _read(_root(store) / "latest_request.json")
        if not pointer:
            raise ValueError("no Story Realization request exists")
        sha = pointer["request_sha256"]
        base = _root(store) / "requests" / sha
        request = load_host_agent_request(base / "request.json")
        response = validate_host_agent_response(request, payload)
        proposal = RealizationCandidate.model_validate_json(response.text)
        previous_response = _read(base / "response.json")
        if previous_response:
            if previous_response != response.model_dump():
                raise BeginnerConcurrencyError("realization request already completed differently")
            return project_realization(store)
        current = _current(store)
        instruction = json.loads(request.user)["revision_instruction"]
        previous = current["candidate"] if instruction.strip() and current else None
        focus = json.loads(request.user)["source"]["focus_ids"]
        source = _source_snapshot(store, focus, previous)
        if _digest(source) != request.settings["source_sha256"]:
            write_host_agent_response(base / "stale_response.json", response)
            raise BeginnerConcurrencyError("Story Vision or architecture changed; stale realization retained")
        _assert_refs(proposal, source)
        write_host_agent_response(base / "response.json", response)
        candidate = proposal.model_dump(mode="json")
        if instruction.strip():
            _atomic_json_write(base / "review.json", {
                "request_sha256": sha, "prior_request_sha256": current["request_sha256"],
                "source_sha256": request.settings["source_sha256"],
                "candidate": candidate, "changes": _diff(current["candidate"], candidate),
            })
        else:
            _atomic_json_write(_root(store) / "current.json", {
                "request_sha256": sha, "source_sha256": request.settings["source_sha256"],
                "candidate": candidate,
            })
    return project_realization(store)


def apply_realization_review(store: CanvasStore, request_sha256: str) -> dict:
    if not isinstance(request_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", request_sha256):
        raise ValueError("valid realization request SHA is required")
    with _FilesystemLock(store._path(".canvas.lock")):
        pointer = _read(_root(store) / "latest_request.json")
        if not pointer or pointer["request_sha256"] != request_sha256:
            raise BeginnerConcurrencyError("a newer realization request superseded this review")
        review = _read(_root(store) / "requests" / request_sha256 / "review.json")
        if not review:
            current = _current(store)
            if current and current["request_sha256"] == request_sha256:
                return project_realization(store)
            raise ValueError("no completed realization revision to apply")
        current = _current(store)
        if not current or current["request_sha256"] != review["prior_request_sha256"]:
            raise BeginnerConcurrencyError("realization baseline changed; review again")
        request = load_host_agent_request(_root(store) / "requests" / request_sha256 / "request.json")
        source = json.loads(request.user)["source"]
        if _digest(_source_snapshot(store, source["focus_ids"], current["candidate"])) != request.settings["source_sha256"]:
            raise BeginnerConcurrencyError("architecture or working source changed; review again")
        _atomic_json_write(_root(store) / "current.json", {
            "request_sha256": request_sha256, "source_sha256": review["source_sha256"],
            "candidate": review["candidate"],
        })
    return project_realization(store)
