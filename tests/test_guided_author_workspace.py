from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
import yaml

from auteur.cli import parse_args
from auteur.structure.proposal_models import ProposalOption, StructureProposal
from auteur.ui.workspace import GuidedAuthorWorkspaceServer, build_workspace_payload


def _project(tmp_path: Path) -> Path:
    proposals = tmp_path / ".auteur" / "structure" / "proposals"
    proposals.mkdir(parents=True)
    proposal = StructureProposal(
        proposal_id="workspace_proposal",
        type="repair",
        source_rule="workspace_fixture",
        source_domain="structure",
        summary="Choose whether to widen the story runway.",
        options=[
            ProposalOption(
                id="widen",
                summary="Give the middle more room.",
                tradeoffs="More escalation space, less compression.",
                data={"structure": {"estimated_chapters": 42}},
            )
        ],
    )
    (proposals / "workspace_proposal.yaml").write_text(
        yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    return tmp_path


def _snapshot(project: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(project)): path.read_bytes()
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }


def test_workspace_payload_is_read_only_and_reuses_author_attention(tmp_path: Path):
    project = _project(tmp_path)
    before = _snapshot(project)

    payload = build_workspace_payload(project)

    assert payload["authority_status"] == "DERIVED WORKSPACE / READ ONLY"
    assert payload["mutates_story"] is False
    assert payload["primary_attention"]["artifact_id"] == "workspace_proposal"
    assert payload["primary_attention"]["state"] == "unselected"
    assert payload["primary_attention"]["authority_status"] == "NONCANONICAL PROPOSAL / NOT APPLIED"
    assert "structure proposal inspect" in payload["primary_attention"]["next_command"]
    assert payload["workflow_stages"] == [
        "Tutor guidance",
        "Proposal review",
        "Revision plan",
        "Change preview",
        "Explicit authority action",
        "Reassessment",
    ]
    assert _snapshot(project) == before


def test_root_parser_routes_workspace_without_expanding_legacy_parser(tmp_path: Path):
    args = parse_args(["workspace", "--project", str(tmp_path), "--port", "0"])
    assert args.project == tmp_path
    assert args.port == 0


def test_workspace_server_is_loopback_get_only_and_does_not_mutate_project(tmp_path: Path):
    project = _project(tmp_path)
    before = _snapshot(project)
    server = GuidedAuthorWorkspaceServer(project, port=0)
    assert server.host == "127.0.0.1"
    server.start_in_thread()
    base = f"http://127.0.0.1:{server.port}"
    try:
        with urlopen(f"{base}/health", timeout=5) as response:
            health = json.loads(response.read().decode("utf-8"))
        assert health == {
            "status": "ok",
            "authority_status": "DERIVED WORKSPACE / READ ONLY",
            "mutates_story": False,
        }

        with urlopen(f"{base}/api/workspace", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["primary_attention"]["artifact_id"] == "workspace_proposal"
        assert payload["mutates_story"] is False

        with urlopen(f"{base}/", timeout=5) as response:
            html = response.read().decode("utf-8")
        assert "Your story, one decision at a time." in html
        assert "What needs your attention" in html
        assert "It never changes the story by itself." in html

        request = Request(f"{base}/api/workspace", data=b"{}", method="POST")
        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=5)
        assert error.value.code == 405
        assert "read-only" in error.value.read().decode("utf-8")
    finally:
        server.stop()

    assert _snapshot(project) == before
