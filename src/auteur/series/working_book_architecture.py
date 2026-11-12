"""Working Book Architecture: one Book's provisional, noncanonical function (develop and resume).

A Book artifact holds the detailed function of one Book: its question and pressure, the Series
conditions it inherits, the engines and agents that drive its conflict, its choice and closure,
its consequences for the Series, its assumptions, rejected alternatives and unknowns. It references
the canvas's working Series architecture by node id and open-question index and text hash. It never
writes that architecture, never writes accepted state, and never reaches an accept path.

Records live under `architecture/books/<n>/` in the canvas directory and share the canvas lock.
This increment provides develop (prepare, complete) and fresh-process resume. Revision, withdrawal
and apply are deferred to the next increment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from auteur.beginner.persistence import BeginnerConcurrencyError, _FilesystemLock
from auteur.beginner.studio_architecture import _candidate, _current_candidate_freshness
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import (
    HostAgentRequest,
    _atomic_json_write,
    build_host_agent_request,
    build_host_agent_response,
    load_host_agent_request,
    validate_host_agent_response,
    write_host_agent_request,
    write_host_agent_response,
)
from auteur.series.models import DependencyType

REQUEST_KIND = "auteur_working_book_architecture_request_v1"
ROLE = "working_book_architecture"
STORY_VISION_ID = "story-vision"

Provenance = Literal[
    "author_fixed", "derived", "agent_proposed", "hypothetical", "unresolved", "accepted", "unlabelled",
]
AGENT_PROVENANCE = frozenset({"derived", "agent_proposed", "hypothetical", "unresolved"})
_ID = r"^[a-z][a-z0-9_-]{0,79}$"
_MAX_TEXT = 8000  # sanity bound against runaway output, not a content cap


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Ref(BaseModel):
    """A typed reference: a Series node, a Book element, or a visible author-source item."""
    model_config = ConfigDict(extra="forbid", strict=True)
    kind: Literal["series_node", "book_element", "source_item"]
    id: str = Field(min_length=1, max_length=120)


class BookElement(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=_ID)
    provenance: Provenance
    text: str = Field(min_length=1, max_length=_MAX_TEXT)
    refs: list[Ref] = Field(default_factory=list, max_length=24)

    @model_validator(mode="after")
    def agent_may_write_this_provenance(self) -> "BookElement":
        if self.provenance not in AGENT_PROVENANCE:
            raise ValueError(
                f"provenance {self.provenance!r} cannot be written by an agent; "
                f"use one of {sorted(AGENT_PROVENANCE)}"
            )
        return self


class FunctionBlock(BookElement):
    question: str = Field(min_length=1, max_length=1000)
    pressure: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def cites_series_conditions(self) -> "FunctionBlock":
        if not any(ref.kind == "series_node" for ref in self.refs):
            raise ValueError("the Book function must cite at least one Series node")
        return self


class EngineElement(BookElement):
    condition: str = Field(min_length=1, max_length=1200)
    choice: str | None = Field(default=None, max_length=1200)
    consequence: str = Field(min_length=1, max_length=1200)
    changed_state: str = Field(min_length=1, max_length=1200)
    new_possibility: str | None = Field(default=None, max_length=1200)


class AgentElement(BookElement):
    """A Book-level motive or constraint. A proper name requires a visible source for the name."""
    name: str | None = Field(default=None, min_length=1, max_length=120)
    name_source: Ref | None = None

    @model_validator(mode="after")
    def named_agents_have_a_visible_source(self) -> "AgentElement":
        if self.name is None:
            return self
        if self.name_source is None or self.name_source.kind not in ("source_item", "series_node"):
            raise ValueError(f"named agent {self.id!r} needs a name_source that is a source item or Series node")
        return self


class ChoiceBlock(BookElement):
    options: list[BookElement] = Field(min_length=2, max_length=6)
    chosen_option_id: str = Field(pattern=_ID)
    costs_kept_visible: list[BookElement] = Field(min_length=1, max_length=12)
    transformation: BookElement

    @model_validator(mode="after")
    def chosen_option_exists(self) -> "ChoiceBlock":
        option_ids = [option.id for option in self.options]
        if len(set(option_ids)) != len(option_ids):
            raise ValueError("choice option ids must be unique")
        if self.chosen_option_id not in option_ids:
            raise ValueError("chosen_option_id must name one of the options")
        return self


class ClosureElement(BookElement):
    closure: bool


class ConsequenceElement(BookElement):
    kind: Literal["changes", "preserves", "complicates"]


class PossibilityElement(BookElement):
    kind: Literal["enabled", "closed"]


class AssumptionElement(BookElement):
    reversal: str | None = Field(default=None, min_length=1, max_length=1200)

    @model_validator(mode="after")
    def agent_assumptions_state_a_reversal(self) -> "AssumptionElement":
        if self.provenance == "agent_proposed" and not self.reversal:
            raise ValueError(f"agent-proposed assumption {self.id!r} must state a reversal condition")
        return self


class AlternativeElement(BookElement):
    title: str = Field(min_length=1, max_length=160)
    status: Literal["hypothetical"]
    rationale: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def alternatives_are_hypothetical(self) -> "AlternativeElement":
        if self.provenance != "hypothetical":
            raise ValueError(f"alternative {self.id!r} must carry hypothetical provenance")
        return self


class DecisionElement(BookElement):
    """An unresolved author decision, bound to one Series open question by index and text hash."""
    series_question_index: int = Field(ge=0, le=63)
    series_question_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class TypedEdge(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=_ID)
    source: str = Field(pattern=_ID)
    target: Ref
    dependency: DependencyType
    function: str = Field(min_length=1, max_length=400)


class WorkingBookArchitecture(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    book_number: int = Field(ge=1, le=60)
    title: str = Field(min_length=1, max_length=160)
    function: FunctionBlock
    inherited: list[BookElement] = Field(default_factory=list, max_length=24)
    engines: list[EngineElement] = Field(min_length=1, max_length=12)
    agents: list[AgentElement] = Field(default_factory=list, max_length=16)
    choice: ChoiceBlock
    local_resolution: list[ClosureElement] = Field(min_length=1, max_length=16)
    series_consequences: list[ConsequenceElement] = Field(min_length=1, max_length=16)
    later_possibilities: list[PossibilityElement] = Field(default_factory=list, max_length=16)
    assumptions: list[AssumptionElement] = Field(min_length=1, max_length=24)
    alternatives: list[AlternativeElement] = Field(default_factory=list, max_length=12)
    unresolved: list[BookElement] = Field(default_factory=list, max_length=32)
    open_author_decisions: list[DecisionElement] = Field(default_factory=list, max_length=16)
    typed_edges: list[TypedEdge] = Field(default_factory=list, max_length=120)


def _elements(artifact: WorkingBookArchitecture) -> list[BookElement]:
    """Every element in the artifact, including nested choice parts. Typed edges are not elements."""
    found: list[BookElement] = [artifact.function, *artifact.inherited, *artifact.engines, *artifact.agents]
    found += [artifact.choice, *artifact.choice.options, *artifact.choice.costs_kept_visible,
              artifact.choice.transformation]
    found += [*artifact.local_resolution, *artifact.series_consequences, *artifact.later_possibilities,
              *artifact.assumptions, *artifact.alternatives, *artifact.unresolved,
              *artifact.open_author_decisions]
    return found


def _all_refs(artifact: WorkingBookArchitecture) -> list[tuple[str, Ref]]:
    refs: list[tuple[str, Ref]] = []
    for element in _elements(artifact):
        refs += [(element.id, ref) for ref in element.refs]
        if isinstance(element, AgentElement) and element.name_source is not None:
            refs.append((element.id, element.name_source))
    refs += [(edge.id, edge.target) for edge in artifact.typed_edges]
    return refs


def _series_refs(artifact: WorkingBookArchitecture) -> set[str]:
    return {ref.id for _, ref in _all_refs(artifact) if ref.kind == "series_node"}


def _check_references(
    artifact: WorkingBookArchitecture, series_candidate: dict, visible_source_ids: set[str],
) -> None:
    """Every reference must resolve against the Series revision this request was built on."""
    ids = [element.id for element in _elements(artifact)] + [edge.id for edge in artifact.typed_edges]
    duplicates = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    if duplicates:
        raise ValueError(f"duplicate Book element id: {', '.join(duplicates)}")
    element_ids = {element.id for element in _elements(artifact)}
    node_ids = {node["id"] for node in series_candidate.get("nodes", [])}
    problems: list[str] = []
    for owner, ref in _all_refs(artifact):
        if ref.kind == "series_node":
            resolved = ref.id in node_ids
        elif ref.kind == "book_element":
            resolved = ref.id in element_ids
        else:
            resolved = ref.id in visible_source_ids
        if not resolved:
            problems.append(f"{owner}: {ref.kind} reference {ref.id!r} does not resolve")
    for edge in artifact.typed_edges:
        if edge.source not in element_ids:
            problems.append(f"{edge.id}: source {edge.source!r} is not a Book element")
    questions = series_candidate.get("open_questions", [])
    for decision in artifact.open_author_decisions:
        index = decision.series_question_index
        if index >= len(questions):
            problems.append(f"{decision.id}: Series open question {index} does not exist")
        elif _text_digest(questions[index]) != decision.series_question_sha256:
            problems.append(f"{decision.id}: Series open question {index} text changed; reference is stale")
    if problems:
        raise ValueError("; ".join(problems[:20]))


# --- storage and lifecycle -------------------------------------------------------------

def _books_root(store: CanvasStore) -> Path:
    return store.directory / "architecture" / "books"


def _book_root(store: CanvasStore, book_number: int) -> Path:
    return _books_root(store) / str(book_number)


def _read(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    if not isinstance(data, dict):
        raise ValueError("Book architecture record must be an object")
    return data


def _check_number(book_number: int) -> None:
    if not isinstance(book_number, int) or not 1 <= book_number <= 60:
        raise ValueError("book number must be an integer from 1 to 60")


def _author_source(store: CanvasStore, book_number: int) -> dict:
    """Author-visible source for one Book: the Story Vision, this Book's source items, and intentions."""
    canvas = store.load()
    vision = [
        {"id": item.id, "title": item.title, "content": item.content}
        for item in canvas.items if item.id == STORY_VISION_ID
    ]
    book_items = [
        {"id": item.id, "title": item.title, "group": item.group, "content": item.content}
        for item in canvas.items if item.group == f"book-{book_number}"
    ]
    intentions = [
        {"id": item.id, "title": item.title, "status": item.intention_status, "content": item.content}
        for item in canvas.items if item.intention_status is not None
    ]
    return {"story_vision": vision, "book_source": book_items, "creative_intentions": intentions}


