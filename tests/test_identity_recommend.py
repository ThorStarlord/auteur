import pytest
from pathlib import Path
import yaml
from auteur.cli import main
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient

def test_cli_identity_recommend_success(tmp_path, monkeypatch):
    identity_yaml_path = tmp_path / "story_identity.yaml"
    
    # Successful YAML output on the first try
    success_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery about a detective who discovers the king is the killer."
target_experience:
  primary: "dread"
  progression: "curiosity -> suspicion -> dread"
  avoid:
    - "satisfaction"
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown blocks the investigation."
  conflict: "Continuing the investigation exposes the detective to treason charges."
  stakes: "The detective's life and the truth."
  change: "The detective changes from an idealistic truth-seeker to a silent accomplice to preserve peace."
not_this:
  - "a standard whodunit"
open_questions:
  - "does the detective survive?"
confidence: 0.9
why_this_is_best: "Tragic ending fits the grim reality of the kingdom."
rejected_directions:
  - "heroic victory"
author_overrides: []
"""
    
    fake_response = LLMResponse(
        text=f"```yaml\n{success_yaml}\n```",
        input_tokens=100,
        output_tokens=100
    )
    
    fake_client = FakeClient([fake_response])
    
    # Monkeypatch build_client to return fake_client
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)
    
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder in a royal palace.",
        "--genre", "mystery",
        "--medium", "novel",
        "--mode", "tragic",
        "--output", str(identity_yaml_path)
    ])
    
    assert exit_code == 0
    assert identity_yaml_path.exists()
    
    with open(identity_yaml_path, "r", encoding="utf-8") as f:
        saved_data = yaml.safe_load(f)
    assert saved_data["title"] == "The Silent Crown"
    assert saved_data["story_type"]["genre"] == "mystery"
    assert saved_data["story_type"]["medium"] == "novel"
    assert saved_data["story_type"]["mode"] == "tragic"


def test_cli_identity_recommend_retry_loop(tmp_path, monkeypatch):
    identity_yaml_path = tmp_path / "story_identity_retry.yaml"
    
    # First response fails validation (duplicate want/change)
    fail_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective wants to solve the murder." # Duplicate!
"""

    # Second response resolves the validation issue
    success_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective changes completely."
"""

    resp_fail = LLMResponse(
        text=f"```yaml\n{fail_yaml}\n```",
        input_tokens=100,
        output_tokens=100
    )
    resp_success = LLMResponse(
        text=f"```yaml\n{success_yaml}\n```",
        input_tokens=200,
        output_tokens=200
    )
    
    fake_client = FakeClient([resp_fail, resp_success])
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)
    
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder.",
        "--output", str(identity_yaml_path)
    ])
    
    assert exit_code == 0
    assert identity_yaml_path.exists()
    
    with open(identity_yaml_path, "r", encoding="utf-8") as f:
        saved_data = yaml.safe_load(f)
    assert saved_data["central_engine"]["change"] == "The detective changes completely."


def test_cli_identity_recommend_max_retries_fail(tmp_path, monkeypatch):
    identity_yaml_path = tmp_path / "story_identity_fail.yaml"
    
    # All responses fail validation
    fail_yaml = """
title: "Failed Story"
core_answer: "A story."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective wants to solve the murder."
"""
    
    responses = [
        LLMResponse(text=f"```yaml\n{fail_yaml}\n```", input_tokens=50, output_tokens=50)
        for _ in range(4)
    ]
    
    fake_client = FakeClient(responses)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)
    
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder.",
        "--output", str(identity_yaml_path)
    ])
    
    assert exit_code == 1
    assert not identity_yaml_path.exists()


def test_cli_identity_recommend_open_ended(tmp_path, monkeypatch):
    # Output path for the main (opinionated) file, although we'll use open-ended mode
    output_yaml = tmp_path / "story_identity.yaml"
    candidate_dir = tmp_path / "story_identity_candidates"

    valid_yaml_tmpl = """
