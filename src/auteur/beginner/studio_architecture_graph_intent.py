"""Validate graph-selected creative intentions against one existing working candidate.

This module deliberately does not import CanvasStore or studio_architecture:
callers hold the canvas lock and check current source / guidance freshness.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AnchorKind = Literal['node','link','genre_interaction','emotion_target','complex_emotion','genre_contract','phase']
GraphOperation = Literal['explain','challenge','explore','compare','connect_to_ask','revise']

COLLECTIONS: dict[str, tuple[str,str]] = {
    'node':('nodes','id'), 'link':('links','id'),
    'genre_interaction':('genre_interactions','id'),
    'emotion_target':('emotion_targets','id'),
    'complex_emotion':('complex_emotions','id'),
    'genre_contract':('genre_contracts','genre_node_id'), 'phase':('phases','id'),
}
# These are source-owned schema properties, never virtual component identities.
FIELDS = {
    'node':{'id','title','category','summary','scope','parent_id'},
    'link':{'id','source','target','function'},
    'genre_interaction':{'id','source_genre_id','target_genre_id','kind','mechanism','risk'},
    'emotion_target':{'id','emotion','role','intended_effect','eliciting_condition','aesthetic_strategy','provenance'},
    'complex_emotion':{'id','title','basic_emotions','context'},
    'genre_contract':{'genre_node_id','role','emotion_target_ids','complex_emotion_ids','trope_functions','narrative_engine','structural_pattern','aesthetic_strategies','payoff_expectations'},
    'phase':{'id','title','order','scope','genres','genre_activations','reader_experience','aesthetic','narrative_function','transition','parallel_with'},
}
REFERENCE_TARGETS = {
    ('node','parent_id'):'node',
    ('genre_contract','emotion_target_ids'):'emotion_target',
    ('genre_contract','complex_emotion_ids'):'complex_emotion',
    ('phase','genre_activations'):'genre_contract',
    ('phase','parallel_with'):'phase',
}

class GraphReference(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    field: str = Field(min_length=1,max_length=80)
    target_kind: AnchorKind
    target_id: str = Field(min_length=1,max_length=80)

class GraphAnchor(BaseModel):
    model_config = ConfigDict(extra='forbid',strict=True)
    kind: AnchorKind
    id: str = Field(min_length=1,max_length=80)
    field: str | None = Field(default=None,max_length=80)
    reference: GraphReference | None = None

    @model_validator(mode='after')
    def exclusive(self):
        if self.field is not None and self.reference is not None:
            raise ValueError('choose either a field or qualified reference')
        return self

class GraphIntent(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    version: Literal[1] = 1
    canvas_id: str = Field(min_length=1,max_length=160)
    # current: the applied working architecture. pending_review: the un-applied revision proposal.
    target: Literal['current','pending_review'] = 'current'
    operation: GraphOperation
    expected_candidate_request_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    anchors: list[GraphAnchor] = Field(default_factory=list,max_length=3)
    author_text: str = Field(min_length=1,max_length=4000)

    @model_validator(mode='after')
    def check_intent(self):
        if not self.author_text.strip(): raise ValueError('author_text must not be blank')
        if not self.anchors and self.target != 'pending_review':
            raise ValueError('at least one graph anchor is required')
        if self.operation == 'connect_to_ask' and len(self.anchors) != 2:
            raise ValueError('connect_to_ask requires exactly two anchors')
        if self.operation == 'compare' and len(self.anchors) < 2:
            raise ValueError('compare requires at least two anchors')
        identifiers=[(a.kind,a.id,a.field,
            (a.reference.field,a.reference.target_kind,a.reference.target_id) if a.reference else None)
            for a in self.anchors]
        if len(identifiers)!=len(set(identifiers)):
            raise ValueError('duplicate graph anchors')
        return self

def _index(candidate: dict, kind: str) -> dict[str,tuple[int,dict]]:
    collection,ident = COLLECTIONS[kind]
    rows=candidate.get(collection,[])
    if not isinstance(rows,list): raise ValueError(f'{collection} is not a list')
    indexed={}
    for i,row in enumerate(rows):
        if not isinstance(row,dict) or not isinstance(row.get(ident),str):
            raise ValueError(f'{collection} contains invalid record')
        key=row[ident]
        if key in indexed: raise ValueError(f'{collection} has ambiguous duplicate identity {key}')
        indexed[key]=(i,row)
    return indexed

def _reference_values(record:dict, field:str) -> list[str]:
    raw=record.get(field)
    if field=='parent_id': return [raw] if isinstance(raw,str) else []
    if field=='genre_activations':
        return [row.get('genre_node_id') for row in raw if isinstance(row,dict)] if isinstance(raw,list) else []
    return raw if isinstance(raw,list) else []

def _short(value:Any,limit:int=560) -> str:
    import json
    result=json.dumps(value,ensure_ascii=False,sort_keys=True)
    return result if len(result)<=limit else result[:limit-1]+'…'

def _recorded_relations(candidate:dict, anchors:list[dict]) -> list[dict]:
    """Returns only source-backed links/interactions/ref memberships around resolved anchors."""
    focused={(a['kind'],a['id']) for a in anchors}
    relations=[]
    for kind,source_key,target_key in (
        ('link','source','target'),('genre_interaction','source_genre_id','target_genre_id'),
    ):
        coll,_=COLLECTIONS[kind]
        for i,edge in enumerate(candidate.get(coll,[])):
            if (kind,edge['id']) in focused or ('node',edge[source_key]) in focused or ('node',edge[target_key]) in focused:
                relations.append(dict(kind=kind,id=edge['id'],sourceRef=f'{coll}/{i}',source=edge[source_key],target=edge[target_key],
                    function=edge.get('function') if kind=='link' else edge.get('mechanism'),authority='recorded'))
    for (owner_kind,field),target_kind in REFERENCE_TARGETS.items():
        coll,_=COLLECTIONS[owner_kind]
        for i,owner in enumerate(candidate.get(coll,[])):
            owner_id=owner.get('genre_node_id') if owner_kind=='genre_contract' else owner.get('id')
            for target_id in _reference_values(owner,field):
                if (owner_kind,owner_id) in focused or (target_kind,target_id) in focused:
                    relations.append(dict(kind='recorded_reference',ownerKind=owner_kind,ownerId=owner_id,
                        field=field,targetKind=target_kind,targetId=target_id,sourceRef=f'{coll}/{i}',authority='recorded'))
    return relations[:48]

def _between(candidate: dict, anchors:list[dict]) -> dict:
    if len(anchors)!=2: return {'status':'not_applicable','relations':[]}
    a,b=anchors
    # Compare the explicitly recorded endpoints and source-backed reference membership, never names.
    relations=[]
    for entry in _recorded_relations(candidate,anchors):
        if entry['kind'] in ('link','genre_interaction'):
            if a['kind']=='node' and b['kind']=='node' and {entry['source'],entry['target']}=={a['id'],b['id']}:
                relations.append(entry)
        elif (entry['ownerKind'],entry['ownerId'])==(a['kind'],a['id']) and (entry['targetKind'],entry['targetId'])==(b['kind'],b['id']):
            relations.append(entry)
        elif (entry['ownerKind'],entry['ownerId'])==(b['kind'],b['id']) and (entry['targetKind'],entry['targetId'])==(a['kind'],a['id']):
            relations.append(entry)
    return {'status':'recorded' if relations else 'no_recorded_relation','relations':relations}

def resolve_anchors(candidate: dict, anchors: list[GraphAnchor]) -> list[dict]:
    """Resolve validated typed anchors against one current candidate; pure and reusable.

    Story Realization uses the same resolution so an emotional or relational anchor keeps one
    source identity across graph inquiry, revision and concrete development.
    """
    if candidate.get('schema_version')!=2:raise ValueError('ArchitectureCandidate v2 required')
    resolved_list=[]
    for anchor in anchors:
        coll,_=COLLECTIONS[anchor.kind]
        indexed=_index(candidate,anchor.kind)
        match=indexed.get(anchor.id)
        if not match:raise ValueError(f'{anchor.kind} {anchor.id} not found in current candidate')
        i,record=match
        resolved={'kind':anchor.kind,'id':anchor.id,'sourceRef':f'{coll}/{i}',
            'authority':'working_noncanonical','recordedSupport':_short(record)}
        if anchor.field:
            if anchor.field not in FIELDS[anchor.kind] or anchor.field not in record:
                raise ValueError('field not recorded on selected element')
            resolved.update(field=anchor.field,fieldValue=record[anchor.field])
        if anchor.reference:
            ref=anchor.reference
            if REFERENCE_TARGETS.get((anchor.kind,ref.field))!=ref.target_kind:
                raise ValueError('reference field or target type not supported')
            values=_reference_values(record,ref.field)
            if ref.target_id not in values: raise ValueError('reference target not recorded')
            if values.count(ref.target_id)!=1: raise ValueError('ambiguous duplicate recorded reference')
            if ref.target_id not in _index(candidate,ref.target_kind):
                raise ValueError('reference target not found in candidate')
            resolved['reference']={'kind':'recorded_reference','field':ref.field,
                'target_kind':ref.target_kind,'target_id':ref.target_id}
        resolved_list.append(resolved)
    return resolved_list


def resolve_intent_views(candidate: dict, anchors: list[GraphAnchor]) -> dict:
    """Resolve anchors and their recorded relations against one candidate (current or proposed)."""
    resolved = resolve_anchors(candidate, anchors)
    return {"anchors": resolved,
            "recorded_relations": _recorded_relations(candidate, resolved),
            "between": _between(candidate, resolved)}


def resolve_graph_intent(candidate:dict,actual_candidate_request_sha256:str,intent:GraphIntent|dict) -> dict:
    if not isinstance(intent,GraphIntent):intent=GraphIntent.model_validate(intent)
    if intent.expected_candidate_request_sha256 != actual_candidate_request_sha256:
        raise ValueError('current candidate request SHA mismatch')
    if candidate.get('schema_version')!=2:raise ValueError('ArchitectureCandidate v2 required')
    anchors=resolve_anchors(candidate,intent.anchors)
    return dict(version=1,target=intent.target,operation=intent.operation,canvas_id=intent.canvas_id,
        expected_candidate_request_sha256=intent.expected_candidate_request_sha256,
        author_text=intent.author_text,anchors=anchors,
        recorded_relations=_recorded_relations(candidate,anchors),between=_between(candidate,anchors))
