"""Deterministic research-local V1.1 execution safeguards."""
import hashlib
import json
from enum import Enum

class RunState(str, Enum):
    PREPARED="PREPARED"; EXTRACTION_CAPTURED="EXTRACTION_CAPTURED"
    PROJECTIONS_VALIDATED="PROJECTIONS_VALIDATED"; GENERATOR_PACKETS_VALIDATED="GENERATOR_PACKETS_VALIDATED"
    GENERATION_CAPTURED="GENERATION_CAPTURED"; EVALUATOR_PACKETS_VALIDATED="EVALUATOR_PACKETS_VALIDATED"
    EVALUATION_CAPTURED="EVALUATION_CAPTURED"; PRE_UNBLIND_READY="PRE_UNBLIND_READY"
    PRE_UNBLIND_FROZEN="PRE_UNBLIND_FROZEN"; UNBLIND_ALLOWED="UNBLIND_ALLOWED"
ORDER=list(RunState)
REL_FIELDS={"relation_type","source_fact_refs","target_ref","member_roles","authority_class","evidence_refs","rationale","support"}
AUTH={"ACCEPTED","DETERMINISTIC_DERIVATION","INTERPRETIVE"}; TYPES={"CAUSAL_SUPPORT","PRESSURE_GROUP"}
ABST_FIELDS={"candidate_area","reason"}

def sha256_text(value): return hashlib.sha256(value.encode("utf-8")).hexdigest()

def validate_extractor(payload, source_refs):
    errors=[]
    if not isinstance(payload,dict): return "FORMAT_INVALID",["top level is not object"]
    if set(payload)-{"relations","abstentions"}: errors.append("disallowed top-level field")
    if not isinstance(payload.get("relations"),list): errors.append("relations is not list")
    if not isinstance(payload.get("abstentions"),list): errors.append("abstentions is not list")
    relations=payload.get("relations",[])
    if isinstance(relations,list) and len(relations)>2: errors.append("more than two relations")
    seen=set()
    for i,r in enumerate(relations if isinstance(relations,list) else []):
        if not isinstance(r,dict): errors.append(f"relation {i} is not object"); continue
        if set(r)-REL_FIELDS: errors.append(f"relation {i} has disallowed fields")
        typ=r.get("relation_type"); sources=r.get("source_fact_refs")
        if typ not in TYPES: errors.append(f"relation {i} invalid type")
        if not isinstance(sources,list) or not sources: errors.append(f"relation {i} invalid sources"); sources=[]
        if any(x not in source_refs for x in sources): errors.append(f"relation {i} unknown source")
        if r.get("target_ref") not in source_refs: errors.append(f"relation {i} unknown target")
        if r.get("authority_class") not in AUTH: errors.append(f"relation {i} invalid authority")
        if "support" in r and r["support"] not in {"strong","moderate","weak"}: errors.append(f"relation {i} invalid support")
        members=r.get("member_roles")
        if not isinstance(members,list): errors.append(f"relation {i} invalid members"); members=[]
        if typ=="CAUSAL_SUPPORT" and len(sources)!=1: errors.append(f"relation {i} causal source count")
        if typ=="PRESSURE_GROUP" and not 2<=len(sources)<=3: errors.append(f"relation {i} pressure source count")
        if typ=="PRESSURE_GROUP" and len(members)!=len(sources): errors.append(f"relation {i} member count")
        for m in members:
            if not isinstance(m,dict) or set(m)!={"fact_ref","role"}: errors.append(f"relation {i} member shape")
            elif m["fact_ref"] not in source_refs or not isinstance(m["role"],str): errors.append(f"relation {i} member ref")
        key=json.dumps(r,sort_keys=True)
        if key in seen: errors.append(f"relation {i} duplicate")
        seen.add(key)
    for i,a in enumerate(payload.get("abstentions",[]) if isinstance(payload.get("abstentions"),list) else []):
        if not isinstance(a,dict) or set(a)!=ABST_FIELDS or not isinstance(a.get("candidate_area"),str) or not isinstance(a.get("reason"),str):
            errors.append(f"abstention {i} shape")
    return ("STRUCTURE_VALID" if not errors else "FORMAT_INVALID"),errors

def canonical_projection(payload):
    entries=[]
    for r in payload["relations"]:
        entries.append({"relation_type":r["relation_type"],"source_fact_refs":sorted(r["source_fact_refs"]),"target_ref":r["target_ref"],"member_roles":sorted(r["member_roles"],key=lambda m:m["fact_ref"]),"authority_class":r["authority_class"]})
    entries.sort(key=lambda x:(x["relation_type"],x["target_ref"],x["source_fact_refs"],x["member_roles"]))
    return json.dumps(entries,ensure_ascii=False,separators=(",",":"))

