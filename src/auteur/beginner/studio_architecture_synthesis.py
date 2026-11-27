"""Long-horizon creative synthesis: one development's trajectory, its portfolio relations and its culmination (advisory).

An author selects one to three existing developments (persistent questions, Architecture mechanisms, or the creative alternative a
revision adopted), states what they want to understand, and may name a possible culmination. The owner builds one bounded packet from
the owners of each source: the developments' own wording, the Working Book elements that cite them (exact counts, read now), the
links among them, any accepted reconsiderations used as handoffs, and the author's own culmination and vision. A fresh agent answers a
structured synthesis. The owner validates every citation and stores the answer beside the request.

A synthesis changes no Working Architecture, no Working Book, and no accepted record, and it is never applied. Its standing is read
from a recomputed evidence fingerprint: it is stale once the material it read has changed, and superseded once a later synthesis exists.
"""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from auteur.host_agent import (
    _atomic_json_write, build_host_agent_request, load_host_agent_request, model_output_contract,
    validate_host_agent_response, write_host_agent_request, write_host_agent_response,
)
from auteur.series.working_book_architecture import book_elements, book_numbers

from . import studio_architecture as arch
from .studio_architecture_consequence import _digest, _refuse
from .studio_architecture_question_projection import project_architecture_questions
from .studio_architecture_reconsideration import CriticismAssessment, reconsideration_handoff
from .studio_store import CanvasStore

ROLE = "studio_architecture_synthesis"
SCHEMA = "studio-architecture-synthesis/1"
AUTHORITY = "advisory_synthesis_not_working_architecture"
SYNTHESIS_SCHEMA_VERSION = 1
DEVELOPMENT_KINDS = ("question", "mechanism", "creative_alternative")
MAX_DEVELOPMENTS = 3
MAX_HANDOFFS = 2
MAX_CRITICISM = 4
MAX_HISTORY = 8
MAX_ELEMENTS_PER_DEVELOPMENT = 12
QUESTION_CHARS = 1200
CULMINATION_CHARS = 600
ELEMENT_TEXT_LIMIT = 400
VISION_LIMIT = 800
RECORD_TEXT_LIMIT = 8000
MAX_LINKS = 8

EvidenceId = Annotated[str, StringConstraints(pattern=r"^E[1-9][0-9]{0,2}$")]
Reference = Annotated[str, StringConstraints(pattern=r"^[ds][1-6]$")]
CriticismId = Annotated[str, StringConstraints(pattern=r"^c[1-9]$")]
RELATION_KINDS = ("prerequisite", "preparation", "enables", "complicates", "reinforces", "independent", "incompatible")
NECESSARY_RELATIONS = ("prerequisite", "enables", "complicates")
DEPENDENCE = ("causal", "thematic", "sequential_only", "none")
VIABILITY = ("viable", "weakened", "closed", "unresolved")


class SynthesisStage(BaseModel):
    """One stage of the trajectory. Stages are ordered by developmental dependency, not by book number."""
    model_config = ConfigDict(extra="forbid", strict=True)
    book: int | None = Field(default=None, ge=1, le=60)
    horizon: Literal["existing_book", "proposed_book"]
    development: str = Field(min_length=1, max_length=600)
    becomes_available: str = Field(min_length=1, max_length=400)
    changes: str = Field(min_length=1, max_length=400)
    basis: Literal["recorded", "inferred", "proposed"]
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=4)


class SynthesisRelation(BaseModel):
    """How two developments or stages bear on each other. ``prerequisite`` is necessary; ``preparation`` is helpful only."""
    model_config = ConfigDict(extra="forbid", strict=True)
    kind: Literal["prerequisite", "preparation", "enables", "complicates", "reinforces", "independent", "incompatible"]
    between: list[Reference] = Field(min_length=2, max_length=3)
    dependence: Literal["causal", "thematic", "sequential_only", "none"]
    reason: str = Field(min_length=1, max_length=400)
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=3)


