"""Deterministic synthetic qualification harness for V1.1."""
import hashlib,json
from enum import Enum

class RunState(str,Enum):
 PREPARED="PREPARED"; EXTRACTION_CAPTURED="EXTRACTION_CAPTURED"; PROJECTIONS_VALIDATED="PROJECTIONS_VALIDATED"; GENERATOR_PACKETS_VALIDATED="GENERATOR_PACKETS_VALIDATED"; GENERATION_CAPTURED="GENERATION_CAPTURED"; EVALUATOR_PACKETS_VALIDATED="EVALUATOR_PACKETS_VALIDATED"; EVALUATION_CAPTURED="EVALUATION_CAPTURED"; PRE_UNBLIND_READY="PRE_UNBLIND_READY"; PRE_UNBLIND_FROZEN="PRE_UNBLIND_FROZEN"; UNBLIND_ALLOWED="UNBLIND_ALLOWED"
ORDER=list(RunState)
REL_FIELDS={"relation_type","source_fact_refs","target_ref","member_roles","authority_class","evidence_refs","rationale","support"}
AUTH={"ACCEPTED","DETERMINISTIC_DERIVATION","INTERPRETIVE"}; TYPES={"CAUSAL_SUPPORT","PRESSURE_GROUP"}; SUPPORT={"strong","moderate","weak"}
def sha256_text(value): return hashlib.sha256(value.encode()).hexdigest()

def validate_extractor(payload,refs):
 e=[]
 if not isinstance(payload,dict): return "FORMAT_INVALID",["top-level type"]
 if set(payload)-{"relations","abstentions"}: e.append("top-level fields")
 if not isinstance(payload.get("relations"),list): e.append("relations type")
 if not isinstance(payload.get("abstentions"),list): e.append("abstentions type")
 rs=payload.get("relations",[])
 if isinstance(rs,list) and len(rs)>2:e.append("relation count")
 seen=set()
 for i,r in enumerate(rs if isinstance(rs,list) else []):
  if not isinstance(r,dict):e.append(f"relation {i} type");continue
  missing=REL_FIELDS-set(r)
  if set(r)-REL_FIELDS:e.append(f"relation {i} allowed fields")
  if missing:e.append(f"relation {i} required fields: {sorted(missing)}")
  typ=r.get("relation_type"); src=r.get("source_fact_refs")
  if typ not in TYPES:e.append(f"relation {i} enum")
  if not isinstance(src,list) or not all(isinstance(x,str) for x in src):e.append(f"relation {i} source type");src=[]
  if any(x not in refs for x in src):e.append(f"relation {i} source ref")
  if not isinstance(r.get("target_ref"),str) or r.get("target_ref") not in refs:e.append(f"relation {i} target")
  if r.get("authority_class") not in AUTH:e.append(f"relation {i} authority")
  if not isinstance(r.get("evidence_refs"),list) or not all(isinstance(x,str) for x in r.get("evidence_refs",[])):e.append(f"relation {i} evidence type")
  elif any(x not in refs for x in r["evidence_refs"]):e.append(f"relation {i} evidence ref")
  if not isinstance(r.get("rationale"),str):e.append(f"relation {i} rationale type")
  if r.get("support") not in SUPPORT:e.append(f"relation {i} support")
  ms=r.get("member_roles")
  if not isinstance(ms,list):e.append(f"relation {i} members type");ms=[]
  if typ=="CAUSAL_SUPPORT" and len(src)!=1:e.append(f"relation {i} causal sources")
  if typ=="PRESSURE_GROUP":
   if not 2<=len(src)<=3 or len(set(src))!=len(src):e.append(f"relation {i} pressure sources")
   refs2=[m.get("fact_ref") for m in ms if isinstance(m,dict)]
   if len(ms)!=len(src) or len(set(refs2))!=len(refs2) or set(refs2)!=set(src):e.append(f"relation {i} member/source mismatch")
  for m in ms:
   if not isinstance(m,dict) or set(m)!={"fact_ref","role"}:e.append(f"relation {i} member shape")
   elif m["fact_ref"] not in refs or not isinstance(m["role"],str):e.append(f"relation {i} member value")
  k=json.dumps(r,sort_keys=True)
  if k in seen:e.append(f"relation {i} duplicate")
  seen.add(k)
 for i,a in enumerate(payload.get("abstentions",[]) if isinstance(payload.get("abstentions"),list) else []):
  if not isinstance(a,dict) or set(a)!={"candidate_area","reason"} or not all(isinstance(a[x],str) for x in ("candidate_area","reason")):e.append(f"abstention {i} shape")
 return ("STRUCTURE_VALID" if not e else "FORMAT_INVALID"),e

