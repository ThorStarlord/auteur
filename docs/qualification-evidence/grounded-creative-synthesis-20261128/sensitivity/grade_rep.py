import json, sys
from pathlib import Path
sys.path.insert(0, "H:/GithubRepositories/auteur/.worktrees/grounded-creative-synthesis/src")
from auteur.beginner.studio_architecture_verification import ClaimVerification, _check_verification
B = Path("C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/bd7bca2c-32f1-43e5-ad86-8d497e2b3639/scratchpad/g1")
for name in ["v2-item-03-r1", "v2-item-03-r2", "v2-item-04-r1", "v3-item-04-r1", "v3-item-04-r2", "v3-item-03-r2"]:
    version, item = name.split("-item-")[0], "item-" + name.split("-item-")[1][:2]
    req = json.loads((B / f"sensitivity_{version}/requests_opaque/{item}.json").read_text(encoding="utf-8"))
    user = json.loads(req["user"])
    path = B / "sensitivity_rep/answers" / f"{name}.json"
    if not path.exists():
        print(name, "no answer yet"); continue
    try:
        v = ClaimVerification.model_validate_json(path.read_text(encoding="utf-8"))
        _check_verification(v, user)
        print(name, "ACCEPTED", v.judgment, [c.status for c in v.clauses])
    except ValueError as e:
        print(name, "REFUSED", str(e).splitlines()[0][:150])
