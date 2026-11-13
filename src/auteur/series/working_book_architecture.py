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
import re
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
REVISION_KIND = "auteur_working_book_revision_request_v1"
ROLE = "working_book_architecture"
STORY_VISION_ID = "story-vision"

Provenance = Literal[
    "author_fixed", "derived", "agent_proposed", "hypothetical", "unresolved", "accepted", "unlabelled",
]
AGENT_PROVENANCE = frozenset({"derived", "agent_proposed", "hypothetical", "unresolved"})
Attribution = Literal["derived", "agent_proposed", "unattributed"]
EpistemicStatus = Literal["asserted", "hypothetical", "unresolved", "conditional", "rejected"]
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
    """One Book element. Two forms are readable; an element uses only one of them.

    Legacy form (Book records written before this correction): `provenance` alone. Its `unresolved`
    value mixed unknown attribution, genuine open questions and assumptions without a reversal, so
    legacy `unresolved` stays ambiguous and is never reinterpreted.

    Explicit form: `attribution` (what supports the statement) and `epistemic_status` (where the statement
    stands in the working proposal). Commitment authority is projected from these and from the author
    decision list. It is never stored, so no element can carry an authority claim of its own.
    """
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=_ID)
    text: str = Field(min_length=1, max_length=_MAX_TEXT)
    refs: list[Ref] = Field(default_factory=list, max_length=24)
    provenance: Provenance | None = None
    attribution: Attribution | None = None
    epistemic_status: EpistemicStatus | None = None
    interpretation: str | None = Field(default=None, min_length=1, max_length=2000)

    @model_validator(mode="after")
    def one_form_only(self) -> "BookElement":
        if self.provenance is not None:
            if self.attribution is not None or self.epistemic_status is not None or self.interpretation is not None:
                raise ValueError(
                    f"element {self.id!r} mixes the legacy provenance label with explicit attribution or status"
                )
            if self.provenance not in AGENT_PROVENANCE:
                raise ValueError(
                    f"provenance {self.provenance!r} cannot be written by an agent; "
                    f"use one of {sorted(AGENT_PROVENANCE)}"
                )
            return self
        if self.attribution is None or self.epistemic_status is None:
            raise ValueError(f"element {self.id!r} needs attribution and epistemic_status")
        if self.attribution == "derived" and not self._has_source_reference():
            raise ValueError(f"source-derived element {self.id!r} must cite a source reference")
        if self.interpretation is not None and self.attribution != "derived":
            raise ValueError(
                f"element {self.id!r}: an interpretive contribution is recorded only on a source-derived element"
            )
        return self

    def _has_source_reference(self) -> bool:
        return bool(self.refs)


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
    """A provisional assumption. An unknown reversal is recorded as unknown; it is not an open author question."""
    reversal: str | None = Field(default=None, min_length=1, max_length=1200)

    @model_validator(mode="after")
    def legacy_agent_assumptions_state_a_reversal(self) -> "AssumptionElement":
        # Rule of the legacy form only, kept so historical records keep their meaning.
        if self.provenance == "agent_proposed" and not self.reversal:
            raise ValueError(f"agent-proposed assumption {self.id!r} must state a reversal condition")
        return self


class AlternativeElement(BookElement):
    title: str = Field(min_length=1, max_length=160)
    status: Literal["hypothetical"]
    rationale: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def alternatives_are_hypothetical(self) -> "AlternativeElement":
        if self.provenance is not None and self.provenance != "hypothetical":
            raise ValueError(f"alternative {self.id!r} must carry hypothetical provenance")
        if self.provenance is None and self.epistemic_status not in ("hypothetical", "rejected"):
            raise ValueError(f"alternative {self.id!r} must have epistemic_status hypothetical or rejected")
        return self


class DecisionElement(BookElement):
    """An author decision, bound to one Series open question by index and text hash. It stays unresolved."""
    series_question_index: int = Field(ge=0, le=63)
    series_question_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    def _has_source_reference(self) -> bool:
        return True  # the binding to the Series open question is the source reference

    @model_validator(mode="after")
    def decisions_stay_unresolved(self) -> "DecisionElement":
        if self.provenance is None and (self.epistemic_status != "unresolved" or self.attribution != "derived"):
            raise ValueError(f"author decision {self.id!r} must be derived from its Series question and unresolved")
        return self


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
    return [element for _collection, element in _labelled_elements(artifact)]


def _labelled_elements(artifact: WorkingBookArchitecture) -> list[tuple[str, BookElement]]:
    """Every element with its collection name, including nested choice parts. Typed edges are not elements."""
    found: list[tuple[str, BookElement]] = [("function", artifact.function)]
    found += [("inherited", item) for item in artifact.inherited]
    found += [("engines", item) for item in artifact.engines]
    found += [("agents", item) for item in artifact.agents]
    found += [("choice", artifact.choice)]
    found += [("choice.options", item) for item in artifact.choice.options]
    found += [("choice.costs_kept_visible", item) for item in artifact.choice.costs_kept_visible]
    found += [("choice.transformation", artifact.choice.transformation)]
    found += [("local_resolution", item) for item in artifact.local_resolution]
    found += [("series_consequences", item) for item in artifact.series_consequences]
    found += [("later_possibilities", item) for item in artifact.later_possibilities]
    found += [("assumptions", item) for item in artifact.assumptions]
    found += [("alternatives", item) for item in artifact.alternatives]
    found += [("unresolved", item) for item in artifact.unresolved]
    found += [("open_author_decisions", item) for item in artifact.open_author_decisions]
    return found


# Legacy `provenance` values, read as what they can establish. `unresolved` is ambiguous on purpose.
_LEGACY_READING = {
    "derived": ("derived", "asserted"),
    "agent_proposed": ("agent_proposed", "asserted"),
    "hypothetical": ("agent_proposed", "hypothetical"),
    "unresolved": ("unknown_legacy", "unknown_legacy"),
}


