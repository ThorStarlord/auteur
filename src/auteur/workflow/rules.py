"""Deterministic stage detection, blocker inference, and recommendation ranking."""

from __future__ import annotations

from pathlib import Path

from auteur.status import gather_status
from auteur.workflow.models import (
    AuthorityLevel,
    BlockerCategory,
    BlockerSeverity,
    StageProgress,
    WorkflowAction,
    WorkflowBlocker,
    WorkflowStage,
)

STAGE_ORDER = [
    WorkflowStage.IDENTITY,
    WorkflowStage.STRUCTURE,
    WorkflowStage.REALIZATION,
    WorkflowStage.DRAFTING,
    WorkflowStage.REASONING,
    WorkflowStage.RECONCILIATION,
    WorkflowStage.ACCEPTANCE,
    WorkflowStage.ASSEMBLY,
    WorkflowStage.PUBLISHING,
]

_STAGE_INDEX = {s: i for i, s in enumerate(STAGE_ORDER)}


def detect_stages(project_root: Path) -> list[StageProgress]:
    """Detect completeness for each workflow stage. Read-only."""
    root = Path(project_root)
    status = gather_status(root)
    blocks = status.get("blocks", [])

    identity_paths = [
        root / "story_identity.yaml",
        root / ".auteur" / "state" / "artifacts" / "story_identity.yaml",
    ]
    identity_ok = any(p.exists() for p in identity_paths)
    blueprint_ok = (root / "blueprint.yaml").exists()
    blueprint_valid = blueprint_ok and _read_yaml(root / "blueprint.yaml") is not None

    chapter_dirs = sorted(root.glob("chapters/*"))
    has_outlines = any((ch / "outline.yaml").exists() for ch in chapter_dirs if ch.is_dir())
    has_drafts = bool(list(root.rglob("draft_v*.md")))
    has_accepted = any(
        (ch / "expression" / "accepted.yaml").exists()
        for ch in chapter_dirs if ch.is_dir()
    )

    book_acc = root / "book" / "expression" / "accepted.yaml"
    has_book = book_acc.exists()

    _detect_recon_complete = _reconciliation_done(root)

    stages: list[StageProgress] = []

    # Identity
    id_blockers = []
    if not identity_ok:
        id_blockers.append(WorkflowBlocker(
            category=BlockerCategory.MISSING_PREREQUISITE,
            severity=BlockerSeverity.BLOCKING,
            message="No accepted story identity found",
            artifact="story_identity.yaml",
        ))
    stages.append(StageProgress(
        stage=WorkflowStage.IDENTITY,
        is_complete=identity_ok,
        current_artifact="story_identity.yaml" if identity_ok else None,
        blockers=id_blockers,
    ))

    # Structure
    struct_blockers = []
    if not blueprint_ok:
        struct_blockers.append(WorkflowBlocker(
            category=BlockerCategory.MISSING_PREREQUISITE,
            severity=BlockerSeverity.BLOCKING,
            message="No blueprint.yaml found",
            artifact="blueprint.yaml",
        ))
    elif not blueprint_valid:
        struct_blockers.append(WorkflowBlocker(
            category=BlockerCategory.INVALID_ARTIFACT,
            severity=BlockerSeverity.BLOCKING,
            message="blueprint.yaml is unparseable or invalid",
            artifact="blueprint.yaml",
        ))
    stages.append(StageProgress(
        stage=WorkflowStage.STRUCTURE,
        is_complete=blueprint_valid,
        current_artifact="blueprint.yaml" if blueprint_ok else None,
        blockers=struct_blockers,
    ))

    # Realization (outlines)
    real_blockers = []
    if blueprint_valid and not has_outlines:
        real_blockers.append(WorkflowBlocker(
            category=BlockerCategory.MISSING_PREREQUISITE,
            severity=BlockerSeverity.BLOCKING,
            message="No chapter outlines found — run cartographer compile",
            artifact="outline.yaml",
        ))
    stages.append(StageProgress(
        stage=WorkflowStage.REALIZATION,
        is_complete=has_outlines,
        current_artifact="outline.yaml" if has_outlines else None,
        blockers=real_blockers,
    ))

    # Drafting
    draft_blockers = []
    if not has_drafts and has_outlines:
        draft_blockers.append(WorkflowBlocker(
            category=BlockerCategory.MISSING_PREREQUISITE,
            severity=BlockerSeverity.INFO,
            message="No drafts yet — run auteur draft",
            artifact="draft_v*.md",
        ))
    stages.append(StageProgress(
        stage=WorkflowStage.DRAFTING,
        is_complete=has_drafts,
        current_artifact="draft_v*.md" if has_drafts else None,
        blockers=draft_blockers,
    ))

    # Reasoning
    reasoning_complete = has_accepted
    reasoning_blockers = []
    if has_drafts and not has_accepted:
        stale = any(
            b.get("severity") == "warning" and b.get("artifact", "").startswith("chapter:")
            for b in blocks
        )
        if stale:
            reasoning_blockers.append(WorkflowBlocker(
                category=BlockerCategory.STALE_ARTIFACT,
                severity=BlockerSeverity.WARNING,
                message="Some chapter expressions are stale",
            ))
    stages.append(StageProgress(
        stage=WorkflowStage.REASONING,
        is_complete=reasoning_complete,
        blockers=reasoning_blockers,
    ))

    # Reconciliation
    recon_blockers = []
    if has_accepted and not _detect_recon_complete:
        recon_blockers.append(WorkflowBlocker(
            category=BlockerCategory.UNRESOLVED_RECONCILIATION,
            severity=BlockerSeverity.WARNING,
            message="Reconciliation not yet completed",
        ))
    stages.append(StageProgress(
        stage=WorkflowStage.RECONCILIATION,
        is_complete=_detect_recon_complete,
        blockers=recon_blockers,
    ))

    # Acceptance (book-level)
    acc_blockers = []
    if _detect_recon_complete and not has_book:
        acc_blockers.append(WorkflowBlocker(
            category=BlockerCategory.UNRESOLVED_RECONCILIATION,
            severity=BlockerSeverity.WARNING,
            message="Book-level expression not yet accepted",
        ))
    stages.append(StageProgress(
        stage=WorkflowStage.ACCEPTANCE,
        is_complete=has_book,
        blockers=acc_blockers,
    ))

    # Assembly
    assembly_complete = (root / "book" / "expression" / "completion.yaml").exists()
    stages.append(StageProgress(
        stage=WorkflowStage.ASSEMBLY,
        is_complete=assembly_complete,
    ))

    # Publishing
    pub_complete = any(
        (root / ".auteur" / "publishing" / "releases").glob("*.yaml")
    ) if (root / ".auteur" / "publishing" / "releases").exists() else False
    stages.append(StageProgress(
        stage=WorkflowStage.PUBLISHING,
        is_complete=pub_complete,
    ))

    return stages


