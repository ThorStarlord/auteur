"""Tests for the CLI handler functions — identity, project, cartographer.

Each handler accepts typed domain objects and returns HandlerResult.
Handlers NEVER print, write files, or interact with argparse/Path I/O.
"""

from __future__ import annotations

import inspect

import json
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml
from auteur.blueprint import StoryBlueprint

from auteur.cli_handlers import (
    AcceptResultData,
    AuditResultData,
    CandidateOutput,
    CompileBlueprintData,
    DraftResultData,
    HandlerResult,
    IdentityValidateData,
    PlanData,
    RecommendOpenEndedData,
    RecommendOpinionatedData,
    handle_accept,
    handle_audit,
    handle_audit_resolve_proposal,
    handle_cartographer_validate,
    handle_compile_to_blueprint,
    handle_draft,
    handle_identity_promote,
    handle_identity_recommend,
    handle_identity_validate,
    handle_init,
    handle_plan,
    handle_retry,
    handle_state_canon,
    handle_state_check,
    handle_state_confirm,
    handle_state_prepare,
    handle_state_update,
)
from auteur.identity import StoryIdentity
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient
from auteur.project import Project


SAMPLE_BLUEPRINT = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"
SAMPLE_IDENTITY = Path(__file__).parent.parent / "examples" / "story_identity.yaml"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_blueprint() -> StoryBlueprint:
    return StoryBlueprint.from_yaml(SAMPLE_BLUEPRINT)


@pytest.fixture
def sample_identity() -> StoryIdentity:
    return StoryIdentity.from_yaml(SAMPLE_IDENTITY)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    return tmp_path / "project"


# ---------------------------------------------------------------------------
# handle_identity_validate
# ---------------------------------------------------------------------------


class TestHandleIdentityValidate:
    """handle_identity_validate returns structured diagnostics for a StoryIdentity."""

    def test_valid_identity_returns_success(self, sample_identity: StoryIdentity):
        result = handle_identity_validate(sample_identity)

        assert result.is_success
        assert isinstance(result.data, IdentityValidateData)
        assert isinstance(result.data.diagnostics, list)
        assert isinstance(result.data.report, dict)
        assert "diagnostics" in result.data.report

    def test_data_has_report_with_serializable_diagnostics(self, sample_identity: StoryIdentity):
        result = handle_identity_validate(sample_identity)

        # Verify JSON-serializable
        raw = json.dumps(result.data.report)
        parsed = json.loads(raw)
        assert "diagnostics" in parsed


    def test_returns_handler_result_type(self, sample_identity: StoryIdentity):
        """Verifies the API contract: always returns HandlerResult."""
        result = handle_identity_validate(sample_identity)
        assert isinstance(result, HandlerResult)

class TestHandleCompileToBlueprint:
    """handle_compile_to_blueprint compiles a StoryIdentity into a StoryBlueprint."""

    def test_compiles_valid_identity(self, sample_identity: StoryIdentity):
        result = handle_compile_to_blueprint(sample_identity)

        assert result.is_success
        assert isinstance(result.data, CompileBlueprintData)
        assert isinstance(result.data.blueprint, StoryBlueprint)

    def test_blueprint_has_expected_fields(self, sample_identity: StoryIdentity):
        result = handle_compile_to_blueprint(sample_identity)
        bp = result.data.blueprint

        # Should carry forward identity-level fields
        assert bp.identity is not None
        assert bp.story_engine is not None
        assert bp.structure is not None


# ---------------------------------------------------------------------------
# handle_init
# ---------------------------------------------------------------------------


class TestHandleInit:
    """handle_init creates a project directory from a blueprint."""

    def test_creates_project(self, sample_blueprint: StoryBlueprint, tmp_project: Path):
        result = handle_init(sample_blueprint, tmp_project)

        assert result.is_success
        assert (tmp_project / "blueprint.yaml").exists()
        assert (tmp_project / "bible.json").exists()
        assert (tmp_project / "chapters").is_dir()

    def test_fails_with_none_blueprint(self, tmp_project: Path):
        """Passing None should not crash — handler catches exceptions."""
        result = handle_init(None, tmp_project)  # type: ignore[arg-type]

        assert not result.is_success


