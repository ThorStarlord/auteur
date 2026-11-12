"""Write a machine-generated manifest of every file in the verification experiment (SHA-256).

Usage: python make_manifest.py <experiment_dir>
The manifest excludes itself. Hashes are of the bytes on disk in this worktree.
"""
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1]).resolve()
rows = []
for p in sorted(root.rglob("*")):
    if not p.is_file() or p.name == "manifest.json":
        continue
    rows.append({"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size,
                 "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
(root / "evidence" / "manifest.json").write_text(
    json.dumps({"experiment": root.name, "files": rows}, indent=2) + "\n", encoding="utf-8")
print(len(rows), "files")