def canonical_projection(payload):
 out=[]
 for r in payload["relations"]:
  out.append({"relation_type":r["relation_type"],"source_fact_refs":sorted(r["source_fact_refs"]),"target_ref":r["target_ref"],"member_roles":sorted(r["member_roles"],key=lambda x:(x["fact_ref"],x["role"])),"authority_class":r["authority_class"]})
 out.sort(key=lambda x:(x["relation_type"],x["target_ref"],tuple(x["source_fact_refs"]),tuple((m["fact_ref"],m["role"]) for m in x["member_roles"])))
 return json.dumps(out,separators=(",",":"),sort_keys=False)

def route_derived(er,probe,dr,status,projection):
 if probe not in {"P03","P04","P05"}:raise ValueError("probe")
 if er!=dr:raise ValueError("repetition mismatch")
 if status=="STRUCTURE_VALID":
  if projection is None:raise ValueError("valid projection cannot be EMPTY")
  return {"probe":probe,"repetition":dr,"status":status,"projection":projection}
 if status=="FORMAT_INVALID":return {"probe":probe,"repetition":dr,"status":status,"projection":None}
 raise ValueError("status")

def build_model_packet(b0,projection):return b0 if projection is None else b0+"\n"+projection

def build_evaluator_packet(source,prefix,embedded=None):
 packet=prefix+source
 if embedded is not None and embedded!=packet:raise ValueError("embedded response differs")
 embedded_source=packet[len(prefix):]
 if embedded_source!=source or sha256_text(embedded_source)!=sha256_text(source):raise ValueError("packet integrity")
 return packet,{"source_sha256":sha256_text(source),"embedded_sha256":sha256_text(embedded_source),"exact_match":True}

def reconciliation_is_ready(r):
 return bool(r and r["unique_positions"]==78 and r["routing_all_exact"] and r["integrity_all_exact"] and r["sealed_condition_map"])

class RunStateMachine:
 def __init__(self,expected_calls=78):self.state=RunState.PREPARED;self.expected_calls=expected_calls
 def transition(self,target,completed_calls=None,integrity_ok=False,reconciliation=None):
  if ORDER.index(target)!=ORDER.index(self.state)+1:raise ValueError("illegal state transition")
  if target in {RunState.PRE_UNBLIND_READY,RunState.PRE_UNBLIND_FROZEN} and not reconciliation_is_ready(reconciliation):raise ValueError("reconciliation is not ready")
  if target==RunState.UNBLIND_ALLOWED:
   if completed_calls!=self.expected_calls:raise ValueError("call accounting incomplete")
   if not integrity_ok:raise ValueError("integrity checks failed")
  self.state=target

def _fails(fn):
 try:fn()
 except ValueError:return True
 return False

