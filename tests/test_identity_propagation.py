"""Tests for bounded identity-to-structure propagation.

Spec: docs/design/identity-structure-bounded-propagation.md
Covers:
  A1/A3 contract propagation: StoryIdentity.not_this / rejected_directions
  -> AuthorAudienceContract.custom_rules (verbatim, deduped, ordered,
  idempotent, conflict-refused), author_overrides NEVER propagated.
  A4 safe explicit naming from IdentityCharacter.structural_role declarations.
  B1 role consistency (four Experiment-3 semantic categories + arc gate +
  authored boundary).
  Universal diagnostics via persisted provenance + analyzer; compatibility.
"""

from copy import deepcopy

import yaml

from auteur.blueprint import (
    StoryBlueprint,
    Genre,
    StoryMode,
    StoryMedium,
    TargetAudience,
    TargetExperience,
    LengthClass,
)
from auteur.genre_packs.models import (
    GenreProfileCommitment,
    ResolutionContractCommitment,
    FramingCommitment,
    AdherencePosture,
)
from auteur.identity import (
    StoryIdentity,
    StoryType,
    HighLevelCentralEngine,
    compile_to_blueprint,
)
from auteur.identity_propagation import apply_contract_propagation
from auteur.structure.diagnostics import DiagnosticSeverity
from auteur.structure.analyzer import analyze_structure


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_base_identity() -> StoryIdentity:
    """A deterministic base identity without genre_profile and without commitments."""
    return StoryIdentity(
        title="Propagation Test",
        core_answer="A test story for identity-to-structure propagation.",
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


def _with_characters(identity: StoryIdentity, characters: list[dict]) -> StoryIdentity:
    """Return a copy of the identity with validated IdentityCharacter entries."""
    data = identity.model_dump(mode="json")
    data["characters"] = characters
    return StoryIdentity.model_validate(data)


def _make_profile_commitment(
    required: list[str] | None = None,
    rejected: list[str] | None = None,
) -> GenreProfileCommitment:
    return GenreProfileCommitment(
        primary_pack_id="erotic_fiction",
        primary_pack_version="0.1.0",
        pack_content_hash="abcdef1234567890",
        primary_profile_id="erotic_psychological_drama",
        accepted_target_emotions={},
        accepted_narrative_engine="erotic_identity_transformation",
        accepted_framing=FramingCommitment(primary="romantic", secondary=["unsettling"]),
        accepted_resolution_contract=ResolutionContractCommitment(
            pattern="transformative_resolution",
            required_outcomes=required or [],
            rejected_outcomes=rejected or [],
        ),
        adherence_posture=AdherencePosture.CONVENTIONAL,
        source_recommendation_id="rec_identity_propagation_test",
        author_overrides=[],
    )


# ---------------------------------------------------------------------------
# A1/A3: verbatim propagation
# ---------------------------------------------------------------------------

class TestContractPropagation:
    def test_not_this_propagates_verbatim_into_custom_rules(self):
        identity = _make_base_identity()
        identity.not_this = [
            "a story where only one partner ever has to be vulnerable",
            "a triumph story",
        ]
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == [
            "a story where only one partner ever has to be vulnerable",
            "a triumph story",
        ]
        # Never misuses forbidden_tropes (free sentences are inert there).
        assert bp.contract.forbidden_tropes == []
        assert bp.contract.expected_elements == []

    def test_rejected_directions_propagates_verbatim_with_source_provenance(self):
        identity = _make_base_identity()
        identity.rejected_directions = ["Do not make the mother secretly responsible for the accident."]
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == [
            "Do not make the mother secretly responsible for the accident."
        ]
        derivation = bp.identity_propagation
        assert derivation is not None
        applied = [o for o in derivation.outcomes if o.classification == "DIRECT_DETERMINISTIC"]
        assert len(applied) == 1
        assert applied[0].rule == "identity.rejected_directions.custom_rules"
        assert applied[0].source == "rejected_directions[0]"
        assert applied[0].destination == "contract.custom_rules[0]"
        assert applied[0].value == "Do not make the mother secretly responsible for the accident."

    def test_absent_commitments_leave_blueprint_inert(self):
        identity = _make_base_identity()
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == []
        assert bp.contract.expected_elements == []
        assert bp.contract.forbidden_tropes == []
        assert bp.identity_propagation is None

    def test_deterministic_ordering_identity_after_profile_items_in_list_order(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(required=["protagonist_transformation"])
        identity.not_this = ["first exclusion", "second exclusion"]
        identity.rejected_directions = ["first rejection", "second rejection"]

        bp = compile_to_blueprint(identity)

        assert bp.contract.expected_elements == ["protagonist_transformation"]
        assert bp.contract.custom_rules == [
            "first exclusion",
            "second exclusion",
            "first rejection",
            "second rejection",
        ]

    def test_duplicate_input_deduplicated_exactly(self):
        identity = _make_base_identity()
        identity.not_this = ["same commitment", "same commitment"]
        identity.rejected_directions = ["same commitment"]
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == ["same commitment"]
        applied = [o for o in bp.identity_propagation.outcomes if o.classification == "DIRECT_DETERMINISTIC"]
        # Only the first occurrence is applied.
        assert len(applied) == 1
        assert applied[0].source == "not_this[0]"

    def test_dedupe_is_case_sensitive_exact_match(self):
        identity = _make_base_identity()
        identity.not_this = ["No magic", "no magic"]
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == ["No magic", "no magic"]

    def test_existing_destination_value_not_duplicated(self):
        """Existing semantically equivalent values must not duplicate."""
        identity = _make_base_identity()
        identity.not_this = ["already present"]
        identity.rejected_directions = ["another rule"]

        contract = _make_contract_with_custom_rules(["already present"])
        outcomes = []
        apply_contract_propagation(identity, contract, outcomes)

        assert contract.custom_rules == ["already present", "another rule"]
        applied = [o for o in outcomes if o.classification == "DIRECT_DETERMINISTIC"]
        assert len(applied) == 1
        assert applied[0].value == "another rule"

    def test_whitespace_only_items_are_skipped(self):
        identity = _make_base_identity()
        identity.not_this = ["   ", "", "real rule"]
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == ["real rule"]

    def test_idempotence_and_no_identity_mutation(self):
        identity = _make_base_identity()
        identity.not_this = ["a story without chosen ones"]
        identity.rejected_directions = ["No redemption arc."]

        snapshot = deepcopy(identity.model_dump())
        bp1 = compile_to_blueprint(identity)
        bp2 = compile_to_blueprint(identity)

        assert bp1.model_dump(mode="json") == bp2.model_dump(mode="json")
        assert identity.model_dump() == snapshot

    def test_round_trip_serialization_preserves_provenance(self):
        identity = _make_base_identity()
        identity.not_this = ["no chosen one prophecy"]
        bp = compile_to_blueprint(identity)

        serialized = yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False)
        loaded = StoryBlueprint.model_validate(yaml.safe_load(serialized))

        assert loaded.contract.custom_rules == ["no chosen one prophecy"]
        assert loaded.identity_propagation is not None
        assert loaded.identity_propagation.model_dump() == bp.identity_propagation.model_dump()


# ---------------------------------------------------------------------------
# A2: author_overrides is never propagated
# ---------------------------------------------------------------------------

class TestAuthorOverridesNeverPropagated:
    def test_author_overrides_never_propagated(self):
        identity = _make_base_identity()
        identity.not_this = ["a real exclusion"]
        identity.author_overrides = [
            "ending_tone",
            "runway_compression",
            "Do not soften the ending into a restoration of the old empire.",
        ]
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == ["a real exclusion"]
        assert all(
            o.source is None or not o.source.startswith("author_overrides")
            for o in bp.identity_propagation.outcomes
        )

    def test_author_overrides_alone_produce_no_propagation(self):
        identity = _make_base_identity()
        identity.author_overrides = ["ending_tone", "runway_compression", "free-text mandate"]
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == []
        assert bp.identity_propagation is None


# ---------------------------------------------------------------------------
# Conflict refusal
# ---------------------------------------------------------------------------

class TestContractConflict:
    def test_expected_custom_conflict_blocks_with_diagnostic(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(required=["protagonist_transformation"])
        identity.not_this = ["protagonist_transformation"]
        bp = compile_to_blueprint(identity)

        # Item stays (nothing is removed); the refusal is recorded.
        assert bp.contract.expected_elements == ["protagonist_transformation"]
        assert bp.contract.custom_rules == ["protagonist_transformation"]

        blocked = [o for o in bp.identity_propagation.outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
        assert len(blocked) == 1
        assert blocked[0].rule == "identity.propagation.contract.conflict"
        assert blocked[0].source == "not_this[0]"
        assert "AUTHOR_DECISION_REQUIRED" in (blocked[0].reason or "")

        diagnostics = analyze_structure(bp)
        conflict_diags = [d for d in diagnostics if d.rule == "identity.propagation.contract.conflict"]
        assert len(conflict_diags) == 1
        assert conflict_diags[0].severity == DiagnosticSeverity.WARNING
        assert "protagonist_transformation" in conflict_diags[0].evidence[1]

    def test_conflict_comparison_uses_casefolded_normalization(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(required=["Protagonist Transformation"])
        identity.not_this = ["  protagonist transformation  "]
        bp = compile_to_blueprint(identity)

        blocked = [o for o in bp.identity_propagation.outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
        assert len(blocked) == 1
        assert blocked[0].rule == "identity.propagation.contract.conflict"

    def test_unrelated_expected_element_does_not_block(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(required=["mentor_death"])
        identity.not_this = ["no chosen one prophecy"]
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == ["no chosen one prophecy"]
        assert all(
            o.classification != "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"
            for o in bp.identity_propagation.outcomes
        )


# ---------------------------------------------------------------------------
# A4: safe explicit naming
# ---------------------------------------------------------------------------

class TestCharacterNaming:
    def test_declared_protagonist_names_placeholder_slot(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Rowan", "structural_role": "protagonist"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[0].name == "Rowan"
        assert bp.characters[1].name == "Antagonist"
        applied = [o for o in bp.identity_propagation.outcomes if o.classification == "DIRECT_DETERMINISTIC"]
        assert any(o.rule == "identity.naming.protagonist" and o.source == "characters[0].name" for o in applied)

    def test_declared_antagonist_names_placeholder_slot(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Mordecai", "structural_role": "antagonist"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[0].name == "Protagonist"
        assert bp.characters[1].name == "Mordecai"

    def test_two_entries_claiming_same_role_blocked_no_naming(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Rowan", "structural_role": "protagonist"},
            {"name": "Mara", "structural_role": "protagonist"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[0].name == "Protagonist"
        assert bp.characters[1].name == "Antagonist"
        blocked = [o for o in bp.identity_propagation.outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
        assert len(blocked) == 2
        assert all(o.rule == "identity.propagation.naming.ambiguous" for o in blocked)

        diagnostics = analyze_structure(bp)
        assert len([d for d in diagnostics if d.rule == "identity.propagation.naming.ambiguous"]) == 2

    def test_entry_without_structural_role_never_names(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Rowan"},
            {"name": "Mara", "structural_role": "antagonist"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[0].name == "Protagonist"
        assert bp.characters[1].name == "Mara"
        # Rowan appears nowhere; no invented slot for her.
        assert all(c.name != "Rowan" for c in bp.characters)

    def test_naming_does_not_require_arc_type(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Rowan", "structural_role": "protagonist", "undergoes_central_change": True},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[0].name == "Rowan"

    def test_naming_mystery_genre_detective_slot(self):
        """Detective/Culprit are the mystery genre's placeholder instances."""
        identity = _make_base_identity()
        identity.story_type.genre = Genre.MYSTERY
        identity = _with_characters(identity, [
            {"name": "Rowan", "structural_role": "protagonist"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[0].name == "Rowan"
        assert bp.characters[1].name == "Culprit"

    def test_role_without_slot_is_restraint_no_trace(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Sam", "structural_role": "supporting"},
        ])
        bp = compile_to_blueprint(identity)

        assert all(c.name != "Sam" for c in bp.characters)
        # Only the naming rule ran and produced no outcome -> no provenance.
        assert bp.identity_propagation is None

    def test_naming_plus_contract_coexist(self):
        identity = _make_base_identity()
        identity.not_this = ["no chosen one prophecy"]
        identity = _with_characters(identity, [
            {"name": "Rowan", "structural_role": "protagonist"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == ["no chosen one prophecy"]
        assert bp.characters[0].name == "Rowan"


# ---------------------------------------------------------------------------
# IdentityCharacter schema compatibility
# ---------------------------------------------------------------------------

class TestIdentityCharacterSchema:
    def test_old_documents_without_characters_remain_valid(self):
        identity = _make_base_identity()
        data = identity.model_dump()
        assert "characters" not in data or data["characters"] == []
        round_tripped = StoryIdentity.model_validate(data)
        assert round_tripped.characters == []

        serialized = yaml.safe_dump(identity.model_dump(mode="json"))
        loaded = StoryIdentity.model_validate(yaml.safe_load(serialized))
        assert loaded.characters == []

    def test_explicit_fields_round_trip(self):
        from auteur.identity import IdentityCharacter

        identity = _make_base_identity()
        identity.characters = [
            IdentityCharacter(
                name="Rowan",
                structural_role="protagonist",
                undergoes_central_change=True,
                arc_type="growth",
            )
        ]
        loaded = StoryIdentity.model_validate(yaml.safe_load(yaml.safe_dump(identity.model_dump(mode="json"))))
        assert loaded.characters[0].name == "Rowan"
        assert loaded.characters[0].structural_role.value == "protagonist"
        assert loaded.characters[0].undergoes_central_change is True
        assert loaded.characters[0].arc_type.value == "growth"

    def test_unknown_distinguishable_from_explicit_false(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Rowan", "undergoes_central_change": None},
            {"name": "Mara", "undergoes_central_change": False},
        ])
        data = identity.model_dump()
        assert data["characters"][0]["undergoes_central_change"] is None
        assert data["characters"][1]["undergoes_central_change"] is False

    def test_identity_validation_still_passes_with_characters(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Rowan", "structural_role": "protagonist", "undergoes_central_change": True},
        ])
        diagnostics = identity.validate_identity()
        assert not any(d.severity == DiagnosticSeverity.ERROR for d in diagnostics)


# ---------------------------------------------------------------------------
# B1: role consistency (the four Experiment-3 semantic categories, structured)
# ---------------------------------------------------------------------------

class TestRoleRule:
    def test_category1_already_correct_role_no_mutation(self):
        """Explicit transformation commitment already represented -> inert."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Protagonist", "structural_role": "protagonist", "undergoes_central_change": True},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[0].name == "Protagonist"
        assert bp.characters[0].role.value == "protagonist"
        assert bp.characters[0].arc_type.value == "corruption"  # tragic seeder default
        assert bp.identity_propagation is None  # restraint leaves no trace

    def test_category1_named_subject_matching_renamed_slot_no_mutation(self):
        """Naming first, then the role rule sees the subject represented."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Rowan", "structural_role": "protagonist", "undergoes_central_change": True},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[0].name == "Rowan"
        assert bp.characters[0].role.value == "protagonist"
        applied_rules = [o.rule for o in bp.identity_propagation.outcomes]
        assert "identity.role_rule.correction" not in applied_rules

    def test_category2_explicit_opponent_who_changes_not_recast(self):
        """A changing explicit opponent is never recast (opposition precedence)."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Oren", "structural_role": "antagonist", "undergoes_central_change": True},
        ])
        bp = compile_to_blueprint(identity)

        # Naming names the antagonist slot; the role rule takes no action.
        assert bp.characters[1].name == "Oren"
        assert bp.characters[1].role.value == "antagonist"
        assert bp.characters[1].arc_type.value == "flat"
        assert bp.characters[1].arc_end_percentage == 0
        assert "identity.role_rule.correction" not in [o.rule for o in bp.identity_propagation.outcomes]

    def test_category2_placeholder_name_opponent_fully_inert(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Antagonist", "structural_role": "antagonist", "undergoes_central_change": True},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[1].name == "Antagonist"
        assert bp.characters[1].role.value == "antagonist"
        assert bp.identity_propagation is None

    def test_category3_ambiguous_subject_fails_closed(self):
        """Two co-transforming subjects -> BLOCKED, no mutation."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Mara", "undergoes_central_change": True},
            {"name": "Tomas", "undergoes_central_change": True},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[1].name == "Antagonist"
        assert bp.characters[1].role.value == "antagonist"
        blocked = [o for o in bp.identity_propagation.outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
        assert len(blocked) == 2
        assert all(o.rule == "identity.propagation.role_rule.ambiguous_subject" for o in blocked)

        diagnostics = analyze_structure(bp)
        assert len([d for d in diagnostics if d.rule == "identity.propagation.role_rule.ambiguous_subject"]) == 2

    def test_category3_no_eligible_placeholder_slot_fails_closed(self):
        """Opposition named first -> no placeholder target remains -> BLOCKED."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Mordecai", "structural_role": "antagonist"},
            {"name": "Rowan", "undergoes_central_change": True, "arc_type": "growth"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[1].name == "Mordecai"
        assert bp.characters[1].role.value == "antagonist"
        blocked = [o for o in bp.identity_propagation.outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
        assert any(o.rule == "identity.propagation.role_contradiction.unresolved" for o in blocked)

    def test_category4_co_transforming_lead_corrected_with_arc(self):
        """Explicit co-transforming lead in the placeholder antagonist slot."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Ines", "undergoes_central_change": True, "arc_type": "growth"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[1].name == "Ines"
        assert bp.characters[1].role.value == "deuteragonist"
        assert bp.characters[1].arc_type.value == "growth"
        assert bp.characters[1].arc_start_percentage == 0
        assert bp.characters[1].arc_end_percentage == 100
        applied = [o for o in bp.identity_propagation.outcomes if o.classification == "DIRECT_DETERMINISTIC"]
        assert any(o.rule == "identity.role_rule.correction" and o.destination == "characters[1]" for o in applied)

    def test_category4_declared_role_honored(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Ines", "structural_role": "deuteragonist", "undergoes_central_change": True, "arc_type": "growth"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[1].name == "Ines"
        assert bp.characters[1].role.value == "deuteragonist"

    def test_stage4a_missing_arc_blocks_never_defaults(self):
        """Correction without explicit arc -> BLOCKED, atomic (no mutation)."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Ines", "undergoes_central_change": True},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[1].name == "Antagonist"
        assert bp.characters[1].role.value == "antagonist"
        assert bp.characters[1].arc_type.value == "flat"
        blocked = [o for o in bp.identity_propagation.outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
        assert len(blocked) == 1
        assert blocked[0].rule == "identity.propagation.role_rule.arc_undeclared"

        diagnostics = analyze_structure(bp)
        arc_diags = [d for d in diagnostics if d.rule == "identity.propagation.role_rule.arc_undeclared"]
        assert len(arc_diags) == 1
        assert arc_diags[0].severity == DiagnosticSeverity.WARNING

    def test_stage5_authored_slot_never_silently_overwritten(self):
        """Authored (non-placeholder) contradictory slot -> BLOCKED diagnostic."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Mordecai", "structural_role": "antagonist"},
            {"name": "Rowan", "undergoes_central_change": True, "arc_type": "growth"},
        ])
        bp = compile_to_blueprint(identity)

        # The antagonist slot was authored (named) by the same identity: no recast.
        assert bp.characters[1].name == "Mordecai"
        assert bp.characters[1].role.value == "antagonist"
        blocked = [o for o in bp.identity_propagation.outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
        assert any(o.rule == "identity.propagation.role_contradiction.unresolved" for o in blocked)

        diagnostics = analyze_structure(bp)
        unresolved = [d for d in diagnostics if d.rule == "identity.propagation.role_contradiction.unresolved"]
        assert len(unresolved) == 1

    def test_opposition_and_co_lead_coexist(self):
        """Opposition precedence: the declared opponent's seat is never recast."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Oren", "structural_role": "antagonist", "undergoes_central_change": True},
            {"name": "Ines", "undergoes_central_change": True, "arc_type": "healing"},
        ])
        bp = compile_to_blueprint(identity)

        # The antagonist seat is occupied by the declared opponent: Ines's
        # transformation has no placeholder target -> fail-closed, no recast.
        assert bp.characters[1].name == "Oren"
        assert bp.characters[1].role.value == "antagonist"
        assert len([o for o in bp.identity_propagation.outcomes if o.rule == "identity.role_rule.correction"]) == 0
        blocked = [o for o in bp.identity_propagation.outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
        assert any(o.rule == "identity.propagation.role_contradiction.unresolved" for o in blocked)

    def test_placeholder_named_subject_with_arc_is_corrected(self):
        """A subject named exactly like the placeholder is still corrected."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Antagonist", "undergoes_central_change": True, "arc_type": "growth"},
        ])
        bp = compile_to_blueprint(identity)

        # The literal placeholder name matches the seeded slot; no
        # structural_role is declared, so the subject is a co-transforming
        # lead in a contradictory seat -> design-conformant correction.
        assert bp.characters[1].name == "Antagonist"
        assert bp.characters[1].role.value == "deuteragonist"
        assert bp.characters[1].arc_type.value == "growth"

    def test_mystery_genre_correction_uses_culprit_slot(self):
        identity = _make_base_identity()
        identity.story_type.genre = Genre.MYSTERY
        identity = _with_characters(identity, [
            {"name": "Rowan", "undergoes_central_change": True, "arc_type": "growth"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.characters[1].name == "Rowan"
        assert bp.characters[1].role.value == "deuteragonist"


# ---------------------------------------------------------------------------
# Analyzer conversion
# ---------------------------------------------------------------------------

class TestAnalyzerConversion:
    def test_applied_outcomes_produce_no_diagnostics(self):
        identity = _make_base_identity()
        identity.not_this = ["no chosen one prophecy"]
        bp = compile_to_blueprint(identity)

        diagnostics = analyze_structure(bp)
        assert not [d for d in diagnostics if d.rule.startswith("identity.propagation.")]

    def test_inert_blueprint_produces_no_propagation_diagnostics(self):
        identity = _make_base_identity()
        bp = compile_to_blueprint(identity)

        assert bp.identity_propagation is None
        diagnostics = analyze_structure(bp)
        assert not [d for d in diagnostics if d.rule.startswith("identity.propagation.")]


# ---------------------------------------------------------------------------
# CLI surfacing (convenience projection; analyzer remains the source of truth)
# ---------------------------------------------------------------------------

class TestCliSurfacing:
    def test_cli_handler_surfaces_blocked_outcomes(self):
        from auteur.cli_handlers import handle_compile_to_blueprint

        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(required=["protagonist_transformation"])
        identity.not_this = ["protagonist_transformation"]

        result = handle_compile_to_blueprint(identity)
        assert result.is_success
        warnings = result.data.propagation_warnings
        assert len(warnings) == 1
        assert "identity.propagation.contract.conflict" in warnings[0]

    def test_cli_handler_no_warnings_when_applied_only(self):
        from auteur.cli_handlers import handle_compile_to_blueprint

        identity = _make_base_identity()
        identity.not_this = ["no chosen one prophecy"]

        result = handle_compile_to_blueprint(identity)
        assert result.is_success
        assert result.data.propagation_warnings == []


# ---------------------------------------------------------------------------
# Universal diagnostics (caller independence) + compatibility
# ---------------------------------------------------------------------------

class TestCrossCallerBehavior:
    def test_blocked_outcomes_identical_via_handler_and_direct_compile(self):
        """Semantic correctness must not depend on which caller compiled."""
        from auteur.cli_handlers import handle_compile_to_blueprint

        identity = _with_characters(_make_base_identity(), [
            {"name": "Ines", "undergoes_central_change": True},  # no arc -> blocked
        ])

        direct = compile_to_blueprint(identity)
        handler_result = handle_compile_to_blueprint(identity)
        assert handler_result.is_success
        via_handler = handler_result.data.blueprint

        direct_diags = analyze_structure(direct)
        handler_diags = analyze_structure(via_handler)
        direct_blocked = [d for d in direct_diags if d.rule.startswith("identity.propagation.")]
        handler_blocked = [d for d in handler_diags if d.rule.startswith("identity.propagation.")]
        assert [d.model_dump() for d in direct_blocked] == [d.model_dump() for d in handler_blocked]
        assert any(d.rule == "identity.propagation.role_rule.arc_undeclared" for d in direct_blocked)
        # The handler's convenience projection matches the analyzer's source of truth.
        assert len(handler_result.data.propagation_warnings) == len(direct_blocked)

    def test_run_all_diagnostics_inherits_propagation_rules(self, tmp_path):
        from auteur.bible import StoryBible
        from auteur.structure.analyzer import run_all_diagnostics

        identity = _with_characters(_make_base_identity(), [
            {"name": "Ines", "undergoes_central_change": True},
        ])
        bp = compile_to_blueprint(identity)
        bible = StoryBible(tmp_path / "bible.json")

        diagnostics = run_all_diagnostics(bp, bible)
        assert any(d.rule == "identity.propagation.role_rule.arc_undeclared" for d in diagnostics)

    def test_cli_surfacing_is_not_required_for_diagnostics(self):
        """The provenance record is the source of truth, not the CLI handler."""
        identity = _with_characters(_make_base_identity(), [
            {"name": "Ines", "undergoes_central_change": True},
        ])
        bp = compile_to_blueprint(identity)

        # No CLI involved; the analyzer still surfaces the refusal.
        diagnostics = analyze_structure(bp)
        assert any(d.rule == "identity.propagation.role_rule.arc_undeclared" for d in diagnostics)


class TestCompatibility:
    def test_inert_identity_blueprint_unchanged(self):
        """Identities without commitments or characters stay semantically identical."""
        identity = _make_base_identity()
        bp = compile_to_blueprint(identity)

        assert bp.contract.custom_rules == []
        assert bp.contract.expected_elements == []
        assert bp.contract.forbidden_tropes == []
        assert bp.identity_propagation is None
        assert [c.name for c in bp.characters] == ["Protagonist", "Antagonist"]
        assert [c.role.value for c in bp.characters] == ["protagonist", "antagonist"]

    def test_existing_identity_fixtures_still_load_and_compile(self):
        from pathlib import Path

        example = Path("examples/story_identity.yaml")
        assert example.exists()
        identity = StoryIdentity.from_yaml(example)
        bp = compile_to_blueprint(identity)
        assert bp.identity.title == identity.title
        assert bp.identity_propagation is not None  # the example carries not_this
        assert bp.contract.custom_rules != []

    def test_compiled_blueprint_round_trips_through_yaml(self):
        identity = _with_characters(_make_base_identity(), [
            {"name": "Ines", "undergoes_central_change": True, "arc_type": "growth"},
        ])
        bp = compile_to_blueprint(identity)

        serialized = yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False)
        loaded = StoryBlueprint.model_validate(yaml.safe_load(serialized))
        assert loaded.characters[1].name == "Ines"
        assert loaded.characters[1].role.value == "deuteragonist"
        assert loaded.identity_propagation is not None
        assert len(loaded.identity_propagation.outcomes) == 1

    def test_profile_derivation_and_identity_propagation_coexist(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile_commitment(required=["protagonist_transformation"])
        identity.not_this = ["no chosen one prophecy"]
        identity = _with_characters(identity, [
            {"name": "Rowan", "structural_role": "protagonist"},
        ])
        bp = compile_to_blueprint(identity)

        assert bp.profile_derivation is not None
        assert bp.identity_propagation is not None
        assert bp.contract.expected_elements == ["protagonist_transformation"]
        assert bp.contract.custom_rules == ["no chosen one prophecy"]
        assert bp.characters[0].name == "Rowan"
        assert bp.profile_derivation.model_dump() != bp.identity_propagation.model_dump()

def _make_contract_with_custom_rules(rules: list[str]):
    from auteur.blueprint import AuthorAudienceContract, ContentRating, EndingTone

    return AuthorAudienceContract(
        content_rating=ContentRating.R,
        mandatory_ending_tone=EndingTone.TRAGIC,
        expected_elements=[],
        forbidden_tropes=[],
        rejected_outcomes=[],
        custom_rules=list(rules),
    )
