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
    (tmp_path / "blueprint.yaml").write_text(
        yaml.safe_dump({"structure": {"estimated_chapters": 30}}, sort_keys=False),
        encoding="utf-8",
    )
    return tmp_path


def _snapshot(project: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(project)): path.read_bytes()
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }


def _post(base: str, server: GuidedAuthorWorkspaceServer, action: str, data: dict):
    request = Request(
        f"{base}/api/actions/{action}",
        data=json.dumps(data).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Origin": base,
            "X-Auteur-CSRF": server.csrf_token,
        },
    )
    return urlopen(request, timeout=5)


def test_workspace_payload_is_projection_until_explicit_action(tmp_path: Path):
    project = _project(tmp_path)
    before = _snapshot(project)
    payload = build_workspace_payload(project, csrf_token="token")
    assert payload["authority_status"] == "GUIDED WORKSPACE / EXPLICIT ACTIONS"
    assert payload["mutates_story_without_explicit_action"] is False
    assert payload["supports_explicit_actions"] is True
    assert payload["csrf_token"] == "token"
    assert payload["primary_attention"]["artifact_id"] == "workspace_proposal"
    assert payload["primary_detail"]["options"][0]["id"] == "widen"
    assert _snapshot(project) == before


def test_root_parser_routes_workspace(tmp_path: Path):
    args = parse_args(["workspace", "--project", str(tmp_path), "--port", "0"])
    assert args.project == tmp_path
    assert args.port == 0


def test_workspace_is_loopback_and_rejects_untrusted_post(tmp_path: Path):
    project = _project(tmp_path)
    before = _snapshot(project)
    server = GuidedAuthorWorkspaceServer(project, port=0)
    assert server.host == "127.0.0.1"
    server.start_in_thread()
    base = f"http://127.0.0.1:{server.port}"
    try:
        with urlopen(f"{base}/health", timeout=5) as response:
            health = json.loads(response.read().decode("utf-8"))
        assert health["supports_explicit_actions"] is True

        with urlopen(f"{base}/api/workspace", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["csrf_token"] == server.csrf_token

        request = Request(
            f"{base}/api/actions/proposal-select",
            data=b"{}",
            method="POST",
            headers={"Content-Type": "application/json", "Origin": base},
        )
        with pytest.raises(HTTPError) as missing_csrf:
            urlopen(request, timeout=5)
        assert missing_csrf.value.code == 403

        request = Request(
            f"{base}/api/actions/proposal-select",
            data=b"{}",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Origin": "https://attacker.invalid",
                "X-Auteur-CSRF": server.csrf_token,
            },
        )
        with pytest.raises(HTTPError) as bad_origin:
            urlopen(request, timeout=5)
        assert bad_origin.value.code == 403
    finally:
        server.stop()
    assert _snapshot(project) == before


def test_workspace_selects_proposal_through_shared_service_without_blueprint_mutation(tmp_path: Path):
    project = _project(tmp_path)
    blueprint_before = (project / "blueprint.yaml").read_bytes()
    server = GuidedAuthorWorkspaceServer(project, port=0)
    server.start_in_thread()
    base = f"http://127.0.0.1:{server.port}"
    try:
        with _post(
            base,
            server,
            "proposal-select",
            {
                "proposal": ".auteur/structure/proposals/workspace_proposal.yaml",
                "option": "widen",
                "author": "Workspace Test",
            },
        ) as response:
            body = json.loads(response.read().decode("utf-8"))
        assert body["result"]["status"] == "ok"
        assert body["result"]["mutates_story"] is False
        assert body["result"]["data"]["ready_for_revision_plan"] is True
        assert (project / "blueprint.yaml").read_bytes() == blueprint_before
        assert body["workspace"]["primary_attention"]["state"] == "selected"
    finally:
        server.stop()


def test_workspace_requires_separate_confirmation_for_authority_action(tmp_path: Path):
    project = _project(tmp_path)
    before = _snapshot(project)
    server = GuidedAuthorWorkspaceServer(project, port=0)
    server.start_in_thread()
    base = f"http://127.0.0.1:{server.port}"
    try:
        request = Request(
            f"{base}/api/actions/revision-apply",
            data=json.dumps({"plan_id": "does-not-matter", "confirmed": False}).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Origin": base,
                "X-Auteur-CSRF": server.csrf_token,
            },
        )
        with pytest.raises(HTTPError) as blocked:
            urlopen(request, timeout=5)
        assert blocked.value.code == 409
        body = json.loads(blocked.value.read().decode("utf-8"))
        assert body["result"]["error_code"] == "confirmation_required"
        assert body["result"]["mutates_story"] is False
    finally:
        server.stop()
    assert _snapshot(project) == before


def test_workspace_confines_proposal_paths(tmp_path: Path):
    project = _project(tmp_path)
    outside = tmp_path.parent / "outside-proposal.yaml"
    outside.write_text("proposal_id: outside\n", encoding="utf-8")
    server = GuidedAuthorWorkspaceServer(project, port=0)
    server.start_in_thread()
    base = f"http://127.0.0.1:{server.port}"
    try:
        request = Request(
            f"{base}/api/actions/proposal-select",
            data=json.dumps({"proposal": str(outside), "option": "x"}).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Origin": base,
                "X-Auteur-CSRF": server.csrf_token,
            },
        )
        with pytest.raises(HTTPError) as blocked:
            urlopen(request, timeout=5)
        assert blocked.value.code == 409
        body = json.loads(blocked.value.read().decode("utf-8"))
        assert "inside the selected project" in body["result"]["message"]
    finally:
        server.stop()