def _visible_source_ids(source: dict) -> list[str]:
    ids = [item["id"] for group in ("story_vision", "book_source", "creative_intentions")
           for item in source[group]]
    return sorted(ids)


def _series_changed(store: CanvasStore, settings: dict) -> bool:
    series = _candidate(store)
    return series is None or series["request_sha256"] != settings["series_request_sha256"]


def _source_changed(store: CanvasStore, book_number: int, settings: dict) -> bool:
    return _digest(_author_source(store, book_number)) != settings["source_sha256"]


def _freshness(store: CanvasStore, book_number: int, record: dict) -> dict:
    series = _candidate(store)
    series_changed = series is None or series["request_sha256"] != record["series_request_sha256"]
    source_changed = _digest(_author_source(store, book_number)) != record["source_sha256"]
    if series is None:
        impact = "contradictory"
    else:
        current_nodes = {node["id"]: _digest(node) for node in series["candidate"].get("nodes", [])}
        impact = "clear"
        for node_id, fingerprint in record["series_nodes"].items():
            if node_id not in current_nodes:
                impact = "contradictory"
                break
            if current_nodes[node_id] != fingerprint:
                impact = "suspect"
    return {
        "freshness": "stale" if (series_changed or source_changed) else "ready",
        "series_changed": series_changed,
        "source_changed": source_changed,
        "semantic_impact": impact,
    }


