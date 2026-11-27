"""Explicitly invoked, agent-directed discovery of creative possibilities across the working Architecture.

The author asks what they may be overlooking. The agent, not the author, chooses which continuing questions and recorded
structures deserve investigation, and answers with at most four possibilities, each grounded in recorded evidence or
labelled speculative. The answer is advisory: it is stored as a noncanonical record, it writes nothing into the
Architecture or a Working Book, and nothing in it is accepted, settled or applied.

The request is stage A (orientation): the working Architecture as the inquiry already reads it, every continuing question
with compact recorded history, and a few Working Book decisions per question, all bounded and counted. Stage C, focused
recovery of history, happens later, when the author takes a possibility into narrative deliberation, through the existing
bounded packet. Discovery never runs a second agent round.

A possibility is never rebound: its questions are identities, and it is transferable only while every one is still a
continuing question. Its wording may have changed since discovery; that is said, not hidden.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from . import studio_architecture as arch
from .studio_architecture_deliberation import _spread
from .studio_architecture_question_projection import project_architecture_questions
from .studio_architecture_questions import text_digest
from .studio_store import CanvasStore

SCHEMA = "studio-opportunity-discovery/1"
ROLE = "studio_architecture_discovery"
MAX_POSSIBILITIES = 4
MIN_QUESTIONS = 2
MAX_QUESTIONS = 3
MAX_EVIDENCE = 6
MAX_BOOK_DECISIONS_SHOWN = 2
# Working Book elements that record an association with a question, shown per question, spread across Books.
MAX_BOOK_ELEMENTS_SHOWN = 2
WORDING_LIMIT = 600
REASON_LIMIT = 240
DECISION_LIMIT = 300
GOAL_LIMIT = 600
COVERAGE_LIMIT = 600
TITLE_LIMIT = 120
POSSIBILITY_LIMIT = 700
SIGNIFICANCE_LIMIT = 500
NEXT_LIMIT = 300
GAINS_LIMIT = 300
COSTS_LIMIT = 300
EVIDENCE_NOTE_LIMIT = 240
NO_REASON_LIMIT = 600
ITEM_LIMIT = 240
UNCERTAINTIES_MAX = 8

KindLabel = Literal[
    "thematic_resonance", "shared_mechanism", "productive_tension", "overlooked_consequence",
    "narrative_inheritance", "productive_independence", "consolidation",
]
RefKind = Literal["node", "link", "genre_interaction", "question", "book_decision", "book_element", "candidate_opportunity"]
MECHANISM_REFS = ("node", "link", "genre_interaction")

_SYSTEM = f"""You are the active Auteur narrative discovery agent. The author has explicitly asked you to look across the
working Architecture for creative possibilities they may be overlooking. You choose what deserves investigation. The
author may have given a goal or area of concern; you may follow it or set it aside.

Read the working Architecture and the discovery packet. The packet lists each continuing open question with its current
wording, its last recorded change and the reason the author recorded for it, and some Working Book decisions that refer to
it. Recorded facts are only what the Architecture, the questions, the recorded reasons and the Book decisions state.
Everything else is your interpretation, and you must label it as such.

Each question may also list book_element_associations: Working Book elements that record an association with that question.
An association is evidence that an element engages the question. It is not evidence that the element matters more than other
material, and it does not establish that the element answers, settles, develops or inherits from the question. A possibility
that rests only on such associations, or on a shared Book reference, is speculative.

Find at most four possibilities that are specific to this narrative and worth serious creative investigation. Each names
two or three continuing questions by their identity, cites the recorded evidence it rests on, and says whether it is
grounded in a recorded mechanism or speculative. A possibility grounded only in a shared Book reference, or in similar
wording, is not grounded. Prefer a few strong possibilities to many plausible ones. You may also conclude that no
possibility is worthwhile: then leave possibilities empty and say why in no_possibility_reason. Say when the questions
should stay independent, and what counterevidence or cost matters.

