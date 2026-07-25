"""Fixture: multi_decision_commitment — multiple open decisions and planning state.

Creates an Auteur project where:
- Complete blueprint with full story_engine.
- Multiple open narrative decisions in the decision workspace
  (``.auteur/decision/snapshots/`` with JSON snapshots).
- Candidate simulation state exists (``.auteur/simulation/``).
- Planning state exists (``.auteur/planning/`` with snapshots and latest pointer).
- Chapter outlines exist.
- Decision entries have different statuses: open / needs_candidate / stale.

Decision workspace follows the ``DecisionStore`` storage layout from
``src/auteur/decision/persistence.py``::

    .auteur/decisions/
        snapshots/<decision_id>.json
        latest/latest.json
        lineage/<lineage_root>.json

Simulation state follows ``SimulationStore`` layout::

    .auteur/simulation/
        baselines/
        scenarios/
        comparisons/
        latest.yaml
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml


def _iso() -> str:
    """Return a deterministic timestamp."""
    return "2026-07-25T12:00:00+00:00"


def build_multi_decision_commitment(root: Path) -> Path:
    """Build a deterministic project with multiple open decisions and simulation state."""
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
        "title": "Forking Paths",
    }
    (root / "story_identity.yaml").write_text(yaml.safe_dump(identity))

    # ------------------------------------------------------------------
    # blueprint.yaml — complete
    # ------------------------------------------------------------------
    blueprint = {
        "identity": {
            "title": "Forking Paths",
            "author_intent": "A noir mystery exploring the cost of choices in police work.",
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
            "estimated_chapters": 6,
            "estimated_word_count": 15000,
            "max_pov_characters": 1,
            "act_structure": "three_act",
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "hopeful",
            "pacing_tolerances": "moderate",
            "genre_expectations": {
                "expected_tropes": ["detective", "hidden_clues"],
                "subverted_tropes": [],
            },
            "medium_failure_modes": ["pacing_drag"],
        },
        "emotional_design": {
            "overall_emotional_arc": "A journey from confusion to clarity as decisions compound.",
            "per_act_tones": [
                {"act_index": 1, "label": "Act One", "tone": "curious and uncertain"},
                {"act_index": 2, "label": "Act Two", "tone": "mounting tension and doubt"},
                {"act_index": 3, "label": "Act Three", "tone": "clarity through sacrifice"},
            ],
        },
        "theme": {
            "central_question": "Which path leads to justice when every choice has a cost?",
            "thesis": "Justice emerges not from perfect choices but from commitment to a chosen path.",
            "motifs": ["crossroads", "keys", "doors"],
        },
        "story_engine": {
            "main_thread": {
                "type": "main_plot",
                "want": {
                    "author_text": "Inspector Reed must identify the murderer before they strike again.",
                    "checkable_claims": ["Reed is assigned to the murder case", "A second victim is found"],
                },
                "resistance": {
                    "author_text": "The killer is methodical, leaving false trails.",
                    "checkable_claims": ["Fingerprints point to an innocent person", "Alibis are fabricated"],
                },
                "conflict": {
                    "author_text": "Reed must choose between two competing theories of the crime.",
                    "checkable_claims": ["Theory A implicates the business partner", "Theory B implicates the spouse"],
                },
                "stakes": {
                    "author_text": "The wrong choice lets the real killer walk free forever.",
                    "checkable_claims": ["Statute of limitations is near", "Public pressure demands an arrest"],
                },
                "change": {
                    "author_text": "Reed learns that conviction without certainty is not justice.",
                    "checkable_claims": ["Reed refuses to arrest on weak evidence", "Reed stakes career on the truth"],
                },
                "thematic_function": "The central question of choosing is dramatized through Reed's investigation fork.",
            },
            "threads": [
                {
                    "name": "Department politics",
                    "type": "political",
                    "want": {
                        "author_text": "Internal affairs investigates the department's handling of the case.",
                        "checkable_claims": ["IA opens an inquiry", "Captain pressures Reed"],
                    },
                    "resistance": {
                        "author_text": "The department closes ranks to protect itself.",
                        "checkable_claims": ["Witnesses recant", "Records disappear"],
                    },
                    "conflict": {
                        "author_text": "Reed must decide whether to cooperate with IA.",
                        "checkable_claims": ["IA offers immunity", "Colleagues accuse Reed of betrayal"],
                    },
                    "stakes": {
                        "author_text": "Reed's career and the case outcome hang in the balance.",
                        "checkable_claims": ["Promotion is on hold", "Case could be dismissed"],
                    },
                    "change": {
                        "author_text": "Reed learns that institutional reform is necessary.",
                        "checkable_claims": ["Reed testifies against the captain", "New procedures are adopted"],
                    },
                    "supports_main_by": ["complicates", "mirrors"],
                    "thematic_function": "The department subplot mirrors the main choice-theme at an institutional scale.",
                },
            ],
        },
        "characters": [
            {
                "name": "Inspector Reed",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
                "current_arc_percentage": 0,
                "key_milestones": [
                    {"at_percentage": 10, "description": "Takes the case"},
                    {"at_percentage": 40, "description": "Discovers two competing theories"},
                    {"at_percentage": 80, "description": "Makes the decisive choice"},
                ],
                "current_state": {
                    "current_goal": "Solve the murder case",
                    "current_obstacle": "Competing theories",
                    "secrets_known": [],
                },
            },
            {
                "name": "Captain Graves",
                "role": "antagonist",
                "arc_type": "fall",
                "arc_start_percentage": 10,
                "arc_end_percentage": 100,
                "current_arc_percentage": 10,
                "key_milestones": [
                    {"at_percentage": 20, "description": "Pressures Reed for quick arrest"},
                    {"at_percentage": 60, "description": "Destroys evidence"},
                ],
                "current_state": {
                    "current_goal": "Protect the department",
                    "current_obstacle": "Reed's integrity",
                    "secrets_known": [],
                },
            },
            {
                "name": "Detective Park",
                "role": "supporting",
                "arc_type": "growth",
                "arc_start_percentage": 10,
                "arc_end_percentage": 90,
                "current_arc_percentage": 10,
                "key_milestones": [
                    {"at_percentage": 15, "description": "Voices Theory A"},
                    {"at_percentage": 50, "description": "Discovers flaw in own theory"},
                ],
                "current_state": {
                    "current_goal": "Find the truth",
                    "current_obstacle": "Lack of evidence",
                    "secrets_known": [],
                },
            },
        ],
        "tension_waveform": {
            "target_curve": [
                {"chapter_index": 1, "score": 3, "label": "inciting_incident"},
                {"chapter_index": 3, "score": 6, "label": "midpoint_fork"},
                {"chapter_index": 6, "score": 9, "label": "climax"},
            ],
        },
    }
    (root / "blueprint.yaml").write_text(yaml.safe_dump(blueprint))

    # ------------------------------------------------------------------
    # chapters/ — outlines
    # ------------------------------------------------------------------
    ch1 = root / "chapters" / "ch_001"
    ch1.mkdir(parents=True, exist_ok=True)
    (ch1 / "outline.yaml").write_text(yaml.safe_dump({
        "chapter_id": "ch_001",
        "title": "The Body",
        "summary": "A body is found. Reed is assigned.",
        "scenes": [{"id": "scene_01_01", "purpose": "Crime scene investigation"}],
    }))

    ch2 = root / "chapters" / "ch_002"
    ch2.mkdir(parents=True, exist_ok=True)
    (ch2 / "outline.yaml").write_text(yaml.safe_dump({
        "chapter_id": "ch_002",
        "title": "Two Theories",
        "summary": "Reed develops two competing theories.",
        "scenes": [{"id": "scene_02_01", "purpose": "Interview with business partner"}, {"id": "scene_02_02", "purpose": "Interview with spouse"}],
    }))

    ch3 = root / "chapters" / "ch_003"
    ch3.mkdir(parents=True, exist_ok=True)
    (ch3 / "outline.yaml").write_text(yaml.safe_dump({
        "chapter_id": "ch_003",
        "title": "Pressure",
        "summary": "Captain Graves pressures Reed for an arrest.",
        "scenes": [{"id": "scene_03_01", "purpose": "Confrontation with Captain"}],
    }))

    # ------------------------------------------------------------------
    # Decision workspace  (.auteur/decisions/)
    # ------------------------------------------------------------------
    decisions_root = root / ".auteur" / "decisions"
    snapshots_dir = decisions_root / "snapshots"
    latest_dir = decisions_root / "latest"
    lineage_dir = decisions_root / "lineage"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    latest_dir.mkdir(parents=True, exist_ok=True)
    lineage_dir.mkdir(parents=True, exist_ok=True)

    # Decision 1: OPEN — which theory to pursue
    dec1 = {
        "decision_id": "dec_theory_fork",
        "snapshot_id": "snap_dec_theory_fork_001",
        "lifecycle_state": "open",
        "readiness": "needs_candidate",
        "trigger": "impact_finding",
        "title": "Which theory of the crime to pursue?",
        "evidence": [
            {
                "evidence_id": "ev_theory_a",
                "source": "impact",
                "type": "structural_fact",
                "classification": "contextual_observation",
                "description": "Theory A points to the business partner.",
                "freshness": "current",
                "recorded_at": _iso(),
            },
            {
                "evidence_id": "ev_theory_b",
                "source": "impact",
                "type": "structural_fact",
                "classification": "contextual_observation",
                "description": "Theory B points to the spouse.",
                "freshness": "current",
                "recorded_at": _iso(),
            },
        ],
        "unresolved_choices": [
            {
                "choice_id": "choice_theory",
                "question": "Which theory should Reed investigate first?",
                "options": ["theory_a", "theory_b"],
                "state": "open",
            },
        ],
        "conflicts": [],
        "candidates": [],
        "actions": [
            {
                "action_id": "act_generate_candidates",
                "label": "Generate candidate simulations",
                "type": "tool",
                "expected_result_state": "needs_evaluation",
            },
        ],
        "created_at": _iso(),
        "updated_at": _iso(),
        "authority_level": "author",
        "title_for_display": "Theory Fork",
    }
    (snapshots_dir / "dec_theory_fork.json").write_text(json.dumps(dec1, indent=2))

    # Decision 2: OPEN with candidates — IA cooperation
    dec2 = {
        "decision_id": "dec_ia_cooperation",
        "snapshot_id": "snap_dec_ia_coop_001",
        "lifecycle_state": "open",
        "readiness": "needs_evaluation",
        "trigger": "impact_finding",
        "title": "Should Reed cooperate with Internal Affairs?",
        "evidence": [
            {
                "evidence_id": "ev_ia_offer",
                "source": "impact",
                "type": "structural_fact",
                "classification": "fact",
                "description": "IA offers Reed immunity in exchange for testimony.",
                "freshness": "current",
                "recorded_at": _iso(),
            },
            {
                "evidence_id": "ev_ia_risk",
                "source": "impact",
                "type": "structural_fact",
                "classification": "contextual_observation",
                "description": "Colleagues will view Reed as a traitor.",
                "freshness": "current",
                "recorded_at": _iso(),
            },
        ],
        "unresolved_choices": [
            {
                "choice_id": "choice_ia",
                "question": "Should Reed cooperate with IA?",
                "options": ["cooperate", "refuse"],
                "state": "open",
            },
        ],
        "conflicts": [
            {
                "conflict_id": "conf_ia_loyalty",
                "type": "creative",
                "description": "Cooperation serves the case but damages team trust.",
                "resolution_boundary": "recompute",
                "evidence_ids": ["ev_ia_offer", "ev_ia_risk"],
                "blocking_status": False,
            },
        ],
        "candidates": [
            {
                "candidate_id": "cand_cooperate",
                "label": "Cooperate with IA",
                "summary": "Reed takes immunity and testifies.",
                "impact_estimate": {"score": 7, "rationale": "Clears the case but alienates team."},
                "confidence": 0.6,
                "status": "draft",
                "acceptance_blockers": [],
            },
            {
                "candidate_id": "cand_refuse",
                "label": "Refuse cooperation",
                "summary": "Reed protects the team but risks the case.",
                "impact_estimate": {"score": 5, "rationale": "Preserves team unity but may lose evidence."},
                "confidence": 0.4,
                "status": "draft",
                "acceptance_blockers": [],
            },
        ],
        "actions": [
            {
                "action_id": "act_evaluate_candidates",
                "label": "Evaluate candidates with reasoning",
                "type": "tool",
                "expected_result_state": "needs_acceptance",
            },
        ],
        "created_at": _iso(),
        "updated_at": _iso(),
        "authority_level": "author",
        "title_for_display": "IA Cooperation",
    }
    (snapshots_dir / "dec_ia_cooperation.json").write_text(json.dumps(dec2, indent=2))

    # Decision 3: STALE — second victim response
    dec3 = {
        "decision_id": "dec_second_victim",
        "snapshot_id": "snap_dec_victim_001",
        "lifecycle_state": "open",
        "readiness": "stale",
        "trigger": "impact_finding",
        "title": "How to respond to the second victim discovery?",
        "evidence": [
            {
                "evidence_id": "ev_second_body",
                "source": "impact",
                "type": "structural_fact",
                "classification": "fact",
                "description": "A second victim is found with the same MO.",
                "freshness": "stale",
                "recorded_at": "2026-07-20T08:00:00+00:00",
            },
        ],
        "unresolved_choices": [
            {
                "choice_id": "choice_response",
                "question": "Should the investigation pivot to the new crime scene or stay focused on the original?",
                "options": ["pivot", "stay_focused"],
                "state": "open",
            },
        ],
        "conflicts": [],
        "candidates": [],
        "actions": [
            {
                "action_id": "act_refresh",
                "label": "Refresh evidence",
                "type": "tool",
                "expected_result_state": "needs_candidate",
            },
        ],
        "created_at": "2026-07-20T08:00:00+00:00",
        "updated_at": "2026-07-20T08:00:00+00:00",
        "authority_level": "author",
        "title_for_display": "Second Victim Response",
    }
    (snapshots_dir / "dec_second_victim.json").write_text(json.dumps(dec3, indent=2))

    # Latest pointer
    latest = {
        "decision_id": "dec_theory_fork",
        "snapshot_id": "snap_dec_theory_fork_001",
        "updated_at": _iso(),
    }
    (latest_dir / "latest.json").write_text(json.dumps(latest, indent=2))

    # Lineage for each decision
    for dec_id in ("dec_theory_fork", "dec_ia_cooperation", "dec_second_victim"):
        lineage = [
            {"snapshot_id": f"snap_{dec_id}_001", "decision_id": dec_id, "created_at": _iso()},
        ]
        (lineage_dir / f"{dec_id}.json").write_text(json.dumps(lineage, indent=2))

    # ------------------------------------------------------------------
    # Simulation state  (.auteur/simulation/)
    # ------------------------------------------------------------------
    sim_root = root / ".auteur" / "simulation"
    (sim_root / "baselines").mkdir(parents=True, exist_ok=True)
    (sim_root / "scenarios").mkdir(parents=True, exist_ok=True)
    (sim_root / "comparisons").mkdir(parents=True, exist_ok=True)

    baseline = {
        "baseline_id": "baseline_001",
        "simulation_id": "sim_prefork",
        "scenario_id": "scenario_current",
        "projection": {
            "estimated_outcome": "case_solved_uncertain",
            "confidence": 0.5,
            "key_uncertainties": ["theory_selection", "ia_cooperation"],
            "milestone_impact": [
                {"milestone_id": "ms_first_arrest", "probability": 0.4},
            ],
        },
        "schema_version": 1,
        "created_at": _iso(),
    }
    (sim_root / "baselines" / "baseline_001.yaml").write_text(yaml.safe_dump(baseline))

    scenario_a = {
        "scenario_id": "scenario_theory_a",
        "simulation_id": "sim_theory_a",
        "description": "What if Reed pursues Theory A first?",
        "assumptions": ["Business partner is guilty", "Forensic evidence is solid"],
        "projection": {
            "estimated_outcome": "wrong_arrest_then_corrected",
            "confidence": 0.6,
            "key_uncertainties": ["evidence_reliability"],
        },
        "schema_version": 1,
        "created_at": _iso(),
    }
    (sim_root / "scenarios" / "scenario_theory_a.yaml").write_text(yaml.safe_dump(scenario_a))

    scenario_b = {
        "scenario_id": "scenario_theory_b",
        "simulation_id": "sim_theory_b",
        "description": "What if Reed pursues Theory B first?",
        "assumptions": ["Spouse is guilty", "Motive is insurance fraud"],
        "projection": {
            "estimated_outcome": "correct_arrest_early",
            "confidence": 0.7,
            "key_uncertainties": ["witness_credibility"],
        },
        "schema_version": 1,
        "created_at": _iso(),
    }
    (sim_root / "scenarios" / "scenario_theory_b.yaml").write_text(yaml.safe_dump(scenario_b))

    comparison_sim = {
        "comparison_id": "comp_theories",
        "scenario_ids": ["scenario_theory_a", "scenario_theory_b"],
        "baseline_id": "baseline_001",
        "recommended_path": "scenario_theory_b",
        "rationale": "Higher confidence and fewer negative externalities.",
        "schema_version": 1,
        "created_at": _iso(),
    }
    (sim_root / "comparisons" / "comp_theories.yaml").write_text(yaml.safe_dump(comparison_sim))

    (sim_root / "latest.yaml").write_text(yaml.safe_dump({
        "baseline_id": "baseline_001",
        "comparison_id": "comp_theories",
    }))

    # ------------------------------------------------------------------
    # Planning state  (.auteur/planning/)
    # ------------------------------------------------------------------
    plan_root = root / ".auteur" / "planning"
    (plan_root / "snapshots").mkdir(parents=True, exist_ok=True)
    (plan_root / "history").mkdir(parents=True, exist_ok=True)

    plan_snapshot = {
        "plan_id": "plan_001",
        "schema_version": 1,
        "milestones": [
            {
                "milestone_id": "ms_theory_choice",
                "label": "Choose investigation theory",
                "status": "blocked",
                "blockers": [
                    {"blocker_id": "blk_no_evaluation", "description": "Candidates have not been evaluated", "status": "active"},
                ],
                "dependencies": [],
                "decisions": ["dec_theory_fork"],
                "target_completion": _iso(),
            },
            {
                "milestone_id": "ms_ia_decision",
                "label": "Decide IA cooperation",
                "status": "in_progress",
                "blockers": [],
                "dependencies": ["ms_theory_choice"],
                "decisions": ["dec_ia_cooperation"],
                "target_completion": _iso(),
            },
            {
                "milestone_id": "ms_second_victim",
                "label": "Respond to second victim",
                "status": "stale",
                "blockers": [
                    {"blocker_id": "blk_stale_evidence", "description": "Evidence is stale, needs refresh", "status": "active"},
                ],
                "dependencies": ["ms_theory_choice"],
                "decisions": ["dec_second_victim"],
                "target_completion": "2026-07-28T12:00:00+00:00",
            },
            {
                "milestone_id": "ms_first_arrest",
                "label": "Make first arrest",
                "status": "pending",
                "blockers": [],
                "dependencies": ["ms_theory_choice", "ms_ia_decision"],
                "decisions": [],
                "target_completion": "2026-08-01T12:00:00+00:00",
            },
        ],
        "critical_path": ["ms_theory_choice", "ms_ia_decision", "ms_first_arrest"],
        "created_at": _iso(),
        "updated_at": _iso(),
    }
    (plan_root / "snapshots" / "plan_001_snapshot.json").write_text(json.dumps(plan_snapshot, indent=2))

    history_entry = {
        "entry_id": "hist_001",
        "plan_id": "plan_001",
        "action": "created",
        "description": "Initial plan with four milestones tracking key decisions.",
        "created_at": _iso(),
    }
    (plan_root / "history" / "hist_001.json").write_text(json.dumps(history_entry, indent=2))

    (plan_root / "latest.yaml").write_text(yaml.safe_dump({"plan_id": "plan_001", "snapshot_path": "snapshots/plan_001_snapshot.json"}))

    # ------------------------------------------------------------------
    # Commitment state  (.auteur/commitment/)
    # ------------------------------------------------------------------
    commit_root = root / ".auteur" / "commitment"
    (commit_root / "definitions").mkdir(parents=True, exist_ok=True)
    (commit_root / "plans").mkdir(parents=True, exist_ok=True)
    (commit_root / "events").mkdir(parents=True, exist_ok=True)

    commitment = {
        "commitment_id": "cmt_001",
        "schema_version": 1,
        "decisions": ["dec_theory_fork", "dec_ia_cooperation", "dec_second_victim"],
        "status": "active",
        "created_at": _iso(),
        "authority_level": "author",
        "title": "Phase 1 Investigation Commitments",
        "description": "All open investigation decisions before the first arrest milestone.",
    }
    (commit_root / "definitions" / "cmt_001.json").write_text(json.dumps(commitment, indent=2))

    execution_plan = {
        "plan_id": "exec_plan_001",
        "commitment_id": "cmt_001",
        "schema_version": 1,
        "steps": [
            {"step_id": "step_001", "action": "evaluate_theory_candidates", "depends_on": [], "status": "pending"},
            {"step_id": "step_002", "action": "decide_ia_cooperation", "depends_on": ["step_001"], "status": "pending"},
            {"step_id": "step_003", "action": "refresh_second_victim_evidence", "depends_on": ["step_001"], "status": "pending"},
        ],
        "created_at": _iso(),
    }
    (commit_root / "plans" / "exec_plan_001.json").write_text(json.dumps(execution_plan, indent=2))

    (commit_root / "latest.yaml").write_text(yaml.safe_dump({"commitment_id": "cmt_001", "plan_id": "exec_plan_001"}))

    return root


@pytest.fixture
def multi_decision_commitment(tmp_path: Path) -> Path:
    """Build a deterministic project with multiple open decisions and planning state."""
    return build_multi_decision_commitment(tmp_path)
