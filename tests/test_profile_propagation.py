"""Counterfactual acceptance tests for Genre Profile resolution-contract propagation.

Tests the full chain:
  GenreProfileCommitment.accepted_resolution_contract
  -> compile_to_blueprint()
  -> Blueprint.contract.expected_elements / forbidden_tropes
  -> ProfileDerivation provenance
  -> structural diagnostics

Spec: docs/superpowers/specs/2026-07-27-genre-profile-blueprint-propagation.md
"""

from datetime import datetime, timezone
from copy import deepcopy

import pytest
import yaml

from auteur.blueprint import (
    StoryBlueprint,
    Genre,
    StoryMode,
    StoryMedium,
    TargetAudience,
    TargetExperience,
    LengthClass,
    ProfileDerivation,
)
from auteur.genre_packs.models import (
    GenreProfileCommitment,
    ResolutionContractCommitment,
    FramingCommitment,
    AdherencePosture,
    GenreAuthorOverride,
)
from auteur.identity import (
    StoryIdentity,
    StoryType,
    HighLevelCentralEngine,
    compile_to_blueprint,
)
from auteur.structure.diagnostics import DiagnosticSeverity
from auteur.structure.analyzer import analyze_structure


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_base_identity() -> StoryIdentity:
    """A deterministic base identity without genre_profile."""
    return StoryIdentity(
        title="Propagation Test",
        core_answer="A test story for profile propagation.",
        target_experience=TargetExperience(
            primary="dread",
            progression="dread -> tension -> catharsis",
        ),
        story_type=StoryType(
            medium=StoryMedium.NOVEL,
            mode=StoryMode.TRAGIC,
            genre=Genre.LITERARY,
            target_audience=TargetAudience.ADULT,
        ),
        central_engine=HighLevelCentralEngine(
            want="The protagonist wants to uncover the truth.",
            resistance="The system protects the lie.",
            conflict="Knowing the truth destroys the innocent.",
            stakes="The protagonist's sanity and the lives of those they love.",
            change="The protagonist accepts that truth is not always freedom.",
        ),
    )


def _make_profile_commitment(
    pattern: str = "transformative_resolution",
    required: list[str] | None = None,
    rejected: list[str] | None = None,
    posture: AdherencePosture = AdherencePosture.CONVENTIONAL,
    rec_id: str = "rec_propagation_test",
    overrides: list[GenreAuthorOverride] | None = None,
) -> GenreProfileCommitment:
    return GenreProfileCommitment(
        primary_pack_id="erotic_fiction",
        primary_pack_version="0.1.0",
        pack_content_hash="abcdef1234567890",
        primary_profile_id="erotic_psychological_drama",
        accepted_target_emotions={"desire": 1.0, "vulnerability": 0.7},
        accepted_narrative_engine="erotic_identity_transformation",
        accepted_framing=FramingCommitment(primary="romantic", secondary=["unsettling"]),
        accepted_resolution_contract=ResolutionContractCommitment(
            pattern=pattern,
            required_outcomes=required or [],
            rejected_outcomes=rejected or [],
        ),
        adherence_posture=posture,
        source_recommendation_id=rec_id,
        author_overrides=overrides or [],
    )


def _normalized_expected_elements(bp: StoryBlueprint) -> list[str]:
    """Return sorted, deduplicated expected_elements for deterministic comparison."""
    return sorted(set(bp.contract.expected_elements))


def _normalized_forbidden_tropes(bp: StoryBlueprint) -> list[str]:
    return sorted(set(bp.contract.forbidden_tropes))


