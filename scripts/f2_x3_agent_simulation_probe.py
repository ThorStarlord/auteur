#!/usr/bin/env python3
"""Integrated F2/X3 coding-agent stress preflight (v2).

Reuses the historical preflight's Glass Archive fixture, but reports the
currently integrated bounded context and Browser orientation contracts. It adds
one adversarial paraphrase case. No human/provider/full-Book claims are made.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from auteur.beginner.book_progress import BookProgressProjection
from auteur.beginner.author_context import compose_author_context
from auteur.beginner.continuation import build_contextual_chapter_plan


ROOT = Path(__file__).resolve().parents[1]


def _write_chapter(
    root: Path,
    index: int,
    *,
    role: str,
    prose: str,
    expected_state: dict[str, Any] | None = None,
) -> None:
    chapter = root / "chapters" / f"{index:02d}"
    chapter.mkdir(parents=True, exist_ok=True)
    (chapter / "final.md").write_text(prose, encoding="utf-8")
    lines = [
        f"chapter_index: {index}",
        f"chapter_summary: {role}",
    ]
    if expected_state:
        lines.append("expected_state:")
        for key, value in expected_state.items():
            lines.append(f"  {key}: {value}")
    (chapter / "outline.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _accepted_history_and_precedence_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        _write_chapter(
            root,
            1,
            role="verify the pump prediction",
            prose="Nia verifies that the seawall pump is genuinely at risk.",
            expected_state={"pump_status": "at_risk"},
        )
        _write_chapter(
            root,
            2,
            role="follow the archive trail",
            prose="Nia learns that the Lantern may be protecting the records.",
            expected_state={"lantern_role": "enemy"},
        )
        chapter_three = root / "chapters" / "03"
        chapter_three.mkdir(parents=True)
        (chapter_three / "outline.yaml").write_text(
            "chapter_index: 3\n"
            "chapter_summary: test the uneasy alliance without restoring the old enemy plan\n",
            encoding="utf-8",
        )
        bible = {
            "events": [
                {
                    "chapter_index": 1,
                    "summary": "The pump threat is real.",
                    "deltas": {"pump_status": "at_risk"},
                },
                {
                    "chapter_index": 2,
                    "summary": "Mara may be an ally rather than the enemy.",
                    "deltas": {"lantern_role": "possible_ally"},
                },
            ]
        }
        (root / "bible.json").write_text(json.dumps(bible), encoding="utf-8")

        prior_outline = root / "chapters" / "02" / "outline.yaml"
        before = prior_outline.read_text(encoding="utf-8")
        plan = build_contextual_chapter_plan(root, 3)
        after = prior_outline.read_text(encoding="utf-8")

        return {
            "claim_class": "mechanical",
            "prior_accepted_chapters_visible": plan.context.get("prior_accepted_chapters") == [1, 2],
            "accepted_prior_state_count": len(plan.context.get("accepted_prior_state", [])),
            "accepted_change_visible": any(
                event.get("deltas", {}).get("lantern_role") == "possible_ally"
                for event in plan.context.get("accepted_prior_state", [])
            ),
            "obsolete_plan_reported_as_divergence": any(
                item.get("field") == "lantern_role"
                and item.get("planned") == "enemy"
                and item.get("accepted") == "possible_ally"
                for item in plan.divergences
            ),
            "historical_plan_not_silently_rewritten": before == after,
            "next_chapter_role_preserved": plan.intended_role
            == "test the uneasy alliance without restoring the old enemy plan",
        }


def _six_chapter_context_relevance_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        events = [
            (1, "pump_status", "at_risk"),
            (1, "umbrella_color", "red"),
            (2, "convent_link", "accepted"),
            (3, "mara_identity", "known"),
            (4, "tom_trust", "strained"),
            (5, "record_provenance", "unresolved"),
        ]
        for index in range(1, 6):
            _write_chapter(
                root,
                index,
                role=f"chapter {index} accepted role",
                prose=f"Accepted Chapter {index} prose.",
            )
        chapter_six = root / "chapters" / "06"
        chapter_six.mkdir(parents=True)
        (chapter_six / "outline.yaml").write_text(
            "chapter_index: 6\n"
            "chapter_summary: resolve forecasting misuse while preserving origin ambiguity\n",
            encoding="utf-8",
        )
        payload = {
            "events": [
                {
                    "chapter_index": chapter,
                    "summary": f"{field} becomes {value}",
                    "deltas": {field: value},
                }
                for chapter, field, value in events
            ]
        }
        (root / "bible.json").write_text(json.dumps(payload), encoding="utf-8")

        plan = build_contextual_chapter_plan(root, 6)
        prior_state = plan.context.get("accepted_prior_state", [])
        fields = {
            key
            for event in prior_state
            for key in (event.get("deltas") or {}).keys()
        }
        return {
            "claim_class": "mechanical",
            "five_prior_accepted_chapters_visible": plan.context.get("prior_accepted_chapters")
            == [1, 2, 3, 4, 5],
            "all_prior_events_exposed": len(prior_state) == len(events),
            "clearly_low_value_detail_still_exposed": "umbrella_color" in fields,
            "relevance_filter_demonstrated": (
                "umbrella_color" not in fields
                and len(prior_state) < len(events)
                and plan.context.get("author_context", {}).get("selection", {}).get("mode")
                == "bounded_recency_plus_current_plan_overlap"
            ),
            "full_evidence_index_preserved": (
                len(plan.context.get("author_context", {}).get("evidence_index", {}).get(
                    "accepted_event_refs", []
                )) == len(events)
            ),
            "finding": (
                "The integrated context selects a bounded recent/lexically relevant "
                "subset and preserves omitted source references. This does not "
                "establish full six-Chapter semantic recall or provider behavior."
            ),
        }


def _paraphrased_dependency_probe() -> dict[str, Any]:
    """A Chapter-6 dependency may be causal without lexical overlap.

    The *simulated* author asks for independent harbor testimony. The accepted
    Chapter-2 source describes Sister Beatrice's convent ledger instead.
    Relevance by overlapping words alone cannot infer their relationship.
    """
    context = compose_author_context(
        chapter_index=6,
        role="Use independent testimony before public disclosure",
        role_ref="chapters/06/outline.yaml",
        current_outline={
            "chapter_index": 6,
            "chapter_summary": "Rely on independent harbor witnesses before publication.",
            "scenes": [{
                "summary": "Determine which outside testimony deserves public disclosure.",
            }],
        },
        accepted_events=[{
            "chapter_index": 2,
            "summary": "Sister Beatrice identifies the convent ledger.",
            "deltas": {"convent_evidence": "critical"},
        }],
        accepted_expressions=[{
            "chapter_index": 2,
            "source_ref": "chapters/02/final.md",
            "text": "Sister Beatrice catalogued sealed convent ledgers.",
        }],
        prior_chapter_refs=[{"chapter_index": 2, "path": "chapters/02/final.md"}],
        structure_refs=["chapters/06/outline.yaml"],
    )
    index = context["evidence_index"]
    omitted_event = "bible.json#/events/0" in index["omitted_accepted_event_refs"]
    omitted_expression = "chapters/02/final.md" in index["omitted_accepted_expression_refs"]
    return {
        "claim_class": "source_derived_adversarial_scenario",
        "author_intent": "Use independent harbor testimony",
        "accepted_source": "Sister Beatrice's convent ledger",
        "older_accepted_event_omitted_from_generation_context": omitted_event,
        "older_accepted_prose_omitted_from_generation_context": omitted_expression,
        "references_remain_indexed": (
            "bible.json#/events/0" in index["accepted_event_refs"]
            and "chapters/02/final.md" in index["accepted_expression_refs"]
        ),
        "risk": "LEXICAL_PARAPHRASE_DEPENDENCY_MISS_POSSIBLE",
        "not_established": "That a real Chapter-6 generation forgets the source",
    }


def _x3_book_orientation_probe() -> dict[str, Any]:
    fields = set(BookProgressProjection.model_fields)
    html = (ROOT / "src" / "auteur" / "beginner" / "browser" / "index.html").read_text(
        encoding="utf-8"
    )
    app = (ROOT / "src" / "auteur" / "beginner" / "browser" / "app.js").read_text(
        encoding="utf-8"
    )
    required_orientation = {
        "current_chapter",
        "recent_changes",
        "pending_updates",
        "next_story_action",
    }
    missing = sorted(required_orientation - fields)
    surface_present = all(name in app for name in (
        "progress.current_chapter", "progress.recent_changes",
        "progress.pending_updates", "progress.next_story_action",
    ))
    primary = '<section aria-label="Book orientation"' in html
    progressive_details = '<details aria-label="Technical Book details"' in html
    return {
        "claim_class": "mechanical_surface_contract",
        "book_progress_fields": sorted(fields),
        "missing_persistent_orientation_fields": missing,
        "author_orientation_surface_present": surface_present,
        "book_orientation_is_primary": primary,
        "technical_details_progressively_disclosed": progressive_details,
        "current_chapter_query_helper_exists": "function currentChapterFromQuery()" in app,
        "whole_book_surface_is_advanced_details": "Advanced: whole-book details" in html,
        "surface_emphasizes_technical_next_command": "Next technical action:" in html,
        "hardcoded_chapter_one_post_draft_heading": "<h3>Chapter 1</h3>" in html,
        "authority_remains_derived": (
            BookProgressProjection.model_fields["authority_status"].default
            == "DERIVED / NOT CANON"
        ),
        "mechanical_x3_gap": (
            bool(missing) or not surface_present or not primary or not progressive_details
        ),
        "finding": (
            "The integrated Browser consumes the existing orientation fields in a "
            "primary, read-only Book surface. Human comprehension and full re-entry "
            "remain separate empirical questions."
        ),
    }


def run_probe() -> dict[str, Any]:
    history = _accepted_history_and_precedence_probe()
    relevance = _six_chapter_context_relevance_probe()
    paraphrase = _paraphrased_dependency_probe()
    x3 = _x3_book_orientation_probe()

    f2_mechanics_pass = all(
        [
            history["prior_accepted_chapters_visible"],
            history["accepted_change_visible"],
            history["obsolete_plan_reported_as_divergence"],
            history["historical_plan_not_silently_rewritten"],
            history["next_chapter_role_preserved"],
        ]
    )

    return {
        "schema": "f2_x3_agent_preflight_v2",
        "evidence_type": "SYNTHETIC_AGENT_AND_REPOSITORY_EVIDENCE",
        "human_participants": 0,
        "provider_calls": 0,
        "source_fixture": "The Glass Archive",
        "probes": {
            "accepted_history_and_precedence": history,
            "six_chapter_context_relevance": relevance,
            "paraphrased_dependency": paraphrase,
            "x3_book_orientation": x3,
        },
        "disposition": {
            "f2_accepted_history_precedence": "PASS" if f2_mechanics_pass else "FAIL",
            "f2_full_frontier": "NOT_QUALIFIED",
            "f2_context_relevance": (
                "BOUNDED_SELECTION_PRESENT"
                if relevance["relevance_filter_demonstrated"]
                and relevance["full_evidence_index_preserved"]
                else "NOT_ESTABLISHED"
            ),
            "f2_paraphrased_dependency": (
                "LEXICAL_MISS_POSSIBLE"
                if paraphrase["older_accepted_event_omitted_from_generation_context"]
                and paraphrase["older_accepted_prose_omitted_from_generation_context"]
                and paraphrase["references_remain_indexed"]
                else "NO_MISS_OBSERVED"
            ),
            "x3_mechanical_projection": (
                "GAP_ESTABLISHED" if x3["mechanical_x3_gap"] else "PRESENT_IN_SOURCE"
            ),
        },
        "current_first_failure_candidates": [
            (
                "F2: inspect meaning-equivalent older accepted facts omitted by lexical "
                "selection; do not infer that raw source references alone make the "
                "fact available in generation-facing content."
            ),
            (
                "X3: try actual re-entry and determine whether the integrated "
                "orientation helps a simulated author without backend coaching."
            ),
        ],
        "not_established": [
            "real-provider intent fidelity or latency",
            "human comprehension or preference",
            "felt ownership or bureaucracy",
            "artistic quality",
            "reader value",
            "full six-Chapter end-to-end F2 pass",
            "comparative superiority over Markdown plus a capable LLM",
        ],
        "gate_rule": (
            "F2/X3 implementation is integrated; this source-level simulation "
            "does not replace an actual six-Chapter run or host-agent dogfood."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = run_probe()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
