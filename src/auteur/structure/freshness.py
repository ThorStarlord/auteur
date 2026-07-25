"""Freshness propagation — auto-update content hashes when a structural proposal is accepted.

When a proposal is accepted and applied to a blueprint, downstream artifacts'
content hashes and dependency pointers become stale. This module provides
:func:`propagate_acceptance` to refresh all affected provenance records in a
single call.
"""

from __future__ import annotations

from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.provenance.store import ArtifactStore, canonical_content_hash
from auteur.structure.proposal_application import apply_proposal_to_blueprint
from auteur.structure.proposal_models import StructureProposal


def propagate_acceptance(
    proposal: StructureProposal,
    blueprint_path: str,
    project_root: str,
) -> dict[str, str]:
    """Apply an accepted proposal and refresh all affected artifact references.

    This is the recommended entry-point for proposal acceptance.  It:
      1. Loads the blueprint from *blueprint_path*.
      2. Calls :func:`~auteur.structure.proposal_application.\
apply_proposal_to_blueprint` with ``in_place=True`` to merge the selected
         option and overwrite the original file.
      3. Re-accepts the blueprint in the :class:`~auteur.provenance.store.\
ArtifactStore` so its content hash reflects the new file on disk.
      4. Updates every downstream artifact's dependency records so they point
         to the new blueprint revision and content hash.

    Args:
        proposal:      The accepted proposal (must have a selected option).
        blueprint_path: Path to the blueprint YAML file to overwrite.
        project_root:  Root directory of the project (used to locate the
                       ``.auteur/state/artifacts/`` provenance store).

    Returns:
        A dict mapping every updated artifact ID to its new content hash.
    """
    # 1. Load blueprint and apply the proposal in-place
    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    _, target_path = apply_proposal_to_blueprint(
        proposal,
        blueprint,
        original_path=blueprint_path,
        in_place=True,
    )

    # 2. Refresh provenance store
    store = ArtifactStore(Path(project_root))
    bp_hash = canonical_content_hash(Path(target_path))

    updated: dict[str, str] = {}

    # Re-accept the blueprint artifact (bumps revision, updates content hash)
    meta = store.accept(Path(target_path), "blueprint")
    if meta is not None:
        updated[meta.artifact_id] = meta.content_hash
        bp_revision = meta.revision
    else:
        # If the store didn't have it yet, adopt it
        meta = store.adopt(Path(target_path), "blueprint")
        updated[meta.artifact_id] = meta.content_hash
        bp_revision = meta.revision

    # 3. Update every downstream artifact's dependency records so they
    #    reference the new blueprint revision / hash.
    for sidecar in store.root.glob("*.yaml"):
        dep_meta = store._load(sidecar.stem)
        if dep_meta is None:
            continue
        if not any(d.artifact_id == "blueprint" for d in dep_meta.dependencies):
            continue

        for dep in dep_meta.dependencies:
            if dep.artifact_id == "blueprint":
                dep.full_content_hash = bp_hash
                dep.projected_hash = bp_hash
                dep.revision = bp_revision

        store._write(dep_meta, snapshot=False)
        updated[dep_meta.artifact_id] = dep_meta.content_hash

    return updated