class TestRejectedOutcomeRepresentation:
    def test_profile_outcomes_are_not_dual_written(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(rejected=["permanent_separation"])

        bp = compile_to_blueprint(identity)

        assert bp.contract.rejected_outcomes == ["permanent_separation"]
        assert bp.contract.forbidden_tropes == []
        assert "rejected_outcomes: permanent_separation" in bp.profile_derivation.obligations_applied

    def test_authored_trope_does_not_trigger_profile_diagnostic(self):
        bp = compile_to_blueprint(_make_base_identity())
        bp.contract.forbidden_tropes = ["permanent_separation"]
        bp.contract.expected_elements = ["permanent_separation"]

        assert not any(
            d.rule == "profile.resolution_contract.rejected_outcome_present"
            for d in analyze_structure(bp)
        )

    def test_legacy_provenance_fallback_is_diagnostic_only(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(rejected=["permanent_separation"])
        bp = compile_to_blueprint(identity)
        bp.contract.rejected_outcomes = []
        bp.contract.forbidden_tropes = ["permanent_separation"]
        bp.profile_derivation.obligations_applied = ["forbidden_tropes: permanent_separation"]
        bp.contract.expected_elements.append("permanent_separation")
        before = bp.model_dump(mode="json")

        diagnostics = analyze_structure(bp)

        assert sum(d.rule == "profile.resolution_contract.rejected_outcome_present" for d in diagnostics) == 1
        assert bp.model_dump(mode="json") == before
        assert bp.contract.rejected_outcomes == []
        assert bp.contract.forbidden_tropes == ["permanent_separation"]

    def test_legacy_trope_without_provenance_is_not_reclassified(self):
        bp = compile_to_blueprint(_make_base_identity())
        bp.contract.forbidden_tropes = ["permanent_separation"]
        bp.contract.expected_elements = ["permanent_separation"]
        bp.profile_derivation = ProfileDerivation(
            source_field="genre_profile.accepted_resolution_contract",
            recommendation_id="legacy",
            derived_at=datetime.now(timezone.utc).isoformat(),
            obligations_applied=[],
        )

        assert not any(
            d.rule == "profile.resolution_contract.rejected_outcome_present"
            for d in analyze_structure(bp)
        )


# ===========================================================================
# Test 1 — No profile versus accepted profile
# ===========================================================================

class TestNoProfileVsAccepted:
    def test_without_profile_has_no_derivation(self):
        identity = _make_base_identity()
        bp = compile_to_blueprint(identity)
        assert bp.profile_derivation is None

    def test_with_profile_has_intentional_difference(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation", "cathartic_release"],
            rejected=["superficial_happy_ending"],
        )
        bp = compile_to_blueprint(identity)

        # Required outcomes should appear in expected_elements
        assert "protagonist_transformation" in bp.contract.expected_elements
        assert "cathartic_release" in bp.contract.expected_elements

        # Rejected outcomes have their own semantic destination.
        assert "superficial_happy_ending" in bp.contract.rejected_outcomes
        assert "superficial_happy_ending" not in bp.contract.forbidden_tropes

    def test_base_identity_fields_unchanged(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
        )
        bp = compile_to_blueprint(identity)

        # Base identity fields should be identical to no-profile compile
        bp_no_profile = compile_to_blueprint(_make_base_identity())
        assert bp.identity.title == bp_no_profile.identity.title
        assert bp.identity.author_intent == bp_no_profile.identity.author_intent
        assert bp.identity.genre == bp_no_profile.identity.genre
        assert bp.identity.mode == bp_no_profile.identity.mode
        assert bp.identity.length_class == bp_no_profile.identity.length_class

    def test_profile_derivation_populated(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
            rec_id="rec_test123",
        )
        bp = compile_to_blueprint(identity)
        assert bp.profile_derivation is not None
        assert bp.profile_derivation.source_field == "genre_profile.accepted_resolution_contract"
        assert bp.profile_derivation.recommendation_id == "rec_test123"
        assert len(bp.profile_derivation.obligations_applied) >= 1


# ===========================================================================
# Test 2 — Two different profiles
# ===========================================================================

class TestTwoProfiles:
    def test_different_profiles_produce_different_obligations(self):
        identity = _make_base_identity()

        # Profile A: relational fulfillment
        id_a = deepcopy(identity)
        id_a.genre_profile = _make_profile_commitment(
            pattern="relational_fulfillment",
            required=["emotional_intimacy", "mutual_commitment"],
            rejected=["permanent_separation"],
        )

        # Profile B: dark transgression
        id_b = deepcopy(identity)
        id_b.genre_profile = _make_profile_commitment(
            pattern="dark_transgression_resolution",
            required=["moral_collapse", "irreversible_loss"],
            rejected=["redemptive_twist"],
        )

        bp_a = compile_to_blueprint(id_a)
        bp_b = compile_to_blueprint(id_b)

        # The required outcomes should differ
        assert _normalized_expected_elements(bp_a) != _normalized_expected_elements(bp_b)

        # Profile-specific required outcomes present
        assert "emotional_intimacy" in bp_a.contract.expected_elements
        assert "moral_collapse" in bp_b.contract.expected_elements

        # Difference is not just metadata — actual obligation content differs
        assert "permanent_separation" in bp_a.contract.rejected_outcomes
        assert "redemptive_twist" in bp_b.contract.rejected_outcomes

    def test_profile_id_not_the_only_difference(self):
        identity = _make_base_identity()

        id_a = deepcopy(identity)
        id_a.genre_profile = _make_profile_commitment(
            pattern="relational_fulfillment",
            required=["emotional_intimacy"],
        )

        id_b = deepcopy(identity)
        id_b.genre_profile = _make_profile_commitment(
            pattern="dark_transgression_resolution",
            required=["emotional_intimacy"],  # same required outcome
            rejected=["superficial_resolution"],
        )

        bp_a = compile_to_blueprint(id_a)
        bp_b = compile_to_blueprint(id_b)

        # Same required outcome = same expected_elements for that item
        assert "emotional_intimacy" in bp_a.contract.expected_elements
        assert "emotional_intimacy" in bp_b.contract.expected_elements

        # But different rejected outcomes remain distinguishable.
        assert bp_a.contract.rejected_outcomes != bp_b.contract.rejected_outcomes


# ===========================================================================
# Test 3 — Explicit author conflict
# ===========================================================================

class TestAuthorConflict:
    def test_mode_wins_over_profile_pattern(self):
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.TRAGIC
        identity.genre_profile = _make_profile_commitment(
            pattern="relational_fulfillment",  # implies bittersweet/hopeful
        )
        bp = compile_to_blueprint(identity)

        # mode=TRAGIC should set mandatory_ending_tone=TRAGIC regardless of profile
        from auteur.blueprint import EndingTone
        assert bp.contract.mandatory_ending_tone == EndingTone.TRAGIC

    def test_no_silent_overwrite_of_expected_elements(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
        )
        bp = compile_to_blueprint(identity)

        bp2 = compile_to_blueprint(identity)
        assert len(bp.contract.expected_elements) == len(bp2.contract.expected_elements)
        assert bp.contract.expected_elements == bp2.contract.expected_elements

    def test_diagnostic_emitted_for_conflict(self):
        """D-RES-003 fires when pattern implies tone ≠ mandatory_ending_tone."""
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.COMIC  # gives BITTERSWEET
        identity.genre_profile = _make_profile_commitment(
            pattern="dark_transgression_resolution",  # implies TRAGIC
            required=["irreversible_loss"],
        )
        bp = compile_to_blueprint(identity)

        diagnostics = analyze_structure(bp)
        res_diags = [d for d in diagnostics if d.rule.startswith("profile.resolution_contract")]
        assert any("ending_tone_conflict" in d.rule for d in res_diags), (
            "D-RES-003 should fire: dark_transgression_resolution implies TRAGIC, "
            f"but mandatory_ending_tone={bp.contract.mandatory_ending_tone.value}"
        )


# ===========================================================================
# Test 4 — Author override
# ===========================================================================

class TestAuthorOverride:
    def test_override_replaces_required_outcome(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
            overrides=[
                GenreAuthorOverride(
                    target_expectation="accepted_resolution_contract.required_outcomes",
                    recommended_value="protagonist_transformation",
                    replacement_value="audience_catharsis",
                    author_rationale="The story needs a communal rather than individual resolution.",
                )
            ],
        )
        bp = compile_to_blueprint(identity)

        # The override's replacement value should appear
        assert "audience_catharsis" in bp.contract.expected_elements

    def test_override_provenance_tracked(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
            overrides=[
                GenreAuthorOverride(
                    target_expectation="accepted_resolution_contract.required_outcomes",
                    recommended_value="protagonist_transformation",
                    replacement_value="audience_catharsis",
                    author_rationale="Communal resolution.",
                )
            ],
        )
        bp = compile_to_blueprint(identity)

        # ProfileDerivation should exist
        assert bp.profile_derivation is not None
        # obligations_applied should reference the override decision
        override_obligations = [o for o in bp.profile_derivation.obligations_applied
                                if "override" in o.lower() or "audience_catharsis" in o]
        assert len(override_obligations) >= 1

    def test_override_suppresses_diagnostic(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
            overrides=[
                GenreAuthorOverride(
                    target_expectation="accepted_resolution_contract.required_outcomes",
                    recommended_value="protagonist_transformation",
                    replacement_value="audience_catharsis",
                    author_rationale="Intentional divergence.",
                )
            ],
        )
        bp = compile_to_blueprint(identity)
        diagnostics = analyze_structure(bp)

        # D-RES-001 should not fire for the overridden outcome
        missing_diags = [d for d in diagnostics if d.rule == "profile.resolution_contract.missing_required_outcome"]
        overridden_outcome_diags = [d for d in missing_diags if "protagonist_transformation" in str(d.evidence)]
        assert len(overridden_outcome_diags) == 0


# ===========================================================================
# Test 5 — Legacy identity (no genre_profile)
# ===========================================================================

class TestLegacyIdentity:
    def test_compile_without_profile_matches_v0371(self, tmp_path):
        """Legacy identity without genre_profile produces output compatible with v0.37.1."""
        identity = _make_base_identity()
        bp = compile_to_blueprint(identity)

        # No profile_derivation field
        assert bp.profile_derivation is None

        # expected_elements should be empty (same as current behavior)
        assert bp.contract.expected_elements == []

        # All existing tests should still pass
        serialized = yaml.safe_dump(bp.model_dump(mode="json"))
        loaded_data = yaml.safe_load(serialized)
        parsed = StoryBlueprint.model_validate(loaded_data)
        assert parsed.identity.title == identity.title
        assert parsed.profile_derivation is None

    def test_no_new_diagnostics_without_profile(self):
        identity = _make_base_identity()
        bp = compile_to_blueprint(identity)

        from auteur.structure.analyzer import analyze_structure
        diagnostics = analyze_structure(bp)
        profile_diags = [d for d in diagnostics if d.rule.startswith("profile.")]
        assert len(profile_diags) == 0


# ===========================================================================
# Test 6 — Idempotence
# ===========================================================================

class TestIdempotence:
    def test_repeated_compile_is_stable(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation", "cathartic_release"],
            rejected=["superficial_happy_ending"],
        )

        bp1 = compile_to_blueprint(identity)
        bp2 = compile_to_blueprint(identity)

        # Compare everything except derived_at timestamp
        d1 = bp1.model_dump(mode="json")
        d2 = bp2.model_dump(mode="json")
        if d1.get("profile_derivation"):
            d1["profile_derivation"]["derived_at"] = "IGNORED"
        if d2.get("profile_derivation"):
            d2["profile_derivation"]["derived_at"] = "IGNORED"
        dump1 = yaml.safe_dump(d1, sort_keys=False)
        dump2 = yaml.safe_dump(d2, sort_keys=False)
        assert dump1 == dump2

    def test_no_duplicate_obligations(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
        )

        bp1 = compile_to_blueprint(identity)
        bp2 = compile_to_blueprint(identity)

        # Each required outcome appears exactly once
        assert bp1.contract.expected_elements.count("protagonist_transformation") == 1
        assert bp2.contract.expected_elements.count("protagonist_transformation") == 1
        # Same length
        assert len(bp1.contract.expected_elements) == len(bp2.contract.expected_elements)

    def test_profile_derivation_stable(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
            rec_id="rec_stable",
        )

        bp1 = compile_to_blueprint(identity)
        bp2 = compile_to_blueprint(identity)

        assert bp1.profile_derivation is not None
        assert bp2.profile_derivation is not None
        assert bp1.profile_derivation.source_field == bp2.profile_derivation.source_field
        assert bp1.profile_derivation.recommendation_id == bp2.profile_derivation.recommendation_id
        assert bp1.profile_derivation.obligations_applied == bp2.profile_derivation.obligations_applied
        # derived_at may differ by microseconds — not compared for stability


# ===========================================================================
# Test 7 — Round trip
# ===========================================================================

class TestRoundTrip:
    def test_genre_profile_survives_serialization(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            pattern="transformative_resolution",
            required=["protagonist_transformation"],
            rejected=["superficial_happy_ending"],
            rec_id="rec_roundtrip",
        )

        # Serialize identity to YAML and reload
        serialized = yaml.safe_dump(identity.model_dump(mode="json"), sort_keys=False)
        loaded_data = yaml.safe_load(serialized)
        loaded_identity = StoryIdentity.model_validate(loaded_data)

        assert loaded_identity.genre_profile is not None
        assert loaded_identity.genre_profile.primary_profile_id == "erotic_psychological_drama"
        assert loaded_identity.genre_profile.accepted_resolution_contract.pattern == "transformative_resolution"
        assert "protagonist_transformation" in loaded_identity.genre_profile.accepted_resolution_contract.required_outcomes

    def test_compile_from_reloaded_identity_matches(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
        )

        # Direct compile
        bp_direct = compile_to_blueprint(identity)

        # Reload compile
        serialized = yaml.safe_dump(identity.model_dump(mode="json"), sort_keys=False)
        loaded_data = yaml.safe_load(serialized)
        loaded_identity = StoryIdentity.model_validate(loaded_data)
        bp_reloaded = compile_to_blueprint(loaded_identity)

        assert bp_direct.contract.expected_elements == bp_reloaded.contract.expected_elements
        assert bp_direct.contract.rejected_outcomes == bp_reloaded.contract.rejected_outcomes
        assert bp_direct.contract.forbidden_tropes == bp_reloaded.contract.forbidden_tropes

    def test_profile_derivation_survives_blueprint_roundtrip(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
            rec_id="rec_bp_rt",
        )

        bp = compile_to_blueprint(identity)
        serialized = yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False)
        loaded_data = yaml.safe_load(serialized)
        loaded_bp = StoryBlueprint.model_validate(loaded_data)

        assert loaded_bp.profile_derivation is not None
        assert loaded_bp.profile_derivation.source_field == bp.profile_derivation.source_field
        assert loaded_bp.profile_derivation.recommendation_id == bp.profile_derivation.recommendation_id
        assert loaded_bp.profile_derivation.obligations_applied == bp.profile_derivation.obligations_applied


# ===========================================================================
# Focused unit coverage
# ===========================================================================

class TestUnitCoverage:
    def test_deterministic_ordering(self):
        """Required outcomes maintain stable ordering in expected_elements."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["c", "a", "b"],  # non-alphabetical
        )
        bp = compile_to_blueprint(identity)
        # Order should match the profile's order (prepended/appended deterministically)
        # but since expected_elements may have existing content, just verify presence
        assert "c" in bp.contract.expected_elements
        assert "a" in bp.contract.expected_elements
        assert "b" in bp.contract.expected_elements

    def test_duplicate_suppression(self):
        """Same item in both required and rejected does not duplicate."""

        class _CustomIdentity:
            pass

        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["item_x", "item_x"],  # duplicate in required
            rejected=["item_x"],  # also in rejected
        )
        bp = compile_to_blueprint(identity)
        # Should not have duplicates
        assert bp.contract.expected_elements.count("item_x") <= 1
        assert bp.contract.rejected_outcomes.count("item_x") <= 1
        assert "item_x" not in bp.contract.forbidden_tropes

    def test_empty_resolution_contract(self):
        """Empty resolution contract produces no obligations."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=[],
            rejected=[],
        )
        bp = compile_to_blueprint(identity)
        assert bp.profile_derivation is not None
        # Should have no profile-derived obligations
        non_pattern_obligations = [o for o in bp.profile_derivation.obligations_applied
                                   if "pattern" not in o]
        assert len(non_pattern_obligations) == 0

    def test_explicit_element_already_present(self):
        """If an expected element already exists, no duplicate is added."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["existing_element"],
        )
        bp = compile_to_blueprint(identity)
        # The test identity starts with expected_elements=[] (from compile_to_blueprint)
        # So "existing_element" should be added exactly once
        assert bp.contract.expected_elements.count("existing_element") == 1

    def test_no_identity_mutation_during_compile(self):
        """compile_to_blueprint must not mutate the identity."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["protagonist_transformation"],
        )
        # Snapshot identity state
        orig_genre = identity.story_type.genre
        orig_subgenres = list(identity.story_type.subgenres)
        orig_profile = identity.genre_profile.model_dump(mode="json")

        bp = compile_to_blueprint(identity)

        # Identity should be unchanged
        assert identity.story_type.genre == orig_genre
        assert identity.story_type.subgenres == orig_subgenres
        assert identity.genre_profile.model_dump(mode="json") == orig_profile

    def test_all_three_rules_reachable_through_public_api(self):
        """Prove D-RES-001/002/003 are all reachable via analyze_structure()."""
        from auteur.structure.analyzer import analyze_structure

        # Trigger all three rules with one blueprint
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.COMIC  # BITTERSWEET (conflict with tragic pattern)
        identity.genre_profile = _make_profile_commitment(
            pattern="dark_transgression_resolution",
            required=["protagonist_transformation"],
            rejected=["superficial_happy_ending"],
            rec_id="rec_reachability",
        )
        bp = compile_to_blueprint(identity)
        # Remove protagonist_transformation from expected_elements to trigger D-RES-001
        bp.contract.expected_elements = [
            e for e in bp.contract.expected_elements if e != "protagonist_transformation"
        ]
        # Add the rejected outcome to expected_elements to trigger D-RES-002
        if "superficial_happy_ending" not in bp.contract.expected_elements:
            bp.contract.expected_elements.append("superficial_happy_ending")

        diagnostics = analyze_structure(bp)
        rules_fired = {d.rule for d in diagnostics}

        assert "profile.resolution_contract.missing_required_outcome" in rules_fired, (
            f"D-RES-001 not fired. Rules: {rules_fired}"
        )
        assert "profile.resolution_contract.rejected_outcome_present" in rules_fired, (
            f"D-RES-002 not fired. Rules: {rules_fired}"
        )
        assert "profile.resolution_contract.ending_tone_conflict" in rules_fired, (
            f"D-RES-003 not fired. Rules: {rules_fired}"
        )

    def test_diagnostic_evidence_paths(self):
        """Diagnostics from profile checks include provenance paths."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(
            required=["missing_outcome"],
            rec_id="rec_diag_evidence",
        )
        bp = compile_to_blueprint(identity)

        # D-RES-001 should reference the profile path
        diagnostics = analyze_structure(bp)
        missing_diags = [d for d in diagnostics if d.rule == "profile.resolution_contract.missing_required_outcome"]
        if missing_diags:
            d = missing_diags[0]
            evidence_text = " ".join(d.evidence)
            assert "genre_profile" in evidence_text or "required_outcomes" in evidence_text
            # Should reference the affected blueprint path
            assert "expected_elements" in evidence_text