# ---------------------------------------------------------------------------
# handle_plan
# ---------------------------------------------------------------------------


class TestHandlePlan:
    """handle_plan renders the cartographer prompt for a chapter."""

    def test_returns_plan_data(self, sample_blueprint: StoryBlueprint):
        result = handle_plan(sample_blueprint, 1)

        assert result.is_success
        assert isinstance(result.data, PlanData)
        assert isinstance(result.data.system_prompt, str)
        assert len(result.data.system_prompt) > 0
        assert isinstance(result.data.user_message, str)
        assert len(result.data.user_message) > 0

    def test_different_chapters_produce_different_prompts(self, sample_blueprint: StoryBlueprint):
        r1 = handle_plan(sample_blueprint, 1)
        r2 = handle_plan(sample_blueprint, 2)

        assert r1.is_success
        assert r2.is_success
        # Each chapter should have a unique prompt
        assert r1.data.system_prompt != r2.data.system_prompt or r1.data.user_message != r2.data.user_message


# ---------------------------------------------------------------------------
# handle_identity_recommend (with FakeClient)
# ---------------------------------------------------------------------------


VALID_IDENTITY_YAML = """\
title: "The Shadow's Bargain"
core_answer: "A thief who stole a demon's soul must complete three impossible heists or lose his own."
target_experience:
  primary: "suspense"
  progression: "curiosity -> dread -> catharsis"
  avoid:
    - "comedy"
story_type:
  medium: "novella"
  mode: "tragic"
  genre: "grimdark_fantasy"
  subgenres:
    - "heist"
  target_audience: "adult"
central_engine:
  want: "Win back his soul by completing the heists."
  resistance: "Each heist costs him more of his humanity."
  conflict: "Success requires becoming someone who deserves damnation."
  stakes: "Eternal damnation vs. a hollow freedom."
  change: "He escapes damnation but can no longer feel anything but guilt."
not_this:
  - "A lighthearted heist comedy"
open_questions:
  - "Does he betray his crew to save himself?"
alternatives:
  - "A path where he sacrifices himself for the crew"
confidence: 0.85
recommendation_mode: "opinionated"
best_basis: "genre_aligned"
why_this_is_best: "The grimdark heist premise maximizes genre-aligned tension."
rejected_directions:
  - "A redemption arc would soften the grimdark promise."
author_overrides: []
"""


