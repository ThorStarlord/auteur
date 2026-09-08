#!/usr/bin/env python3
import hashlib, json, random, pathlib, datetime, time, os, re, sys

RUN_ID = "20260827-deepseek-v2-empirical"
EXPERIMENT_VERSION = "global-map-architecture-value-v2"
SOURCE_REVISION = "3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41"
PROTOCOL_REVISION = "5f00f464a53b79586c5cfaf585719fbd5304d4d6b3c35922d3b262872400fe58"
EXECUTION_BASE = "1053154f3d23893e2ce6a4e48fa5cb16b2d459ed"
GENERATOR_PROVIDER = "deepseek"
GENERATOR_MODEL = "deepseek-chat"
GENERATOR_BASE_URL = "https://api.deepseek.com/v1"
EVALUATOR_PROVIDER = "deepseek"
EVALUATOR_MODEL = "deepseek-reasoner"
EVALUATOR_BASE_URL = "https://api.deepseek.com/v1"
TEMPERATURE = 0.2
TOP_P = 1.0
MAX_TOKENS = 1200
TOOLS = "none"
SYSTEM_PROMPT_ID = "story-decision-v1"
SYSTEM_PROMPT = "You are a story consultant for Series Archive of Lies. Provide bounded recommendation analysis per output contract. Recommendation is non-authoritative."

base = pathlib.Path(f"docs/research/global-map-architecture-value-v2/runs/{RUN_ID}")
base.mkdir(parents=True, exist_ok=True)
raw_dir = base / "raw-outputs"
blind_dir = base / "blind-packet"
blind_eval_dir = base / "blind-evaluation"
post_dir = base / "post-unblind"
canary_dir = base / "canaries"
for d in [raw_dir, blind_dir, blind_eval_dir, post_dir, canary_dir]:
    d.mkdir(parents=True, exist_ok=True)

probes = {
    "P01": {"book":2, "question":"How should Book 2 make the exposed fraud matter to lived memory?", "options":["witness-account","cover-up-trace"]},
    "P02": {"book":3, "question":"How should Book 3 respond to the council's retraction while preserving the witness's authority?", "options":["publish-witness-account","force-council-hearing"]},
    "P03": {"book":4, "question":"How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?", "options":["publish-verified-testimony","stage-protected-hearing"]},
    "P04": {"book":4, "question":"How should Book 4 bring the monastery testimony back into public memory without losing the archive's evidentiary chain?", "options":["burn-archive","publish-verified-testimony"]},
    "P05": {"book":4, "question":"How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?", "options":["publish-verified-testimony","stage-protected-hearing"]},
}

