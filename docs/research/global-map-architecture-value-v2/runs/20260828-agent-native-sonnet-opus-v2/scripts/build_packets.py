"""Agent-native V2 replication: packet construction, schedule, opaque IDs.

Builds the 15 distinct generator packets (5 probes x 3 conditions), the
45-slot schedule (3 fresh-context repetitions per packet), randomized opaque
IDs, and the sealed condition map. Deterministic given RUN_SEED.

This script performs NO model inference. It only assembles frozen-protocol
text. Generation and evaluation are separate genuine model invocations
(spawned sub-agents), performed by the orchestrator after this script runs.
"""
from __future__ import annotations

import hashlib
import json
import random
import string
from pathlib import Path

RUN_ID = "20260828-agent-native-sonnet-opus-v2"
SOURCE_REVISION = "3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41"
RUN_SEED = int(hashlib.sha256(RUN_ID.encode()).hexdigest(), 16) % (2**32)

OUT = Path(__file__).parent
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

# ---------------------------------------------------------------------------
# Probe definitions (generator-visible; from decision-probes.md V2, verbatim)
# ---------------------------------------------------------------------------

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

C_DECISION_MAPS = {
    2: """Golden Global Map -> Decision Map (Book 2), traced to `candidate-architecture-ledger.md`:

Series:
- DIR-S1 (ACCEPTED): Series "Archive of Lies", ongoing; pressure "Every public correction gives hidden archivists reason to erase another witness."

Active commitments (current constraints on Book 2):
- DIR-SC1 `contested-history` (ACCEPTED, active): "Every Book must expose conflict between official history and lived memory." Carried by accepted Book 1 direction. [REL-01: Series pressure manifests as active conflict in each Book via carried commitment.]
- DIR-SC2 `commitment-falsifier` (ACCEPTED, active/unresolved): "Person who falsified founding record must be identified." Carried by accepted Book 1 direction; not yet resolved (resolution comes in Book 2 realization, not yet accepted at this horizon).

Active current fact:
- ST-F1 `founding-record` (ACCEPTED, active): archive.founding_record = forged. Book 2 planning intent explicitly references this fact, so it is a current constraint. [REL-02: founding-record forged is causal setup for the later named-falsifier investigation (forward-looking; investigation not yet realized at this horizon).]

History (not current constraints, included for traceability, not as active peers):
- ST-F2 `monastery-testimony` (ACCEPTED, dormant): monastery.testimony = preserved. Not referenced by Book 2 planning intent; remains dormant. [REL-06 will reactivate this only when a later planning intent explicitly references it.]
- ST-I1 `broken-lantern` (ACCEPTED, dormant/irrelevant): archive_lantern.condition = broken. [REL-08: this chain never supports active continuity.]

Excluded (not accepted, never enter Decision Map):
- ST-P1 `burn-archive`, ST-P2 `ally-militia` (PROPOSED NOT ACCEPTED).

Grouping: only one active fact (`founding-record`) currently carries `contested-history`; no multi-member group forms yet at this horizon (grouping under REL-09 requires 2+ concurrently active consequences of the same commitment).""",
    3: """Golden Global Map -> Decision Map (Book 3), traced to `candidate-architecture-ledger.md`:

Series:
- DIR-S1 (ACCEPTED): Series "Archive of Lies", ongoing; pressure as above.

Active commitments (current constraints on Book 3):
- DIR-SC1 `contested-history` (ACCEPTED, active): carried by accepted Book 1 and Book 2 direction. [REL-01]

Resolved (history support only, not an active driver):
- DIR-SC2 `commitment-falsifier` (ACCEPTED, resolved): resolved by ST-F3 `named-falsifier` (Book 2 realization). [REL-03: named-falsifier resolves commitment-falsifier; question closed.]

Active current fact:
- ST-F5 `admission-retracted` (ACCEPTED, active, current): council.archive_position = retracted admission. Book 3 planning intent explicitly references this fact, so it is the current constraint. [REL-04: this fact supersedes ST-F4 `public-admission` (council.archive_position = admitted fraud) — public-admission is accepted history but is NOT the current state; retracted admission is current.]

History (not current constraints):
- ST-F4 `public-admission` (ACCEPTED, superseded): council.archive_position = admitted fraud — accepted history, but current state is the later retraction (ST-F5), not this. [REL-04]
- ST-F1 `founding-record` (ACCEPTED, dormant): not referenced by Book 3 intent.
- ST-F2 `monastery-testimony` (ACCEPTED, dormant).
- ST-I1 `broken-lantern` (ACCEPTED, dormant/irrelevant). [REL-08]

Excluded: ST-P1, ST-P2 (unaccepted).""",
    4: """Golden Global Map -> Decision Map (Book 4), traced to `candidate-architecture-ledger.md`:

Series:
- DIR-S1 (ACCEPTED): Series "Archive of Lies", ongoing; pressure as above.

Active commitment, grouped (current constraints on Book 4):
- DIR-SC1 `contested-history` (ACCEPTED, active). [REL-01] At this horizon TWO accepted consequences concurrently carry this commitment and are grouped as one compact pressure cluster [REL-09]:
  - ST-F2 `monastery-testimony` (ACCEPTED, REACTIVATED): monastery.testimony = preserved. Dormant since Book 1; reactivated because Book 4 planning intent explicitly references it. [REL-06: dormant fact reactivated when a later planning intent's relevance refs name it.]
  - ST-F6 `archive-protected` (ACCEPTED, ACTIVE, current): archive.protection = treaty protected. Book 4 planning intent explicitly references this fact, so it is a current constraint. [REL-05: this treaty exists because ST-F5 `admission-retracted` made the evidence vulnerable, causing the protective treaty — admission-retracted itself is grouped supporting history for this cluster, not a separate active peer.]

Explicit derived relationship (current-state compatibility), traced to ledger:
- REL-07 (DETERMINISTIC_DERIVATION): ST-F6 `archive-protected` (archive.protection = treaty protected) is a current-state constraint that is incompatible with the never-accepted `burn-archive` proposal (ST-P1). This derivation exists in the golden ledger independent of any specific probe's option list; it is presented here as part of Book 4's Decision Map, not as a label on any option text you may separately be given.

History (not current constraints, included for traceability, not as active peers):
- DIR-SC2 `commitment-falsifier` (ACCEPTED, resolved). [REL-03]
- ST-F1 `founding-record` (ACCEPTED, dormant): part of the grouped pressure's supporting history, not separately surfaced as an active peer.
- ST-F5 `admission-retracted` (ACCEPTED, dormant as a separate peer): grouped as causal history explaining ST-F6 (see REL-05 above), not surfaced as its own active peer.
- ST-F4 `public-admission` (ACCEPTED, superseded, then further superseded by ST-F5).
- ST-I1 `broken-lantern` (ACCEPTED, superseded by ST-I2) and ST-I2 `repaired-lantern` (ACCEPTED, irrelevant despite being recent): [REL-08] neither lantern state supports active continuity or the current decision; `repaired-lantern` is recent but explicitly irrelevant (false-recency is excluded, not promoted).

Interpretive (not a hard constraint):
- REL-10 (INTERPRETIVE): thematic tension "official history vs. lived memory" persists via Series pressure; future payoff requires preserving the evidentiary chain (ST-F6) to authenticate the testimony (ST-F2). This is researcher phrasing of accepted material — treat as interpretive context, not canon or hard constraint.

Excluded (not accepted, never enter Decision Map): ST-P1 `burn-archive`, ST-P2 `ally-militia` (PROPOSED NOT ACCEPTED).""",
}


