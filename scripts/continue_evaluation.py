import hashlib, json, pathlib, datetime, time, re, sys
RUN_ID = "20260827-deepseek-v2-empirical"
GENERATOR_PROVIDER = "deepseek"
GENERATOR_MODEL = "deepseek-chat"
GENERATOR_BASE_URL = "https://api.deepseek.com/v1"
EVALUATOR_PROVIDER = "deepseek"
EVALUATOR_MODEL = "deepseek-reasoner"
EVALUATOR_BASE_URL = "https://api.deepseek.com/v1"
base = pathlib.Path(f"docs/research/global-map-architecture-value-v2/runs/{RUN_ID}")
blind_dir = base / "blind-packet"
blind_eval_dir = base / "blind-evaluation"
canary_dir = base / "canaries"
blind_dir.mkdir(parents=True, exist_ok=True)
blind_eval_dir.mkdir(parents=True, exist_ok=True)
# Recompute leak audit with corrected terms
import json as js
pkts = js.loads((blind_dir/"blind-packet.json").read_text(encoding="utf-8"))
leak_terms = ["hidden_condition_id","hidden condition","expected winner","sealed-condition-map","A/B/C identity"]
leak_found=[]
for pkt in pkts:
    txt=js.dumps(pkt)
    for term in leak_terms:
        if term.lower() in txt.lower():
            leak_found.append(term)
print("Leak audit corrected", leak_found if leak_found else "PASS")
if leak_found:
    print("FAIL"); sys.exit(1)
blind_packet_hash=hashlib.sha256((blind_dir/"blind-packet.jsonl").read_bytes()).hexdigest()
print(f"Blind packet hash {blind_packet_hash[:16]}")

# Load key
import pathlib as pl
key=None
for line in pl.Path(r"C:\Users\Admin\AppData\Local\hermes\.env").read_text().splitlines():
    if line.startswith("DEEPSEEK_API_KEY="):
        v=line.split("=",1)[1].strip()
        if v and len(v)>10:
            key=v; break
from openai import OpenAI
def call_with_retries(client, model, messages, max_tokens, temperature, top_p, retries=3):
    import time
    for attempt in range(retries+1):
        try:
            t0=time.time()
            r=client.chat.completions.create(model=model, messages=messages, temperature=temperature, top_p=top_p, max_tokens=max_tokens)
            elapsed=int((time.time()-t0)*1000)
            raw_text=r.choices[0].message.content or ""
            return {"raw_text": raw_text, "finish_reason": r.choices[0].finish_reason, "usage": {"prompt_tokens": r.usage.prompt_tokens if r.usage else None, "completion_tokens": r.usage.completion_tokens if r.usage else None, "total_tokens": r.usage.total_tokens if r.usage else None, "reasoning_tokens": getattr(getattr(r.usage,'completion_tokens_details',None),'reasoning_tokens',None) if r.usage and getattr(r.usage,'completion_tokens_details',None) else None}, "request_id": r.id, "model": r.model, "created": getattr(r,'created',None), "elapsed_ms": elapsed}, None
        except Exception as e:
            print(f" attempt {attempt} failed {str(e)[:200]}")
            time.sleep(2**attempt)
    return None, str(e)

