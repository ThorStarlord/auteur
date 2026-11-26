"""Consequence analysis of one pending working revision: what it keeps, transforms and may displace.

An author about to apply a reviewed working revision can ask an explicitly invoked coding agent what the proposal does to
the creative concerns the Architecture already holds. The request is built from the exact pending review: the baseline
it would replace, the proposed candidate, the question changes the owner recorded, the question history and Working Book
decisions of each examined question, the author's instruction and any chosen alternative or discovery origin. Every
fact the agent may cite has an identifier, and the owner refuses an answer that cites anything else.

The answer is advisory. It is stored as a noncanonical record beside the Architecture and changes no Architecture,
review, Working Book or accepted record. Apply is never gated by it: a deliberately transformative revision is not
blocked. A deterministic comparison says what changed; only the agent says what that may mean, and the owner never judges
that two wordings mean the same thing or that a concern was intentionally abandoned.

An analysis is about the exact proposal it examined. Its standing is read at each projection, never stored: ``current``
while that proposal is still the pending review on the same baseline, ``applied`` once it has been applied, ``superseded``
when another revision has replaced it, and ``stale_context`` when the source or design guidance changed. Only ``current``
is presented as about the proposal on screen.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from auteur.host_agent import (
    _atomic_json_write, build_host_agent_request, load_host_agent_request, validate_host_agent_response,
    write_host_agent_request, write_host_agent_response,
)
from auteur.series.working_book_architecture import book_numbers, book_series_references

from . import studio_architecture as arch
from .studio_architecture_deliberation import _book_item, _history_for, deliberation_standing
from .studio_architecture_question_projection import project_architecture_questions
from .studio_architecture_questions import text_digest
from .studio_store import CanvasStore

SCHEMA = "studio-revision-consequence/1"
ROLE = "studio_architecture_consequence"
AUTHORITY = "noncanonical_consequence_analysis_not_working_architecture"

# Bounds. Every limit the answer must respect is a named constant here, and the instruction is generated from them.
MAX_CONCERNS = 6
MAX_PROSPECTIVE = 4
MAX_ALTERNATIVES = 4
MAX_EVIDENCE_PER_CONCERN = 6
MAX_EXAMINED_QUESTIONS = 4
MAX_BOOK_DECISIONS = 4
MAX_COMPONENTS = 10
MAX_PHASES = 10
MAX_BOOK_TITLES = 12
MAX_CONSTRAINTS = 6
MAX_COUNTEREVIDENCE = 3
MAX_NOT_ESTABLISHED = 6
MAX_HISTORY = 8
INSTRUCTION_LIMIT = 1200
VISION_LIMIT = 800
TEXT_LIMIT = 600
REASON_LIMIT = 400
DISCOVERY_LIMIT = 600
READING_LIMIT = 900
CONCERN_TITLE_LIMIT = 120
CONCERN_READING_LIMIT = 600
CONCERN_SIDE_LIMIT = 400
COUNTER_LIMIT = 240
PROSPECT_LIMIT = 500
APPROACH_TITLE_LIMIT = 120
APPROACH_SUMMARY_LIMIT = 500
APPROACH_GAINS_LIMIT = 300
APPROACH_COSTS_LIMIT = 300
NEXT_LIMIT = 300
NOT_ESTABLISHED_LIMIT = 240
NO_CONCERN_LIMIT = 400
ITEM_LIMIT = 240

ConcernStatus = Literal["preserved", "transformed", "possibly_displaced", "introduced"]
IntentBasis = Literal["instruction_names_it", "selected_alternative_names_it", "not_established"]
Approach = Literal["replace", "integrate", "separate", "retain", "defer", "reframe"]
ProspectKind = Literal["recorded_relationship", "proposed_possibility"]

EvidenceId = Annotated[str, StringConstraints(pattern=r"^E[1-9][0-9]{0,2}$")]
QuestionId = Annotated[str, StringConstraints(min_length=1, max_length=80)]
ItemText = Annotated[str, StringConstraints(min_length=1, max_length=COUNTER_LIMIT)]

_SYSTEM = f"""You are the active Auteur consequence-analysis agent. The author is considering a proposed working revision of
the narrative Architecture. The revision has been reviewed but NOT applied. Your task is to help the author understand what
the proposal accomplishes; which earlier creative concerns it keeps, transforms or may displace; what it may make possible or
require reconsidering in later Books; and which developable alternatives exist. You are not judging whether the proposal is
right. Deliberate transformation is legitimate: a concern may be replaced, separated, combined or abandoned on purpose. Do not
presume that preserving every earlier concern is better, and do not presume that integration is better than separation.

