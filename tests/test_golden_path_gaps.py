"""Tests for Auteur v0.36 Golden-Path Gap Repairs.

Verifies:
1. Genre Pack domain applicability and abstention.
2. Built-in Genre Pack profile recognition in StoryIdentity validation.
3. LLM API key prerequisite handling in identity recommend.
4. Offline StoryIdentity initialization via `auteur identity init`.
5. Prerequisites orchestration during genre recommendation acceptance when story_identity.yaml is missing.
"""


from auteur.genre_packs.models import (
    PackApplicabilityStatus,
    GenreRecommendationAdvisory,
    GenreRecommendation,
)
from auteur.genre_packs.recommendation import (
    evaluate_pack_applicability,
    recommend_genre_profile,
)
from auteur.identity import StoryIdentity


def test_pack_applicability_erotic_fiction():
    """Erotic fiction premises should evaluate as APPLICABLE."""
    premise = (
        "A marine biologist trapped in a storm with her rival must choose "
        "between guarded autonomy and intense physical desire and intimacy."
    )
    eval_result = evaluate_pack_applicability(premise, "erotic_fiction")
    assert eval_result.status == PackApplicabilityStatus.APPLICABLE
    assert eval_result.applicability_score >= 0.30
    assert len(eval_result.matched_signals) > 0


def test_pack_applicability_sci_fi_mystery_abstention():
    """Non-erotic sci-fi murder mystery premises should evaluate as NOT_APPLICABLE and abstain."""
    premise = (
        "In a subterranean atmospheric research station on Titan, Inspector Kieran Vance "
        "investigates the mysterious death of an engineer locked inside an airlock. "
        "The only witness is a damaged synth-mind with corrupted logs."
    )
    eval_result = evaluate_pack_applicability(premise, "erotic_fiction")
    assert eval_result.status == PackApplicabilityStatus.NOT_APPLICABLE
    assert eval_result.applicability_score < 0.10

    # Running recommend_genre_profile should return GenreRecommendationAdvisory
    result = recommend_genre_profile(premise, pack_id="erotic_fiction")
    assert isinstance(result, GenreRecommendationAdvisory)
    assert result.status == "no_applicable_pack"
    assert "No installed Genre Pack is a strong fit" in result.message


def test_identity_validate_recognizes_pack_profiles():
    """StoryIdentity validate must recognize built-in GenrePack subgenre profiles without unknown warnings."""
    identity_data = {
        "title": "The Tides of Autonomy",
        "core_answer": "A biologist trapped with her rival chooses between autonomy and intimacy.",
        "target_experience": {
            "primary": "desire",
            "progression": "desire -> vulnerability",
            "avoid": ["fluff"],
        },
        "story_type": {
            "medium": "novel",
            "mode": "intimate",
            "genre": "erotic_fiction",
            "subgenres": ["erotic_psychological_drama"],
            "target_audience": "adult",
        },
        "central_engine": {
            "want": "Elena wants to save the ecosystem.",
            "resistance": "Working with Marcus exposes her vulnerabilities.",
            "conflict": "Surrendering to intimacy risks her defenses.",
            "stakes": "Her career and guarded self-identity.",
            "change": "Elena transforms from guarded to accepting intimacy.",
        },
        "genre_profile": {
            "primary_pack_id": "erotic_fiction",
            "primary_pack_version": "0.1.0",
            "pack_content_hash": "1b128b997f2d1d48169f88a128075ec97b90325fee4dd8d184ec91e5ec4f62b8",
            "primary_profile_id": "erotic_psychological_drama",
            "accepted_target_emotions": {"desire": 1.0},
            "accepted_narrative_engine": "erotic_identity_transformation",
            "accepted_framing": {"primary": "unsettling", "secondary": ["unsettling"]},
            "accepted_resolution_contract": {
                "pattern": "transformative_resolution",
                "required_outcomes": ["psychological_transformation"],
                "rejected_outcomes": ["superficial_happy_ending"],
            },
            "adherence_posture": "conventional",
        },
    }

    identity = StoryIdentity.model_validate(identity_data)
    diagnostics = identity.validate_identity()
    unknown_warnings = [d for d in diagnostics if d.rule == "identity.subgenre.unknown"]
    assert len(unknown_warnings) == 0, f"Unexpected unknown subgenre warnings: {unknown_warnings}"