title: "The Silent Crown {idx}"
core_answer: "A tragedy mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "Want {idx}"
  resistance: "Resistance {idx}"
  conflict: "Conflict {idx}"
  stakes: "Stakes {idx}"
  change: "Change {idx}"
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "open_ended"
best_basis: "{basis}"
why_this_is_best: "Explanation {idx}"
rejected_directions: []
author_overrides: []
"""

    summary_json = '{"summary": "A detective story.", "tradeoffs": ["t1", "t2"], "risks": ["r1", "r2"], "best_for": ["b1", "b2"]}'

    # We will generate 3 candidates, so we need 6 responses:
    # 1. Candidate 1 YAML (genre_aligned)
    # 2. Summary 1 JSON
    # 3. Candidate 2 YAML (structurally_coherent)
    # 4. Summary 2 JSON
    # 5. Candidate 3 YAML (faithful_to_input)
    # 6. Summary 3 JSON
    responses = [
        LLMResponse(text=f"```yaml\n{valid_yaml_tmpl.format(idx=1, basis='genre_aligned')}\n```", input_tokens=100, output_tokens=100),
        LLMResponse(text=summary_json, input_tokens=100, output_tokens=100),
        LLMResponse(text=f"```yaml\n{valid_yaml_tmpl.format(idx=2, basis='structurally_coherent')}\n```", input_tokens=100, output_tokens=100),
        LLMResponse(text=summary_json, input_tokens=100, output_tokens=100),
        LLMResponse(text=f"```yaml\n{valid_yaml_tmpl.format(idx=3, basis='faithful_to_input')}\n```", input_tokens=100, output_tokens=100),
        LLMResponse(text=summary_json, input_tokens=100, output_tokens=100),
    ]

    fake_client = FakeClient(responses)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)

    exit_code = main([
        "identity", "recommend",
        "A detective investigates a royal palace murder.",
        "--recommend-mode", "open-ended",
        "--candidates", "3",
        "--output", str(output_yaml),
    ])

    assert exit_code == 0
    # The opinionated story_identity.yaml should NOT be directly created (it compiles candidates first)
    assert not output_yaml.exists()
    assert candidate_dir.exists()

    # Verify candidates
    for idx in range(1, 4):
        c_path = candidate_dir / f"candidate_{idx}.yaml"
        assert c_path.exists()
        with open(c_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["title"] == f"The Silent Crown {idx}"

    # Verify recommendation_set.yaml
    rec_set_path = candidate_dir / "recommendation_set.yaml"
    assert rec_set_path.exists()
    with open(rec_set_path, "r", encoding="utf-8") as f:
        rec_data = yaml.safe_load(f)
    assert rec_data["mode"] == "open_ended"
    assert len(rec_data["candidates"]) == 3
    assert rec_data["candidates"][0]["best_basis"] == "genre_aligned"

    # Verify comparison.md
    comp_path = candidate_dir / "comparison.md"
    assert comp_path.exists()
    comp_content = comp_path.read_text(encoding="utf-8")
    assert "Story Identity Candidate Comparison" in comp_content
    assert "candidate_1" in comp_content


def test_cli_identity_accept_candidate(tmp_path):
    candidate_dir = tmp_path / "story_identity_candidates"
    candidate_dir.mkdir(parents=True)

    candidate_yaml = """
title: "Accepted Story"
core_answer: "A tragedy mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "Want"
  resistance: "Resistance"
  conflict: "Conflict"
  stakes: "Stakes"
  change: "Change"
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "open_ended"
best_basis: "genre_aligned"
why_this_is_best: "Explanation"
rejected_directions: []
author_overrides: []
"""
    c_path = candidate_dir / "candidate_1.yaml"
    c_path.write_text(candidate_yaml, encoding="utf-8")

    # Save a fake recommendation_set.yaml to test hash comparison (optional but good)
    import hashlib
    chash = "sha256:" + hashlib.sha256(candidate_yaml.encode("utf-8")).hexdigest()

    rec_set_yaml = f"""
mode: open_ended
source_input_path: "A detective story"
generated_at: "2026-05-19T00:00:00Z"
requested_candidates: 1
valid_candidates: 1
candidates:
  - candidate_id: candidate_1
    path: "{str(c_path)}"
    content_hash: "{chash}"
"""
    (candidate_dir / "recommendation_set.yaml").write_text(rec_set_yaml, encoding="utf-8")

    dest_yaml = tmp_path / "story_identity.yaml"

    # 1. Accept and promote
    exit_code = main([
        "identity", "accept-candidate",
        str(c_path),
        "--output", str(dest_yaml)
    ])

    assert exit_code == 0
    assert dest_yaml.exists()
    # By default, candidate directory should be cleaned up
    assert not candidate_dir.exists()

    with open(dest_yaml, "r", encoding="utf-8") as f:
        promoted = yaml.safe_load(f)
    assert promoted["title"] == "Accepted Story"


def test_cli_identity_accept_candidate_keep(tmp_path):
    candidate_dir = tmp_path / "story_identity_candidates"
    candidate_dir.mkdir(parents=True)

    c_path = candidate_dir / "candidate_1.yaml"
    c_path.write_text("""