def project_element(element: BookElement, *, collection: str, decision_ids: set[str]) -> dict:
    """Read one element's attribution, working status and commitment authority without storing authority.

    Commitment authority is never `author_fixed` or `accepted`: Book operations cannot produce either.
    """
    if element.provenance is not None:
        attribution, status = _LEGACY_READING[element.provenance]
        form = "legacy"
    else:
        attribution, status = element.attribution, element.epistemic_status
        form = "explicit"
    if status == "rejected":
        authority = "withdrawn"
    elif element.id in decision_ids:
        authority = "author_reserved"
    elif status == "hypothetical":
        authority = "not_adopted"
    elif status in ("unresolved", "unknown_legacy"):
        authority = "undecided"
    elif attribution == "unattributed":
        authority = "not_established"
    elif attribution == "unknown_legacy":
        authority = "undecided"
    else:
        authority = "agent_working"
    view = {
        "id": element.id,
        "collection": collection,
        "form": form,
        "attribution": attribution,
        "epistemic_status": status,
        "commitment_authority": authority,
        "ambiguous": status == "unknown_legacy",
    }
    if element.interpretation is not None:
        view["interpretation"] = element.interpretation
    if isinstance(element, AssumptionElement):
        view["provisional"] = True
        view["reversal_status"] = "stated" if element.reversal else "unknown"
    return view


def _projected(element: BookElement, collection: str, decision_ids: set[str]) -> dict:
    view = project_element(element, collection=collection, decision_ids=decision_ids)
    view.pop("collection")
    return view


def project_artifact(artifact: WorkingBookArchitecture) -> dict:
    decision_ids = {item.id for item in artifact.open_author_decisions}
    views = [
        project_element(element, collection=collection, decision_ids=decision_ids)
        for collection, element in _labelled_elements(artifact)
    ]
    summary: dict[str, dict[str, int]] = {"attribution": {}, "epistemic_status": {}, "commitment_authority": {}}
    for view in views:
        for field in summary:
            summary[field][view[field]] = summary[field].get(view[field], 0) + 1
    summary["form"] = {
        "legacy": sum(1 for view in views if view["form"] == "legacy"),
        "explicit": sum(1 for view in views if view["form"] == "explicit"),
        "legacy_ambiguous": sum(1 for view in views if view["ambiguous"]),
    }
    return {"elements": views, "summary": summary}


def _check_semantics(artifact: WorkingBookArchitecture) -> None:
    """Explicit-form rules that keep genuine questions, author decisions and assumptions apart."""
    decision_ids = {item.id for item in artifact.open_author_decisions}
    assumption_ids = {item.id for item in artifact.assumptions}
    problems: list[str] = []
    for _collection, element in _labelled_elements(artifact):
        if element.provenance is not None:
            continue
        if element.epistemic_status == "asserted":
            for ref in element.refs:
                if ref.kind == "book_element" and ref.id in decision_ids:
                    problems.append(
                        f"{element.id}: asserts a claim that depends on author decision {ref.id}; "
                        "it must be conditional on that decision"
                    )
        if element.epistemic_status == "conditional":
            conditions = [
                ref.id for ref in element.refs
                if ref.kind == "book_element" and (ref.id in assumption_ids or ref.id in decision_ids)
            ]
            if not conditions:
                problems.append(
                    f"{element.id}: conditional status needs a reference to an assumption or author decision"
                )
    for item in artifact.unresolved:
        if item.provenance is None and item.epistemic_status != "unresolved":
            problems.append(f"{item.id}: an item listed as unresolved must have epistemic_status unresolved")
    if problems:
        raise ValueError("; ".join(problems[:20]))


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


def book_prepare(
    store: CanvasStore, book_number: int, *, instruction: str | None = None,
    targets: tuple[str, ...] = (), holistic: bool = False,
) -> dict:
    """Develop a Book when none exists. With an instruction, prepare a reviewed revision of the existing one."""
    _check_number(book_number)
    if instruction is None:
        return _prepare_develop(store, book_number)
    return _prepare_revision(store, book_number, instruction, tuple(targets), holistic)


def _prepare_develop(store: CanvasStore, book_number: int) -> dict:
    """Open a develop request for one Book, built on the current working Series architecture."""
    with _FilesystemLock(store._path(".canvas.lock")):
        if _read(_book_root(store, book_number) / "current.json") is not None:
            raise ValueError(
                f"Book {book_number} already has a working architecture; prepare a revision with --instruction and --target"
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
    review = None
    if pointer and (record is None or record["request_sha256"] != pointer["request_sha256"]):
        sha = pointer["request_sha256"]
        pending = load_host_agent_request(base / "requests" / sha / "request.json")
        review = _read(base / "requests" / sha / "review.json")
    if pending is not None and review is not None:
        status = "review_ready" if review["applicable"] else "review_blocked"
    elif pending is not None:
        status = "awaiting_host_agent"
    elif record is None:
        status = "not_started"
    else:
        status = _freshness(store, book_number, record)["freshness"]
    return {
        "book_number": book_number,
        "status": status,
        "authority": "working_noncanonical",
        "request": pending.model_dump() if pending is not None and review is None else None,
        "request_sha256": record["request_sha256"] if record else None,
        "pending_request_sha256": pending.request_sha256 if pending is not None else None,
        "review": {key: value for key, value in review.items() if key != "candidate"} if review else None,
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
        operation = request.settings.get("operation", "develop")
        if operation == "revise":
            return _complete_revision(store, book_number, base, sha, request, response)
        if operation != "develop":
            raise ValueError(f"a {operation} request does not accept a candidate")
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
        _check_semantics(artifact)
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
            # The Book's own source, verbatim, so recovery does not depend on the canvas item still existing.
            "source_items": packet["author_source"]["book_source"],
        })
    return book_project(store, book_number)


