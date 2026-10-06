#!/usr/bin/env python3
"""Activated #318 F2 bounded-context qualification over The Glass Archive."""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from auteur.beginner.continuation import build_contextual_chapter_plan


def _write_kept(root: Path, index: int, prose: str) -> None:
    chapter = root / "chapters" / f"{index:02d}"
    chapter.mkdir(parents=True, exist_ok=True)
    (chapter / "final.md").write_text(prose, encoding="utf-8")
    (chapter / "outline.yaml").write_text(
        f"chapter_index: {index}\nchapter_summary: accepted Chapter {index} role\n",
        encoding="utf-8",
    )


def run_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        for index in range(1, 6):
            _write_kept(root, index, f"Accepted Chapter {index} prose.")

        chapter_six = root / "chapters" / "06"
        chapter_six.mkdir(parents=True)
        (chapter_six / "outline.yaml").write_text(
            "chapter_index: 6\n"
            "chapter_summary: expose forecasting misuse while preserving origin ambiguity\n"
            "scenes:\n"
            "  - purpose: Nia chooses what can responsibly become public\n"
            "    continuity_constraints:\n"
            "      - Sister Beatrice's convent link supports the public-history choice\n"
            "      - Mara's identity as Nia's older sister is already known\n"
            "      - Tom's strained trust affects collaboration\n"
            "      - The pump disaster was already prevented\n"
            "      - Record provenance remains unresolved\n",
            encoding="utf-8",
        )
        events = [
            {"chapter_index": 1, "summary": "The pump prediction becomes active.", "deltas": {"pump_prediction": "active"}},
            {"chapter_index": 1, "summary": "Nia carries a red umbrella.", "deltas": {"umbrella_color": "red"}},
            {"chapter_index": 2, "summary": "The convent link is accepted.", "deltas": {"convent_link": "accepted"}},
            {"chapter_index": 3, "summary": "Mara is revealed as Nia's older sister.", "deltas": {"mara_identity": "older_sister"}},
            {"chapter_index": 4, "summary": "Tom's trust is strained.", "deltas": {"tom_trust": "strained"}},
            {"chapter_index": 5, "summary": "The pump disaster is prevented.", "deltas": {"pump_status": "prevented"}},
            {"chapter_index": 5, "summary": "Record provenance remains unresolved.", "deltas": {"record_provenance": "unresolved"}},
        ]
        (root / "bible.json").write_text(json.dumps({"events": events}), encoding="utf-8")

        # One compatible, unresolved Chapter-5 update must remain explicit and
        # nonblocking rather than being flattened into accepted state.
        kept = (root / "chapters/05/final.md").read_bytes()
        receipt = root / ".auteur/beginner/reconciliation/5-pending.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(
            json.dumps({
                "canonical": False,
                "chapter_index": 5,
                "chapter_accepted": True,
                "candidate_sha256": hashlib.sha256(kept).hexdigest(),
                "status": "proposal_ready",
                "proposal_items": [{
                    "label": "Forecasting origin",
                    "value": "Keep the ultimate origin unresolved",
                    "status": "proposed",
                    "canonical": False,
                    "target_owner": "realized_state",
                }],
            }),
            encoding="utf-8",
        )

        plan = build_contextual_chapter_plan(root, 6)
        author = plan.context["author_context"]
        fields = set(author["accepted_state"])
        required = {"convent_link", "mara_identity", "tom_trust", "pump_status", "record_provenance"}
        return {
            "claim_class": "mechanical_context_composition",
            "five_prior_chapters_addressable": author["evidence_index"]["accepted_chapter_refs"]
            == [f"chapters/{i:02d}/final.md" for i in range(1, 6)],
            "all_accepted_events_addressable": len(author["evidence_index"]["accepted_event_refs"]) == len(events),
            "old_trivia_omitted_from_generation_context": "umbrella_color" not in fields,
            "required_long_range_dependencies_present": required <= fields,
            "unresolved_accepted_state_preserved": author["accepted_state"]["record_provenance"]["value"] == "unresolved",
            "pending_update_explicit": len(author["pending_updates"]) == 1
            and author["pending_updates"][0]["authority"] == "suggested"
            and author["pending_updates"][0]["blocking"] is False,
            "raw_bible_not_flattened_into_realized_state": "events" not in plan.context["realized_state"],
            "selected_event_count": author["selection"]["accepted_events_selected"],
            "omitted_event_count": author["selection"]["accepted_events_omitted"],
            "selection_mode": author["selection"]["mode"],
        }


def main() -> int:
    print(json.dumps(run_probe(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
