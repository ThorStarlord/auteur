import json
from pathlib import Path
from urllib.request import Request, urlopen

from auteur.beginner.server import (
    BeginnerRuntimeDependencies,
    BeginnerWorkspaceServer,
    default_runtime_dependencies,
)
from auteur.llm import LLMResponse


def _json(url: str, *, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def test_server_exposes_review_and_contextual_plan(tmp_path: Path) -> None:
    chapter_one = tmp_path / "chapters" / "01"
    chapter_one.mkdir(parents=True)
    (chapter_one / "draft_v1.md").write_text("candidate", encoding="utf-8")
    (chapter_one / "validation_v1.json").write_text(
        json.dumps({"findings": []}),
        encoding="utf-8",
    )

    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        review = _json(f"{base}/api/beginner/chapters/1/review")
        assert review["source_draft"] == "draft_v1.md"
        assert review["draft_text"] == "candidate"
        assert review["production_status"] == "candidate_draft"

        plan = _json(f"{base}/api/beginner/chapters/2/plan")
        assert plan["plan"]["chapter_index"] == 2
        assert plan["plan"]["continuation"]["current_chapter_index"] == 2
    finally:
        server.stop()
        thread.join(timeout=5)


def test_server_prepares_noncanonical_revision_handoff(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")

    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        result = _json(
            f"{base}/api/beginner/chapters/1/revision-handoff",
            method="POST",
            payload={
                "command_id": "server-revision",
                "decision": "repair continuity",
                "route": "retry",
            },
        )
        assert result["route"] == "retry"
        assert not (chapter / "final.md").exists()
    finally:
        server.stop()
        thread.join(timeout=5)

class _QuickDraftLLM:
    def complete(self, request):
        return LLMResponse(
            text=(
                "Detective Miller watched Vance smile.\n\n"
                "\"You remember me holding the knife,\" Miller said."
            ),
            input_tokens=20,
            output_tokens=25,
        )


def test_server_exposes_two_input_quick_draft_edit_and_discovery(tmp_path: Path) -> None:
    base_dependencies = default_runtime_dependencies()
    dependencies = BeginnerRuntimeDependencies(
        architecture_analyzer=base_dependencies.architecture_analyzer,
        discovery_recommender=base_dependencies.discovery_recommender,
        drafting_client=_QuickDraftLLM(),
    )
    server = BeginnerWorkspaceServer(tmp_path, port=0, dependencies=dependencies)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        created = _json(
            f"{base}/api/beginner/quick-draft",
            method="POST",
            payload={
                "premise": "Detective Miller investigates conflicting memories of one murder.",
                "first_scene": "Miller questions Suspect Vance about the murder.",
            },
        )
        assert created["status"] == "inferred_provisional"
        assert "Miller watched Vance smile" in created["draft_text"]
        session_id = created["session_id"]

        reopened = _json(f"{base}/api/beginner/quick-draft/{session_id}")
        assert reopened["session_id"] == session_id
        assert reopened["draft_text"] == created["draft_text"]

        edited = _json(
            f"{base}/api/beginner/quick-draft/{session_id}/save",
            method="POST",
            payload={
                "draft_text": (
                    "At the abandoned seaside convent, Sister Beatrice tells "
                    "Detective Miller that Vance slept there."
                ),
            },
        )
        assert edited["draft"]["edit_count"] == 1

        discoveries = _json(
            f"{base}/api/beginner/quick-draft/{session_id}/discoveries"
        )
        values = {item["value"] for item in discoveries["discoveries"]}
        assert "Sister Beatrice" in values
        assert any("abandoned seaside convent" in value.lower() for value in values)
    finally:
        server.stop()
        thread.join(timeout=5)


def test_server_reconcile_new_elements_can_route_revision_without_acceptance(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    (chapter / "draft_v1.md").write_text("unexpected draft", encoding="utf-8")

    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        result = _json(
            f"{base}/api/beginner/chapters/1/reconcile-new-elements",
            method="POST",
            payload={
                "command_id": "reconcile-revise",
                "decision": "revise_to_plan",
            },
        )
        assert result["accepted"] is False
        assert result["decision"] == "revise_to_plan"
        assert not (chapter / "final.md").exists()
    finally:
        server.stop()
        thread.join(timeout=5)

def test_server_shape_workspace_retains_only_selected_quick_draft_context(tmp_path: Path) -> None:
    base_dependencies = default_runtime_dependencies()
    dependencies = BeginnerRuntimeDependencies(
        architecture_analyzer=base_dependencies.architecture_analyzer,
        discovery_recommender=base_dependencies.discovery_recommender,
        drafting_client=_QuickDraftLLM(),
    )
    server = BeginnerWorkspaceServer(tmp_path, port=0, dependencies=dependencies)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        created = _json(
            f"{base}/api/beginner/quick-draft",
            method="POST",
            payload={
                "premise": "Detective Miller investigates conflicting memories of one murder.",
                "first_scene": "Miller questions Suspect Vance about the murder.",
            },
        )
        session_id = created["session_id"]
        _json(
            f"{base}/api/beginner/quick-draft/{session_id}/save",
            method="POST",
            payload={
                "draft_text": (
                    "At the abandoned seaside convent, Sister Beatrice tells "
                    "Detective Miller that Vance slept there."
                ),
            },
        )
        discovery_payload = _json(
            f"{base}/api/beginner/quick-draft/{session_id}/discoveries"
        )
        sister = next(
            item
            for item in discovery_payload["discoveries"]
            if item["value"] == "Sister Beatrice"
        )

        workspace = _json(
            f"{base}/api/beginner/workspaces",
            method="POST",
            payload={
                "command_id": "create-from-quick",
                "workspace_id": "workspace-quick",
                "premise": (
                    "Detective Miller investigates conflicting memories of one murder.\n\n"
                    "First scene I want: Miller questions Suspect Vance about the murder.\n\n"
                    "Ideas I discovered while drafting and explicitly want to carry forward:\n"
                    "- Sister Beatrice"
                ),
                "quick_draft_session_id": session_id,
                "quick_draft_discoveries": [sister],
            },
        )

        assert workspace["workspace"]["workspace_id"] == "workspace-quick"
        handoff = (
            tmp_path
            / ".auteur"
            / "beginner"
            / "quick_draft_handoffs"
            / "workspace-quick.yaml"
        )
        assert handoff.is_file()
        text = handoff.read_text(encoding="utf-8")
        assert "canonical: false" in text
        assert "Sister Beatrice" in text
        assert "abandoned seaside convent" not in text
    finally:
        server.stop()
        thread.join(timeout=5)

