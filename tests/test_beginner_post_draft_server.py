import json
import threading
from http.client import HTTPConnection
from pathlib import Path

from auteur.beginner.server import create_server


def test_review_endpoint_returns_derived_projection(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")
    server = create_server(tmp_path)
    server.server_bind()
    server.server_activate()
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    try:
        host, port = server.server_address
        connection = HTTPConnection(host, port)
        connection.request("GET", "/api/beginner/chapters/1/review")
        response = connection.getresponse()
        body = json.loads(response.read())
    finally:
        server.server_close()
        thread.join(timeout=2)

    assert response.status == 200
    assert body["chapter_index"] == 1
    assert body["production_status"] == "candidate_draft"


def test_unknown_api_route_is_not_silently_handled(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    server.server_bind()
    server.server_activate()
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    try:
        host, port = server.server_address
        connection = HTTPConnection(host, port)
        connection.request("GET", "/api/beginner/nope")
        response = connection.getresponse()
        response.read()
    finally:
        server.server_close()
        thread.join(timeout=2)
    assert response.status == 404


def test_plan_endpoint_exposes_contextual_next_chapter_plan(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    (chapter / "final.md").write_text("accepted", encoding="utf-8")
    server = create_server(tmp_path)
    server.server_bind()
    server.server_activate()
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    try:
        host, port = server.server_address
        connection = HTTPConnection(host, port)
        connection.request("GET", "/api/beginner/chapters/2/plan")
        response = connection.getresponse()
        body = json.loads(response.read())
    finally:
        server.server_close()
        thread.join(timeout=2)

    assert response.status == 200
    assert body["plan"]["chapter_index"] == 2
    assert body["plan"]["context"]["prior_accepted_chapters"] == [1]
