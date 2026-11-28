"""Machine-generated summary of the claim-basis verification exercises, read from the owner records kept beside this script.

For each exercise: the verifier's judgement per claim (from the owner's stored result), the independent critic's flag per claim (transcribed
from the critic report kept in this folder, verbatim verdict words), and whether the two agree. A verifier flag is a judgement in the
misreading or unsupported family. A critic flag is any verdict other than supported, acceptable proposal, or no-flag. The disagreements
are adjudicated by hand in EVALUATION.md; this script only counts.

Run: python build_summary.py   (writes summary.json beside this file)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MISREADING = {"overreaching", "temporal_misreading", "modal_misreading", "attribution_error", "standing_confusion",
              "unsupported_relation", "contradicted"}

# Critic flags transcribed from the reports in this folder (critics-v2 for A, B and C; exercise-F critic for the follow-up).
CRITIC = {
    "A3": {"flagged": {"s1", "s2", "s3", "s5", "r1", "r3", "r4", "r5", "a2", "o1", "o2"},
           "clean": {"s4", "r2", "a1", "a3"}, "source": "critics-v2/grounding-critic-exercise-A.md"},
    "B3": {"flagged": {"s1", "s2", "s3", "s4", "r4", "a2", "a3", "o1"},
           "clean": {"r1", "r2", "r3", "a1", "o2", "o3"}, "source": "critics-v2/grounding-critic-exercises-B-and-C.md"},
    "C3": {"flagged": {"s1", "r1", "r2", "r4", "r6", "e1", "e2", "e3", "o2"},
           "clean": {"s2", "s3", "s4", "r3", "r5", "a1", "a2", "a3", "o1", "o3", "n1", "n2", "n3"},
           "source": "critics-v2/grounding-critic-exercises-B-and-C.md"},
    "F3v": {"flagged": {"s2", "r2", "a2"},
            "clean": {"s1", "s3", "s4", "s5", "r1", "r3", "a1", "a3", "o1", "o2", "o3"},
            "source": "exercise-F-followup/critic/critic-F3.md"},
}

# Where each exercise's verifier records live (owner results), relative to this folder.
VERIFIER_RECORDS = {
    "A3": "exercise-A-verification/owner",
    "B3": "exercise-B-verification/owner",
    "C3": "exercise-C-verification/owner",
    "F3v": "exercise-F-followup/second-verification/owner",
}


def load_verdicts(folder: Path) -> dict[str, dict]:
    verdicts = {}
    for path in sorted(folder.glob("verification-*-result.json")):
        claim = path.name.split("-")[1]
        verdicts[claim] = json.loads(path.read_text(encoding="utf-8"))["result"]
    return verdicts


def main() -> None:
    summary = {"schema": "claim-basis-verification-summary/1", "exercises": {}}
    for exercise, folder in VERIFIER_RECORDS.items():
        verdicts = load_verdicts(HERE / folder)
        if exercise == "C3":
            # The first C s1 judgement was refused on the length limit; its corrected judgement is in its own record.
            corrected = HERE / "exercise-C-verification" / "s1-corrected-instruction" / "owner" / "verification-s1-result.json"
            verdicts["s1"] = json.loads(corrected.read_text(encoding="utf-8"))["result"]
        rows = []
        for claim, verdict in sorted(verdicts.items(), key=lambda item: (item[0][0], int(item[0][1:]))):
            verifier_flag = verdict["judgment"] in MISREADING
            critic = CRITIC[exercise]
            if claim in critic["flagged"]:
                critic_flag = True
            elif claim in critic["clean"]:
                critic_flag = False
            else:
                critic_flag = None
            rows.append({"claim": claim, "verifier": verdict["judgment"], "verifier_register": verdict["evidence_register"],
                         "verifier_flag": verifier_flag, "critic_flag": critic_flag,
                         "agree": (verifier_flag == critic_flag) if critic_flag is not None else None})
        agree = sum(1 for row in rows if row["agree"])
        total = sum(1 for row in rows if row["agree"] is not None)
        summary["exercises"][exercise] = {
            "claims": len(rows), "verifier_flags": sum(row["verifier_flag"] for row in rows),
            "critic_flags": sum(1 for row in rows if row["critic_flag"]), "compared": total, "agree": agree,
            "critic_source": CRITIC[exercise]["source"], "rows": rows,
        }
    summary["disagreements_adjudicated_by_hand"] = "see EVALUATION.md section 4"
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for exercise, data in summary["exercises"].items():
        print(f"{exercise}: claims {data['claims']}, verifier flags {data['verifier_flags']}, critic flags {data['critic_flags']}, "
              f"agreement {data['agree']}/{data['compared']}")


if __name__ == "__main__":
    main()
