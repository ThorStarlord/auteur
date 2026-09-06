from auteur.cli import main, parse_args


def test_design_pack_commands_parse_and_run(capsys):
    args = parse_args(["design", "pack", "compose", "--pack", "superhero", "--pack", "anti_hero"])
    assert args.command == "design"
    assert args.design_pack_command == "compose"
    assert main(["design", "pack", "list", "--json"]) == 0
    assert '"pack_id": "superhero"' in capsys.readouterr().out


def test_tutor_command_is_derived_and_does_not_require_identity(capsys):
    assert main(["design", "tutor", "recommend", "--pack", "superhero", "--decision", "power origin"]) == 0
    output = capsys.readouterr().out
    assert "DERIVED / NOT CANON" in output
    assert "Recommended:" in output


def test_story_discovery_accepts_optional_design_pack_priors():
    args = parse_args([
        "story-discovery", "run", "a premise", "--design-pack", "superhero",
        "--design-pack", "hard_determinism",
    ])
    assert args.design_packs == ["superhero", "hard_determinism"]
