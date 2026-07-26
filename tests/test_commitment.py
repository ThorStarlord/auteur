"""Tests for Portfolio Commitment and Coordinated Execution (v0.13.0)."""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.commitment.models import (
    PortfolioCommitment,
    ExecutionPlan,
    ExecutionStep,
    ExecutionStepState,
    ExecutionStepType,
    CommitmentState,
    DivergenceFinding,
    DivergenceSeverity,
    DivergenceType,
    CommitmentProgress,
    SCHEMA_VERSION,
    _stable_id,
)
from auteur.commitment.planner import CommitmentPlanner
from auteur.commitment.progress import CommitmentProgressTracker
from auteur.commitment.persistence import CommitmentStore

@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
    return tmp_path

@pytest.fixture
def sample_commitment() -> PortfolioCommitment:
    return PortfolioCommitment(
        commitment_id="cm-001",
        assignments={"dec-1": "a", "dec-2": "c"},
        state=CommitmentState.CREATED,
    )


# =========================================================================
# Models
# =========================================================================


class TestModels:

    def test_commitment_identity(self):
        c1 = PortfolioCommitment(commitment_id="cm-1", assignments={"dec-1": "a"})
        assert c1.commitment_id == "cm-1"
        assert c1.state == CommitmentState.CREATED

    def test_commitment_lifecycle(self):
        for state in CommitmentState:
            c = PortfolioCommitment(commitment_id=f"cm-{state.value}", assignments={"d1": "a"}, state=state)
            assert c.state == state

    def test_execution_step_types(self):
        for st in ExecutionStepType:
            s = ExecutionStep(step_id="s1", commitment_id="cm-1", decision_id="d1",
                              candidate_id="a", step_type=st)
            assert s.step_type == st

    def test_no_acceptance_in_models(self):
        """Commitment models must not perform acceptance."""
        c = PortfolioCommitment(commitment_id="cm-1", assignments={"d1": "a"})
        assert not hasattr(c, "accepted")
        assert not hasattr(c, "approved")

    def test_schema_version(self):
        c = PortfolioCommitment(commitment_id="cm-1", assignments={"d1": "a"})
        assert c.schema_version == SCHEMA_VERSION


# =========================================================================
# Commitment Creation
# =========================================================================


class TestCommitmentCreation:

    def test_create_commitment(self, project_root):
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        c = svc.create_commitment(assignments={"dec-1": "a", "dec-2": "c"}, confirm=True)
        assert c.commitment_id
        assert len(c.assignments) == 2
        assert c.state == CommitmentState.CREATED

    def test_requires_confirmation(self, project_root):
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        with pytest.raises(ValueError, match="Confirmation required"):
            svc.create_commitment(assignments={"dec-1": "a"}, confirm=False)

    def test_no_acceptance_during_creation(self, project_root):
        """Commitment creation must not create acceptance records."""
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        before_accepted = list((project_root / ".auteur").glob("**/acceptance*"))
        svc.create_commitment(assignments={"dec-1": "a"}, confirm=True)
        after_accepted = list((project_root / ".auteur").glob("**/acceptance*"))
        assert before_accepted == after_accepted

    def test_no_pointer_mutation_during_creation(self, project_root):
        """Commitment creation must not create canonical pointers."""
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        canon_dir = project_root / ".auteur" / "canonical"
        assert not canon_dir.exists()  # No canonical state before
        before = sorted(str(p) for p in project_root.rglob("*"))
        svc.create_commitment(assignments={"dec-1": "a"}, confirm=True)
        after = sorted(str(p) for p in project_root.rglob("*"))
        # Only .auteur/commitments/ files may be added
        unexpected = [f for f in after if f not in before and "commitments" not in str(f)]
        assert len(unexpected) == 0, f"Files outside commitments/: {unexpected}"


# =========================================================================
# Execution Planning
# =========================================================================


