import sys, hashlib, json, pathlib
oid, text = sys.argv[1], sys.stdin.read()
p = pathlib.Path(f"/tmp/claude-0/-home-user-auteur/55e1f0ad-02df-5f40-a07d-9d274de959e5/scratchpad/v2run/raw-outputs/{oid}.md")
p.write_text(text, encoding="utf-8")
print(oid, hashlib.sha256(text.encode()).hexdigest()[:16], len(text))
