from __future__ import annotations

import importlib.util
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_package_module():
    module_path = ROOT / "scripts" / "package_skill.py"
    assert module_path.exists(), "scripts/package_skill.py must exist"

    spec = importlib.util.spec_from_file_location("package_skill_script", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_package_story_identity_architect_skill_zip(tmp_path: Path) -> None:
    module = _load_package_module()
    skill_path = ROOT / "skills" / "story-identity-architect"
    output_path = tmp_path / "story-identity-architect.skill.zip"

    result = module.package_skill(skill_path, output_path)

    assert result == output_path
    assert output_path.exists()
    with zipfile.ZipFile(output_path) as archive:
        names = archive.namelist()

    assert names == [
        "SKILL.md",
        "agents/openai.yaml",
    ]


def test_package_skill_rejects_missing_metadata(tmp_path: Path) -> None:
    module = _load_package_module()
    skill_path = tmp_path / "incomplete-skill"
    skill_path.mkdir()
    (skill_path / "SKILL.md").write_text(
        """---
name: incomplete-skill
description: "valid but not package-ready"
---

# Incomplete Skill
""",
        encoding="utf-8",
    )

    output_path = tmp_path / "incomplete-skill.skill.zip"

    try:
        module.package_skill(skill_path, output_path)
    except module.PackageSkillError as exc:
        assert "agents/openai.yaml" in str(exc)
    else:
        raise AssertionError("Expected package_skill to reject missing openai metadata")