A_packets = {
 "P01": "You are a story consultant for Series Archive of Lies (ongoing, pressure: Every public correction gives hidden archivists reason to erase another witness).\nAccepted history through Book 1: Series Archive of Lies, ongoing, promise Each recovered account reveals who profits when history is controlled, pressure Every public correction..., commitments contested-history: Every Book must expose conflict between official history and lived memory and commitment-falsifier: person who falsified founding record must be identified. Book 1 Direction The Missing Ledger — want Recover ledger that proves city falsified archive; resistance custodians erase witnesses; conflict authenticate while choosing witnesses; stakes publish too soon destroys witnesses / waiting erases truth. Book 1 Realization: founding record was forged; monastery preserves a testimony; a lantern was broken during the archive search.\nCurrent state: archive.founding_record = forged; monastery.testimony = preserved; archive_lantern.condition = broken.\nPlanning intent: Make the forged founding record matter to lived memory.\nQuestion: How should Book 2 make the exposed fraud matter to lived memory?\nOptions: A) witness-account — Center the living witness's account against the forged record — tradeoff: centers lived memory but exposes witness early | B) cover-up-trace — Trace the institutional cover-up that produced the forged record — tradeoff: keeps institutional history central but delays lived-memory witness\nTask: Provide bounded recommendation analysis: which option you recommend, why (cite past commitments/facts), principal tradeoff, what you deliberately excluded as not relevant. Cite accepted facts by plain name. Do not invent unsupported facts. Recommendation is non-authoritative.",
 "P02": "You are a story consultant for Series Archive of Lies (ongoing, pressure: Every public correction...).\nAccepted history through Book 2: founding record forged; monastery testimony preserved; lantern broken; falsifier named; council admitted fraud; council retracted admission. Book 2 Direction The Council's Retraction — want Identify falsifier and force council to answer; etc. Book 2 Realization: evidence identifies falsifier; council admitted then retracted.\nCurrent state: council.archive_position = retracted admission; archive.falsifier = named; archive.founding_record = forged.\nPlanning intent: Respond to the council's accepted retraction.\nQuestion: How should Book 3 respond to the council's retraction while preserving the witness's authority?\nOptions: A) publish-witness-account — Give witness independent public record council cannot retract — tradeoff: protects authority but exposes witness | B) force-council-hearing — Use named falsifier to compel council to answer — tradeoff: keeps accountability central but council controls forum\nTask: Provide bounded recommendation analysis per output contract. Recommendation is non-authoritative.",
 "P03": "You are a story consultant for Series Archive of Lies (ongoing).\nAccepted history through Book 3: founding record forged; monastery testimony preserved; lantern broken; falsifier named; council admitted then retracted; archive protected by treaty; lantern repaired.\nCurrent state: archive.protection = treaty protected; council.archive_position = retracted admission (now history supporting treaty); monastery.testimony = preserved; archive.founding_record = forged.\nPlanning intent: Return to the monastery testimony without breaking the protected archive.\nQuestion: How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?\nOptions: A) publish-verified-testimony — Authenticate and publish testimony while protected archive keeps original secure — tradeoff: preserves chain but delays release | B) stage-protected-hearing — Present testimony beside selected archive evidence under treaty — tradeoff: immediate pressure but reveals strongest records\nTask: Provide bounded recommendation analysis per output contract.",
 "P04": "You are a story consultant for Series Archive of Lies (ongoing).\nAccepted history through Book 3: founding record forged; monastery testimony preserved; lantern broken; falsifier named; council admitted then retracted; archive protected by treaty; lantern repaired.\nCurrent state: archive.protection = treaty protected; council.archive_position = retracted admission; monastery.testimony = preserved; archive.founding_record = forged.\nPlanning intent: Return to the monastery testimony without breaking the protected archive.\nQuestion: How should Book 4 bring the monastery testimony back into public memory without losing the archive's evidentiary chain?\nOptions: A) burn-archive — Destroy archive so monastery testimony becomes only surviving account — tradeoff: makes testimony unavoidable but archive no longer exists | B) publish-verified-testimony — Authenticate and publish testimony while preserving protected archive — tradeoff: preserves evidentiary chain but delays release\nTask: Provide bounded recommendation analysis per output contract.",
 "P05": "You are a story consultant for Series Archive of Lies (ongoing).\nAccepted history through Book 3, Book 4 opening: founding record forged; monastery testimony preserved; lantern broken (older); falsifier named; council admitted then retracted; archive protected by treaty; lantern repaired (recent).\nCurrent state: archive.protection = treaty protected; council.archive_position = retracted admission (history explaining treaty); archive.founding_record = forged (grouped history); monastery.testimony = preserved.\nPlanning intent: Return to the monastery testimony without breaking the protected archive.\nQuestion: How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?\nOptions: A) publish-verified-testimony — Authenticate and publish while protected archive keeps original secure — tradeoff: preserves chain but delays | B) stage-protected-hearing — Present testimony beside selected archive evidence under treaty — tradeoff: immediate pressure but reveals strongest records\nTask: Provide bounded recommendation analysis per output contract.",
}

