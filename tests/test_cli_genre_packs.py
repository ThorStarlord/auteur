"""CLI tests for Genre Packs commands."""

import json
from pathlib import Path
import pytest

from auteur.cli import main
from auteur.identity import StoryIdentity, HighLevelCentralEngine, StoryType
from auteur.blueprint import Genre, StoryMedium, StoryMode, TargetExperience


def _setup_project(tmp_path: Path) -> Path:
    proj_dir = tmp_path / "test_proj"
    proj_dir.mkdir()
    ident = StoryIdentity(
        title="Test Story",
        core_answer="An intense story of desire and identity transformation.",
        target_experience=TargetExperience(primary="desire", progression="rising", avoid=[]),
        story_type=StoryType(medium=StoryMedium.NOVEL, mode=StoryMode.INTIMATE, genre=Genre.ROMANCE),
        central_engine=HighLevelCentralEngine(
            want="Surrender to passion.",
            resistance="Fear of exposure.",
            conflict="Desire vs self-image.",
            stakes="Isolation vs transformation.",
            change="Replaces pride with intimacy.",
        ),
    )
    ident.to_yaml(proj_dir / "story_identity.yaml")
    return proj_dir


def test_cli_genre_pack_list(capsys):
    rc = main(["genre", "pack", "list"])
    assert rc is None or rc == 0
    captured = capsys.readouterr()
    assert "erotic_fiction" in captured.out


def test_cli_genre_pack_list_json(capsys):
    rc = main(["genre", "pack", "list", "--json"])
    assert rc is None or rc == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert any(p["pack_id"] == "erotic_fiction" for p in data)


def test_cli_genre_pack_inspect(capsys):
    rc = main(["genre", "pack", "inspect", "erotic_fiction", "--json"])
    assert rc is None or rc == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["pack_id"] == "erotic_fiction"
    assert len(data["subgenre_profiles"]) == 3


def test_cli_genre_recommend(capsys):
    rc = main(["genre", "recommend", "--premise", "A story of intense erotic desire and psychological facades", "--json"])
    assert rc is None or rc == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["recommended_pack_id"] == "erotic_fiction"
    assert data["recommended_profile_id"] in ("erotic_psychological_drama", "erotic_romance", "erotic_horror")


def test_cli_genre_recommend_and_accept(tmp_path, capsys):
    proj_dir = _setup_project(tmp_path)
    # Recommend
    rc = main(["genre", "recommend", "--project", str(proj_dir), "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    rec_data = json.loads(captured.out)
    rec_id = rec_data["recommendation_id"]

    # Accept
    rc2 = main(["genre", "recommendation", "accept", rec_id, "--project", str(proj_dir), "--confirm"])
    assert rc2 == 0
    capsys.readouterr()  # Clear stdout

    # Profile show
    rc3 = main(["genre", "profile", "show", "--project", str(proj_dir), "--json"])
    assert rc3 == 0
    captured3 = capsys.readouterr()
    prof_data = json.loads(captured3.out)
    assert prof_data["primary_pack_id"] == "erotic_fiction"