class CulminationCondition(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    text: str = Field(min_length=1, max_length=300)
    evidence: list[EvidenceId] = Field(min_length=1, max_length=3)


class Culmination(BaseModel):
    """The culmination the author named (or the answer reads), with what it needs and what earlier Books keep for themselves."""
    model_config = ConfigDict(extra="forbid", strict=True)
    statement: str = Field(min_length=1, max_length=400)
    necessary: list[CulminationCondition] = Field(default_factory=list, max_length=4)
    enrichment: list[CulminationCondition] = Field(default_factory=list, max_length=4)
    standalone_value: str = Field(min_length=1, max_length=400)


class AlternativePath(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    ordering: str = Field(min_length=1, max_length=400)
    effect: str = Field(min_length=1, max_length=400)
    viability: Literal["viable", "weakened", "closed", "unresolved"]
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=3)


class Opportunity(BaseModel):
    """Something the interaction of two or three developments makes possible that none makes possible alone."""
    model_config = ConfigDict(extra="forbid", strict=True)
    text: str = Field(min_length=1, max_length=400)
    between: list[Reference] = Field(min_length=2, max_length=3)
    evidence: list[EvidenceId] = Field(min_length=1, max_length=3)


class SynthesisAnswer(BaseModel):
    """A structured synthesis of selected developments. The owner holds the developments and the question; the agent gives the reading."""
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    trajectory: list[SynthesisStage] = Field(min_length=2, max_length=6)
    relations: list[SynthesisRelation] = Field(default_factory=list, max_length=8)
    culmination: Culmination | None = None
    alternative_paths: list[AlternativePath] = Field(min_length=1, max_length=3)
    opportunities: list[Opportunity] = Field(default_factory=list, max_length=3)
    reader_experience: str = Field(min_length=1, max_length=600)
    open_decisions: list[Annotated[str, StringConstraints(min_length=1, max_length=240)]] = Field(default_factory=list, max_length=4)
    uncertainty: list[Annotated[str, StringConstraints(min_length=1, max_length=240)]] = Field(default_factory=list, max_length=4)
    criticism_assessments: list[CriticismAssessment] = Field(default_factory=list, max_length=MAX_CRITICISM)
    changes_from_prior: list[Annotated[str, StringConstraints(min_length=1, max_length=240)]] = Field(default_factory=list, max_length=4)


_SYSTEM_SYNTHESIS = """You are the active Auteur creative synthesis agent. The author has selected one to three creative developments of a working narrative architecture and asks what they could become across the Series. Your reading is advisory: it is not canon, not an applied revision, not a commitment, and it changes no record.

The request holds the developments' own wording, the Working Book elements that cite them, the links among them, any accepted reconsiderations offered as handoffs, and, when the author gave one, the culmination the author named. Cite only the identifiers the request gives (E-numbers). Excerpts are shown as excerpts; never present an excerpt as the whole record.

Reason about a trajectory, not a list of events. For each stage say what becomes available (the earlier condition that makes it possible, cited), and what it changes in what the earlier developments mean or make possible. Label each stage's basis: recorded (the cited record states it), inferred (it follows from the record, and you say how), or proposed (a new development that the record does not contain; state it conditionally and do not name new people, places or factions the author has not given). A book number is a placement in an existing Book, not a claim of chronology, and a stage beyond the existing Books is a proposed_book with no book number.

Relations: use prerequisite only for what the later development cannot occur without; preparation for what makes it richer or easier. Say whether the dependence is causal, thematic, sequential_only or none. Use interference and incompatibility only where the record shows one development constraining another. Give alternative paths that change the order or the condition of the developments, and say whether each stays viable.

If the author named a culmination, reason about it backward (what it needs) and forward (what the earlier developments already make possible), separate necessary conditions from enrichment, and state what the earlier Books keep as their own experience if the culmination never arrives. Earlier Books must remain meaningful in their own right.

Criticism is evidence to weigh, not a verdict. Assess each criticism the request supplies, by its identifier, as accepted, partly_accepted, rejected or unresolved, with a reason. A follow-up request may give an earlier judgement as text: it is not evidence, so cite nothing from it, and state in changes_from_prior what changed and why.

Keep what the record establishes, what you infer, what you propose and what remains open distinct. Leave decisions the author should make as open_decisions. Do not claim the synthesis is accepted, applied or canonical.

Return ONLY one JSON object with these keys: schema_version (1), trajectory, relations, culmination (an object, or null when the author named none and you offer none), alternative_paths, opportunities, reader_experience, open_decisions, uncertainty, criticism_assessments, changes_from_prior. Field names and literal values are exact, as the output_contract gives them."""


class _Packet:
    """The owner's bounded packet: the evidence the answer may cite, and the request's user payload."""

    def __init__(self, user: dict[str, Any], evidence: list[dict[str, Any]], developments: list[dict[str, Any]]):
        self.user = user
        self.evidence = evidence
        self.developments = developments
        self.evidence_sha256 = _digest(evidence)


def _root(store: CanvasStore):
    return arch._root(store) / "synthesis"


def _evidence(identifier_number: int, kind: str, source: str, owner: str, freshness: str, text: str, limit: int = RECORD_TEXT_LIMIT,
              version_sha256: str | None = None, **fields: Any) -> dict[str, Any]:
    # The fingerprint covers the whole source the owner read, not only the excerpt the packet supplies: a change beyond the excerpt
    # is still a change to the material this synthesis reads, and would otherwise leave the standing current.
    return {"id": f"E{identifier_number}", "kind": kind, "source": source, "owner": owner, "freshness": freshness,
            "version_sha256": version_sha256, "source_sha256": _digest(text), "truncated": len(text) > limit,
            "text": text[:limit], **fields}


def _development_from_question(store: CanvasStore, ref: str) -> dict[str, Any]:
    rows = {row["id"]: row for row in project_architecture_questions(store)["questions"]}
    row = rows.get(ref)
    if row is None:
        raise ValueError(f"the current Architecture has no question {ref!r}")
    if row["standing"] != "continuing":
        raise ValueError(f"question {ref!r} is not a continuing question of the current Architecture")
    text = str(row["text"])
    return {"kind": "question", "ref": ref, "title": text[:80], "text": text, "question_ids": [ref], "node_ids": [],
            "link": None, "version_sha256": _digest(text), "source": "architecture_question"}


def _development_from_mechanism(store: CanvasStore, ref: str) -> dict[str, Any]:
    candidate = arch._candidate(store)["candidate"]
    node = next((row for row in candidate.get("nodes", []) if row.get("id") == ref), None)
    if node is not None:
        return {"kind": "mechanism", "ref": ref, "title": str(node.get("title") or ref), "text": json.dumps(node, ensure_ascii=False,
                sort_keys=True), "question_ids": [], "node_ids": [ref], "link": None, "version_sha256": _digest(node),
                "source": "architecture_node"}
    link = next((row for row in candidate.get("links", []) if row.get("id") == ref), None)
    if link is None:
        raise ValueError(f"the current Architecture has no mechanism {ref!r}")
    return {"kind": "mechanism", "ref": ref, "title": str(link.get("function") or ref),
            "text": json.dumps(link, ensure_ascii=False, sort_keys=True), "question_ids": [], "node_ids": [],
            "link": (link["source"], link["target"]), "version_sha256": _digest(link), "source": "architecture_link"}


def _development_from_alternative(store: CanvasStore, ref: str) -> dict[str, Any]:
    """The creative alternative a revision adopted, read in full from that revision request (its exact recorded wording)."""
    request = load_host_agent_request(arch._root(store) / "requests" / ref / "request.json")
    selected = json.loads(request.user).get("selected_creative_alternative")
    if not selected:
        raise ValueError("that revision adopted no creative alternative")
    text = f"{selected.get('title', '')}. {selected.get('description', '')}"
    return {"kind": "creative_alternative", "ref": ref, "title": str(selected.get("title") or ref), "text": text,
            "question_ids": [row["id"] for row in selected.get("considered_questions") or []],
            "node_ids": [row["id"] for row in selected.get("considered_mechanisms") or []], "link": None,
            "version_sha256": request.request_sha256, "source": "revision_request", "hypothesis_id": selected.get("hypothesis_id")}


def _resolve_development(store: CanvasStore, selection: dict[str, Any]) -> dict[str, Any]:
    kind, ref = selection.get("kind"), selection.get("ref")
    if kind not in DEVELOPMENT_KINDS or not isinstance(ref, str) or not ref:
        raise ValueError(f"a development is named by one of {', '.join(DEVELOPMENT_KINDS)} and its reference")
    if kind == "question":
        return _development_from_question(store, ref)
    if kind == "mechanism":
        return _development_from_mechanism(store, ref)
    return _development_from_alternative(store, ref)


def _cites(development: dict[str, Any], element: dict[str, Any]) -> bool:
    refs = set(element.get("series_refs") or [])
    questions = set(element.get("question_refs") or [])
    if questions & set(development["question_ids"]):
        return True
    if development["node_ids"] and refs & set(development["node_ids"]):
        return True
    if development.get("link") is not None:
        source, target = development["link"]
        return development["ref"] in refs or {source, target} <= refs
    return False


def _packet_for(store: CanvasStore, inputs: dict[str, Any]) -> _Packet:
    """The packet for these inputs, read now. Raises ValueError when a named development is no longer in the Architecture."""
    developments = [_resolve_development(store, selection) for selection in inputs["developments"]]
    evidence: list[dict[str, Any]] = []

    def add(kind: str, source: str, owner: str, freshness: str, text: str, **fields: Any) -> str:
        item = _evidence(len(evidence) + 1, kind, source, owner, freshness, text, **fields)
        evidence.append(item)
        return item["id"]

    rows: list[dict[str, Any]] = []
    for number, development in enumerate(developments, start=1):
        identifier = add("development", development["source"], "the Architecture or the revision that adopted it",
                         "as_adopted" if development["kind"] == "creative_alternative" else "current_read", development["text"],
                         version_sha256=development["version_sha256"], development=f"d{number}")
        rows.append({"id": f"d{number}", "kind": development["kind"], "ref": development["ref"], "title": development["title"],
                     "evidence": identifier, "text_sha256": development["version_sha256"]})

    culmination_text = inputs.get("culmination")
    if culmination_text:
        add("author_culmination", "author", "the author, on the canvas", "author_current", culmination_text,
            limit=CULMINATION_CHARS)
    vision = next((item.content for item in store.load().items if item.id == "story-vision"), "")
    if vision and vision.strip():
        add("author_vision", "author", "the author, Story Vision", "author_current", vision, limit=VISION_LIMIT)

    cited_elements: dict[tuple[int, str], dict[str, Any]] = {}
    considered = 0
    readable_books: list[int] = []
    books_of_text: dict[str, set[int]] = {}
    for number in book_numbers(store):
        readable_books.append(number)
        for element in book_elements(store, number):
            considered += 1
            books_of_text.setdefault(_digest(str(element.get("text") or "")), set()).add(number)
            matched = [index for index, development in enumerate(developments) if _cites(development, element)]
            if matched:
                cited_elements[(number, element["id"])] = {"element": element, "developments": matched}
    counts: dict[str, Any] = {"books_read": readable_books, "elements_read": considered, "citing_elements_by_development": {}}
    # Exact fact, not judgement: a cited element whose content is identical to an element of another Book. The owner states it so a
    # reading does not mistake a repeated record for a new development.
    repeats = [{"book": number, "element_id": element_id,
                "same_text_in_books": sorted(books_of_text[_digest(str(value["element"].get("text") or ""))] - {number})}
               for (number, element_id), value in sorted(cited_elements.items())
               if books_of_text[_digest(str(value["element"].get("text") or ""))] - {number}]
    counts["same_text_elsewhere"] = {"count": len(repeats), "listed": repeats[:2 * MAX_ELEMENTS_PER_DEVELOPMENT],
                                     "listing_truncated": len(repeats) > 2 * MAX_ELEMENTS_PER_DEVELOPMENT}
    ordered = sorted(cited_elements.items(), key=lambda pair: (pair[0][0], pair[0][1]))
    for index, development in enumerate(developments):
        citing = [key for key, value in ordered if index in value["developments"]]
        counts["citing_elements_by_development"][f"d{index + 1}"] = {
            "citing": len(citing), "excerpted": min(len(citing), MAX_ELEMENTS_PER_DEVELOPMENT),
            "listing_truncated": len(citing) > MAX_ELEMENTS_PER_DEVELOPMENT}
    shown_per_development: dict[int, int] = {}
    for (number, element_id), value in ordered:
        owners = value["developments"]
        if all(shown_per_development.get(index, 0) >= MAX_ELEMENTS_PER_DEVELOPMENT for index in owners):
            continue
        for index in owners:
            shown_per_development[index] = shown_per_development.get(index, 0) + 1
        element = value["element"]
        text = str(element.get("text") or element.get("title") or "")
        add("book_element", "working_book", "Working Book owner, read now", "current_read", text, limit=ELEMENT_TEXT_LIMIT,
            book=number, element_id=element_id, cites=[f"d{index + 1}" for index in owners],
            epistemic_status=element.get("epistemic_status"), attribution=element.get("attribution"))
    add("coverage", "working_book", "Working Book owner, read now", "current_read", json.dumps(counts, ensure_ascii=False,
        sort_keys=True), coverage=counts)

    node_ids = {node for development in developments for node in development["node_ids"]}
    candidate = arch._candidate(store)["candidate"]
    for link in candidate.get("links", []):
        if link.get("source") in node_ids and link.get("target") in node_ids:
            add("link", "architecture", "the Architecture, current", "current_read", json.dumps(link, ensure_ascii=False,
                sort_keys=True), link_id=link.get("id"))
            if sum(1 for item in evidence if item["kind"] == "link") >= MAX_LINKS:
                break

    handoffs = []
    for sha in inputs.get("handoffs") or []:
        handoff = reconsideration_handoff(store, sha)
        judgement = (f"{handoff['disposition']}: {handoff['reconsidered_judgment']} Remaining uncertainty: "
                     + "; ".join(handoff["remaining_uncertainty"]))
        identifier = add("handoff", "reconsideration", "reconsideration owner: accepted judgement, advisory", handoff["standing"],
                         judgement, version_sha256=handoff["reconsideration_request_sha256"],
                         analysis_request_sha256=handoff["analysis_request_sha256"], claim=handoff["claim"],
                         reconsideration_request_sha256=handoff["reconsideration_request_sha256"])
        handoffs.append({"evidence": identifier, "reconsideration_request_sha256": sha, "standing": handoff["standing"]})

    criticism = [{"id": f"c{number}", "text": text} for number, text in enumerate(inputs.get("criticism") or [], start=1)]
    prior = None
    if inputs.get("prior_request_sha256"):
        prior_result = arch._read(_root(store) / "requests" / inputs["prior_request_sha256"] / "result.json")
        if prior_result is None:
            raise ValueError("the earlier synthesis is not completed, so there is no judgement to follow")
        prior = {"request_sha256": inputs["prior_request_sha256"],
                 "trajectory": [{"ref": f"s{index}", "book": stage["book"], "development": stage["development"]}
                                for index, stage in enumerate(prior_result["answer"]["trajectory"], start=1)],
                 "note": "Earlier judgement, not evidence: cite no identifier from it."}

    user = {
        "operation": "synthesize_development",
        "question": inputs["question"],
        "culmination_requested": bool(culmination_text),
        "developments": rows,
        "existing_books": readable_books,
        "evidence": evidence,
        "allowed_evidence": [item["id"] for item in evidence],
        "criticism": criticism,
        "handoffs": handoffs,
        "prior_judgement": prior,
    }
    return _Packet(user, evidence, rows)


def _normalized_selections(developments: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"kind": str(item.get("kind")), "ref": str(item.get("ref"))} for item in developments]