title: "Accepted Story Keep"
core_answer: "A tragedy mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "Want"
  resistance: "Resistance"
  conflict: "Conflict"
  stakes: "Stakes"
  change: "Change"
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "open_ended"
best_basis: "genre_aligned"
why_this_is_best: "Explanation"
rejected_directions: []
author_overrides: []
""", encoding="utf-8")

    dest_yaml = tmp_path / "story_identity.yaml"

    exit_code = main([
        "identity", "accept-candidate",
        str(c_path),
        "--output", str(dest_yaml),
        "--keep-candidates"
    ])

    assert exit_code == 0
    assert dest_yaml.exists()
    assert candidate_dir.exists()

def test_cli_identity_recommend_auto_override_rejection(tmp_path, monkeypatch):
    identity_yaml_path = tmp_path / "story_identity_override.yaml"
    
    # First response attempts to inject an author override to cheat ending_tone/runway
    fail_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective wants to solve the murder." # Duplicate!
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "opinionated"
best_basis: "genre_aligned"
why_this_is_best: "Explanation"
rejected_directions: []
author_overrides:
  - "ending_tone"
"""

    # Second response is valid and clean of overrides
    success_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective changes completely."
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "opinionated"
best_basis: "genre_aligned"
why_this_is_best: "Explanation"
rejected_directions: []
author_overrides: []
"""

    resp_fail = LLMResponse(
        text=f"```yaml\n{fail_yaml}\n```",
        input_tokens=100,
        output_tokens=100
    )
    resp_success = LLMResponse(
        text=f"```yaml\n{success_yaml}\n```",
        input_tokens=200,
        output_tokens=200
    )
    
    fake_client = FakeClient([resp_fail, resp_success])
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)
    
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder.",
        "--output", str(identity_yaml_path)
    ])
    
    assert exit_code == 0
    assert identity_yaml_path.exists()
    
    with open(identity_yaml_path, "r", encoding="utf-8") as f:
        saved_data = yaml.safe_load(f)
    assert saved_data["author_overrides"] == []
    assert saved_data["central_engine"]["change"] == "The detective changes completely."


def test_cli_identity_recommend_warning_confidence_penalty(tmp_path, monkeypatch):
    identity_yaml_path = tmp_path / "story_identity_warning.yaml"
    
    # Valid YAML but includes an unknown subgenre which generates a warning
    warning_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres:
    - "cyberpunk_cozy"
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective changes completely."
not_this: []
open_questions: []
confidence: 0.90
recommendation_mode: "opinionated"
best_basis: "genre_aligned"
why_this_is_best: "Explanation"
rejected_directions: []
author_overrides: []
"""

    resp = LLMResponse(
        text=f"```yaml\n{warning_yaml}\n```",
        input_tokens=100,
        output_tokens=100
    )
    
    fake_client = FakeClient([resp])
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)
    
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder.",
        "--output", str(identity_yaml_path)
    ])
    
    assert exit_code == 0
    assert identity_yaml_path.exists()
    
    with open(identity_yaml_path, "r", encoding="utf-8") as f:
        saved_data = yaml.safe_load(f)
    
    assert saved_data["confidence"] == 0.85


