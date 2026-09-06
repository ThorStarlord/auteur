from auteur.story_design_packs.tutor import tutor_recommend


def test_tutor_guidance_contains_teaching_and_author_boundary():
    guidance = tutor_recommend(
        ["superhero", "anti_hero", "hard_determinism"],
        decision="protagonist moral boundary",
        premise="a hero who believes free will is an illusion",
    )
    assert guidance.recommendation
    assert guidance.plain_language_explanation
    assert guidance.story_application.startswith("In ")
    assert guidance.tradeoffs
    assert guidance.alternatives
    assert guidance.question_for_author
    assert guidance.authority_status == "DERIVED / NOT CANON"
