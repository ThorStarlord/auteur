"""Evidence-grounded reconsideration of one claim of an accepted consequence analysis (advisory).

The reconsideration binds to one claim of a saved analysis and to the exact bytes of that analysis's result. It recovers the
exact source wording the claim needs from the candidates the analysis read, and, for coverage claims, an exact count of Working
Book elements. Its answer is validated by the owner and stored beside the analysis. The analysis is never rewritten, and a
reconsideration changes no narrative record, applies nothing and adopts nothing.
"""

from __future__ import annotations

import hashlib
import json
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from auteur.host_agent import (
    _atomic_json_write, build_host_agent_request, load_host_agent_request, model_output_contract,
    validate_host_agent_response, write_host_agent_request, write_host_agent_response,
)
from auteur.series.working_book_architecture import book_elements, book_numbers

from . import studio_architecture as arch
from .studio_architecture_consequence import ROLE as CONSEQUENCE_ROLE, _digest, _refuse, _root as _consequence_root, _standing
from .studio_store import CanvasStore

ROLE = "studio_architecture_consequence_reconsideration"
SCHEMA = "studio-consequence-reconsideration/1"
AUTHORITY = "advisory_reconsideration_not_working_architecture"
RECONSIDERATION_SCHEMA_VERSION = 1

VERDICTS = ("accepted", "partly_accepted", "rejected", "unresolved")
CLAIM_KINDS = ("concern", "mechanism", "connection", "inheritance", "alternative", "reach")
RECOVERED_TEXT_LIMIT = 2000
MAX_RECOVERED_RECORDS = 6
# Identifier rows only, so the listing covers every element that cites a claim's nodes in a Study of this size. The count is exact
# regardless; a truncated listing says so.
MAX_CITING_ELEMENTS = 24
MAX_CRITICISM = 4

EvidenceId = Annotated[str, StringConstraints(pattern=r"^E[1-9][0-9]{0,2}$")]
CriticismId = Annotated[str, StringConstraints(pattern=r"^c[1-9]$")]


class CriticismAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    criticism: CriticismId
    verdict: Literal["accepted", "partly_accepted", "rejected", "unresolved"]
    reason: str = Field(min_length=1, max_length=400)


