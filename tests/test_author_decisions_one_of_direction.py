"""TDD tests for choice-shape consequence composition: combination_direction
extends to one_of (approved design 2026-08-choice-shape-composition.md @ da1f366).

Binding invariants under test:
- combination_direction stays EXACTLY {kept, cut}; valid ONLY for one_of and
  choose_k_of_n; fail closed on any other shape;
- one_of + kept  -> selected = kept, non-selected = cut;
- one_of + cut   -> selected = cut, non-selected = kept;
- one_of without direction -> selection membership only, NO keep/cut composition;
- direction is NEVER inferred from question text, criterion text, labels, or ids
  (misleading "which should be cut?" wording with direction absent -> no composition);
- consumer reuses the shipped nature x kept/cut x resolved-target composition
  (one_of + direction behaves as the semantic equivalent of choose_k_of_n(k=1));
- backward compatible: existing directionless one_of artifacts stay schema-
  compatible (gaining only the honest membership observation); choose_k_of_n
  goldens byte-identical.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml as _yaml

from auteur.author_decisions import (
    AuthorDecision,
    build_decision_context,
    DecisionValidationError,
)
from auteur.blueprint import StoryBlueprint
from auteur.identity import StoryIdentity

FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE_ONE_OF = FIXTURES / "case-one-of"
CASE_D = FIXTURES / "case-d"
CASE_E = FIXTURES / "case-e"


def load_identity(case_dir: Path):
    return StoryIdentity.from_yaml(case_dir / "story_identity.yaml")


def load_blueprint(case_dir: Path):
    return StoryBlueprint.from_yaml(case_dir / "blueprint.yaml")


def ctx_for(decision, case_dir: Path):
    return build_decision_context(decision, load_identity(case_dir), load_blueprint(case_dir))


def decision_for(name: str):
    return AuthorDecision.from_yaml(CASE_ONE_OF / name)


def all_messages(cons):
    msgs = [o["message"] for o in cons["observations"]]
    for a in cons["alternatives"]:
        msgs += [f["message"] for f in a["findings"]]
    for c in cons.get("combinations", []):
        msgs += [f["message"] for f in c["findings"]]
    return msgs


# ---------------------------------------------------------------------------
# Schema: combination_direction valid for one_of, fail closed elsewhere
# ---------------------------------------------------------------------------

def test_one_of_direction_kept_parses():
    dec = decision_for("one-of-kept.yaml")
    assert dec.combination_direction == "kept"
    assert dec.combination.rule == "one_of"


def test_one_of_direction_cut_parses():
    dec = decision_for("one-of-cut.yaml")
    assert dec.combination_direction == "cut"


def test_one_of_directionless_parses():
    dec = decision_for("one-of-directionless.yaml")
    assert dec.combination_direction is None


def test_direction_value_closed_vocabulary():
    data = _yaml.safe_load((CASE_ONE_OF / "one-of-directionless.yaml").read_text(encoding="utf-8"))
    data["combination_direction"] = "replace"
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_direction_fail_closed_unknown_shape():
    """If a future decision shape were added, direction must be rejected on it.
    The rule Literal only admits one_of|choose_k_of_n today, so this exercises
    the validator's fail-closed structure via a forced invalid rule."""
    data = _yaml.safe_load((CASE_ONE_OF / "one-of-directionless.yaml").read_text(encoding="utf-8"))
    data["combination"] = {"rule": "choose_two"}
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


# ---------------------------------------------------------------------------
# Probe: honest semantics observation for one_of
# ---------------------------------------------------------------------------

def test_probe_one_of_direction_message():
    cons = ctx_for(decision_for("one-of-kept.yaml"), CASE_ONE_OF).build_report()["consequences"]
    assert any(
        "authored combination direction: one_of means kept" == o["message"]
        for o in cons["observations"]
    )


def test_probe_one_of_cut_message():
    cons = ctx_for(decision_for("one-of-cut.yaml"), CASE_ONE_OF).build_report()["consequences"]
    assert any(
        "authored combination direction: one_of means cut" == o["message"]
        for o in cons["observations"]
    )


def test_probe_one_of_directionless_message():
    cons = ctx_for(decision_for("one-of-directionless.yaml"), CASE_ONE_OF).build_report()["consequences"]
    assert any(
        "selection membership is explicit; no keep/cut composition is performed" == o["message"]
        for o in cons["observations"]
    )


# ---------------------------------------------------------------------------
# Consumer: one_of + direction composes like choose_k_of_n(k=1)
# ---------------------------------------------------------------------------

def test_one_of_kept_composition():
    cons = ctx_for(decision_for("one-of-kept.yaml"), CASE_ONE_OF).build_report()["consequences"]
    combos = cons["combinations"]
    by_members = {tuple(c["combination"]): c for c in combos}
    # one singleton combination per alternative
    assert set(by_members) == {("marta_pregnancy",), ("signe_marriage",)}
    # selected kept -> preserves its declared relationships
    keep_marta = by_members[("marta_pregnancy",)]
    assert keep_marta["kept"] == ["marta_pregnancy"]
    assert keep_marta["cut"] == ["signe_marriage"]
    msgs = [f["message"] for f in keep_marta["findings"]]
    assert "kept alternative marta_pregnancy preserves its declared sustaining relationship to " \
           "blueprint.contract.mandatory_ending_tone = bittersweet" in msgs
    assert "kept alternative marta_pregnancy preserves its declared pressuring relationship to " \
           "blueprint.identity.pov_type = third_person_limited_single" in msgs
    # non-selected cut -> removes its declared relationships
    assert "cut alternative signe_marriage removes its declared sustaining relationship to " \
           "blueprint.identity.pov_type = third_person_limited_single" in msgs
    assert "cut alternative signe_marriage removes its declared pressuring relationship to " \
           "blueprint.contract.mandatory_ending_tone = bittersweet" in msgs


