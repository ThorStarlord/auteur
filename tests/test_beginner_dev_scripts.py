from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_package_scripts_expose_beginner_workflow_commands():
    package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    assert package["scripts"]["start"] == "node scripts/beginner-dev.mjs"
    assert package["scripts"]["workspace:new"] == "node scripts/beginner-workspace.mjs"
    assert package["scripts"]["qualification:sealed-elevator"] == "node scripts/qualification/sealed-elevator-human.mjs"
    assert package["scripts"]["dev"] == "node scripts/beginner-dev.mjs"
    assert package["private"] is True


def test_readme_documents_start_new_workspace_and_watch_commands():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "npm start" in readme
    assert "npm run workspace:new" in readme
    assert "npm run dev" in readme
    assert "127.0.0.1:8791" in readme
    assert "new workspace ID" in readme
