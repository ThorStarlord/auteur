"""A single Book element brought to an inquiry carries its question associations, and may be investigated on the open ones.

An association is engagement: the element references a Series question by identity. The owner reports each association against the
current Architecture's open questions, and an anchor on a question the element engages is accepted only while that question is open.
The Book owner's read of the element is stubbed here, because the seeded study records no element with a question association; the
owner's own packet function and its anchor rules are exercised as they are.
"""
import pytest

import auteur.beginner.studio_architecture_inquiry as inquiry
from auteur.beginner.studio_architecture_graph_intent import GraphIntent

CURRENT = {
    "request_sha256": "a" * 64,
    "candidate": {"open_question_ids": ["q-settlement", "q-finale"],
                  "open_questions": ["Is the conversion a lasting settlement?", "Which finale mechanism is chosen?"]},
}
ELEMENT_CONTENT = "c" * 64
BOOK_REQUEST = "b" * 64


def element(question_refs):
    return {"id": "obs-1", "collection": "observations", "content_sha256": ELEMENT_CONTENT, "text": "An observation.",
            "title": None, "attribution": "author", "epistemic_status": "working", "commitment_authority": "none",
            "form": "observation", "book_refs": [], "question_refs": question_refs}


def evidence(question_refs):
    return {"book_number": 24, "title": "Book 24", "revision_number": 2, "book_request_sha256": BOOK_REQUEST,
            "book_content_sha256": "d" * 64, "written_against_architecture_request_sha256": CURRENT["request_sha256"],
            "freshness": "current", "decision_question": None, "element": element(question_refs),
            "cited_architecture_concepts": []}


def intent(*anchors):
    return GraphIntent.model_validate({
        "canvas_id": "spring", "operation": "explain", "expected_candidate_request_sha256": CURRENT["request_sha256"],
        "author_text": "What does this observation engage?", "anchors": list(anchors)})


def reference():
    return inquiry.BookEvidenceRef(book_number=24, element_id="obs-1", expected_book_request_sha256=BOOK_REQUEST,
                                   expected_element_content_sha256=ELEMENT_CONTENT)


def test_each_association_names_the_question_by_identity_and_whether_it_is_still_open():
    rows = inquiry._question_associations(CURRENT, element(["q-settlement", "q-removed"]))
    assert [row["question_id"] for row in rows] == ["q-settlement", "q-removed"]
    assert rows[0]["standing"] == "open_in_current_architecture"
    assert rows[0]["current_wording"] == "Is the conversion a lasting settlement?"
    assert rows[1]["standing"] == "not_open_in_current_architecture" and rows[1]["current_wording"] is None
    assert all(row["note"] == inquiry.ASSOCIATION_NOTE for row in rows)
    assert "engagement" in inquiry.ASSOCIATION_NOTE and "not" in inquiry.ASSOCIATION_NOTE


def test_the_packet_carries_the_associations_and_an_open_engaged_question_may_anchor_the_inquiry(monkeypatch):
    monkeypatch.setattr(inquiry, "_book_evidence", lambda store, ref: evidence(["q-settlement"]))
    packet = inquiry._book_evidence_packet(None, CURRENT, intent({"kind": "question", "id": "q-settlement"}), reference())
    assert packet["question_associations"][0]["question_id"] == "q-settlement"
    assert packet["question_associations"][0]["standing"] == "open_in_current_architecture"
    assert packet["element"]["question_refs"] == ["q-settlement"]


def test_an_engaged_question_no_longer_open_cannot_anchor_the_inquiry(monkeypatch):
    # The only association is no longer open, and the element records no current concept: nothing is recorded to ask about.
    monkeypatch.setattr(inquiry, "_book_evidence", lambda store, ref: evidence(["q-removed"]))
    with pytest.raises(ValueError, match="records no reference to a concept the current working architecture has"):
        inquiry._book_evidence_packet(None, CURRENT, intent({"kind": "question", "id": "q-removed"}), reference())


def test_a_question_the_element_does_not_engage_cannot_anchor_the_inquiry(monkeypatch):
    monkeypatch.setattr(inquiry, "_book_evidence", lambda store, ref: evidence(["q-settlement"]))
    with pytest.raises(ValueError, match="every anchor must be a current Architecture concept"):
        inquiry._book_evidence_packet(None, CURRENT, intent({"kind": "question", "id": "q-finale"}), reference())


def test_the_guidance_tells_the_agent_an_association_is_engagement_and_not_an_answer():
    flat = " ".join(inquiry._BOOK_EVIDENCE_GUIDANCE.split())
    assert "question_associations names the Series questions" in flat
    assert "An association is engagement only" in flat
