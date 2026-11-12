"""Apply a completed working revision in a disposable Studio canvas.

Auteur's CLI bridge exposes prepare, complete-file and show, but not apply.
Applying a reviewed working revision therefore uses the Python entry point
apply_architecture_review(), as the original experiment did. Only the scratch
canvas named on the command line is written.

Usage: python apply_review.py <project_root> <canvas_id> <request_sha256>
"""
import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import apply_architecture_review
from auteur.beginner.studio_store import CanvasStore

project, canvas, sha = sys.argv[1], sys.argv[2], sys.argv[3]
store = CanvasStore(Path(project), canvas)
result = apply_architecture_review(store, sha)
print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
