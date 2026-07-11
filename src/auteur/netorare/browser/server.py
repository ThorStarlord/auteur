"""Lightweight HTTP server for netorare browser UI using Python stdlib only.

Serves HTML UI to browser and provides JSON API endpoints for session state
management and validation. No external dependencies beyond stdlib.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs

from auteur.netorare.session import SessionManager, SessionError
from auteur.netorare.validation import validate_choices
from auteur.netorare.core_templates import (
    HumiliationTemplate, HorrorTemplate, MysteryTemplate
)


logger = logging.getLogger(__name__)


class ServerError(Exception):
    """Raised when server operations fail."""
    pass


class NetorareRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for netorare server.

    Manages:
    - Static HTML serving
    - JSON API endpoints for session state
    - CORS headers for browser communication
    - Error handling for malformed requests
    """

    # Class-level reference to session manager (set by server before request handling)
    session_manager: Optional[SessionManager] = None
    html_content: Optional[str] = None

    def log_message(self, format, *args):
        """Override to use project logger instead of default stderr."""
        logger.info(format % args)

    def send_json_response(self, data: Dict[str, Any], status_code: int = 200) -> None:
        """Send a JSON response with appropriate headers.

        Args:
            data: Dict to serialize as JSON
            status_code: HTTP status code (default 200)
        """
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        response_json = json.dumps(data)
        self.wfile.write(response_json.encode())

    def send_error_response(self, message: str, status_code: int = 400) -> None:
        """Send a JSON error response.

        Args:
            message: Error message
            status_code: HTTP status code (default 400)
        """
        self.send_json_response({"error": message}, status_code=status_code)

    def send_html_response(self, content: str) -> None:
        """Send HTML content response.

        Args:
            content: HTML content to send
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content.encode())

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        try:
            if path == "/":
                self._handle_root()
            elif path == "/session":
                self._handle_get_session()
            elif path == "/session/validate":
                self._handle_validate_session()
            else:
                self.send_error_response("Not found", status_code=404)
        except Exception as e:
            logger.exception(f"Error handling GET {path}")
            self.send_error_response(f"Internal server error: {str(e)}", status_code=500)

    def do_POST(self) -> None:
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            if path == "/session/update":
                self._handle_update_session(body)
            elif path == "/session/complete":
                self._handle_complete_session(body)
            else:
                self.send_error_response("Not found", status_code=404)
        except json.JSONDecodeError as e:
            self.send_error_response(f"Invalid JSON: {str(e)}", status_code=400)
        except Exception as e:
            logger.exception(f"Error handling POST {path}")
            self.send_error_response(f"Internal server error: {str(e)}", status_code=500)

    def _handle_root(self) -> None:
        """Serve root HTML index."""
        if self.html_content:
            self.send_html_response(self.html_content)
        else:
            # Minimal fallback HTML
            fallback_html = """
            <html>
            <head><title>Netorare Browser</title></head>
            <body><h1>Netorare Browser</h1><p>Loading...</p></body>
            </html>
            """
            self.send_html_response(fallback_html)

    def _handle_get_session(self) -> None:
        """Handle GET /session - return current session state."""
        if not self.session_manager:
            self.send_error_response("Session manager not initialized", status_code=500)
            return

        try:
            state = self.session_manager.get_state()
            self.send_json_response(state)
        except SessionError as e:
            self.send_error_response(str(e), status_code=400)

    def _handle_update_session(self, body: bytes) -> None:
        """Handle POST /session/update - update session choices.

        Expected JSON body:
        {
            "phase": 4,
            "choices": {"want": "want-dignity", "change": "change-accept"}
        }

        Args:
            body: Raw request body bytes
        """
        if not self.session_manager:
            self.send_error_response("Session manager not initialized", status_code=500)
            return

        try:
            data = json.loads(body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self.send_error_response(f"Invalid JSON: {str(e)}", status_code=400)
            return

        try:
            # Validate required fields
            if "phase" not in data or "choices" not in data:
                self.send_error_response(
                    "Missing required fields: phase, choices",
                    status_code=400
                )
                return

            phase = data["phase"]
            choices = data["choices"]

            # Validate types
            if not isinstance(phase, int) or not isinstance(choices, dict):
                self.send_error_response(
                    "Invalid field types: phase must be int, choices must be dict",
                    status_code=400
                )
                return

            # Update session
            self.session_manager.update_choices(phase, choices)
            self.session_manager.write_to_file()

            # Return updated state
            state = self.session_manager.get_state()
            self.send_json_response({
                "status": "updated",
                "session": state
            })
        except SessionError as e:
            self.send_error_response(str(e), status_code=400)

    def _handle_complete_session(self, body: bytes) -> None:
        """Handle POST /session/complete - mark session as complete.

        Expected JSON body: {} (empty or optional metadata)

        Args:
            body: Raw request body bytes
        """
        if not self.session_manager:
            self.send_error_response("Session manager not initialized", status_code=500)
            return

        try:
            # Body can be empty, but if provided should be valid JSON
            if body:
                try:
                    data = json.loads(body.decode())
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    self.send_error_response(f"Invalid JSON: {str(e)}", status_code=400)
                    return

            # Mark complete and persist
            self.session_manager.mark_complete()
            self.session_manager.write_to_file()

            # Return updated state
            state = self.session_manager.get_state()
            self.send_json_response({
                "status": "completed",
                "session": state
            })
        except SessionError as e:
            self.send_error_response(str(e), status_code=400)

    def _handle_validate_session(self) -> None:
        """Handle GET /session/validate - validate current choices.

        Returns validation results against the session's core template rules.
        """
        if not self.session_manager:
            self.send_error_response("Session manager not initialized", status_code=500)
            return

        try:
            state = self.session_manager.get_state()
            core_id = state.get("core_id")
            choices = state.get("choices", {})

            # Load appropriate template
            if core_id == "classic_humiliation":
                template = HumiliationTemplate()
            elif core_id == "horror":
                template = HorrorTemplate()
            elif core_id == "mystery":
                template = MysteryTemplate()
            else:
                self.send_error_response(f"Unknown core_id: {core_id}", status_code=400)
                return

            # Validate
            is_valid, errors, warnings = validate_choices(template, choices)

            self.send_json_response({
                "is_valid": is_valid,
                "errors": errors,
                "warnings": warnings,
                "session_id": state.get("id")
            })
        except Exception as e:
            logger.exception("Validation error")
            self.send_error_response(str(e), status_code=400)


class NetorareServer:
    """Lightweight HTTP server for netorare browser UI.

    Manages:
    - Server startup and shutdown
    - Session state persistence
    - HTML content serving
    - Request routing through NetorareRequestHandler

    Typical usage:
        server = NetorareServer(
            session_file=Path("project/netorare/session.json"),
            port=8000,
            html_content=html_str
        )
        server.start()  # Blocking
    """

    def __init__(
        self,
        session_file: Path,
        port: int = 8000,
        html_content: Optional[str] = None
    ):
        """Initialize the netorare server.

        Args:
            session_file: Path to session.json file
            port: Port to bind to (default 8000)
            html_content: HTML content to serve (optional fallback)

        Raises:
            ServerError: If session file doesn't exist
        """
        self.session_file = Path(session_file)
        self.port = port
        self.html_content = html_content
        self.httpd: Optional[HTTPServer] = None

        # Validate session file exists
        if not self.session_file.exists():
            raise ServerError(f"Session file not found: {self.session_file}")

        # Load session
        try:
            self.session_manager = SessionManager.load_session(self.session_file)
        except SessionError as e:
            raise ServerError(f"Failed to load session: {e}")

    def start(self) -> None:
        """Start the HTTP server (blocking).

        Serves on localhost:port until interrupted or stopped.
        """
        try:
            # Create server
            self.httpd = HTTPServer(
                ("localhost", self.port),
                NetorareRequestHandler
            )

            # Share session manager with request handler
            NetorareRequestHandler.session_manager = self.session_manager
            NetorareRequestHandler.html_content = self.html_content

            logger.info(f"Starting netorare server on http://localhost:{self.port}")

            # Serve (blocking)
            self.httpd.serve_forever()
        except OSError as e:
            raise ServerError(f"Failed to start server on port {self.port}: {e}")
        except KeyboardInterrupt:
            logger.info("Server interrupted")
        finally:
            if self.httpd:
                self.httpd.server_close()
                self.httpd = None

    def stop(self) -> None:
        """Stop the HTTP server."""
        httpd = self.httpd
        if httpd:
            httpd.shutdown()
            httpd.server_close()
            self.httpd = None
            logger.info("Server stopped")

    def shutdown(self) -> None:
        """Alias for stop() for compatibility."""
        self.stop()