def prepare_architecture_synthesis(store: CanvasStore, *, question: str, developments: list[dict[str, Any]],
                                   culmination: str | None = None, handoffs: list[str] | None = None,
                                   criticism: list[str] | None = None, prior_request_sha256: str | None = None) -> dict[str, Any]:
    """Prepare one synthesis of selected developments. Explicit only; nothing is executed, applied or accepted."""
    text = (question or "").strip()
    if not text:
        raise ValueError("a synthesis needs the question the author wants to understand")
    if len(text) > QUESTION_CHARS:
        raise ValueError(f"a synthesis question is at most {QUESTION_CHARS} characters")
    if not 1 <= len(developments) <= MAX_DEVELOPMENTS:
        raise ValueError(f"a synthesis reads one to {MAX_DEVELOPMENTS} developments")
    culmination_text = (culmination or "").strip() or None
    if culmination_text and len(culmination_text) > CULMINATION_CHARS:
        raise ValueError(f"a named culmination is at most {CULMINATION_CHARS} characters")
    handoff_list = list(dict.fromkeys(handoffs or []))
    if len(handoff_list) > MAX_HANDOFFS:
        raise ValueError(f"a synthesis takes at most {MAX_HANDOFFS} reconsiderations as handoffs")
    criticism_texts = [item.strip() for item in (criticism or []) if item and item.strip()]
    if len(criticism_texts) > MAX_CRITICISM:
        raise ValueError(f"a synthesis weighs at most {MAX_CRITICISM} criticisms")
    selections = _normalized_selections(developments)
    if prior_request_sha256:
        prior_folder = _root(store) / "requests" / prior_request_sha256
        if not (prior_folder / "request.json").exists():
            raise ValueError("no earlier synthesis is recorded under that request")
        if arch._read(prior_folder / "result.json") is None:
            raise ValueError("the earlier synthesis is not completed, so there is no judgement to follow")
        prior_inputs = json.loads(load_host_agent_request(prior_folder / "request.json").user)["inputs"]
        if _normalized_selections(prior_inputs["developments"]) != selections:
            raise ValueError("a follow-up continues the same developments as the synthesis it follows")
    inputs = {"question": text, "developments": selections, "culmination": culmination_text, "handoffs": handoff_list,
              "criticism": criticism_texts, "prior_request_sha256": prior_request_sha256}
    with arch._FilesystemLock(store._path(".canvas.lock")):
        packet = _packet_for(store, inputs)
        user_payload = {**packet.user, "inputs": inputs}
        user_text = json.dumps(user_payload, ensure_ascii=False, sort_keys=True)
        settings = {
            "operation": "synthesize_architecture_development",
            "inputs_sha256": _digest(inputs),
            "developments_sha256": _digest(selections),
            "question_sha256": _digest(text),
            "culmination_sha256": _digest(culmination_text) if culmination_text else None,
            "handoffs_sha256": _digest(handoff_list),
            "criticism_sha256": _digest(criticism_texts),
            "prior_request_sha256": prior_request_sha256,
            "evidence_sha256": packet.evidence_sha256,
            "synthesis_schema_version": SYNTHESIS_SCHEMA_VERSION,
        }
        request = build_host_agent_request(
            candidate_id="studio-synthesis-" + _digest({"settings": settings, "user": user_text})[:24],
            role=ROLE, system=_SYSTEM_SYNTHESIS, user=user_text, settings=settings,
            output_contract=model_output_contract(SynthesisAnswer),
        )
        folder = _root(store) / "requests" / request.request_sha256
        if not (folder / "request.json").exists():
            write_host_agent_request(folder / "request.json", request)
        _atomic_json_write(_root(store) / "latest_request.json", {"request_sha256": request.request_sha256})
        pointer = _developments_pointer(store, settings["developments_sha256"])
        pointer.parent.mkdir(parents=True, exist_ok=True)
        _atomic_json_write(pointer, {"request_sha256": request.request_sha256})
        row = _row(store, folder, load_host_agent_request(folder / "request.json"))
    return {"request": request.model_dump(), "synthesis": row}


