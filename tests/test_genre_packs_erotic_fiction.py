"""Comprehensive test suite for Genre Packs Erotic Fiction MVP."""

import json
from pathlib import Path
import pytest

from auteur.blueprint import (
    Genre,
    StoryMedium,
    StoryMode,
    TargetExperience,
    StoryBlueprint,
)
from pydantic import BaseModel, Field


class TestScene(BaseModel):
    scene_number: int = 1
    title: str = ""
    summary: str = ""
    scene_function: str = ""
    state_change: str = ""


class TestChapter(BaseModel):
    chapter_number: int = 1
    scenes: list[TestScene] = Field(default_factory=list)


class TestAct(BaseModel):
    act_number: int = 1
    title: str = ""
    chapters: list[TestChapter] = Field(default_factory=list)


class DummyBlueprint(BaseModel):
    acts: list[TestAct] = Field(default_factory=list)
from auteur.identity import StoryIdentity, HighLevelCentralEngine, StoryType
from auteur.genre_packs import (
    GenrePack,
    GenrePackRegistry,
    get_pack_registry,
    load_genre_pack,
    compute_pack_content_hash,
    recommend_genre_profile,
    validate_pack_schema,
    validate_genre_profile_identity,
    reconcile_identity_with_recommendation,
    run_genre_diagnostics,
    GenreAuthorOverride,
    GenrePackError,
    GenreErrorCode,
)
from auteur.structure.diagnostics import DiagnosticSeverity


def _make_minimal_identity(tmp_path: Path) -> StoryIdentity:
    ident = StoryIdentity(
        title="Bound Souls",
        core_answer="A story exploring how intense erotic desire dismantles psychological armor.",
        target_experience=TargetExperience(primary="desire", progression="desire -> vulnerability -> intimacy", avoid=[]),
        story_type=StoryType(medium=StoryMedium.NOVEL, mode=StoryMode.INTIMATE, genre=Genre.ROMANCE),
        central_engine=HighLevelCentralEngine(
            want="To surrender to passion without compromising autonomy.",
            resistance="Deep-seated fear of psychological vulnerability.",
            conflict="Irresistible erotic pull versus defensive isolation.",
            stakes="Emotional isolation versus authentic transformation.",
            change="Replaces protective pride with transformative intimacy.",
        ),
    )
    p = tmp_path / "story_identity.yaml"
    ident.to_yaml(p)
    return ident


def test_erotic_fiction_pack_loads_and_validates():
    registry = get_pack_registry()
    pack, content_hash = registry.get_pack("erotic_fiction", "0.1.0")
    assert pack.pack_id == "erotic_fiction"
    assert pack.version == "0.1.0"
    assert len(pack.subgenre_profiles) == 3
    assert len(content_hash) == 64
    validate_pack_schema(pack)


def test_invalid_pack_fails_atomically():
    invalid_yaml = """
pack_id: malformed_pack
display_name: Malformed
version: 0.1.0
schema_version: 1
description: Invalid pack
audience_promises:
  - id: dup_id
    description: First
  - id: dup_id
    description: Duplicate ID
"""
    with pytest.raises(GenrePackError) as exc_info:
        pack, _ = load_genre_pack(invalid_yaml)
        validate_pack_schema(pack)
    assert exc_info.value.code in (GenreErrorCode.PACK_INVALID, GenreErrorCode.PACK_NOT_FOUND)


def test_subgenre_profiles_inherit_from_erotic_fiction_pack():
    registry = get_pack_registry()
    pack, _ = registry.get_pack("erotic_fiction", "0.1.0")
    profile_ids = [p.profile_id for p in pack.subgenre_profiles]
    assert "erotic_romance" in profile_ids
    assert "erotic_psychological_drama" in profile_ids
    assert "erotic_horror" in profile_ids

    romance = registry.get_profile("erotic_fiction", "erotic_romance")
    assert romance.base_pack_id == "erotic_fiction"
    assert romance.preferred_framing == "romantic"


def test_recommendation_returns_one_primary_profile():
    premise = "A psychological drama about an elite architect whose secret obsession with a rival exposes identity facades."
    rec = recommend_genre_profile(premise)
    assert rec.recommended_profile_id == "erotic_psychological_drama"
    assert "erotic psychological drama" in rec.why_this_is_best.casefold()


