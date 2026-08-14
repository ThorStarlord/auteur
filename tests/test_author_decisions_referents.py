"""TDD tests for F2: explicit promotion of a decision-local structural anchor
into a durable StructuralReferent (approved design 2026-08-canonical-referents
@ 90515ac). Agent-selected under the standing delegated-authority envelope.

Binding invariants:
- promotion is explicit/author-controlled (decision promote --anchor);
- durable subset copied: anchor_id->referent_id, kind, participants, carrier_refs;
- bears_on + nature are NOT promoted (decision-contextual);
- provenance links back to decision_id + anchor_id + timestamp;
- promotion MAY create the durable referent in Blueprint, but NEVER enacts the
  chosen outcome (no cut/keep interpretation, no story-content restructure);
- idempotent duplicate promotion; inert when a canonical referent already exists;
- fail closed on stale/unresolvable participant refs;
- no name/prose/fuzzy/LLM matching; no automatic promotion;
- backward compatible (existing blueprints load unchanged);
- F1 significance stays decision-local.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml as _yaml

from auteur.blueprint import StoryBlueprint

PY = sys.executable
FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE = FIXTURES / "case-goal-significance"


def _project(tmp_path, with_chosen: bool = False) -> Path:
    proj = tmp_path / "p"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(CASE / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(CASE / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    data = _yaml.safe_load((CASE / "absent.yaml").read_text(encoding="utf-8"))
    data.pop("goal_significance", None)
    if with_chosen:
        data["chosen"] = ["signe_marriage"]
    (ad / "goal-significance-absent.yaml").write_text(
        _yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return proj


def _promote(proj: Path, anchor: str = "signe_marriage"):
    return subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "promote", "goal-significance-absent",
         "--anchor", anchor, "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120)


def _blueprint(proj: Path) -> StoryBlueprint:
    return StoryBlueprint.from_yaml(proj / "blueprint.yaml")


def _blueprint_bytes(proj: Path) -> bytes:
    return (proj / "blueprint.yaml").read_bytes()


# ---------------------------------------------------------------------------
# Controls 1-2: promote creates a stable referent; outcome can address it
# ---------------------------------------------------------------------------

def test_promote_creates_durable_referent(tmp_path):
    proj = _project(tmp_path, with_chosen=True)
    r = _promote(proj)
    assert r.returncode == 0, r.stderr
    bp = _blueprint(proj)
    ids = [x.referent_id for x in bp.structural_referents]
    assert "signe_marriage" in ids


def test_promoted_referent_has_durable_subset_only(tmp_path):
    """kind, participants, carrier_refs are durable; bears_on/nature are NOT."""
    proj = _project(tmp_path, with_chosen=True)
    r = _promote(proj)
    assert r.returncode == 0, r.stderr
    bp = _blueprint(proj)
    ref = next(x for x in bp.structural_referents if x.referent_id == "signe_marriage")
    assert ref.kind == "subplot"
    assert ref.participants  # durable
    # provenance present, decision-contextual fields absent
    assert ref.provenance.promoted_from_decision_id == "goal-significance-absent"
    assert ref.provenance.promoted_from_anchor_id == "signe_marriage"
    # no bears_on/nature leaked into the durable referent
    assert not hasattr(ref, "bears_on")


# ---------------------------------------------------------------------------
# Control 3: unpromoted anchor remains local
# ---------------------------------------------------------------------------

def test_unpromoted_anchor_stays_local(tmp_path):
    proj = _project(tmp_path, with_chosen=False)
    bp = _blueprint(proj)
    assert "signe_marriage" not in [x.referent_id for x in bp.structural_referents]


# ---------------------------------------------------------------------------
# Control 4: already-canonical referent requires no promotion (idempotent/inert)
# ---------------------------------------------------------------------------

def test_duplicate_promotion_is_idempotent(tmp_path):
    proj = _project(tmp_path, with_chosen=True)
    r1 = _promote(proj)
    assert r1.returncode == 0, r1.stderr
    before = _blueprint_bytes(proj)
    r2 = _promote(proj)
    assert r2.returncode == 0, r2.stderr
    assert _blueprint_bytes(proj) == before  # no second copy


# ---------------------------------------------------------------------------
# Control 5: promotion does not enact cut/keep
# ---------------------------------------------------------------------------

def test_promotion_does_not_enact_outcome(tmp_path):
    proj = _project(tmp_path, with_chosen=True)
    before = _blueprint(proj)
    r = _promote(proj)
    assert r.returncode == 0, r.stderr
    after = _blueprint(proj)
    # promotion must NOT enact the outcome: story_engine and characters are
    # unchanged; only structural_referents may change.
    assert after.story_engine == before.story_engine
    assert after.characters == before.characters
    assert after.structural_referents != before.structural_referents


# ---------------------------------------------------------------------------
# Control 6: significance stays decision-local (not promoted)
# ---------------------------------------------------------------------------

def test_significance_not_promoted(tmp_path):
    proj = _project(tmp_path, with_chosen=True)
    r = _promote(proj)
    assert r.returncode == 0, r.stderr
    raw = _yaml.safe_load((proj / "blueprint.yaml").read_text(encoding="utf-8"))
    # no priority/weights/goal_significance anywhere in canonical blueprint
    text = (proj / "blueprint.yaml").read_text(encoding="utf-8")
    assert "goal_significance" not in text
    assert "ordered" not in raw.get("structural_referents", [{}])[0] if raw.get("structural_referents") else True


# ---------------------------------------------------------------------------
# Control 7: existing blueprints load unchanged (backward compat)
# ---------------------------------------------------------------------------

def test_existing_blueprint_without_referents_loads(tmp_path):
    proj = _project(tmp_path, with_chosen=False)
    bp = _blueprint(proj)
    assert bp.structural_referents == []


# ---------------------------------------------------------------------------
# Fail closed: stale/unresolvable participant ref
# ---------------------------------------------------------------------------

def test_promote_fails_closed_on_unknown_anchor(tmp_path):
    proj = _project(tmp_path, with_chosen=True)
    r = _promote(proj, anchor="does_not_exist")
    assert r.returncode != 0


def test_promote_fails_closed_on_stale_participant_ref(tmp_path):
    proj = _project(tmp_path, with_chosen=True)
    data = _yaml.safe_load(
        (proj / "author_decisions" / "goal-significance-absent.yaml").read_text(encoding="utf-8"))
    # corrupt the signe_marriage anchor's participant to an unresolvable path
    for a in data["structural_anchors"]:
        if a["anchor_id"] == "signe_marriage":
            a["participants"] = ["identity.characters[999]"]
    (proj / "author_decisions" / "goal-significance-absent.yaml").write_text(
        _yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    r = _promote(proj)
    assert r.returncode != 0
