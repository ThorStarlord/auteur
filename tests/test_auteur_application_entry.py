from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_windows_launcher_and_shortcut_installer_delegate_to_canonical_launcher() -> None:
    launcher = (ROOT / "Auteur.cmd").read_text(encoding="utf-8")
    installer = (ROOT / "scripts" / "install-auteur-shortcut.ps1").read_text(encoding="utf-8")

    assert "auteur open --project" in launcher
    assert "python -m auteur.cli open --project" in launcher
    assert "Auteur.cmd" in installer
    assert "Auteur.lnk" in installer


def test_package_scripts_keep_developer_and_product_entry_separate() -> None:
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    assert package["scripts"]["start"] == "node scripts/beginner-dev.mjs"
    assert package["scripts"]["dev"] == "node scripts/beginner-dev.mjs"
    assert package["scripts"]["app:open"] == "auteur open"
    assert "install-auteur-shortcut.ps1" in package["scripts"]["shortcut:install"]


def test_application_entry_docs_do_not_teach_workspace_creation_as_primary_launch() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    contract = (
        ROOT / "docs" / "design" / "2026-09-24-auteur-application-entry.md"
    ).read_text(encoding="utf-8")

    assert "# Open Auteur" in readme
    assert "auteur open" in readme
    assert "Auteur Home" in readme
    assert "npm run workspace:new" in readme
    assert "Advanced/developer commands" in readme

    assert "workspace ID" in contract
    assert "not the primary product" in contract
    assert "native packaged" in contract.lower()