def test_recommendation_explains_rejected_profiles():
    premise = "A gothic romance exploring intense desire and emotional trust."
    rec = recommend_genre_profile(premise)
    assert len(rec.rejected_profiles) == 2
    rej_ids = [r.profile_id for r in rec.rejected_profiles]
    assert "erotic_romance" not in rej_ids or "erotic_horror" in rej_ids
    for rej in rec.rejected_profiles:
        assert len(rej.why_rejected) > 0
        assert len(rej.premise_adjustment_to_enable) > 0


def test_recommendation_does_not_mutate_story_identity(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    original_yaml = (tmp_path / "story_identity.yaml").read_text(encoding="utf-8")

    rec = recommend_genre_profile(ident.core_answer)
    assert rec.recommended_profile_id is not None

    after_yaml = (tmp_path / "story_identity.yaml").read_text(encoding="utf-8")
    assert original_yaml == after_yaml
    assert ident.genre_profile is None


def test_accepting_recommendation_updates_story_identity(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)

    updated_ident = reconcile_identity_with_recommendation(ident, rec)
    assert updated_ident.genre_profile is not None
    assert updated_ident.genre_profile.primary_pack_id == "erotic_fiction"
    assert updated_ident.genre_profile.primary_profile_id == rec.recommended_profile_id
    assert updated_ident.genre_profile.pack_content_hash == rec.pack_content_hash
    assert updated_ident.story_type.genre == Genre.EROTIC_FICTION
    assert rec.recommended_profile_id in updated_ident.story_type.subgenres


def test_author_override_is_persisted_explicitly(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)

    override = GenreAuthorOverride(
        target_expectation="genre_profile.primary_framing",
        recommended_value="unsettling",
        replacement_value="heroic",
        author_rationale="Author prefers heroic framing for psychological transformation.",
    )
    updated_ident = reconcile_identity_with_recommendation(ident, rec, author_overrides=[override])

    assert len(updated_ident.genre_profile.author_overrides) == 1
    ao = updated_ident.genre_profile.author_overrides[0]
    assert ao.target_expectation == "genre_profile.primary_framing"
    assert ao.replacement_value == "heroic"
    assert ao.author_rationale == "Author prefers heroic framing for psychological transformation."


def test_existing_minimal_story_identity_remains_compatible(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    p = tmp_path / "story_identity.yaml"
    loaded = StoryIdentity.from_yaml(p)
    assert loaded.genre_profile is None
    diags = loaded.validate_identity()
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 0


def test_accepted_identity_records_pack_version_and_hash(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)
    updated = reconcile_identity_with_recommendation(ident, rec)
    assert updated.genre_profile.primary_pack_version == "0.1.0"
    assert len(updated.genre_profile.pack_content_hash) == 64


def test_pack_update_does_not_silently_change_accepted_identity(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)
    updated = reconcile_identity_with_recommendation(ident, rec)
    p_hash = updated.genre_profile.pack_content_hash

    # Save to disk
    p = tmp_path / "story_identity.yaml"
    updated.to_yaml(p)

    # Reload identity
    reloaded = StoryIdentity.from_yaml(p)
    assert reloaded.genre_profile.pack_content_hash == p_hash


def test_stale_recommendation_is_refused_before_acceptance(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)
    # Simulate pack hash change
    rec.pack_content_hash = "0000000000000000000000000000000000000000000000000000000000000000"

    with pytest.raises(GenrePackError) as exc_info:
        reconcile_identity_with_recommendation(ident, rec)
    assert exc_info.value.code == GenreErrorCode.RECOMMENDATION_STALE


def test_genre_alignment_warning_respects_explicit_subversion(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile("Dark erotic psychological thriller.")
    rec.recommended_framing.primary = "horrific"

    override = GenreAuthorOverride(
        target_expectation="genre_profile.primary_framing",
        recommended_value="unsettling",
        replacement_value="horrific",
        author_rationale="Deliberate subversion to horror framing.",
    )
    updated = reconcile_identity_with_recommendation(ident, rec, author_overrides=[override])
    diags = validate_genre_profile_identity(updated)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 0


def test_genre_drift_is_diagnostic_not_automatic_mutation(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile("Erotic Romance")
    updated = reconcile_identity_with_recommendation(ident, rec)

    # Run diagnostics
    diags = run_genre_diagnostics(updated)
    # Ensure diagnostics do not mutate StoryIdentity
    assert updated.genre_profile.primary_profile_id == rec.recommended_profile_id


def test_genre_validation_uses_accepted_identity_profile(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)
    updated = reconcile_identity_with_recommendation(ident, rec)

    diags = validate_genre_profile_identity(updated)
    assert isinstance(diags, list)


def test_intimate_scene_without_state_change_produces_finding(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)
    updated = reconcile_identity_with_recommendation(ident, rec)

    blueprint = DummyBlueprint(
        acts=[
            TestAct(
                act_number=1,
                title="Setup",
                chapters=[
                    TestChapter(
                        chapter_number=1,
                        scenes=[
                            TestScene(scene_number=1, title="Embrace", summary="An intimate encounter where they embrace passionately.")
                        ],
                    )
                ],
            )
        ],
    )
    diags = run_genre_diagnostics(updated, blueprint)
    rules = [d.rule for d in diags]
    assert "genre.erotic_fiction.intimate_scenes_change_state" in rules


def test_repetitive_scene_function_produces_genre_finding(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)
    updated = reconcile_identity_with_recommendation(ident, rec)

    sc1 = TestScene(scene_number=1, title="Intimate 1", summary="An intimate encounter.", scene_function="test_boundary")
    sc2 = TestScene(scene_number=2, title="Intimate 2", summary="An intimate embrace.", scene_function="test_boundary")

    blueprint = DummyBlueprint(
        acts=[TestAct(act_number=1, title="Setup", chapters=[TestChapter(chapter_number=1, scenes=[sc1, sc2])])],
    )
    diags = run_genre_diagnostics(updated, blueprint)
    rules = [d.rule for d in diags]
    assert "genre.erotic_fiction.scene_function_diversity" in rules


def test_resolution_missing_erotic_arc_payoff_produces_finding(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)
    updated = reconcile_identity_with_recommendation(ident, rec)

    blueprint = DummyBlueprint(
        acts=[
            TestAct(act_number=1, title="Setup", chapters=[]),
            TestAct(act_number=2, title="Confrontation", chapters=[]),
            TestAct(act_number=3, title="Resolution", chapters=[
                TestChapter(chapter_number=3, scenes=[
                    TestScene(scene_number=1, title="Battle", summary="They fight an unrelated villain in a warehouse.")
                ])
            ]),
        ],
    )
    diags = run_genre_diagnostics(updated, blueprint)
    rules = [d.rule for d in diags]
    assert "genre.erotic_fiction.resolution_addresses_erotic_arc" in rules


def test_recommendation_durability_across_process_restart(tmp_path: Path):
    from auteur.genre_packs.recommendation import save_recommendation, load_recommendation, _PENDING_RECOMMENDATIONS
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)
    save_recommendation(rec, tmp_path)
    rec_id = rec.recommendation_id

    # 1. Simulate process restart by wiping in-memory dictionary
    _PENDING_RECOMMENDATIONS.clear()

    # 2. Inspect recommendation from stored ID
    reloaded_rec = load_recommendation(rec_id, tmp_path)
    assert reloaded_rec.recommendation_id == rec_id
    assert reloaded_rec.recommended_profile_id == rec.recommended_profile_id
    assert reloaded_rec.confidence == rec.confidence

    # 3. Accept recommendation
    updated = reconcile_identity_with_recommendation(ident, reloaded_rec)
    p = tmp_path / "story_identity.yaml"
    updated.to_yaml(p)

    # 4. Simulate process restart again
    _PENDING_RECOMMENDATIONS.clear()

    # 5. Inspect original recommendation after restart and acceptance
    post_accept_rec = load_recommendation(rec_id, tmp_path)
    assert post_accept_rec.recommendation_id == rec_id
    assert post_accept_rec.recommended_profile_id == rec.recommended_profile_id


def test_cli_human_json_semantic_parity():
    rec = recommend_genre_profile("A psychological story of desire and identity facades.")
    data = rec.model_dump(mode="json")
    
    # Assert exact semantic parity across representation formats
    assert data["recommendation_id"] == rec.recommendation_id
    assert data["recommended_pack_id"] == rec.recommended_pack_id
    assert data["recommended_pack_version"] == rec.recommended_pack_version
    assert data["recommended_profile_id"] == rec.recommended_profile_id
    assert data["confidence"] == rec.confidence
    assert data["why_this_is_best"] == rec.why_this_is_best
    assert len(data["rejected_profiles"]) == len(rec.rejected_profiles)


def test_accepted_identity_pack_version_stability(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)
    rec = recommend_genre_profile(ident.core_answer)
    updated = reconcile_identity_with_recommendation(ident, rec)
    
    p = tmp_path / "story_identity.yaml"
    updated.to_yaml(p)

    # Reload identity and verify accepted profile remains pinned
    reloaded = StoryIdentity.from_yaml(p)
    assert reloaded.genre_profile.primary_pack_version == "0.1.0"
    assert reloaded.genre_profile.pack_content_hash == rec.pack_content_hash
    assert reloaded.genre_profile.primary_profile_id == "erotic_psychological_drama"


def test_recommendation_project_local_authority_and_isolation(tmp_path: Path):
    from auteur.genre_packs.recommendation import save_recommendation, load_recommendation, _PENDING_RECOMMENDATIONS
    proj_a = tmp_path / "proj_a"
    proj_b = tmp_path / "proj_b"
    proj_a.mkdir()
    proj_b.mkdir()

    rec_a = recommend_genre_profile("Project A story of passion")
    save_recommendation(rec_a, proj_a)
    rec_id = rec_a.recommendation_id

    # Clear memory cache
    _PENDING_RECOMMENDATIONS.clear()

    # Proj A loads rec_a cleanly
    loaded_a = load_recommendation(rec_id, proj_a)
    assert loaded_a.recommendation_id == rec_id

    # Clear memory cache
    _PENDING_RECOMMENDATIONS.clear()

    # Proj B cannot cross-resolve rec_a (isolation enforced)
    with pytest.raises(GenrePackError) as exc_info:
        load_recommendation(rec_id, proj_b)
    assert exc_info.value.code == GenreErrorCode.RECOMMENDATION_NOT_FOUND


def test_recommendation_atomic_write_safety(tmp_path: Path):
    from auteur.genre_packs.recommendation import _atomic_write_json
    rec = recommend_genre_profile("Test atomic write")
    target_file = tmp_path / ".auteur" / "genre_recommendations" / f"{rec.recommendation_id}.json"

    _atomic_write_json(target_file, rec.model_dump(mode="json"))
    assert target_file.exists()
    
    # Ensure no leftover temp files exist
    temp_files = list(target_file.parent.glob(".tmp_*"))
    assert len(temp_files) == 0


def test_recommendation_survives_restart_and_project_relocation(tmp_path: Path):
    from auteur.genre_packs.recommendation import save_recommendation, load_recommendation, _PENDING_RECOMMENDATIONS
    import shutil
    orig_proj = tmp_path / "original_proj"
    orig_proj.mkdir()

    rec = recommend_genre_profile("Story surviving relocation")
    save_recommendation(rec, orig_proj)
    rec_id = rec.recommendation_id

    # Relocate project directory
    new_proj = tmp_path / "relocated_proj"
    shutil.move(str(orig_proj), str(new_proj))

    # Clear in-memory store
    _PENDING_RECOMMENDATIONS.clear()

    # Inspect from relocated path succeeds because artifact is project-local
    reloaded = load_recommendation(rec_id, new_proj)
    assert reloaded.recommendation_id == rec_id
    assert reloaded.recommended_profile_id == rec.recommended_profile_id


def test_project_local_artifact_missing_no_silent_global_fallback(tmp_path: Path):
    from auteur.genre_packs.recommendation import save_recommendation, load_recommendation, _PENDING_RECOMMENDATIONS
    proj = tmp_path / "proj_missing"
    proj.mkdir()
    rec = recommend_genre_profile("Testing no silent global fallback")
    save_recommendation(rec, proj)
    rec_id = rec.recommendation_id

    # Delete project-local recommendation artifact
    local_file = proj / ".auteur" / "genre_recommendations" / f"{rec_id}.json"
    local_file.unlink()

    # Clear memory cache
    _PENDING_RECOMMENDATIONS.clear()

    # Attempting to load project recommendation must NOT silently load from global cache
    with pytest.raises(GenrePackError) as exc_info:
        load_recommendation(rec_id, proj)
    assert exc_info.value.code == GenreErrorCode.RECOMMENDATION_NOT_FOUND


def test_project_local_artifact_malformed_reports_corruption(tmp_path: Path):
    from auteur.genre_packs.recommendation import save_recommendation, load_recommendation, _PENDING_RECOMMENDATIONS
    proj = tmp_path / "proj_malformed"
    proj.mkdir()
    rec = recommend_genre_profile("Testing malformed local artifact")
    save_recommendation(rec, proj)
    rec_id = rec.recommendation_id

    # Corrupt local artifact
    local_file = proj / ".auteur" / "genre_recommendations" / f"{rec_id}.json"
    local_file.write_text("{invalid_json: true", encoding="utf-8")

    # Clear memory cache
    _PENDING_RECOMMENDATIONS.clear()

    with pytest.raises(GenrePackError) as exc_info:
        load_recommendation(rec_id, proj)
    assert exc_info.value.code == GenreErrorCode.RECOMMENDATION_NOT_FOUND
    assert "Corrupt" in str(exc_info.value)


def test_two_projects_same_recommendation_id_isolated(tmp_path: Path):
    from auteur.genre_packs.recommendation import save_recommendation, load_recommendation, _PENDING_RECOMMENDATIONS
    proj_a = tmp_path / "proj_a"
    proj_b = tmp_path / "proj_b"
    proj_a.mkdir(); proj_b.mkdir()

    rec_a = recommend_genre_profile("Premise A")
    save_recommendation(rec_a, proj_a)
    
    # Save rec with same ID in project B but different premise
    rec_b = recommend_genre_profile("Premise B")
    rec_b.recommendation_id = rec_a.recommendation_id
    save_recommendation(rec_b, proj_b)

    _PENDING_RECOMMENDATIONS.clear()

    loaded_a = load_recommendation(rec_a.recommendation_id, proj_a)
    loaded_b = load_recommendation(rec_a.recommendation_id, proj_b)

    assert loaded_a.why_this_is_best == rec_a.why_this_is_best
    assert loaded_b.why_this_is_best == rec_b.why_this_is_best


def test_global_only_recommendation_cannot_be_treated_as_project_bound(tmp_path: Path):
    from auteur.genre_packs.recommendation import save_recommendation, load_recommendation, _PENDING_RECOMMENDATIONS
    rec = recommend_genre_profile("Global recommendation premise")
    save_recommendation(rec, project_dir=None)
    rec_id = rec.recommendation_id

    _PENDING_RECOMMENDATIONS.clear()

    proj = tmp_path / "some_proj"
    proj.mkdir()

    # Querying global recommendation with project_dir should fail
    with pytest.raises(GenrePackError) as exc_info:
        load_recommendation(rec_id, proj)
    assert exc_info.value.code == GenreErrorCode.RECOMMENDATION_NOT_FOUND


def test_installed_genre_pack_journey(tmp_path: Path):
    ident = _make_minimal_identity(tmp_path)

    # 1. Recommend
    rec = recommend_genre_profile(ident.core_answer)
    assert rec.recommended_pack_id == "erotic_fiction"

    # 2. Accept
    updated = reconcile_identity_with_recommendation(ident, rec)
    p = tmp_path / "story_identity.yaml"
    updated.to_yaml(p)

    # 3. Reload & Validate
    reloaded = StoryIdentity.from_yaml(p)
    assert reloaded.genre_profile.primary_profile_id == rec.recommended_profile_id

    diags = validate_genre_profile_identity(reloaded)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 0
