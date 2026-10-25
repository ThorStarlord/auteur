"""Noncanonical Story Realization proposals linked to established *working architecture*.

Story Realization is an author-facing workspace, not the canonical Realization layer.
No Scene/Identity/Structure/Bible data is created or accepted here.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from auteur.host_agent import (
    _atomic_json_write, HostAgentRequest, build_host_agent_request,
    build_host_agent_response, load_host_agent_request,
    validate_host_agent_response, write_host_agent_request, write_host_agent_response,
)
from .persistence import BeginnerConcurrencyError, _FilesystemLock
from .studio_store import CanvasStore
from .studio_architecture import (
    _candidate as architecture_current, _current_candidate_is_stale, _digest, _read, _source,
)


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
Working items may contain only the first 1,000 characters of longer prose.
Respect content_is_excerpt, content_characters and omitted_working_item_count;
source fingerprints show freshness, not content the agent has actually read.
When interpreting existing manuscript fragments, cite visible working item IDs,
separate observed text from proposed story mechanisms, and never invent facts
from missing text. All inferred character motives and outcomes stay provisional.
Return candidates for characters, locations, factions, world systems, plot arcs,
events or scenes, with explicit architecture_refs for EVERY concrete element.
Construct causally different alternatives if appropriate. When source.focus_ids
is nonempty, include at least one concrete element referencing EACH selected
architecture node; other relevant nodes may also be used. An empty focus_ids
means whole-story development. For each selected focus, make its causal or
thematic function visible in a concrete element description: show what it
causes, constrains, enables, or changes in characters' actions or conflicts.
Do not merely attach a focus ID to an unrelated element to satisfy validation.
If an abstract focus has multiple plausible realizations, offer them as
provisional alternatives or open questions, not accepted story facts.
Keep link function labels within 120 characters.
Do not assume a specific realization has already been accepted or exists in canon.
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


def _source_snapshot(
    store: CanvasStore, focus_ids: list[str], previous: dict | None,
    *, source_format: int = 2,
) -> dict:
    architecture = architecture_current(store)
    if not architecture:
        raise ValueError("develop Narrative Architecture before generating Story Realization")
    nodes = architecture["candidate"]["nodes"]
    known_ids = {node["id"] for node in nodes}
    if len(focus_ids) > 12 or any(not isinstance(ref, str) for ref in focus_ids):
        raise ValueError("realization focus must contain architecture identifiers")
    if len(set(focus_ids)) != len(focus_ids) or any(ref not in known_ids for ref in focus_ids):
        raise ValueError("realization focus must contain distinct existing architecture IDs")
    working = _source(store, source_format=source_format)
    visible_items = working["working_items"][:12]
    result = {
        "architecture_request_sha256": architecture["request_sha256"],
        "architecture": architecture["candidate"],
        "focus_ids": focus_ids,
        "working_vision": working["vision"],
        "working_items": visible_items,
        "previous_realization": previous,
    }
    if source_format == 2:
        dropped_items = working["working_items"][12:]
        omitted = working["omitted_working_item_count"] + len(dropped_items)
        result["working_source_format"] = 2
        result["omitted_working_item_count"] = omitted
        if omitted:
            result["omitted_working_items_sha256"] = _digest({
                "dropped_visible_items": dropped_items,
                "already_omitted": working.get("omitted_working_items_sha256"),
            })
    return result


def _source_format(original: dict) -> int:
    """Honor the source projection used when a prior agent request was staged."""
    return 2 if original.get("working_source_format") == 2 else 1


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
    stale = False
    if current and not pending:
        source_request = load_host_agent_request(
            _root(store) / "requests" / current["request_sha256"] / "request.json"
        )
        original = json.loads(source_request.user)["source"]
        try:
            latest = _source_snapshot(
                store, original["focus_ids"], original["previous_realization"],
                source_format=_source_format(original),
            )
            stale = _digest(latest) != current["source_sha256"]
        except ValueError:
            stale = True
    return {
        "status": "review_ready" if review else "awaiting_host_agent" if pending
                  else "stale" if stale else "ready" if current else "not_started",
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
        if _current_candidate_is_stale(store, architecture_current(store)):
            raise ValueError("narrative architecture is stale; develop or revise it before realization")
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
    covered = {ref for item in proposal.elements for ref in item.architecture_refs}
    if not set(source["focus_ids"]).issubset(covered):
        raise ValueError("realization elements must cover each selected architecture focus")
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
        original_source = json.loads(request.user)["source"]
        source = _source_snapshot(
            store, original_source["focus_ids"], previous,
            source_format=_source_format(original_source),
        )
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
        if _digest(_source_snapshot(
            store, source["focus_ids"], current["candidate"],
            source_format=_source_format(source),
        )) != request.settings["source_sha256"]:
            raise BeginnerConcurrencyError("architecture or working source changed; review again")
        _atomic_json_write(_root(store) / "current.json", {
            "request_sha256": request_sha256, "source_sha256": review["source_sha256"],
            "candidate": review["candidate"],
        })
    return project_realization(store)


def main(argv: list[str] | None = None) -> int:
    """A local coding agent supplies candidate JSON; this CLI never calls a provider."""
    parser = argparse.ArgumentParser(description="Auteur Story Realization host-agent bridge")
    parser.add_argument("--project", required=True)
    parser.add_argument("--canvas", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("show")
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--focus", action="append", default=[])
    prepare.add_argument("--instruction", default="")
    finish = commands.add_parser("complete-file")
    finish.add_argument("--candidate", required=True)
    args = parser.parse_args(argv)
    store = CanvasStore(Path(args.project), args.canvas)
    if args.command == "prepare":
        result = prepare_realization(store, args.focus, args.instruction)
    elif args.command == "complete-file":
        pending = project_realization(store)
        if pending["status"] != "awaiting_host_agent" or not pending["request"]:
            raise ValueError("no pending realization request to complete")
        request = HostAgentRequest(**pending["request"])
        reply = build_host_agent_response(
            request, Path(args.candidate).read_text(encoding="utf-8")
        )
        result = complete_realization(store, reply.model_dump())
    else:
        result = project_realization(store)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
