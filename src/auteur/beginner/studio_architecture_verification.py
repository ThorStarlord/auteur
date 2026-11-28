"""Claim-basis verification: one fresh judgement of whether one claim of a completed synthesis is warranted by the exact evidence the
synthesis was given (advisory, read-only).

The author asks for one claim (a stage, a relation, an alternative path, an opportunity or a culmination condition) of a completed
synthesis to be checked. The owner builds the packet from the synthesis's own stored request, so the verifier sees the exact text the
synthesis read, with its owner, freshness and epistemic status, and not the synthesis's reasoning. A fresh agent returns one judgement
about the claim, with the evidence it relies on and what remains creatively open. The owner validates it and stores it beside its
request.

A verification changes no synthesis, no record and no Architecture, applies nothing, and is not canon. It may enter a follow-up
synthesis as one criticism, where the synthesis weighs it. It can be disagreed with: the verifier's judgement is a judgement.
"""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from auteur.host_agent import (
    _atomic_json_write, build_host_agent_request, load_host_agent_request, model_output_contract, validate_host_agent_response,
    write_host_agent_request, write_host_agent_response,
)

from . import studio_architecture as arch
from .studio_architecture_consequence import _digest, _refuse
from .studio_architecture_synthesis import _grounded, synthesis_record, verification_root
from .studio_store import CanvasStore

ROLE = "studio_architecture_claim_verification"
SCHEMA = "studio-claim-verification/1"
AUTHORITY = "advisory_verification_not_applied"
VERIFICATION_SCHEMA_VERSION = 1
CLAIM_PATTERN = r"^(s[1-6]|r[1-8]|a[1-3]|o[1-3]|n[1-4]|e[1-4])$"
CLAIM_KINDS = {"s": "stage", "r": "relation", "a": "alternative_path", "o": "opportunity", "n": "necessary_condition",
               "e": "enrichment_condition"}
LOAD_KINDS = ("prerequisite", "enables", "complicates")
JUDGMENTS = ("supported", "defensible_inference", "creative_speculation", "overreaching", "temporal_misreading", "modal_misreading",
             "attribution_error", "standing_confusion", "unsupported_relation", "contradicted", "insufficient_evidence")
MISREADINGS = ("overreaching", "temporal_misreading", "modal_misreading", "attribution_error", "standing_confusion",
               "unsupported_relation", "contradicted")
NO_EVIDENCE_NEEDED = ("insufficient_evidence", "creative_speculation")

EvidenceId = Annotated[str, StringConstraints(pattern=r"^E[1-9][0-9]{0,2}$")]

# The owner's limits. The instruction states each one from these constants, so the prompt and the schema cannot drift apart: an
# unstated limit refused a whole answer in the first authentic run (creative_room at 401 characters).
REASONING_CHARS = 600
EVIDENCE_MAX = 4
QUOTE_CHARS = 240
ALTERNATIVE_CHARS = 400
SETTLE_CHARS = 240
ROOM_CHARS = 400


class ClaimVerification(BaseModel):
    """The verifier's judgement of one claim. ``creative_room`` is required: a verification that narrows possibility without saying so
    is a defect of the verifier."""
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    claim: Annotated[str, StringConstraints(pattern=CLAIM_PATTERN)]
    evidence_register: Literal["established", "inferred_from_established", "agent_proposed", "author_stated", "not_established", "mixed"]
    judgment: Literal["supported", "defensible_inference", "creative_speculation", "overreaching", "temporal_misreading",
                      "modal_misreading", "attribution_error", "standing_confusion", "unsupported_relation", "contradicted",
                      "insufficient_evidence"]
    affects: Literal["creative_possibility", "asserted_condition", "load_bearing_premise"]
    reasoning: str = Field(min_length=1, max_length=REASONING_CHARS)
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=EVIDENCE_MAX)
    quote: str | None = Field(default=None, max_length=QUOTE_CHARS)
    alternative_reading: str | None = Field(default=None, max_length=ALTERNATIVE_CHARS)
    would_settle: str | None = Field(default=None, max_length=SETTLE_CHARS)
    creative_room: str = Field(min_length=1, max_length=ROOM_CHARS)