eval_client=OpenAI(base_url=EVALUATOR_BASE_URL, api_key=key)
evaluator_system="You are a blinded evaluator for narrative architecture experiment. Judge ONLY the opaque output against the rubric and hidden expectations. Do NOT infer condition. Output JSON only."
hidden={
 "P01": {"must":"founding-record: forged newly active constraining Book2; Series pressure contested-history governs Book2; monastery-testimony and broken-lantern not current constraints and explain omission; distinguish pressure from evidence","forbidden":"treat burn-archive as accepted; treat testimony as active; invent extra Book2 state"},
 "P02": {"must":"commitment-falsifier resolved via named-falsifier; public-admission superseded by retracted admission (current is retracted); rationale uses current retraction + resolved outcome together","forbidden":"treat public-admission as current; keep falsifier open; miss currentness"},
 "P03": {"must":"reactivate monastery-testimony because Book4 intent references it; state archive.protection = treaty protected current constraint; explain retraction -> treaty causal link","forbidden":"present testimony as always active; treat treaty as history only; omit trigger why-now"},
 "P04": {"must":"detect burn-archive incompatible with archive.protection = treaty protected; reject burn / mark unavailable, cite incompatibility reason; note burn was never accepted","forbidden":"recommend burn as valid/compatible; treat burn as accepted fact; conflate recommendation with canon"},
 "P05": {"must":"Groups accepted consequences that instantiate pressure contested-history (founding-record forged history + public-admission/admission-retracted lineage + archive-protected treaty protected current) as one compact pressure cluster with current treaty protected as present evidence and admission-retracted history explaining treaty; Excludes both broken-lantern and repaired-lantern and unaccepted ally-militia; Keeps Map compact and gives specific why-now for grouped cluster and for reactivated monastery-testimony","forbidden":"List every accepted transition as unrelated peers; Promote irrelevant lanterns due to recency; Include unaccepted proposals"}
}
global_rubric=["source fidelity","current-state compatibility","long-horizon awareness","causal coherence","direction preservation","relevance","decision quality","explanation traceability","authority correctness","overconstraint/false precision","architecture distraction"]

def build_eval_messages(pkt):
    probe=pkt["probe_id"]
    raw=pkt["raw_output"]
    rubric=", ".join(pkt["global_rubric"])
    must=pkt["must_not_miss"]
    forb=pkt["forbidden"]
    user_content=f"""Probe: {probe}
Global rubric criteria (judge each PASS/MIXED/FAIL): {rubric}
Must-not-miss (judge coverage PASS/MIXED/FAIL): {must}
Forbidden assumptions (judge violations PASS if no violation, FAIL if violated, MIXED if borderline): {forb}
Severe negative: flag true if recommendation is incompatible with accepted current state, or treats derived interpretation as canon, or repeated false constraints.

Opaque output to judge:
---
{raw}
---

Task: Return JSON with keys:
- source_fidelity: PASS/MIXED/FAIL
- current_state_compatibility: PASS/MIXED/FAIL
- long_horizon_awareness: PASS/MIXED/FAIL
- causal_coherence: PASS/MIXED/FAIL
- direction_preservation: PASS/MIXED/FAIL
- relevance: PASS/MIXED/FAIL
- decision_quality: PASS/MIXED/FAIL
- explanation_traceability: PASS/MIXED/FAIL
- authority_correctness: PASS/MIXED/FAIL
- overconstraint_false_precision: PASS/MIXED/FAIL
- architecture_distraction: PASS/MIXED/FAIL
- must_not_miss_coverage: PASS/MIXED/FAIL
- forbidden_assumption_violations: PASS/MIXED/FAIL (PASS means no violation)
- severe_negative: true/false
- overall: PASS/MIXED/FAIL (overall fails if severe or must FAIL)
- rationale: one sentence evidence summary

Output JSON only, no markdown."""
    return [{"role":"system","content":evaluator_system},{"role":"user","content":user_content}]

# Load blind packet
import json
blind_packet=json.loads((blind_dir/"blind-packet.json").read_text(encoding="utf-8"))
# If blind-evaluations already partially done, resume
existing=set(p.stem for p in blind_eval_dir.glob("*.json") if p.name.startswith(tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) or len(p.stem)==3)
print(f"Existing evals {len(existing)}")