def test_identity_init_creates_editable_skeleton(tmp_path):
    """auteur identity init should create a valid editable StoryIdentity skeleton."""
    from auteur.cli_handlers import handle_identity_init

    premise = "A detective investigates a locked-room mystery on a space station."
    output_path = tmp_path / "story_identity.yaml"

    result = handle_identity_init(premise_text=premise, output_path=output_path, title="Space Station Mystery")
    assert result.is_success
    assert output_path.exists()

    # Verify produced identity is valid
    identity = StoryIdentity.from_yaml(output_path)
    assert identity.title == "Space Station Mystery"
    assert identity.story_type.genre.value is not None


def test_genre_recommendation_accept_missing_identity_guidance(tmp_path):
    """Accepting a genre recommendation when story_identity.yaml is missing must safely inform user without mutating."""
    from auteur.genre_packs.recommendation import save_recommendation
    from auteur.genre_packs.cli import dispatch_genre_pack_commands
    from argparse import Namespace

    rec = GenreRecommendation(
        recommendation_id="rec_test123",
        recommended_pack_id="erotic_fiction",
        recommended_pack_version="0.1.0",
        pack_content_hash="1b128b99",
        recommended_profile_id="erotic_psychological_drama",
        recommended_profile_display_name="Erotic Psychological Drama",
        confidence=0.88,
        best_basis="GENRE_ALIGNED",
        why_this_is_best="Test rationale",
        supporting_evidence=["test"],
        recommended_emotional_targets={"desire": 1.0},
        recommended_narrative_engine="erotic_identity_transformation",
        recommended_framing={"primary": "unsettling", "secondary": ["unsettling"]},
        recommended_resolution_contract={
            "pattern": "transformative_resolution",
            "required_outcomes": ["test"],
            "rejected_outcomes": [],
        },
        rejected_profiles=[],
        warnings=[],
        questions_or_uncertainties=[],
        created_at="2026-07-26T00:00:00Z",
    )

    save_recommendation(rec, project_dir=tmp_path)

    # Attempt accept on empty tmp_path (no story_identity.yaml exists)
    args = Namespace(
        genre_command="recommendation",
        recommendation_command="accept",
        rec_id="rec_test123",
        project=tmp_path,
        confirm=True,
        json=False,
    )
    exit_code = dispatch_genre_pack_commands(args)
    assert exit_code != 0

    # Ensure saved recommendation is still present
    rec_file = tmp_path / ".auteur" / "genre_recommendations" / "rec_test123.json"
    assert rec_file.exists()


# =====================================================================
# ADVERSARIAL APPLICABILITY TEST MATRIX (Section 5)
# =====================================================================

def test_adversarial_matrix_negation_challenges():
    """Negated domain cues must trigger NOT_APPLICABLE status with low score."""
    from auteur.genre_packs.recommendation import evaluate_pack_applicability
    from auteur.genre_packs.models import PackApplicabilityStatus

    negated_premises = [
        "She rejects desire and avoids all intimacy.",
        "The cult attempts erotic manipulation, but the protagonist is never attracted and the plot centers on escape. This is non-erotic.",
        "This is not an erotic story; it is a platonic only drama.",
    ]
    for premise in negated_premises:
        res = evaluate_pack_applicability(premise, "erotic_fiction")
        assert res.status == PackApplicabilityStatus.NOT_APPLICABLE
        assert res.applicability_score == 0.05


def test_adversarial_matrix_clear_negatives():
    """Non-domain premises must result in abstention advisory."""
    from auteur.genre_packs.recommendation import recommend_genre_profile
    from auteur.genre_packs.models import GenreRecommendationAdvisory

    negative_premises = [
        "Chief Inspector Kieran Vance investigates a locked-room mystery on Titan.",
        "A squad of elite infantry defends a mountain pass against armored divisions.",
        "A quiet family tries to organize a surprise birthday party while dodging comical mishaps.",
        "A technical handbook detailing rust memory layout and compiler optimization flags.",
    ]
    for premise in negative_premises:
        res = recommend_genre_profile(premise)
        assert isinstance(res, GenreRecommendationAdvisory)
        assert res.status == "no_applicable_pack"
        assert res.mutated_state is False