def _check_answer(answer: SynthesisAnswer, payload: dict[str, Any]) -> None:
    """Every citation resolves to evidence this request carries; every reference names a development or stage of it; each
    basis rests on cited evidence; and a named culmination is reasoned about."""
    allowed = set(payload["allowed_evidence"])
    problems: list[str] = []
    cited: list[str] = []
    for stage in answer.trajectory:
        cited += stage.evidence
    for relation in answer.relations:
        cited += relation.evidence
    for path in answer.alternative_paths:
        cited += path.evidence
    for opportunity in answer.opportunities:
        cited += opportunity.evidence
    if answer.culmination is not None:
        cited += [identifier for condition in answer.culmination.necessary + answer.culmination.enrichment
                  for identifier in condition.evidence]
    for identifier in dict.fromkeys(cited):
        if identifier not in allowed:
            problems.append(f"the answer cites {identifier}, which is not in this request")
    references = {f"d{index}" for index in range(1, len(payload["developments"]) + 1)}
    references |= {f"s{index}" for index in range(1, len(answer.trajectory) + 1)}
    for relation in answer.relations:
        for reference in relation.between:
            if reference not in references:
                problems.append(f"a relation refers to {reference}, which is not a development or stage of this synthesis")
    for opportunity in answer.opportunities:
        for reference in opportunity.between:
            if reference not in references:
                problems.append(f"an opportunity refers to {reference}, which is not a development or stage of this synthesis")
    existing = set(payload["existing_books"])
    for index, stage in enumerate(answer.trajectory, start=1):
        if stage.horizon == "existing_book":
            if stage.book not in existing:
                problems.append(f"s{index} names Book {stage.book}, which is not a Working Book of this Architecture")
        elif stage.book is not None:
            problems.append(f"s{index} is a proposed Book and must not name a Book number")
        if stage.basis in ("recorded", "inferred") and not stage.evidence:
            problems.append(f"s{index} is {stage.basis} and cites no evidence")
    for relation in answer.relations:
        if relation.kind in NECESSARY_RELATIONS and not relation.evidence:
            problems.append(f"a {relation.kind} relation cites no evidence")
    supplied = {row["id"] for row in payload["criticism"]}
    seen: set[str] = set()
    for assessment in answer.criticism_assessments:
        if assessment.criticism not in supplied:
            problems.append(f"{assessment.criticism} is not a criticism this request supplied")
        elif assessment.criticism in seen:
            problems.append(f"{assessment.criticism} is assessed more than once")
        seen.add(assessment.criticism)
    if answer.changes_from_prior and not payload.get("prior_judgement"):
        problems.append("changes_from_prior names a change from an earlier judgement; this request has none")
    if payload["culmination_requested"] and answer.culmination is None:
        problems.append("the author named a culmination; the answer must reason about it")
    _refuse(problems)


