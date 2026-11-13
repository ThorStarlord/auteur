"""Hash every file under a project, so before and after states of a Book operation can be compared exactly."""
import hashlib
import json
import sys
from pathlib import Path

project = Path(sys.argv[1])
out = Path(sys.argv[2])
files = {}
for path in sorted(project.rglob("*")):
    if path.is_file():
        files[path.relative_to(project).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
out.write_text(json.dumps(files, indent=2, sort_keys=True), encoding="utf-8")
print(f"{len(files)} files hashed -> {out}")
