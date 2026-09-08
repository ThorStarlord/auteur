import json, pathlib, collections
base=pathlib.Path('docs/research/global-map-architecture-value-v2/runs/20260827-deepseek-v2-empirical')
manifest=json.loads((base/'generation-manifest.json').read_text(encoding='utf-8'))
sealed=json.loads((base/'sealed-condition-map.json').read_text(encoding='utf-8'))
evals=json.loads((base/'blind-evaluation/blind-evaluations.json').read_text(encoding='utf-8'))
cond_map={s['opaque_run_id']:s['hidden_condition_id'] for s in sealed}
for e in evals:
    e['condition']=cond_map[e['opaque_run_id']]
for probe in ['P01','P02','P03','P04','P05']:
    print(f"== {probe}")
    for cond in ['A','B','C']:
        subset=[e for e in evals if e['probe_id']==probe and e['condition']==cond]
        from collections import Counter
        c=Counter(e['parsed_judgment']['overall'] for e in subset)
        m=Counter(e['parsed_judgment']['must_not_miss_coverage'] for e in subset)
        sev=sum(1 for e in subset if e['parsed_judgment']['severe_negative'])
        print(f" {cond}: overall {dict(c)} must {dict(m)} severe {sev}")
        for e in subset:
            pj=e['parsed_judgment']
            rat=pj.get('rationale','')
            print(f"  {e['opaque_run_id']} overall={pj['overall']} must={pj['must_not_miss_coverage']} forb={pj['forbidden_assumption_violations']} sev={pj['severe_negative']}")
            print(f"    rationale: {rat[:120]}")
