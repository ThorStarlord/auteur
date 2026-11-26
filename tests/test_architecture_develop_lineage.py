"""Developing over an existing working Architecture keeps its revision lineage (concern A, PR #643 review).

The Studio's "Develop architecture with coding agent" button is always rendered and sends an empty instruction. Over an
existing Architecture that is a regeneration. It must name the version it replaces, so the revision chain, the question
history read through it and every identity retired along it stay whole. Before the fix, the regenerated version had no
review and no lineage, so the chain read it as a first version: earlier history became unreachable, and an identity
retired by an earlier revision could name a different question again.
"""
import copy
import shutil
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import _candidate, architecture_revision_chain, prepare_architecture, complete_architecture
from auteur.beginner.studio_architecture_question_projection import project_architecture_questions
from auteur.beginner.studio_store import CanvasStore

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities  # noqa: E402


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("develop-lineage") / "discovery"
    discovery.seed_discovery(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    target = tmp_path / "discovery"
    shutil.copytree(pristine, target)
    return target


def ledger_store(project: Path) -> CanvasStore:
    return CanvasStore(project, discovery.SPRING)


def develop_over_existing(store: CanvasStore) -> str:
    """The Studio's develop action over an existing Architecture: an empty instruction, from the same sources."""
    # A collaboration preference makes this request distinct from the seeded first develop of the same sources.
    waiting = prepare_architecture(store, instruction="", initiative="exploration_intensive")
    regenerated = copy.deepcopy(_candidate(store)["candidate"])
    complete_architecture(store, impact.base._reply(waiting["request"], regenerated, "develop-over-existing"))
    return waiting["request"]["request_sha256"]


def test_a_develop_over_an_existing_architecture_keeps_every_earlier_version_reachable(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    impact.revise_architecture(store, "Remove the first open question.", _drop_first_question)
    before = architecture_revision_chain(store)
    assert before["complete"]

    regenerated = develop_over_existing(store)

    after = architecture_revision_chain(store)
    assert after["complete"], "the regenerated version must name the version it replaced"
    assert after["requests"][0] == regenerated
    assert after["requests"][1:] == before["requests"]
    view = project_architecture_questions(store)
    assert view["history"]["chain_complete"]
    assert view["history"]["versions_read"] == len(after["requests"])


def test_an_identity_retired_before_a_develop_stays_retired_after_it(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    retired = _candidate(store)["candidate"]["open_question_ids"][0]
    impact.revise_architecture(store, "Remove the first open question.", _drop_first_question)
    develop_over_existing(store)

    def reuse(candidate):
        candidate["open_questions"].append("A new question about the ferry timetable?")
        candidate["open_question_ids"].append(retired)

    with pytest.raises(ValueError, match="already used by an earlier version"):
        impact.revise_architecture(store, "Ask about the ferry timetable.", reuse)
    assert retired not in _candidate(store)["candidate"]["open_question_ids"]


def _drop_first_question(candidate):
    candidate["open_questions"] = candidate["open_questions"][1:]
    candidate["open_question_ids"] = candidate["open_question_ids"][1:]
