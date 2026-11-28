"""Grade the v2 sensitivity answers (neutral filler) through the owner's contract and checks, joined to the private mapping."""
import json
import sys
from pathlib import Path

ROOT = Path("H:/GithubRepositories/auteur/.worktrees/grounded-creative-synthesis")
sys.path.insert(0, str(ROOT / "src"))

from auteur.beginner.studio_architecture_verification import ClaimVerification, _check_verification  # noqa: E402

BASE = Path("C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/bd7bca2c-32f1-43e5-ad86-8d497e2b3639/scratchpad/g1/sensitivity_v3")


def grade() -> list[dict]:
    mapping = json.loads((BASE / "mapping.private.json").read_text(encoding="utf-8"))
    rows = []
    for item in sorted(mapping):
        request = json.loads((BASE / "requests_opaque" / f"{item}.json").read_text(encoding="utf-8"))
        user = json.loads(request["user"])
        row = {"item": item, "pair": mapping[item]}
        answer_path = BASE / "answers" / f"{item}.json"
        if not answer_path.exists():
            row["status"] = "no answer"
            rows.append(row)
            continue
        text = answer_path.read_text(encoding="utf-8")
        try:
            verdict = ClaimVerification.model_validate_json(text)
            _check_verification(verdict, user)
            row.update({"status": "accepted", "judgment": verdict.judgment, "register": verdict.evidence_register,
                        "clauses": [(clause.status, clause.text[:90]) for clause in verdict.clauses],
                        "possibility": verdict.defensible_possibility, "survives": verdict.relation_survives_correction,
                        "reasoning": verdict.reasoning})
        except ValueError as refusal:
            row.update({"status": "refused", "refusal": str(refusal).splitlines()[0][:220]})
        rows.append(row)
    return rows


if __name__ == "__main__":
    out = grade()
    (BASE / "graded.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in out:
        if row["status"] != "accepted":
            print(row["item"], row["pair"], row["status"], row.get("refusal", ""))
        else:
            print(row["item"], row["pair"], row["judgment"], row["register"], row["survives"],
                  [status for status, _ in row["clauses"]])
