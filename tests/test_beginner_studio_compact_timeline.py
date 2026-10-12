"""Temporal cards do not duplicate genre-wide engine and payoff essays."""
from pathlib import Path
BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"

def test_compact_phase_cards_and_selection_to_full_inspector():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    css = (BROWSER / "studio.css").read_text(encoding="utf-8")
    cards = js.split("function renderTimeline()", 1)[1].split("function render()", 1)[0]
    assert 'state.selectedPhase = phase.id;' in cards
    assert 'phase.genre_activations || []' in cards
    assert 'phase.parallel_with' in cards
    assert 'phase.narrative_function' in cards
    assert 'firstTrope' in cards and 'firstFunction' in cards
    assert 'contract.narrative_engine' not in cards
    assert 'contract.payoff_expectations' not in cards
    assert 'function renderPhaseInspector(phase)' in js
    assert 'phase.reader_experience' in js
    assert 'Inspect phase trope function' in js
    assert 'Inspect phase structural function' in js
    assert 'visitFacet(facet, key, id);' in js
    assert 'phase: state.selectedPhase' in js
    assert '.timeline-select[aria-pressed="true"]' in css