def test_adversarial_matrix_input_robustness():
    """Empty, whitespace, unicode, and extreme length inputs must not crash."""
    from auteur.genre_packs.recommendation import evaluate_pack_applicability
    from auteur.genre_packs.models import PackApplicabilityStatus

    inputs = [
        "",
        "   ",
        "A" * 10000,
        "Café romance de l'amour et désir 💖 🔥 🔥",
        "!!!???!!!",
    ]
    for inp in inputs:
        res = evaluate_pack_applicability(inp, "erotic_fiction")
        assert isinstance(res.status, PackApplicabilityStatus)
        assert 0.0 <= res.applicability_score <= 1.0


# =====================================================================
# ADVISORY RESULT COMPATIBILITY AUDIT (Section 6)
# =====================================================================

def test_advisory_result_compatibility_properties():
    """GenreRecommendationAdvisory must adhere strictly to advisory contract semantics."""
    from auteur.genre_packs.models import GenreRecommendationAdvisory, PackApplicabilityEvaluation, PackApplicabilityStatus

    eval_item = PackApplicabilityEvaluation(
        pack_id="erotic_fiction",
        version="0.1.0",
        status=PackApplicabilityStatus.NOT_APPLICABLE,
        applicability_score=0.05,
        explanation="Test explanation",
    )
    adv = GenreRecommendationAdvisory(
        status="no_applicable_pack",
        message="No match",
        evaluated_packs=[eval_item],
        recommended_next_actions=["action 1"],
        mutated_state=False,
    )
    assert adv.status == "no_applicable_pack"
    assert adv.mutated_state is False
    assert not hasattr(adv, "recommendation_id")
    assert not hasattr(adv, "recommended_profile_id")


# =====================================================================
# IDENTITY INIT AUTHORITY SEMANTICS AUDIT (Section 7)
# =====================================================================

def test_identity_init_authority_semantics(tmp_path):
    """auteur identity init must mark placeholders clearly and preserve user inputs."""
    from auteur.cli_handlers import handle_identity_init

    output = tmp_path / "story_identity.yaml"
    res = handle_identity_init(
        premise_text="A space detective investigates a mystery.",
        output_path=output,
        title="Custom Title",
        genre="Sci-Fi",
    )
    assert res.is_success
    identity = StoryIdentity.from_yaml(output)

    assert identity.title == "Custom Title"
    assert identity.story_type.genre.value == "sci_fi"
    assert identity.confidence is None  # Un-evaluated offline skeleton has no AI confidence claim!
    assert "Seeded offline identity skeleton" in identity.why_this_is_best
    assert identity.genre_profile is None  # Zero unearned GenreProfileCommitment!


def test_identity_init_refuses_overwrite_without_force(tmp_path):
    """handle_identity_init must fail if file exists and overwrite is False."""
    from auteur.cli_handlers import handle_identity_init

    output = tmp_path / "story_identity.yaml"
    output.write_text("existing content", encoding="utf-8")

    res = handle_identity_init(premise_text="New premise", output_path=output, overwrite=False)
    assert not res.is_success
    assert "already exists" in res.error


# =====================================================================
# PACK VERSION & PROVENANCE VALIDATION AUDIT (Section 10)
# =====================================================================

