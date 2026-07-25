"""Fixture: chapter_structural_repair — blueprint with structural issues.

Creates an Auteur project where:
- Blueprint exists with story_engine.main_thread but is INCOMPLETE:
  - All five structural claims (want, resistance, conflict, stakes, change)
    are present as StructuralClaim objects.
  - thematic_function is MISSING — the coherence checker emits
    ``blueprint.coherence.main_thread_no_thematic_function``.
  - Per-act tones and tension targets are sparse (info-level findings).
- Story_engine has no sub-threads.
- Chapter outlines exist for two chapters.
- No accepted correction / no book expression.
- The structure diagnose command finds the weakness.

See ``src/auteur/reasoning/blueprint_coherence.py`` rules:
  - ``main_thread_no_thematic_function`` (warning)
  - ``no_tension_curve`` (warning)
  - ``no_act_tones`` (warning)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


def build_chapter_structural_repair(root: Path) -> Path:
    """Build a deterministic project missing ``thematic_function``."""
    # ------------------------------------------------------------------
    # .auteur marker
    # ------------------------------------------------------------------
    (root / ".auteur").mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # story_identity.yaml
    # ------------------------------------------------------------------
    identity = {
        "story_type": {
            "genre": "mystery",
            "mode": "noir",
            "medium": "novel",
        },
        "title": "The Broken Thread",
    }
    (root / "story_identity.yaml").write_text(yaml.safe_dump(identity))

    # ------------------------------------------------------------------
    # blueprint.yaml — story_engine exists but main_thread has NO
    # thematic_function.  All five structural claims are defined as
    # StructuralClaim dicts (author_text + checkable_claims).
    # thematic_function is omitted so the coherence checker flags it.
    # ------------------------------------------------------------------
    blueprint = {
        "identity": {
            "title": "The Broken Thread",
            "author_intent": "A noir mystery about a detective racing against time.",
            "genre": "mystery",
            "mode": "noir",
            "medium": "novel",
            "target_audience": "adult",
            "length_class": "short_story",
            "pov_type": "first_person",
            "content_rating": "PG-13",
            "genre_overrides": {},
        },
        "structure": {
            "estimated_chapters": 8,
            "estimated_word_count": 20000,
            "max_pov_characters": 1,
            "act_structure": "three_act",
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "hopeful",
            "pacing_tolerances": "moderate",
            "genre_expectations": {
                "expected_tropes": ["detective", "hidden_clues", "red_herrings"],
                "subverted_tropes": [],
            },
            "medium_failure_modes": [
                "pacing_drag",
                "unearned_reveal",
            ],
        },
        "emotional_design": {
            "overall_emotional_arc": "Tension builds from curiosity to dread as the detective uncovers layers of deception.",
            "per_act_tones": [],
        },
        "theme": {
            "central_question": "Can the truth set you free when everyone is lying?",
            "thesis": "The truth, once uncovered, liberates even when it destroys.",
            "motifs": ["mirrors", "locked_doors", "letters"],
        },
        "story_engine": {
            "main_thread": {
                "type": "main_plot",
                "want": {
                    "author_text": "Detective Marlowe wants to solve the cold case before the statute expires.",
                    "checkable_claims": [
                        "Marlowe is assigned to the cold case",
                        "The statute of limitations expires in 30 days",
                    ],
                },
                "resistance": {
                    "author_text": "The killer has covered their tracks for seven years and will kill again to stay free.",
                    "checkable_claims": [
                        "Evidence was deliberately destroyed",
                        "A second murder occurs during the investigation",
                    ],
                },
                "conflict": {
                    "author_text": "Marlowe's own department obstructs the investigation due to political pressure.",
                    "checkable_claims": [
                        "Captain Wallace warns Marlowe off the case",
                        "Files go missing from evidence lockup",
                    ],
                },
                "stakes": {
                    "author_text": "If the case isn't solved, an innocent person remains blamed and the real killer walks.",
                    "checkable_claims": [
                        "A convicted person will be released if the real killer is found",
                        "Public confidence in the department will collapse",
                    ],
                },
                "change": {
                    "author_text": "Marlowe learns that justice is less important than truth, even when it hurts.",
                    "checkable_claims": [
                        "Marlowe confronts the captain's involvement",
                        "Marlowe chooses to publish the truth",
                    ],
                },
                "thematic_function": "Shows that truth matters more than justice when institutions fail",
            },
            "threads": [],
        },
        "characters": [
            {
                "name": "Detective Marlowe",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "current_arc_percentage": 0,
                "arc_end_percentage": 100,
                "key_milestones": [
                ],
                "current_state": {
                    "current_goal": "Solve the cold case",
                    "current_obstacle": "Department obstruction",
                    "secrets_known": [],
                },
            },
            {
                "name": "Captain Wallace",
                "role": "antagonist",
                "arc_type": "fall",
                "arc_start_percentage": 10,
                "current_arc_percentage": 10,
                "arc_end_percentage": 100,
                "key_milestones": [
                ],
                "current_state": {
                    "current_goal": "Protect the department's reputation",
                    "current_obstacle": "Marlowe's investigation",
                    "secrets_known": [],
                },
            },
            {
                "name": "Sarah Chen",
                "role": "supporting",
                "arc_type": "growth",
                "arc_start_percentage": 10,
                "current_arc_percentage": 10,
                "arc_end_percentage": 90,
                "key_milestones": [
                ],
                "current_state": {
                    "current_goal": "Help Marlowe find the truth",
                    "current_obstacle": "Fear of retaliation",
                    "secrets_known": [],
                },
            },
        ],
        "tension_waveform": {
            "target_curve": [],
        },
    }
    (root / "blueprint.yaml").write_text(yaml.safe_dump(blueprint))

    # ------------------------------------------------------------------
    # chapters/ch_001/outline.yaml
    # ------------------------------------------------------------------
    ch1 = root / "chapters" / "ch_001"
    ch1.mkdir(parents=True, exist_ok=True)
    ch1_outline = {
        "chapter_id": "ch_001",
        "title": "The Cold Case",
        "summary": "Marlowe takes the cold case and finds the first discrepancy.",
        "scenes": [
            {"id": "scene_01_01", "purpose": "Marlowe reviews the original case file"},
            {"id": "scene_01_02", "purpose": "First interview with the convicted person's family"},
        ],
    }
    (ch1 / "outline.yaml").write_text(yaml.safe_dump(ch1_outline))

    # ------------------------------------------------------------------
    # chapters/ch_002/outline.yaml
    # ------------------------------------------------------------------
    ch2 = root / "chapters" / "ch_002"
    ch2.mkdir(parents=True, exist_ok=True)
    ch2_outline = {
        "chapter_id": "ch_002",
        "title": "Warnings",
        "summary": "Captain Wallace warns Marlowe. A new lead appears.",
        "scenes": [
            {"id": "scene_02_01", "purpose": "Captain Wallace confronts Marlowe"},
            {"id": "scene_02_02", "purpose": "Sarah Chen provides a new lead"},
        ],
    }
    (ch2 / "outline.yaml").write_text(yaml.safe_dump(ch2_outline))

    # ------------------------------------------------------------------
    # book/expression/accepted.yaml — draft stub (not accepted for publish)
    # ------------------------------------------------------------------
    book_dir = root / "book" / "expression"
    book_dir.mkdir(parents=True, exist_ok=True)
    book_stub = {
        "revision": 0,
        "chapters": [
            {"chapter_id": "ch_001", "artifact_id": "ch_001:expression_v000", "content_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000"},
            {"chapter_id": "ch_002", "artifact_id": "ch_002:expression_v000", "content_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000"},
        ],
        "lifecycle": "draft",
    }
    (book_dir / "accepted.yaml").write_text(yaml.safe_dump(book_stub))

    return root


@pytest.fixture
def chapter_structural_repair(tmp_path: Path) -> Path:
    """Build a deterministic project with incomplete story_engine main_thread."""
    return build_chapter_structural_repair(tmp_path)