class DownstreamItem(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    text: str = Field(min_length=1, max_length=300)
    evidence: list[EvidenceId] = Field(min_length=1, max_length=3)


class ReconsiderationAnswer(BaseModel):
    """A focused reconsideration of one claim. The owner holds the original claim; the agent gives the judgement."""
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    disposition: Literal["retained", "qualified", "narrowed", "corrected", "expanded", "reframed", "withdrawn", "unresolved"]
    new_consideration: str = Field(min_length=1, max_length=800)
    reconsidered_judgment: str = Field(min_length=1, max_length=800)
    evidence: list[EvidenceId] = Field(min_length=1, max_length=6)
    criticism_assessments: list[CriticismAssessment] = Field(default_factory=list, max_length=MAX_CRITICISM)
    creative_significance: str | None = Field(default=None, max_length=600)
    remaining_uncertainty: list[Annotated[str, StringConstraints(min_length=1, max_length=240)]] = Field(
        default_factory=list, max_length=4)
    downstream: list[DownstreamItem] = Field(default_factory=list, max_length=3)


_SYSTEM_RECONSIDERATION = """You are the active Auteur reconsideration agent. An earlier consequence analysis of a proposed working revision was accepted by the owner. The author asks you to reconsider ONE claim of that analysis. Your reading is advisory: it is not an applied revision, it is not canon, and it changes no record.

The request gives you the claim, with its original text held by the owner. Do not restate that original text. It gives the original evidence the analysis cited, and the recovered records: exact full source wording read from the version the analysis read, and, where the claim concerns Working Book coverage, a coverage record with exact counts. Recovered records are the only source of exact wording. A clipped packet line is not exact wording.

Decide what the claim now warrants, and say why. Use exactly one disposition: retained (the claim stands as it was), qualified (it stands with a stated limit), narrowed (its scope is reduced), corrected (its reading was wrong on the source), expanded (it omits a consequence the source supports), reframed (the same source supports a different reading), withdrawn (it is not supported and should not be relied on), or unresolved (the source does not decide it).

Rules. Cite only the identifiers the request gives. A correction must cite at least one recovered record, because a correction rests on exact source. A coverage statement must use the counts the coverage record gives, and must not say that an element was read unless the coverage record lists it. Keep apart what the record states, what it relates, what you interpret, what is a hypothesis and what remains unestablished. Do not present an inference as recorded.

Criticism is evidence to weigh, not a verdict. Assess each criticism the request supplies, by its identifier, as accepted, partly_accepted, rejected or unresolved, and give a reason for each. A criticism that overstates what the source shows may be rejected. A criticism that correctly finds a misreading must be accepted. Preserve legitimate creative speculation that the record labels as speculation: qualify it, and do not withdraw it merely because the record does not state it.

Do not claim that this reconsideration is accepted, applied or canonical, and do not describe a narrative change as if it were made.

Return ONLY one JSON object with these keys: schema_version (1), disposition, new_consideration (what prompted the reconsideration), reconsidered_judgment (what is now retained, corrected, qualified, expanded or withdrawn), evidence (1 to 6 identifiers), criticism_assessments (0 to 4 objects with criticism, verdict and reason), creative_significance (optional), remaining_uncertainty (0 to 4 strings), and downstream (0 to 3 objects with text and evidence, for consequences of a correction that matter later). Field names and literal values are exact, as the output_contract gives them."""


def reconsideration_standing(analysis_standing: str | None) -> str:
    """A reconsideration of the analysis's current claim is current; of any other analysis it is historical, and says so."""
    return "current" if analysis_standing == "current" else "historical"


def _root(store: CanvasStore):
    return _consequence_root(store) / "reconsiderations"


def _analysis(store: CanvasStore, analysis_request_sha256: str):
    folder = _consequence_root(store) / "requests" / analysis_request_sha256
    if not (folder / "request.json").exists() or not (folder / "result.json").exists():
        raise ValueError("no saved consequence analysis with that request")
    request = load_host_agent_request(folder / "request.json")
    if request.role != CONSEQUENCE_ROLE:
        raise ValueError("the named request is not a consequence analysis")
    result_bytes = (folder / "result.json").read_bytes()
    return request, json.loads(result_bytes.decode("utf-8")), result_bytes


def _claim(result: dict[str, Any], packet: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    """The original claim, read from the saved result by the owner. The agent never supplies it."""
    kind, ref = selection.get("kind"), selection.get("ref")
    if kind not in CLAIM_KINDS:
        raise ValueError(f"a reconsideration names one of {', '.join(CLAIM_KINDS)}, not {kind!r}")
    if kind in ("concern", "connection", "inheritance"):
        rows = result.get({"concern": "concerns", "connection": "connections", "inheritance": "inheritance"}[kind]) or []
        if not isinstance(ref, int) or not 0 <= ref < len(rows):
            raise ValueError(f"the analysis has no {kind} {ref}")
        original = rows[ref]
        if kind == "concern":
            evidence = list(original.get("evidence") or [])
        elif kind == "connection":
            evidence = list(original.get("between") or []) + list(original.get("evidence") or [])
        else:
            evidence = [original["from"], original["to"]] + list(original.get("evidence") or [])
    elif kind == "mechanism":
        row = next((r for r in result.get("mechanisms") or [] if r.get("evidence") == ref), None)
        if row is None:
            raise ValueError(f"the analysis reads no mechanism {ref}")
        original = row
        evidence = [ref] + [c for item in row.get("counterevidence") or [] for c in item.get("evidence") or []]
    elif kind == "alternative":
        row = next((r for r in result.get("alternatives") or [] if r.get("id") == ref), None)
        if row is None:
            raise ValueError(f"the analysis has no alternative {ref}")
        original = row
        evidence = list(row.get("keeps") or []) + list(row.get("mechanisms") or [])
    else:  # reach: the change's own mechanisms, as the packet identifies them
        original = {"reach": result.get("reach"), "reading": result.get("reading")}
        evidence = [item["id"] for item in packet["evidence"]
                    if item["kind"] == "mechanism" and item.get("provenance") in ("transformed", "introduced", "removed")]
        ref = None
    return {"kind": kind, "ref": ref, "original": original, "evidence": list(dict.fromkeys(evidence))}


def _find_record(candidate: dict[str, Any], record_id: str) -> dict[str, Any] | None:
    for value in candidate.values():
        if isinstance(value, list):
            for row in value:
                if isinstance(row, dict) and row.get("id") == record_id:
                    return row
    return None


def _coverage(store: CanvasStore, packet: dict[str, Any], nodes: set[str]) -> dict[str, Any]:
    """Exact counts of Working Book elements, read now. Elements that cite the claim's nodes are listed, up to a bound."""
    read_total, books_read, books_unreadable, citing = 0, [], [], []
    for number in book_numbers(store):
        try:
            rows = book_elements(store, number)
        except Exception:  # noqa: BLE001 - one Book's damage is named for that Book only
            books_unreadable.append(number)
            continue
        books_read.append(number)
        read_total += len(rows)
        for row in rows:
            cited = sorted(set(row.get("series_refs") or []) & nodes)
            if cited:
                citing.append({"book_number": number, "element_id": row.get("id"), "cites_claim_nodes": cited})
    limits = packet["limits"]
    return {
        "owner": "Working Book owner, read now",
        "freshness": "current_read",
        "books_read": books_read,
        "books_unreadable": books_unreadable,
        "elements_read": read_total,
        "elements_considered_by_packet": limits["book_elements_considered"],
        "elements_supplied_to_analysis": limits["book_elements_shown"],
        "claim_nodes": sorted(nodes),
        "citing_count": len(citing),
        "citing_claim_nodes": citing[:MAX_CITING_ELEMENTS],
        "listing_truncated": len(citing) > MAX_CITING_ELEMENTS,
    }


def _recover(store: CanvasStore, analysis: dict[str, Any], packet: dict[str, Any], claim: dict[str, Any]):
    """Exact source wording for the claim's mechanisms, from the candidates the analysis read; coverage for coverage claims."""
    items = {item["id"]: item for item in packet["evidence"]}
    number = max(int(identifier[1:]) for identifier in items) + 1
    records: list[dict[str, Any]] = []
    nodes: set[str] = set()
    for identifier in claim["evidence"]:
        item = items.get(identifier)
        if item is None or item["kind"] != "mechanism":
            continue
        for side, key in (("baseline", "baseline_candidate"), ("proposed", "proposed_candidate")):
            if not item.get(f"{side}_sha256"):
                continue
            candidate = analysis[key]
            record = _find_record(candidate, item["record_id"])
            if record is None:
                continue
            if record.get("source") and record.get("target"):
                nodes.update([record["source"], record["target"]])
            if item["record_kind"] == "node":
                nodes.add(record["id"])
            if len(records) >= MAX_RECOVERED_RECORDS:
                continue
            text = json.dumps(record, ensure_ascii=False, sort_keys=True)
            records.append({
                "id": f"E{number}", "source": "recovered", "owner": "Architecture candidate the analysis read",
                "record_kind": item["record_kind"], "record_id": item["record_id"], "side": side,
                "version_sha256": _digest(candidate), "freshness": "as_analysed",
                "truncated": len(text) > RECOVERED_TEXT_LIMIT, "text": text[:RECOVERED_TEXT_LIMIT],
            })
            number += 1
    coverage = None
    if claim["kind"] in ("reach", "inheritance"):
        for identifier in claim["evidence"]:
            item = items.get(identifier)
            if item and item["kind"] == "mechanism":
                nodes.update(node for node in item.get("endpoints") or [] if node)
        coverage = _coverage(store, packet, nodes)
        text = json.dumps(coverage, ensure_ascii=False, sort_keys=True)
        records.append({
            "id": f"E{number}", "source": "recovered", "owner": coverage["owner"], "record_kind": "coverage",
            "record_id": None, "side": None, "version_sha256": None, "freshness": coverage["freshness"],
            "truncated": len(text) > RECOVERED_TEXT_LIMIT, "text": text[:RECOVERED_TEXT_LIMIT],
        })
    return records, coverage


def _row(store: CanvasStore, folder, request) -> dict[str, Any]:
    """The reconsideration as it stands: its binding, its claim, its recovered evidence and its owner-validated answer."""
    payload = json.loads(request.user)
    result = arch._read(folder / "result.json")
    analysis_sha = request.settings["analysis_request_sha256"]
    analysis_request = load_host_agent_request(_consequence_root(store) / "requests" / analysis_sha / "request.json")
    pending = arch.project_architecture(store).get("review")
    analysis_standing = _standing(store, analysis_request, pending, arch._candidate(store), latest=True)
    refused = folder / "refused"
    return {
        "schema": SCHEMA,
        "authority": AUTHORITY,
        "request_sha256": request.request_sha256,
        "analysis_request_sha256": analysis_sha,
        "status": "ready" if result is not None else "awaiting_host_agent",
        "claim": {"kind": payload["claim"]["kind"], "ref": payload["claim"]["ref"],
                  "original_text": payload["claim"]["original_text"], "evidence": payload["claim"]["evidence"],
                  "claim_sha256": payload["claim"]["claim_sha256"]},
        "instruction": payload["instruction"],
        "criticism": payload["criticism"],
        "recovery": payload["recovery"],
        "answer": result["answer"] if result is not None else None,
        "request_sha256": request.request_sha256,
        "request": request.model_dump() if result is None else None,
        "refused_attempts": len(list(refused.glob("*.json"))) if refused.exists() else 0,
        "analysis_standing": analysis_standing,
        "standing": reconsideration_standing(analysis_standing),
    }


def prepare_consequence_reconsideration(store: CanvasStore, *, analysis_request_sha256: str, selection: dict[str, Any],
                                        instruction: str, criticism: list[str] | None = None) -> dict[str, Any]:
    """Prepare the reconsideration of one claim of a saved analysis. Explicit only; nothing is executed or changed."""
    if not instruction or not instruction.strip():
        raise ValueError("a reconsideration needs the author's question")
    criticism_texts = [text.strip() for text in (criticism or []) if text and text.strip()]
    if len(criticism_texts) > MAX_CRITICISM:
        raise ValueError(f"a reconsideration weighs at most {MAX_CRITICISM} criticisms")
    with arch._FilesystemLock(store._path(".canvas.lock")):
        analysis_request, result, result_bytes = _analysis(store, analysis_request_sha256)
        analysis = json.loads(analysis_request.user)
        packet = analysis["consequence_packet"]
        claim = _claim(result, packet, selection)
        items = {item["id"]: item for item in packet["evidence"]}
        original_evidence = [items[identifier] for identifier in claim["evidence"] if identifier in items]
        recovered, coverage = _recover(store, analysis, packet, claim)
        criticism_rows = [{"id": f"c{number}", "text": text} for number, text in enumerate(criticism_texts, start=1)]
        recovery = {"records": recovered, "coverage": coverage}
        allowed = sorted({identifier for identifier in items} | {row["id"] for row in recovered},
                         key=lambda identifier: int(identifier[1:]))
        user = {
            "operation": "consequence_reconsideration",
            "analysis": {
                "analysis_request_sha256": analysis_request_sha256,
                "analysis_result_sha256": hashlib.sha256(result_bytes).hexdigest(),
                "revision_request_sha256": analysis_request.settings["review_request_sha256"],
                "baseline_request_sha256": analysis_request.settings["baseline_candidate_request_sha256"],
                "proposal_sha256": analysis_request.settings["proposal_sha256"],
                "evidence_sha256": packet["evidence_sha256"],
            },
            "claim": {"kind": claim["kind"], "ref": claim["ref"], "claim_sha256": _digest(claim["original"]),
                      "evidence": claim["evidence"], "original_text": claim["original"]},
            "original_evidence": original_evidence,
            "recovery": recovery,
            "recovered_evidence": [row["id"] for row in recovered],
            "allowed_evidence": allowed,
            "instruction": instruction.strip(),
            "criticism": criticism_rows,
        }
        user_text = json.dumps(user, ensure_ascii=False, sort_keys=True)
        settings = {
            "operation": "reconsider_consequence",
            "analysis_request_sha256": analysis_request_sha256,
            "analysis_result_sha256": user["analysis"]["analysis_result_sha256"],
            "claim_kind": claim["kind"],
            "claim_ref": claim["ref"],
            "claim_sha256": user["claim"]["claim_sha256"],
            "instruction_sha256": _digest(instruction.strip()),
            "criticism_sha256": _digest(criticism_rows),
            "recovery_sha256": _digest(recovery),
            "evidence_sha256": packet["evidence_sha256"],
            "reconsideration_schema_version": RECONSIDERATION_SCHEMA_VERSION,
        }
        request = build_host_agent_request(
            candidate_id="studio-reconsideration-" + _digest({"settings": settings, "user": user_text})[:24],
            role=ROLE, system=_SYSTEM_RECONSIDERATION, user=user_text, settings=settings,
            output_contract=model_output_contract(ReconsiderationAnswer),
        )
        folder = _root(store) / request.request_sha256
        if not (folder / "request.json").exists():
            write_host_agent_request(folder / "request.json", request)
        row = _row(store, folder, load_host_agent_request(folder / "request.json"))
    return {"request": request.model_dump(), "reconsideration": row}


def _check_answer(answer: ReconsiderationAnswer, payload: dict[str, Any]) -> None:
    """Every identifier resolves inside this request; a correction rests on recovered source; each criticism is one the request
    supplied, assessed once."""
    allowed = set(payload["allowed_evidence"])
    recovered = set(payload["recovered_evidence"])
    problems: list[str] = []
    cited = list(answer.evidence) + [identifier for item in answer.downstream for identifier in item.evidence]
    for identifier in dict.fromkeys(cited):
        if identifier not in allowed:
            problems.append(f"the answer cites {identifier}, which is not in this request")
    if answer.disposition == "corrected" and not set(answer.evidence) & recovered:
        problems.append("a correction must rest on recovered source: cite at least one recovered record")
    supplied = {row["id"] for row in payload["criticism"]}
    seen: set[str] = set()
    for assessment in answer.criticism_assessments:
        if assessment.criticism not in supplied:
            problems.append(f"{assessment.criticism} is not a criticism this request supplied")
        elif assessment.criticism in seen:
            problems.append(f"{assessment.criticism} is assessed more than once")
        seen.add(assessment.criticism)
    _refuse(problems)


def complete_consequence_reconsideration(store: CanvasStore, payload: dict) -> dict[str, Any]:
    """Validate and store the agent's reconsideration of the request it names. A refused answer is kept beside its message."""
    with arch._FilesystemLock(store._path(".canvas.lock")):
        request_sha = payload.get("request_sha256")
        if not isinstance(request_sha, str):
            raise ValueError("a reconsideration response names its request")
        folder = _root(store) / request_sha
        if not (folder / "request.json").exists():
            raise ValueError("no reconsideration request exists for that response")
        request = load_host_agent_request(folder / "request.json")
        if request.role != ROLE:
            raise ValueError("wrong reconsideration role")
        response = validate_host_agent_response(request, payload)
        prior = arch._read(folder / "response.json")
        if prior and prior != response.model_dump():
            raise arch.BeginnerConcurrencyError("a different reconsideration response already completed this request")
        if prior and arch._read(folder / "result.json") is not None:
            return _row(store, folder, request)
        analysis_sha = request.settings["analysis_request_sha256"]
        current_bytes = (_consequence_root(store) / "requests" / analysis_sha / "result.json").read_bytes()
        if hashlib.sha256(current_bytes).hexdigest() != request.settings["analysis_result_sha256"]:
            raise arch.BeginnerConcurrencyError(
                "the analysis this reconsideration reads has changed since it was prepared; the reconsideration is not stored")
        submitted = json.loads(request.user)
        try:
            answer = ReconsiderationAnswer.model_validate_json(response.text)
            _check_answer(answer, submitted)
        except ValueError as refusal:
            # A refused answer is kept as evidence of what was returned and refused, beside the owner's message. It never
            # becomes the reconsideration, and it never changes the analysis it read.
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
            "original": {"analysis_request_sha256": analysis_sha,
                         "analysis_result_sha256": request.settings["analysis_result_sha256"],
                         "claim": {"kind": request.settings["claim_kind"], "ref": request.settings["claim_ref"],
                                   "claim_sha256": request.settings["claim_sha256"]}},
            "answer": answer.model_dump(mode="json"),
            "completion": {"attempt": refused_before + 1, "refused_attempts": refused_before,
                           "first_pass": refused_before == 0},
        })
        return _row(store, folder, request)


def project_consequence_reconsiderations(store: CanvasStore, analysis_request_sha256: str) -> list[dict[str, Any]]:
    """Read-only: the reconsiderations of one saved analysis, oldest first."""
    rows = []
    base = _root(store)
    if not base.is_dir():
        return rows
    for folder in sorted(base.iterdir()):
        if not (folder / "request.json").exists():
            continue
        request = load_host_agent_request(folder / "request.json")
        if request.role == ROLE and request.settings["analysis_request_sha256"] == analysis_request_sha256:
            rows.append(_row(store, folder, request))
    return rows


__all__ = [
    "ReconsiderationAnswer", "complete_consequence_reconsideration", "prepare_consequence_reconsideration",
    "project_consequence_reconsiderations", "reconsideration_standing",
]
