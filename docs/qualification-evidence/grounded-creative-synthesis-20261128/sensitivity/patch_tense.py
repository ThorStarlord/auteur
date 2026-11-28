from pathlib import Path

p = Path("H:/GithubRepositories/auteur/.worktrees/grounded-creative-synthesis/src/auteur/beginner/studio_architecture_verification.py")
s = p.read_text(encoding="utf-8")
anchor = "Use only the identifiers in allowed_evidence."
assert s.count(anchor) == 1, s.count(anchor)
addition = (
    "A proposal is stated conditionally. If a claim labelled proposed or inferred states its proposed event in the indicative, as though it "
    "occurs (for example 'are trained', 'is demonstrated', 'is tested'), that wording is a modal misreading: the label does not license the "
    "tense. Judge the tense, and give the conditional reading the evidence supports in alternative_reading. A hypothetical that asserts no "
    "necessary dependency, written as an 'if' or 'could', is not a misreading of tense; judge its premises clause by clause.\n\n"
)
s = s.replace(anchor, addition + anchor)
p.write_text(s, encoding="utf-8")
print("tense sentence added to the verifier instruction")