def book_resume(store: CanvasStore, book_number: int) -> dict:
    """Read-only recovery of one Book's working architecture in a fresh process."""
    _check_number(book_number)
    record = _read(_book_root(store, book_number) / "current.json")
    if record is None:
        return {"book_number": book_number, "status": "not_started", "authority": "working_noncanonical"}
    artifact = WorkingBookArchitecture.model_validate_json(json.dumps(record["artifact"]))
    decision_ids = {item.id for item in artifact.open_author_decisions}
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
                {**_projected(item, "assumptions", decision_ids), "text": item.text, "reversal": item.reversal}
                for item in artifact.assumptions
            ],
            "alternatives": [
                {**_projected(item, "alternatives", decision_ids), "title": item.title}
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
        "unresolved": [
            {**_projected(item, "unresolved", decision_ids), "text": item.text} for item in artifact.unresolved
        ],
        "semantics": project_artifact(artifact)["summary"],
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
        "verbatim_source": record.get("source_items", []),
        "revision": {
            "number": record.get("revision_number", 0),
            "lineage": record.get("lineage", []),
            "applied_review": record.get("applied_review"),
        },
    }


# --- CLI --------------------------------------------------------------------------------

_NESTED_FIELDS = frozenset({"options", "costs_kept_visible", "transformation"})
_CHANGE_FIELDS = ("attribution", "epistemic_status", "provenance", "reversal", "interpretation")
_TOP_LEVEL = ("title", "book_number", "schema_version")


def _index_elements(artifact: WorkingBookArchitecture) -> dict[str, dict]:
    """Identity and content of every element and typed edge.

    A choice block's own hash excludes its parts, which are indexed on their own, so a change to one
    option is attributed to that option. Each entry keeps the parsed element for reference reads.
    """
    index: dict[str, dict] = {}
    for collection, element in _labelled_elements(artifact):
        exclude = _NESTED_FIELDS if isinstance(element, ChoiceBlock) else None
        own = element.model_dump(mode="json", exclude=exclude)
        index[element.id] = {"collection": collection, "own": own, "hash": _digest(own),
                             "element": element, "edge": None}
    for edge in artifact.typed_edges:
        own = edge.model_dump(mode="json")
        index[edge.id] = {"collection": "typed_edges", "own": own, "hash": _digest(own),
                          "element": None, "edge": edge}
    return index


def _entry_refs(entry: dict) -> list[Ref]:
    element = entry["element"]
    if element is None:
        edge = entry["edge"]
        return [Ref(kind="book_element", id=edge.source), edge.target]
    refs = list(element.refs)
    if isinstance(element, AgentElement) and element.name_source is not None:
        refs.append(element.name_source)
    return refs


def _references_of(index: dict[str, dict], identifier: str) -> set[str]:
    """Book elements that this element references, explicitly and mechanically."""
    return {ref.id for ref in _entry_refs(index[identifier]) if ref.kind == "book_element"}


def _series_refs_of(index: dict[str, dict], identifier: str) -> set[str]:
    return {ref.id for ref in _entry_refs(index[identifier]) if ref.kind == "series_node"}


def _dependents_of(index: dict[str, dict], targets: set[str]) -> set[str]:
    """Elements that reference a target by an explicit reference or a typed edge. Nothing is inferred."""
    return {
        identifier for identifier in index
        if identifier not in targets and _references_of(index, identifier) & targets
    }


def _compare(base_index: dict, cand_index: dict, allowed: set[str] | None) -> tuple[dict, list[str], list[dict]]:
    base_ids, cand_ids = set(base_index), set(cand_index)
    both = base_ids & cand_ids
    changed = sorted(
        identifier for identifier in both
        if base_index[identifier]["hash"] != cand_index[identifier]["hash"]
        or base_index[identifier]["collection"] != cand_index[identifier]["collection"]
    )
    preserved = sorted(identifier for identifier in both if identifier not in set(changed))
    changes: dict[str, list[dict]] = {"added": [], "changed": [], "removed": []}
    unexpected: list[dict] = []

    for identifier in sorted(cand_ids - base_ids):
        refs = _references_of(cand_index, identifier)
        changes["added"].append({"id": identifier, "collection": cand_index[identifier]["collection"],
                                 "references": sorted(refs)})
        if allowed is not None and not (refs & allowed):
            unexpected.append({"id": identifier, "change": "added",
                               "reason": "adds an element that references no permitted element"})

    for identifier in sorted(base_ids - cand_ids):
        changes["removed"].append({"id": identifier, "collection": base_index[identifier]["collection"]})
        if allowed is not None and identifier not in allowed:
            unexpected.append({"id": identifier, "change": "removed", "reason": "not a permitted element"})

    for identifier in changed:
        before, after = base_index[identifier]["own"], cand_index[identifier]["own"]
        fields = sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))
        changes["changed"].append({
            "id": identifier,
            "collection": cand_index[identifier]["collection"],
            "classification": _classify_change(before, after),
            "fields_changed": fields,
            "before_text": before.get("text") if "text" in fields else None,
            "after_text": after.get("text") if "text" in fields else None,
        })
        if allowed is not None and identifier not in allowed:
            unexpected.append({"id": identifier, "change": "changed", "reason": "not a permitted element"})
    return changes, preserved, unexpected


def _classify_change(before: dict, after: dict) -> str:
    """Interpretive means the words changed. Representation means only how the statement is labelled changed."""
    if before.get("text") != after.get("text") or before.get("interpretation") != after.get("interpretation"):
        return "interpretive"
    if any(before.get(field) != after.get(field) for field in _CHANGE_FIELDS):
        if before.get("provenance") is not None and after.get("provenance") is None:
            return "representation_reclassified_from_legacy"
        return "representation"
    return "mechanical"


