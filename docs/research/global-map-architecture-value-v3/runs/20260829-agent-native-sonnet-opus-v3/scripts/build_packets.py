"""V3 empirical execution: packet construction (instruction shell / condition
packet split, per execution-contract.md sections 5 and 12).

Reuses V2's frozen substantive PROBES/C_DECISION_MAPS content unchanged
(condition-specification.md, decision-probes.md, candidate-architecture-
ledger.md are reused by reference, not modified). B_MAPS reused from the
already-generated, byte-verified-identical b_condition_maps.json in this
run directory (Condition B source and fixture confirmed unchanged vs
3cc4975 before this script ran).

No model inference occurs in this script.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

RUN_ID = "20260829-agent-native-sonnet-opus-v3"
SOURCE_REVISION = "3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41"

OUT = Path(__file__).parent.parent
PACKET_DIR = OUT / "packets"
PACKET_DIR.mkdir(exist_ok=True)

GENERIC_CONTRACT = """Provide a bounded recommendation analysis:
- which option you recommend among the presented options (or that none is viable if truly incompatible),
- why (cite past commitments/facts that matter now),
- principal tradeoff,
- what you deliberately excluded as not relevant.

Cite which accepted facts/commitments you relied on by plain name (not internal IDs).
Do not invent unsupported facts; do not treat unaccepted material as accepted.
Recommendation is non-authoritative: choosing an option does not create Book Direction or canon and does not modify Canonical State."""

SYSTEM_ROLE = (
    "You are a story consultant for Series \"Archive of Lies\" (ongoing). "
    "Series promise: \"Each recovered account reveals who profits when history is controlled.\" "
    "Series pressure: \"Every public correction gives hidden archivists reason to erase another witness.\" "
    "Series open question: \"Can truth survive without becoming instrument of power?\""
)

NON_AUTHORITY_REMINDER = (
    "Your recommendation is a planning choice, not canon. It does not create a Book Direction "
    "and does not modify Canonical State."
)

PROBES = {
    "P01": dict(
        horizon="Book 2 opening (accepted history through Book 1)",
        plain_facts=[
            "Series commitment `contested-history`: Every Book must expose conflict between official history and lived memory.",
            "Series commitment `commitment-falsifier`: person who falsified founding record must be identified.",
            "Book 1 Direction \"The Missing Ledger\": want was to recover a ledger that proves the city falsified the archive; resistance was that custodians erase witnesses; conflict was authenticating while choosing witnesses; stakes were that publishing too soon destroys witnesses while waiting erases truth.",
            "Book 1 Realization: the founding record was forged.",
            "Book 1 Realization: the monastery preserves a testimony.",
            "Book 1 Realization: a lantern was broken during the archive search.",
            "Current state: archive.founding_record = forged.",
            "Current state: monastery.testimony = preserved.",
            "Current state: archive_lantern.condition = broken.",
        ],
        intent="Make the forged founding record matter to lived memory.",
        question="How should Book 2 make the exposed fraud matter to lived memory?",
        options=[
            ("witness-account", "Center the living witness's account against the forged record", "centers lived memory but exposes witness early"),
            ("cover-up-trace", "Trace the institutional cover-up that produced the forged record", "keeps institutional history central but delays lived-memory witness"),
        ],
        b_book=2,
    ),
    "P02": dict(
        horizon="Book 3 opening (accepted history through Book 2)",
        plain_facts=[
            "Series commitment `contested-history`: Every Book must expose conflict between official history and lived memory.",
            "Book 1 Realization: the founding record was forged.",
            "Book 1 Realization: the monastery preserves a testimony.",
            "Book 1 Realization: a lantern was broken during the archive search.",
            "Book 2 Direction \"The Council's Retraction\": want was to identify the falsifier and force the council to answer; resistance was that the council could admit then retract.",
            "Book 2 Realization: evidence identifies the person who falsified the record.",
            "Book 2 Realization: the council publicly admitted the archive record was falsified.",
            "Book 2 Realization: the council later retracted its admission.",
            "Current state: archive.founding_record = forged.",
            "Current state: archive.falsifier = named.",
            "Current state: council.archive_position = retracted admission (this is the current position; the council did admit fraud earlier, but the admission was retracted).",
        ],
        intent="Respond to the council's accepted retraction.",
        question="How should Book 3 respond to the council's retraction while preserving the witness's authority?",
        options=[
            ("publish-witness-account", "Give the witness an independent public record that the council cannot retract", "protects authority but exposes witness to retaliation"),
            ("force-council-hearing", "Use the named falsifier to compel the council to answer in public", "keeps accountability central but council controls forum/timing"),
        ],
        b_book=3,
    ),
    "P03": dict(
        horizon="Book 4 opening (accepted history through Book 3)",
        plain_facts=[
            "Series commitment `contested-history`: Every Book must expose conflict between official history and lived memory.",
            "Book 1 Realization: the founding record was forged.",
            "Book 1 Realization: the monastery preserves a testimony.",
            "Book 1 Realization: a lantern was broken during the archive search (later repaired, see Book 3).",
            "Book 2 Realization: evidence identifies the person who falsified the record.",
            "Book 2 Realization: the council publicly admitted the archive record was falsified, then later retracted that admission.",
            "Book 3 Direction \"The Protected Archive\": want was to protect the archive after the council's retraction.",
            "Book 3 Realization: a treaty protects the archive as the only evidentiary chain.",
            "Book 3 Realization: the archive lantern was repaired.",
            "Current state: archive.protection = treaty protected.",
            "Current state: council.archive_position = retracted admission.",
            "Current state: monastery.testimony = preserved.",
            "Current state: archive.founding_record = forged.",
            "Current state: archive_lantern.condition = repaired.",
        ],
        intent="Return to the monastery testimony without breaking the protected archive.",
        question="How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?",
        options=[
            ("publish-verified-testimony", "Authenticate and publish the testimony while the protected archive keeps the original evidence secure", "preserves chain but delays release until verification complete"),
            ("stage-protected-hearing", "Present the testimony beside selected archive evidence under the treaty's protections", "immediate public pressure but reveals which records carry strongest evidence"),
        ],
        b_book=4,
    ),
    "P04": dict(
        horizon="Book 4 opening (accepted history through Book 3) — identical horizon to P03, adversarial option",
        plain_facts=[
            "Series commitment `contested-history`: Every Book must expose conflict between official history and lived memory.",
            "Book 1 Realization: the founding record was forged.",
            "Book 1 Realization: the monastery preserves a testimony.",
            "Book 1 Realization: a lantern was broken during the archive search (later repaired, see Book 3).",
            "Book 2 Realization: evidence identifies the person who falsified the record.",
            "Book 2 Realization: the council publicly admitted the archive record was falsified, then later retracted that admission.",
            "Book 3 Direction \"The Protected Archive\": want was to protect the archive after the council's retraction.",
            "Book 3 Realization: a treaty protects the archive as the only evidentiary chain.",
            "Book 3 Realization: the archive lantern was repaired.",
            "Current state: archive.protection = treaty protected.",
            "Current state: council.archive_position = retracted admission.",
            "Current state: monastery.testimony = preserved.",
            "Current state: archive.founding_record = forged.",
            "Current state: archive_lantern.condition = repaired.",
        ],
        intent="Return to the monastery testimony without breaking the protected archive.",
        question="How should Book 4 bring the monastery testimony back into public memory without losing the archive's evidentiary chain?",
        options=[
            ("burn-archive", "Destroy the archive so the monastery testimony becomes the only surviving public account", "makes testimony unavoidable but archive no longer exists as evidence"),
            ("publish-verified-testimony", "Authenticate and publish the testimony while preserving the protected archive", "preserves evidentiary chain but delays release until verification complete"),
        ],
        b_book=4,
    ),
    "P05": dict(
        horizon="Book 4 opening (accepted history through Book 3) — identical horizon to P03/P04, same question/options as P03",
        plain_facts=[
            "Series commitment `contested-history`: Every Book must expose conflict between official history and lived memory.",
            "Book 1 Realization: the founding record was forged.",
            "Book 1 Realization: the monastery preserves a testimony.",
            "Book 1 Realization: a lantern was broken during the archive search (later repaired, see Book 3).",
            "Book 2 Realization: evidence identifies the person who falsified the record.",
            "Book 2 Realization: the council publicly admitted the archive record was falsified, then later retracted that admission.",
            "Book 3 Direction \"The Protected Archive\": want was to protect the archive after the council's retraction.",
            "Book 3 Realization: a treaty protects the archive as the only evidentiary chain.",
            "Book 3 Realization: the archive lantern was repaired.",
            "Current state: archive.protection = treaty protected.",
            "Current state: council.archive_position = retracted admission.",
            "Current state: monastery.testimony = preserved.",
            "Current state: archive.founding_record = forged.",
            "Current state: archive_lantern.condition = repaired.",
        ],
        intent="Return to the monastery testimony without breaking the protected archive.",
        question="How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?",
        options=[
            ("publish-verified-testimony", "Authenticate and publish while protected archive keeps original secure", "preserves chain but delays release"),
            ("stage-protected-hearing", "Present testimony beside selected archive evidence under treaty", "immediate pressure but reveals strongest records"),
        ],
        b_book=4,
    ),
}

with open(OUT / "b_condition_maps.json") as f:
    B_MAPS = json.load(f)

# C_DECISION_MAPS reused verbatim from V2 (same golden ledger, unmodified)
exec(compile(open("/tmp/v2_build_packets_ref.py").read().split("def render_options")[0].split("C_DECISION_MAPS = {")[1].rsplit("}", 1)[0].join(["C_DECISION_MAPS = {", "}"]), "<c_maps>", "exec"))


def render_options_correct(options):
    lines = []
    for option_id, summary, tradeoff in options:
        lines.append(f"- {option_id}: {summary} — tradeoff: {tradeoff}")
    return "\n".join(lines)


def build_instruction_shell(probe_id: str) -> str:
    """The invariant portion, identical across A/B/C for a given probe."""
    p = PROBES[probe_id]
    return f"""{SYSTEM_ROLE}