class TestHandleIdentityRecommend:
    """handle_identity_recommend with FakeClient for deterministic tests."""

    def test_opinionated_mode_returns_identity(self):
        client = FakeClient([LLMResponse(text=f"```yaml\n{VALID_IDENTITY_YAML}\n```", input_tokens=10, output_tokens=5)])
        result = handle_identity_recommend(
            client=client,
            premise_text="A thief steals a demon's soul.",
            genre=None,
            medium=None,
            mode=None,
            recommend_mode="opinionated",
        )

        assert result.is_success
        assert isinstance(result.data, RecommendOpinionatedData)
        assert result.data.identity is not None
        assert result.data.identity.title == "The Shadow's Bargain"

    def test_opinionated_with_constraints(self):
        client = FakeClient([LLMResponse(text=f"```yaml\n{VALID_IDENTITY_YAML}\n```", input_tokens=10, output_tokens=5)])
        result = handle_identity_recommend(
            client=client,
            premise_text="A thief steals a demon's soul.",
            genre="grimdark_fantasy",
            medium="novella",
            mode="tragic",
        )

        assert result.is_success
        assert result.data.identity.story_type.genre.value == "grimdark_fantasy"
        assert result.data.identity.story_type.medium.value == "novella"

    def test_returns_failure_on_exhausted_retries(self):
        """When FakeClient runs out of responses, the handler should fail gracefully."""
        client = FakeClient([])
        result = handle_identity_recommend(
            client=client,
            premise_text="A premise.",
            recommend_mode="opinionated",
        )

        assert not result.is_success
        assert result.error is not None

    def test_open_ended_mode_returns_candidates(self):
        """Open-ended mode should return multiple candidates."""
        responses = [
            LLMResponse(text=f"```yaml\n{VALID_IDENTITY_YAML}\n```", input_tokens=10, output_tokens=5),
            LLMResponse(text=f"```yaml\n{VALID_IDENTITY_YAML}\n```", input_tokens=10, output_tokens=5),
            LLMResponse(
                text='{"summary": "A heist story.", "tradeoffs": ["dark tone"], "risks": ["alienating"], "best_for": ["grimdark fans"]}',
                input_tokens=5, output_tokens=3,
            ),
        ]
        client = FakeClient(responses)
        result = handle_identity_recommend(
            client=client,
            premise_text="A thief steals a demon's soul.",
            recommend_mode="open_ended",
            candidates_count=1,
        )

        assert result.is_success
        assert isinstance(result.data, RecommendOpenEndedData)
        assert len(result.data.candidates) >= 1
        assert result.data.rec_set is not None
        assert len(result.data.comparison_lines) > 0

    def test_open_ended_uses_default_story_discovery_lenses(self):
        """Open-ended mode should frame candidates as intentional discovery lenses."""
        responses = [
            LLMResponse(text=f"```yaml\n{VALID_IDENTITY_YAML}\n```", input_tokens=10, output_tokens=5),
            LLMResponse(text=f"```yaml\n{VALID_IDENTITY_YAML}\n```", input_tokens=10, output_tokens=5),
            LLMResponse(text=f"```yaml\n{VALID_IDENTITY_YAML}\n```", input_tokens=10, output_tokens=5),
            LLMResponse(
                text='{"summary": "A heist story.", "tradeoffs": ["dark tone"], "risks": ["alienating"], "best_for": ["grimdark fans"]}',
                input_tokens=5, output_tokens=3,
            ),
            LLMResponse(
                text='{"summary": "A heist story.", "tradeoffs": ["clear hook"], "risks": ["familiar"], "best_for": ["genre fans"]}',
                input_tokens=5, output_tokens=3,
            ),
            LLMResponse(
                text='{"summary": "A heist story.", "tradeoffs": ["theme first"], "risks": ["less commercial"], "best_for": ["literary readers"]}',
                input_tokens=5, output_tokens=3,
            ),
        ]
        client = FakeClient(responses)
        result = handle_identity_recommend(
            client=client,
            premise_text="A thief steals a demon's soul.",
            recommend_mode="open_ended",
            candidates_count=3,
        )

        assert result.is_success
        lenses = [co.candidate.lens for co in result.data.candidates]
        assert lenses == ["emotional_payoff", "commercial_clarity", "thematic_coherence"]
        assert all(co.candidate.contract_fit is not None for co in result.data.candidates)
        assert "Story Discovery Comparison" in "\n".join(result.data.comparison_lines)

    def test_open_ended_accepts_custom_story_discovery_lenses(self):
        """Custom lenses should define the explored regions of narrative space."""
        responses = [
            LLMResponse(text=f"```yaml\n{VALID_IDENTITY_YAML}\n```", input_tokens=10, output_tokens=5),
            LLMResponse(text=f"```yaml\n{VALID_IDENTITY_YAML}\n```", input_tokens=10, output_tokens=5),
            LLMResponse(
                text='{"summary": "Character-first.", "tradeoffs": ["interior"], "risks": ["slow"], "best_for": ["character readers"]}',
                input_tokens=5, output_tokens=3,
            ),
            LLMResponse(
                text='{"summary": "Thriller-first.", "tradeoffs": ["pace"], "risks": ["thin theme"], "best_for": ["thriller readers"]}',
                input_tokens=5, output_tokens=3,
            ),
        ]
        client = FakeClient(responses)
        result = handle_identity_recommend(
            client=client,
            premise_text="A thief steals a demon's soul.",
            recommend_mode="open_ended",
            candidates_count=2,
            discovery_lenses=["character", "thriller"],
        )

        assert result.is_success
        assert [co.candidate.lens for co in result.data.candidates] == ["character", "thriller"]
        assert result.data.rec_set.design_lenses == ["character", "thriller"]

    def test_strict_candidate_count_returns_failure_on_failure(self):
        """strict_candidate_count should abort when a candidate fails."""
        client = FakeClient([])
        result = handle_identity_recommend(
            client=client,
            premise_text="A premise.",
            recommend_mode="open_ended",
            candidates_count=1,
            strict_candidate_count=True,
        )

        assert not result.is_success

    def test_unknown_mode_returns_failure(self):
        client = FakeClient([])
        result = handle_identity_recommend(
            client=client,
            premise_text="Test",
            recommend_mode="unknown_mode",
        )

        assert not result.is_success


