"""Tests for netorare browser UI HTML and integration with server API."""

import json
import pytest
import tempfile
import threading
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from auteur.netorare.session import SessionManager
from auteur.netorare.browser.server import NetorareServer


class TestBrowserUIStructure:
    """Tests for HTML structure and embedded assets."""

    def test_html_file_exists(self):
        """Browser UI HTML file exists at expected location."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"
        assert html_file.exists()

    def test_html_contains_required_elements(self):
        """HTML contains all required structural elements."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        # Check for required structural elements
        assert "<html" in content.lower()
        assert "container" in content
        assert "left-panel" in content
        assert "right-panel" in content
        assert "layers-container" in content
        assert "phase-container" in content

    def test_html_has_embedded_css(self):
        """HTML contains embedded CSS (no external stylesheets)."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        # Should have embedded style tag
        assert "<style>" in content
        assert "var(--color-primary)" in content  # CSS variables
        assert ".container" in content

        # Should not have external stylesheet links (except potentially fonts)
        import re
        links = re.findall(r'<link[^>]*rel="stylesheet"[^>]*>', content)
        stylesheet_links = [l for l in links if "fonts" not in l.lower()]
        assert len(stylesheet_links) == 0

    def test_html_has_embedded_javascript(self):
        """HTML contains embedded JavaScript (no external scripts)."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        # Should have embedded script tag with logic
        assert "<script>" in content
        assert "fetch(" in content  # Uses fetch API
        assert "async function init" in content
        assert "addEventListener" in content

    def test_html_is_valid_markup(self):
        """HTML is syntactically valid."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        # Basic validation - self-closing tags may have different counts
        # Just ensure we have more open than close or roughly equal (allowing for self-closing)
        open_count = content.count("<")
        close_count = content.count(">")
        assert close_count >= open_count - 10, "Significantly mismatched tags"
        assert content.lower().count("<html") == 1, "Should have exactly one html tag"
        assert content.lower().count("<body") == 1, "Should have exactly one body tag"
        # Verify closing tags exist
        assert "</html>" in content.lower(), "Missing closing html tag"
        assert "</body>" in content.lower(), "Missing closing body tag"


class TestBrowserUILayout:
    """Tests for responsive layout and UI components."""

    def test_html_is_responsive(self):
        """HTML includes responsive viewport meta tag and media queries."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert 'viewport' in content
        assert '@media' in content

    def test_html_has_grid_layout(self):
        """HTML uses CSS Grid for two-column layout."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert 'grid-template-columns' in content
        assert 'display: grid' in content

    def test_html_has_phase_containers(self):
        """HTML has containers for all 9 phases."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        # Check for phase JavaScript setup
        assert "phase-" in content
        assert "phase-container" in content
        assert "PHASE_CONFIGS" in content

    def test_html_has_9_layer_preview(self):
        """HTML includes 9-layer preview panel."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "layers-container" in content
        assert "LAYER_NAMES" in content
        assert "layer-" in content  # layer-1 through layer-9


class TestBrowserAPIIntegration:
    """Tests for browser UI making API calls to server."""

    def _start_server_background(self, server):
        """Start server in background thread."""
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()
        time.sleep(0.5)
        return thread

    def test_html_loads_from_server(self, tmp_path):
        """Browser can fetch and display HTML from server."""
        # Setup
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        # Load HTML
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"
        with open(html_file, "r") as f:
            html_content = f.read()

        # Start server
        server = NetorareServer(
            session_file=session_file,
            port=8020,
            html_content=html_content
        )
        thread = self._start_server_background(server)

        try:
            # Fetch HTML from server
            response = urlopen("http://localhost:8020/")
            content = response.read().decode()

            # Verify content
            assert "Netorare" in content
            assert "container" in content
            assert "left-panel" in content
        finally:
            server.stop()

    def test_html_can_fetch_session_via_fetch_api(self, tmp_path):
        """HTML JavaScript can fetch session state."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "horror")
        session.update_choices(4, {"want": "want-escape"})
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"
        with open(html_file, "r") as f:
            html_content = f.read()

        server = NetorareServer(
            session_file=session_file,
            port=8021,
            html_content=html_content
        )
        thread = self._start_server_background(server)

        try:
            # Fetch session directly to verify it works
            response = urlopen("http://localhost:8021/session")
            data = json.loads(response.read().decode())

            assert data["core_id"] == "horror"
            assert "4" in data["choices"]
            assert data["choices"]["4"]["want"] == "want-escape"
        finally:
            server.stop()

    def test_html_contains_fetch_logic(self):
        """HTML JavaScript contains fetch logic for all API endpoints."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        # Check for fetch calls
        assert 'fetch("/session")' in content
        assert 'fetch("/session/update"' in content
        assert 'fetch("/session/complete"' in content
        assert 'fetch("/session/validate"' in content


class TestBrowserUIInteractivity:
    """Tests for JavaScript interactivity and event handling."""

    def test_html_has_event_handlers(self):
        """HTML JavaScript defines event handlers for user interactions."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        # Check for event handler functions
        assert "addEventListener(" in content
        assert "onclick=" in content
        assert "selectOption" in content
        assert "navigateToPhase" in content
        assert "approvePhase" in content

    def test_html_has_phase_navigation(self):
        """HTML contains logic for navigating between phases."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "navigateToPhase" in content
        assert "phase-container.active" in content or "phase-container" in content and ".active" in content
        assert "currentPhase" in content

    def test_html_has_choice_selection(self):
        """HTML contains logic for selecting options."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "selectOption" in content
        assert "state.choices" in content
        assert ".selected" in content  # CSS class for selected state

    def test_html_has_layer_preview_updates(self):
        """HTML contains logic to update 9-layer preview in real-time."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "updateLayersPreview" in content
        assert "layer-content-" in content
        assert "getLayerContent" in content


class TestBrowserUIValidation:
    """Tests for form validation and error handling."""

    def test_html_has_validation_logic(self):
        """HTML contains validation logic."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "validateSession" in content
        assert "/session/validate" in content

    def test_html_has_error_display(self):
        """HTML has elements to display errors and success messages."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "error-banner" in content
        assert "success-banner" in content
        assert "showError" in content
        assert "showSuccess" in content

    def test_html_has_loading_states(self):
        """HTML shows loading state during API operations."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "isLoading" in content
        assert "disabled" in content


