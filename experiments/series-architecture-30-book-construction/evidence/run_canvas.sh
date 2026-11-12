#!/usr/bin/env bash
# Run one Studio canvas through Auteur's architecture operations, in a disposable project.
#
#   run_canvas.sh <project_root> <canvas_id> <baseline_candidate.json> \
#                 [<revision_instruction.txt> <revision_candidate.json>]
#
# Steps: create the canvas with the fixed Story Vision; record the four author-fixed
# intentions from PR #551; submit the baseline candidate as a completed host response;
# and, if a revision is given, prepare it with its instruction, submit the revised
# candidate as the host response, and apply the reviewed working revision.
# Every product response is written to <project_root>/../<canvas_id>-run/.
set -euo pipefail

PROJ="$1"; CANVAS="$2"; BASE="$3"; INSTR="${4:-}"; REVCAND="${5:-}"
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
SRC_551="${SRC_551:-H:/GithubRepositories/worktrees/auteur-series-architecture-30/experiments/series-architecture-30-book-v1}"
OUT="$(dirname "$PROJ")/${CANVAS}-run"
mkdir -p "$OUT/intent"
export PYTHONPATH="$REPO/src" PYTHONUTF8=1
BRIDGE=(python -m auteur.beginner.studio_architecture --project "$PROJ" --canvas "$CANVAS")

python "$SRC_551/evidence/create_store.py" "$PROJ" "$CANVAS" > "$OUT/create.txt"

python - "$SRC_551" "$OUT/intent" <<'PY'
import json, pathlib, sys
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
for i in range(1, 5):
    it = json.loads((src / "evidence" / f"intention-{i}.json").read_text(encoding="utf-8"))["intention"]
    (out / f"directive-{i}.txt").write_text(it["directive"], encoding="utf-8")
    (out / f"title-{i}.txt").write_text(it["title"], encoding="utf-8")
PY
for i in 1 2 3 4; do
  "${BRIDGE[@]}" keep-intention --title "$(cat "$OUT/intent/title-$i.txt")" \
      --directive-file "$OUT/intent/directive-$i.txt" > "$OUT/keep-$i.json"
done

"${BRIDGE[@]}" prepare > "$OUT/baseline-prepare.json"
"${BRIDGE[@]}" complete-file --candidate "$BASE" > "$OUT/baseline-complete.json"

if [[ -n "$INSTR" ]]; then
  "${BRIDGE[@]}" prepare --instruction "$(cat "$INSTR")" > "$OUT/revision-prepare.json"
  SHA="$(python -c "import json,sys;print(json.load(open(sys.argv[1],encoding='utf-8'))['request']['request_sha256'])" "$OUT/revision-prepare.json")"
  "${BRIDGE[@]}" complete-file --candidate "$REVCAND" > "$OUT/revision-complete.json"
  python "$REPO/experiments/series-architecture-30-book-construction/evidence/apply_review.py" "$PROJ" "$CANVAS" "$SHA" > "$OUT/revision-apply.json"
  echo "$SHA" > "$OUT/revision-request-sha256.txt"
fi
"${BRIDGE[@]}" show > "$OUT/show-final.json"
echo "canvas $CANVAS done; outputs in $OUT"