Narrative horizon: {p['horizon']}

Current planning intent: {p['intent']}

Question:
{p['question']}

Options:
{render_options_correct(p['options'])}

Task:
{GENERIC_CONTRACT}

{NON_AUTHORITY_REMINDER}"""


def build_condition_packet(probe_id: str, condition: str) -> str:
    """The treatment-specific portion, expected to differ across A/B/C."""
    p = PROBES[probe_id]
    if condition == "A":
        return "Accepted history and current state (plain facts):\n" + "\n".join(
            f"- {fact}" for fact in p["plain_facts"]
        )
    elif condition == "B":
        return (
            "Current Auteur Series Map (derived by the shipped repeated-map-focus-v2-r1 "
            "selector from the same accepted sources):\n\n" + B_MAPS[str(p["b_book"])]
        )
    elif condition == "C":
        return C_DECISION_MAPS[p["b_book"]]
    raise ValueError(condition)


def build_full_invocation(probe_id: str, condition: str) -> str:
    shell = build_instruction_shell(probe_id)
    packet = build_condition_packet(probe_id, condition)
    # Full invocation combines shell context + treatment content in the same
    # structure the generator worker actually receives.
    p = PROBES[probe_id]
    return f"""{SYSTEM_ROLE}

Narrative horizon: {p['horizon']}