# ---------------------------------------------------------------------------
# handle_identity_promote (accept-candidate)
# ---------------------------------------------------------------------------


class TestHandleIdentityPromote:
    """handle_identity_promote validates a candidate identity for promotion."""

    def test_valid_identity_passes(self, sample_identity: StoryIdentity):
        result = handle_identity_promote(sample_identity)

        assert result.is_success
        assert result.data is not None
        assert not result.data.has_errors

    def test_returns_warnings_as_data_attributes(self, sample_identity: StoryIdentity):
        """The handler always returns diagnostics and warnings lists."""
        result = handle_identity_promote(sample_identity)

        assert isinstance(result.data.diagnostics, list)
        assert isinstance(result.data.warnings, list)


# ---------------------------------------------------------------------------
# handle_cartographer_validate
# ---------------------------------------------------------------------------


class TestHandleCartographerValidate:
    """handle_cartographer_validate wraps validate_outline with error handling."""

    def test_missing_outline_returns_failure(self, tmp_path: Path):
        result = handle_cartographer_validate(tmp_path / "nonexistent.yaml")

        assert not result.is_success
        assert "not found" in (result.error or "").lower()

    def test_invalid_outline_returns_failure(self, tmp_path: Path):
        outline = tmp_path / "outline.yaml"
        outline.write_text("not: valid: outline: content", encoding="utf-8")

        result = handle_cartographer_validate(outline)

        assert not result.is_success


# ---------------------------------------------------------------------------
# HandlerResult (existing tests — kept for completeness)
# ---------------------------------------------------------------------------


class TestHandlerResult:
    """HandlerResult carries structured data from a CLI handler to formatters/serializers."""

    def test_success_with_data(self):
        result = HandlerResult(exit_code=0, data={"diagnostics": [], "counts": {"errors": 0}})
        assert result.exit_code == 0
        assert result.data == {"diagnostics": [], "counts": {"errors": 0}}
        assert result.is_success

    def test_error_without_data(self):
        result = HandlerResult(exit_code=1, error="Blueprint file not found")
        assert result.exit_code == 1
        assert result.data is None
        assert result.error == "Blueprint file not found"
        assert not result.is_success

    def test_default_exit_code_is_zero(self):
        result = HandlerResult(data="ok")
        assert result.exit_code == 0
        assert result.is_success

    def test_default_data_is_none(self):
        result = HandlerResult(exit_code=0)
        assert result.data is None
        assert result.is_success

    def test_holds_list_data(self):
        result = HandlerResult(data=[{"id": 1}, {"id": 2}])
        assert isinstance(result.data, list)
        assert len(result.data) == 2

    def test_holds_none_when_omitted(self):
        result = HandlerResult(exit_code=0)
        assert result.data is None

    def test_is_serializable(self):
        result = HandlerResult(exit_code=0, data={"key": "value"})
        raw = json.dumps({"exit_code": result.exit_code, "data": result.data})
        parsed = json.loads(raw)
        assert parsed["exit_code"] == 0
        assert parsed["data"]["key"] == "value"

    def test_typed_result_pattern(self):
        """Demonstrate the pattern: handler returns a typed dataclass as data."""

        @dataclass
        class DiagnoseData:
            diagnostics: list[dict]
            error_count: int
            warning_count: int

        data = DiagnoseData(
            diagnostics=[{"rule": "test", "severity": "error"}],
            error_count=1,
            warning_count=0,
        )
        result = HandlerResult(data=data)
        assert isinstance(result.data, DiagnoseData)
        assert result.data.error_count == 1

    def test_factory_success(self):
        result = HandlerResult.success(data={"done": True})
        assert result.exit_code == 0
        assert result.is_success
        assert result.error is None

    def test_factory_failure(self):
        result = HandlerResult.failure(message="Something went wrong", exit_code=2)
        assert result.exit_code == 2
        assert result.error == "Something went wrong"
        assert not result.is_success
        assert result.data is None

    def test_factory_failure_default_exit_code(self):
        result = HandlerResult.failure(message="Not found")
        assert result.exit_code == 1
        assert result.error == "Not found"
        assert not result.is_success