def test_identity_subgenre_unknown_validation():
    """StoryIdentity.validate_identity should pass built-in profiles and warn on unknown ones."""
    identity_dict = {
        "title": "Test Title",
        "core_answer": "Core Answer",
        "target_experience": {"primary": "dread"},
        "story_type": {
            "medium": "novel",
            "mode": "tragic",
            "genre": "grimdark_fantasy",
            "subgenres": ["erotic_psychological_drama"],
        },
        "central_engine": {
            "want": "want",
            "resistance": "resistance",
            "conflict": "conflict",
            "stakes": "stakes",
            "change": "change",
        },
    }
    identity = StoryIdentity(**identity_dict)
    report = identity.validate_identity()

    # Valid profile should NOT produce subgenre unknown warning
    subgenre_warnings = [w for w in report if getattr(w, "rule", None) == "identity.subgenre.unknown"]
    assert len(subgenre_warnings) == 0

    # Arbitrary unknown subgenre MUST still produce warning
    identity_dict["story_type"]["subgenres"] = ["random_unregistered_subgenre"]
    identity_unknown = StoryIdentity(**identity_dict)
    report_unknown = identity_unknown.validate_identity()
    subgenre_warnings_unknown = [w for w in report_unknown if getattr(w, "rule", None) == "identity.subgenre.unknown"]
    assert len(subgenre_warnings_unknown) == 1


# =====================================================================
# V0.37.X HARDENING TESTS (F-01, F-02, F-03)
# =====================================================================

def test_negation_explicit_global_domain_negation():
    """Explicit domain negation like 'This is not an erotic story' must evaluate as NOT_APPLICABLE."""
    negated_premises = [
        "This is not an erotic story. A detective investigates sabotage aboard a research station.",
        "The story is not erotic and contains no romance or intimacy.",
        "Attraction is not part of the story. The protagonist escapes a cult.",
        "A scholar studies erotic literature in a university library.",
        "A film critic analyzes erotic horror movies for a journal article.",
    ]
    for premise in negated_premises:
        eval_result = evaluate_pack_applicability(premise, "erotic_fiction")
        assert eval_result.status == PackApplicabilityStatus.NOT_APPLICABLE
        assert eval_result.applicability_score < 0.10


def test_negation_character_denial_with_positive_evidence():
    """Character denial inside an in-domain premise must not cause false abstention when positive evidence exists."""
    in_domain_premises = [
        "She denies her desire in public, but private longing and physical intimacy drive every decision.",
        "He insists the relationship is not romantic, while their erotic obsession intensifies.",
    ]
    for premise in in_domain_premises:
        eval_result = evaluate_pack_applicability(premise, "erotic_fiction")
        assert eval_result.status == PackApplicabilityStatus.APPLICABLE
        assert eval_result.applicability_score >= 0.40


def test_cli_override_requires_confirm(tmp_path):
    """genre recommendation override must refuse mutation without --confirm flag."""
    from argparse import Namespace
    from auteur.genre_packs.cli import dispatch_genre_pack_commands
    from auteur.identity import StoryIdentity

    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    identity_path = project_dir / "story_identity.yaml"

    # Initialize skeleton
    StoryIdentity(
        title="Test Title",
        core_answer="Core answer",
        target_experience={"primary": "desire"},
        story_type={"medium": "novel", "mode": "intimate", "genre": "erotic_fiction"},
        central_engine={"want": "w", "resistance": "r", "conflict": "c", "stakes": "s", "change": "ch"}
    ).to_yaml(identity_path)

    # Attempt override without --confirm
    args_no_confirm = Namespace(
        genre_command="recommendation",
        recommendation_command="override",
        rec_id="rec_12345",
        project=project_dir,
        target="erotic_romance",
        replacement="erotic_psychological_drama",
        rationale="Author rationale",
        confirm=False,
        json=False,
    )
    exit_code = dispatch_genre_pack_commands(args_no_confirm)
    assert exit_code == 1

    # Verify StoryIdentity was NOT mutated
    identity_after = StoryIdentity.from_yaml(identity_path)
    assert identity_after.genre_profile is None


def test_pydantic_v2_configdict_import_warnings():
    """Importing scene_state module should produce no Pydantic deprecation warnings."""
    import warnings

    with warnings.catch_warnings(record=True) as recorded_warnings:
        warnings.simplefilter("always")
        import importlib
        import auteur.narrative_realization.schema.scene_state as scene_state
        importlib.reload(scene_state)

        pydantic_warnings = [
            w for w in recorded_warnings
            if "PydanticDeprecatedSince20" in str(w.message) or "class-based `config`" in str(w.message)
        ]
        assert len(pydantic_warnings) == 0



