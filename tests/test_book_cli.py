import yaml

from auteur.cli import main
from auteur.series.models import BookPlan
from series_fixtures import valid_trilogy_data


def test_book_build_compiles_one_book_plan_to_story_identity(tmp_path):
    plan = BookPlan.model_validate(valid_trilogy_data()["book_plans"][0])
    source = tmp_path / "book_plan.yaml"
    output = tmp_path / "book" / "story_identity.yaml"
    source.write_text(yaml.safe_dump(plan.model_dump(mode="json"), sort_keys=False), encoding="utf-8")

    assert main(["book", "build", str(source), "--output", str(output)]) == 0
    assert output.exists()
    assert yaml.safe_load(output.read_text(encoding="utf-8"))["title"] == plan.title
