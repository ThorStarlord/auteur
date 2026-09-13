"""Guard the root command groups included in the 1.0 CLI promise."""

from auteur.cli_parser import build_parser


STABLE_ROOT_COMMANDS = {
    "status",
    "init",
    "identity",
    "structure",
    "workflow",
    "campaign",
    "decision",
    "review",
    "publish",
}


def test_stable_cli_command_groups_are_registered() -> None:
    parser = build_parser()
    registered = set(parser._subparsers._group_actions[0].choices)

    assert STABLE_ROOT_COMMANDS <= registered
