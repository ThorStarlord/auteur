"""Check that quotations in the Stage A and Stage B reports appear in their packets.

Usage: python check_quotes.py <report.md> <packet_dir> [more packet files...]

A quotation is any text between double quotation marks in the report with at least
12 characters. Quotations containing an ellipsis are split on it, and each fragment of
at least 12 characters must appear. Matching ignores case, curly quotes and whitespace
runs. Each report line names the quotation's status: found, split-found, or missing.
"""
import pathlib
import re
import sys

report = pathlib.Path(sys.argv[1])
packet_dir = pathlib.Path(sys.argv[2])


def norm(s):
    s = s.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\\", "")
    return re.sub(r"\s+", " ", s).strip().lower()


corpus = "\n".join(p.read_text(encoding="utf-8") for p in sorted(packet_dir.iterdir()) if p.is_file())
corpus_n = norm(corpus)
text = report.read_text(encoding="utf-8")
body = text.split("---", 2)[-1] if text.count("---") >= 2 else text
quotes = re.findall(r'"([^"\n]{12,})"', body)
seen = []
results = {"found": 0, "split-found": 0, "missing": 0}
for q in quotes:
    if q in seen:
        continue
    seen.append(q)
    fragments = [f.strip(" .,;:") for f in re.split(r"…|\.\.\.", q) if len(f.strip()) >= 12]
    if not fragments:
        continue
    hits = [norm(f) in corpus_n for f in fragments]
    if all(hits) and len(fragments) == 1:
        status = "found"
    elif all(hits):
        status = "split-found"
    else:
        status = "missing"
    results[status] += 1
    print(f"{status:12} | {q[:110]}")
print("summary:", results)