def test_cli_identity_recommend_mode_open_ended_deprecation_warning(tmp_path, monkeypatch, capsys):
    """--mode open-ended prints deprecation warning to stderr."""
    valid_yaml = """
title: "Test"
core_answer: "A test."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "Want"
  resistance: "Resistance"
  conflict: "Conflict"
  stakes: "Stakes"
  change: "Change"
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "opinionated"
best_basis: "genre_aligned"
why_this_is_best: "Explanation"
rejected_directions: []
author_overrides: []
"""

    output_path = tmp_path / "story_identity.yaml"
    fake_client = FakeClient([LLMResponse(text=f"```yaml\n{valid_yaml}\n```", input_tokens=50, output_tokens=50)])
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)

    exit_code = main([
        "identity", "recommend",
        "A test premise.",
        "--mode", "open-ended",
        "--output", str(output_path),
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "deprecated" in captured.err.lower()
    assert "--recommend-mode open-ended" in captured.err


def test_cli_identity_recommend_recommend_mode_clean_path(tmp_path, monkeypatch, capsys):
    """--recommend-mode open-ended does NOT print deprecation warning."""
    candidate_dir = tmp_path / "story_identity_candidates"
    valid_yaml_tmpl = """
title: "Test {idx}"
core_answer: "A test."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "Want {idx}"
  resistance: "Resistance {idx}"
  conflict: "Conflict {idx}"
  stakes: "Stakes {idx}"
  change: "Change {idx}"
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "open_ended"
best_basis: "{basis}"
why_this_is_best: "Explanation {idx}"
rejected_directions: []
author_overrides: []
"""
    summary_json = '{"summary": "Test.", "tradeoffs": ["t1"], "risks": ["r1"], "best_for": ["b1"]}'

    responses = [
        LLMResponse(text=f"```yaml\n{valid_yaml_tmpl.format(idx=1, basis='genre_aligned')}\n```", input_tokens=50, output_tokens=50),
        LLMResponse(text=summary_json, input_tokens=50, output_tokens=50),
    ]
    fake_client = FakeClient(responses)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)

    exit_code = main([
        "identity", "recommend",
        "A test premise.",
        "--recommend-mode", "open-ended",
        "--candidates", "1",
        "--output", str(tmp_path / "story_identity.yaml"),
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "deprecated" not in captured.err.lower()


def test_cli_identity_recommend_mode_vs_recommend_mode_equivalence(tmp_path, monkeypatch, capsys):
    """Both --mode open-ended and --recommend-mode open-ended produce same output."""
    valid_yaml_tmpl = """
title: "Test {idx}"
core_answer: "A test."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "Want {idx}"
  resistance: "Resistance {idx}"
  conflict: "Conflict {idx}"
  stakes: "Stakes {idx}"
  change: "Change {idx}"
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "open_ended"
best_basis: "{basis}"
why_this_is_best: "Explanation {idx}"
rejected_directions: []
author_overrides: []
"""
    summary_json = '{"summary": "Test.", "tradeoffs": ["t1"], "risks": ["r1"], "best_for": ["b1"]}'

    def make_client():
        return FakeClient([
            LLMResponse(text=f"```yaml\n{valid_yaml_tmpl.format(idx=1, basis='genre_aligned')}\n```", input_tokens=50, output_tokens=50),
            LLMResponse(text=summary_json, input_tokens=50, output_tokens=50),
        ])

    # Run with --mode open-ended
    dir1 = tmp_path / "run_mode"
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: make_client())
    exit1 = main([
        "identity", "recommend",
        "A test premise.",
        "--mode", "open-ended",
        "--candidates", "1",
        "--output", str(dir1 / "story_identity.yaml"),
    ])

    # Run with --recommend-mode open-ended
    dir2 = tmp_path / "run_recommend_mode"
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: make_client())
    exit2 = main([
        "identity", "recommend",
        "A test premise.",
        "--recommend-mode", "open-ended",
        "--candidates", "1",
        "--output", str(dir2 / "story_identity.yaml"),
    ])

    captured = capsys.readouterr()
    assert exit1 == 0
    assert exit2 == 0
    assert "deprecated" in captured.err  # --mode version emitted warning
    assert "--recommend-mode open-ended" in captured.err

    cand1 = dir1 / "story_identity_candidates" / "candidate_1.yaml"
    cand2 = dir2 / "story_identity_candidates" / "candidate_1.yaml"
    assert cand1.exists()
    assert cand2.exists()
    assert cand1.read_text(encoding="utf-8") == cand2.read_text(encoding="utf-8")


def test_cli_identity_recommend_valid_story_mode_no_deprecation(tmp_path, monkeypatch, capsys):
    """--mode tragic (valid StoryMode) does NOT emit deprecation."""
    valid_yaml = """
title: "Test"
core_answer: "A test."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "Want"
  resistance: "Resistance"
  conflict: "Conflict"
  stakes: "Stakes"
  change: "Change"
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "opinionated"
best_basis: "genre_aligned"
why_this_is_best: "Explanation"
rejected_directions: []
author_overrides: []
"""

    output_path = tmp_path / "story_identity.yaml"
    fake_client = FakeClient([LLMResponse(text=f"```yaml\n{valid_yaml}\n```", input_tokens=50, output_tokens=50)])
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)

    exit_code = main([
        "identity", "recommend",
        "A test premise.",
        "--mode", "tragic",
        "--output", str(output_path),
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "deprecated" not in captured.err.lower()


def test_cli_identity_recommend_debug_logging(tmp_path, monkeypatch):
    identity_yaml_path = tmp_path / "story_identity_debug.yaml"
    
    # First response fails validation (duplicate want/change)
    fail_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective wants to solve the murder." # Duplicate!
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "opinionated"
best_basis: "genre_aligned"
why_this_is_best: "Explanation"
rejected_directions: []
author_overrides: []
"""

    # Second response is valid
    success_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective changes completely."
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "opinionated"
best_basis: "genre_aligned"
why_this_is_best: "Explanation"
rejected_directions: []
author_overrides: []
"""

    resp_fail = LLMResponse(text=f"```yaml\n{fail_yaml}\n```", input_tokens=100, output_tokens=100)
    resp_success = LLMResponse(text=f"```yaml\n{success_yaml}\n```", input_tokens=100, output_tokens=100)
    
    fake_client = FakeClient([resp_fail, resp_success])
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)
    
    import shutil
    runs_dir = Path(".auteur/runs")
    if runs_dir.exists():
        shutil.rmtree(runs_dir)
        
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder.",
        "--output", str(identity_yaml_path),
        "--debug"
    ])
    
    assert exit_code == 0
    assert runs_dir.exists()
    
    subdirs = list(runs_dir.iterdir())
    assert len(subdirs) == 1
    
    attempt_files = list(subdirs[0].glob("*.txt"))
    assert len(attempt_files) == 1
    assert "attempt_1" in attempt_files[0].name
    
    content = attempt_files[0].read_text(encoding="utf-8")
    assert "The detective wants to solve the murder." in content
    assert "change_duplicates_want" in content

    shutil.rmtree(runs_dir)