def _developments_pointer(store: CanvasStore, developments_sha256: str):
    return _root(store) / "latest_by_developments" / f"{developments_sha256}.json"


def _standing(store: CanvasStore, request_sha256: str, request) -> str:
    """``current`` while this is the latest synthesis of these developments and the material it read is unchanged; ``superseded`` when
    a later synthesis of the same developments exists (a synthesis of other developments does not supersede it); ``stale`` when the
    Architecture, the Working Book, the vision or a handoff it read has changed, or a development is gone."""
    try:
        recomputed = _packet_for(store, json.loads(request.user)["inputs"]).evidence_sha256
    except ValueError:
        return "stale"
    if recomputed != request.settings["evidence_sha256"]:
        return "stale"
    pointer = arch._read(_developments_pointer(store, request.settings["developments_sha256"]))
    latest_here = pointer.get("request_sha256") if pointer else None
    return "current" if request_sha256 == latest_here else "superseded"


def _row(store: CanvasStore, folder, request) -> dict[str, Any]:
    result = arch._read(folder / "result.json")
    standing = _standing(store, request.request_sha256, request)
    payload = json.loads(request.user)
    refused = folder / "refused"
    return {
        "schema": SCHEMA,
        "authority": AUTHORITY,
        "request_sha256": request.request_sha256,
        "standing": standing,
        "status": "ready" if result is not None else ("awaiting_host_agent" if standing == "current" else "unanswered"),
        "inputs": payload["inputs"],
        "developments": payload["developments"],
        "evidence": payload["evidence"],
        "coverage": next((item["coverage"] for item in payload["evidence"] if item["kind"] == "coverage"), None),
        "handoffs": payload["handoffs"],
        "prior_judgement": payload["prior_judgement"],
        "criticism": payload["criticism"],
        "request": request.model_dump() if result is None and standing == "current" else None,
        "result": result["answer"] if result is not None else None,
        "refused_attempts": len(list(refused.glob("*.json"))) if refused.exists() else 0,
    }


