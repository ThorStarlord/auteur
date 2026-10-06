#!/usr/bin/env python3
"""Verify that F2 author context reaches the Bard generation request."""
from __future__ import annotations

from pathlib import Path

from auteur.bard import render_bard_prompt
from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint


ROOT = Path(__file__).resolve().parents[1]


def run_probe() -> dict[str, bool]:
    blueprint = StoryBlueprint.from_yaml(ROOT / "examples" / "sample_blueprint.yaml")
    bible = StoryBible(ROOT / ".auteur" / "f2-prompt-probe-bible.json")
    context = {
        "schema": "beginner_author_context_v1",
        "current_plan": {"chapter_index": 6, "role": "Converge the accepted Book", "authority": "planning_context"},
        "accepted_expression": [{
            "chapter_index": 2,
            "text": "Sister Beatrice connects the convent to the forecasting office.",
            "source_ref": "chapters/02/final.md",
            "authority": "accepted_expression",
        }],
        "accepted_state": {
            "record_provenance": {
                "value": "unresolved",
                "source_ref": "bible.json#/events/6",
                "chapter_index": 5,
                "authority": "accepted",
            }
        },
        "pending_updates": [{
            "summary": "Forecasting origin: keep unresolved",
            "source_ref": ".auteur/beginner/reconciliation/5.json#/proposal_items/0",
            "chapter_index": 5,
            "authority": "suggested",
            "blocking": False,
        }],
        "uncertainty": [],
    }
    outline = {
        "scope": "chapter",
        "chapter_index": 6,
        "chapter_summary": "Converge the accepted Book.",
        "scenes": [{"scene_id": "s1", "pov_character": "Kael", "summary": "Make the final evidence choice."}],
    }
    _, user = render_bard_prompt(
        outline=outline,
        bible=bible,
        blueprint=blueprint,
        chapter_index=6,
        prior_draft=None,
        findings=None,
        author_context=context,
    )
    return {
        "author_context_section_present": "AUTHOR CONTEXT — PROVENANCE PRESERVED" in user,
        "accepted_expression_present": "Sister Beatrice" in user and '"authority": "accepted_expression"' in user,
        "accepted_state_present": '"record_provenance"' in user and '"authority": "accepted"' in user,
        "suggested_update_distinguished": '"authority": "suggested"' in user,
        "promotion_warning_present": "Do not promote Suggested or Needs-attention" in user,
    }


def main() -> int:
    result = run_probe()
    print(result)
    return 0 if all(result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