Read the baseline candidate (the applied working Architecture), the proposed candidate (the un-applied revision) and the
consequence packet. The packet's evidence list gives items E1, E2 and so on. Each is a fact the owners recorded, or a
deterministic comparison of the two candidates. Cite evidence only by these identifiers. Keep apart what the record shows
(cite it), what you interpret (say so) and what the record cannot establish (say so in not_established). A changed wording does
not prove a changed meaning, and an unchanged identity does not prove an unchanged concern. A book_decision whose
proposal_status is not unchanged refers to a question the proposal changes: that is a recorded relationship by identity, not a
demonstrated contradiction. A Working Book the coverage note lists only by title was not read for its decisions, and that is not
evidence that it is unaffected. A named_gap is missing history: never fill it in.

Return ONLY a JSON object with these keys:
- schema_version: 1
- reading: what the proposal accomplishes and what it changes, in plain words. Required, at most {READING_LIMIT} characters.
- concerns: 0 to {MAX_CONCERNS} objects. Each has title (at most {CONCERN_TITLE_LIMIT} characters); status, one of preserved,
  transformed, possibly_displaced or introduced; earlier and proposed (optional, at most {CONCERN_SIDE_LIMIT} characters each: how
  the concern was formulated before and how the proposal formulates or displaces it); reading (required, at most
  {CONCERN_READING_LIMIT} characters); evidence (1 to {MAX_EVIDENCE_PER_CONCERN} identifiers); intent (required for transformed and
  possibly_displaced: instruction_names_it, selected_alternative_names_it or not_established; instruction_names_it must cite the
  instruction item, and selected_alternative_names_it must cite the selected_alternative item; never assert an intent the evidence
  does not show; omit intent for preserved and introduced); counterevidence (0 to {MAX_COUNTEREVIDENCE} strings, each at most
  {COUNTER_LIMIT} characters); competing_reading (optional, at most {CONCERN_SIDE_LIMIT} characters).
  Status meanings: preserved, the concern is still represented; transformed, it is still in play but its formulation or function has
  changed; possibly_displaced, it may no longer be represented or may need separate consideration, and the record may not establish
  whether that was intended; introduced, a new uncertainty, tension or opportunity the proposal brings. A concern is never given a new
  identity by you.
- no_concern_reason: required when concerns is empty (at most {NO_CONCERN_LIMIT} characters): say why no concern is consequential. Do
  not produce repetitive assessments for trivial wording changes.
Evidence rules, enforced exactly as written. Cite only the items that bear on the concern, and cite each kind of item it needs:
preserved needs at least one cited item; introduced needs at least one proposed_wording or proposed_component item;
possibly_displaced needs at least one baseline_wording, recorded_history or book_decision item; transformed needs at least one
earlier-side item (baseline_wording, recorded_history or book_decision) AND at least one proposed-side item (proposed_wording,
proposed_component or removed). Concern titles are distinct from one another. An alternative names two or three distinct question
ids, each one of baseline_question_ids, and its title is distinct from the other alternatives' titles.
- prospective: 0 to {MAX_PROSPECTIVE} objects. Each has kind, recorded_relationship (must cite a book_decision or recorded_history
  item) or proposed_possibility; text (at most {PROSPECT_LIMIT} characters); evidence (0 to 4 identifiers).
- alternatives: 0 to {MAX_ALTERNATIVES} objects. Each has approach, one of replace, integrate, separate, retain, defer or reframe;
  title (at most {APPROACH_TITLE_LIMIT} characters); summary (at most {APPROACH_SUMMARY_LIMIT} characters); questions (two or three
  question ids, each one of the baseline_question_ids the packet lists); gains (at most {APPROACH_GAINS_LIMIT} characters); costs
  (at most {APPROACH_COSTS_LIMIT} characters); next_investigation (at most {NEXT_LIMIT} characters). Every approach states its costs as
  well as its gains. Name what each approach keeps, and for separate, name the questions it keeps: a distinct question it would
  introduce is described in the summary and is not given an identity. If you recommend one approach, say why it is stronger than the
  others here.
- not_established: 0 to {MAX_NOT_ESTABLISHED} strings, each at most {NOT_ESTABLISHED_LIMIT} characters.