class TestPlanning:

    def test_plan_generation(self, sample_commitment):
        planner = CommitmentPlanner()
        plan = planner.plan(sample_commitment)
        assert plan.plan_id
        assert plan.commitment_id == "cm-001"
        assert len(plan.steps) > 0

    def test_sequential_dependencies(self, sample_commitment):
        planner = CommitmentPlanner()
        plan = planner.plan(sample_commitment)
        # First step should be READY, others PENDING
        assert plan.steps[0].state == ExecutionStepState.READY

    def test_step_ids_deterministic(self, sample_commitment):
        planner = CommitmentPlanner()
        plan1 = planner.plan(sample_commitment)
        plan2 = planner.plan(sample_commitment)
        assert [s.step_id for s in plan1.steps] == [s.step_id for s in plan2.steps]

    def test_authority_steps_marked(self, sample_commitment):
        planner = CommitmentPlanner()
        plan = planner.plan(sample_commitment)
        prepare_steps = [s for s in plan.steps if s.step_type == ExecutionStepType.PREPARE_ACCEPTANCE]
        for s in prepare_steps:
            assert s.safe_to_execute is False

    def test_safe_steps_marked(self, sample_commitment):
        planner = CommitmentPlanner()
        plan = planner.plan(sample_commitment)
        review_steps = [s for s in plan.steps if s.step_type == ExecutionStepType.START_REVIEW]
        for s in review_steps:
            assert s.safe_to_execute is True


# =========================================================================
# Execution
# =========================================================================


class TestExecution:

    def test_safe_step_can_execute(self, sample_commitment):
        from auteur.commitment.execution import CommitmentExecutor
        executor = CommitmentExecutor(Path("/tmp"))
        step = ExecutionStep(step_id="s1", commitment_id="cm-1", decision_id="d1",
                             candidate_id="a", step_type=ExecutionStepType.INSPECT_EVIDENCE,
                             state=ExecutionStepState.READY, safe_to_execute=True)
        can, _ = executor.can_execute(step)
        assert can is True

    def test_author_step_cannot_execute(self, sample_commitment):
        from auteur.commitment.execution import CommitmentExecutor
        executor = CommitmentExecutor(Path("/tmp"))
        step = ExecutionStep(step_id="s1", commitment_id="cm-1", decision_id="d1",
                             candidate_id="a", step_type=ExecutionStepType.PREPARE_ACCEPTANCE,
                             state=ExecutionStepState.READY, safe_to_execute=False)
        can, msg = executor.can_execute(step)
        assert can is False
        assert "authority" in msg.lower()

    def test_execute_inspect_evidence(self, sample_commitment):
        from auteur.commitment.execution import CommitmentExecutor
        executor = CommitmentExecutor(Path("/tmp"))
        step = ExecutionStep(step_id="s1", commitment_id="cm-1", decision_id="d1",
                             candidate_id="a", step_type=ExecutionStepType.INSPECT_EVIDENCE,
                             state=ExecutionStepState.READY, safe_to_execute=True)
        result = executor.execute_step(step)
        assert result.state == ExecutionStepState.COMPLETED

    def test_not_ready_step_cannot_execute(self, sample_commitment):
        from auteur.commitment.execution import CommitmentExecutor
        executor = CommitmentExecutor(Path("/tmp"))
        step = ExecutionStep(step_id="s1", commitment_id="cm-1", decision_id="d1",
                             candidate_id="a", step_type=ExecutionStepType.START_REVIEW,
                             state=ExecutionStepState.PENDING, safe_to_execute=True)
        can, msg = executor.can_execute(step)
        assert can is False


# =========================================================================
# Progress
# =========================================================================


