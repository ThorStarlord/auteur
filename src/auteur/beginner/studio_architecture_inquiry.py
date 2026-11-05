"""Source-checked, noncanonical architecture inquiries via the existing host-agent protocol.

Unlike a holistic revision, an inquiry never produces ArchitectureCandidate or writes
architecture/current.json or architecture/latest_request.json.
"""
from __future__ import annotations

import json
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
"""

class InquiryObservation(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    kind: Literal['node','link','genre_interaction','emotion_target','complex_emotion','genre_contract','phase']
    id: str = Field(min_length=1,max_length=80)
    claim: str = Field(min_length=1,max_length=700)

class InquiryHypothesis(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    title: str = Field(min_length=1,max_length=120)
    description: str = Field(min_length=1,max_length=1400)

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
        user=json.dumps({
            'operation':'architecture_inquiry','author_question':intent.author_text,
            'graph_intent':resolved,'working_candidate':current['candidate'],
            'narrative_design_context':design_context,
        },ensure_ascii=False,sort_keys=True)
        settings={'operation':'inquire','canvas_id':store.canvas_id,
            'baseline_candidate_request_sha256':current['request_sha256'],
            'source_sha256':current['source_sha256'],
            'design_guidance_sha256':current.get('design_guidance_sha256'),
            'freshness_format':2,'inquiry_schema_version':1}
        request=build_request(candidate_id='studio-inquiry-'+arch._digest({'settings':settings,'user':user})[:24],
            role='studio_architecture_inquiry',system=_SYSTEM,user=user,settings=settings)
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
    base=_inquiry_root(store);pointer=arch._read(base/'latest_request.json')
    if not pointer:return {'status':'not_started','request':None,'result':None}
    import re
    sha=pointer.get('request_sha256','')
    if not isinstance(sha,str) or not re.fullmatch(r'[0-9a-f]{64}',sha):
        raise ValueError('invalid architecture inquiry pointer')
    request=load_request(base/'requests'/sha/'request.json')
    if request.role!='studio_architecture_inquiry':raise ValueError('unexpected inquiry host role')
    result=arch._read(base/'requests'/sha/'result.json')
    current=arch._candidate(store)
    valid=_live_matches(store,current,request,arch)
    return {'status':('ready' if valid else 'stale') if result else
            ('awaiting_host_agent' if valid else 'stale'),
            'request':request.model_dump() if result is None and valid else None,
            'result':result if valid else None,
            'request_sha256':sha,
            'baseline_candidate_request_sha256':request.settings['baseline_candidate_request_sha256'],
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
            'authority':'noncanonical_inquiry','baseline_candidate_request_sha256':current['request_sha256'],
            'intent':json.loads(request.user)['graph_intent']}
        write_response(folder/'response.json',response)
        atomic_write(folder/'result.json',saved)
    return project_architecture_inquiry(store)
