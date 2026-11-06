"""Source-checked, noncanonical architecture inquiries via the existing host-agent protocol.

Unlike a holistic revision, an inquiry never produces ArchitectureCandidate or writes
architecture/current.json or architecture/latest_request.json.

Creative deliberation continuity: each inquiry packet carries the author's most recent completed
exchanges for the SAME baseline candidate (noncanonical working context), so follow-up references such as
"the second alternative" can be resolved from the request itself. Exchanges never cross a changed baseline.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

from .studio_architecture_graph_intent import GraphIntent, GraphAnchor, resolve_graph_intent

_SYSTEM = """You are the active Auteur narrative-architecture inquiry agent.
Reason about the author's exact question using the existing working architecture,
recorded relationships, explicitly labeled hypotheses and accepted constraints.
Return ONLY a JSON object with schema_version=1, analysis (your interpretation),
recorded_observations (0-8 entries with source kind, id and an attributed claim),
hypotheses (0-5 objects with title and description) and uncertainties (0-8 strings).
Do not return an ArchitectureCandidate or claim acceptance. All claims of literary
causality are interpretations, not deterministic graph proof.
prior_exchanges, when present, are the author's earlier questions and your earlier
answers about this same baseline (noncanonical). Use them to resolve references such as
"the second alternative" and to continue the thread rather than repeat it. Never treat
them as accepted canon or as recorded facts.
"""

# Operation-specific obligations. Explore must produce differentiated alternatives, not restatements.
_OPERATION_GUIDANCE = {
    "explain": (
        "Operation explain: explain the narrative function of the selected elements in the author's terms: "
        "what each supports, what it makes possible for the reader, and how it relates to recorded neighbors. "
        "Offer no alternatives; leave hypotheses empty unless one reading is genuinely unresolved."
    ),
    "challenge": (
        "Operation challenge: identify the weakest assumption, an unrecorded dependency, a contradiction or "
        "an artistic cost in the selected elements. Name what the record leaves undecided. Offer a counter-reading "
        "in hypotheses only when it is genuinely different, and state the uncertainty."
    ),
    "explore": (
        "Operation explore: propose at least two materially different alternatives. Each alternative must change "
        "a causal variable while keeping the author's stated commitments. Give each hypothesis a distinct title, a "
        "description that names the causal variable it changes, and a divergence_axis from causal_engine, "
        "character_agency, reader_emotion, social_scale, structure, theme or genre_relation. Each alternative must "
        "declare a different divergence_axis: two alternatives that change the same variable, such as who bears a "
        "single cost, are one idea. Changes of wording, tone or decoration are not alternatives."
    ),
    "compare": (
        "Operation compare: contrast the selected elements by narrative function, causal role and reader effect. "
        "Use hypotheses only for distinct interpretive readings of the difference."
    ),
    "connect_to_ask": (
        "Operation connect_to_ask: the two anchors may have no recorded relation. State whether a recorded relation "
        "exists. Propose possible relations as labeled hypotheses; never present a possible relation as recorded."
    ),
}

_MAX_PRIOR_IN_REQUEST = 3
_MAX_HISTORY_PROJECTED = 8


class InquiryObservation(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    kind: Literal['node','link','genre_interaction','emotion_target','complex_emotion','genre_contract','phase']
    id: str = Field(min_length=1,max_length=80)
    claim: str = Field(min_length=1,max_length=700)

# Same divergence vocabulary as Studio Mentor directions, so creative operations share one language.
DivergenceAxis = Literal[
    'causal_engine','character_agency','reader_emotion','social_scale','structure','theme','genre_relation',
]

class InquiryHypothesis(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    title: str = Field(min_length=1,max_length=120)
    description: str = Field(min_length=1,max_length=1400)
    divergence_axis: DivergenceAxis | None = None

class ArchitectureInquiryResult(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    schema_version: Literal[1]
    analysis: str = Field(min_length=1,max_length=5000)
    recorded_observations: list[InquiryObservation] = Field(default_factory=list,max_length=8)
    hypotheses: list[InquiryHypothesis] = Field(default_factory=list,max_length=5)
    uncertainties: list[str] = Field(default_factory=list,max_length=8)


def _helpers():
    from auteur.host_agent import (
        build_host_agent_request, load_host_agent_request, validate_host_agent_response,
        write_host_agent_request, write_host_agent_response, _atomic_json_write,
    )
    from . import studio_architecture as arch
    return arch,build_host_agent_request,load_host_agent_request,validate_host_agent_response,write_host_agent_request,write_host_agent_response,_atomic_json_write


def _inquiry_root(store):
    from . import studio_architecture as arch
    return arch._root(store)/'inquiries'


def _normalized_title(title: str) -> str:
    return " ".join(title.casefold().split())


def _with_ids(hypotheses: list[dict]) -> list[dict]:
    """Stable, server-assigned alternative IDs (h1, h2, ...); older results receive the same order-derived IDs."""
    return [
        {"id": row.get("id") or f"h{index}", "title": row["title"], "description": row["description"],
         "divergence_axis": row.get("divergence_axis")}
        for index, row in enumerate(hypotheses, start=1)
    ]


def _exchange_view(result: dict, request_created_at: str, request_sha: str) -> dict:
    intent = result.get("intent") or {}
    anchors = []
    for anchor in intent.get("anchors", []):
        view = {"kind": anchor.get("kind"), "id": anchor.get("id")}
        if anchor.get("field"):
            view["field"] = anchor["field"]
        if anchor.get("reference"):
            view["reference"] = anchor["reference"]
        anchors.append(view)
    return {
        "request_sha256": request_sha,
        "created_at": request_created_at,
        "baseline_candidate_request_sha256": result.get("baseline_candidate_request_sha256"),
        "operation": intent.get("operation"),
        "author_question": intent.get("author_text", ""),
        "anchors": anchors,
        "analysis": str(result.get("analysis", ""))[:1200],
        "hypotheses": [
            {"id": h["id"], "title": h["title"], "description": h["description"][:500],
             "divergence_axis": h.get("divergence_axis")}
            for h in _with_ids(result.get("hypotheses") or [])
        ],
        "uncertainties": [str(item)[:300] for item in (result.get("uncertainties") or [])[:4]],
    }


def _all_completed_exchanges(store) -> list[dict]:
    """Every completed inquiry on this canvas, oldest first, each labelled with its baseline."""
    from auteur.host_agent import load_host_agent_request
    from . import studio_architecture as arch
    requests_root = _inquiry_root(store)/'requests'
    if not requests_root.is_dir():
        return []
    rows = []
    for folder in requests_root.iterdir():
        result = arch._read(folder/'result.json')
        if not result:
            continue
        request = load_host_agent_request(folder/'request.json')
        rows.append((request.created_at, _exchange_view(result, request.created_at, folder.name)))
    rows.sort(key=lambda row: (row[0], row[1]['request_sha256']))
    return [view for _, view in rows]


def _completed_exchanges(store, baseline_sha: str | None) -> list[dict]:
    """Completed inquiries for exactly this baseline, oldest first. Never crosses a changed baseline."""
    if not baseline_sha:
        return []
    return [view for view in _all_completed_exchanges(store)
            if view['baseline_candidate_request_sha256'] == baseline_sha]


def _history_for(store, baseline_sha: str | None) -> list[dict]:
    return list(reversed(_completed_exchanges(store, baseline_sha)))[:_MAX_HISTORY_PROJECTED]


def superseded_history(store, baseline_sha: str | None) -> list[dict]:
    """Earlier-baseline exchanges, newest first: historical lineage for recovery, never prompt context."""
    if not baseline_sha:
        return []
    earlier = [view for view in _all_completed_exchanges(store)
               if view['baseline_candidate_request_sha256'] != baseline_sha]
    return list(reversed(earlier))[:_MAX_HISTORY_PROJECTED]


def _parse_anchor(text: str) -> dict:
    kind, separator, rest = text.partition(":")
    if not separator or not rest:
        raise ValueError("anchor must be kind:id, kind:id@field or kind:id@ref:field:target_kind:target_id")
    if "@" not in rest:
        return {"kind": kind, "id": rest}
    identifier, _, spec = rest.partition("@")
    if spec.startswith("ref:"):
        _, field, target_kind, target_id = spec.split(":", 3)
        return {"kind": kind, "id": identifier,
                "reference": {"field": field, "target_kind": target_kind, "target_id": target_id}}
    return {"kind": kind, "id": identifier, "field": spec}


def prepare_architecture_inquiry(store,graph_intent:dict) -> dict:
    arch,build_request,_,_,write_request,_,atomic_write=_helpers()
    intent=GraphIntent.model_validate(graph_intent)
    if intent.operation=='revise':raise ValueError('inquiry must not be a revision')
    if intent.canvas_id!=store.canvas_id:raise ValueError('graph intent canvas ID mismatch')
    with arch._FilesystemLock(store._path('.canvas.lock')):
        current=arch._candidate(store)
        if not current:raise ValueError('no current working architecture')
        if arch._current_candidate_freshness(store,current)!='ready':
            raise arch.BeginnerConcurrencyError('architecture source or guidance is stale')
        resolved=resolve_graph_intent(current['candidate'],current['request_sha256'],intent)
        context=arch._source(store,previous=current['candidate'])
        _,guidance,design_context=arch._design_context_parts(store,context)
        prior=_completed_exchanges(store,current['request_sha256'])[-_MAX_PRIOR_IN_REQUEST:]
        user=json.dumps({
            'operation':'architecture_inquiry','author_question':intent.author_text,
            'graph_intent':resolved,'working_candidate':current['candidate'],
            'narrative_design_context':design_context,'prior_exchanges':prior,
        },ensure_ascii=False,sort_keys=True)
        system=_SYSTEM+'\n'+_OPERATION_GUIDANCE[intent.operation]
        settings={'operation':'inquire','canvas_id':store.canvas_id,
            'baseline_candidate_request_sha256':current['request_sha256'],
            'source_sha256':current['source_sha256'],
            'design_guidance_sha256':current.get('design_guidance_sha256'),
            'freshness_format':2,'inquiry_schema_version':1}
        request=build_request(candidate_id='studio-inquiry-'+arch._digest({'settings':settings,'user':user})[:24],
            role='studio_architecture_inquiry',system=system,user=user,settings=settings)
        base=_inquiry_root(store)
        write_request(base/'requests'/request.request_sha256/'request.json',request)
        atomic_write(base/'latest_request.json',{'request_sha256':request.request_sha256})
    return project_architecture_inquiry(store)


def _live_matches(store,current,request,arch) -> bool:
    if not current or current['request_sha256']!=request.settings['baseline_candidate_request_sha256']:
        return False
    if arch._current_candidate_freshness(store,current)!='ready':return False
    if current.get('source_sha256')!=request.settings.get('source_sha256'):return False
    if current.get('design_guidance_sha256')!=request.settings.get('design_guidance_sha256'):return False
    return True


def project_architecture_inquiry(store)->dict:
    arch,_,load_request,_,_,_,_=_helpers()
    current=arch._candidate(store)
    history=_history_for(store,current['request_sha256'] if current else None)
    base=_inquiry_root(store);pointer=arch._read(base/'latest_request.json')
    if not pointer:return {'status':'not_started','request':None,'result':None,'history':history}
    import re
    sha=pointer.get('request_sha256','')
    if not isinstance(sha,str) or not re.fullmatch(r'[0-9a-f]{64}',sha):
        raise ValueError('invalid architecture inquiry pointer')
    request=load_request(base/'requests'/sha/'request.json')
    if request.role!='studio_architecture_inquiry':raise ValueError('unexpected inquiry host role')
    result=arch._read(base/'requests'/sha/'result.json')
    valid=_live_matches(store,current,request,arch)
    return {'status':('ready' if valid else 'stale') if result else
            ('awaiting_host_agent' if valid else 'stale'),
            'request':request.model_dump() if result is None and valid else None,
            'result':result if valid else None,
            'request_sha256':sha,
            'baseline_candidate_request_sha256':request.settings['baseline_candidate_request_sha256'],
            'history':history,
            'authority':'noncanonical_inquiry_not_working_architecture'}


def complete_architecture_inquiry(store,payload:dict)->dict:
    arch,_,load_request,validate_response,_,write_response,atomic_write=_helpers()
    with arch._FilesystemLock(store._path('.canvas.lock')):
        base=_inquiry_root(store)
        pointer=arch._read(base/'latest_request.json')
        if not pointer:raise ValueError('no architecture inquiry request exists')
        sha=pointer['request_sha256'];folder=base/'requests'/sha
        request=load_request(folder/'request.json')
        if request.role!='studio_architecture_inquiry':raise ValueError('wrong inquiry role')
        response=validate_response(request,payload)
        prior=arch._read(folder/'response.json')
        if prior:
            if prior!=response.model_dump():raise arch.BeginnerConcurrencyError('different inquiry response already completed')
            return project_architecture_inquiry(store)
        current=arch._candidate(store)
        if not _live_matches(store,current,request,arch):
            write_response(folder/'stale_response.json',response)
            raise arch.BeginnerConcurrencyError('inquiry baseline or design context changed; retained stale response')
        result=ArchitectureInquiryResult.model_validate_json(response.text)
        operation=json.loads(request.user)['graph_intent']['operation']
        if operation=='explore':
            if len(result.hypotheses)<2:
                raise ValueError('explore requires at least two alternative hypotheses; ask explain or challenge for a single reading')
            titles=[_normalized_title(h.title) for h in result.hypotheses]
            if len(set(titles))!=len(titles):
                raise ValueError('explore alternatives must have distinct titles')
            axes=[h.divergence_axis for h in result.hypotheses]
            if any(axis is None for axis in axes) or len(set(axes))!=len(axes):
                raise ValueError('explore alternatives must each declare a distinct divergence_axis: each must change a different causal variable')
        # Verify recorded-observation anchors exist. Source address is computed server-side,
        # while the agent's proposed causal interpretation remains explicitly unverified.
        validated_observations=[]
        for obs in result.recorded_observations:
            an=GraphAnchor(kind=obs.kind,id=obs.id)
            one=GraphIntent(canvas_id=store.canvas_id,operation='explain',
                expected_candidate_request_sha256=current['request_sha256'],
                author_text='Verify inquiry observation identity.',anchors=[an])
            resolved=resolve_graph_intent(current['candidate'],current['request_sha256'],one)
            validated_observations.append({'kind':obs.kind,'id':obs.id,'claim':obs.claim,
                'sourceRef':resolved['anchors'][0]['sourceRef'],
                'interpretation_status':'agent_claim_not_causal_proof'})
        saved={**result.model_dump(mode='json'),'recorded_observations':validated_observations,
            'hypotheses':_with_ids([h.model_dump(mode='json') for h in result.hypotheses]),
            'authority':'noncanonical_inquiry','baseline_candidate_request_sha256':current['request_sha256'],
            'intent':json.loads(request.user)['graph_intent']}
        write_response(folder/'response.json',response)
        atomic_write(folder/'result.json',saved)
    return project_architecture_inquiry(store)


def main(argv: list[str] | None = None) -> int:
    """Host coding-agent bridge for read-only inquiries; prepares or completes, never mutates architecture."""
    from .studio_store import CanvasStore
    from auteur.host_agent import build_host_agent_response
    from . import studio_architecture as arch

    parser = argparse.ArgumentParser(description="Auteur Studio read-only architecture inquiry bridge")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--canvas", required=True)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("show")
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--op", required=True,
                         choices=("explain", "challenge", "explore", "compare", "connect_to_ask"))
    prepare.add_argument("--anchor", action="append", required=True,
                         help="kind:id, kind:id@field, or kind:id@ref:field:target_kind:target_id")
    prepare.add_argument("--text-file", type=Path, required=True)
    complete = commands.add_parser("complete-file")
    complete.add_argument("--response-file", type=Path, required=True)
    args = parser.parse_args(argv)
    store = CanvasStore(args.project, args.canvas)
    if args.action == "prepare":
        text = args.text_file.read_text(encoding="utf-8").rstrip("\r\n")
        current = arch.project_architecture(store)
        intent = {
            "version": 1, "canvas_id": store.canvas_id, "operation": args.op,
            "expected_candidate_request_sha256": current["candidate_request_sha256"],
            "anchors": [_parse_anchor(item) for item in args.anchor], "author_text": text,
        }
        result = prepare_architecture_inquiry(store, intent)
    elif args.action == "complete-file":
        pending = project_architecture_inquiry(store)
        if pending["status"] != "awaiting_host_agent" or not pending["request"]:
            raise ValueError("no pending architecture inquiry request to complete")
        from auteur.host_agent import HostAgentRequest
        request = HostAgentRequest(**pending["request"])
        response = build_host_agent_response(request, args.response_file.read_text(encoding="utf-8"))
        result = complete_architecture_inquiry(store, response.model_dump())
    else:
        result = project_architecture_inquiry(store)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