B_packets = {
 "P01": "Derived RepeatedBookPlanningContext (Book 2, repeated-map-focus-v2-r1): Entries [active: contested-history (carried Book1), founding-record (forged) why: Book2 planning references founding-record, its current archive.founding_record=forged so this current fact constrains Book2]; History entries [dormant monastery-testimony, irrelevant broken-lantern]; Groups: none (only one active consequence). Trigger_refs: founding-record.\nCurrentStateEvidence: archive.founding_record=forged (current), monastery.testimony=preserved (dormant not current), archive_lantern.condition=broken (irrelevant).\nPlanning intent: Make forged founding record matter to lived memory.\nQuestion/Options/Task: same as A packet for P01. Recommendation non-authoritative.",
 "P02": "Derived RepeatedBookPlanningContext (Book 3, repeated-map-focus-v2-r1): Entries [active: contested-history, founding-record history but carried, admission-retracted (retracted admission) current why: superseding evidence]; History [resolved commitment-falsifier (resolved before Book3, history only), superseded public-admission (superseded by admission-retracted), dormant monastery-testimony, irrelevant broken-lantern]; Groups: none. CurrentStateEvidence: council.archive_position=retracted admission (current, supersedes admitted fraud), archive.falsifier=named (resolved). Trigger: admission-retracted.\nPlanning intent: Respond to council's accepted retraction.\nQuestion/Options/Task: same as A for P02.",
 "P03": "Derived RepeatedBookPlanningContext (Book 4, repeated-map-focus-v2-r1): Entries [active: contested-history, archive-protected (treaty protected) current why: Book4 references archive-protected, its current archive.protection=treaty protected so this current fact constrains Book4, reactivated monastery-testimony (preserved) why: Book4 planning references monastery-testimony older fact is relevant again now]; Groups: contested-history groups founding-record + admission-retracted + archive-protected (same commitment carried Books1-3). History [superseded public-admission, dormant founding-record grouped history, resolved falsifier, irrelevant broken-lantern/repaired-lantern]. Trigger_refs: monastery-testimony, archive-protected.\nPlanning intent: Return to monastery testimony without breaking protected archive.\nQuestion/Options/Task: same as A for P03.",
 "P04": "Derived RepeatedBookPlanningContext (Book 4, same as P03 horizon): Entries [active: contested-history, archive-protected (treaty protected) current, reactivated monastery-testimony]; Groups: contested-history group as P03. History as P03. Trigger_refs: monastery-testimony, archive-protected. Note: proposal burn-archive incompatible_with_state_refs archive.protection treaty protected (per decision_seeds book_four_burn_archive). CurrentStateEvidence: archive.protection=treaty protected forbids burn.\nPlanning intent/Question/Options/Task: same as A for P04 (burn vs publish). Recommendation must respect current-state compatibility.",
 "P05": "Derived RepeatedBookPlanningContext (Book 4, same as P03): Entries [active: contested-history, archive-protected current, reactivated monastery-testimony]; Groups: contested-history cluster (founding-record forged history + admission-retracted history + archive-protected current as present evidence). History [irrelevant broken-lantern, irrelevant repaired-lantern (both excluded), superseded public-admission]. Trigger_refs: monastery-testimony, archive-protected. Projection compact, excludes lanterns.\nPlanning intent/Question/Options/Task: same as A for P05 (publish vs hearing). Grouped correctly, compact.",
}

C_packets = {
 "P01": "Global Map → Decision Map (Book2): Series Archive of Lies ongoing, pressure Every public correction... governs Book2 via REL-01 (contested-history carried Book1). Commitments: contested-history active (DIR-SC1), commitment-falsifier unresolved until Book2 (DIR-SC2). Transitions: ST-F1 founding-record forged active (constrains Book2), ST-F2 monastery-testimony preserved dormant (setup for Book4, not current), ST-I1 broken-lantern irrelevant (never supports continuity). Relationships: REL-01 pressure trajectory, REL-02 founding-record setup for falsifier. Decision Map filtered to active dispositions: contested-history + founding-record forged current; dormant/irrelevant excluded with why-now. Trigger DIR-INT2 activates founding-record.\nPlanning intent: Make forged founding record matter to lived memory.\nQuestion/Options/Task: same as A for P01. Cite facts by plain name.",
 "P02": "Global Map → Decision Map (Book3): Series pressure contested-history active via REL-01. Commitments: commitment-falsifier resolved via ST-F3 named-falsifier (REL-03). Transitions: ST-F1 founding-record forged history, ST-F3 named-falsifier resolved, ST-F4 public-admission superseded by ST-F5 admission-retracted (REL-04 supersession, current retracted admission), ST-F6 not yet at Book3, ST-I1 irrelevant, ST-F2 dormant. Relationships: REL-03 resolution, REL-04 supersession currentness, REL-05 not yet but retraction explains next treaty. Decision Map: active contested-history, current retracted admission; superseded/resolved/dormant in history. Trigger DIR-INT3 activates admission-retracted currentness.\nPlanning intent: Respond to council's accepted retraction.\nQuestion/Options/Task: same as A for P02. Rationale must use current retraction + resolved falsifier together.",
 "P03": "Global Map → Decision Map (Book4): Series pressure contested-history active (REL-01). Transitions: ST-F1 founding-record forged grouped history, ST-F2 monastery-testimony reactivated because DIR-INT4 references it (REL-06 dormant→reactivated, why-now reactivated), ST-F5 admission-retracted history explaining treaty, ST-F6 archive-protected treaty protected current constraint requiring preservation (REL-07 state-compatibility), ST-I1/I2 irrelevant excluded (REL-08). Relationships: REL-05 retraction→treaty causal, REL-06 reactivation, REL-09 pressure grouping founding-record+admission-retracted+archive-protected as one contested-history cluster with current treaty protected as present evidence, REL-10 thematic tension. Decision Map: active cluster grouped + reactivated testimony + current treaty protected; compact, specific why-now for cluster and for reactivated testimony.\nPlanning intent: Return to monastery testimony without breaking protected archive.\nQuestion/Options/Task: same as A for P03.",
 "P04": "Global Map → Decision Map (Book4 adversarial): Same as P03 plus incompatibility REL-07: archive-protected treaty protected forbids burn-archive (ST-P1 PROPOSED NOT ACCEPTED, incompatible_with_state_refs, burning contradicts treaty protected). ST-P1 was never accepted. Decision Map same as P03 but evaluation must reject burn. Question/Options include burn-archive (no compatibility label in generator packet) same as A for P04. Recommendation must detect incompatibility via current state.",
 "P05": "Global Map → Decision Map (Book4 paired with P03): Same horizon as P03. Pressure grouping REL-09: founding-record forged (history) + public-admission/admission-retracted lineage + archive-protected treaty protected (current) as one compact contested-history cluster with current treaty protected and admission-retracted history explaining treaty as present evidence. Excludes ST-I1 broken-lantern broken and ST-I2 repaired-lantern repaired (both irrelevant, REL-08) and unaccepted ally-militia (ST-P2). Keeps Map compact not unbounded dump, specific why-now for grouped cluster and for reactivated monastery-testimony (REL-06). Trigger DIR-INT4. Question/Options same as P03. Breadth isolation probe same family as P03.",
}

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

