"""Build blind evaluation packets: opaque output + global rubric + per-probe
hidden must-not-miss/forbidden. NO condition identity, NO hidden mapping,
NO expected winner. Probe ID is shared (required by protocol; does not
reveal condition)."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).parent
EVAL_DIR = OUT / "eval-packets"
EVAL_DIR.mkdir(exist_ok=True)

schedule = json.loads((OUT / "schedule.json").read_text())

GLOBAL_RUBRIC = """Global criteria (apply per output, from evaluation-rubric.md, byte-identical intent to V1):

1. SOURCE FIDELITY — Faithful to accepted facts; no invented unsupported conditions.
2. CURRENT-STATE COMPATIBILITY — Does not reason from superseded/contradicted state.
3. LONG-HORIZON AWARENESS — Notices consequential earlier commitments/setups/trajectories/consequences/future pressures.
4. CAUSAL COHERENCE — Respects prerequisite/consequence relationships.
5. DIRECTION / TRAJECTORY PRESERVATION — Recognizes when a locally attractive option damages established longer-range direction.
6. RELEVANCE — Identifies what actually matters to the current decision vs. flooding with unrelated continuity.
7. DECISION QUALITY — Produces a useful bounded recommendation / choice analysis.
8. EXPLANATION TRACEABILITY — Can explain WHY a past element matters now (why-now trace).
9. AUTHORITY CORRECTNESS — Preserves recommendation vs. accepted fact vs. author decision; does not claim the recommendation creates canon.
10. OVERCONSTRAINT / FALSE PRECISION — Does not treat provisional/interpretive material as rigid law.
11. ARCHITECTURE DISTRACTION — Does not distort the answer with irrelevant architecture/detail.

Judgment rule: Do not require one predetermined artistic taste among defensible options. Judge whether the reasoning noticed consequential constraints/opportunities, not whether it matches a specific option. Only P04 has a probe where one option (burn-archive) must be rejected on state-compatibility grounds; for all other probes either option can be defensible if reasoning respects must-not-miss and avoids forbidden."""

HIDDEN_BY_PROBE = {
    "P01": """P01 hidden must-not-miss (Book 2, independent decision):
- Notes founding-record (forged) is a newly active consequence constraining Book 2.
- Notes Series pressure contested-history still governs Book 2.
- Notes monastery-testimony and broken-lantern are NOT current constraints (dormant) and explains the omission.
- Distinguishes pressure from concrete evidence (grouping).

P01 forbidden:
- Treating book-2-burn-archive as an accepted/current option.
- Treating monastery-testimony as currently active (it is dormant until a later Book explicitly triggers it).
- Inventing extra Book 2 state beyond the forged record.""",
    "P02": """P02 hidden must-not-miss (Book 3, independent decision):
- Explicitly states commitment-falsifier is RESOLVED (not an active driver) due to named-falsifier.
- Explicitly states public-admission is SUPERSEDED by retracted admission, and that the current state is the retraction.
- Rationale uses the current retraction AND the resolved falsifier outcome together.

P02 forbidden:
- Treating public-admission ("admitted fraud") as the current state.
- Keeping the falsifier question as an open/unresolved driver.
- Missing currentness (e.g., citing only the named falsifier and ignoring the retraction).""",
    "P03": """P03 hidden must-not-miss (Book 4, independent decision, paired with P05):
- Reactivates monastery-testimony BECAUSE the Book 4 planning intent explicitly references it.
- States archive.protection = treaty protected is a current constraint requiring preservation.
- Explains the causal link: retraction → treaty (the treaty exists because the retraction made the evidence vulnerable).

P03 forbidden:
- Presenting the testimony as always active (ignoring its dormancy until the Book 4 trigger).
- Treating the treaty as history only (it is current).
- Omitting why the testimony matters NOW (the trigger).""",
    "P04": """P04 hidden must-not-miss (Book 4, adversarial variant, same horizon as P03/P05):
- Detects that burn-archive is INCOMPATIBLE with the current state archive.protection = treaty protected.
- Rejects burn (or marks it unavailable/non-viable) and recommends the compatible alternative; cites the incompatibility (current treaty-protected state) as the reason.
- Notes/treats burn-archive as never having been an accepted fact (it is only a proposed, never-accepted alternative) — does not treat it as canon or as an equally weighted tradeoff without a state check.

P04 forbidden:
- Recommending burn-archive as valid/compatible with current state.
- Treating burn-archive as an accepted fact.
- Conflating the recommendation with canon (e.g., implying that choosing burn would itself make it canon).

This is the ONLY probe where one specific option (burn-archive) must be rejected on state-compatibility grounds for a PASS on this criterion; do not apply this severity requirement to any other probe.""",
    "P05": """P05 hidden must-not-miss (Book 4, paired projection/isolation probe, same question/options as P03 — judge grouping/compactness, not just decision quality):