def test_cli_identity_recommend_mode_deprecation_warning(tmp_path, monkeypatch, capsys):
    """Test that --mode open-ended emits deprecation warning but still works."""
    identity_yaml_path = tmp_path / "story_identity.yaml"

    success_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown blocks the investigation."
  conflict: "Continuing exposes the detective to charges."
  stakes: "The detective's life and the truth."
  change: "The detective becomes a silent accomplice."
not_this: []
open_questions: []
confidence: 0.9
why_this_is_best: "Tragic ending fits the grim reality."
rejected_directions: []
author_overrides: []
"""

    fake_response = LLMResponse(
        text=f"```yaml\n{success_yaml}\n```",
        input_tokens=100,
        output_tokens=100
    )

    fake_client = FakeClient([fake_response])
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)

    # Use deprecated --mode open-ended flag
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder.",
        "--mode", "open-ended",
        "--output", str(identity_yaml_path),
    ])

    # Should still succeed
    assert exit_code == 0

    # Should emit deprecation warning to stderr
    captured = capsys.readouterr()
    assert "Warning: --mode open-ended is deprecated" in captured.err
    assert "--recommend-mode open-ended" in captured.err


def test_cli_identity_recommend_recommend_mode_no_warning(tmp_path, monkeypatch, capsys):
    """Test that --recommend-mode open-ended does NOT emit deprecation warning."""
    candidate_dir = tmp_path / "story_identity_candidates"

    valid_yaml_tmpl = """
title: "The Silent Crown {idx}"
core_answer: "A tragedy mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "Want {idx}"
  resistance: "Resistance {idx}"
  conflict: "Conflict {idx}"
  stakes: "Stakes {idx}"
  change: "Change {idx}"
not_this: []
open_questions: []
confidence: 0.95
recommendation_mode: "open_ended"
best_basis: "{basis}"
why_this_is_best: "Explanation {idx}"
rejected_directions: []
author_overrides: []
"""

    summary_json = '{"summary": "A detective story.", "tradeoffs": ["t1", "t2"], "risks": ["r1", "r2"], "best_for": ["b1", "b2"]}'

    responses = [
        LLMResponse(text=f"```yaml\n{valid_yaml_tmpl.format(idx=1, basis='genre_aligned')}\n```", input_tokens=100, output_tokens=100),
        LLMResponse(text=summary_json, input_tokens=100, output_tokens=100),
    ]

    fake_client = FakeClient(responses)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)

    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder.",
        "--recommend-mode", "open-ended",
        "--candidates", "1",
        "--output", str(tmp_path / "story_identity.yaml"),
    ])

    assert exit_code == 0

    # Should NOT emit deprecation warning
    captured = capsys.readouterr()
    assert "Warning: --mode open-ended is deprecated" not in captured.err
