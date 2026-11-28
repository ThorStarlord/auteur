"""Fix the six defects found by the independent implementation review of the grounded-synthesis increment."""
from pathlib import Path

ROOT = Path("H:/GithubRepositories/auteur/.worktrees/grounded-creative-synthesis")
verif = ROOT / "src/auteur/beginner/studio_architecture_verification.py"
host = ROOT / "src/auteur/host_agent.py"


def replace_once(text, old, new):
    assert text.count(old) == 1, ("anchor count", text.count(old), old[:90])
    return text.replace(old, new)


s = verif.read_text(encoding="utf-8")

# (4) the instruction states every bound that the owner enforces, including the conditional requirements the generator cannot express
# (3) the key list matches the contract (version 2 and every key)
s = replace_once(
    s,
    "Return ONLY one JSON object with these keys: schema_version (1), claim, evidence_register, judgment, affects, reasoning, evidence, quote, alternative_reading, would_settle, creative_room. Field names and literal values are exact, as the output_contract gives them.",
    "Return ONLY one JSON object with these keys: schema_version (2), claim, evidence_register, judgment, affects, reasoning, evidence, quote, alternative_reading, would_settle, creative_room, clauses, defensible_possibility, relation_survives_correction. Field names and literal values are exact, as the output_contract gives them.\n\n"
    "Required, enforced by the owner: clauses (at least one) for every judgement other than insufficient_evidence; evidence for every judgement other than creative_speculation and insufficient_evidence; alternative_reading for every judgement other than supported, defensible_inference, creative_speculation and insufficient_evidence; would_settle for insufficient_evidence; creative_room always.",
)

# (5) the tense rule reaches proposed claims only: an inference from established facts may be indicative
s = replace_once(
    s,
    "If a claim labelled proposed or inferred states its proposed event in the indicative",
    "If a claim labelled proposed states its proposed event in the indicative",
)

# (1) and (2) clause checks: a judgement must name its clauses; a clause must name a whole part of the claim; a supported judgement cannot
# carry a clause the verifier marks proposed, unsupported or contradicted
new_clause_fn = (
    open(Path(__file__).with_name("new_clause_fn.txt"), encoding="utf-8").read()
)
old_start = s.index("def _check_clauses(verdict: ClaimVerification, user: dict[str, Any]) -> list[str]:")
old_end = s.index("def _check_verification(", old_start)
s = s[:old_start] + new_clause_fn + s[old_end:]

s = replace_once(s, "    problems += _check_clauses(verdict, user)\n",
                 "    if hasattr(verdict, \"clauses\"):  # contract version 2; a version-1 judgement has no clauses and is checked as it was\n"
                 "        problems += _check_clauses(verdict, user)\n")

# (6) contract version 1 stays readable: a request prepared under version 1 completes under the version-1 model
s = replace_once(s, "class ClaimVerification(BaseModel):\n",
'''class ClaimVerificationV1(BaseModel):
    """Contract version 1: a judgement with no clauses. Kept so that a request prepared under version 1 can still be completed under the
    contract it was prepared with (its identity is its inputs; it is not rebound to a newer contract)."""
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    claim: Annotated[str, StringConstraints(pattern=CLAIM_PATTERN)]
    evidence_register: Literal["established", "inferred_from_established", "agent_proposed", "author_stated", "not_established", "mixed"]
    judgment: Literal["supported", "defensible_inference", "creative_speculation", "overreaching", "temporal_misreading",
                      "modal_misreading", "attribution_error", "standing_confusion", "unsupported_relation", "contradicted",
                      "insufficient_evidence"]
    affects: Literal["creative_possibility", "asserted_condition", "load_bearing_premise"]
    reasoning: str = Field(min_length=1, max_length=REASONING_CHARS)
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=EVIDENCE_MAX)
    quote: str | None = Field(default=None, max_length=QUOTE_CHARS)
    alternative_reading: str | None = Field(default=None, max_length=ALTERNATIVE_CHARS)
    would_settle: str | None = Field(default=None, max_length=SETTLE_CHARS)
    creative_room: str = Field(min_length=1, max_length=ROOM_CHARS)


class ClaimVerification(BaseModel):
''')

s = replace_once(s, "            verdict = ClaimVerification.model_validate_json(response.text)\n",
                 "            model = ClaimVerificationV1 if request.settings.get(\"verification_schema_version\") == 1 else ClaimVerification\n"
                 "            verdict = model.model_validate_json(response.text)\n")
s = replace_once(s, '''    "AUTHORITY", "ClaimVerification", "ROLE", "SCHEMA", "claim_inventory", "claim_text", "claims_of", "complete_claim_verification",''',
                 '''    "AUTHORITY", "ClaimVerification", "ClaimVerificationV1", "ROLE", "SCHEMA", "claim_inventory", "claim_text", "claims_of",
    "complete_claim_verification",''')
verif.write_text(s, encoding="utf-8")

h = host.read_text(encoding="utf-8")
# (4) a minimum of one is stated too: a non-empty field is a bound the owner enforces
h = replace_once(h, '            if option.get("minLength", 0) > 1:', '            if option.get("minLength", 0) >= 1:')
h = replace_once(h, '                if option.get("minItems", 0) > 1:', '                if option.get("minItems", 0) >= 1:')
host.write_text(h, encoding="utf-8")
print("review defects patched")