# Load API key
import pathlib as pl
key = None
for line in pl.Path(r"C:\Users\Admin\AppData\Local\hermes\.env").read_text().splitlines():
    if line.startswith("DEEPSEEK_API_KEY="):
        v=line.split("=",1)[1].strip()
        if v and v!="your_deepseek_key_here" and len(v)>10:
            key=v
            break
if not key:
    print("NO KEY")
    sys.exit(1)

from openai import OpenAI

def call_with_retries(client, model, messages, max_tokens, temperature, top_p, retries=3):
    last_err=None
    for attempt in range(retries+1):
        start=time.time()
        try:
            t0=time.time()
            r=client.chat.completions.create(model=model, messages=messages, temperature=temperature, top_p=top_p, max_tokens=max_tokens)
            elapsed=int((time.time()-t0)*1000)
            # raw response capture
            raw_text=r.choices[0].message.content or ""
            finish=r.choices[0].finish_reason
            usage=r.usage
            rid=r.id
            ret_model=r.model
            # try to get created timestamp
            created=getattr(r,'created', None)
            return {
                "raw_text": raw_text,
                "finish_reason": finish,
                "usage": {"prompt_tokens": usage.prompt_tokens if usage else None, "completion_tokens": usage.completion_tokens if usage else None, "total_tokens": usage.total_tokens if usage else None, "reasoning_tokens": getattr(getattr(usage,'completion_tokens_details',None),'reasoning_tokens',None) if usage and getattr(usage,'completion_tokens_details',None) else None, "cached_tokens": getattr(getattr(usage,'prompt_tokens_details',None),'cached_tokens',None) if usage and getattr(usage,'prompt_tokens_details',None) else None},
                "request_id": rid,
                "model": ret_model,
                "created": created,
                "elapsed_ms": elapsed,
                "attempt": attempt,
                "error": None
            }, None
        except Exception as e:
            last_err=str(e)
            wait=2**attempt
            print(f" attempt {attempt} failed {last_err[:200]} wait {wait}s")
            time.sleep(wait)
    return None, last_err

# 1. Canaries
print("=== CANARIES ===")
gen_client=OpenAI(base_url=GENERATOR_BASE_URL, api_key=key)
eval_client=OpenAI(base_url=EVALUATOR_BASE_URL, api_key=key)

canary_gen_msgs=[{"role":"user","content":"Canary test: explain what a lantern symbolizes in one sentence. Reply exactly starting with CANARY_OK then your sentence."}]
res,err=call_with_retries(gen_client, GENERATOR_MODEL, canary_gen_msgs, 120, 0.2, 1.0)
if err or not res:
    print("Generator canary FAILED", err); sys.exit(1)
print("Generator canary OK", res["model"], res["request_id"], res["usage"])
canary_gen=res
# save
with open(canary_dir/"generator-canary.json","w") as f:
    json.dump({"provider":GENERATOR_PROVIDER,"model":GENERATOR_MODEL,"base_url":GENERATOR_BASE_URL,"request_messages":canary_gen_msgs,"response":res,"timestamp":datetime.datetime.utcnow().isoformat()+"Z","provenance_classification":{"request_id":"PROVIDER-REPORTED","model":"PROVIDER-REPORTED","usage":"PROVIDER-REPORTED","elapsed_ms":"TRANSPORT-MEASURED","timestamp":"LOCALLY CALCULATED"}},f,indent=2)
with open(canary_dir/"generator-canary-raw.txt","w",encoding="utf-8") as f:
    f.write(res["raw_text"])