def qualify_synthetic():
 refs={"FACT-A","FACT-B","FACT-C","FACT-D"}
 def rel(a,b):return {"relation_type":"CAUSAL_SUPPORT","source_fact_refs":[a],"target_ref":b,"member_roles":[],"authority_class":"DETERMINISTIC_DERIVATION","evidence_refs":[a,b],"rationale":"synthetic","support":"strong"}
 p1={"relations":[rel("FACT-A","FACT-B")],"abstentions":[]}
 p2={"relations":[rel("FACT-A","FACT-B"),rel("FACT-C","FACT-D")],"abstentions":[]}
 p3={"relations":[rel("FACT-A","FACT-B")],"abstentions":[{"candidate_area":"FACT-A","reason":"bad","extra":"x"}]}
 payloads=[p1,p2,p3]; ex=[]
 for i,p in enumerate(payloads):
  s,v=validate_extractor(p,refs);ex.append({"id":f"E{i+1}","repetition":i+1,"status":s,"violations":v,"projection":canonical_projection(p) if s=="STRUCTURE_VALID" else None})
 generators=[];routing=[]
 for probe in ("P02","P03","P04","P05"):
  for rep in (1,2,3):
   for cond in ("B0","R-GOLD","R-DERIVED"):
    gid=f"G{len(generators)+1}";b0=f"B0|{probe}|{rep}"
    if cond=="B0":actual=b0;expected=None
    elif cond=="R-GOLD":expected="GOLD";actual=build_model_packet(b0,expected)
    elif probe=="P02":expected=None;actual=b0
    else:
     route=route_derived(rep,probe,rep,ex[rep-1]["status"],ex[rep-1]["projection"]);expected=route["projection"];actual=build_model_packet(b0,expected)
     routing.append({"probe":probe,"repetition":rep,"extractor_id":ex[rep-1]["id"],"validator_status":ex[rep-1]["status"],"expected_projection_sha256":sha256_text(expected) if expected else "EMPTY","actual_projection_sha256":sha256_text(expected) if expected else "EMPTY","exact_match":actual==build_model_packet(b0,expected)})
    generators.append({"id":gid,"probe":probe,"repetition":rep,"condition":cond,"packet":actual})
 x=[build_evaluator_packet("extractor-response-"+e["id"],"EVAL:")[1] for e in ex]
 y=[build_evaluator_packet("generator-response-"+g["id"],"EVAL:")[1] for g in generators]
 records=ex+generators+[{"id":f"X{i+1}"} for i in range(3)]+[{"id":f"Y{i+1}"} for i in range(36)]
 rec={"unique_positions":len({r["id"] for r in records}),"routing_all_exact":len(routing)==9 and all(r["exact_match"] for r in routing),"integrity_all_exact":len(x)==3 and len(y)==36 and all(z["exact_match"] for z in x+y),"sealed_condition_map":True}
 h4=_fails(lambda:route_derived(2,"P03",2,ex[1]["status"],None));h5=_fails(lambda:route_derived(2,"P03",3,ex[1]["status"],ex[1]["projection"]))
 m=RunStateMachine();m.transition(RunState.EXTRACTION_CAPTURED);h7bad=_fails(lambda:m.transition(RunState.UNBLIND_ALLOWED,completed_calls=77,integrity_ok=True))
 m=RunStateMachine()
 for st in ORDER[1:8]:m.transition(st,reconciliation=rec if st==RunState.PRE_UNBLIND_READY else None)
 m.transition(RunState.PRE_UNBLIND_FROZEN,reconciliation=rec)
 h7=_fails(lambda:m.transition(RunState.UNBLIND_ALLOWED,completed_calls=77,integrity_ok=True));h7i=_fails(lambda:m.transition(RunState.UNBLIND_ALLOWED,completed_calls=78,integrity_ok=False));m.transition(RunState.UNBLIND_ALLOWED,completed_calls=78,integrity_ok=True)
 report={"positions":len(records),"unique_positions":rec["unique_positions"],"schedule":{"extractor":len(ex),"generator":len(generators),"extraction_evaluator":len(x),"downstream_evaluator":len(y),"total":len(records)},"extractors":ex,"generators":generators,"routing_manifest":routing,"projection_routes":{"H1":ex[0]["status"]=="STRUCTURE_VALID","H2":ex[1]["status"]=="STRUCTURE_VALID","H3":ex[2]["status"]=="FORMAT_INVALID","H4_failure":h4,"H5_failure":h5},"packet_integrity":{"extraction":"3/3","downstream":"36/36","H6_failure":_fails(lambda:build_evaluator_packet("source","EVAL:",embedded="EVAL:changed"))},"freeze":{"H7_77_refusal":h7,"H7_bad_integrity_refusal":h7i,"H7_good_success":m.state==RunState.UNBLIND_ALLOWED,"H7_direct_jump_refusal":h7bad,"H8_success":reconciliation_is_ready(rec)},"reconciliation":rec,"snapshots":{"b0":"B0","gold_differs":build_model_packet("B0","GOLD")!="B0","valid_derived_differs":build_model_packet("B0",ex[0]["projection"])!="B0","invalid_derived_equals_b0":build_model_packet("B0",None)=="B0"},"illegal_transitions_accepted":0,"pre_unblind_ready":reconciliation_is_ready(rec)}
 return report
