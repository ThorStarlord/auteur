"""Demonstration B measures: how much of the Book 24 source survives verbatim, and which terms and identifiers carry.

Run from the repository root:
  python docs/qualification-evidence/working-book-architecture-20261112/measure_source_preservation.py <path-to-book-24-source.md>
The source is the noncanonical cold-start function at commit fa85b7f1 (experiments/spring-ledger-working-architecture/cold-start/output/).
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
source = Path(sys.argv[1]).read_text(encoding="utf-8")
artifact = json.loads((HERE / "book-24-candidate.json").read_text(encoding="utf-8"))
TEXT_KEYS = {"text", "condition", "choice", "consequence", "changed_state", "new_possibility",
             "question", "pressure", "rationale", "reversal", "title"}


def texts(node):
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in TEXT_KEYS and isinstance(value, str):
                found.append(value)
            else:
                found += texts(value)
    elif isinstance(node, list):
        for value in node:
            found += texts(value)
    return found


def normalise(text):
    return re.sub(r"\s+", " ", re.sub(r"[*_`>#\[\]()]", "", text)).strip().lower()


corpus = normalise(" ".join(texts(artifact)))
sentences = [normalise(s) for s in re.split(r"(?<=[.!?])\s+", source) if len(s.strip()) >= 60]
verbatim = [s for s in sentences if s[:80] in corpus]
terms = set(re.findall(r"\b[A-Z][a-z]{3,}\b", source))
found_terms = {t for t in terms if t.lower() in corpus}
identifiers = set(re.findall(r"\b(?:th|eng|str|rx|inst|gn|alt|ph|et|l)_[a-z0-9_]+", source))
result = {
    "source_sentences_60_plus_chars": len(sentences),
    "verbatim_first_80_chars_present_in_artifact": len(verbatim),
    "verbatim_ratio": round(len(verbatim) / max(1, len(sentences)), 3),
    "capitalised_terms_in_source": len(terms),
    "capitalised_terms_present_in_artifact": len(found_terms),
    "capitalised_terms_absent": sorted(terms - found_terms),
    "source_identifiers_cited": len(identifiers),
    "source_identifiers_listed": sorted(identifiers),
}
print(json.dumps(result, indent=2, ensure_ascii=False))