def render_options(options: list[tuple[str, str, str]]) -> str:
    return "\n".join(
        f"- {oid}: {label} — {summary} — tradeoff: {tradeoff}"
        for oid, label, summary, *_ in [
            (o[0], o[1], o[1], o[2]) for o in options
        ]
    )


def render_options_correct(options):
    lines = []
    for option_id, summary, tradeoff in options:
        lines.append(f"- {option_id}: {summary} — tradeoff: {tradeoff}")
    return "\n".join(lines)


def build_packet(probe_id: str, condition: str) -> str:
    p = PROBES[probe_id]
    if condition == "A":
        context_block = "Accepted history and current state (plain facts):\n" + "\n".join(
            f"- {fact}" for fact in p["plain_facts"]
        )
    elif condition == "B":
        context_block = (
            "Current Auteur Series Map (derived by the shipped repeated-map-focus-v2-r1 "
            "selector from the same accepted sources):\n\n" + B_MAPS[str(p["b_book"])]
        )
    elif condition == "C":
        context_block = C_DECISION_MAPS[p["b_book"]]
    else:
        raise ValueError(condition)

    packet = f"""{SYSTEM_ROLE}

Narrative horizon: {p['horizon']}

{context_block}

Current planning intent: {p['intent']}

Question:
{p['question']}

Options:
{render_options_correct(p['options'])}

Task:
{GENERIC_CONTRACT}

{NON_AUTHORITY_REMINDER}"""
    return packet


# ---------------------------------------------------------------------------
# Build all 15 packets, hash them, write to disk
# ---------------------------------------------------------------------------

rows = []
for probe_id in PROBES:
    for condition in ("A", "B", "C"):
        text = build_packet(probe_id, condition)
        h = hashlib.sha256(text.encode()).hexdigest()
        path = PACKET_DIR / f"{probe_id}-{condition}.txt"
        path.write_text(text, encoding="utf-8")
        rows.append(dict(probe_id=probe_id, condition=condition, packet_hash=h, packet_path=str(path)))

# ---------------------------------------------------------------------------
# Schedule: 45 slots = 15 packets x 3 fresh-context repetitions, randomized
# order, opaque IDs not encoding probe/condition/repetition.
# ---------------------------------------------------------------------------

rng = random.Random(RUN_SEED)
slots = []
for row in rows:
    for rep in (1, 2, 3):
        slots.append(dict(probe_id=row["probe_id"], condition=row["condition"], repetition_index=rep,
                           packet_hash=row["packet_hash"], packet_path=row["packet_path"]))
rng.shuffle(slots)

alphabet = string.ascii_uppercase
used_ids = set()


def gen_opaque_id() -> str:
    while True:
        oid = rng.choice(alphabet) + f"{rng.randint(0, 99):02d}"
        if oid not in used_ids:
            used_ids.add(oid)
            return oid


schedule = []
for slot in slots:
    oid = gen_opaque_id()
    schedule.append(dict(opaque_run_id=oid, **slot))

schedule_json = json.dumps(schedule, indent=2, sort_keys=True)
schedule_hash = hashlib.sha256(schedule_json.encode()).hexdigest()

(OUT / "schedule.json").write_text(schedule_json, encoding="utf-8")
(OUT / "schedule_hash.txt").write_text(schedule_hash + "\n", encoding="utf-8")

sealed_map = {s["opaque_run_id"]: dict(hidden_condition_id=s["condition"], probe_id=s["probe_id"],
                                        repetition_index=s["repetition_index"]) for s in schedule}
(OUT / "sealed-condition-map.json").write_text(json.dumps(sealed_map, indent=2, sort_keys=True), encoding="utf-8")

print("RUN_ID", RUN_ID)
print("RUN_SEED", RUN_SEED)
print("packets:", len(rows))
print("schedule slots:", len(schedule))
print("schedule_hash:", schedule_hash)