def _enforce_revision_rules(base_index: dict, cand_index: dict) -> None:
    """Rules a revision cannot break whatever its scope: explicit form for changes, and fixed questions."""
    problems: list[str] = []
    for identifier, entry in cand_index.items():
        base_entry = base_index.get(identifier)
        if base_entry is not None and base_entry["hash"] == entry["hash"] and base_entry["collection"] == entry["collection"]:
            continue
        element = entry["element"]
        if element is not None and element.provenance is not None:
            problems.append(f"{identifier}: a new or changed element must use explicit attribution and epistemic_status")
    for identifier, entry in base_index.items():
        base_element = entry["element"]
        if base_element is None:
            continue
        is_decision = isinstance(base_element, DecisionElement)
        explicit_unresolved = base_element.provenance is None and base_element.epistemic_status == "unresolved"
        if not (is_decision or explicit_unresolved):
            continue
        cand_element = cand_index.get(identifier, {}).get("element")
        if cand_element is None:
            problems.append(f"{identifier}: an open question or author decision cannot be removed by a revision")
            continue
        if cand_element.provenance is None and cand_element.epistemic_status != "unresolved":
            problems.append(f"{identifier}: an unresolved question cannot be settled by a working revision")
        if is_decision and (
            cand_element.series_question_index != base_element.series_question_index
            or cand_element.series_question_sha256 != base_element.series_question_sha256
        ):
            problems.append(f"{identifier}: an author decision's Series binding is fixed")
    if problems:
        raise ValueError("; ".join(problems[:20]))


def _build_review(
    *, baseline: WorkingBookArchitecture, candidate: WorkingBookArchitecture, base_index: dict,
    cand_index: dict, settings: dict, instruction: str, series_node_ids: set[str], request_sha256: str,
    withdrawal: dict | None = None,
) -> dict:
    allowed = None if settings["mode"] == "holistic" else set(settings["allowed_ids"])
    changes, preserved, unexpected = _compare(base_index, cand_index, allowed)
    if allowed is not None:
        for field in _TOP_LEVEL:
            if getattr(baseline, field) != getattr(candidate, field):
                unexpected.append({"id": field, "change": "changed",
                                   "reason": "top-level fields change only in a holistic revision"})
    changed_ids = {entry["id"] for entry in changes["changed"]}
    added_ids = {entry["id"] for entry in changes["added"]}
    removed_ids = {entry["id"] for entry in changes["removed"]}
    affected = changed_ids | removed_ids

    consequence_candidates = []
    implications = []
    for identifier in preserved:
        via = sorted(_references_of(cand_index, identifier) & affected)
        if via:
            consequence_candidates.append({
                "id": identifier, "via": via, "classification": "mechanical_link", "basis": "explicit_book_reference",
                "reason": "unchanged element references an element this revision changed; inspect whether it still holds",
            })
    for identifier in sorted(changed_ids | added_ids):
        for target in sorted(_references_of(cand_index, identifier)):
            if target in set(preserved):
                implications.append({"from": identifier, "to": target, "relation": "reference",
                                     "classification": "mechanical_link", "basis": "explicit_book_reference"})

    touched = affected | added_ids | {entry["id"] for entry in consequence_candidates}
    series_map: dict[str, set[str]] = {}
    for identifier in touched:
        refs = _series_refs_of(cand_index, identifier) if identifier in cand_index else set()
        refs |= _series_refs_of(base_index, identifier) if identifier in base_index else set()
        for node in refs:
            series_map.setdefault(node, set()).add(identifier)
    series_consequences = [
        {"series_node_id": node, "cited_by": sorted(ids), "exists_in_series": node in series_node_ids,
         "basis": "explicit_series_reference", "series_state": "unchanged",
         "status": "inspection_recommended" if node in series_node_ids else "missing_in_series"}
        for node, ids in sorted(series_map.items())
    ]

    decision_ids = {identifier for identifier, entry in base_index.items()
                    if isinstance(entry["element"], DecisionElement)}
    decision_map: dict[str, set[str]] = {}
    for identifier in touched | removed_ids:
        refs = _references_of(cand_index, identifier) if identifier in cand_index else set()
        refs |= _references_of(base_index, identifier) if identifier in base_index else set()
        for decision in (refs | ({identifier} if identifier in decision_ids else set())) & decision_ids:
            decision_map.setdefault(decision, set()).add(identifier)
    author_decisions = [
        {"decision_id": decision, "touched_by": sorted(ids), "status": "remains_author_reserved"}
        for decision, ids in sorted(decision_map.items())
    ]

    base_views = {view["id"]: view for view in project_artifact(baseline)["elements"]}
    cand_views = {view["id"]: view for view in project_artifact(candidate)["elements"]}
    authority_changes = [
        {"id": identifier, "before": base_views[identifier]["commitment_authority"],
         "after": cand_views[identifier]["commitment_authority"]}
        for identifier in sorted(changed_ids | added_ids)
        if identifier in base_views and identifier in cand_views
        and base_views[identifier]["commitment_authority"] != cand_views[identifier]["commitment_authority"]
    ]

    edge_sources = {edge.source for edge in candidate.typed_edges} | {edge.target.id for edge in candidate.typed_edges}
    unresolved_effects = [
        {"id": entry["id"],
         "note": "interpretive change with no recorded typed dependency; the representation does not establish its consequences"}
        for entry in changes["changed"]
        if entry["classification"] == "interpretive"
        and not _references_of(cand_index, entry["id"]) and entry["id"] not in edge_sources
    ]
    return {
        "authority": "working_revision_review_not_acceptance",
        "request_sha256": request_sha256,
        "book_number": candidate.book_number,
        "baseline": {
            "request_sha256": settings["baseline_request_sha256"],
            "content_sha256": settings["baseline_content_sha256"],
            "revision_number": settings["baseline_revision_number"],
        },
        "revision_number": settings["baseline_revision_number"] + 1,
        "mode": settings["mode"],
        "instruction": instruction,
        "permitted_ids": settings["allowed_ids"],
        "changes": changes,
        "preserved": {"ids": preserved, "count": len(preserved)},
        "unexpected_changes": unexpected,
        "dependency_implications": implications,
        "consequence_candidates": consequence_candidates,
        "series_consequences": series_consequences,
        "author_decisions": author_decisions,
        "authority_changes": authority_changes,
        "unresolved_effects": unresolved_effects,
        "withdrawal": withdrawal,
        "applicable": not unexpected,
        "applied": False,
        "note": ("Mechanical references are dependencies to inspect, not evidence of a narrative contradiction. "
                 "This is a working proposal. It changes no Series, accepted, or intention state."),
        "candidate": candidate.model_dump(mode="json"),
    }


