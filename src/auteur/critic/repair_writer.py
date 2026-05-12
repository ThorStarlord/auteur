"""Critic repair writer — convert error findings into StructureProposal YAML files.

When a chapter draft exhausts its iteration budget, the error-severity
critic findings are promoted to Decision Packets (StructureProposal YAML)
so the author can review options and resolve them.
"""

from __future__ import annotations

import re
from pathlib import Path

from auteur.critic import CriticFinding, ValidationReport
from auteur.structure.proposal_models import (
    ProposalOption,
    ProposalType,
    StructureProposal,
)


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", text.lower().replace(" ", "_").replace("-", "_"))


_PRESERVE_TRADEOFFS = (
    "Preserves the current outline and blueprint constraints. "
    "The author edits the chapter draft to address the finding."
)

_CHALLENGE_TRADEOFFS = (
    "Keeps the chapter draft as-is. The author must revise the outline or "
    "blueprint constraint that the finding conflicts with."
)


def _finding_to_proposal(
    finding: CriticFinding,
    chapter_index: int,
) -> StructureProposal:
    """Convert one error-severity CriticFinding into a StructureProposal."""
    slug = f"critic_{finding.critic}_{chapter_index:02d}_{_slugify(finding.rule)}"
    summary = (
        f"[{finding.critic.upper()}] {finding.severity.upper()}: "
        f"{finding.evidence[:120]}"
    )

    options = [
        ProposalOption(
            id="preserve_intent",
            summary=finding.requested_change,
            tradeoffs=_PRESERVE_TRADEOFFS,
            data={},
        ),
        ProposalOption(
            id="challenge_intent",
            summary=(
                "Accept the draft and revise the outline or blueprint "
                "constraint that conflicts with this finding."
            ),
            tradeoffs=_CHALLENGE_TRADEOFFS,
            data={},
        ),
    ]

    return StructureProposal(
        proposal_id=slug,
        type=ProposalType.REPAIR,
        source_rule=finding.rule,
        summary=summary,
        options=options,
    )


def write_critic_proposals(
    proposals_dir: Path,
    report: ValidationReport,
    chapter_index: int,
) -> list[Path]:
    """Write error-severity critic findings as StructureProposal YAML files.

    Args:
        proposals_dir: Directory to write proposal YAML files into.
        report: The ValidationReport from the last (failed) iteration.
        chapter_index: Chapter number for proposal ID generation.

    Returns:
        List of paths to written proposal files.
    """
    import yaml as _yaml

    error_findings = [f for f in report.findings if f.severity == "error"]
    written: list[Path] = []

    for finding in error_findings:
        proposal = _finding_to_proposal(finding, chapter_index)

        # Skip if already resolved
        proposal_path = proposals_dir / f"{proposal.proposal_id}.yaml"
        if proposal_path.exists():
            continue

        proposal_path.write_text(
            _yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        written.append(proposal_path)

    return written
