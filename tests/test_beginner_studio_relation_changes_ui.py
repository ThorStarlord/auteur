"""Relationship change filtering doesn't masquerade as reconstructed history."""
from pathlib import Path

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_relationship_change_filters_present_explicit_caution():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    assert 'id="relationship-chapter"' in html
    assert "relationship_changes" in js
    assert "Current relation values are not historical snapshots." in js