def test_one_of_cut_composition():
    cons = ctx_for(decision_for("one-of-cut.yaml"), CASE_ONE_OF).build_report()["consequences"]
    by_members = {tuple(c["combination"]): c for c in cons["combinations"]}
    cut_marta = by_members[("marta_pregnancy",)]
    assert cut_marta["kept"] == ["signe_marriage"]
    assert cut_marta["cut"] == ["marta_pregnancy"]
    msgs = [f["message"] for f in cut_marta["findings"]]
    # selected cut -> removes its declared relationships
    assert "cut alternative marta_pregnancy removes its declared sustaining relationship to " \
           "blueprint.contract.mandatory_ending_tone = bittersweet" in msgs
    assert "cut alternative marta_pregnancy removes its declared pressuring relationship to " \
           "blueprint.identity.pov_type = third_person_limited_single" in msgs
    # non-selected kept -> preserves its declared relationships
    assert "kept alternative signe_marriage preserves its declared sustaining relationship to " \
           "blueprint.identity.pov_type = third_person_limited_single" in msgs


def test_one_of_directionless_no_composition():
    cons = ctx_for(decision_for("one-of-directionless.yaml"), CASE_ONE_OF).build_report()["consequences"]
    # status quo: no combination sections, no composed keeps/removes
    assert "combinations" not in cons
    msgs = all_messages(cons)
    assert not any("removes its declared" in m or "preserves its declared" in m for m in msgs)
    # relationship-level natures still render
    assert any("nature: sustains" in m for m in msgs)


def test_misleading_wording_no_composition():
    """'which should be cut?' in the question must NOT imply direction."""
    cons = ctx_for(decision_for("one-of-misleading.yaml"), CASE_ONE_OF).build_report()["consequences"]
    assert "combinations" not in cons
    msgs = all_messages(cons)
    assert not any("removes its declared" in m or "preserves its declared" in m for m in msgs)


def test_substitute_wording_remains_unrepresented():
    """Substitution operation is deferred: substitute-wording directionless
    one_of renders no composition — unsupported semantics stay honest."""
    data = _yaml.safe_load((CASE_ONE_OF / "one-of-directionless.yaml").read_text(encoding="utf-8"))
    data["unresolved_choice"]["question"] = (
        "Which subplot should be substituted into the main thread as its new primary engine, "
        "replacing the current arrangement?"
    )
    data["criterion"]["text"] = "Which subplot to substitute into the main thread"
    cons = ctx_for(AuthorDecision.from_dict(data), CASE_ONE_OF).build_report()["consequences"]
    assert "combinations" not in cons
    msgs = all_messages(cons)
    assert not any("removes its declared" in m or "preserves its declared" in m for m in msgs)


# ---------------------------------------------------------------------------
# Golden discriminators + backward compatibility
# ---------------------------------------------------------------------------

def test_one_of_kept_golden():
    cons = ctx_for(decision_for("one-of-kept.yaml"), CASE_ONE_OF).build_report()["consequences"]
    golden = _yaml.safe_load((CASE_ONE_OF / "expected-consequences-kept.yaml").read_text(encoding="utf-8"))
    assert cons == golden


def test_one_of_cut_golden():
    cons = ctx_for(decision_for("one-of-cut.yaml"), CASE_ONE_OF).build_report()["consequences"]
    golden = _yaml.safe_load((CASE_ONE_OF / "expected-consequences-cut.yaml").read_text(encoding="utf-8"))
    assert cons == golden


def test_no_verdict_in_one_of_composition():
    cons = ctx_for(decision_for("one-of-kept.yaml"), CASE_ONE_OF).build_report()["consequences"]
    msgs = all_messages(cons)
    assert not any("recommend" in m.lower() for m in msgs)
    assert not any("therefore" in m.lower() for m in msgs)


def test_choose_k_of_n_goldens_byte_identical():
    """Existing choose_k_of_n goldens must not change."""
    for case_dir, decision_name in (
        (CASE_E, "salt-of-the-earth-subplot-cut.yaml"),
    ):
        dec = AuthorDecision.from_yaml(case_dir / decision_name)
        cons = ctx_for(dec, case_dir).build_report()["consequences"]
        golden = _yaml.safe_load((case_dir / "expected-consequences.yaml").read_text(encoding="utf-8"))
        assert cons == golden, decision_name


def test_case_d_directionless_golden_updated():
    """Case D is a directionless one_of: schema-compatible, gaining ONLY the
    honest membership observation; nothing else changes."""
    dec = AuthorDecision.from_yaml(CASE_D / "nine-chairs-structure.yaml")
    cons = ctx_for(dec, CASE_D).build_report()["consequences"]
    golden = _yaml.safe_load((CASE_D / "expected-consequences.yaml").read_text(encoding="utf-8"))
    assert cons == golden
