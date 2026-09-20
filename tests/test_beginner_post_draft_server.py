import json
from pathlib import Path
from urllib.request import Request, urlopen

from auteur.beginner.server import BeginnerWorkspaceServer


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