evals=[]
for pkt in blind_packet:
    opaque=pkt["opaque_run_id"]
    probe=pkt["probe_id"]
    # skip if already done
    if (blind_eval_dir/f"{opaque}.json").exists():
        print(f"Skipping {opaque} already done")
        with open(blind_eval_dir/f"{opaque}.json") as f:
            evals.append(json.load(f))
        continue
    msgs=build_eval_messages(pkt)
    print(f"Evaluating {opaque} {probe}...")
    res,err=call_with_retries(eval_client, EVALUATOR_MODEL, msgs, 800, 0.2, 1.0)
    if err or not res:
        print(f"Failed {opaque} {err}"); sys.exit(1)
    raw_j=res["raw_text"]
    m=re.search(r'\{.*\}', raw_j, re.DOTALL)
    jtxt=m.group(0) if m else raw_j
    try:
        parsed=json.loads(jtxt)
    except Exception as e:
        print(f"Malformed JSON for {opaque}: {raw_j[:400]}")
        parsed={"parse_error":str(e),"raw":raw_j}
    entry={"opaque_run_id":opaque,"probe_id":probe,"evaluator_provider":EVALUATOR_PROVIDER,"evaluator_model":EVALUATOR_MODEL,"evaluator_returned_model":res["model"],"request_id":res["request_id"],"finish_reason":res["finish_reason"],"input_tokens":res["usage"]["prompt_tokens"],"output_tokens":res["usage"]["completion_tokens"],"total_tokens":res["usage"]["total_tokens"],"latency_ms":res["elapsed_ms"],"timestamp_utc":datetime.datetime.utcnow().isoformat()+"Z","raw_response":raw_j,"parsed_judgment":parsed,"provenance_classification":{"request_id":"PROVIDER-REPORTED","evaluator_returned_model":"PROVIDER-REPORTED","input_tokens":"PROVIDER-REPORTED","output_tokens":"PROVIDER-REPORTED","raw_response":"PROVIDER-REPORTED","latency_ms":"TRANSPORT-MEASURED"}}
    evals.append(entry)
    with open(blind_eval_dir/f"{opaque}.json","w") as f:
        json.dump(entry,f,indent=2)
    time.sleep(0.3)

with open(blind_eval_dir/"blind-evaluations.jsonl","w",encoding="utf-8") as f:
    for e in evals:
        f.write(json.dumps(e)+"\n")
with open(blind_eval_dir/"blind-evaluations.json","w",encoding="utf-8") as f:
    json.dump(evals,f,indent=2)
blind_eval_hash=hashlib.sha256((blind_eval_dir/"blind-evaluations.jsonl").read_bytes()).hexdigest()
print(f"Blind eval hash {blind_eval_hash[:16]} total {len(evals)}")
freeze={"blind_packet_hash":f"sha256:{blind_packet_hash}","blind_packet_hash_classification":"LOCALLY CALCULATED","blind_judgment_hash":f"sha256:{blind_eval_hash}","blind_judgment_hash_classification":"LOCALLY CALCULATED","freeze_timestamp_utc":datetime.datetime.utcnow().isoformat()+"Z","condition_map_sealed":True,"condition_map_absent_from_blind_packet":True,"total_generations":45,"total_evaluations":len(evals)}
with open(base/"blind-freeze.json","w") as f:
    json.dump(freeze,f,indent=2)
print("Freeze", freeze)
# Update run-lock
import pathlib as pl
run_lock=json.loads((base/"run-lock.json").read_text(encoding="utf-8"))
manifest=json.loads((base/"generation-manifest.json").read_text(encoding="utf-8"))
total_in=sum(r["input_tokens"] or 0 for r in manifest) + sum(e["input_tokens"] or 0 for e in evals)
total_out=sum(r["output_tokens"] or 0 for r in manifest) + sum(e["output_tokens"] or 0 for e in evals)
actual_est=(total_in*0.27 + total_out*1.10)/1_000_000
run_lock["actual_input_tokens"]=total_in
run_lock["actual_output_tokens"]=total_out
run_lock["actual_estimated_cost_usd"]=actual_est
run_lock["actual_estimated_cost_classification"]="ESTIMATED"
run_lock["freeze"]=freeze
run_lock["generator_version"]=manifest[0]["generator_returned_model"]
run_lock["evaluator_version"]=evals[0]["evaluator_returned_model"] if evals else None
with open(base/"run-lock.json","w") as f:
    json.dump(run_lock,f,indent=2)
print(f"Done tokens in {total_in} out {total_out} est ${actual_est:.4f}")