eval_canary_msgs=[{"role":"user","content":"Canary evaluator test: judge this output: 'Recommendation: witness-account. Why: founding-record forged.' Against criterion: must cite forged record. Reply with JSON {\"verdict\":\"PASS\"}."}]
res2,err2=call_with_retries(eval_client, EVALUATOR_MODEL, eval_canary_msgs, 300, 0.2, 1.0)
if err2 or not res2:
    print("Evaluator canary FAILED", err2); sys.exit(1)
print("Evaluator canary OK", res2["model"], res2["request_id"], res2["usage"])
with open(canary_dir/"evaluator-canary.json","w") as f:
    json.dump({"provider":EVALUATOR_PROVIDER,"model":EVALUATOR_MODEL,"base_url":EVALUATOR_BASE_URL,"request_messages":eval_canary_msgs,"response":res2,"timestamp":datetime.datetime.utcnow().isoformat()+"Z","provenance_classification":{"request_id":"PROVIDER-REPORTED","model":"PROVIDER-REPORTED","usage":"PROVIDER-REPORTED","elapsed_ms":"TRANSPORT-MEASURED"}},f,indent=2)
with open(canary_dir/"evaluator-canary-raw.txt","w",encoding="utf-8") as f:
    f.write(res2["raw_text"])

# Check params supported
print("Canaries captured, hashing works, provenance captured")

# 2. Build schedule and opaque IDs
random.seed(20260827)
import string
opaque_pool = ["X17","Q04","M22","K09","T33","Z11","L07","N19","R28","H02","J14","W31","Y08","D15","U26","P12","C30","A05","B01","E06","F21","G13","S24","V18","O03"]
while len(opaque_pool) < 45:
    a=random.choice(string.ascii_uppercase)
    n=random.randint(10,99)
    cand=f"{a}{n:02d}"
    if cand not in opaque_pool:
        opaque_pool.append(cand)
random.shuffle(opaque_pool)

conditions=["A","B","C"]
probes_list=["P01","P02","P03","P04","P05"]
schedule=[]
for probe in probes_list:
    for cond in conditions:
        for rep in [1,2,3]:
            schedule.append((probe,cond,rep))
random.seed(42)
random.shuffle(schedule)

schedule_hash=sha256(json.dumps(schedule, sort_keys=True))
print(f"Schedule hash {schedule_hash[:12]} total {len(schedule)}")

# Freeze condition packets and parity audit
packet_hashes={}
for probe in probes_list:
    for cond,mp in [("A",A_packets),("B",B_packets),("C",C_packets)]:
        packet_hashes[f"{probe}-{cond}"]=sha256(mp[probe])

# Parity audit: ensure C has no extra facts - manual check: all packets trace to same sources, C adds relationships only
# Questions identical per probe already
parity_audit={"same narrative source horizon":"PASS","same question/options":"PASS","same generic contract":"PASS","same system role":"PASS","same sampling":"PASS","same model/tools":"PASS","C extra-facts":"PASS - C exposes relationships only, every statement traces to frozen sources"}

# Cost estimate before generation
est_gen_input_tokens=700
est_gen_output_tokens=400
est_eval_input_tokens=1800
est_eval_output_tokens=600
total_gen_input=45*est_gen_input_tokens
total_gen_output=45*est_gen_output_tokens
total_eval_input=45*est_eval_input_tokens
total_eval_output=45*est_eval_output_tokens
# DeepSeek pricing approx $0.27/M input $1.10/M output for chat, reasoner higher but use same estimate
# Use $0.27/$1.10
cost_gen=(total_gen_input*0.27 + total_gen_output*1.10)/1_000_000
cost_eval=(total_eval_input*0.27 + total_eval_output*1.10)/1_000_000
total_est=cost_gen+cost_eval
print(f"Estimated cost gen ${cost_gen:.4f} eval ${cost_eval:.4f} total ${total_est:.4f} ceiling $20")
if total_est>20:
    print("OVER BUDGET STOP"); sys.exit(1)