class TestProgress:

    def test_progress_aggregate(self, sample_commitment):
        tracker = CommitmentProgressTracker()
        p = tracker.progress(sample_commitment)
        assert p.total == 2

    def test_progress_state_matches(self, sample_commitment):
        tracker = CommitmentProgressTracker()
        p = tracker.progress(sample_commitment)
        assert p.state == CommitmentState.CREATED.value

    def test_completed_state(self):
        c = PortfolioCommitment(
            commitment_id="cm-complete",
            assignments={"d1": "a", "d2": "c"},
            state=CommitmentState.COMPLETED,
        )
        tracker = CommitmentProgressTracker()
        p = tracker.progress(c)
        assert p.accepted_as_committed == 2


# =========================================================================
# Persistence
# =========================================================================


class TestPersistence:

    def test_save_commitment(self, project_root):
        store = CommitmentStore(project_root)
        c = PortfolioCommitment(commitment_id="cm-test", assignments={"d1": "a"})
        store.save_commitment(c)
        loaded = store.load_commitment("cm-test")
        assert loaded is not None
        assert loaded.commitment_id == "cm-test"

    def test_list_commitments(self, project_root):
        store = CommitmentStore(project_root)
        store.save_commitment(PortfolioCommitment(commitment_id="cm-1", assignments={"d1": "a"}))
        store.save_commitment(PortfolioCommitment(commitment_id="cm-2", assignments={"d2": "b"}))
        commitments = store.list_commitments()
        assert len(commitments) >= 2

    def test_latest_pointer(self, project_root):
        store = CommitmentStore(project_root)
        store.save_latest("cm-latest")
        assert store.load_latest_id() == "cm-latest"

    def test_save_plan(self, project_root):
        store = CommitmentStore(project_root)
        plan = ExecutionPlan(plan_id="plan-test", commitment_id="cm-1")
        store.save_plan(plan)

    def test_history(self, project_root):
        store = CommitmentStore(project_root)
        store.save_commitment(PortfolioCommitment(commitment_id="cm-hist", assignments={"d1": "a"}))
        history = store.list_history()
        assert len(history) >= 1


# =========================================================================
# Service Integration
# =========================================================================


class TestService:

    def test_service_requires_project(self, tmp_path):
        from auteur.commitment.service import CommitmentService
        with pytest.raises(ValueError, match="Not an Auteur project"):
            CommitmentService(tmp_path / "nonexistent")

    def test_create_and_plan(self, project_root):
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        c = svc.create_commitment(assignments={"dec-1": "a"}, confirm=True)
        plan = svc.plan(c.commitment_id)
        assert plan.plan_id
        assert len(plan.steps) > 0

    def test_status(self, project_root):
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        status = svc.status()
        assert "total_commitments" in status

    def test_list_commitments(self, project_root):
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        commitments = svc.list_commitments()
        assert isinstance(commitments, list)

    def test_inspect(self, project_root):
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        assert svc.inspect("nonexistent") is None


# =========================================================================
# CLI
# =========================================================================


class TestCLI:

    def test_commit_help(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["commit", "--help"])
        assert exc.value.code == 0

    def test_commit_create(self, project_root):
        from auteur.cli import main
        rc = main(["commit", "create", "--project", str(project_root),
                    "--assignment", "dec-1=a", "--assignment", "dec-2=c",
                    "--confirm"])
        assert rc == 0

    def test_commit_status(self, project_root):
        from auteur.cli import main
        rc = main(["commit", "status", "--project", str(project_root)])
        assert rc == 0

    def test_commit_no_project(self, tmp_path):
        from auteur.cli import main
        rc = main(["commit", "status", "--project", str(tmp_path)])
        assert rc == 1

    def test_commit_list(self, project_root):
        from auteur.cli import main
        rc = main(["commit", "list", "--project", str(project_root)])
        assert rc == 0

    def test_commit_history(self, project_root):
        from auteur.cli import main
        rc = main(["commit", "history", "--project", str(project_root)])
        assert rc == 0

    def test_commit_create_no_confirm(self, project_root):
        """--confirm is required by argparse."""
        from auteur.cli import main as cli_main
        with pytest.raises(SystemExit):
            cli_main(["commit", "create", "--project", str(project_root),
                       "--assignment", "dec-1=a"])