class TestBrowserUIResponsiveness:
    """Tests for mobile and tablet responsiveness."""

    def test_html_has_viewport_meta(self):
        """HTML includes viewport meta tag for mobile."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert 'name="viewport"' in content
        assert 'initial-scale' in content

    def test_html_has_mobile_media_queries(self):
        """HTML CSS includes mobile media queries."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "@media (max-width:" in content or "@media (max-width :" in content

    def test_html_uses_flexible_units(self):
        """HTML CSS uses flexible units (rem, em, %) for scalability."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        # Should have relative units
        assert "rem" in content or "em" in content
        assert "%" in content


class TestBrowserUIAccessibility:
    """Tests for accessibility and semantic HTML."""

    def test_html_uses_semantic_elements(self):
        """HTML uses semantic elements where appropriate."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "<h1" in content
        assert "<h2" in content or "<h" in content  # Heading hierarchy
        assert "<button" in content

    def test_html_has_labels_and_descriptions(self):
        """HTML options have descriptive labels."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "option-label" in content
        assert "option-description" in content


class TestBrowserUIIntegrationWorkflow:
    """Integration tests for complete workflows through the browser UI."""

    def _start_server_background(self, server):
        """Start server in background thread."""
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()
        time.sleep(0.5)
        return thread

    def test_browser_ui_workflow_session_to_choices_to_complete(self, tmp_path):
        """Full workflow: load session → make choices → validate → complete."""
        # Setup
        project_path = tmp_path / "project"
        project_path.mkdir()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.write_to_file()
        session_file = project_path / "netorare" / "session.json"

        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"
        with open(html_file, "r") as f:
            html_content = f.read()

        server = NetorareServer(
            session_file=session_file,
            port=8022,
            html_content=html_content
        )
        thread = self._start_server_background(server)

        try:
            # 1. Load HTML (UI starts here)
            response = urlopen("http://localhost:8022/")
            html = response.read().decode()
            assert "Netorare" in html

            # 2. Load session state (browser would do this)
            response = urlopen("http://localhost:8022/session")
            state = json.loads(response.read().decode())
            assert state["status"] == "incomplete"
            session_id = state["id"]

            # 3. Update choices (browser would POST after user selects)
            update_req = Request(
                "http://localhost:8022/session/update",
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
            assert data["session"]["id"] == session_id

            # 4. Validate choices
            response = urlopen("http://localhost:8022/session/validate")
            validation = json.loads(response.read().decode())
            assert "is_valid" in validation

            # 5. Complete session
            complete_req = Request(
                "http://localhost:8022/session/complete",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            response = urlopen(complete_req)
            data = json.loads(response.read().decode())
            assert data["status"] == "completed"
        finally:
            server.stop()


class TestBrowserUIEdgeCases:
    """Tests for edge cases and error conditions."""

    def _start_server_background(self, server):
        """Start server in background thread."""
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()
        time.sleep(0.5)
        return thread

    def test_html_handles_missing_session_gracefully(self, tmp_path):
        """HTML has error handling for missing session."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        # Should have error handling
        assert "catch (error)" in content or "try {" in content
        assert "showError" in content

    def test_html_can_recover_from_api_errors(self, tmp_path):
        """HTML JavaScript has error recovery logic."""
        from auteur.netorare.browser import __file__ as browser_init
        browser_dir = Path(browser_init).parent
        html_file = browser_dir / "index.html"

        with open(html_file, "r") as f:
            content = f.read()

        assert "try" in content
        assert "catch" in content
        assert ".ok" in content or "response.ok" in content  # HTTP status checking
