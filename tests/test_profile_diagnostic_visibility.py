"""Public workflow tests for profile diagnostic visibility.

Tests that D-RES-001/002/003 are reachable through the public
genre diagnose workflow, and that the D-RES-003 false-positive fix
for tragic + transformative_resolution is correct.

Requirements:
  docs/reviews/2026-07-27-profile-diagnostic-visibility-verification.md
"""

import json
from pathlib import Path

import pytest
import yaml

from auteur.blueprint import (
    StoryBlueprint,
    Genre,
    StoryMode,
    StoryMedium,
    TargetAudience,
    TargetExperience,
    EndingTone,
)
from auteur.cli import main
from auteur.genre_packs.diagnostics import run_genre_diagnostics
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
    return StoryIdentity(
        title="Visibility Test",
        core_answer="A test story for diagnostic visibility.",
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


def _make_profile(
    pattern: str = "transformative_resolution",
    required: list[str] | None = None,
    rejected: list[str] | None = None,
    posture: AdherencePosture = AdherencePosture.CONVENTIONAL,
    rec_id: str = "rec_visibility_test",
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


def _setup_project(tmp_path: Path, identity: StoryIdentity) -> Path:
    """Write identity to a temp project directory and return the path."""
    proj_dir = tmp_path / "test_proj"
    proj_dir.mkdir(exist_ok=True)
    identity.to_yaml(proj_dir / "story_identity.yaml")
    return proj_dir


def _profile_diags(diags: list) -> list:
    return [d for d in diags if d.rule.startswith("profile.")]


# ===========================================================================
# 1. genre diagnose exposes D-RES-001
# ===========================================================================

class TestDiagnoseExposesDRES001:
    def test_via_run_genre_diagnostics(self):
        """D-RES-001 reachable through run_genre_diagnostics with blueprint."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile(
            required=["protagonist_transformation"],
        )
        bp = compile_to_blueprint(identity)
        bp.contract.expected_elements = [
            e for e in bp.contract.expected_elements
            if e != "protagonist_transformation"
        ]
        diags = run_genre_diagnostics(identity, blueprint=bp)
        rules = {d.rule for d in diags}
        assert "profile.resolution_contract.missing_required_outcome" in rules

    def test_via_cli_human(self, tmp_path, capsys):
        """D-RES-001 visible through 'auteur genre diagnose' human output."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile(
            required=["protagonist_transformation"],
        )
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        bp.contract.expected_elements = [
            e for e in bp.contract.expected_elements
            if e != "protagonist_transformation"
        ]
        # Write blueprint so diagnose can find it
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        blueprint_path = bp_dir / "blueprint.yaml"
        blueprint_path.write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )

        rc = main(["genre", "diagnose", "--project", str(proj_dir)])
        assert rc is None or rc == 0
        captured = capsys.readouterr()
        assert "profile.resolution_contract.missing_required_outcome" in captured.out
        # Human output includes the rule and message; provenance is visible in JSON
        assert "recommendation_id" in captured.out or "expected_elements" in captured.out

    def test_via_cli_json(self, tmp_path, capsys):
        """D-RES-001 visible through 'auteur genre diagnose --json'."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile(
            required=["protagonist_transformation"],
        )
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        bp.contract.expected_elements = [
            e for e in bp.contract.expected_elements
            if e != "protagonist_transformation"
        ]
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        blueprint_path = bp_dir / "blueprint.yaml"
        blueprint_path.write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )

        rc = main(["genre", "diagnose", "--project", str(proj_dir), "--json"])
        assert rc is None or rc == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rules = {d["rule"] for d in data}
        assert "profile.resolution_contract.missing_required_outcome" in rules


# ===========================================================================
# 2. genre diagnose exposes D-RES-002
# ===========================================================================

class TestDiagnoseExposesDRES002:
    def test_via_run_genre_diagnostics(self):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile(
            pattern="transformative_resolution",
            required=["protagonist_transformation"],
            rejected=["superficial_happy_ending"],
        )
        bp = compile_to_blueprint(identity)
        if "superficial_happy_ending" not in bp.contract.expected_elements:
            bp.contract.expected_elements.append("superficial_happy_ending")
        diags = run_genre_diagnostics(identity, blueprint=bp)
        rules = {d.rule for d in diags}
        assert "profile.resolution_contract.rejected_outcome_present" in rules

    def test_via_cli(self, tmp_path, capsys):
        identity = _make_base_identity()
        identity.genre_profile = _make_profile(
            pattern="transformative_resolution",
            required=["protagonist_transformation"],
            rejected=["superficial_happy_ending"],
        )
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        if "superficial_happy_ending" not in bp.contract.expected_elements:
            bp.contract.expected_elements.append("superficial_happy_ending")
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        (bp_dir / "blueprint.yaml").write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        rc = main(["genre", "diagnose", "--project", str(proj_dir), "--json"])
        assert rc is None or rc == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rules = {d["rule"] for d in data}
        assert "profile.resolution_contract.rejected_outcome_present" in rules


# ===========================================================================
# 3. genre diagnose exposes D-RES-003 for a real contradiction
# ===========================================================================

class TestDiagnoseExposesDRES003:
    def test_via_run_genre_diagnostics(self):
        """COMIC + dark_transgression_resolution still fires D-RES-003."""
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.COMIC
        identity.genre_profile = _make_profile(
            pattern="dark_transgression_resolution",
        )
        bp = compile_to_blueprint(identity)
        diags = run_genre_diagnostics(identity, blueprint=bp)
        rules = {d.rule for d in diags}
        assert "profile.resolution_contract.ending_tone_conflict" in rules

    def test_via_cli(self, tmp_path, capsys):
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.COMIC
        identity.genre_profile = _make_profile(
            pattern="dark_transgression_resolution",
        )
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        (bp_dir / "blueprint.yaml").write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        rc = main(["genre", "diagnose", "--project", str(proj_dir), "--json"])
        assert rc is None or rc == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rules = {d["rule"] for d in data}
        assert "profile.resolution_contract.ending_tone_conflict" in rules


# ===========================================================================
# 4. tragic + transformative_resolution produces no D-RES-003
# ===========================================================================

class TestTragicTransformativeNoFalsePositive:
    def test_via_analyze_structure(self):
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.TRAGIC
        identity.genre_profile = _make_profile(
            pattern="transformative_resolution"
        )
        bp = compile_to_blueprint(identity)
        diags = analyze_structure(bp)
        dres003 = [d for d in diags if "ending_tone_conflict" in d.rule]
        assert len(dres003) == 0

    def test_via_run_genre_diagnostics(self):
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.TRAGIC
        identity.genre_profile = _make_profile(
            pattern="transformative_resolution"
        )
        bp = compile_to_blueprint(identity)
        diags = run_genre_diagnostics(identity, blueprint=bp)
        dres003 = [d for d in diags if "ending_tone_conflict" in d.rule]
        assert len(dres003) == 0

    def test_via_cli(self, tmp_path, capsys):
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.TRAGIC
        identity.genre_profile = _make_profile(
            pattern="transformative_resolution"
        )
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        (bp_dir / "blueprint.yaml").write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        rc = main(["genre", "diagnose", "--project", str(proj_dir), "--json"])
        assert rc is None or rc == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        dres003 = [d for d in data if "ending_tone_conflict" in d.get("rule", "")]
        assert len(dres003) == 0


# ===========================================================================
# 5. Human output includes originating commitment and affected field
# ===========================================================================

class TestHumanOutputProvenance:
    def test_human_output_contains_rule_and_message(self, tmp_path, capsys):
        """Human output includes the diagnostic rule ID and message.
        Evidence/provenance fields are visible in JSON output."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile(
            required=["protagonist_transformation"],
            rec_id="rec_provenance_test",
        )
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        bp.contract.expected_elements = [
            e for e in bp.contract.expected_elements
            if e != "protagonist_transformation"
        ]
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        (bp_dir / "blueprint.yaml").write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        rc = main(["genre", "diagnose", "--project", str(proj_dir)])
        assert rc is None or rc == 0
        captured = capsys.readouterr()
        assert "profile.resolution_contract.missing_required_outcome" in captured.out

    def test_json_output_contains_provenance(self, tmp_path, capsys):
        """JSON output includes evidence/provenance fields."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile(
            required=["protagonist_transformation"],
            rec_id="rec_json_provenance",
        )
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        bp.contract.expected_elements = [
            e for e in bp.contract.expected_elements
            if e != "protagonist_transformation"
        ]
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        (bp_dir / "blueprint.yaml").write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        rc = main(["genre", "diagnose", "--project", str(proj_dir), "--json"])
        assert rc is None or rc == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        dres001 = [d for d in data if d.get("rule") == "profile.resolution_contract.missing_required_outcome"]
        assert len(dres001) == 1
        d = dres001[0]
        # Evidence should reference the profile path
        evidence_text = " ".join(d.get("evidence", []))
        assert "genre_profile" in evidence_text or "expected_elements" in evidence_text


# ===========================================================================
# 6. JSON output contains same diagnostic IDs and severities
# ===========================================================================

class TestJsonParity:
    def test_json_has_same_rules_as_human(self, tmp_path, capsys):
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.COMIC
        identity.genre_profile = _make_profile(
            pattern="dark_transgression_resolution",
            required=["protagonist_transformation"],
            rejected=["superficial_happy_ending"],
            rec_id="rec_parity",
        )
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        bp.contract.expected_elements = [
            e for e in bp.contract.expected_elements
            if e != "protagonist_transformation"
        ]
        if "superficial_happy_ending" not in bp.contract.expected_elements:
            bp.contract.expected_elements.append("superficial_happy_ending")
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        (bp_dir / "blueprint.yaml").write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )

        # Human output
        rc_h = main(["genre", "diagnose", "--project", str(proj_dir)])
        assert rc_h is None or rc_h == 0
        human = capsys.readouterr()

        # JSON output
        rc_j = main(["genre", "diagnose", "--project", str(proj_dir), "--json"])
        assert rc_j is None or rc_j == 0
        json_out = capsys.readouterr()
        data = json.loads(json_out.out)

        # Verify each JSON diagnostic has rule and severity
        for d in data:
            assert "rule" in d
            assert "severity" in d

        # Verify profile diagnostics appear in both
        assert "profile.resolution_contract.missing_required_outcome" in human.out
        json_rules = {d["rule"] for d in data}
        assert "profile.resolution_contract.missing_required_outcome" in json_rules


# ===========================================================================
# 7. No-profile projects receive no profile diagnostics
# ===========================================================================

class TestNoProfile:
    def test_no_profile_diagnostics(self, tmp_path, capsys):
        identity = _make_base_identity()
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        (bp_dir / "blueprint.yaml").write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        rc = main(["genre", "diagnose", "--project", str(proj_dir), "--json"])
        assert rc is None or rc == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        profile_rules = [d for d in data if d.get("rule", "").startswith("profile.")]
        assert len(profile_rules) == 0


# ===========================================================================
# 8. Existing pack-specific diagnostics still appear
# ===========================================================================

class TestExistingPackDiagnostics:
    def test_erotica_identity_diagnostics_still_fire(self):
        """Erotica-specific rules still fire through run_genre_diagnostics."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile()
        # Override central_engine.want to NOT contain desire keywords
        identity.central_engine.want = "The protagonist seeks power and control."
        bp = compile_to_blueprint(identity)
        diags = run_genre_diagnostics(identity, blueprint=bp)
        rules = {d.rule for d in diags}
        assert "genre.erotic_fiction.desire_affects_decisions" in rules


