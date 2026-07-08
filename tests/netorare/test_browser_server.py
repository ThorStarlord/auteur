"""Comprehensive tests for netorare HTTP server and browser API endpoints."""

import json
import pytest
import tempfile
import threading
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from auteur.netorare.session import SessionManager, SessionError
from auteur.netorare.browser.server import (
    NetorareServer, NetorareRequestHandler, ServerError
)


class TestServerInitialization:
    """Tests for server initialization and configuration."""

    def test_server_init_requires_session_file(self, tmp_path):
        """Server requires a valid session file to initialize."""
        with pytest.raises(ServerError):
            NetorareServer(
                session_file=tmp_path / "nonexistent.json",
                port=8001
            )

    def test_server_init_loads_existing_session(self, tmp_path):
        """Server loads and validates existing session file."""
        # Create session
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")

        # Initialize server
        session_file = project_path / "netorare" / "session.json"
        server = NetorareServer(session_file=session_file, port=8001)

        assert server.session_manager is not None
        assert server.session_manager.get_state()["core_id"] == "classic_humiliation"

    def test_server_init_accepts_optional_html_content(self, tmp_path):
        """Server accepts optional HTML content for serving."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "horror")
        session_file = project_path / "netorare" / "session.json"

        html = "<html><body>Test</body></html>"
        server = NetorareServer(
            session_file=session_file,
            port=8001,
            html_content=html
        )

        assert server.html_content == html

    def test_server_init_sets_port(self, tmp_path):
        """Server stores the configured port."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "mystery")
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8765)

        assert server.port == 8765

    def test_server_default_port_is_8000(self, tmp_path):
        """Server defaults to port 8000 if not specified."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file)

        assert server.port == 8000


class TestServerEndpoints:
    """Tests for HTTP endpoints via actual server."""

    def _start_server_background(self, server, timeout=5):
        """Start server in background thread and wait for it to be ready."""
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()
        # Give server time to start
        time.sleep(0.5)
        return thread

    def test_get_session_endpoint(self, tmp_path):
        """GET /session returns current session state."""
        # Setup
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {"want": "want-dignity"})
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        # Start server
        server = NetorareServer(session_file=session_file, port=8001)
        thread = self._start_server_background(server)

        try:
            # Make request
            response = urlopen("http://localhost:8001/session")
            data = json.loads(response.read().decode())

            # Verify
            assert data["core_id"] == "classic_humiliation"
            # JSON converts integer keys to strings
            assert "4" in data["choices"]
            assert data["choices"]["4"]["want"] == "want-dignity"
            assert response.status == 200
        finally:
            server.stop()

    def test_get_session_endpoint_cors_headers(self, tmp_path):
        """GET /session includes CORS headers."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "horror")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8002)
        thread = self._start_server_background(server)

        try:
            response = urlopen("http://localhost:8002/session")
            assert response.headers.get("Access-Control-Allow-Origin") == "*"
        finally:
            server.stop()

    def test_post_session_update_endpoint(self, tmp_path):
        """POST /session/update updates session choices."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8003)
        thread = self._start_server_background(server)

        try:
            # Send update
            update_data = {
                "phase": 5,
                "choices": {"theme": "theme-1", "mood": "dark"}
            }
            body = json.dumps(update_data).encode()

            req = Request(
                "http://localhost:8003/session/update",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            response = urlopen(req)
            data = json.loads(response.read().decode())

            # Verify response (JSON converts int keys to strings)
            assert data["status"] == "updated"
            assert data["session"]["choices"]["5"]["theme"] == "theme-1"
            assert data["session"]["choices"]["5"]["mood"] == "dark"

            # Verify persisted to disk (session manager uses int keys)
            reloaded = SessionManager.load_session(session_file)
            state = reloaded.get_state()
            assert state["choices"][5]["theme"] == "theme-1"
        finally:
            server.stop()

    def test_post_session_update_merges_choices(self, tmp_path):
        """POST /session/update merges with existing choices."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "mystery")
        session.update_choices(4, {"want": "want-truth"})
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8004)
        thread = self._start_server_background(server)

        try:
            # Send update with additional field
            update_data = {
                "phase": 4,
                "choices": {"change": "change-participant"}
            }
            body = json.dumps(update_data).encode()

            req = Request(
                "http://localhost:8004/session/update",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            response = urlopen(req)
            data = json.loads(response.read().decode())

            # Both should be present (JSON converts int keys to strings)
            choices = data["session"]["choices"]["4"]
            assert choices["want"] == "want-truth"  # Original
            assert choices["change"] == "change-participant"  # New
        finally:
            server.stop()

    def test_post_session_complete_endpoint(self, tmp_path):
        """POST /session/complete marks session as complete."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8005)
        thread = self._start_server_background(server)

        try:
            # Send complete request
            body = json.dumps({}).encode()

            req = Request(
                "http://localhost:8005/session/complete",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            response = urlopen(req)
            data = json.loads(response.read().decode())

            # Verify response
            assert data["status"] == "completed"
            assert data["session"]["status"] == "complete"

            # Verify persisted to disk
            reloaded = SessionManager.load_session(session_file)
            assert reloaded.is_complete()
        finally:
            server.stop()

    def test_get_session_validate_endpoint(self, tmp_path):
        """GET /session/validate returns validation results."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        # Add valid choices
        session.update_choices(4, {
            "want": "want-dignity",
            "resistance": "resistance-inadequacy",
            "change": "change-accept"
        })
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8006)
        thread = self._start_server_background(server)

        try:
            response = urlopen("http://localhost:8006/session/validate")
            data = json.loads(response.read().decode())

            # Verify response structure
            assert "is_valid" in data
            assert "errors" in data
            assert "warnings" in data
            assert "session_id" in data
        finally:
            server.stop()

    def test_get_root_serves_html(self, tmp_path):
        """GET / serves HTML content."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "horror")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        html_content = "<html><body>Custom HTML</body></html>"
        server = NetorareServer(
            session_file=session_file,
            port=8007,
            html_content=html_content
        )
        thread = self._start_server_background(server)

        try:
            response = urlopen("http://localhost:8007/")
            content = response.read().decode()

            assert "Custom HTML" in content
            assert response.headers.get("Content-Type") == "text/html"
        finally:
            server.stop()

    def test_get_root_fallback_html(self, tmp_path):
        """GET / serves fallback HTML if none provided."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "mystery")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8008)
        thread = self._start_server_background(server)

        try:
            response = urlopen("http://localhost:8008/")
            content = response.read().decode()

            # Should contain minimal fallback
            assert "Netorare" in content or "Loading" in content
        finally:
            server.stop()

    def test_options_request_cors_preflight(self, tmp_path):
        """OPTIONS request returns CORS headers for preflight."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8009)
        thread = self._start_server_background(server)

        try:
            req = Request(
                "http://localhost:8009/session",
                method="OPTIONS"
            )
            response = urlopen(req)

            assert response.status == 200
            assert response.headers.get("Access-Control-Allow-Origin") == "*"
            assert "POST" in response.headers.get("Access-Control-Allow-Methods", "")
        finally:
            server.stop()


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def _start_server_background(self, server, timeout=5):
        """Start server in background thread."""
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()
        time.sleep(0.5)
        return thread

    def test_malformed_json_in_update_request(self, tmp_path):
        """Malformed JSON in POST body returns 400."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8010)
        thread = self._start_server_background(server)

        try:
            req = Request(
                "http://localhost:8010/session/update",
                data=b"{invalid json",
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with pytest.raises(HTTPError) as exc_info:
                urlopen(req)

            assert exc_info.value.code == 400
        finally:
            server.stop()

    def test_missing_required_field_in_update(self, tmp_path):
        """Missing required field in update request returns 400."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "horror")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8011)
        thread = self._start_server_background(server)

        try:
            # Missing "choices" field
            req = Request(
                "http://localhost:8011/session/update",
                data=json.dumps({"phase": 4}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with pytest.raises(HTTPError) as exc_info:
                urlopen(req)

            assert exc_info.value.code == 400
        finally:
            server.stop()

    def test_invalid_field_type_in_update(self, tmp_path):
        """Invalid field types in update request returns 400."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "mystery")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8012)
        thread = self._start_server_background(server)

        try:
            # phase should be int, not string
            req = Request(
                "http://localhost:8012/session/update",
                data=json.dumps({
                    "phase": "four",  # Wrong type
                    "choices": {"want": "want-dignity"}
                }).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with pytest.raises(HTTPError) as exc_info:
                urlopen(req)

            assert exc_info.value.code == 400
        finally:
            server.stop()

    def test_nonexistent_endpoint_returns_404(self, tmp_path):
        """Request to nonexistent endpoint returns 404."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8013)
        thread = self._start_server_background(server)

        try:
            with pytest.raises(HTTPError) as exc_info:
                urlopen("http://localhost:8013/nonexistent")

            assert exc_info.value.code == 404
        finally:
            server.stop()

    def test_empty_body_in_complete_request(self, tmp_path):
        """Empty body in complete request is accepted."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "horror")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8014)
        thread = self._start_server_background(server)

        try:
            req = Request(
                "http://localhost:8014/session/complete",
                data=b"",
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            response = urlopen(req)
            data = json.loads(response.read().decode())

            # Should succeed with empty body
            assert data["status"] == "completed"
        finally:
            server.stop()


class TestServerIntegration:
    """Integration tests for complete workflows."""

    def _start_server_background(self, server):
        """Start server in background thread."""
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()
        time.sleep(0.5)
        return thread

    def test_full_session_workflow_via_api(self, tmp_path):
        """Complete workflow: create → read → update → validate → complete."""
        # Setup
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8015)
        thread = self._start_server_background(server)

        try:
            # 1. Read initial state
            response = urlopen("http://localhost:8015/session")
            data = json.loads(response.read().decode())
            assert data["status"] == "incomplete"
            initial_id = data["id"]

            # 2. Update choices
            update_req = Request(
                "http://localhost:8015/session/update",
                data=json.dumps({
                    "phase": 4,
                    "choices": {
                        "want": "want-dignity",
                        "resistance": "resistance-inadequacy",
                        "change": "change-accept"
                    }
                }).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            response = urlopen(update_req)
            data = json.loads(response.read().decode())
            assert data["status"] == "updated"

            # 3. Validate choices
            response = urlopen("http://localhost:8015/session/validate")
            data = json.loads(response.read().decode())
            # Validation result will depend on template rules
            assert "is_valid" in data

            # 4. Complete session
            complete_req = Request(
                "http://localhost:8015/session/complete",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            response = urlopen(complete_req)
            data = json.loads(response.read().decode())
            assert data["status"] == "completed"
            assert data["session"]["status"] == "complete"
            assert data["session"]["id"] == initial_id
        finally:
            server.stop()

    def test_multiple_phases_via_api(self, tmp_path):
        """Update multiple phases through API."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "mystery")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        server = NetorareServer(session_file=session_file, port=8016)
        thread = self._start_server_background(server)

        try:
            # Update phase 4
            req4 = Request(
                "http://localhost:8016/session/update",
                data=json.dumps({
                    "phase": 4,
                    "choices": {"want": "want-truth"}
                }).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urlopen(req4)

            # Update phase 5
            req5 = Request(
                "http://localhost:8016/session/update",
                data=json.dumps({
                    "phase": 5,
                    "choices": {"theme": "theme-1"}
                }).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urlopen(req5)

            # Verify both phases in state (JSON converts int keys to strings)
            response = urlopen("http://localhost:8016/session")
            data = json.loads(response.read().decode())
            assert "4" in data["choices"]
            assert "5" in data["choices"]
            assert data["choices"]["4"]["want"] == "want-truth"
            assert data["choices"]["5"]["theme"] == "theme-1"
        finally:
            server.stop()
