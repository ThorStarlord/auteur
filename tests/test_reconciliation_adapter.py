from pathlib import Path

import yaml

from auteur.decision.adapters.reconciliation_adapter import ReconciliationAdapter


def test_load_proposals_reads_expression_reconciliation_store(tmp_path: Path) -> None:
    (tmp_path / ".auteur").mkdir()
    proposal_dir = tmp_path / "chapters" / "01" / "expression" / "reconciliation" / "proposals"
    proposal_dir.mkdir(parents=True)
    proposal = {
        "proposal_id": "proposal-1",
        "target_artifact_id": "scene-1",
        "conflicts": [{"id": "c1", "classification": "creative", "description": "Choose one", "blocking": True}],
    }
    (proposal_dir / "proposal-1.yaml").write_text(yaml.safe_dump(proposal), encoding="utf-8")

    loaded = ReconciliationAdapter(tmp_path).load_proposals("scene-1")

    assert [item["proposal_id"] for item in loaded] == ["proposal-1"]
