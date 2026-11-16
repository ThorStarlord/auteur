"""Build the qualification artifact manifest and drop oversized intermediates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("qualification")
DROP = {
    "qual576/artifacts/projection.json",
    "qual576/artifacts/resume.json",
    "t10/arm-a/resume-after-apply.json",
}

rows = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.suffix == ".pyc":
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel in {"t10/blind/mapping.json", "MANIFEST.md"}:
        continue
    data = path.read_bytes()
    rows.append({
        "path": rel,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "committed": rel not in DROP,
    })

header = [
    "# Qualification artifact manifest",
    "",
    "Every file produced by the 2026-11-16 qualification run. Files marked",
    "NOT COMMITTED were produced and hashed but omitted from git because of size;",
    "their checksums preserve their identity.",
    "",
    "| Path | Bytes | SHA-256 | Committed |",
    "|---|---|---|---|",
]
body = []
for row in rows:
    mark = "yes" if row["committed"] else "**no**"
    body.append(
        "| `{}` | {} | `{}...` | {} |".format(
            row["path"], row["bytes"], row["sha256"][:32], mark,
        )
    )
(ROOT / "MANIFEST.md").write_text("\n".join(header + body) + "\n", encoding="utf-8")

for rel in DROP:
    target = ROOT / rel
    if target.exists():
        target.unlink()

print(json.dumps({
    "files": len(rows),
    "committed": sum(1 for r in rows if r["committed"]),
    "dropped": len(DROP),
}, indent=2))