def complete_architecture_synthesis(store: CanvasStore, payload: dict) -> dict[str, Any]:
    """Validate and store the agent's synthesis of the request it names. A refused answer is kept beside its refusal."""
    with arch._FilesystemLock(store._path(".canvas.lock")):
        request_sha = payload.get("request_sha256")
        if not isinstance(request_sha, str):
            raise ValueError("a synthesis response names its request")
        folder = _root(store) / "requests" / request_sha
        if not (folder / "request.json").exists():
            raise ValueError("no synthesis request exists for that response")
        request = load_host_agent_request(folder / "request.json")
        if request.role != ROLE:
            raise ValueError("wrong synthesis role")
        response = validate_host_agent_response(request, payload)
        prior = arch._read(folder / "response.json")
        if prior and prior != response.model_dump():
            raise arch.BeginnerConcurrencyError("a different synthesis response already completed this request")
        if prior and arch._read(folder / "result.json") is not None:
            return _row(store, folder, request)
        inputs = json.loads(request.user)["inputs"]
        try:
            recomputed = _packet_for(store, inputs).evidence_sha256
        except ValueError as gone:
            raise arch.BeginnerConcurrencyError(
                f"the Architecture this synthesis reads has changed since it was prepared ({gone}); the synthesis is not stored") from gone
        if recomputed != request.settings["evidence_sha256"]:
            raise arch.BeginnerConcurrencyError(
                "the evidence this synthesis reads has changed since it was prepared; the synthesis is not stored")
        submitted = json.loads(request.user)
        try:
            answer = SynthesisAnswer.model_validate_json(response.text)
            _check_answer(answer, submitted)
        except ValueError as refusal:
            # A refused answer is kept as evidence of what was returned and refused. It never becomes the synthesis.
            refused = response.model_dump()
            directory = folder / "refused"
            directory.mkdir(parents=True, exist_ok=True)
            name = f"{len(list(directory.glob('*.json'))) + 1:02d}-{_digest(refused)[:16]}"
            _atomic_json_write(directory / f"{name}.json", refused)
            (directory / f"{name}.refusal.txt").write_text(str(refusal).strip() + "\n", encoding="utf-8")
            raise
        refused_before = len(list((folder / "refused").glob("*.json"))) if (folder / "refused").exists() else 0
        write_host_agent_response(folder / "response.json", response)
        _atomic_json_write(folder / "result.json", {
            "schema": SCHEMA,
            "authority": AUTHORITY,
            "request_sha256": request_sha,
            "evidence_sha256": request.settings["evidence_sha256"],
            "answer": answer.model_dump(mode="json"),
            "completion": {"attempt": refused_before + 1, "refused_attempts": refused_before,
                           "first_pass": refused_before == 0},
        })
        return _row(store, folder, request)