- Groups founding-record (history) + public-admission (superseded) + admission-retracted (history) + archive-protected (current) as ONE compact contested-history pressure cluster, with the current treaty-protected state and the retraction history presented as supporting evidence for that cluster — rather than listing every accepted transition as unrelated peers.
- Excludes BOTH broken-lantern (older) and repaired-lantern (recent) as irrelevant, and excludes any unaccepted proposal (e.g., ally-militia, burn-archive) from the active picture.
- Keeps the map/reasoning compact (not an unbounded dump of every accepted fact, not a "most recent wins" recency window) and gives a specific why-now for the grouped cluster and for the reactivated monastery-testimony.

P05 forbidden:
- Listing every accepted transition as unrelated peers (no grouping).
- Promoting the irrelevant lantern (especially the recent repaired one) into relevance merely because it is recent (false-recency).
- Including any unaccepted proposal in the active/relevant picture.

Interpretation note: P05 shares its question/options with P03. Judge P05 specifically on compactness/grouping/irrelevance-filtering, not on which option was chosen (either publish-verified-testimony or stage-protected-hearing can be defensible if P05's must-not-miss items are met)."""
}


def render_packet(oid: str, probe_id: str, output_text: str) -> str:
    return f"""You are a blinded evaluator for a research experiment on narrative-planning reasoning quality. You do NOT know and must NOT try to infer which experimental condition (there is no "A"/"B"/"C" label available to you, and you must not guess or assume one) produced this candidate output. Judge it only on its own merits against the rubric below.

Candidate ID: {oid}
Probe: {probe_id}

{GLOBAL_RUBRIC}

{HIDDEN_BY_PROBE[probe_id]}

=== CANDIDATE OUTPUT (verbatim, unedited) ===
{output_text}
=== END CANDIDATE OUTPUT ===

Task: Produce a structured judgment as valid JSON with EXACTLY this shape (no prose outside the JSON):
{{
  "candidate_id": "{oid}",
  "probe_id": "{probe_id}",
  "criteria": {{
    "source_fidelity": "PASS|MIXED|FAIL",
    "current_state_compatibility": "PASS|MIXED|FAIL",
    "long_horizon_awareness": "PASS|MIXED|FAIL",
    "causal_coherence": "PASS|MIXED|FAIL",
    "direction_preservation": "PASS|MIXED|FAIL",
    "relevance": "PASS|MIXED|FAIL",
    "decision_quality": "PASS|MIXED|FAIL",
    "explanation_traceability": "PASS|MIXED|FAIL",
    "authority_correctness": "PASS|MIXED|FAIL",
    "overconstraint_false_precision": "PASS|MIXED|FAIL",
    "architecture_distraction": "PASS|MIXED|FAIL"
  }},
  "must_not_miss_covered": ["list the specific must-not-miss items above that this candidate actually covered, by short paraphrase"],
  "must_not_miss_missed": ["list the specific must-not-miss items above that this candidate missed"],
  "forbidden_violations": ["list any forbidden items above that this candidate violated; empty list if none"],
  "severe_negative": true or false,
  "severe_negative_reason": "string, empty if severe_negative is false",
  "overall": "PASS|MIXED|FAIL",
  "one_line_rationale": "one sentence justifying the overall verdict"
}}

Overall PASS requires: no forbidden violations, and all or nearly all must-not-miss items covered. FAIL requires: any forbidden violation, OR a severe miss of a must-not-miss item central to the probe (especially P04 burn-archive incompatibility), OR current-state-compatibility FAIL. MIXED is between these.
"""


for slot in schedule:
    oid = slot["opaque_run_id"]
    probe_id = slot["probe_id"]
    output_text = (OUT / "raw-outputs" / f"{oid}.md").read_text(encoding="utf-8")
    packet = render_packet(oid, probe_id, output_text)
    (EVAL_DIR / f"{oid}.txt").write_text(packet, encoding="utf-8")

# Leakage audit: verify no A/B/C token, no "hidden_condition", no map content leaked into any eval packet
import re
leaked = []
sealed_map_text = (OUT / "sealed-condition-map.json").read_text()
for slot in schedule:
    oid = slot["opaque_run_id"]
    text = (EVAL_DIR / f"{oid}.txt").read_text()
    for banned in ["hidden_condition", "Condition A", "Condition B", "Condition C", "condition A", "condition B", "condition C"]:
        if banned in text:
            leaked.append((oid, banned))

blind_packet_concat = "\n".join((EVAL_DIR / f"{s['opaque_run_id']}.txt").read_text() for s in schedule)
blind_packet_hash = hashlib.sha256(blind_packet_concat.encode()).hexdigest()
(OUT / "blind_packet_hash.txt").write_text(blind_packet_hash + "\n")

print("eval packets built:", len(schedule))
print("leakage audit findings:", leaked if leaked else "NONE")
print("blind packet concat hash:", blind_packet_hash)