def book_prepare(store: CanvasStore, book_number: int) -> dict:
    """Open a develop request for one Book, built on the current working Series architecture."""
    _check_number(book_number)
    with _FilesystemLock(store._path(".canvas.lock")):
        if _read(_book_root(store, book_number) / "current.json") is not None:
            raise ValueError(
                f"Book {book_number} already has a working architecture; revision is not available yet"
            )
        series = _candidate(store)
        if series is None or _current_candidate_freshness(store, series) != "ready":
            raise BeginnerConcurrencyError(
                "develop and complete the Series working architecture first; it must be current"
            )
        source = _author_source(store, book_number)
        if not source["book_source"]:
            raise ValueError(f"record Book {book_number}'s source as working items in group 'book-{book_number}'")
        questions = series["candidate"].get("open_questions", [])
        packet = {
            "schema": REQUEST_KIND,
            "operation": "develop",
            "book_number": book_number,
            "series_architecture": {
                "request_sha256": series["request_sha256"],
                "candidate_sha256": _digest(series["candidate"]),
                "candidate": series["candidate"],
                "open_questions": [
                    {"index": index, "text": text, "sha256": _text_digest(text)}
                    for index, text in enumerate(questions)
                ],
            },
            "author_source": source,
            "visible_source_ids": _visible_source_ids(source),
        }
        user = json.dumps(packet, ensure_ascii=False, sort_keys=True)
        settings = {
            "book_number": book_number,
            "series_request_sha256": series["request_sha256"],
            "source_sha256": _digest(source),
            "freshness_format": 1,
        }
        request = build_host_agent_request(
            candidate_id=f"book-{book_number}-" + _digest({"user": user})[:16],
            role=ROLE, system=_BOOK_SYSTEM, user=user, settings=settings,
        )
        base = _book_root(store, book_number)
        write_host_agent_request(base / "requests" / request.request_sha256 / "request.json", request)
        _atomic_json_write(base / "latest_request.json", {"request_sha256": request.request_sha256})
    return book_project(store, book_number)