Length limits are strict: an answer that exceeds one is refused as a whole, so count before you answer. Limits in
characters: coverage_note {COVERAGE_LIMIT}; title {TITLE_LIMIT}; possibility {POSSIBILITY_LIMIT}; significance
{SIGNIFICANCE_LIMIT}; next_investigation {NEXT_LIMIT}; gains and costs {GAINS_LIMIT} each; each evidence note
{EVIDENCE_NOTE_LIMIT}; no_possibility_reason {NO_REASON_LIMIT}; each assumption, counterevidence item and uncertainty
{ITEM_LIMIT}. Lists: at most four assumptions and four counterevidence items per possibility, at most {UNCERTAINTIES_MAX}
uncertainties.

Return ONLY a JSON object with schema_version=1, coverage_note (what you surveyed and what you set aside), possibilities
(0-4 objects, each with the keys "title", "kind" (optional: thematic_resonance, shared_mechanism, productive_tension,
overlooked_consequence, narrative_inheritance, productive_independence or consolidation), "possibility", "significance",
"questions" (two or three question ids), "evidence" (one to six objects, each with the keys "ref_kind", "ref_id", "note" and,
for ref_kind book_decision or book_element only, "book_number"), "basis" ("grounded" or "speculative"), "assumptions" (0-4 strings),
"counterevidence" (0-4 strings), "gains" (optional string), "costs" (optional string) and "next_investigation"),
no_possibility_reason (required when possibilities is empty) and uncertainties (0-8 strings).