def current_stage(stages: list[StageProgress]) -> WorkflowStage | None:
    """Find the first incomplete stage, or None if all complete."""
    for sp in stages:
        if not sp.is_complete:
            return sp.stage
    return None


def collect_blockers(stages: list[StageProgress]) -> list[WorkflowBlocker]:
    """Aggregate all blockers from all stages."""
    result: list[WorkflowBlocker] = []
    for sp in stages:
        result.extend(sp.blockers)
    return result


def integrate_decision_actions(
    decisions: list[Any],
    current_stage: WorkflowStage | None,
) -> list[WorkflowAction]:
    """Convert AuthorDecision next-actions to WorkflowActions.

    Returns actions ranked by priority: blocked first, then author-decision,
    then evaluation/comparison, then acceptance-ready.
    """
    if not decisions:
        return []

    from auteur.decision.models import DecisionReadiness
    from auteur.workflow.models import FORBIDDEN_DECISION_ACTIONS, SAFE_DECISION_ACTIONS

    workflow_actions: list[WorkflowAction] = []

    for decision in decisions:
        # Map DecisionReadiness to workflow action
        readiness = decision.readiness
        decision_id = decision.decision_id

        if readiness == DecisionReadiness.BLOCKED:
            workflow_actions.append(WorkflowAction(
                label=f"Review blockers: {decision_id[:12]}...",
                command=f"auteur decision inspect {decision_id}",
                authority=AuthorityLevel.READ_ONLY,
                description=f"Decision {decision_id[:12]}... is blocked. Inspect to see blockers.",
                auto_executable=True,
            ))
        elif readiness == DecisionReadiness.NEEDS_CANDIDATE:
            workflow_actions.append(WorkflowAction(
                label=f"Generate candidate: {decision_id[:12]}...",
                command=f"auteur decision next {decision_id}",
                authority=AuthorityLevel.CANDIDATE_GENERATION,
                description=f"Decision {decision_id[:12]}... needs a candidate.",
                auto_executable=True,
            ))
        elif readiness == DecisionReadiness.NEEDS_EVALUATION:
            workflow_actions.append(WorkflowAction(
                label=f"Evaluate candidate: {decision_id[:12]}...",
                command=f"auteur decision next {decision_id}",
                authority=AuthorityLevel.CANDIDATE_GENERATION,
                description=f"Decision {decision_id[:12]}... has unevaluated candidates.",
                auto_executable=True,
            ))
        elif readiness == DecisionReadiness.NEEDS_COMPARISON:
            workflow_actions.append(WorkflowAction(
                label=f"Compare candidates: {decision_id[:12]}...",
                command=f"auteur decision compare {decision_id}",
                authority=AuthorityLevel.DERIVED_ARTIFACT,
                description=f"Decision {decision_id[:12]}... has multiple candidates to compare.",
                auto_executable=True,
            ))
        elif readiness == DecisionReadiness.NEEDS_RECONCILIATION:
            workflow_actions.append(WorkflowAction(
                label=f"Resolve conflicts: {decision_id[:12]}...",
                command=f"auteur decision conflicts {decision_id}",
                authority=AuthorityLevel.READ_ONLY,
                description=f"Decision {decision_id[:12]}... has unresolved reconciliation conflicts.",
                auto_executable=False,
            ))
        elif readiness == DecisionReadiness.NEEDS_AUTHOR_DECISION:
            workflow_actions.append(WorkflowAction(
                label=f"Author decision needed: {decision_id[:12]}...",
                command=f"auteur decision inspect {decision_id}",
                authority=AuthorityLevel.AUTHORITY_BEARING,
                description=f"Decision {decision_id[:12]}... requires author input.",
                auto_executable=False,
            ))
        elif readiness == DecisionReadiness.READY_FOR_ACCEPTANCE:
            workflow_actions.append(WorkflowAction(
                label=f"Prepare acceptance: {decision_id[:12]}...",
                command=f"auteur decision prepare-acceptance {decision_id} --candidate <id>",
                authority=AuthorityLevel.DERIVED_ARTIFACT,
                description=f"Decision {decision_id[:12]}... is ready for acceptance preparation.",
                auto_executable=False,
            ))

    return workflow_actions