_SYSTEM_VERIFY = """You are the Auteur claim-basis verifier. You judge one claim of a completed creative synthesis against the exact evidence that synthesis was given. Your judgement is advisory: it is not canon, it changes no record, and the author may disagree with it.

You do not judge whether the idea is artistically good, whether the story should go this way, or the quality of the prose. Judge only whether the claim is warranted by the evidence, and say what the evidence actually establishes.

Keep these apart. What the evidence establishes (its own words state it as fact, and its epistemic status or attribution does not mark it as proposed). What the evidence supports by inference (say how). What is agent-proposed (an agent_proposed element, or wording that proposes or conditions). What the author has stated. What remains creatively possible. A creative proposal that the evidence does not entail is not an error when it is presented as a proposal; the error is a claim whose premise the evidence does not carry. Typical errors: present tense read as an achieved event; a conditional or hypothetical read as an event; agent-proposed text presented as record; a repeated element read as a new development; a dependency the evidence does not state; an attribution to the wrong source; a standing or authority the evidence does not grant.

Use only the identifiers in allowed_evidence. Quote only words copied exactly from a cited item, up to 240 characters, that carry the premise of your judgement. If the claim's offered quote does not carry its premise, say so in alternative_reading. State an absence as 'not stated in the cited items', never as a fact about the story.

Always fill creative_room: what remains creatively possible with this claim, and which parts of it would have to be treated as proposals rather than record. Never narrow the space of creative possibilities without saying what it is.

Return ONLY one JSON object with these keys: schema_version (1), claim, evidence_register, judgment, affects, reasoning, evidence, quote, alternative_reading, would_settle, creative_room. Field names and literal values are exact, as the output_contract gives them.

Limits, enforced by the owner (an answer that exceeds one is refused whole): reasoning at most {reasoning} characters; evidence at most {evidence} identifiers; quote at most {quote} characters; alternative_reading at most {alternative} characters, and required for every judgment other than supported, defensible_inference, creative_speculation and insufficient_evidence; would_settle at most {settle} characters, and required for insufficient_evidence; creative_room at most {room} characters and always required.""".format(
    reasoning=REASONING_CHARS, evidence=EVIDENCE_MAX, quote=QUOTE_CHARS, alternative=ALTERNATIVE_CHARS, settle=SETTLE_CHARS,
    room=ROOM_CHARS)