def project_architecture_synthesis(store: CanvasStore) -> dict[str, Any]:
    """Read-only: the latest synthesis with its standing, and the earlier ones, newest first."""
    base = _root(store)
    pointer = arch._read(base / "latest_request.json")
    if not pointer:
        return {"schema": SCHEMA, "authority": AUTHORITY, "status": "not_started", "standing": None, "request": None,
                "result": None, "history": []}
    latest = pointer["request_sha256"]
    rows = []
    for folder in sorted((base / "requests").iterdir()) if (base / "requests").is_dir() else []:
        if not (folder / "request.json").exists():
            continue
        request = load_host_agent_request(folder / "request.json")
        if request.role == ROLE:
            rows.append((request.created_at, folder, request))
    rows.sort(key=lambda item: item[0], reverse=True)
    history = [_row(store, folder, request) for _created, folder, request in rows[:MAX_HISTORY]]
    current = next((row for row in history if row["request_sha256"] == latest), None)
    if current is None:
        return {"schema": SCHEMA, "authority": AUTHORITY, "status": "unreadable", "standing": None, "request": None,
                "result": None, "history": history}
    return {"schema": SCHEMA, "authority": AUTHORITY, "status": current["status"], "standing": current["standing"],
            "request_sha256": latest, "request": current["request"], "result": current["result"], "history": history,
            "developments": current["developments"], "inputs": current["inputs"], "evidence": current["evidence"],
            "coverage": current["coverage"], "handoffs": current["handoffs"], "criticism": current["criticism"]}


__all__ = [
    "AUTHORITY", "ROLE", "SCHEMA", "SynthesisAnswer", "complete_architecture_synthesis", "prepare_architecture_synthesis",
    "project_architecture_synthesis",
]