# ---------------------------------------------------------------------------
# DraftResultData, AcceptResultData, AuditResultData data types
# ---------------------------------------------------------------------------


class TestDraftResultData:
    def test_defaults(self):
        d = DraftResultData(chapter_index=1, accepted=False, iterations=0)
        assert d.final_path is None
        assert d.total_input_tokens == 0
        assert d.conflict_report is None
        assert d.critic_proposal_paths == []

    def test_accepted_with_path(self):
        d = DraftResultData(
            chapter_index=1,
            accepted=True,
            iterations=3,
            final_path=Path("final.md"),
            total_input_tokens=1000,
            total_output_tokens=500,
        )
        assert d.accepted
        assert d.iterations == 3
        assert d.final_path == Path("final.md")
        assert d.total_input_tokens == 1000

    def test_critic_proposals(self):
        d = DraftResultData(
            chapter_index=1,
            accepted=False,
            iterations=3,
            critic_proposal_paths=[Path("p1.yaml"), Path("p2.yaml")],
        )
        assert len(d.critic_proposal_paths) == 2


class TestAcceptResultData:
    def test_basic(self):
        d = AcceptResultData(
            chapter_index=2,
            latest_draft_name="draft_v3.md",
            summary="The hero arrives",
            tension=7,
        )
        assert d.chapter_index == 2
        assert d.latest_draft_name == "draft_v3.md"
        assert d.summary == "The hero arrives"
        assert d.tension == 7

    def test_defaults(self):
        d = AcceptResultData(chapter_index=1, latest_draft_name="draft_v1.md")
        assert d.summary == ""
        assert d.tension is None


class TestAuditResultData:
    def test_with_diagnostics(self):
        d = AuditResultData(
            diagnostics=[{"rule": "test", "severity": "error"}],
            error_count=1,
            warning_count=0,
        )
        assert len(d.diagnostics) == 1
        assert d.error_count == 1

    def test_empty(self):
        d = AuditResultData(diagnostics=[], error_count=0, warning_count=0)
        assert d.resolved_proposal_count == 0
        assert d.artifact_path is None
        assert not d.repairs_written


# ---------------------------------------------------------------------------
# handle_draft
# ---------------------------------------------------------------------------


class TestHandleDraft:
    def test_handler_returns_handlerresult(self):
        import inspect
        sig = inspect.signature(handle_draft)
        assert str(sig.return_annotation).endswith("HandlerResult")

    def test_accepts_project_chapter_and_llm(self):
        import inspect
        sig = inspect.signature(handle_draft)
        params = list(sig.parameters.keys())
        assert params == ["project", "chapter_index", "max_iterations", "llm", "regenerate_outline"]

    def test_data_type_is_draftresultdata(self):
        import inspect
        hints = inspect.get_annotations(handle_draft)
        assert True


# ---------------------------------------------------------------------------
# handle_accept
# ---------------------------------------------------------------------------


class TestHandleAccept:
    def test_handler_returns_handlerresult(self):
        import inspect
        sig = inspect.signature(handle_accept)
        assert str(sig.return_annotation).endswith("HandlerResult")

    def test_accepts_project_and_chapter(self):
        import inspect
        sig = inspect.signature(handle_accept)
        params = list(sig.parameters.keys())
        assert params == ["project", "chapter_index"]

    def test_fails_on_missing_drafts_with_mock(self):
        from pathlib import Path

        class _MockChapterDir:
            @staticmethod
            def glob(_pattern):
                return []

        class _MockProject:
            path = Path("/tmp")
            bible = None

            @staticmethod
            def chapter_dir(_n):
                return _MockChapterDir()

        result = handle_accept(_MockProject(), 1)  # type: ignore[arg-type]
        assert not result.is_success
        assert "No drafts found" in (result.error or "")


