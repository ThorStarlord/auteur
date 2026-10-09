from auteur.beginner.author_context import compose_author_context


def _events():
    return [
        {"chapter_index": 1, "summary": "The pump prediction becomes active.", "deltas": {"pump_prediction": "active"}},
        {"chapter_index": 1, "summary": "Nia carries a red umbrella.", "deltas": {"umbrella_color": "red"}},
        {"chapter_index": 2, "summary": "The convent link is accepted.", "deltas": {"convent_link": "accepted"}},
        {"chapter_index": 3, "summary": "Mara is revealed as Nia's older sister.", "deltas": {"mara_identity": "older_sister"}},
        {"chapter_index": 4, "summary": "Tom's trust is strained.", "deltas": {"tom_trust": "strained"}},
        {"chapter_index": 5, "summary": "The pump disaster is prevented.", "deltas": {"pump_status": "prevented"}},
        {"chapter_index": 5, "summary": "Record provenance remains unresolved.", "deltas": {"record_provenance": "unresolved"}},
    ]



def _expressions():
    return [
        {"chapter_index": 1, "source_ref": "chapters/01/final.md", "text": "Nia verifies the pump prediction while carrying a red umbrella."},
        {"chapter_index": 2, "source_ref": "chapters/02/final.md", "text": "Sister Beatrice reveals the convent link to the old forecasting office."},
        {"chapter_index": 3, "source_ref": "chapters/03/final.md", "text": "The Lantern is Mara, Nia's older sister; trust remains incomplete."},
        {"chapter_index": 4, "source_ref": "chapters/04/final.md", "text": "Tom's trust in Nia is strained as the investigation widens."},
        {"chapter_index": 5, "source_ref": "chapters/05/final.md", "text": "The pump disaster is prevented while record provenance remains unresolved."},
    ]

def _outline():
    return {
        "chapter_index": 6,
        "chapter_summary": "Expose forecasting misuse while preserving origin ambiguity.",
        "scenes": [{
            "purpose": "Nia chooses what can responsibly become public.",
            "continuity_constraints": [
                "Sister Beatrice's convent link supports the public-history choice.",
                "Mara's identity as Nia's older sister is already known.",
                "Tom's strained trust affects collaboration.",
                "The pump disaster was already prevented.",
                "Record provenance remains unresolved.",
            ],
        }],
    }


def test_glass_archive_context_keeps_dependencies_and_drops_old_trivia():
    result = compose_author_context(
        chapter_index=6,
        role="resolve forecasting misuse while preserving origin ambiguity",
        role_ref="chapters/06/outline.yaml",
        current_outline=_outline(),
        accepted_events=_events(),
        accepted_expressions=_expressions(),
        prior_chapter_refs=[{"chapter_index": i, "path": f"chapters/{i:02d}/final.md"} for i in range(1, 6)],
        structure_refs=["story_identity.yaml", "outline.yaml"],
    )
    fields = set(result["accepted_state"])
    assert "umbrella_color" not in fields
    assert {"convent_link", "mara_identity", "tom_trust", "pump_status", "record_provenance"} <= fields
    assert result["accepted_state"]["record_provenance"]["value"] == "unresolved"
    expression_chapters = {item["chapter_index"] for item in result["accepted_expression"]}
    assert expression_chapters == {2, 3, 4, 5}
    assert 1 not in expression_chapters
    assert len(result["evidence_index"]["accepted_chapter_refs"]) == 5
    assert len(result["evidence_index"]["accepted_event_refs"]) == 7
    assert "bible.json#/events/1" in result["evidence_index"]["omitted_accepted_event_refs"]


def test_recent_events_stay_available_without_semantic_retrieval():
    result = compose_author_context(
        chapter_index=6,
        role="A completely unrelated immediate goal",
        role_ref=None,
        current_outline={"chapter_summary": "A completely unrelated immediate goal"},
        accepted_events=_events(),
        accepted_expressions=_expressions(),
        prior_chapter_refs=[],
        structure_refs=[],
    )
    assert {item["chapter_index"] for item in result["accepted_history"]} == {4, 5}
    assert result["selection"]["mode"] == "bounded_recency_plus_current_plan_overlap"


def test_pending_and_attention_are_not_flattened_into_accepted_state():
    result = compose_author_context(
        chapter_index=3,
        role="continue investigation",
        role_ref="chapters/03/outline.yaml",
        current_outline={},
        accepted_events=[],
        prior_chapter_refs=[],
        structure_refs=[],
        pending_updates=[{
            "summary": "Sister Beatrice: carry forward",
            "source_ref": ".auteur/beginner/reconciliation/2.json#/proposal_items/0",
            "chapter_index": 2,
            "blocking": False,
        }],
        needs_attention=[{
            "summary": "Old review is stale.",
            "source_ref": "chapters/02/validation_v1.json",
            "chapter_index": 2,
            "blocking": False,
        }],
    )
    assert result["accepted_state"] == {}
    assert result["pending_updates"][0]["authority"] == "suggested"
    assert result["uncertainty"][0]["authority"] == "needs_attention"
    assert result["pending_updates"][0]["blocking"] is False