def claims_of(answer: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Every checkable claim of a synthesis answer, by reference, with its wording, its stated basis, its citations and its references."""
    claims: dict[str, dict[str, Any]] = {}
    for index, stage in enumerate(answer["trajectory"], start=1):
        claims[f"s{index}"] = {"kind": "stage", "basis": stage["basis"], "evidence": list(stage["evidence"]), "quote": stage.get("quote"),
                               "refers_to": [],
                               "wording": {"book": stage["book"], "horizon": stage["horizon"], "development": stage["development"],
                                           "becomes_available": stage["becomes_available"], "changes": stage["changes"]}}
    for index, relation in enumerate(answer["relations"], start=1):
        claims[f"r{index}"] = {"kind": "relation", "basis": None, "evidence": list(relation["evidence"]), "quote": relation.get("quote"),
                               "refers_to": list(relation["between"]),
                               "wording": {"relation": relation["kind"], "between": list(relation["between"]),
                                           "dependence": relation["dependence"], "reason": relation["reason"]}}
    for index, path in enumerate(answer["alternative_paths"], start=1):
        claims[f"a{index}"] = {"kind": "alternative_path", "basis": None, "evidence": list(path["evidence"]), "quote": path.get("quote"),
                               "refers_to": [], "wording": {"ordering": path["ordering"], "effect": path["effect"],
                                                            "viability": path["viability"]}}
    for index, opportunity in enumerate(answer["opportunities"], start=1):
        claims[f"o{index}"] = {"kind": "opportunity", "basis": None, "evidence": list(opportunity["evidence"]),
                               "quote": opportunity.get("quote"), "refers_to": list(opportunity["between"]),
                               "wording": {"text": opportunity["text"], "between": list(opportunity["between"])}}
    culmination = answer.get("culmination")
    if culmination:
        for index, condition in enumerate(culmination["necessary"], start=1):
            claims[f"n{index}"] = {"kind": "necessary_condition", "basis": None, "evidence": list(condition["evidence"]),
                                   "quote": condition.get("quote"), "refers_to": [], "wording": {"text": condition["text"]}}
        for index, condition in enumerate(culmination["enrichment"], start=1):
            claims[f"e{index}"] = {"kind": "enrichment_condition", "basis": None, "evidence": list(condition["evidence"]),
                                   "quote": condition.get("quote"), "refers_to": [], "wording": {"text": condition["text"]}}
    return claims


def dependents_of(answer: dict[str, Any], claims: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """For each claim: the claims that use it, and whether any of them is a necessary, enabling or complicating relation or an
    opportunity. A count of uses, not a score; the rule is the record's own references."""
    result = {ref: {"used_by": [], "load_bearing": False} for ref in claims}
    for ref, claim in claims.items():
        for target in claim["refers_to"]:
            if target not in result:
                continue
            result[target]["used_by"].append(ref)
            if claim["kind"] == "opportunity" or (claim["kind"] == "relation" and claim["wording"]["relation"] in LOAD_KINDS):
                result[target]["load_bearing"] = True
    return result


def _packet(record: dict[str, Any], claim_ref: str, claims: dict[str, dict[str, Any]], uses: dict[str, dict[str, Any]]) -> dict[str, Any]:
    info = claims[claim_ref]
    return {
        "operation": "verify_claim_basis",
        "synthesis_question": record["question"],
        "claim": {"ref": claim_ref, "kind": info["kind"], "wording": info["wording"], "basis_as_stated": info["basis"],
                  "quote_offered": info["quote"], "cited_evidence": info["evidence"]},
        "used_by": uses[claim_ref]["used_by"],
        "load_bearing": uses[claim_ref]["load_bearing"],
        "developments": record["developments"],
        "evidence": record["evidence"],
        "allowed_evidence": [item["id"] for item in record["evidence"]],
    }


def _check_verification(verdict: ClaimVerification, user: dict[str, Any]) -> None:
    """Refuse what the owner can check: citations inside the packet, a verbatim quote, a reason where the judgement needs one, and
    consistency between the judgement and the register the verifier gives the evidence. Meaning is not checked here."""
    problems: list[str] = []
    allowed = set(user["allowed_evidence"])
    for identifier in verdict.evidence:
        if identifier not in allowed:
            problems.append(f"the verification cites {identifier}, which is not in this request")
    if verdict.judgment not in NO_EVIDENCE_NEEDED and not verdict.evidence:
        problems.append(f"a {verdict.judgment} judgement cites no evidence")
    texts = {row["id"]: row.get("text") or "" for row in user["evidence"]}
    problems += _grounded("the verification", verdict.quote, verdict.evidence, texts)
    if verdict.judgment in MISREADINGS and not verdict.alternative_reading:
        problems.append(f"a {verdict.judgment} judgement must say what the evidence does support (alternative_reading)")
    if verdict.judgment == "insufficient_evidence" and not verdict.would_settle:
        problems.append("an insufficient_evidence judgement must name what would settle it (would_settle)")
    if verdict.judgment == "supported" and verdict.evidence_register not in ("established", "inferred_from_established", "author_stated"):
        problems.append("a supported judgement needs evidence that establishes or infers the premise, not evidence the verifier "
                        "marks as agent_proposed or not_established")
    if user["claim"]["basis_as_stated"] == "recorded" and verdict.judgment == "supported" \
            and verdict.evidence_register not in ("established", "author_stated"):
        problems.append("the claim is stated as recorded, so it is supported only by evidence that establishes it; "
                        "evidence that infers it is a standing_confusion or defensible_inference")
    _refuse(problems)


def _claim_pointer(store: CanvasStore, synthesis_request_sha256: str, claim: str):
    return verification_root(store) / "latest_by_claim" / f"{_digest([synthesis_request_sha256, claim])}.json"


def _standing(store: CanvasStore, request_sha256: str, request) -> str:
    """``stale`` once the evidence the synthesis read has changed or the synthesis is gone; ``superseded`` when a later verification of
    the same claim exists; ``current`` otherwise."""
    synthesis_sha = request.settings["synthesis_request_sha256"]
    try:
        record = synthesis_record(store, synthesis_sha)
    except ValueError:
        return "stale"
    if record["evidence_sha256_now"] != request.settings["evidence_sha256"]:
        return "stale"
    pointer = arch._read(_claim_pointer(store, synthesis_sha, request.settings["claim"]))
    latest = pointer.get("request_sha256") if pointer else None
    return "current" if request_sha256 == latest else "superseded"


def _row(store: CanvasStore, folder, request) -> dict[str, Any]:
    result = arch._read(folder / "result.json")
    standing = _standing(store, request.request_sha256, request)
    user = json.loads(request.user)
    refused = folder / "refused"
    return {
        "schema": SCHEMA,
        "authority": AUTHORITY,
        "request_sha256": request.request_sha256,
        "synthesis_request_sha256": request.settings["synthesis_request_sha256"],
        "claim": request.settings["claim"],
        "claim_kind": user["claim"]["kind"],
        "claim_wording": user["claim"]["wording"],
        "claimed_basis": user["claim"]["basis_as_stated"],
        "used_by": user["used_by"],
        "load_bearing": user["load_bearing"],
        "standing": standing,
        "status": "ready" if result is not None else ("awaiting_host_agent" if standing == "current" else "unanswered"),
        "request": request.model_dump() if result is None and standing == "current" else None,
        "result": result["verification"] if result is not None else None,
        "refused_attempts": len(list(refused.glob("*.json"))) if refused.exists() else 0,
    }


def prepare_claim_verification(store: CanvasStore, *, synthesis_request_sha256: str, claim: str) -> dict[str, Any]:
    """Prepare one claim-basis verification of a completed synthesis. Explicit only; read-only for every record."""
    with arch._FilesystemLock(store._path(".canvas.lock")):
        record = synthesis_record(store, synthesis_request_sha256)
        claims = claims_of(record["answer"])
        if claim not in claims:
            raise ValueError(f"the synthesis has no claim {claim!r}")
        uses = dependents_of(record["answer"], claims)
        user_text = json.dumps(_packet(record, claim, claims, uses), ensure_ascii=False, sort_keys=True)
        settings = {
            "operation": "verify_synthesis_claim",
            "synthesis_request_sha256": synthesis_request_sha256,
            "synthesis_result_sha256": record["result_sha256"],
            "claim": claim,
            "claim_sha256": _digest(claims[claim]),
            "evidence_sha256": record["evidence_sha256"],
            "verification_schema_version": VERIFICATION_SCHEMA_VERSION,
        }
        request = build_host_agent_request(
            candidate_id="claim-verification-" + _digest({"settings": settings, "user": user_text})[:24],
            role=ROLE, system=_SYSTEM_VERIFY, user=user_text, settings=settings,
            output_contract=model_output_contract(ClaimVerification),
        )
        folder = verification_root(store) / "requests" / request.request_sha256
        if not (folder / "request.json").exists():
            write_host_agent_request(folder / "request.json", request)
        _atomic_json_write(_claim_pointer(store, synthesis_request_sha256, claim), {"request_sha256": request.request_sha256})
        row = _row(store, folder, load_host_agent_request(folder / "request.json"))
    return {"request": request.model_dump(), "verification": row}


def complete_claim_verification(store: CanvasStore, payload: dict) -> dict[str, Any]:
    """Validate and store the verifier's judgement of the request it names. A refused judgement is kept beside its refusal."""
    with arch._FilesystemLock(store._path(".canvas.lock")):
        request_sha = payload.get("request_sha256")
        if not isinstance(request_sha, str):
            raise ValueError("a verification response names its request")
        folder = verification_root(store) / "requests" / request_sha
        if not (folder / "request.json").exists():
            raise ValueError("no verification request exists for that response")
        request = load_host_agent_request(folder / "request.json")
        if request.role != ROLE:
            raise ValueError("wrong verification role")
        response = validate_host_agent_response(request, payload)
        prior = arch._read(folder / "response.json")
        if prior and prior != response.model_dump():
            raise arch.BeginnerConcurrencyError("a different verification response already completed this request")
        if prior and arch._read(folder / "result.json") is not None:
            return _row(store, folder, request)
        synthesis_sha = request.settings["synthesis_request_sha256"]
        try:
            record = synthesis_record(store, synthesis_sha)
        except ValueError as gone:
            raise arch.BeginnerConcurrencyError(
                f"the synthesis this verification checks is no longer completed ({gone}); the verification is not stored") from gone
        if record["evidence_sha256_now"] != request.settings["evidence_sha256"]:
            raise arch.BeginnerConcurrencyError(
                "the evidence the synthesis read has changed since this verification was prepared; the verification is not stored")
        if record["result_sha256"] != request.settings["synthesis_result_sha256"]:
            raise arch.BeginnerConcurrencyError("the synthesis changed since this verification was prepared; it is not stored")
        user = json.loads(request.user)
        try:
            verdict = ClaimVerification.model_validate_json(response.text)
            if verdict.claim != request.settings["claim"]:
                raise ValueError(f"the verification judges {verdict.claim}, but this request asks about {request.settings['claim']}")
            _check_verification(verdict, user)
        except ValueError as refusal:
            # A refused judgement is kept as evidence of what was returned and refused. It never becomes the verification.
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
            "synthesis_request_sha256": synthesis_sha,
            "synthesis_result_sha256": record["result_sha256"],
            "claim": request.settings["claim"],
            "claim_sha256": request.settings["claim_sha256"],
            "evidence_sha256": request.settings["evidence_sha256"],
            "verification": verdict.model_dump(mode="json"),
            "completion": {"attempt": refused_before + 1, "refused_attempts": refused_before,
                           "first_pass": refused_before == 0},
        })
        return _row(store, folder, request)