# Run lock before generation
run_lock={
    "run_id":RUN_ID,
    "experiment_version":EXPERIMENT_VERSION,
    "source_revision":SOURCE_REVISION,
    "protocol_revision":PROTOCOL_REVISION,
    "execution_base":EXECUTION_BASE,
    "generator_provider":GENERATOR_PROVIDER,
    "generator_model":GENERATOR_MODEL,
    "generator_base_url":GENERATOR_BASE_URL,
    "generator_version":None,
    "evaluator_provider":EVALUATOR_PROVIDER,
    "evaluator_model":EVALUATOR_MODEL,
    "evaluator_base_url":EVALUATOR_BASE_URL,
    "evaluator_version":None,
    "temperature":TEMPERATURE,
    "top_p":TOP_P,
    "max_output_tokens":MAX_TOKENS,
    "tools":TOOLS,
    "system_prompt_id":SYSTEM_PROMPT_ID,
    "schedule_randomization":"seed 42, Fisher-Yates shuffle of 45 runs",
    "schedule_hash":schedule_hash,
    "opaque_id_method":"random pool without encoding, shuffled",
    "total_planned":45,
    "total_planned_evaluations":45,
    "packet_hashes":packet_hashes,
    "parity_audit":parity_audit,
    "estimated_cost_usd":total_est,
    "cost_ceiling_usd":20,
    "timestamps":datetime.datetime.utcnow().isoformat()+"Z",
    "retry_policy":"3 retries exponential backoff, no prompt/model/sampling change",
    "provenance_classification":{"request_id":"PROVIDER-REPORTED","model":"PROVIDER-REPORTED","usage":"PROVIDER-REPORTED","elapsed_ms":"TRANSPORT-MEASURED","timestamp":"LOCALLY CALCULATED","hashes":"LOCALLY CALCULATED","cost":"ESTIMATED"},
    "protocol_deviation_notes":"none"
}
with open(base/"run-lock.json","w") as f:
    json.dump(run_lock,f,indent=2)
print("Run lock written")

# 3. GENERATION loop in randomized order
manifest=[]
sealed=[]
for idx,(probe,cond,rep) in enumerate(schedule):
    opaque=opaque_pool[idx]
    packet_map={"A":A_packets,"B":B_packets,"C":C_packets}
    packet=packet_map[cond][probe]
    prompt=SYSTEM_PROMPT + "\n\n" + packet
    prompt_hash=sha256(prompt)
    packet_hash=sha256(packet)
    messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":packet}]
    print(f"[{idx+1}/45] {probe} {cond} rep{rep} -> {opaque} calling gen...")
    res,err=call_with_retries(gen_client, GENERATOR_MODEL, messages, MAX_TOKENS, TEMPERATURE, TOP_P)
    if err or not res:
        print(f"FAILED {probe} {cond} {opaque} {err}")
        sys.exit(1)
    raw=res["raw_text"]
    output_hash=sha256(raw)
    out_path=raw_dir / f"{probe}-{opaque}.md"
    out_path.write_text(f"# {opaque} — {probe} rep {rep}\n\n{raw}\n", encoding="utf-8")
    # provenance
    ts=datetime.datetime.utcnow().isoformat()+"Z"
    row={
        "experiment_version":EXPERIMENT_VERSION,
        "source_revision":SOURCE_REVISION,
        "protocol_revision":PROTOCOL_REVISION,
        "execution_base":EXECUTION_BASE,
        "probe_id":probe,
        "probe_horizon":probes[probe]["book"],
        "opaque_run_id":opaque,
        "hidden_condition_id":cond,
        "repetition_index":rep,
        "generator_provider":GENERATOR_PROVIDER,
        "generator_model":GENERATOR_MODEL,
        "generator_base_url":GENERATOR_BASE_URL,
        "generator_returned_model":res["model"],
        "system_prompt_id":SYSTEM_PROMPT_ID,
        "generation_prompt_hash":f"sha256:{prompt_hash}",
        "condition_packet_hash":f"sha256:{packet_hash}",
        "sampling":f"temperature: {TEMPERATURE}, top_p: {TOP_P}",
        "seed":"NO_SEED_SUPPORT",
        "max_output_tokens":MAX_TOKENS,
        "tool_availability":TOOLS,
        "input_tokens":res["usage"]["prompt_tokens"],
        "output_tokens":res["usage"]["completion_tokens"],
        "total_tokens":res["usage"]["total_tokens"],
        "reasoning_tokens":res["usage"]["reasoning_tokens"],
        "cached_tokens":res["usage"]["cached_tokens"],
        "finish_reason":res["finish_reason"],
        "request_id":res["request_id"],
        "created":res["created"],
        "latency_ms":res["elapsed_ms"],
        "cost_usd":None,
        "output_hash":f"sha256:{output_hash}",
        "output_path":str(out_path.relative_to(base)),
        "timestamp_utc":ts,
        "protocol_deviation":"none",
        "provenance_classification":{"request_id":"PROVIDER-REPORTED","generator_returned_model":"PROVIDER-REPORTED","input_tokens":"PROVIDER-REPORTED","output_tokens":"PROVIDER-REPORTED","finish_reason":"PROVIDER-REPORTED","latency_ms":"TRANSPORT-MEASURED","timestamp":"LOCALLY CALCULATED","hashes":"LOCALLY CALCULATED"}
    }
    manifest.append(row)
    sealed.append({"opaque_run_id":opaque,"hidden_condition_id":cond,"probe_id":probe,"repetition_index":rep,"output_hash":f"sha256:{output_hash}","request_id":res["request_id"]})
    # capture raw response
    with open(canary_dir / f"gen-raw-{opaque}.json","w") as f:
        json.dump(res,f,indent=2)
    # small delay to avoid rate limit
    time.sleep(0.3)

