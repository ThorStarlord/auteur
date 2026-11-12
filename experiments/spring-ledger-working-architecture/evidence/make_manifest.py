"""Write a machine-generated SHA-256 manifest of every file in this package (excluding itself).

Usage: python make_manifest.py <package_dir>
Hashes are of the bytes in the working copy (CRLF on this machine); committed blobs are LF.
"""
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1]).resolve()
rows = []
for p in sorted(root.rglob("*")):
    if p.is_file() and p.name != "manifest.json":
        rows.append({"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size,
                     "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
(root / "evidence" / "manifest.json").write_text(json.dumps({"package": root.name, "files": rows}, indent=2) + "\n", encoding="utf-8")
print(len(rows), "files")