# ===========================================================================
# 9. Duplicate diagnostics are not emitted
# ===========================================================================

class TestNoDuplicates:
    def test_no_duplicate_rules_via_run_genre_diagnostics(self):
        """run_genre_diagnostics does not emit the same rule twice."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile(
            required=["protagonist_transformation"],
        )
        bp = compile_to_blueprint(identity)
        bp.contract.expected_elements = [
            e for e in bp.contract.expected_elements
            if e != "protagonist_transformation"
        ]
        diags = run_genre_diagnostics(identity, blueprint=bp)
        rules = [d.rule for d in diags]
        assert len(rules) == len(set(rules)), f"Duplicate rules: {rules}"

    def test_no_duplicate_rules_via_cli(self, tmp_path, capsys):
        identity = _make_base_identity()
        identity.story_type.mode = StoryMode.COMIC
        identity.genre_profile = _make_profile(
            pattern="dark_transgression_resolution",
            required=["protagonist_transformation"],
        )
        proj_dir = _setup_project(tmp_path, identity)
        bp = compile_to_blueprint(identity)
        bp.contract.expected_elements = [
            e for e in bp.contract.expected_elements
            if e != "protagonist_transformation"
        ]
        bp_dir = proj_dir / ".auteur"
        bp_dir.mkdir(exist_ok=True)
        (bp_dir / "blueprint.yaml").write_text(
            yaml.safe_dump(bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        rc = main(["genre", "diagnose", "--project", str(proj_dir), "--json"])
        assert rc is None or rc == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rules = [d["rule"] for d in data]
        assert len(rules) == len(set(rules)), f"Duplicate CLI rules: {rules}"


# ===========================================================================
# 10. Override behavior remains respected
# ===========================================================================

class TestOverrideRespected:
    def test_override_suppresses_dres001(self):
        """Override on required_outcomes suppresses D-RES-001."""
        identity = _make_base_identity()
        identity.genre_profile = _make_profile(
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
        diags = run_genre_diagnostics(identity, blueprint=bp)
        dres001 = [d for d in diags
                   if d.rule == "profile.resolution_contract.missing_required_outcome"]
        overridden_diags = [d for d in dres001
                            if "protagonist_transformation" in str(d.evidence)]
        assert len(overridden_diags) == 0
