"""Tests for freshness propagation — auto-update content hashes on proposal acceptance."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.blueprint import StoryBlueprint
from auteur.provenance.store import ArtifactStore, canonical_content_hash
from auteur.structure.freshness import propagate_acceptance
from auteur.structure.proposal_models import (
    ProposalOption,
    ProposalType,
    StructureProposal,
)

SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_accepted_proposal() -> StructureProposal:
    """A minimal accepted proposal that changes the identity title."""
    return StructureProposal(
        proposal_id="freshness_test_001",
        type=ProposalType.GENERATION,
        summary="Test proposal for freshness propagation",
        options=[
            ProposalOption(
                id="opt_tighten",
                summary="Tighten the story scope",
                tradeoffs="Less room for subplots",
                data={
                    "identity": {
                        "title": "Refreshed Blueprint",
                        "author_intent": "A test with refreshed identity.",
                    }
                },
            ),
        ],
    )


def _set_up_project(tmp_path: Path) -> tuple[Path, Path, StoryBlueprint]:
    """Create a minimal project with an accepted blueprint in provenance store.

    Returns (project_root, blueprint_path, blueprint).
    """
    proot = tmp_path / "project"
    (proot / ".auteur" / "state" / "artifacts").mkdir(parents=True)

    bp_path = proot / "blueprint.yaml"
    bp = StoryBlueprint.from_yaml(SAMPLE_YAML)
    _write_yaml(bp_path, bp.model_dump(mode="json"))

    # Register the blueprint in the provenance store
    store = ArtifactStore(proot)
    store.accept(bp_path, "blueprint")
    return proot, bp_path, bp


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPropagateAcceptance:
    """propagate_acceptance refreshes provenance after proposal application."""

    def test_basic_propagation(self, tmp_path: Path) -> None:
        """After propagation the store's blueprint hash matches the file."""
        proot, bp_path, bp = _set_up_project(tmp_path)
        proposal = _make_accepted_proposal()
        proposal.accept("opt_tighten", author="test")

        result = propagate_acceptance(proposal, str(bp_path), str(proot))

        # The result should contain at least the blueprint artifact
        assert isinstance(result, dict)
        assert "blueprint" in result
        assert result["blueprint"].startswith("sha256:")

        # The stored content hash should match the on-disk hash
        store = ArtifactStore(proot)
        meta = store.current("blueprint")
        assert meta is not None
        on_disk_hash = canonical_content_hash(bp_path)
        assert meta.content_hash == on_disk_hash

    def test_updates_downstream_dependency_records(self, tmp_path: Path) -> None:
        """Downstream artifacts that depend on the blueprint get updated records."""
        proot, bp_path, bp = _set_up_project(tmp_path)
        store = ArtifactStore(proot)

        # Add a downstream artifact (chapter outline depending on blueprint)
        chapter_path = proot / "chapters" / "01" / "outline.yaml"
        _write_yaml(chapter_path, {"chapter_index": 1, "scenes": [{"id": "s1"}]})
        store.adopt(chapter_path, "chapter_outline")
        store.accept(chapter_path, "chapter_outline")

        # Capture the dependency hash before proposal application
        chapter_meta_before = store.current("chapter_01")
        assert chapter_meta_before is not None
        blueprint_hash_before = canonical_content_hash(bp_path)

        # Apply the proposal
        proposal = _make_accepted_proposal()
        proposal.accept("opt_tighten", author="test")
        result = propagate_acceptance(proposal, str(bp_path), str(proot))

        # The blueprint hash should have changed
        blueprint_hash_after = canonical_content_hash(bp_path)
        assert blueprint_hash_before != blueprint_hash_after, (
            f"blueprint hash did not change: {blueprint_hash_before}"
        )

        # The downstream artifact should have its dependency record updated
        chapter_meta_after = store.current("chapter_01")
        assert chapter_meta_after is not None
        bp_dep_after = next(
            (d for d in chapter_meta_after.dependencies if d.artifact_id == "blueprint"),
            None,
        )
        assert bp_dep_after is not None
        assert bp_dep_after.full_content_hash == blueprint_hash_after
        assert bp_dep_after.projected_hash == blueprint_hash_after

        # The result should include the downstream artifact ID
        assert "chapter_01" in result
        # The downstream artifact's own content hasn't changed, so its hash stays
        assert result["chapter_01"] == chapter_meta_before.content_hash

    def test_store_accepts_undocumented_blueprint(self, tmp_path: Path) -> None:
        """If the blueprint is not yet in the store, propagate_acceptance adopts it."""
        proot = tmp_path / "project"
        (proot / ".auteur" / "state" / "artifacts").mkdir(parents=True)
        bp_path = proot / "blueprint.yaml"
        _write_yaml(bp_path, StoryBlueprint.from_yaml(SAMPLE_YAML).model_dump(mode="json"))

        # Do NOT register the blueprint in the store beforehand
        proposal = _make_accepted_proposal()
        proposal.accept("opt_tighten", author="test")
        result = propagate_acceptance(proposal, str(bp_path), str(proot))

        assert "blueprint" in result
        assert result["blueprint"].startswith("sha256:")

        store = ArtifactStore(proot)
        meta = store.current("blueprint")
        assert meta is not None
        assert meta.content_hash == result["blueprint"]

    def test_returns_dict_of_updated_ids_and_hashes(self, tmp_path: Path) -> None:
        """Return value maps artifact IDs to their content hashes."""
        proot, bp_path, bp = _set_up_project(tmp_path)
        store = ArtifactStore(proot)

        # One downstream
        chapter_path = proot / "chapters" / "01" / "outline.yaml"
        _write_yaml(chapter_path, {"chapter_index": 1, "scenes": [{"id": "s1"}]})
        store.adopt(chapter_path, "chapter_outline")
        store.accept(chapter_path, "chapter_outline")

        proposal = _make_accepted_proposal()
        proposal.accept("opt_tighten", author="test")
        result = propagate_acceptance(proposal, str(bp_path), str(proot))

        # All keys are artifact IDs, all values are hashes
        assert len(result) >= 2
        for artifact_id, content_hash_value in result.items():
            assert isinstance(artifact_id, str)
            assert isinstance(content_hash_value, str)
            assert content_hash_value.startswith("sha256:")

    def test_integration_with_accept_flow(self, tmp_path: Path) -> None:
        """Full integration: proposal.accept() + propagate_acceptance leaves store fresh."""
        proot, bp_path, bp = _set_up_project(tmp_path)
        store = ArtifactStore(proot)

        # Build a proposal with a real option using the correct schema
        proposal = StructureProposal(
            proposal_id="intg_001",
            type=ProposalType.GENERATION,
            summary="Integration test proposal",
            options=[
                ProposalOption(
                    id="opt_rename",
                    summary="Rename the story",
                    tradeoffs="Minor",
                    data={
                        "identity": {
                            "title": "Integration Test",
                            "author_intent": "Integration test intent.",
                        }
                    },
                ),
            ],
        )

        # Author accepts the proposal
        proposal.accept("opt_rename", author="integration_test")

        # Verify the proposal state
        assert proposal.decision is not None
        assert proposal.decision.status == "accepted"

        # Run propagation
        result = propagate_acceptance(proposal, str(bp_path), str(proot))

        # Verify the store now has the updated blueprint
        assert "blueprint" in result
        meta = store.current("blueprint")
        assert meta is not None
        assert meta.lifecycle.value == "accepted"

        # The blueprint file on disk should have the merged title
        with open(bp_path, encoding="utf-8") as f:
            bp_data = yaml.safe_load(f)
        assert bp_data.get("identity", {}).get("title") == "Integration Test"

    def test_provenance_revision_bumps(self, tmp_path: Path) -> None:
        """Blueprint revision increments after proposal acceptance propagation."""
        proot, bp_path, bp = _set_up_project(tmp_path)
        store = ArtifactStore(proot)

        meta_before = store.current("blueprint")
        assert meta_before is not None
        rev_before = meta_before.revision

        proposal = _make_accepted_proposal()
        proposal.accept("opt_tighten", author="test")
        propagate_acceptance(proposal, str(bp_path), str(proot))

        meta_after = store.current("blueprint")
        assert meta_after is not None
        assert meta_after.revision == rev_before + 1