def test_inputs_are_not_mutated():
    events, outline = _events(), _outline()
    snapshot = repr((events, outline))
    compose_author_context(
        chapter_index=6,
        role="resolve",
        role_ref=None,
        current_outline=outline,
        accepted_events=events,
        prior_chapter_refs=[],
        structure_refs=[],
    )
    assert repr((events, outline)) == snapshot


def test_paraphrased_chapter_can_name_exact_accepted_sources_without_semantic_search():
    result = compose_author_context(
        chapter_index=6,
        role="Use independent harbor testimony before public disclosure",
        role_ref="chapters/06/outline.yaml",
        current_outline={
            "chapter_summary": "Weigh independent harbor witnesses",
            "scenes": [{
                "continuity_constraints": [
                    "Honor bible.json#/events/2 and chapters/02/final.md as accepted sources.",
                ],
            }],
        },
        accepted_events=_events(),
        accepted_expressions=_expressions(),
        prior_chapter_refs=[],
        structure_refs=[],
    )
    selected_refs = {item["source_ref"] for item in result["accepted_history"]}
    expression_refs = {item["source_ref"] for item in result["accepted_expression"]}
    assert "bible.json#/events/2" in selected_refs
    assert "chapters/02/final.md" in expression_refs
    assert result["accepted_state"]["convent_link"]["value"] == "accepted"
    assert "umbrella_color" not in result["accepted_state"]
    assert result["selection"]["explicit_sources_requested"] == 2
    assert result["evidence_index"]["unresolved_explicit_source_refs"] == []


def test_explicit_old_source_includes_later_updates_of_the_same_accepted_field():
    result = compose_author_context(
        chapter_index=6,
        role="Continue an unrelated task",
        role_ref=None,
        current_outline={
            "scenes": [{
                "continuity_constraints": ["Consult bible.json#/events/0."],
            }],
        },
        accepted_events=[
            {
                "chapter_index": 2,
                "summary": "The Lantern appears hostile.",
                "deltas": {"lantern_role": "enemy"},
            },
            {
                "chapter_index": 3,
                "summary": "A later accepted decision changes the relationship.",
                "deltas": {"lantern_role": "possible_ally"},
            },
        ],
        accepted_expressions=[],
        prior_chapter_refs=[],
        structure_refs=[],
    )
    assert len(result["accepted_history"]) == 2
    assert result["accepted_state"]["lantern_role"]["value"] == "possible_ally"
    assert result["accepted_state"]["lantern_role"]["source_ref"] == "bible.json#/events/1"
    assert "later_update_to_explicit_source" in result["accepted_history"][1]["relevance_reasons"]


def test_missing_explicit_accepted_source_is_visible_and_blocking():
    result = compose_author_context(
        chapter_index=6,
        role="Continue the Book",
        role_ref=None,
        current_outline={
            "scenes": [{
                "continuity_constraints": [
                    "Read bible.json#/events/99 and chapters/02/final.md first.",
                ],
            }],
        },
        accepted_events=_events(),
        accepted_expressions=[],
        prior_chapter_refs=[],
        structure_refs=[],
    )
    missing = result["evidence_index"]["unresolved_explicit_source_refs"]
    assert missing == ["bible.json#/events/99", "chapters/02/final.md"]
    assert result["selection"]["explicit_sources_unresolved"] == 2
    assert all(item["blocking"] for item in result["uncertainty"])
    assert all(item["authority"] == "needs_attention" for item in result["uncertainty"])
    assert "bible.json#/events/99" not in result["evidence_index"]["accepted_event_refs"]


def test_explicit_old_dependency_cannot_restore_stale_state_when_bible_is_unordered():
    result = compose_author_context(
        chapter_index=6,
        role="New task without the old name",
        role_ref=None,
        current_outline={"continuity_constraints": ["Check bible.json#/events/1."]},
        accepted_events=[
            {
                "chapter_index": 3,
                "summary": "Latest accepted development.",
                "deltas": {"lantern_role": "possible_ally"},
            },
            {
                "chapter_index": 2,
                "summary": "Earlier accepted assumption.",
                "deltas": {"lantern_role": "enemy"},
            },
        ],
        prior_chapter_refs=[],
        structure_refs=[],
    )
    assert result["accepted_state"]["lantern_role"]["value"] == "possible_ally"
    assert result["accepted_state"]["lantern_role"]["chapter_index"] == 3