def _revision_packet(
    artifact: WorkingBookArchitecture, index: dict, book_number: int, current: dict, series: dict,
    source: dict, targets: set[str], dependents: set[str], holistic: bool, instruction: str,
) -> dict:
    in_scope = set(index) if holistic else targets | dependents
    views = {view["id"]: view for view in project_artifact(artifact)["elements"]}

    def scoped_record(identifier: str) -> dict:
        entry = index[identifier]
        full = entry["element"].model_dump(mode="json") if entry["element"] is not None else entry["own"]
        return {"id": identifier, "collection": entry["collection"], "content_sha256": entry["hash"], "record": full}

    manifest = [] if holistic else [
        {"id": identifier, "collection": index[identifier]["collection"],
         "content_sha256": index[identifier]["hash"],
         "attribution": views[identifier]["attribution"] if identifier in views else None,
         "epistemic_status": views[identifier]["epistemic_status"] if identifier in views else None}
        for identifier in sorted(index) if identifier not in in_scope
    ]
    nodes = {node["id"]: node for node in series["candidate"].get("nodes", [])}
    referenced = sorted({node for identifier in in_scope for node in _series_refs_of(index, identifier)})
    questions = series["candidate"].get("open_questions", [])
    return {
        "schema": REVISION_KIND,
        "operation": "revise",
        "book_number": book_number,
        "baseline": {
            "request_sha256": current["request_sha256"],
            "content_sha256": current["content_sha256"],
            "revision_number": current.get("revision_number", 0),
        },
        "instruction": instruction,
        "mode": "holistic" if holistic else "targeted",
        "permitted_ids": None if holistic else sorted(in_scope),
        "scoped_elements": [scoped_record(identifier) for identifier in sorted(in_scope)],
        "unchanged_elements": manifest,
        "governing": {
            "function": {"question": artifact.function.question, "pressure": artifact.function.pressure},
            "book_source": source["book_source"],
            "story_vision": source["story_vision"],
            "creative_intentions": source["creative_intentions"],
            "assumptions": [item.model_dump(mode="json") for item in artifact.assumptions],
            "alternatives": [item.model_dump(mode="json") for item in artifact.alternatives],
        },
        "series_architecture": {
            "request_sha256": series["request_sha256"],
            "candidate_sha256": _digest(series["candidate"]),
            "referenced_nodes": [nodes[node] for node in referenced if node in nodes],
            "node_index": [{"id": node["id"], "category": node["category"], "title": node["title"]}
                           for node in series["candidate"].get("nodes", [])],
            "open_questions": [{"index": i, "text": text, "sha256": _text_digest(text)}
                               for i, text in enumerate(questions)],
        },
        "visible_source_ids": _visible_source_ids(source),
    }


def _prepare_revision(
    store: CanvasStore, book_number: int, instruction: str, targets: tuple[str, ...], holistic: bool,
) -> dict:
    if not instruction.strip():
        raise ValueError("a revision needs a non-empty instruction")
    if len(instruction) > 4000:
        raise ValueError("revision instruction must be under 4000 characters")
    if holistic and targets:
        raise ValueError("choose either --target elements or --holistic, not both")
    if not holistic and not targets:
        raise ValueError("name the elements to revise with --target, or use --holistic")
    with _FilesystemLock(store._path(".canvas.lock")):
        base = _book_root(store, book_number)
        current = _read(base / "current.json")
        if current is None:
            raise ValueError(f"Book {book_number} has no working architecture to revise; develop it first")
        artifact = WorkingBookArchitecture.model_validate_json(json.dumps(current["artifact"]))
        index = _index_elements(artifact)
        unknown = sorted(identifier for identifier in targets if identifier not in index)
        if unknown:
            raise ValueError(f"unknown target elements: {', '.join(unknown)}")
        target_set = set(targets)
        dependents = set() if holistic else _dependents_of(index, target_set)
        series = _candidate(store)
        if series is None or _current_candidate_freshness(store, series) != "ready":
            raise BeginnerConcurrencyError("the Series working architecture must be current before a Book revision")
        source = _author_source(store, book_number)
        packet = _revision_packet(artifact, index, book_number, current, series, source,
                                  target_set, dependents, holistic, instruction)
        user = json.dumps(packet, ensure_ascii=False, sort_keys=True)
        settings = {
            "book_number": book_number,
            "operation": "revise",
            "baseline_request_sha256": current["request_sha256"],
            "baseline_content_sha256": current["content_sha256"],
            "baseline_revision_number": current.get("revision_number", 0),
            "series_request_sha256": series["request_sha256"],
            "source_sha256": _digest(source),
            "mode": "holistic" if holistic else "targeted",
            "targets": sorted(target_set),
            "dependents": sorted(dependents),
            "allowed_ids": None if holistic else sorted(target_set | dependents),
            "freshness_format": 2,
        }
        request = build_host_agent_request(
            candidate_id=f"book-{book_number}-rev{settings['baseline_revision_number'] + 1}-"
                         + _digest({"user": user})[:16],
            role=ROLE, system=_BOOK_REVISION_SYSTEM, user=user, settings=settings,
        )
        write_host_agent_request(base / "requests" / request.request_sha256 / "request.json", request)
        _atomic_json_write(base / "latest_request.json", {"request_sha256": request.request_sha256})
    return book_project(store, book_number)


