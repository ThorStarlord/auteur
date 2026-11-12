"""Build the Stage A review packet for the final corrected 30-Book candidate.

Usage: python make_stage_packet.py <worktree_root> <out_dir> <source_commit>

Sources are read from <source_commit> with `git show`, so the packet is built from
committed content, not from whatever the working copy holds. Templates are read from
the verification experiment's review/templates folder in the working copy.

Withholdings are applied only where marked below. They are the designer's own
self-assessment and nomination passages, and each one is named in the printed log.
The coordinator's manifest is written to a separate record folder, not to the packet,
so the reviewer does not see the names of files that were left out.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
commit = sys.argv[3]
exp_rel = "experiments/series-architecture-30-book-construction"
v1_rel = "experiments/series-architecture-30-book-v1"
ver_rel = "experiments/series-architecture-30-book-verification"
out.mkdir(parents=True, exist_ok=True)


def blob(path):
    return subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{path}"],
        capture_output=True, check=True,
    ).stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text(path):
    return blob(path).decode("utf-8")


def template(name):
    return (root / ver_rel / "review" / "templates" / name).read_text(encoding="utf-8")


# 01: the author's fixed brief, from the four recorded intentions and the Fixed/Open rows of §1.
intentions = [json.loads(text(f"{v1_rel}/evidence/intention-{n}.json"))["intention"] for n in range(1, 5)]
original = text(f"{v1_rel}/A-original-architecture.md")
fixed_rows = [
    line for line in original.splitlines()
    if line.startswith("| **[Fixed]**") or line.startswith("| **[Open to author choice]**")
]
assert len(fixed_rows) == 2, fixed_rows
brief = ["# Author brief (fixed input)", "",
         "Source: the four Studio intention records in `experiments/series-architecture-30-book-v1/evidence/` "
         "(intention-1 to intention-4). Authority recorded as `author_directed_working_intention`. "
         "Each is working and noncanonical.", ""]
for it in intentions:
    brief += [f"## {it['title']}", "", f"Record: `{it['id']}`", "", it["directive"], ""]
brief += ["## Fixed and open rows from the original architecture (§1)", "",
          "| Status | Commitment |", "|---|---|"] + fixed_rows + [""]
(out / "01-author-brief.md").write_text("\n".join(brief), encoding="utf-8")

# 02: the original architecture, with the designer's self-assessment withheld.
cut = original.index("## 8. Where the design is thin (admitted)")
a_wh = original[:cut].rstrip() + (
    "\n\n## 8. [Withheld by design: the designer's self-assessment of the original architecture.]\n")
sentence = "Arc IV is deliberately the thinnest. It is the place where filler is most likely (see §8)."
assert a_wh.count(sentence) == 1
a_wh = a_wh.replace(sentence, "[Withheld by design: one sentence of the designer's self-assessment.]")
(out / "02-original-architecture.md").write_text(a_wh, encoding="utf-8")

# 03: the causal construction, included unmodified.
(out / "03-causal-construction.md").write_bytes(blob(f"{exp_rel}/01-causal-construction.md"))

# 04: the finale alternatives, with the designer's nomination and one advocacy paragraph withheld.
fin = text(f"{exp_rel}/02-finale-alternatives.md")
start = fin.index("## Working direction for testing")
end = fin.index("## Author-reserved decisions")
fin_wh = fin[:start] + "[Withheld by design: the designer's nomination section.]\n\n" + fin[end:]
assert fin_wh.count("**Why it is an improvement.**") == 1
p0 = fin_wh.index("**Why it is an improvement.**")
p1 = fin_wh.index("\n", p0)
fin_wh = fin_wh[:p0] + "[Withheld by design: the designer's advocacy paragraph for one mechanism.]" + fin_wh[p1:]
(out / "04-finale-alternatives.md").write_text(fin_wh, encoding="utf-8")

# 05: the final corrected candidate (W2), included byte-for-byte.
(out / "05-candidate-W2.json").write_bytes(blob(f"{exp_rel}/03-working-candidate-v2.json"))

# 00 and 06: the reviewer instructions and the source identity, from the templates.
(out / "00-reviewer-instructions.md").write_text(template("00-reviewer-instructions.md"), encoding="utf-8")
(out / "06-source-identity.md").write_text(template("06-source-identity.md"), encoding="utf-8")

packet = sorted(p for p in out.iterdir() if p.is_file())
manifest = {
    "packet": "stage-A",
    "source_commit": commit,
    "builder": f"{ver_rel}/evidence/make_stage_packet.py",
    "files": [{"path": p.name, "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size} for p in packet],
    "source_blobs": {
        rel: sha(blob(rel)) for rel in [
            f"{v1_rel}/A-original-architecture.md",
            f"{exp_rel}/01-causal-construction.md",
            f"{exp_rel}/02-finale-alternatives.md",
            f"{exp_rel}/03-working-candidate-v2.json",
        ]
    },
    "withholdings": [
        {"packet_file": "02-original-architecture.md",
         "withheld": "§8 'Where the design is thin (admitted)' (whole section); one sentence in §4",
         "reason": "the designer's self-assessment of the original architecture"},
        {"packet_file": "04-finale-alternatives.md",
         "withheld": "section 'Working direction for testing (agent-proposed, not an author decision)'; "
                     "the paragraph 'Why it is an improvement.' under C",
         "reason": "the designer's nomination and advocacy for one mechanism"},
    ],
    "included_but_labelled": [
        {"packet_file": "05-candidate-W2.json",
         "where": ["summary (names C as the agent-proposed working direction for testing)",
                   "nodes.alt_c_ratified_trigger.title"],
         "reason": "the candidate is included byte-for-byte; the labels are disclosed in file 00 and file 06"},
        {"packet_file": "03-causal-construction.md",
         "note": "the designer's reasoning and reskin checks are included unmodified"},
        {"packet_file": "04-finale-alternatives.md",
         "note": "the comparison table is the designer's characterisation; included unmodified; file 00 says to treat it as a claim"},
    ],
    "not_in_packet_but_referenced": ["05-consistency-record.md (linked from 03)",
                                     "A-studio-candidate-original.json (named in 02)"],
}
record = pathlib.Path(sys.argv[4]) if len(sys.argv) > 4 else None
if record:
    record.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("manifest written:", record)
for entry in manifest["files"]:
    print(f"{entry['sha256'][:16]}  {entry['bytes']:>7}  {entry['path']}")
