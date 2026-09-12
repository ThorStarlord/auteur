from pathlib import Path

import yaml

from auteur.decision.adapters.reconciliation_adapter import ReconciliationAdapter


def _write_proposal(root: Path, proposal_id: str, *, target: str, source: str) -> None:
    path = root / "chapters" / "1" / "expression" / "reconciliation" / "proposals" / f"{proposal_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "proposal_id": proposal_id,
                "target_artifact_id": target,
                "source_assembly": {"artifact_id": source},
                "source_inspection": "inspection_001",
                "conflicts": [{"id": f"{proposal_id}-conflict", "description": "needs review", "blocking": True}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_load_proposals_reads_matching_reconciliation_artifacts_without_writing(tmp_path: Path) -> None:
    _write_proposal(tmp_path, "proposal_one", target="scene_01", source="chapter_01")
    _write_proposal(tmp_path, "proposal_two", target="scene_02", source="chapter_02")
    before = {path: path.read_bytes() for path in tmp_path.rglob("*.yaml")}

    adapter = ReconciliationAdapter(tmp_path)

    assert [item["proposal_id"] for item in adapter.load_proposals("chapter_01")] == ["proposal_one"]
    assert [item["proposal_id"] for item in adapter.load_proposals("scene_02")] == ["proposal_two"]
    assert {path: path.read_bytes() for path in tmp_path.rglob("*.yaml")} == before


def test_adapter_exposes_blocking_conflicts_and_proposal_lineage(tmp_path: Path) -> None:
    _write_proposal(tmp_path, "proposal_one", target="scene_01", source="chapter_01")
    _write_proposal(tmp_path, "proposal_two", target="scene_02", source="chapter_01")
    adapter = ReconciliationAdapter(tmp_path)

    assert adapter.get_unresolved_obligations("chapter_01") == [
        "proposal_one-conflict",
        "proposal_two-conflict",
    ]
    assert [item["proposal_id"] for item in adapter.load_proposal_lineage("proposal_one")] == [
        "proposal_one",
        "proposal_two",
    ]
