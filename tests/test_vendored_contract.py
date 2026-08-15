"""Focused tests for scripts/verify_vendored_contract.py."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import verify_vendored_contract as vvc  # noqa: E402


class TestManifestLoad:
    def test_real_manifest_loads(self):
        manifest = vvc.load_manifest()
        assert manifest["contract_name"] == "vendored-sensemaking-subset"
        assert manifest["status"] == "intentional_curated_subset"
        assert (
            manifest["source"]["revision"]
            == "1458f9210c79336175878b8527ed7ecba1e0b6a3"
        )
        assert manifest["source"]["baseline_status"] == "canonical_pinned"
        assert manifest["historical_provenance"]["previous_revision"] == "UNRECORDED"
        assert (
            manifest["historical_provenance"]["provenance_status"]
            == "unrecoverable_for_pinning"
        )

    def test_missing_manifest_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            vvc.load_manifest(tmp_path / "nope.yaml")

    def test_malformed_manifest_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("schema_version: 2\n")
        with pytest.raises(ValueError):
            vvc.load_manifest(bad)


class TestDrift:
    def _manifest(self, tmp_path, root, included=None, excluded=None):
        manifest = {
            "schema_version": 1,
            "included": included or {
                "skills": ["demo-skill"],
                "scripts": ["demo-script.py"],
                "framework_docs": ["docs/demo.md"],
            },
            "excluded": excluded or ["skills/workflow-planner"],
        }
        # Build the included files so the baseline is clean.
        (root / "skills" / "demo-skill").mkdir(parents=True, exist_ok=True)
        (root / "skills" / "demo-skill" / "SKILL.md").write_text("x")
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "demo-script.py").write_text("x")
        (root / "docs").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "demo.md").write_text("x")
        return manifest

    def test_clean_contract(self, tmp_path):
        manifest = self._manifest(tmp_path, root=tmp_path)
        assert vvc.check_drift(manifest, root=tmp_path) == []

    def test_missing_included_is_drift(self, tmp_path):
        manifest = self._manifest(tmp_path, root=tmp_path)
        (tmp_path / "scripts" / "demo-script.py").unlink()
        problems = vvc.check_drift(manifest, root=tmp_path)
        assert any("demo-script.py" in p for p in problems)

    def test_excluded_present_is_drift(self, tmp_path):
        manifest = self._manifest(tmp_path, root=tmp_path)
        (tmp_path / "skills" / "workflow-planner").mkdir(parents=True)
        problems = vvc.check_drift(manifest, root=tmp_path)
        assert any("workflow-planner" in p for p in problems)

    def test_real_tree_is_clean(self):
        manifest = vvc.load_manifest()
        assert vvc.check_drift(manifest) == []