ref_kind is one of node, link, genre_interaction, question, book_decision, book_element or candidate_opportunity. A
book_element ref_id is the element id; cite it only for a question of the possibility that the element engages. Use only ids that appear
in the packet or the Architecture. A possibility is advisory: never say it is accepted, settled or applied. Do not restate an
existing question or recorded opportunity without a new consequence. Do not invent narrative facts; a speculative
possibility names the imaginative step it takes."""


ItemText = Annotated[str, StringConstraints(min_length=1, max_length=ITEM_LIMIT)]


class DiscoveredEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    ref_kind: RefKind
    ref_id: str = Field(min_length=1, max_length=80)
    book_number: int | None = Field(default=None, ge=1, le=60)
    note: str = Field(min_length=1, max_length=EVIDENCE_NOTE_LIMIT)

    @model_validator(mode="after")
    def book_reference_names_its_book(self) -> "DiscoveredEvidence":
        in_book = self.ref_kind in ("book_decision", "book_element")
        if in_book != (self.book_number is not None):
            raise ValueError("a book_decision or book_element reference names its book_number, and only those do")
        return self


class DiscoveredPossibility(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    title: str = Field(min_length=1, max_length=TITLE_LIMIT)
    kind: KindLabel | None = None
    possibility: str = Field(min_length=1, max_length=POSSIBILITY_LIMIT)
    significance: str = Field(min_length=1, max_length=SIGNIFICANCE_LIMIT)
    questions: list[str] = Field(min_length=MIN_QUESTIONS, max_length=MAX_QUESTIONS)
    evidence: list[DiscoveredEvidence] = Field(min_length=1, max_length=MAX_EVIDENCE)
    basis: Literal["grounded", "speculative"]
    assumptions: list[ItemText] = Field(default_factory=list, max_length=4)
    counterevidence: list[ItemText] = Field(default_factory=list, max_length=4)
    gains: str | None = Field(default=None, max_length=GAINS_LIMIT)
    costs: str | None = Field(default=None, max_length=COSTS_LIMIT)
    next_investigation: str = Field(min_length=1, max_length=NEXT_LIMIT)

    @model_validator(mode="after")
    def distinct_questions(self) -> "DiscoveredPossibility":
        if len(set(self.questions)) != len(self.questions):
            raise ValueError("a possibility names each question once")
        return self


class DiscoveryAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    coverage_note: str = Field(min_length=1, max_length=COVERAGE_LIMIT)
    possibilities: list[DiscoveredPossibility] = Field(default_factory=list, max_length=MAX_POSSIBILITIES)
    no_possibility_reason: str | None = Field(default=None, max_length=NO_REASON_LIMIT)
    uncertainties: list[ItemText] = Field(default_factory=list, max_length=UNCERTAINTIES_MAX)

    @model_validator(mode="after")
    def empty_answers_say_why(self) -> "DiscoveryAnswer":
        if not self.possibilities and not (self.no_possibility_reason or "").strip():
            raise ValueError("an answer with no possibility must say why in no_possibility_reason")
        return self


def _clip(text: Any, limit: int) -> str | None:
    if text is None:
        return None
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _discovery_root(store: CanvasStore):
    return arch._root(store) / "discoveries"


def _last_change(spans: list[dict]) -> dict | None:
    for span in reversed(spans):
        if span.get("kind") == "present" and span.get("change") in ("introduced", "moved", "reworded", "moved_and_reworded"):
            reason = span.get("reason") or {}
            return {
                "change": span["change"],
                "from_revision": span.get("from_revision"),
                "to_revision": span.get("to_revision"),
                "reason_instruction": _clip(reason.get("instruction"), REASON_LIMIT) if reason.get("readable") else None,
                "reason_recorded": bool(reason.get("instruction") or reason.get("selected_alternative")),
            }
    return None


ORIENTATIONS = ("full", "current_state")


def build_discovery_packet(store: CanvasStore, goal: str | None, *, orientation: str = "full") -> dict[str, Any]:
    """Stage A: compact, bounded and source-qualified orientation. Read-only; raises if there is no working Architecture.

    ``full`` (the product path) gives each question its last recorded change and reason, and its Book decision texts.
    ``current_state`` is the comparison baseline: the same questions and Book references, without history or texts.
    """
    if orientation not in ORIENTATIONS:
        raise ValueError("orientation must be full or current_state")
    with_history = orientation == "full"
    view = project_architecture_questions(store)
    if not view["available"]:
        raise ValueError("no current working architecture")
    questions = []
    omitted = {}
    omitted_elements: dict[str, int] = {}
    for question in view["questions"]:
        if question["standing"] != "continuing":
            continue
        books = sorted(question["books"], key=lambda entry: (entry["book_number"], entry["decision_id"]))
        shown = books[:MAX_BOOK_DECISIONS_SHOWN]
        omitted[question["id"]] = max(0, len(books) - len(shown))
        engagements_all = sorted(question.get("engagements") or [],
                                 key=lambda entry: (entry["book_number"], entry["element_id"]))
        engagements, engagements_omitted = _spread(engagements_all, MAX_BOOK_ELEMENTS_SHOWN)
        omitted_elements[question["id"]] = engagements_omitted
        questions.append({
            "id": question["id"],
            "index": question["index"],
            "current_wording": _clip(question["text"], WORDING_LIMIT),
            "text_sha256": question["text_sha256"],
            "history_complete": bool(question["history"]["complete"]),
            "readable_formulations": sum(len(span["versions"]) for span in question["spans"] if span["kind"] == "present"),
            "last_change": _last_change(question["spans"]) if with_history else None,
            "book_decisions": [{
                "book_number": entry["book_number"],
                "decision_id": entry["decision_id"],
                "title": entry["title"],
                "state": entry["state"],
                "identity_basis": ("recorded_by_decision" if entry["records_identity"]
                                   else "resolved_by_owner_from_recorded_version"),
                "decision_text": _clip(entry.get("decision_text"), DECISION_LIMIT) if with_history else None,
                "decision_text_sha256": text_digest(entry.get("decision_text") or ""),
            } for entry in shown],
            "book_element_associations": [{
                "book_number": entry["book_number"],
                "element_id": entry["element_id"],
                "title": entry["title"],
                "collection": entry["collection"],
                "standing": entry["state"],
                "element_text": _clip(entry.get("element_text"), DECISION_LIMIT) if with_history else None,
                "element_text_sha256": text_digest(entry.get("element_text") or ""),
                "attribution": entry.get("attribution"),
                "epistemic_status": entry.get("epistemic_status"),
                "commitment_authority": entry.get("commitment_authority"),
            } for entry in engagements],
        })
    historical = [{
        "id": question["id"],
        "last_wording": _clip(question["text"], REASON_LIMIT),
        "anchorable": False,
        "note": "No longer an open question. Historical only: it cannot anchor a possibility.",
    } for question in view["no_longer_open"]]
    packet: dict[str, Any] = {
        "schema": SCHEMA,
        "authority": "agent_discovery_request_noncanonical",
        "stage": "A_orientation",
        "author_goal": _clip(goal, GOAL_LIMIT) if goal else None,
        "orientation": orientation,
        "current_architecture": {
            "revision_number": view["current"]["revision_number"],
            "numbered": view["current"]["numbered"],
            "history_chain_complete": view["history"]["chain_complete"],
        },
        "questions": questions,
        "no_longer_open_historical": historical,
        "limits": {
            "questions_shown": "all continuing questions",
            "book_decisions_per_question": MAX_BOOK_DECISIONS_SHOWN,
            "book_decisions_omitted": omitted,
            "book_element_associations_per_question": MAX_BOOK_ELEMENTS_SHOWN,
            "book_element_associations_omitted": omitted_elements,
            "wording_characters": WORDING_LIMIT,
            "reason_characters": REASON_LIMIT,
            "decision_characters": DECISION_LIMIT,
            "possibilities": MAX_POSSIBILITIES,
            "note": ("The full working Architecture is in the request, bounded by its own schema. Question history is "
                     "compact here; a possibility's full history is recovered only when it is taken into deliberation."),
        },
    }
    packet["evidence_sha256"] = _digest(packet)
    return packet


def _helpers():
    from auteur.host_agent import (
        build_host_agent_request, load_host_agent_request, validate_host_agent_response,
        write_host_agent_request, write_host_agent_response, _atomic_json_write,
    )
    return (build_host_agent_request, load_host_agent_request, validate_host_agent_response,
            write_host_agent_request, write_host_agent_response, _atomic_json_write)


def _live(store: CanvasStore, current: dict | None, request) -> bool:
    if not current or current["request_sha256"] != request.settings["baseline_candidate_request_sha256"]:
        return False
    if arch._current_candidate_freshness(store, current) != "ready":
        return False
    if current.get("source_sha256") != request.settings.get("source_sha256"):
        return False
    return current.get("design_guidance_sha256") == request.settings.get("design_guidance_sha256")


def prepare_architecture_discovery(store: CanvasStore, *, goal: str | None = None, orientation: str = "full") -> dict:
    """Prepare the agent-directed discovery request. Explicit only; nothing is executed and nothing is changed."""
    build_request, _, _, write_request, _, atomic_write = _helpers()
    if goal is not None and (not isinstance(goal, str) or len(goal) > GOAL_LIMIT):
        raise ValueError(f"the goal must be text under {GOAL_LIMIT} characters")
    with arch._FilesystemLock(store._path(".canvas.lock")):
        current = arch._candidate(store)
        if not current:
            raise ValueError("no current working architecture")
        if arch._current_candidate_freshness(store, current) != "ready":
            raise arch.BeginnerConcurrencyError("architecture source or guidance is stale")
        context = arch._source(store, previous=current["candidate"])
        _, _, design_context = arch._design_context_parts(store, context)
        packet = build_discovery_packet(store, goal, orientation=orientation)
        payload = {
            "operation": "architecture_discovery",
            "author_goal": goal or None,
            "discovery_packet": packet,
            "working_candidate": current["candidate"],
            "narrative_design_context": design_context,
        }
        user = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        settings = {
            "operation": "discover",
            "canvas_id": store.canvas_id,
            "baseline_candidate_request_sha256": current["request_sha256"],
            "source_sha256": current["source_sha256"],
            "design_guidance_sha256": current.get("design_guidance_sha256"),
            "discovery_schema_version": 1,
            "orientation": orientation,
            "discovery_evidence_sha256": packet["evidence_sha256"],
            # Each explicit invocation is its own record: an identical request on an unchanged Architecture is still a new ask.
            "invocation": uuid.uuid4().hex,
        }
        request = build_request(
            candidate_id="studio-discovery-" + _digest({"settings": settings, "user": user})[:24],
            role=ROLE, system=_SYSTEM, user=user, settings=settings,
        )
        base = _discovery_root(store)
        write_request(base / "requests" / request.request_sha256 / "request.json", request)
        atomic_write(base / "latest_request.json", {"request_sha256": request.request_sha256})
    return project_architecture_discoveries(store)


def _check_answer(answer: DiscoveryAnswer, packet: dict, candidate: dict) -> None:
    """Every reference must resolve inside this request. Raises ValueError naming the first that does not."""
    continuing = {question["id"] for question in packet["questions"]}
    historical = {question["id"] for question in packet["no_longer_open_historical"]}
    nodes = {node["id"] for node in candidate.get("nodes", [])}
    links = {link["id"] for link in candidate.get("links", [])}
    interactions = {item["id"] for item in candidate.get("genre_interactions", [])}
    opportunities = {item["id"] for item in candidate.get("opportunities", [])}
    decisions = {(book["book_number"], book["decision_id"]) for question in packet["questions"]
                 for book in question["book_decisions"]}
    # A Book element is evidence only for a question of the possibility that it actually engages in this request.
    engaged: dict[tuple[int, str], set[str]] = {}
    for question in packet["questions"]:
        for entry in question["book_element_associations"]:
            engaged.setdefault((entry["book_number"], entry["element_id"]), set()).add(question["id"])
    titles: set[str] = set()
    for possibility in answer.possibilities:
        key = " ".join(possibility.title.casefold().split())
        if key in titles:
            raise ValueError(f"two possibilities share the title {possibility.title!r}")
        titles.add(key)
        for identifier in possibility.questions:
            if identifier not in continuing:
                raise ValueError(f"{identifier} is not a continuing open question of this request")
        grounded = False
        for item in possibility.evidence:
            kind, identifier = item.ref_kind, item.ref_id
            if kind == "node":
                ok = identifier in nodes
            elif kind == "link":
                ok = identifier in links
            elif kind == "genre_interaction":
                ok = identifier in interactions
            elif kind == "question":
                ok = identifier in continuing or identifier in historical
            elif kind == "candidate_opportunity":
                ok = identifier in opportunities
            elif kind == "book_element":
                ok = bool(set(possibility.questions) & engaged.get((item.book_number, identifier), set()))
            else:
                ok = (item.book_number, identifier) in decisions
            if not ok:
                raise ValueError(f"evidence {kind} {identifier!r} is not in this request")
            grounded = grounded or kind in MECHANISM_REFS
        if possibility.basis == "grounded" and not grounded:
            raise ValueError(f"{possibility.title!r} is labelled grounded but cites no recorded mechanism")


def _with_ids(possibilities: list[dict]) -> list[dict]:
    return [{"id": f"p{index}", **row} for index, row in enumerate(possibilities, start=1)]


def complete_architecture_discovery(store: CanvasStore, payload: dict) -> dict:
    _, load_request, validate_response, _, write_response, atomic_write = _helpers()
    with arch._FilesystemLock(store._path(".canvas.lock")):
        base = _discovery_root(store)
        pointer = arch._read(base / "latest_request.json")
        if not pointer:
            raise ValueError("no discovery request exists")
        sha = pointer["request_sha256"]
        folder = base / "requests" / sha
        request = load_request(folder / "request.json")
        if request.role != ROLE:
            raise ValueError("wrong discovery role")
        response = validate_response(request, payload)
        prior = arch._read(folder / "response.json")
        if prior:
            if prior != response.model_dump():
                raise arch.BeginnerConcurrencyError("a different discovery response already completed this request")
            return project_architecture_discoveries(store)
        current = arch._candidate(store)
        if not _live(store, current, request):
            write_response(folder / "stale_response.json", response)
            raise arch.BeginnerConcurrencyError(
                "the working Architecture changed since this discovery was prepared; response retained as stale evidence")
        answer = DiscoveryAnswer.model_validate_json(response.text)
        submitted = json.loads(request.user)
        _check_answer(answer, submitted["discovery_packet"], submitted["working_candidate"])
        saved = {
            **answer.model_dump(mode="json"),
            "possibilities": _with_ids([item.model_dump(mode="json") for item in answer.possibilities]),
            "schema": SCHEMA,
            "authority": "noncanonical_discovery",
            "baseline_candidate_request_sha256": current["request_sha256"],
            "author_goal": submitted.get("author_goal"),
            "evidence": submitted["discovery_packet"],
            "evidence_sha256": submitted["discovery_packet"]["evidence_sha256"],
        }
        write_response(folder / "response.json", response)
        atomic_write(folder / "result.json", saved)
    return project_architecture_discoveries(store)


def record_possibility_decision(store: CanvasStore, request_sha256: str, possibility_id: str,
                                decision: Literal["declined", "reopened"], reason: str | None = None) -> dict:
    """The author's own choice about one possibility. It is kept beside the discovery and changes no narrative record."""
    import re
    _, _, _, _, _, atomic_write = _helpers()
    if not isinstance(request_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", request_sha256):
        raise ValueError("a valid discovery request is required")
    if not isinstance(possibility_id, str) or not possibility_id:
        raise ValueError("a possibility is named by its id")
    if decision not in ("declined", "reopened"):
        raise ValueError("decision must be declined or reopened")
    if reason is not None and (not isinstance(reason, str) or len(reason) > 300):
        raise ValueError("the reason must be text under 300 characters")
    with arch._FilesystemLock(store._path(".canvas.lock")):
        folder = _discovery_root(store) / "requests" / request_sha256
        result = arch._read(folder / "result.json")
        if not result or possibility_id not in {row["id"] for row in result.get("possibilities", [])}:
            raise ValueError("that possibility is not in this discovery")
        decisions = arch._read(folder / "decisions.json") or {}
        if decision == "reopened":
            decisions.pop(possibility_id, None)
        else:
            decisions[possibility_id] = {"decision": "declined", "reason": reason or None}
        atomic_write(folder / "decisions.json", decisions)
    return project_architecture_discoveries(store)


def _applied_inquiries(store: CanvasStore) -> set[str]:
    """Inquiries whose alternative a revision in the applied chain was made from."""
    applied: set[str] = set()
    for sha in arch.architecture_revision_chain(store)["requests"]:
        review = arch._read(arch._root(store) / "requests" / sha / "review.json") or {}
        chosen = review.get("selected_creative_alternative") or {}
        if chosen.get("inquiry_request_sha256"):
            applied.add(chosen["inquiry_request_sha256"])
    return applied


def _inquiries_from(store: CanvasStore, discovery_sha: str, possibility_id: str) -> list[dict]:
    rows = []
    root = arch._root(store) / "inquiries" / "requests"
    if not root.is_dir():
        return rows
    for folder in root.iterdir():
        result = arch._read(folder / "result.json") or {}
        origin = result.get("from_discovery") or {}
        if origin.get("request_sha256") == discovery_sha and origin.get("possibility_id") == possibility_id:
            rows.append({"inquiry_request_sha256": folder.name, "operation": (result.get("intent") or {}).get("operation")})
    return sorted(rows, key=lambda row: row["inquiry_request_sha256"])


def _status(possibility: dict, packet: dict, current_questions: dict[str, dict]) -> dict:
    """Transferability, judged now, never stored. Questions are identities; wording is only compared, never matched."""
    recorded = {question["id"]: question for question in packet["questions"]}
    missing = [identifier for identifier in possibility["questions"] if identifier not in current_questions]
    if missing:
        return {"transferable": False, "state": "not_transferable",
                "note": ("A question this possibility concerns is no longer open: "
                         + ", ".join(missing) + ". It is not rebound to another question.")}
    reworded = [identifier for identifier in possibility["questions"]
                if current_questions[identifier]["text_sha256"] != recorded.get(identifier, {}).get("text_sha256")]
    if reworded:
        return {"transferable": True, "state": "reworded",
                "note": ("Formulated against an earlier wording of " + ", ".join(reworded) +
                         ". It remains transferable; its questions have kept their identity.")}
    return {"transferable": True, "state": "transferable", "note": None}


def _evidence_view(item: dict, candidate: dict, current_questions: dict[str, dict], packet: dict) -> dict:
    kind, identifier = item["ref_kind"], item["ref_id"]
    if kind == "node":
        present = identifier in {node["id"] for node in candidate.get("nodes", [])}
    elif kind == "link":
        present = identifier in {link["id"] for link in candidate.get("links", [])}
    elif kind == "genre_interaction":
        present = identifier in {row["id"] for row in candidate.get("genre_interactions", [])}
    elif kind == "candidate_opportunity":
        present = identifier in {row["id"] for row in candidate.get("opportunities", [])}
    elif kind == "question":
        # A question no longer open is historical: it is not in the Architecture now, whatever its record says.
        present = identifier in current_questions
    else:
        present = None  # a Book decision is read again when the possibility is taken into deliberation
    return {**item, "present_now": present}


def project_architecture_discoveries(store: CanvasStore, limit: int = 10, only: str | None = None) -> dict[str, Any]:
    """Read-only: the discoveries on this canvas, newest first, each possibility with its present transferability,
    decisions and the investigations it has led to. A historical discovery stays readable."""
    base = _discovery_root(store)
    pointer = arch._read(base / "latest_request.json")
    current = arch._candidate(store)
    baseline = current["request_sha256"] if current else None
    current_questions: dict[str, dict] = {}
    if current:
        view = project_architecture_questions(store)
        current_questions = {q["id"]: q for q in view["questions"] if q["standing"] == "continuing"}
    applied = _applied_inquiries(store) if current else set()
    rows, pending, unreadable = [], None, []
    if pointer:
        from auteur.host_agent import load_host_agent_request
        requests_root = base / "requests"
        folders = [folder for folder in requests_root.iterdir() if folder.is_dir()] if requests_root.is_dir() else []
        ordered = []
        for folder in folders:
            try:
                request = load_host_agent_request(folder / "request.json")
            except Exception:  # noqa: BLE001 - one damaged folder is named, and must not hide the rest
                unreadable.append({"request_sha256": folder.name, "status": "unreadable"})
                continue
            ordered.append((request.created_at, folder.name, folder, request))
        ordered.sort(key=lambda row: (row[0], row[1]), reverse=True)
        for _created, sha, folder, request in ordered:
            if only is not None and sha != only:
                continue
            result = arch._read(folder / "result.json")
            if result is None:
                if sha == pointer["request_sha256"]:
                    live = _live(store, current, request)
                    pending = {"request_sha256": sha, "status": "awaiting_host_agent" if live else "stale",
                               "request": request.model_dump() if live else None}
                continue
            decisions = arch._read(folder / "decisions.json") or {}
            packet = result["evidence"]
            candidate = json.loads(request.user)["working_candidate"]
            possibilities = []
            for possibility in result.get("possibilities", []):
                pid = possibility["id"]
                investigations = _inquiries_from(store, sha, pid)
                possibilities.append({
                    **possibility,
                    "status": _status(possibility, packet, current_questions) if current else
                              {"transferable": False, "state": "no_current_architecture", "note": None},
                    "evidence": [_evidence_view(item, candidate, current_questions, packet)
                                 for item in possibility["evidence"]],
                    "decision": decisions.get(pid),
                    "investigations": investigations,
                    "applied": any(row["inquiry_request_sha256"] in applied for row in investigations),
                })
            rows.append({
                "request_sha256": sha,
                "created_at": request.created_at,
                "author_goal": result.get("author_goal"),
                "baseline": "current" if result.get("baseline_candidate_request_sha256") == baseline else "earlier_architecture",
                "coverage_note": result.get("coverage_note"),
                "no_possibility_reason": result.get("no_possibility_reason"),
                "uncertainties": result.get("uncertainties", []),
                "possibilities": possibilities,
            })
            if len(rows) >= limit:
                break
    return {
        "schema": SCHEMA,
        "authority": "noncanonical_discovery_not_working_architecture",
        "canvas_id": store.canvas_id,
        "status": "not_started" if not pointer else ("pending" if pending else "ready"),
        "pending": pending,
        "discoveries": rows,
        "unreadable": unreadable,
    }


def discovery_origin(store: CanvasStore, origin: dict, anchor_ids: list[str]) -> dict:
    """The check a deliberation makes when it is taken from a possibility. Raises ValueError if it may not be."""
    if not isinstance(origin, dict):
        raise ValueError("a discovered possibility is named by its discovery and its possibility id")
    discovery_sha = origin.get("request_sha256") if isinstance(origin.get("request_sha256"), str) else ""
    possibility_id = origin.get("possibility_id") if isinstance(origin.get("possibility_id"), str) else ""
    if not discovery_sha or not possibility_id:
        raise ValueError("a discovered possibility is named by its discovery and its possibility id")
    projection = project_architecture_discoveries(store, limit=10 ** 6, only=discovery_sha)
    discovery = next((row for row in projection["discoveries"] if row["request_sha256"] == discovery_sha), None)
    if discovery is None:
        raise ValueError("that discovery is not recorded on this canvas")
    possibility = next((row for row in discovery["possibilities"] if row["id"] == possibility_id), None)
    if possibility is None:
        raise ValueError("that possibility is not in the discovery")
    if set(possibility["questions"]) != set(anchor_ids):
        raise ValueError("the investigation must concern exactly the questions the possibility names; "
                         "it cannot substitute other questions")
    if not possibility["status"]["transferable"]:
        raise ValueError(possibility["status"]["note"] or "this possibility is not transferable")
    text = json.dumps({k: possibility[k] for k in ("title", "kind", "possibility", "questions", "basis")},
                      ensure_ascii=False, sort_keys=True)
    # The possibility's own account, as the discovery agent stated it, so the investigation can test what was claimed. It is
    # the discovery's noncanonical proposal, identified by its discovery and id, and it is never presented as a record.
    return {"request_sha256": discovery_sha, "possibility_id": possibility_id, "title": possibility["title"],
            "possibility_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "status_at_transfer": possibility["status"]["state"],
            "authority": "agent_discovery_proposal_noncanonical",
            "proposal": {"kind": possibility.get("kind"), "basis": possibility["basis"],
                         "possibility": possibility["possibility"], "significance": possibility["significance"],
                         "assumptions": list(possibility.get("assumptions") or []),
                         "counterevidence": list(possibility.get("counterevidence") or []),
                         "gains": possibility.get("gains"), "costs": possibility.get("costs"),
                         "next_investigation": possibility.get("next_investigation"),
                         "evidence": [{"ref_kind": item["ref_kind"], "ref_id": item["ref_id"],
                                       "book_number": item.get("book_number"), "note": item["note"]}
                                      for item in possibility.get("evidence") or []]}}
