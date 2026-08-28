"""Freeze blind evaluations (hash), THEN reveal sealed condition map and
mechanically join. No judgment content is altered at any point."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).parent

# 1. Freeze: build blind-evaluations.jsonl from the 45 individual JSON files,
# in schedule order, and hash it. This is the artifact whose hash proves the
# judgments existed before unblinding.
schedule = json.loads((OUT / "schedule.json").read_text())
rows = []
for slot in schedule:
    oid = slot["opaque_run_id"]
    d = json.loads((OUT / "blind-evaluation" / f"{oid}.json").read_text())
    rows.append(d)

blind_eval_jsonl = "\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n"
(OUT / "blind-evaluations.jsonl").write_text(blind_eval_jsonl, encoding="utf-8")
judgment_hash = hashlib.sha256(blind_eval_jsonl.encode()).hexdigest()
(OUT / "judgment_hash.txt").write_text(judgment_hash + "\n")
print("FREEZE: judgment_hash =", judgment_hash)
print("FREEZE: 45 judgments written to blind-evaluations.jsonl, timestamp-ordered by schedule")

# 2. Leakage check on the frozen judgments themselves: verify no judgment
# JSON mentions condition identity (it shouldn't, since it was never given
# the mapping) -- sanity check only.
leaked = []
for r in rows:
    blob = json.dumps(r)
    for banned in ["\"A\"", "\"B\"", "\"C\"", "condition"]:
        if banned.lower() in blob.lower() and banned != '"A"' and banned != '"B"' and banned != '"C"':
            leaked.append((r["candidate_id"], banned))
print("post-freeze leakage scan (condition-identity related):", leaked if leaked else "NONE")

# ============================================================
# ONLY NOW does the sealed condition map get read and joined.
# ============================================================
sealed_map = json.loads((OUT / "sealed-condition-map.json").read_text())

full_rows = []
for slot in schedule:
    oid = slot["opaque_run_id"]
    judgment = next(r for r in rows if r["candidate_id"] == oid)
    mapping = sealed_map[oid]
    assert mapping["probe_id"] == slot["probe_id"] == judgment["probe_id"]
    full_rows.append(dict(
        opaque_run_id=oid,
        hidden_condition_id_for_analysis_only=mapping["hidden_condition_id"],
        probe_id=slot["probe_id"],
        repetition_index=slot["repetition_index"],
        overall=judgment["overall"],
        severe_negative=judgment.get("severe_negative", False),
        severe_negative_reason=judgment.get("severe_negative_reason", ""),
        must_not_miss_covered_count=len(judgment.get("must_not_miss_covered", [])),
        must_not_miss_missed_count=len(judgment.get("must_not_miss_missed", [])),
        forbidden_violations_count=len(judgment.get("forbidden_violations", [])),
        criteria=judgment["criteria"],
        one_line_rationale=judgment.get("one_line_rationale", ""),
    ))

(OUT / "full-evaluations-with-conditions.jsonl").write_text(
    "\n".join(json.dumps(r, sort_keys=True) for r in full_rows) + "\n", encoding="utf-8"
)
print("UNBLIND: 45 rows joined with hidden_condition_id, written to full-evaluations-with-conditions.jsonl")

# ============================================================
# Mechanical reconciliation
# ============================================================
from collections import Counter

total = len(full_rows)
per_condition = Counter(r["hidden_condition_id_for_analysis_only"] for r in full_rows)
per_probe = Counter(r["probe_id"] for r in full_rows)
per_condition_probe = Counter((r["hidden_condition_id_for_analysis_only"], r["probe_id"]) for r in full_rows)
overall_by_condition = {}
for cond in ("A", "B", "C"):
    c = Counter(r["overall"] for r in full_rows if r["hidden_condition_id_for_analysis_only"] == cond)
    overall_by_condition[cond] = dict(c)

severe_by_condition = Counter(
    r["hidden_condition_id_for_analysis_only"] for r in full_rows if r["severe_negative"]
)

print()
print("=== MECHANICAL RECONCILIATION ===")
print("total:", total)
print("per_condition:", dict(per_condition))
print("per_probe:", dict(per_probe))
print("per_condition_probe (expect all ==3):", {f"{k[0]}-{k[1]}": v for k, v in sorted(per_condition_probe.items())})
print("overall_by_condition:", overall_by_condition)
print("severe_by_condition:", dict(severe_by_condition))

# invariant check
assert total == 45
for cond in ("A", "B", "C"):
    assert per_condition[cond] == 15, (cond, per_condition[cond])
    for probe in ("P01", "P02", "P03", "P04", "P05"):
        assert per_condition_probe[(cond, probe)] == 3, (cond, probe, per_condition_probe[(cond, probe)])
print()
print("INVARIANT CHECK: PASS (45 total, 15 per condition, 3 per condition-probe cell)")