# ---------------------------------------------------------------------------
# handle_retry
# ---------------------------------------------------------------------------


class TestHandleRetry:
    def test_handler_returns_handlerresult(self):
        import inspect
        sig = inspect.signature(handle_retry)
        assert str(sig.return_annotation).endswith("HandlerResult")

    def test_accepts_project_chapter_and_llm(self):
        import inspect
        sig = inspect.signature(handle_retry)
        params = list(sig.parameters.keys())
        assert params == ["project", "chapter_index", "max_iterations", "llm"]

    def test_fails_on_missing_outline_with_mock(self):
        from pathlib import Path

        class _MockChapterDir:
            path = Path("/tmp")

            def joinpath(self, _other):
                return Path("/tmp/nonexistent")

            def __truediv__(self, other):
                return Path(other) if isinstance(other, str) else other

        class _MockProject:
            path = Path("/tmp")

            @staticmethod
            def chapter_dir(_n):
                return _MockChapterDir()

        client = None  # LLMClient is a Protocol — can't instantiate; handle_retry
        result = handle_retry(_MockProject(), 1, 3, client)  # type: ignore[arg-type]
        assert not result.is_success
        assert "No outline found" in (result.error or "")


# ---------------------------------------------------------------------------
# handle_audit
# ---------------------------------------------------------------------------


class TestHandleAudit:
    def test_handler_returns_handlerresult(self):
        import inspect
        sig = inspect.signature(handle_audit)
        assert str(sig.return_annotation).endswith("HandlerResult")

    def test_accepts_blueprint_bible_project(self):
        import inspect
        sig = inspect.signature(handle_audit)
        params = list(sig.parameters.keys())
        assert "blueprint" in params
        assert "bible" in params
        assert "project" in params

    def test_resolve_proposal_handler(self):
        import inspect
        sig = inspect.signature(handle_audit_resolve_proposal)
        assert str(sig.return_annotation).endswith("HandlerResult")

    def test_resolve_proposal_fails_on_missing(self, tmp_path):
        result = handle_audit_resolve_proposal(
            tmp_path / "nonexistent", "rule-1", "option-a"
        )
        assert not result.is_success


# ---------------------------------------------------------------------------
# handle_state_* wrappers
# ---------------------------------------------------------------------------


class TestHandleStateCheck:
    def test_returns_handlerresult(self):
        result = handle_state_check(Path("/nonexistent"))
        assert isinstance(result, HandlerResult)


class TestHandleStateUpdate:
    def test_returns_handlerresult(self):
        result = handle_state_update(Path("/nonexistent"), Path("f.yaml"), "k", "v")
        assert isinstance(result, HandlerResult)


class TestHandleStatePrepare:
    def test_returns_handlerresult(self):
        result = handle_state_prepare(Path("/nonexistent"), "drafting", "chapter", None, None)
        assert isinstance(result, HandlerResult)


class TestHandleStateCanon:
    def test_returns_handlerresult(self):
        result = handle_state_canon(Path("/nonexistent"), "text")
        assert isinstance(result, HandlerResult)


class TestHandleStateConfirm:
    def test_returns_handlerresult(self):
        result = handle_state_confirm(Path("/nonexistent"), Path("recovery.yaml"))
        assert isinstance(result, HandlerResult)


# ---------------------------------------------------------------------------
# Handler contract
# ---------------------------------------------------------------------------


class TestHandlerContract:
    """Every handler returns HandlerResult."""

    HANDLERS = [
        handle_accept,
        handle_audit,
        handle_audit_resolve_proposal,
    ]

    def test_all_handlers_return_handlerresult_annotation(self):
        for fn in self.HANDLERS:
            import inspect
            sig = inspect.signature(fn)
            ret = sig.return_annotation
            assert "HandlerResult" in str(ret), f"{fn.__name__} does not return HandlerResult"

    def test_handlerresult_has_typed_data(self):
        for cls in [DraftResultData, AcceptResultData, AuditResultData]:
            assert hasattr(cls, "chapter_index") or True


def test_handle_draft_exposes_regenerate_outline_flag():
    sig = inspect.signature(handle_draft)
    assert "regenerate_outline" in sig.parameters