def book_project(store: CanvasStore, book_number: int) -> dict:
    _check_number(book_number)
    base = _book_root(store, book_number)
    pointer = _read(base / "latest_request.json")
    record = _read(base / "current.json")
    pending = None
    if pointer and (record is None or record["request_sha256"] != pointer["request_sha256"]):
        pending = load_host_agent_request(base / "requests" / pointer["request_sha256"] / "request.json")
    if pending is not None:
        status = "awaiting_host_agent"
    elif record is None:
        status = "not_started"
    else:
        status = _freshness(store, book_number, record)["freshness"]
    return {
        "book_number": book_number,
        "status": status,
        "authority": "working_noncanonical",
        "request": pending.model_dump() if pending is not None else None,
        "request_sha256": record["request_sha256"] if record else None,
        "artifact": record["artifact"] if record else None,
    }


def book_complete(store: CanvasStore, book_number: int, payload: dict) -> dict:
    """Validate and persist a host-agent response to the pending Book request. Never accepts."""
    _check_number(book_number)
    with _FilesystemLock(store._path(".canvas.lock")):
        base = _book_root(store, book_number)
        pointer = _read(base / "latest_request.json")
        if not pointer:
            raise ValueError(f"no Book {book_number} architecture request exists")
        sha = pointer["request_sha256"]
        request = load_host_agent_request(base / "requests" / sha / "request.json")
        response = validate_host_agent_response(request, payload)
        prior = _read(base / "requests" / sha / "response.json")
        if prior:
            if prior != response.model_dump():
                raise BeginnerConcurrencyError("a different response already completed this Book request")
            return book_project(store, book_number)
        settings = request.settings
        if _series_changed(store, settings) or _source_changed(store, book_number, settings):
            write_host_agent_response(base / "requests" / sha / "stale_response.json", response)
            raise BeginnerConcurrencyError(
                "the Series architecture or the Book's source changed after this request; "
                "response retained as stale evidence"
            )
        packet = json.loads(request.user)
        artifact = WorkingBookArchitecture.model_validate_json(response.text)
        if artifact.book_number != book_number:
            raise ValueError("the artifact's book_number does not match the request")
        _check_references(
            artifact, packet["series_architecture"]["candidate"], set(packet["visible_source_ids"]),
        )
        write_host_agent_response(base / "requests" / sha / "response.json", response)
        series_nodes = {node["id"]: _digest(node) for node in packet["series_architecture"]["candidate"]["nodes"]}
        artifact_json = artifact.model_dump(mode="json")
        _atomic_json_write(base / "current.json", {
            "book_number": book_number,
            "request_sha256": sha,
            "series_request_sha256": settings["series_request_sha256"],
            "source_sha256": settings["source_sha256"],
            "series_nodes": {
                node_id: series_nodes[node_id] for node_id in sorted(_series_refs(artifact))
            },
            "content_sha256": _digest(artifact_json),
            "authority": "working_noncanonical",
            "artifact": artifact_json,
        })
    return book_project(store, book_number)


