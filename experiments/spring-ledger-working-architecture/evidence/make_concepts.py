"""Write the five provisional concept files recorded in the disposable Studio canvas.

Each concept is agent-proposed, reversible and status provisional. None is author-declared.
Usage: python make_concepts.py <package_dir>
"""
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1]) / "evidence" / "concepts"
out.mkdir(parents=True, exist_ok=True)
concepts = {
    "01-hollow-gate.json": {
        "name": "Hollow Gate",
        "definition": "The sluice that divides the high cistern's release between the upper and lower channels. Its schedule is set by the Gate Table from the gauge.",
        "motivating_story_use": "Arc IV Conflict B (Books 21-22) and the Book 30 routing of the Long Return both need one physical point where two practices draw on the same outflow.",
        "why_existing_concepts_insufficient": "The original names the cistern, the channels and the lower gate at Harrow Lowe, but not one point where a schedule splits release between them.",
        "related_concepts": ["High cistern", "Lower channels", "Gate Table", "Balance Stones"],
        "proposed_relations": ["The Gate Table sets its schedule", "Release through it draws the high cistern down"],
        "compatibility_concerns": ["Its acceptance as a world element is author-reserved", "Its physics must not contradict the Source's balance rule"],
        "status": "provisional",
    },
    "02-gate-table.json": {
        "name": "Gate Table",
        "definition": "A rotating body formed in Book 22 that sets the Hollow Gate's schedule from the gauge. It has seats for each practice and one seat drawn by lot. It holds no record, no shares and no authority over any practice.",
        "motivating_story_use": "Separates schedule from record after Conflict B; the first coordinating body between communities.",
        "why_existing_concepts_insufficient": "The Council schedules the Turn and the Reading Hall keeps the record, so neither can coordinate two practices at one outflow without taking the other's role.",
        "related_concepts": ["Hollow Gate", "Terrace Council", "Reading Hall"],
        "proposed_relations": ["Sets the Hollow Gate schedule", "Publishes nothing; the Reading Hall publishes the gauge"],
        "compatibility_concerns": ["Its acceptance as a world element is author-reserved", "Under the binding finale alternative its seats are lot-drawn and its authority is time-limited"],
        "status": "provisional",
    },
    "03-harrow-lowe-gate.json": {
        "name": "Harrow Lowe lower gate",
        "definition": "The lower gate at Harrow Lowe, which passes lowland overflow beyond the orchard terrace. The original places the Mill Compact at it. The operating arrangement is an assumption: the Compact's factor keeps the gate under the Book 6 settlement.",
        "motivating_story_use": "The lowland outlet that a Book 30 surge can use instead of the orchard terrace.",
        "why_existing_concepts_insufficient": "The Hollow Gate is inside the valley, and the lowland towns have no arc, so nothing in the candidate can pass overflow to the lowland.",
        "related_concepts": ["Mill Compact", "Orchard terrace", "Lowland plots"],
        "proposed_relations": ["Passes overflow onward to the lowland plots when open"],
        "compatibility_concerns": ["Inherited from the original and absent from the candidate: it must be added before any use in a candidate", "Its operation is an unestablished assumption"],
        "status": "provisional",
    },
    "04-compact-labour-contribution.json": {
        "name": "Compact grain-labour",
        "definition": "The Mill Compact pays grain for hired lowland labour, capped at a fixed number per window. The contribution is owed only under a binding finale alternative, and it is voluntary otherwise.",
        "motivating_story_use": "The only lever on lowland draw, which carries no return labour.",
        "why_existing_concepts_insufficient": "Purchased draw owes no labour under the original's Book 6 settlement, so nothing currently ties the lowland to the valley's labour.",
        "related_concepts": ["Mill Compact", "Long Rota", "Ratified trigger"],
        "proposed_relations": ["Owed under Alternative B or C; voluntary under A"],
        "compatibility_concerns": ["The Compact's settlement is author-reserved", "The cap is an illustrative value, not canon"],
        "status": "provisional",
    },
    "05-book-15-surfeit.json": {
        "name": "Book 15 surfeit mechanism",
        "definition": "The construction's assumption that the Book 15 trial's uncounted return exceeded the draw the Turn counted, so the surplus showed in the high cistern. Surfeit is too much return, or stored water with no draw.",
        "motivating_story_use": "Explains why the trial's cost fell on the high cistern, which the Book 22 Gate Table then inherits.",
        "why_existing_concepts_insufficient": "The original names the cost but not its mechanism.",
        "related_concepts": ["Unmeasured Return", "Surfeit", "Stewardship tally"],
        "proposed_relations": ["Makes the trial's cost a Source consequence, not a Ledger one"],
        "compatibility_concerns": ["Must not be read as release causing surfeit: release draws the cistern down", "The author may reject it"],
        "status": "provisional",
    },
}
for name, doc in concepts.items():
    (out / name).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("concept files:", len(concepts))