Use only the evidence identifiers and question ids the packet gives. Do not invent narrative facts, Book content or future events.
A proposed_possibility and an alternative are the only places for speculation, and each must be labelled as such. Never state or imply
that the proposal is accepted, applied or canonical, and never say that a Working Book has been changed by this analysis."""


class ConsequenceConcern(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    title: str = Field(min_length=1, max_length=CONCERN_TITLE_LIMIT)
    status: ConcernStatus
    earlier: str | None = Field(default=None, max_length=CONCERN_SIDE_LIMIT)
    proposed: str | None = Field(default=None, max_length=CONCERN_SIDE_LIMIT)
    reading: str = Field(min_length=1, max_length=CONCERN_READING_LIMIT)
    evidence: list[EvidenceId] = Field(min_length=1, max_length=MAX_EVIDENCE_PER_CONCERN)
    intent: IntentBasis | None = None
    counterevidence: list[ItemText] = Field(default_factory=list, max_length=MAX_COUNTEREVIDENCE)
    competing_reading: str | None = Field(default=None, max_length=CONCERN_SIDE_LIMIT)

    @model_validator(mode="after")
    def intent_only_where_it_is_asked(self) -> "ConsequenceConcern":
        if self.status in ("transformed", "possibly_displaced") and self.intent is None:
            raise ValueError("a transformed or possibly displaced concern states its intent basis")
        if self.status in ("preserved", "introduced") and self.intent is not None:
            raise ValueError("intent applies only to a transformed or possibly displaced concern")
        return self


class ConsequenceProspect(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    kind: ProspectKind
    text: str = Field(min_length=1, max_length=PROSPECT_LIMIT)
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=4)


class ConsequenceAlternative(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    approach: Approach
    title: str = Field(min_length=1, max_length=APPROACH_TITLE_LIMIT)
    summary: str = Field(min_length=1, max_length=APPROACH_SUMMARY_LIMIT)
    questions: list[QuestionId] = Field(min_length=2, max_length=3)
    gains: str = Field(min_length=1, max_length=APPROACH_GAINS_LIMIT)
    costs: str = Field(min_length=1, max_length=APPROACH_COSTS_LIMIT)
    next_investigation: str = Field(min_length=1, max_length=NEXT_LIMIT)

    @model_validator(mode="after")
    def distinct_questions(self) -> "ConsequenceAlternative":
        if len(set(self.questions)) != len(self.questions):
            raise ValueError("an alternative names each question once")
        return self


class ConsequenceAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    reading: str = Field(min_length=1, max_length=READING_LIMIT)
    concerns: list[ConsequenceConcern] = Field(default_factory=list, max_length=MAX_CONCERNS)
    no_concern_reason: str | None = Field(default=None, max_length=NO_CONCERN_LIMIT)
    prospective: list[ConsequenceProspect] = Field(default_factory=list, max_length=MAX_PROSPECTIVE)
    alternatives: list[ConsequenceAlternative] = Field(default_factory=list, max_length=MAX_ALTERNATIVES)
    not_established: list[str] = Field(default_factory=list, max_length=MAX_NOT_ESTABLISHED)

    @model_validator(mode="after")
    def empty_concerns_say_why(self) -> "ConsequenceAnswer":
        if not self.concerns and not (self.no_concern_reason or "").strip():
            raise ValueError("an analysis with no concern must say why in no_concern_reason")
        for text in self.not_established:
            if not text.strip() or len(text) > NOT_ESTABLISHED_LIMIT:
                raise ValueError(f"each not_established item is text under {NOT_ESTABLISHED_LIMIT} characters")
        return self


def _clip(text: Any, limit: int = TEXT_LIMIT) -> str | None:
    if text is None:
        return None
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _root(store: CanvasStore):
    return arch._root(store) / "consequences"


def _discovery_possibility(store: CanvasStore, origin: dict) -> dict | None:
    """The possibility a discovery origin names, read from its completed discovery result (text only; never judged)."""
    sha = origin.get("request_sha256")
    if not isinstance(sha, str):
        return None
    result = arch._read(arch._root(store) / "discoveries" / "requests" / sha / "result.json") or {}
    return next((row for row in result.get("possibilities", []) if row.get("id") == origin.get("possibility_id")), None)


def build_consequence_packet(store: CanvasStore, review: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    """The bounded, ID-cited evidence for one pending revision. Read-only; raises ValueError when no baseline is readable.

    The packet names each fact it gives the agent. A question's history and Book decisions come from the same owner reads
    the deliberation uses; ``proposal_status`` on a Book decision is the deterministic change of its question in the
    proposal (an identity fact), never a judgement of meaning.
    """
    proposed = review["candidate"]
    view = project_architecture_questions(store)
    if not view["available"]:
        raise ValueError("no current working architecture")
    continuing = {question["id"]: question for question in view["questions"] if question["standing"] == "continuing"}
    changes = review.get("question_changes") or {}
    rows = {row["id"]: row for row in changes.get("questions", []) if row.get("id")}
    removed = {row["id"]: row for row in changes.get("removed", [])}
    chosen = review.get("selected_creative_alternative") or {}
    considered = [row["id"] for row in chosen.get("considered_questions") or []]

    # What is examined first: a deliberate removal, then rewordings and introductions, then the questions the instruction
    # considered. A question that moved only in position is not a change of wording, and a removal or introduction shifts the
    # positions of later questions: those shifts must not crowd the change itself out of the examined set.
    changed = list(removed) + [identifier for identifier, row in rows.items()
                               if row["status"] in ("reworded", "moved_and_reworded", "introduced")]
    examined = list(dict.fromkeys(changed + [identifier for identifier in considered]))
    questions_omitted = max(0, len(examined) - MAX_EXAMINED_QUESTIONS)
    examined = examined[:MAX_EXAMINED_QUESTIONS]

    evidence: list[dict[str, Any]] = []

    def add(kind: str, text: Any, limit: int = TEXT_LIMIT, **fields: Any) -> str:
        identifier = f"E{len(evidence) + 1}"
        evidence.append({"id": identifier, "kind": kind, "text": _clip(text, limit), **fields})
        return identifier

    requested = str(review.get("requested_change") or "")
    if requested.strip():
        add("instruction", requested, INSTRUCTION_LIMIT, sha256=text_digest(requested))
    if chosen:
        add("selected_alternative",
            f"{chosen.get('title', '')}. {chosen.get('description', '')}", TEXT_LIMIT,
            hypothesis_id=chosen.get("hypothesis_id"), inquiry_request_sha256=chosen.get("inquiry_request_sha256"),
            considered_questions=considered)
    origin = chosen.get("from_discovery")
    if isinstance(origin, dict):
        possibility = _discovery_possibility(store, origin) or {}
        add("discovery_origin",
            f"{origin.get('title', '')}. {possibility.get('possibility', '')}", DISCOVERY_LIMIT,
            request_sha256=origin.get("request_sha256"), possibility_id=origin.get("possibility_id"),
            questions=possibility.get("questions", []))
    vision = next((item.content for item in store.load().items if item.id == "story-vision"), "")
    if vision and vision.strip():
        add("author_vision", vision, VISION_LIMIT)
    preserved = review.get("preserved") or {}
    constraints = list(preserved.get("accepted_constraints") or [])
    not_this = list(preserved.get("accepted_not_this") or [])
    for text in constraints[:MAX_CONSTRAINTS]:
        add("accepted_constraint", text, ITEM_LIMIT)
    for text in not_this[:MAX_CONSTRAINTS]:
        add("accepted_not_this", text, ITEM_LIMIT)

    examined_books: set[int] = set()
    examined_rows = []
    for identifier in examined:
        status = rows[identifier]["status"] if identifier in rows else (
            "removed" if identifier in removed else "not_in_proposal")
        baseline_question = continuing.get(identifier)
        row_view: dict[str, Any] = {"id": identifier, "proposal_status": status, "baseline_evidence": [],
                                    "proposed_evidence": [], "history_items_omitted": 0, "book_decisions_omitted": 0}
        if baseline_question is not None:
            wording = add("baseline_wording", baseline_question["text"], question_id=identifier,
                          index=baseline_question["index"])
            row_view["baseline_evidence"].append(wording)
            history, omitted_history = _history_for(baseline_question)
            row_view["history_items_omitted"] = omitted_history
            for item in history:
                if item.get("basis") == "named_gap":
                    # An unreadable version is said to be unreadable, never left as an empty item.
                    add("named_gap", item.get("note") or item.get("gap") or
                        "A recorded version of this question cannot be read, so its wording is not shown.",
                        question_id=identifier, gap=item.get("gap") or "unreadable_version")
                    continue
                reason = item.get("reason") or {}
                label = item.get("text")
                if label is None and item.get("kind") == "absent":
                    label = "The question was not recorded in this version."
                # The owner's reason item carries the author's instruction under "instruction" (or a named gap with no instruction).
                row_view["baseline_evidence"].append(add(
                    "recorded_history", label, question_id=identifier, basis=item.get("basis"),
                    change=item.get("change"), from_revision=item.get("from_revision"), to_revision=item.get("to_revision"),
                    recorded_reason=reason.get("instruction"),
                    selected_alternative=(reason.get("selected_alternative") or {}).get("title"),
                    note=reason.get("note") or item.get("note")))
            entries = sorted(baseline_question["books"], key=lambda entry: (entry["book_number"], entry["decision_id"]))
            # Every Book that records a decision on an examined question was read for it, even when its decision is beyond the
            # display limit, which is counted and not shown.
            examined_books.update(entry["book_number"] for entry in entries)
            shown = entries[:MAX_BOOK_DECISIONS]
            row_view["book_decisions_omitted"] = max(0, len(entries) - len(shown))
            book_rows = [_book_item(entry) for entry in shown]
            standing = {(row["book_number"], row["decision_id"]): row["standing"] for row in deliberation_standing(
                store, {"questions": [{"id": identifier, "books": book_rows}]})}
            for book in book_rows:
                row_view["baseline_evidence"].append(add(
                    "book_decision", book.get("decision_text") or "", question_id=identifier,
                    book_number=book["book_number"], title=book["title"], decision_id=book["decision_id"],
                    state=book["state"], identity_basis=book["identity_basis"],
                    standing=standing.get((book["book_number"], book["decision_id"])),
                    recorded_text=(book["recorded"] or {}).get("text"),
                    current_text=(book["current"] or {}).get("text") if book.get("current") else None,
                    proposal_status=status))
        if identifier in rows:
            row = rows[identifier]
            row_view["proposed_evidence"].append(add(
                "proposed_wording", row["text"], question_id=identifier, index=row["index"],
                proposal_status=status, previous_text=row.get("previous_text")))
        if identifier in removed:
            row_view["proposed_evidence"].append(add(
                "removed", removed[identifier]["previous_text"], question_id=identifier, proposal_status="removed"))
        examined_rows.append(row_view)

    components = list(review.get("changed_components") or [])
    for component in components[:MAX_COMPONENTS]:
        add("proposed_component",
            f"{component.get('kind')} · {component.get('title')} ({component.get('change')}): "
            f"{component.get('before')} -> {component.get('after')}",
            component_kind=component.get("kind"), component_id=component.get("id"))

    phases = list((baseline.get("phases") or []))
    for phase in phases[:MAX_PHASES]:
        add("recorded_phase", f"{phase.get('order')}. {phase.get('title')}: {phase.get('narrative_function')}",
            phase_id=phase.get("id"))

    unreadable_books = [row["book_number"] for row in view["books"]["unreadable"]]
    for number in unreadable_books:
        add("named_gap", f"Working Book {number} cannot be read, so its references are not shown.",
            gap="book_unreadable", book_number=number)
    readable_books = []
    for number in book_numbers(store):
        if number in unreadable_books:
            continue
        try:
            title = book_series_references(store, number)["title"]
        except Exception:  # noqa: BLE001 - one Book's damage is reported for that Book only
            add("named_gap", f"Working Book {number} cannot be read, so its references are not shown.",
                gap="book_unreadable", book_number=number)
            continue
        readable_books.append((number, title))
    for number, title in readable_books[:MAX_BOOK_TITLES]:
        add("working_book", f"Book {number}: {title}", book_number=number,
            records_examined_decisions=number in examined_books)
    if not view["history"]["chain_complete"]:
        add("named_gap", "The revision history cannot be read whole, so no earlier version is numbered.",
            gap="chain_incomplete")

    packet: dict[str, Any] = {
        "schema": SCHEMA,
        "authority": AUTHORITY,
        "proposal": {
            "revision_request_sha256": review["request_sha256"],
            "baseline_request_sha256": review.get("prior_request_sha256"),
            "proposal_sha256": _digest(proposed),
            "baseline_candidate_sha256": _digest(baseline),
            "requested_change_sha256": text_digest(requested) if requested.strip() else None,
            "proposed_summary": (review.get("proposed_rationale") or {}).get("text"),
        },
        "baseline_question_ids": [question["id"] for question in view["questions"]
                                  if question["standing"] == "continuing"],
        "examined_questions": examined_rows,
        "evidence": evidence,
        "coverage": {
            # Only the titles actually shown count as read; any beyond the title limit are counted in limits, never listed.
            "books_read": [number for number, _ in readable_books[:MAX_BOOK_TITLES]],
            "books_with_decisions_on_examined_questions": sorted(examined_books),
            "books_listed_by_title_only": [number for number, _ in readable_books[:MAX_BOOK_TITLES]
                                           if number not in examined_books],
            "unreadable_books": unreadable_books,
            "note": ("A Working Book listed by title only was not read for its decisions about these questions. That is "
                     "not evidence that it is unaffected."),
        },
        "limits": {
            "examined_questions_shown": MAX_EXAMINED_QUESTIONS,
            "questions_omitted": questions_omitted,
            "book_decisions_per_question": MAX_BOOK_DECISIONS,
            "components_shown": min(len(components), MAX_COMPONENTS),
            "components_omitted": max(0, len(components) - MAX_COMPONENTS),
            "phases_shown": min(len(phases), MAX_PHASES),
            "phases_omitted": max(0, len(phases) - MAX_PHASES),
            "books_shown": min(len(readable_books), MAX_BOOK_TITLES),
            "books_omitted": max(0, len(readable_books) - MAX_BOOK_TITLES),
            "instruction_characters": INSTRUCTION_LIMIT,
            "text_characters": TEXT_LIMIT,
        },
    }
    packet["evidence_sha256"] = _digest(packet)
    return packet


def _live(store: CanvasStore, current: dict | None, request, review: dict | None) -> bool:
    """The examined proposal is still the pending review, on the same baseline, source and design guidance."""
    settings = request.settings
    if not current or current["request_sha256"] != settings["baseline_candidate_request_sha256"]:
        return False
    if arch._current_candidate_freshness(store, current) != "ready":
        return False
    if current.get("source_sha256") != settings.get("source_sha256"):
        return False
    if current.get("design_guidance_sha256") != settings.get("design_guidance_sha256"):
        return False
    if not review or review.get("request_sha256") != settings["review_request_sha256"]:
        return False
    # The pending review carries its own working context (sources, guidance, creative intentions). Apply refuses it once that
    # context changes, so an analysis of it is stale from the same moment.
    review_request = load_host_agent_request(arch._root(store) / "requests" / settings["review_request_sha256"] / "request.json")
    return not arch.review_context_changed(store, review_request)


def _standing(store: CanvasStore, request, pending: dict | None, current: dict | None, latest: bool = False) -> str:
    """The standing of one analysis against the proposal as it is now. Only the latest analysis of the pending proposal, while
    it is still live, is ``current``; an earlier analysis of that same proposal is ``superseded`` by the later one."""
    revision = request.settings["review_request_sha256"]
    if current and current["request_sha256"] == revision:
        return "applied"
    if pending and pending.get("request_sha256") == revision:
        if not _live(store, current, request, pending):
            return "stale_context"
        return "current" if latest else "superseded"
    if revision in arch.architecture_revision_chain(store)["requests"]:
        return "applied"
    return "superseded"


def prepare_architecture_consequence(store: CanvasStore) -> dict:
    """Prepare the analysis of the pending revision. Explicit only; nothing is executed and no record changes."""
    with arch._FilesystemLock(store._path(".canvas.lock")):
        current = arch._candidate(store)
        if not current:
            raise ValueError("no current working architecture")
        if arch._current_candidate_freshness(store, current) != "ready":
            raise arch.BeginnerConcurrencyError("architecture source or guidance is stale")
        projection = arch.project_architecture(store)
        review = projection.get("review")
        if projection.get("status") != "review_ready" or not review:
            raise ValueError("no pending architecture revision to analyse")
        if review.get("prior_request_sha256") != current["request_sha256"]:
            raise arch.BeginnerConcurrencyError("the pending revision was prepared against a superseded baseline")
        packet = build_consequence_packet(store, review, current["candidate"])
        context = arch._source(store, previous=current["candidate"])
        _, _, design_context = arch._design_context_parts(store, context)
        payload = {
            "operation": "consequence_analysis",
            "consequence_packet": packet,
            "baseline_candidate": current["candidate"],
            "proposed_candidate": review["candidate"],
            "narrative_design_context": design_context,
        }
        user = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        settings = {
            "operation": "analyse_consequences",
            "canvas_id": store.canvas_id,
            "review_request_sha256": review["request_sha256"],
            "baseline_candidate_request_sha256": current["request_sha256"],
            "proposal_sha256": packet["proposal"]["proposal_sha256"],
            "source_sha256": current["source_sha256"],
            "design_guidance_sha256": current.get("design_guidance_sha256"),
            "consequence_schema_version": 1,
            "evidence_sha256": packet["evidence_sha256"],
            # Each explicit invocation is its own record, so an identical request is still a new ask.
            "invocation": uuid.uuid4().hex,
        }
        request = build_host_agent_request(
            candidate_id="studio-consequence-" + _digest({"settings": settings, "user": user})[:24],
            role=ROLE, system=_SYSTEM, user=user, settings=settings,
        )
        base = _root(store)
        write_host_agent_request(base / "requests" / request.request_sha256 / "request.json", request)
        _atomic_json_write(base / "latest_request.json", {"request_sha256": request.request_sha256})
    return project_architecture_consequence(store)


def _check_answer(answer: ConsequenceAnswer, packet: dict[str, Any]) -> None:
    """Every reference resolves inside this request, and every stated basis is the one the evidence shows."""
    evidence = {item["id"]: item for item in packet["evidence"]}
    baseline_ids = set(packet["baseline_question_ids"])

    def cited_kinds(identifiers: list[str], owner: str) -> set[str]:
        for identifier in identifiers:
            if identifier not in evidence:
                raise ValueError(f"{owner} cites {identifier}, which is not in this request")
        return {evidence[identifier]["kind"] for identifier in identifiers}

    titles: set[str] = set()
    earlier = {"baseline_wording", "recorded_history", "book_decision"}
    proposed = {"proposed_wording", "proposed_component", "removed"}
    for concern in answer.concerns:
        key = " ".join(concern.title.casefold().split())
        if key in titles:
            raise ValueError(f"two concerns share the title {concern.title!r}")
        titles.add(key)
        kinds = cited_kinds(concern.evidence, f"concern {concern.title!r}")
        if concern.intent == "instruction_names_it" and "instruction" not in kinds:
            raise ValueError(f"concern {concern.title!r} says the instruction names it but cites no instruction")
        if concern.intent == "selected_alternative_names_it" and "selected_alternative" not in kinds:
            raise ValueError(f"concern {concern.title!r} says the selected alternative names it but cites none")
        # An introduced concern is new wording or a new structure. A removal is the opposite, so it never satisfies this rule.
        if concern.status == "introduced" and not kinds & {"proposed_wording", "proposed_component"}:
            raise ValueError(f"concern {concern.title!r} is introduced but cites no proposed wording or component")
        if concern.status == "possibly_displaced" and not kinds & earlier:
            raise ValueError(f"concern {concern.title!r} may be displaced but cites no earlier formulation or decision")
        if concern.status == "transformed" and not (kinds & earlier and kinds & proposed):
            raise ValueError(f"concern {concern.title!r} is transformed and must cite both its earlier and its proposed form")
    for item in answer.prospective:
        kinds = cited_kinds(item.evidence, "a prospective item")
        if item.kind == "recorded_relationship" and not kinds & {"book_decision", "recorded_history"}:
            raise ValueError("a recorded relationship must cite a Book decision or recorded history")
    alternative_titles: set[str] = set()
    for alternative in answer.alternatives:
        key = " ".join(alternative.title.casefold().split())
        if key in alternative_titles:
            raise ValueError(f"two alternatives share the title {alternative.title!r}")
        alternative_titles.add(key)
        missing = [identifier for identifier in alternative.questions if identifier not in baseline_ids]
        if missing:
            raise ValueError(f"alternative {alternative.title!r} names {', '.join(missing)}, which is not a continuing "
                             "question of the baseline")


def _with_ids(alternatives: list[dict]) -> list[dict]:
    return [{"id": f"a{index}", **row} for index, row in enumerate(alternatives, start=1)]


def complete_architecture_consequence(store: CanvasStore, payload: dict) -> dict:
    with arch._FilesystemLock(store._path(".canvas.lock")):
        base = _root(store)
        pointer = arch._read(base / "latest_request.json")
        if not pointer:
            raise ValueError("no consequence analysis request exists")
        sha = pointer["request_sha256"]
        folder = base / "requests" / sha
        request = load_host_agent_request(folder / "request.json")
        if request.role != ROLE:
            raise ValueError("wrong consequence analysis role")
        response = validate_host_agent_response(request, payload)
        prior = arch._read(folder / "response.json")
        if prior and prior != response.model_dump():
            raise arch.BeginnerConcurrencyError("a different analysis response already completed this request")
        if prior and arch._read(folder / "result.json") is not None:
            return project_architecture_consequence(store)
        # A response stored without its result (an interrupted completion) is completed now, if the proposal is still live.
        current = arch._candidate(store)
        pending = arch.project_architecture(store).get("review")
        if not _live(store, current, request, pending):
            write_host_agent_response(folder / "stale_response.json", response)
            raise arch.BeginnerConcurrencyError(
                "the pending revision, its baseline or the design context changed since this analysis was prepared; "
                "response retained as stale evidence")
        submitted = json.loads(request.user)
        try:
            answer = ConsequenceAnswer.model_validate_json(response.text)
            _check_answer(answer, submitted["consequence_packet"])
        except ValueError:
            # A refused answer is kept as evidence of what was returned and refused. It is never stored as the analysis, and a
            # corrected answer may still complete the same request.
            refused = response.model_dump()
            (folder / "refused").mkdir(parents=True, exist_ok=True)
            _atomic_json_write(folder / "refused" / f"{_digest(refused)[:16]}.json", refused)
            raise
        saved = {
            **answer.model_dump(mode="json"),
            "alternatives": _with_ids([row.model_dump(mode="json") for row in answer.alternatives]),
            "schema": SCHEMA,
            "authority": AUTHORITY,
            "revision_request_sha256": request.settings["review_request_sha256"],
            "baseline_request_sha256": request.settings["baseline_candidate_request_sha256"],
            "proposal_sha256": request.settings["proposal_sha256"],
            "evidence": submitted["consequence_packet"],
            "evidence_sha256": submitted["consequence_packet"]["evidence_sha256"],
        }
        write_host_agent_response(folder / "response.json", response)
        _atomic_json_write(folder / "result.json", saved)
    return project_architecture_consequence(store)


def _analysis_rows(store: CanvasStore, pending: dict | None, current: dict | None, limit: int, latest: str | None) -> list[dict]:
    """Completed analyses on this canvas, newest first, each with its standing read now."""
    requests_root = _root(store) / "requests"
    if not requests_root.is_dir():
        return []
    rows = []
    for folder in requests_root.iterdir():
        try:
            # One damaged folder is named by its absence, and must not hide the rest.
            result = arch._read(folder / "result.json")
            if result is None:
                continue
            request = load_host_agent_request(folder / "request.json")
        except Exception:  # noqa: BLE001
            continue
        rows.append((request.created_at, folder.name, request, result))
    rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return [{
        "request_sha256": name,
        "revision_request_sha256": request.settings["review_request_sha256"],
        "standing": _standing(store, request, pending, current, latest=(name == latest)),
        "concern_count": len(result.get("concerns", [])),
        "alternative_titles": [row["title"] for row in result.get("alternatives", [])],
    } for _created, name, request, result in rows[:limit]]


def project_architecture_consequence(store: CanvasStore) -> dict[str, Any]:
    """Read-only: the latest analysis, its standing against the pending revision as it is now, and earlier analyses."""
    projection = arch.project_architecture(store)
    pending = projection.get("review")
    current = arch._candidate(store)
    base = _root(store)
    pointer = arch._read(base / "latest_request.json")
    latest = pointer.get("request_sha256") if pointer else None
    history = _analysis_rows(store, pending, current, MAX_HISTORY, latest)
    if not pointer:
        return {"schema": SCHEMA, "authority": AUTHORITY, "status": "not_started", "standing": None, "request": None,
                "request_sha256": None, "result": None, "history": history,
                "pending_revision_request_sha256": pending["request_sha256"] if pending else None}
    sha = pointer.get("request_sha256", "")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ValueError("invalid consequence analysis pointer")
    request = load_host_agent_request(base / "requests" / sha / "request.json")
    if request.role != ROLE:
        raise ValueError("unexpected consequence analysis host role")
    try:
        result = arch._read(base / "requests" / sha / "result.json")
    except (OSError, ValueError):
        # A damaged result is named as unreadable; the earlier analyses stay readable.
        return {"schema": SCHEMA, "authority": AUTHORITY, "status": "unreadable", "standing": None, "request": None,
                "request_sha256": sha, "revision_request_sha256": request.settings["review_request_sha256"],
                "result": None, "history": history,
                "pending_revision_request_sha256": pending["request_sha256"] if pending else None}
    standing = _standing(store, request, pending, current, latest=True)
    if result is None:
        status = "awaiting_host_agent" if standing == "current" else "stale"
    else:
        status = "ready"
    return {
        "schema": SCHEMA,
        "authority": AUTHORITY,
        "status": status,
        "standing": standing,
        "request_sha256": sha,
        "revision_request_sha256": request.settings["review_request_sha256"],
        "request": request.model_dump() if result is None and standing == "current" else None,
        "result": result,
        "history": history,
        "pending_revision_request_sha256": pending["request_sha256"] if pending else None,
    }


def consequence_origin(store: CanvasStore, origin: dict, anchor_ids: list[str]) -> dict:
    """The check an investigation makes when it is taken from an analysed alternative. Raises ValueError if it may not be.

    The alternative's questions are identities. An investigation concerns exactly those questions, and only while each is
    still a continuing question of the current working Architecture. Nothing is rebound to a replacement by wording.
    """
    if not isinstance(origin, dict):
        raise ValueError("a consequence alternative is named by its analysis and its alternative id")
    sha = origin.get("request_sha256") if isinstance(origin.get("request_sha256"), str) else ""
    alternative_id = origin.get("alternative_id") if isinstance(origin.get("alternative_id"), str) else ""
    if not re.fullmatch(r"[0-9a-f]{64}", sha) or not alternative_id:
        raise ValueError("a consequence alternative is named by its analysis and its alternative id")
    folder = _root(store) / "requests" / sha
    if not (folder / "request.json").is_file():
        raise ValueError("that consequence analysis is not recorded on this canvas")
    result = arch._read(folder / "result.json")
    if result is None:
        raise ValueError("that consequence analysis is not completed")
    alternative = next((row for row in result.get("alternatives", []) if row["id"] == alternative_id), None)
    if alternative is None:
        raise ValueError("that alternative is not in the consequence analysis")
    if set(alternative["questions"]) != set(anchor_ids):
        raise ValueError("the investigation must concern exactly the questions the alternative names; "
                         "it cannot substitute other questions")
    continuing = {question["id"] for question in project_architecture_questions(store)["questions"]
                  if question["standing"] == "continuing"}
    missing = [identifier for identifier in alternative["questions"] if identifier not in continuing]
    if missing:
        raise ValueError("a question this alternative concerns is no longer open: " + ", ".join(missing) +
                         ". It is not rebound to another question.")
    text = json.dumps({key: alternative[key] for key in ("title", "approach", "summary", "questions")},
                      ensure_ascii=False, sort_keys=True)
    # An investigation starts only from the latest analysis of the proposal on screen. An earlier analysis, or one whose
    # revision has been applied or replaced, is history: its alternatives are read there, not investigated from here.
    request = load_host_agent_request(folder / "request.json")
    pointer = arch._read(_root(store) / "latest_request.json") or {}
    standing = _standing(store, request, arch.project_architecture(store).get("review"), arch._candidate(store),
                         latest=(pointer.get("request_sha256") == sha))
    if standing != "current":
        raise ValueError("only the latest analysis of the proposal on screen can be investigated; this one is "
                         + ("about an earlier or replaced proposal" if standing == "superseded" else standing.replace("_", " ")))
    return {"request_sha256": sha, "alternative_id": alternative_id, "title": alternative["title"],
            "approach": alternative["approach"], "questions": list(alternative["questions"]),
            "alternative_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