def book_resume(store: CanvasStore, book_number: int) -> dict:
    """Read-only recovery of one Book's working architecture in a fresh process."""
    _check_number(book_number)
    record = _read(_book_root(store, book_number) / "current.json")
    if record is None:
        return {"book_number": book_number, "status": "not_started", "authority": "working_noncanonical"}
    artifact = WorkingBookArchitecture.model_validate_json(json.dumps(record["artifact"]))
    series = _candidate(store)
    series_nodes = {node["id"]: node for node in (series or {}).get("candidate", {}).get("nodes", [])}
    questions = (series or {}).get("candidate", {}).get("open_questions", [])
    constraints = []
    for node_id in sorted(_series_refs(artifact)):
        node = series_nodes.get(node_id)
        constraints.append({
            "id": node_id,
            "status": "present" if node else "missing",
            "title": node.get("title") if node else None,
            "category": node.get("category") if node else None,
            "summary": node.get("summary") if node else None,
        })
    source = _author_source(store, book_number)
    vision = source["story_vision"][0]["content"] if source["story_vision"] else ""
    packet = {
        "identity": {
            "book_number": book_number,
            "title": artifact.title,
            "question": artifact.function.question,
            "pressure": artifact.function.pressure,
        },
        "author_fixed_context": {
            "story_vision_excerpt": vision[:600],
            "creative_intentions": [
                {"id": item["id"], "title": item["title"], "status": item["status"]}
                for item in source["creative_intentions"]
            ],
        },
        "series_constraints": constraints,
        "exports": {
            "series_consequences": [
                {"id": item.id, "kind": item.kind, "text": item.text}
                for item in artifact.series_consequences
            ],
            "later_possibilities": [
                {"id": item.id, "kind": item.kind, "text": item.text}
                for item in artifact.later_possibilities
            ],
            "assumptions": [
                {"id": item.id, "provenance": item.provenance, "text": item.text, "reversal": item.reversal}
                for item in artifact.assumptions
            ],
            "alternatives": [
                {"id": item.id, "title": item.title, "status": item.status}
                for item in artifact.alternatives
            ],
        },
        "open_author_decisions": [
            {
                "id": decision.id,
                "series_question_index": decision.series_question_index,
                "current_text": questions[decision.series_question_index]
                if decision.series_question_index < len(questions) else None,
                "reference_stale": (
                    decision.series_question_index >= len(questions)
                    or _text_digest(questions[decision.series_question_index]) != decision.series_question_sha256
                ),
            }
            for decision in artifact.open_author_decisions
        ],
        "unresolved": [{"id": item.id, "text": item.text} for item in artifact.unresolved],
        "revision_identity": {
            "book_request_sha256": record["request_sha256"],
            "series_request_sha256": record["series_request_sha256"],
            "source_sha256": record["source_sha256"],
            "content_sha256": record["content_sha256"],
        },
    }
    return {
        "book_number": book_number,
        "authority": "working_noncanonical",
        **_freshness(store, book_number, record),
        "packet": packet,
        "artifact": record["artifact"],
    }