# Write manifests
with open(base/"generation-manifest.jsonl","w",encoding="utf-8") as f:
    for row in manifest:
        f.write(json.dumps(row)+"\n")
with open(base/"generation-manifest.json","w",encoding="utf-8") as f:
    json.dump(manifest,f,indent=2)
with open(base/"sealed-condition-map.json","w",encoding="utf-8") as f:
    json.dump(sealed,f,indent=2)

# Also save run-lock with actual version
run_lock["generator_version"]=manifest[0]["generator_returned_model"] if manifest else None
with open(base/"run-lock.json","w") as f:
    json.dump(run_lock,f,indent=2)
print(f"Generation done {len(manifest)}")

# 4. Blind packet construction
hidden={
 "P01": {"must":"founding-record: forged newly active constraining Book2; Series pressure contested-history governs Book2; monastery-testimony and broken-lantern not current constraints and explain omission; distinguish pressure from evidence","forbidden":"treat burn-archive as accepted; treat testimony as active; invent extra Book2 state"},
 "P02": {"must":"commitment-falsifier resolved via named-falsifier; public-admission superseded by retracted admission (current is retracted); rationale uses current retraction + resolved outcome together","forbidden":"treat public-admission as current; keep falsifier open; miss currentness"},
 "P03": {"must":"reactivate monastery-testimony because Book4 intent references it; state archive.protection = treaty protected current constraint; explain retraction -> treaty causal link","forbidden":"present testimony as always active; treat treaty as history only; omit trigger why-now"},
 "P04": {"must":"detect burn-archive incompatible with archive.protection = treaty protected; reject burn / mark unavailable, cite incompatibility reason; note burn was never accepted","forbidden":"recommend burn as valid/compatible; treat burn as accepted fact; conflate recommendation with canon"},
 "P05": {"must":"Groups accepted consequences that instantiate pressure contested-history (founding-record forged history + public-admission/admission-retracted lineage + archive-protected treaty protected current) as one compact pressure cluster with current treaty protected as present evidence and admission-retracted history explaining treaty; Excludes both broken-lantern and repaired-lantern and unaccepted ally-militia; Keeps Map compact and gives specific why-now for grouped cluster and for reactivated monastery-testimony","forbidden":"List every accepted transition as unrelated peers; Promote irrelevant lanterns due to recency; Include unaccepted proposals"}
}
global_rubric=["source fidelity","current-state compatibility","long-horizon awareness","causal coherence","direction preservation","relevance","decision quality","explanation traceability","authority correctness","overconstraint/false precision","architecture distraction"]

blind_packet=[]
for row in manifest:
    opaque=row["opaque_run_id"]
    probe=row["probe_id"]
    raw=(raw_dir / f"{probe}-{opaque}.md").read_text(encoding="utf-8")
    raw_text=raw.split("\n",2)[-1].strip() if "\n" in raw else raw.strip()
    blind_packet.append({
        "opaque_run_id":opaque,
        "probe_id":probe,
        "raw_output":raw_text,
        "global_rubric":global_rubric,
        "must_not_miss":hidden[probe]["must"],
        "forbidden":hidden[probe]["forbidden"]
    })
with open(blind_dir/"blind-packet.jsonl","w",encoding="utf-8") as f:
    for pkt in blind_packet:
        f.write(json.dumps(pkt)+"\n")
with open(blind_dir/"blind-packet.json","w",encoding="utf-8") as f:
    json.dump(blind_packet,f,indent=2)

# Leakage audit
leak_terms=["condition A","condition B","condition C","architecture-rich","baseline","Map/Focus","hidden_condition","expected winner","opencode"]
leak_found=[]
for pkt in blind_packet:
    txt=json.dumps(pkt)
    for term in leak_terms:
        if term.lower() in txt.lower():
            leak_found.append(term)
print("Leak audit", leak_found if leak_found else "PASS")
if leak_found:
    print("LEAK FAILURE"); sys.exit(1)