def _series_view(packet: dict) -> dict:
    """The Series facts a revision was built on, as reference checks need them: node ids and question texts."""
    series = packet["series_architecture"]
    return {"nodes": series["node_index"], "open_questions": [item["text"] for item in series["open_questions"]]}


def _complete_revision(
    store: CanvasStore, book_number: int, base: Path, sha: str,
    request: HostAgentRequest, response: Any,
) -> dict:
    """Store a reviewed proposal. Never replaces current.json; only book_apply_review does that."""
    settings = request.settings
    current = _read(base / "current.json")
    if current is None or current["request_sha256"] != settings["baseline_request_sha256"]:
        write_host_agent_response(base / "requests" / sha / "stale_response.json", response)
        raise BeginnerConcurrencyError(
            "the working Book changed after this revision was prepared; response retained as stale evidence"
        )
    if _series_changed(store, settings) or _source_changed(store, book_number, settings):
        write_host_agent_response(base / "requests" / sha / "stale_response.json", response)
        raise BeginnerConcurrencyError(
            "the Series architecture or the Book's source changed after this request; "
            "response retained as stale evidence"
        )
    packet = json.loads(request.user)
    candidate = WorkingBookArchitecture.model_validate_json(response.text)
    if candidate.book_number != book_number:
        raise ValueError("the artifact's book_number does not match the request")
    baseline = WorkingBookArchitecture.model_validate_json(json.dumps(current["artifact"]))
    series_view = _series_view(packet)
    _check_references(candidate, series_view, set(packet["visible_source_ids"]))
    _check_semantics(candidate)
    base_index = _index_elements(baseline)
    cand_index = _index_elements(candidate)
    _enforce_revision_rules(base_index, cand_index)
    series_node_ids = {node["id"] for node in series_view["nodes"]}
    review = _build_review(
        baseline=baseline, candidate=candidate, base_index=base_index, cand_index=cand_index,
        settings=settings, instruction=packet["instruction"], series_node_ids=series_node_ids,
        request_sha256=sha,
    )
    write_host_agent_response(base / "requests" / sha / "response.json", response)
    _atomic_json_write(base / "requests" / sha / "review.json", review)
    return book_project(store, book_number)


def _set_epistemic_status(node: Any, identifier: str, status: str) -> bool:
    """Set the explicit status on the one element with this id, wherever it sits in the record."""
    if isinstance(node, dict):
        if node.get("id") == identifier and "epistemic_status" in node:
            node["epistemic_status"] = status
            return True
        return any(_set_epistemic_status(value, identifier, status) for value in node.values())
    if isinstance(node, list):
        return any(_set_epistemic_status(value, identifier, status) for value in node)
    return False


def book_withdraw(store: CanvasStore, book_number: int, element_id: str, rationale: str) -> dict:
    """Propose a working withdrawal. It is a reviewed revision: nothing changes until it is applied."""
    _check_number(book_number)
    if not rationale.strip() or len(rationale) > 2000:
        raise ValueError("a withdrawal needs a rationale under 2000 characters")
    with _FilesystemLock(store._path(".canvas.lock")):
        base = _book_root(store, book_number)
        current = _read(base / "current.json")
        if current is None:
            raise ValueError(f"Book {book_number} has no working architecture to withdraw from")
        artifact = WorkingBookArchitecture.model_validate_json(json.dumps(current["artifact"]))
        index = _index_elements(artifact)
        if element_id not in index:
            raise ValueError(f"unknown element {element_id!r}")
        entry = index[element_id]
        element = entry["element"]
        if element is None:
            raise ValueError("typed edges are withdrawn with the elements they connect, not on their own")
        if isinstance(element, FunctionBlock):
            raise ValueError("the Book's function cannot be withdrawn; revise it instead")
        if isinstance(element, DecisionElement) or element.epistemic_status in ("unresolved", "rejected"):
            raise ValueError("author decisions, open questions and rejected items cannot be withdrawn by a working operation")
        if element.provenance is not None:
            raise ValueError("re-label this legacy element with a revision before withdrawing it")
        cand_json = json.loads(json.dumps(current["artifact"]))
        _set_epistemic_status(cand_json, element_id, "rejected")
        candidate = WorkingBookArchitecture.model_validate_json(json.dumps(cand_json))
        _check_semantics(candidate)
        cand_index = _index_elements(candidate)
        _enforce_revision_rules(index, cand_index)
        settings = {
            "book_number": book_number,
            "operation": "withdraw",
            "baseline_request_sha256": current["request_sha256"],
            "baseline_content_sha256": current["content_sha256"],
            "baseline_revision_number": current.get("revision_number", 0),
            "series_request_sha256": current["series_request_sha256"],
            "source_sha256": current["source_sha256"],
            "mode": "targeted",
            "targets": [element_id],
            "dependents": sorted(_dependents_of(index, {element_id})),
            "allowed_ids": [element_id],
            "freshness_format": 2,
        }
        user = json.dumps({
            "schema": REVISION_KIND, "operation": "withdraw", "book_number": book_number,
            "element": entry["element"].model_dump(mode="json"), "rationale": rationale,
            "baseline": {"request_sha256": current["request_sha256"], "content_sha256": current["content_sha256"]},
        }, ensure_ascii=False, sort_keys=True)
        request = build_host_agent_request(
            candidate_id=f"book-{book_number}-withdraw-" + _digest({"user": user})[:16],
            role=ROLE, system=_BOOK_REVISION_SYSTEM, user=user, settings=settings,
        )
        request_dir = base / "requests" / request.request_sha256
        write_host_agent_request(request_dir / "request.json", request)
        _atomic_json_write(base / "latest_request.json", {"request_sha256": request.request_sha256})
        review = _build_review(
            baseline=artifact, candidate=candidate, base_index=index, cand_index=cand_index,
            settings=settings, instruction=f"withdraw {element_id}: {rationale}",
            series_node_ids={node["id"] for node in (_candidate(store) or {}).get("candidate", {}).get("nodes", [])},
            request_sha256=request.request_sha256,
            withdrawal={"element_id": element_id, "rationale": rationale},
        )
        _atomic_json_write(request_dir / "review.json", review)
    return book_project(store, book_number)