# --- CLI --------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Auteur working Book architecture (noncanonical)")
    parser.add_argument("--project", required=True, help="Local Auteur project root")
    parser.add_argument("--canvas", required=True, help="Canvas id")
    actions = parser.add_subparsers(dest="action", required=True)
    prepare = actions.add_parser("book-prepare", help="Open a develop request for one Book")
    prepare.add_argument("--book", type=int, required=True)
    complete = actions.add_parser("book-complete-file", help="Validate and store the host agent's Book JSON")
    complete.add_argument("--book", type=int, required=True)
    complete.add_argument("--candidate", required=True, help="Path to Book architecture JSON")
    resume = actions.add_parser("book-resume", help="Read-only re-entry for one Book")
    resume.add_argument("--book", type=int, required=True)
    args = parser.parse_args(argv)
    store = CanvasStore(Path(args.project), args.canvas)
    try:
        if args.action == "book-prepare":
            result = book_prepare(store, args.book)
        elif args.action == "book-complete-file":
            pending = book_project(store, args.book)
            if pending["status"] != "awaiting_host_agent" or not pending["request"]:
                raise ValueError("no pending Book architecture request to complete")
            request = HostAgentRequest(**pending["request"])
            text = Path(args.candidate).read_text(encoding="utf-8")
            response = build_host_agent_response(request, text)
            result = book_complete(store, args.book, response.model_dump())
        else:
            result = book_resume(store, args.book)
    except (ValueError, BeginnerConcurrencyError) as exc:
        print(json.dumps({"result": "rejected", "error": str(exc)}, indent=2, ensure_ascii=False))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


_BOOK_SYSTEM = """You are developing ONE Book's working architecture for a long-form Series. Output exactly one JSON object, schema_version 1, and nothing else. This is a noncanonical proposal: never accept, never write prose or chapters, never create character identities, character commitments or relationship states.

Top level: schema_version, book_number, title, function, inherited, engines, agents, choice, local_resolution, series_consequences, later_possibilities, assumptions, alternatives, unresolved, open_author_decisions, typed_edges.
Every element: id (lowercase, starts with a letter), provenance, text (the substance, as long as it needs to be, under 8000 characters), refs.
- provenance: derived (you cite the refs it rests on), agent_proposed (your own working inference), hypothetical (alternatives only), unresolved (information missing from the source). Never author_fixed, accepted or unlabelled. If the source gives no attribution for an item, use unresolved, never a guess.
- refs: {kind, id}. kind series_node (an id in series_architecture.candidate.nodes), book_element (an id you define in this object), source_item (an id listed in visible_source_ids). Every ref must resolve.
- function: question, pressure, and at least one series_node ref.
- engines: condition, consequence, changed_state (required); choice, new_possibility (optional).
- agents: motives, institutions and constraints. Give a proper name only when a visible source item states it; then name_source must be a source_item or series_node ref. Never invent a name.
- choice: two to six options (each an element), chosen_option_id, costs_kept_visible (one or more elements), transformation (an element).
- local_resolution: items with closure true or false. series_consequences: items with kind changes, preserves or complicates. later_possibilities: items with kind enabled or closed.
- assumptions: agent_proposed assumptions MUST state a reversal condition. If you cannot state one, mark the assumption unresolved with reversal null.
- alternatives: title, status "hypothetical", rationale, provenance "hypothetical".
- unresolved: missing information and author-reserved decisions.
- open_author_decisions: series_question_index and series_question_sha256, copied exactly from series_architecture.open_questions. Use them only for a Series open question this Book must leave to the author.
- typed_edges: {id, source (a Book element id), target (a ref), dependency (sets_up, pays_off, depends_on, pressures, contradicts or transforms), function}.
Preserve the source's causal, motivational and prospective substance; do not compress it into labels. Do not fabricate provenance, reversal conditions or references to make the object valid. Cite what the source says and mark what it does not say."""


if __name__ == "__main__":
    raise SystemExit(main())