def claim_inventory(store: CanvasStore, synthesis_request_sha256: str) -> list[dict[str, Any]]:
    """Every checkable claim of a completed synthesis, with the claims that use it and whether others depend on it. Empty while the
    synthesis is not completed: there is nothing yet to check."""
    try:
        record = synthesis_record(store, synthesis_request_sha256)
    except ValueError:
        return []
    claims = claims_of(record["answer"])
    uses = dependents_of(record["answer"], claims)
    return [{"claim": ref, "kind": info["kind"], "wording": info["wording"], "basis": info["basis"],
             "used_by": uses[ref]["used_by"], "load_bearing": uses[ref]["load_bearing"]} for ref, info in claims.items()]


def project_claim_verifications(store: CanvasStore, synthesis_request_sha256: str) -> dict[str, Any]:
    """Read-only: for one synthesis, each claim's newest verification with its standing, how many earlier ones there were, and the
    claim inventory (which claims others depend on)."""
    base = verification_root(store) / "requests"
    rows: list[tuple[str, Any, Any]] = []
    if base.is_dir():
        for folder in sorted(base.iterdir()):
            if not (folder / "request.json").exists():
                continue
            request = load_host_agent_request(folder / "request.json")
            if request.role == ROLE and request.settings.get("synthesis_request_sha256") == synthesis_request_sha256:
                rows.append((request.created_at, folder, request))
    rows.sort(key=lambda item: item[0], reverse=True)
    by_claim: dict[str, list[dict[str, Any]]] = {}
    for _created, folder, request in rows:
        by_claim.setdefault(request.settings["claim"], []).append(_row(store, folder, request))
    return {"schema": SCHEMA, "authority": AUTHORITY, "synthesis_request_sha256": synthesis_request_sha256,
            "inventory": claim_inventory(store, synthesis_request_sha256),
            "claims": {claim: {"latest": history[0], "earlier": len(history) - 1} for claim, history in sorted(by_claim.items())}}


__all__ = [
    "AUTHORITY", "ClaimVerification", "ROLE", "SCHEMA", "claim_inventory", "claims_of", "complete_claim_verification",
    "dependents_of", "prepare_claim_verification", "project_claim_verifications",
]
