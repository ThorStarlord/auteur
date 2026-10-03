#!/usr/bin/env python3
"""Adversarial synthetic evidence probe for the Beginner author experience.

This probe deliberately establishes only repository/agent-answerable claims.
It does not infer human preference, joy, ownership, cognitive load, or desire
to continue.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
import tempfile
from pathlib import Path
from typing import Any

from auteur.beginner.post_draft import project_draft_review, project_next_chapter_context
from auteur.llm import LLMResponse
from auteur.quick_draft import (
    prepare_quick_draft_shape_handoff,
    project_quick_draft_discoveries,
    run_quick_draft,
    save_quick_draft_revision,
)


ROOT = Path(__file__).resolve().parents[1]


class FakeDraftLLM:
    """Deterministic drafting facade for authority/workflow stress only."""

    def __init__(self) -> None:
        self.requests: list[Any] = []

    def complete(self, request: Any) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(
            text=(
                "# Chapter 1\n\n"
                "Vance watches Miller carefully.\n\n"
                "\"You remember the knife,\" Vance says."
            ),
            input_tokens=80,
            output_tokens=28,
        )


def _mechanical_entry_probe() -> dict[str, Any]:
    namespace = runpy.run_path(str(ROOT / "scripts" / "quick_draft_product_probe.py"))
    comparison = namespace["mechanical_comparison"]()
    conditions = {
        item["condition"]: item for item in comparison["conditions"]
    }
    return {
        "claim_class": "mechanical",
        "old_visible_interactions_to_prose": conditions["A_pre_compression"][
            "visible_interactions_to_prose"
        ],
        "compressed_visible_interactions_to_prose": conditions["B_compressed"][
            "visible_interactions_to_prose"
        ],
        "quick_draft_visible_interactions_to_prose": conditions["C_quick_draft"][
            "visible_interactions_to_prose"
        ],
        "quick_draft_explicit_pre_prose_acceptance": conditions["C_quick_draft"][
            "explicit_pre_prose_acceptance"
        ],
        "warning": comparison["warning"],
    }


def _discovery_writer_probe() -> dict[str, Any]:
    premise = (
        "Detective Miller discovers that every witness remembers the same murder "
        "differently."
    )
    first_scene = (
        "Miller questions Suspect Vance, who describes Miller himself committing "
        "the murder."
    )
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        llm = FakeDraftLLM()
        result = run_quick_draft(
            premise,
            first_scene,
            project_root=root,
            llm=llm,
            provider_label="synthetic/fake",
        )
        scaffold = result.scaffold_path.read_text(encoding="utf-8")
        no_accepted_root_artifacts = all(
            not (root / path).exists()
            for path in (
                "story_identity.yaml",
                "blueprint.yaml",
                "bible.json",
                "chapters/01/final.md",
            )
        )

        edited = (
            "At the abandoned seaside convent, Sister Beatrice tells Detective Miller "
            "that Suspect Vance slept there."
        )
        save_quick_draft_revision(root, result.session_id, edited)
        discoveries = project_quick_draft_discoveries(root, result.session_id)[
            "discoveries"
        ]
        sister = next(
            item for item in discoveries if item.get("value") == "Sister Beatrice"
        )
        handoff = prepare_quick_draft_shape_handoff(
            root,
            result.session_id,
            "synthetic-workspace",
            [sister],
        )
        payload = __import__("yaml").safe_load(handoff.read_text(encoding="utf-8"))
        selected_values = [
            str(item.get("value", "")) for item in payload["selected_discoveries"]
        ]

        return {
            "claim_class": "mechanical",
            "draft_generated_before_acceptance": result.draft_path.is_file(),
            "one_generation_request": len(llm.requests) == 1,
            "scaffold_explicitly_provisional": "status: inferred_provisional" in scaffold,
            "no_accepted_root_artifacts": no_accepted_root_artifacts,
            "unplanned_character_detected": any(
                item.get("value") == "Sister Beatrice" for item in discoveries
            ),
            "unplanned_place_detected": any(
                "abandoned seaside convent" in str(item.get("value", "")).lower()
                for item in discoveries
            ),
            "only_explicitly_selected_discovery_carried": (
                selected_values == ["Sister Beatrice"]
            ),
            "handoff_is_noncanonical": payload["canonical"] is False,
        }


def _ambiguity_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        llm = FakeDraftLLM()
        result = run_quick_draft(
            "Someone wakes with a key that should not exist.",
            "They try it on the only locked door in the apartment.",
            project_root=root,
            llm=llm,
            provider_label="synthetic/fake",
        )
        import yaml

        scaffold = yaml.safe_load(result.scaffold_path.read_text(encoding="utf-8"))
        scene = scaffold["inferred_scaffolding"]["scene_plan"]
        return {
            "claim_class": "mechanical",
            "pov_left_open": scene["pov_character"] == "",
            "location_left_open": scene["location"] == "",
            "story_setup_not_accepted": scaffold["authority"]["story_setup"]
            == "not_accepted",
            "structure_not_accepted": scaffold["authority"]["structure"]
            == "not_accepted",
        }


def _chaotic_writer_review_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        chapter = root / "chapters" / "01"
        chapter.mkdir(parents=True)
        original = "Detective Miller questions Suspect Vance."
        draft = chapter / "draft_v1.md"
        draft.write_text(original, encoding="utf-8")
        original_hash = hashlib.sha256(draft.read_bytes()).hexdigest()
        (chapter / "draft_v1.meta.json").write_text(
            json.dumps({"candidate_sha256": original_hash}),
            encoding="utf-8",
        )
        (chapter / "validation_v1.json").write_text(
            json.dumps(
                {
                    "findings": [
                        {
                            "severity": "ERROR",
                            "message": "old review should become stale",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        draft.write_text(
            (
                "At the abandoned seaside convent, Sister Beatrice tells Detective "
                "Miller that Vance was never at the precinct."
            ),
            encoding="utf-8",
        )
        review = project_draft_review(root, 1)
        values = [str(item.get("value", "")) for item in review.creative_discoveries]
        return {
            "claim_class": "mechanical",
            "review_stale_after_edit": review.review_stale,
            "stale_findings_not_presented_as_current": not review.blocking_findings
            and not review.warnings,
            "reconciliation_available": review.reconciliation_available,
            "creative_discovery_detected": any(
                value == "Sister Beatrice"
                or "abandoned seaside convent" in value.lower()
                for value in values
            ),
            "recommended_action_is_story_language": (
                "draft changed after review"
                in review.recommended_next_action.lower()
            ),
        }


def _longitudinal_context_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        for index, prose in (
            (1, "Miller learns that Vance knew Sister Beatrice."),
            (2, "Sister Beatrice takes Miller to the seaside convent."),
        ):
            chapter = root / "chapters" / f"{index:02d}"
            chapter.mkdir(parents=True, exist_ok=True)
            (chapter / "final.md").write_text(prose, encoding="utf-8")
        bible = {
            "characters": [
                {"name": "Sister Beatrice", "status": "active"},
            ],
            "events": [
                {
                    "chapter_index": 2,
                    "what": "Miller reaches the seaside convent",
                }
            ],
        }
        (root / "bible.json").write_text(json.dumps(bible), encoding="utf-8")
        context = project_next_chapter_context(root, 3)
        return {
            "claim_class": "mechanical",
            "prior_accepted_chapters_visible": context["prior_accepted_chapters"]
            == [1, 2],
            "prior_chapter_refs_visible": len(context["prior_chapter_refs"]) == 2,
            "realized_state_visible": context["realized_state"] == bible,
            "finding": (
                "Current context projection can expose accepted prior chapters and "
                "realized state. This does not establish relevance selection, "
                "six-Chapter coherence, or human-perceived continuity value."
            ),
        }


def _front_door_vocabulary_probe() -> dict[str, Any]:
    text = "\n".join(
        (
            (ROOT / "src" / "auteur" / "beginner" / "browser" / "index.html").read_text(
                encoding="utf-8"
            ),
            (ROOT / "src" / "auteur" / "beginner" / "browser" / "app.js").read_text(
                encoding="utf-8"
            ),
        )
    ).lower()
    terms = ("canon", "canonical", "provenance", "reconciliation", "candidate")
    return {
        "claim_class": "static_surface_audit",
        "raw_source_occurrences": {term: text.count(term) for term in terms},
        "warning": (
            "Source occurrence is not equivalent to primary-screen visibility or "
            "human comprehension. Use this only to flag terminology for inspection."
        ),
    }


def run_probe() -> dict[str, Any]:
    return {
        "schema": "beginner_adversarial_agent_simulation_v1",
        "evidence_type": "SYNTHETIC_AGENT_AND_REPOSITORY_EVIDENCE",
        "human_participants": 0,
        "personas": [
            "discovery_writer",
            "planner",
            "uncertain_beginner",
            "chaotic_writer",
            "change_my_mind_writer",
            "minimalist_llm_baseline_user",
        ],
        "probes": {
            "entry_flow": _mechanical_entry_probe(),
            "discovery_writer": _discovery_writer_probe(),
            "ambiguity": _ambiguity_probe(),
            "chaotic_writer_review": _chaotic_writer_review_probe(),
            "longitudinal_context": _longitudinal_context_probe(),
            "front_door_vocabulary": _front_door_vocabulary_probe(),
        },
        "agent_hypotheses": {
            "shape_first_vs_write_first": (
                "The evidence supports retaining two tempos rather than declaring one "
                "universal winner: write-first minimizes pre-prose commitment while "
                "shape-first can trade extra interaction for earlier interpretation."
            ),
            "human_study_scope": (
                "Human testing should be reserved for unresolved human-subjective "
                "claims that remain decision-changing after synthetic and provider "
                "evidence are exhausted."
            ),
        },
        "not_established": [
            "human preference",
            "felt ownership",
            "joy",
            "frustration",
            "cognitive fatigue",
            "prose taste",
            "desire to continue",
            "market value",
            "real-provider quality",
            "six-chapter longitudinal coherence",
        ],
        "provider_dependent_next_probe": (
            "Run #310 and the blind Auteur-vs-general-LLM longitudinal comparison "
            "when provider credentials are available."
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