def book_apply_review(store: CanvasStore, book_number: int, request_sha256: str) -> dict:
    """Apply one completed, applicable review. Repeated application is an explicit no-op."""
    _check_number(book_number)
    if not isinstance(request_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", request_sha256):
        raise ValueError("valid request_sha256 is required")
    with _FilesystemLock(store._path(".canvas.lock")):
        base = _book_root(store, book_number)
        pointer = _read(base / "latest_request.json")
        review = _read(base / "requests" / request_sha256 / "review.json")
        current = _read(base / "current.json")
        if review is None:
            raise ValueError("this request has no completed review")
        if pointer is None or pointer["request_sha256"] != request_sha256:
            raise BeginnerConcurrencyError("a newer Book request superseded this review")
        if current is not None and current["request_sha256"] == request_sha256:
            return {"result": "already_applied", **book_project(store, book_number)}
        if current is None or current["request_sha256"] != review["baseline"]["request_sha256"]:
            raise BeginnerConcurrencyError("the working Book changed after this review was prepared; review again")
        request = load_host_agent_request(base / "requests" / request_sha256 / "request.json")
        settings = request.settings
        if _series_changed(store, settings) or _source_changed(store, book_number, settings):
            raise BeginnerConcurrencyError(
                "working context changed: the Series architecture or the Book's source changed; review again"
            )
        if not review["applicable"]:
            problems = "; ".join(f"{item['id']} ({item['change']}: {item['reason']})"
                                 for item in review["unexpected_changes"][:10])
            raise ValueError(f"unexpected changes block application: {problems}")
        artifact_json = review["candidate"]
        artifact = WorkingBookArchitecture.model_validate_json(json.dumps(artifact_json))
        series = _candidate(store)
        series_nodes = {node["id"]: _digest(node) for node in (series or {}).get("candidate", {}).get("nodes", [])}
        lineage = current.get("lineage") or [{
            "revision": 0, "request_sha256": current["request_sha256"],
            "content_sha256": current["content_sha256"], "operation": "develop",
        }]
        lineage = [*lineage, {
            "revision": review["revision_number"], "request_sha256": request_sha256,
            "content_sha256": _digest(artifact_json), "operation": "revise",
            "baseline_request_sha256": review["baseline"]["request_sha256"],
        }]
        changed_ids = [entry["id"] for entry in review["changes"]["changed"]]
        _atomic_json_write(base / "current.json", {
            "book_number": book_number,
            "request_sha256": request_sha256,
            "series_request_sha256": settings["series_request_sha256"],
            "source_sha256": settings["source_sha256"],
            "series_nodes": {node: series_nodes[node] for node in sorted(_series_refs(artifact))
                             if node in series_nodes},
            "content_sha256": _digest(artifact_json),
            "authority": "working_noncanonical",
            "artifact": artifact_json,
            "source_items": current.get("source_items", []),
            "revision_number": review["revision_number"],
            "lineage": lineage,
            "applied_review": {
                "mode": review["mode"],
                "added": [entry["id"] for entry in review["changes"]["added"]],
                "changed": changed_ids,
                "removed": [entry["id"] for entry in review["changes"]["removed"]],
                "preserved_count": review["preserved"]["count"],
                "representation_only": [entry["id"] for entry in review["changes"]["changed"]
                                        if entry["classification"].startswith("representation")],
                "consequence_candidates": [entry["id"] for entry in review["consequence_candidates"]],
                "author_decisions": [entry["decision_id"] for entry in review["author_decisions"]],
                "withdrawal": review.get("withdrawal"),
            },
        })
    return {"result": "applied", **book_project(store, book_number)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Auteur working Book architecture (noncanonical)")
    parser.add_argument("--project", required=True, help="Local Auteur project root")
    parser.add_argument("--canvas", required=True, help="Canvas id")
    actions = parser.add_subparsers(dest="action", required=True)
    prepare = actions.add_parser("book-prepare", help="Develop a Book, or prepare a revision with --instruction")
    prepare.add_argument("--book", type=int, required=True)
    prepare.add_argument("--instruction", default=None, help="Revision instruction. Omit to develop.")
    prepare.add_argument("--target", action="append", default=[], help="Element id to revise (repeatable)")
    prepare.add_argument("--holistic", action="store_true", help="Permit changes to any element")
    complete = actions.add_parser("book-complete-file", help="Validate and store the host agent's Book JSON")
    complete.add_argument("--book", type=int, required=True)
    complete.add_argument("--candidate", required=True, help="Path to Book architecture JSON")
    withdraw = actions.add_parser("book-withdraw", help="Propose withdrawing one working element (a reviewed revision)")
    withdraw.add_argument("--book", type=int, required=True)
    withdraw.add_argument("--element", required=True)
    withdraw.add_argument("--rationale", required=True)
    apply_review = actions.add_parser("book-apply-review", help="Apply one completed, applicable review")
    apply_review.add_argument("--book", type=int, required=True)
    apply_review.add_argument("--request-sha256", required=True, help="Exact reviewed request SHA-256")
    resume = actions.add_parser("book-resume", help="Read-only re-entry for one Book")
    resume.add_argument("--book", type=int, required=True)
    args = parser.parse_args(argv)
    store = CanvasStore(Path(args.project), args.canvas)
    try:
        if args.action == "book-prepare":
            result = book_prepare(
                store, args.book, instruction=args.instruction, targets=tuple(args.target), holistic=args.holistic,
            )
        elif args.action == "book-complete-file":
            pending = book_project(store, args.book)
            if pending["status"] != "awaiting_host_agent" or not pending["request"]:
                raise ValueError("no pending Book architecture request to complete")
            request = HostAgentRequest(**pending["request"])
            text = Path(args.candidate).read_text(encoding="utf-8")
            response = build_host_agent_response(request, text)
            result = book_complete(store, args.book, response.model_dump())
        elif args.action == "book-withdraw":
            result = book_withdraw(store, args.book, args.element, args.rationale)
        elif args.action == "book-apply-review":
            result = book_apply_review(store, args.book, args.request_sha256)
        else:
            result = book_resume(store, args.book)
    except (ValueError, BeginnerConcurrencyError) as exc:
        print(json.dumps({"result": "rejected", "error": str(exc)}, indent=2, ensure_ascii=False))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


_BOOK_SYSTEM = """You are developing ONE Book's working architecture for a long-form Series. Output exactly one JSON object, schema_version 1, and nothing else. This is a noncanonical proposal: never accept, never write prose or chapters, never create character identities, character commitments or relationship states.

Top level: schema_version, book_number, title, function, inherited, engines, agents, choice, local_resolution, series_consequences, later_possibilities, assumptions, alternatives, unresolved, open_author_decisions, typed_edges.
Every element: id (lowercase, starts with a letter), attribution, epistemic_status, text (the substance, as long as it needs to be, under 8000 characters), refs, and interpretation only where the element is source-derived.
- attribution: derived (cite the source in refs; put your own contribution in interpretation), agent_proposed (your own working inference), or unattributed (the source asserts it without naming a source; do not guess one). Never author_fixed, accepted, unlabelled, author-declared or author-supplied.
- epistemic_status: asserted (the working proposal states it), hypothetical (an alternative not taken), unresolved (a genuinely open question or missing information), conditional (depends on an assumption or author decision you cite in refs; never assert a claim that depends on an author decision), rejected.
- An assumption may state no reversal (reversal null) when none is known. That leaves the reversal unknown; it does not make the assumption unresolved.
- refs: {kind, id}. kind series_node (an id in series_architecture.candidate.nodes), book_element (an id you define in this object), source_item (an id listed in visible_source_ids). Every ref must resolve.
- function: question, pressure, and at least one series_node ref.
- engines: condition, consequence, changed_state (required); choice, new_possibility (optional).
- agents: motives, institutions and constraints. Give a proper name only when a visible source item states it; then name_source must be a source_item or series_node ref. Never invent a name.
- choice: two to six options (each an element), chosen_option_id, costs_kept_visible (one or more elements), transformation (an element).
- local_resolution: items with closure true or false. series_consequences: items with kind changes, preserves or complicates. later_possibilities: items with kind enabled or closed.
- assumptions: agent_proposed assumptions MUST state a reversal condition. If you cannot state one, mark the assumption unresolved with reversal null.
- alternatives: title, status "hypothetical", rationale, attribution "agent_proposed", epistemic_status "hypothetical".
- unresolved: missing information and author-reserved decisions.
- open_author_decisions: series_question_index and series_question_sha256, copied exactly from series_architecture.open_questions. Use them only for a Series open question this Book must leave to the author.
- typed_edges: {id, source (a Book element id), target (a ref), dependency (sets_up, pays_off, depends_on, pressures, contradicts or transforms), function}.
Preserve the source's causal, motivational and prospective substance; do not compress it into labels. Do not fabricate attribution, reversal conditions or references to make the object valid. Cite what the source says and mark what it does not say."""


_BOOK_REVISION_SYSTEM = """You are revising ONE existing working Book architecture. Output exactly one JSON object with schema_version 1 and nothing else. It is the COMPLETE revised Book object, not a patch. This is a noncanonical working proposal: never accept, never write prose or chapters, never create character identities, character commitments or relationship states.

Scope. Change only the elements whose ids appear in permitted_ids. Copy every other element exactly as it appears in the baseline (the record you are given in full for scoped elements, and the unchanged_elements manifest for the rest). You may refer to unchanged elements by id in refs. Keep a stable id wherever the same narrative responsibility continues. Introduce a new id only for a genuinely new element, and make it reference a permitted element.

Form. Every element you change or add uses the explicit form: attribution (derived, with at least one ref to the source; agent_proposed; or unattributed when the source gives no attribution) and epistemic_status (asserted, hypothetical, unresolved, conditional or rejected). Put your own contribution to a source-derived statement in interpretation. Never write provenance, author_fixed, accepted, unlabelled, author-declared or author-supplied. An element that depends on an assumption or an author decision is conditional and cites it in refs. An assumption may state no reversal (reversal null) when none is known.

Fixed. Open questions and author decisions stay unresolved and keep their Series binding. A working revision does not settle an open question or an author decision. Never assert a claim that depends on an author decision. Do not invent names, character commitments or relationship states.

Instruction. The instruction is a working revision requested by the operator. Treat it as a hypothetical working change to develop and test, not as canon or an author decision. When it changes a mechanism, state the changed condition as an assumption, and record the condition it replaces as its reversal where you know it. Reflect the consequences inside the permitted elements, and record each dependency you establish as a typed edge. Do not rewrite the Series architecture and do not choose an accepted ending.
"""

if __name__ == "__main__":
    raise SystemExit(main())
