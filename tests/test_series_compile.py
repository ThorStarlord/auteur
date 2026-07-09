from __future__ import annotations

import yaml

from series_fixtures import valid_trilogy_data


def test_trilogy_compiles_to_valid_story_identities():
    from auteur.cli_handlers import handle_identity_validate
    from auteur.series.compiler import compile_book_identities
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())
    identities = compile_book_identities(series)

    assert len(identities) == 3
    assert [identity.title for identity in identities] == [
        "Ashes of Order",
        "The Civil Crown",
        "The Human Throne",
    ]
    assert all(handle_identity_validate(identity).is_success for identity in identities)
    assert all(not handle_identity_validate(identity).data.has_error for identity in identities)


def test_write_book_identities(tmp_path):
    from auteur.series.compiler import write_book_identities
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())
    written = write_book_identities(series, tmp_path / "series")

    assert len(written) == 3
    for index in range(1, 4):
        path = tmp_path / "series" / f"book_{index:02d}" / "story_identity.yaml"
        assert path.exists()
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["title"]