def recommend_actions(
    stages: list[StageProgress],
    status: dict | None = None,
    decisions: list[Any] | None = None,
) -> list[WorkflowAction]:
    """Generate recommended actions based on current stage, blockers, and open decisions."""
    actions: list[WorkflowAction] = []
    cs = current_stage(stages)

    # Generate decision-aware actions when decisions are provided
    decision_actions: list[WorkflowAction] = []
    if decisions:
        decision_actions = integrate_decision_actions(decisions, cs)

    # When no decisions are open, pure workflow behavior
    if not decision_actions:
        if cs is None:
            actions.append(WorkflowAction(
                label="All stages complete",
                command="",
                authority=AuthorityLevel.READ_ONLY,
                description="All workflow stages are complete.",
            ))
            return actions

        if cs == WorkflowStage.IDENTITY:
            actions.append(WorkflowAction(
                label="Define story identity",
                command="auteur identity recommend your_premise.txt --output story_identity.yaml",
                authority=AuthorityLevel.CANDIDATE_GENERATION,
                description="Generate a recommended story identity from a premise text file.",
            ))
        elif cs == WorkflowStage.STRUCTURE:
            actions.append(WorkflowAction(
                label="Diagnose structure",
                command="auteur structure diagnose blueprint.yaml",
                authority=AuthorityLevel.READ_ONLY,
                description="Run structural diagnostics on the blueprint.",
            ))
            actions.append(WorkflowAction(
                label="Seed blueprint from identity",
                command="auteur blueprint seed story_identity.yaml --output blueprint.yaml",
                authority=AuthorityLevel.DERIVED_ARTIFACT,
                description="Compile identity into a blueprint skeleton.",
            ))
        elif cs == WorkflowStage.REALIZATION:
            actions.append(WorkflowAction(
                label="Compile chapter outlines",
                command="auteur cartographer compile --blueprint blueprint.yaml --project .",
                authority=AuthorityLevel.DERIVED_ARTIFACT,
                description="Generate chapter outlines from the blueprint (requires LLM).",
            ))
            actions.append(WorkflowAction(
                label="Check realization convergence status",
                command="auteur realization status --chapter 1 --project .",
                authority=AuthorityLevel.READ_ONLY,
                description="Inspect scene/chapter convergence and revision status.",
            ))
        elif cs == WorkflowStage.DRAFTING:
            actions.append(WorkflowAction(
                label="Draft first chapter",
                command="auteur draft . 1",
                authority=AuthorityLevel.CANDIDATE_GENERATION,
                description="Draft chapter 1 through the planning and iteration pipeline.",
            ))
        elif cs == WorkflowStage.REASONING:
            actions.append(WorkflowAction(
                label="Review reasoning findings",
                command="auteur reasoning review PATH_TO_REVIEW --project .",
                authority=AuthorityLevel.READ_ONLY,
                description="Inspect derived reasoning reviews.",
            ))
        elif cs == WorkflowStage.RECONCILIATION:
            actions.append(WorkflowAction(
                label="Inspect reconciliation",
                command="auteur expression inspect-book-manuscript PATH_TO_MANUSCRIPT --project .",
                authority=AuthorityLevel.READ_ONLY,
                description="Inspect book manuscript reconciliation status.",
            ))
        elif cs == WorkflowStage.ACCEPTANCE:
            actions.append(WorkflowAction(
                label="Accept book expression",
                command="auteur expression compose-book --project .",
                authority=AuthorityLevel.DERIVED_ARTIFACT,
                description="Compose and accept the book-level expression.",
            ))
        elif cs == WorkflowStage.ASSEMBLY:
            actions.append(WorkflowAction(
                label="Complete assembly",
                command="auteur expression complete-book-reconciliation ACCEPTANCE_ID --project .",
                authority=AuthorityLevel.AUTHORITY_BEARING,
                description="Complete book-level reconciliation.",
            ))
        elif cs == WorkflowStage.PUBLISHING:
            actions.append(WorkflowAction(
                label="Create release",
                command="auteur publishing release --project .",
                authority=AuthorityLevel.AUTHORITY_BEARING,
                description="Create a publishing release.",
            ))

        return actions

    # Decisions are open — interleave decision actions with workflow stage actions
    # Decision actions come first when relevant to the current stage
    actions.extend(decision_actions)

    # Append current-stage workflow action if it exists (for context)
    if cs is not None:
        stage_labels = {
            WorkflowStage.IDENTITY: "Current stage: Identity — continue with story definition",
            WorkflowStage.STRUCTURE: "Current stage: Structure — continue with structural planning",
            WorkflowStage.REALIZATION: "Current stage: Realization — continue with scene/outline work",
            WorkflowStage.DRAFTING: "Current stage: Drafting — continue with chapter drafting",
            WorkflowStage.REASONING: "Current stage: Reasoning — continue with review",
            WorkflowStage.RECONCILIATION: "Current stage: Reconciliation",
            WorkflowStage.ACCEPTANCE: "Current stage: Acceptance",
            WorkflowStage.ASSEMBLY: "Current stage: Assembly",
            WorkflowStage.PUBLISHING: "Current stage: Publishing",
        }
        label = stage_labels.get(cs, f"Current stage: {cs.value}")
        actions.append(WorkflowAction(
            label=label,
            command="",
            authority=AuthorityLevel.READ_ONLY,
            description=f"Workflow stage: {cs.value}",
        ))

    return actions


def _reconciliation_done(root: Path) -> bool:
    """Check if book-level reconciliation is complete."""
    for base in [root / ".auteur" / "book" / "expression" / "reconciliation",
                 root / "book" / "expression" / "reconciliation"]:
        completions = sorted(base.glob("completions/*.yaml")) if base.exists() else []
        if completions:
            return True
    return False


def _read_yaml(path: Path) -> dict | None:
    import yaml
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, yaml.YAMLError):
        return None