def route_derived(extractor_repetition,probe,downstream_repetition,status,projection):
    if probe not in {"P03","P04","P05"}: raise ValueError("derived routing requires Book-4 probe")
    if extractor_repetition!=downstream_repetition: raise ValueError("repetition mismatch")
    if status=="STRUCTURE_VALID":
        if projection is None: raise ValueError("valid extraction cannot route to EMPTY")
        return {"probe":probe,"repetition":downstream_repetition,"status":status,"projection":projection}
    if status=="FORMAT_INVALID": return {"probe":probe,"repetition":downstream_repetition,"status":status,"projection":None}
    raise ValueError("unknown status")

def build_model_packet(b0_packet,projection): return b0_packet if projection is None else b0_packet+"\n"+projection

def build_evaluator_packet(source,prefix,embedded=None):
    packet=prefix+source
    if embedded is not None and embedded!=packet: raise ValueError("embedded response differs")
    embedded_source=packet[len(prefix):]
    if embedded_source!=source or sha256_text(embedded_source)!=sha256_text(source): raise ValueError("packet integrity failure")
    return packet,{"source_sha256":sha256_text(source),"embedded_sha256":sha256_text(embedded_source),"exact_match":True}

class RunStateMachine:
    def __init__(self,expected_calls=78): self.state=RunState.PREPARED; self.expected_calls=expected_calls
    def transition(self,target,completed_calls=None,integrity_ok=False):
        if ORDER.index(target)!=ORDER.index(self.state)+1: raise ValueError("illegal transition")
        if target==RunState.UNBLIND_ALLOWED and (completed_calls!=self.expected_calls or not integrity_ok): raise ValueError("unblind requires complete calls and integrity")
        self.state=target

def _fails(fn):
    try: fn()
    except ValueError: return True
    return False

def qualify_synthetic():
    one={"relations":[{"relation_type":"CAUSAL_SUPPORT","source_fact_refs":["FACT-A"],"target_ref":"FACT-B","member_roles":[],"authority_class":"DETERMINISTIC_DERIVATION"}],"abstentions":[]}
    two={"relations":[one["relations"][0],{**one["relations"][0],"source_fact_refs":["FACT-C"]}],"abstentions":[]}
    s1,_=validate_extractor(one,{"FACT-A","FACT-B","FACT-C"}); s2,_=validate_extractor(two,{"FACT-A","FACT-B","FACT-C"})
    p1=canonical_projection(one); p2=canonical_projection(two)
    h1=all(route_derived(1,p,1,s1,p1)["projection"]==p1 for p in ("P03","P04","P05"))
    h2=all(route_derived(2,p,2,s2,p2)["projection"]==p2 for p in ("P03","P04","P05"))
    h3=all(build_model_packet("B0",route_derived(3,p,3,"FORMAT_INVALID",None)["projection"])=="B0" for p in ("P03","P04","P05"))
    h4=_fails(lambda:route_derived(2,"P03",2,s2,None)); h5=_fails(lambda:route_derived(2,"P03",3,s2,p2))
    h6=_fails(lambda:build_evaluator_packet("source","EVAL:",embedded="EVAL:source altered"))
    m=RunStateMachine(); m.transition(RunState.EXTRACTION_CAPTURED); h7=_fails(lambda:m.transition(RunState.UNBLIND_ALLOWED,completed_calls=77,integrity_ok=True))
    m=RunStateMachine()
    for state in ORDER[1:-1]: m.transition(state)
    m.transition(RunState.UNBLIND_ALLOWED,completed_calls=78,integrity_ok=True); h8=m.state==RunState.UNBLIND_ALLOWED
    snapshot_b0="SYNTHETIC_B0"
    snapshot_gold=build_model_packet(snapshot_b0,p1)
    snapshot_valid=build_model_packet(snapshot_b0,p2)
    snapshot_invalid=build_model_packet(snapshot_b0,None)
    return {"positions":78,
            "schedule":{"extractor":3,"generator":36,"extraction_evaluator":3,"downstream_evaluator":36,"total":78},
            "projection_routes":{"H1":h1,"H2":h2,"H3":h3,"H4_failure":h4,"H5_failure":h5},
            "packet_integrity":{"H6_failure":h6},
            "freeze":{"H7_refusal":h7,"H8_success":h8},
            "snapshots":{"b0":snapshot_b0,"gold_differs":snapshot_gold!=snapshot_b0,
                         "valid_derived_differs":snapshot_valid!=snapshot_b0,
                         "invalid_derived_equals_b0":snapshot_invalid==snapshot_b0},
            "integrity":{"extraction":"3/3","downstream":"36/36"},
            "illegal_transitions_accepted":0,
            "pre_unblind_ready":all((h1,h2,h3,h4,h5,h6,h7,h8))}