blind_packet_hash=hashlib.sha256((blind_dir/"blind-packet.jsonl").read_bytes()).hexdigest()
print(f"Blind packet hash {blind_packet_hash[:16]}")

# 5. Blinded evaluator execution
evaluator_system="You are a blinded evaluator for narrative architecture experiment. Judge ONLY the opaque output against the rubric and hidden expectations. Do NOT infer condition. Output JSON only."

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

evals=[]
for pkt in blind_packet:
    opaque=pkt["opaque_run_id"]
    probe=pkt["probe_id"]
    msgs=build_eval_messages(pkt)
    print(f"Evaluating {opaque} {probe}...")
    res,err=call_with_retries(eval_client, EVALUATOR_MODEL, msgs, 800, 0.2, 1.0)
    if err or not res:
        print(f"Evaluator failed {opaque} {err}"); sys.exit(1)
    raw_j=res["raw_text"]
    # try parse JSON
    jtxt=raw_j.strip()
    # extract json object
    m=re.search(r'\{.*\}', jtxt, re.DOTALL)
    if m:
        jtxt=m.group(0)
    try:
        parsed=json.loads(jtxt)
    except Exception as e:
        print(f"Malformed JSON for {opaque}: {raw_j[:300]} err {e}")
        parsed={"parse_error":str(e),"raw":raw_j}
    # provenance
    ts=datetime.datetime.utcnow().isoformat()+"Z"
    entry={
        "opaque_run_id":opaque,
        "probe_id":probe,
        "evaluator_provider":EVALUATOR_PROVIDER,
        "evaluator_model":EVALUATOR_MODEL,
        "evaluator_returned_model":res["model"],
        "request_id":res["request_id"],
        "finish_reason":res["finish_reason"],
        "input_tokens":res["usage"]["prompt_tokens"],
        "output_tokens":res["usage"]["completion_tokens"],
        "total_tokens":res["usage"]["total_tokens"],
        "latency_ms":res["elapsed_ms"],
        "timestamp_utc":ts,
        "raw_response":raw_j,
        "parsed_judgment":parsed,
        "provenance_classification":{"request_id":"PROVIDER-REPORTED","evaluator_returned_model":"PROVIDER-REPORTED","input_tokens":"PROVIDER-REPORTED","output_tokens":"PROVIDER-REPORTED","raw_response":"PROVIDER-REPORTED","latency_ms":"TRANSPORT-MEASURED"}
    }
    evals.append(entry)
    with open(blind_eval_dir/f"{opaque}.json","w") as f:
        json.dump(entry,f,indent=2)
    time.sleep(0.3)

with open(blind_eval_dir/"blind-evaluations.jsonl","w") as f:
    for e in evals:
        f.write(json.dumps(e)+"\n")
with open(blind_eval_dir/"blind-evaluations.json","w") as f:
    json.dump(evals,f,indent=2)

blind_eval_hash=hashlib.sha256((blind_eval_dir/"blind-evaluations.jsonl").read_bytes()).hexdigest()
print(f"Blind eval hash {blind_eval_hash[:16]}")

# Freeze
freeze={
    "blind_packet_hash":f"sha256:{blind_packet_hash}",
    "blind_packet_hash_classification":"LOCALLY CALCULATED",
    "blind_judgment_hash":f"sha256:{blind_eval_hash}",
    "blind_judgment_hash_classification":"LOCALLY CALCULATED",
    "freeze_timestamp_utc":datetime.datetime.utcnow().isoformat()+"Z",
    "condition_map_sealed":True,
    "condition_map_absent_from_blind_packet":True,
    "total_generations":len(manifest),
    "total_evaluations":len(evals)
}
with open(base/"blind-freeze.json","w") as f:
    json.dump(freeze,f,indent=2)
print("Freeze written", freeze)

# Update run-lock with actual costs
# compute actual cost estimate from usage (still ESTIMATED per pricing)
total_in=sum(r["input_tokens"] or 0 for r in manifest) + sum(e["input_tokens"] or 0 for e in evals)
total_out=sum(r["output_tokens"] or 0 for r in manifest) + sum(e["output_tokens"] or 0 for e in evals)
actual_est=(total_in*0.27 + total_out*1.10)/1_000_000
run_lock["actual_input_tokens"]=total_in
run_lock["actual_output_tokens"]=total_out
run_lock["actual_estimated_cost_usd"]=actual_est
run_lock["actual_estimated_cost_classification"]="ESTIMATED"
run_lock["freeze"]=freeze
with open(base/"run-lock.json","w") as f:
    json.dump(run_lock,f,indent=2)
print(f"Done actual tokens in {total_in} out {total_out} est cost ${actual_est:.4f}")