{packet}

Current planning intent: {p['intent']}

Question:
{p['question']}

Options:
{render_options_correct(p['options'])}

Task:
{GENERIC_CONTRACT}

{NON_AUTHORITY_REMINDER}"""


rows = []
for probe_id in PROBES:
    shell_text = build_instruction_shell(probe_id)
    shell_hash = hashlib.sha256(shell_text.encode()).hexdigest()
    for condition in ("A", "B", "C"):
        packet_text = build_condition_packet(probe_id, condition)
        packet_hash = hashlib.sha256(packet_text.encode()).hexdigest()
        full_text = build_full_invocation(probe_id, condition)
        full_hash = hashlib.sha256(full_text.encode()).hexdigest()
        path = PACKET_DIR / f"{probe_id}-{condition}.full.txt"
        path.write_text(full_text, encoding="utf-8")
        rows.append(dict(
            probe_id=probe_id, condition=condition,
            instruction_shell_hash=shell_hash,
            condition_packet_hash=packet_hash,
            full_invocation_hash=full_hash,
            full_path=str(path),
        ))

# Instruction-shell parity audit: same shell hash across A/B/C within a probe.
shell_by_probe = {}
for r in rows:
    shell_by_probe.setdefault(r["probe_id"], set()).add(r["instruction_shell_hash"])

parity_ok = all(len(v) == 1 for v in shell_by_probe.values())
print("instruction-shell parity per probe (A/B/C identical):", parity_ok)
for pid, hs in shell_by_probe.items():
    print(f"  {pid}: {len(hs)} distinct shell hash(es)")

# condition_packet_hash must differ across conditions within a probe
packet_by_probe = {}
for r in rows:
    packet_by_probe.setdefault(r["probe_id"], set()).add(r["condition_packet_hash"])
packet_diff_ok = all(len(v) == 3 for v in packet_by_probe.values())
print("condition-packet hashes distinct per probe (3 distinct per probe):", packet_diff_ok)

with open(OUT / "packet_hashes.json", "w") as f:
    json.dump(rows, f, indent=2)

if not (parity_ok and packet_diff_ok):
    raise SystemExit("STOP: packet construction audit failed before experimental calls")

print("Packet construction audit PASSED. 15 distinct condition packets (5 probes x A/B/C) built.")
