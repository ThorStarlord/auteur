"""Attempt 4 mechanical bridge; routing and validation delegate to the frozen harness."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/"docs/research/story-instance-relationship-extraction-v1-1/harness"))
from execution_harness import build_model_packet,build_evaluator_packet,canonical_projection,route_derived,sha256_text,validate_extractor
REFS={"series_direction.yaml#contested-history","book_1_realization.yaml#founding-record","book_1_realization.yaml#monastery-testimony","book_2_realization.yaml#public-admission","book_2_realization.yaml#admission-retracted","book_3_direction.yaml#protect-archive-after-retraction","book_3_realization.yaml#archive-protected","book_3_realization.yaml#lantern-repaired","deterministic-current-state"}
GOLD=json.dumps([{"relation_type":"CAUSAL_SUPPORT","source_fact_refs":["book_2_realization.yaml#admission-retracted"],"target_ref":"book_3_realization.yaml#archive-protected","member_roles":[],"authority_class":"INTERPRETIVE"},{"relation_type":"PRESSURE_GROUP","source_fact_refs":["book_1_realization.yaml#founding-record","book_2_realization.yaml#admission-retracted","book_3_realization.yaml#archive-protected"],"target_ref":"series_direction.yaml#contested-history","member_roles":[{"fact_ref":"book_1_realization.yaml#founding-record","role":"originating_history"},{"fact_ref":"book_2_realization.yaml#admission-retracted","role":"causal_pivot"},{"fact_ref":"book_3_realization.yaml#archive-protected","role":"current_constraint"}],"authority_class":"DETERMINISTIC_DERIVATION"}],separators=(",",":"))
def main(root):
 root=Path(root); schedule=json.loads((root/"manifests/blinded-schedule.json").read_text())["schedule"]; bases=json.loads((root/"packets/base-prompts.json").read_text())
 cmap={x["id"]:x for x in json.loads(Path(r"C:\Users\Admin\AppData\Local\Temp\v11-r5-condition-map-readable.json").read_text())}
 ext=sorted([x for x in schedule if x["role"]=="extractor"],key=lambda x:x["repetition"]); extracted=[]
 for e in ext:
  raw=json.loads((root/f"raw/extractor-{e['id']}.json").read_text())["response"]
  try: payload=json.loads(raw); parse="PASS"
  except Exception as exc: payload=None;parse="FAIL";parse_error=str(exc)
  if payload is None: status="FORMAT_INVALID"; violations=[parse_error]; projection=None
  else: status,violations=validate_extractor(payload,REFS); projection=canonical_projection(payload) if status=="STRUCTURE_VALID" else None
  extracted.append({"id":e["id"],"repetition":e["repetition"],"parse_status":parse,"status":status,"violations":violations,"projection":projection,"projection_sha256":sha256_text(projection) if projection is not None else "EMPTY"})
 emap={x["repetition"]:x for x in extracted}; out=[]
 for g in sorted([x for x in schedule if x["role"]=="generator"],key=lambda x:x["schedule_position"]):
  base="Do not call or use tools. Answer only from material contained in this prompt. "+bases[g["probe"]]; c=cmap[g["id"]]
  if c["condition"]=="B0" or g["probe"]=="P02" and c["condition"]=="R-DERIVED": p=base
  elif c["condition"]=="R-GOLD": p=build_model_packet(base,GOLD)
  else: p=build_model_packet(base,route_derived(g["repetition"],g["probe"],g["repetition"],emap[g["repetition"]]["status"],emap[g["repetition"]]["projection"])["projection"])
  out.append({"id":g["id"],"prompt":p})
 result={"extractors":extracted,"generators":out}
 mode=sys.argv[2] if len(sys.argv)>2 else "all"
 if mode=="summary": result.pop("generators",None)
 elif mode.startswith("generator:"): result={"generator":next(x for x in out if x["id"]==mode.split(":",1)[1])}
 elif mode.startswith("evaluator:"):
  eid=mode.split(":",1)[1]; row=next(x for x in schedule if x["id"]==eid)
  if row["role"]=="extraction_evaluator": source=json.loads((root/f"raw/extractor-{next(x for x in schedule if x['role']=='extractor' and x['repetition']==row['repetition'])['id']}.json").read_text())["response"]; prefix="Evaluate this extractor response against the frozen semantic gold reference. Use semantic equivalence, not exact wording. Return a concise JSON evaluation only. Gold reference: GOLD-R01 is causal support from admission-retracted to archive-protected; GOLD-R02 is a pressure group of founding-record, admission-retracted, and archive-protected targeting contested-history.\nEXACT RESPONSE:\n"
  else: source=json.loads((root/f"raw/generator-{row['pair_generator_id']}.json").read_text())["response"]; prefix="Evaluate this bounded downstream recommendation for the supplied story decision. Return a concise JSON evaluation only. Assess recommendation validity, use of accepted facts, principal tradeoff, irrelevant exclusions, and whether it invents facts or changes canon.\nEXACT RESPONSE:\n"
  packet,integrity=build_evaluator_packet(source,prefix); result={"id":eid,"prompt":packet,"integrity":integrity}
 print(json.dumps(result,separators=(",",":")))
if __name__=="__main__": main(sys.argv[1])


