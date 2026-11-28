"""Build paired verification requests for the epistemic-label sensitivity experiment.

Each pair holds the evidence and the developments fixed (the Exercise A packet) and changes one controlled feature. The packets are
built through the owner's own packet builder, so each request carries the real instruction and the real evidence text. Nothing is stored
as a synthesis or a verification record; this is a controlled experiment on the verifier, not a product judgement.
"""
import json
import sys
from pathlib import Path

REPO = Path("H:/GithubRepositories/auteur/.worktrees/grounded-creative-synthesis")
sys.path.insert(0, str(REPO / "src"))

from auteur.beginner.studio_architecture_verification import _SYSTEM_VERIFY, _packet, claims_of, dependents_of  # noqa: E402
from auteur.host_agent import model_output_contract  # noqa: E402
from auteur.beginner.studio_architecture_verification import ClaimVerification  # noqa: E402

SCRATCH = Path("C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/bd7bca2c-32f1-43e5-ad86-8d497e2b3639/scratchpad/g1/sensitivity_v2")
PACKET = json.loads(Path("C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/bd7bca2c-32f1-43e5-ad86-8d497e2b3639/scratchpad/ltm/verify/A3/request-verification-s1.json").read_text(encoding="utf-8"))
SOURCE = json.loads(PACKET["user"])
EVIDENCE = SOURCE["evidence"]
DEVELOPMENTS = SOURCE["developments"]
QUESTION = SOURCE["synthesis_question"]

STAGE_FILLER = {"book": None, "horizon": "proposed_book", "becomes_available": "The stage asks what the lineage would then have to carry.",
                "changes": "The stage asks what it would mean for the labour."}


def stage(development, basis, evidence, **extra):
    return {**STAGE_FILLER, "development": development, "basis": basis, "evidence": evidence, "quote": None, **extra}


def answer(trajectory=None, alternatives=None):
    return {"trajectory": trajectory or [stage("A filler development that is not under test.", "proposed", ["E1"])],
            "relations": [], "culmination": None,
            "alternative_paths": alternatives or [{"ordering": "A filler ordering.", "effect": "A filler effect.",
                                                    "viability": "viable", "evidence": ["E1"], "quote": None}],
            "opportunities": []}


def quote_of(identifier, length=60):
    return next(item["text"] for item in EVIDENCE if item["id"] == identifier)[:length]


PAIRS = {}
# P1: identical wording and evidence; only the declared basis differs
P1_TEXT = "Book 24 is where the labour gap is first met by people rather than by a schedule."
PAIRS["P1a_recorded"] = ("s1", answer([stage(P1_TEXT, "recorded", ["E5", "E1"])]))
PAIRS["P1b_proposed"] = ("s1", answer([stage(P1_TEXT, "proposed", ["E5", "E1"])]))
# P2: identical basis; the wording is unconditional or conditional
PAIRS["P2a_unconditional"] = ("s1", answer([stage("Outside apprentices are trained under the Special Draw Right and their repair is demonstrated, so the condition the Right carries is tested.", "proposed", ["E3", "E7"])]))
PAIRS["P2b_conditional"] = ("s1", answer([stage("If outside apprentices are trained under the Special Draw Right, their repair could be demonstrated, and the condition the Right carries would then be tested.", "proposed", ["E3", "E7"])]))
# P3: a legitimate proposal, with and without an unsupported premise; the possibility is the same
PAIRS["P3a_unsupported_premise"] = ("s1", answer([stage("A later Book could have the Council steward refuse the outside crew, because the Mill Compact has already secured the lineage's loyalty.", "proposed", ["E5"])]))
PAIRS["P3b_no_premise"] = ("s1", answer([stage("A later Book could have the Council steward refuse the outside crew, which would test her commitment to the labour.", "proposed", ["E5"])]))
# P4: the same content under a labelled inference or a recorded label
PAIRS["P4a_labelled_inference"] = ("s1", answer([stage("Inferred: the uncounted generation practises both kinds of return and may, in time, claim standing in channel coordination.", "inferred", ["E8", "E4"])]))
PAIRS["P4b_recorded_label"] = ("s1", answer([stage("The uncounted generation practises both kinds of return and may, in time, claim standing in channel coordination.", "recorded", ["E8", "E4"])]))
# P5: a hypothetical ordering against an asserted necessity (an alternative path)
PAIRS["P5a_hypothetical_order"] = ("a1", answer(alternatives=[{"ordering": "If the training demonstration comes before the review, the review tests demonstrated repair.", "effect": "The reader would meet the review in that order.", "viability": "viable", "evidence": ["E3"], "quote": None}]))
PAIRS["P5b_asserted_necessity"] = ("a1", answer(alternatives=[{"ordering": "The review must come after the training demonstration, because the Right cannot be reviewed before it is trained.", "effect": "The reader would meet the review in that order.", "viability": "viable", "evidence": ["E3"], "quote": None}]))


def build() -> None:
    (SCRATCH / "requests").mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, (claim, synthetic) in PAIRS.items():
        claims = claims_of(synthetic)
        uses = dependents_of(synthetic, claims)
        record = {"question": QUESTION, "developments": DEVELOPMENTS, "evidence": EVIDENCE}
        user_text = json.dumps(_packet(record, claim, claims, uses), ensure_ascii=False, sort_keys=True)
        request = {"system": _SYSTEM_VERIFY, "user": user_text, "output_contract": model_output_contract(ClaimVerification),
                   "claim": claim, "pair": name}
        (SCRATCH / "requests" / f"{name}.json").write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest[name] = {"claim": claim, "wording": claims[claim]["wording"]}
    (SCRATCH / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("built", len(PAIRS), "requests")


if __name__ == "__main__":
    build()
