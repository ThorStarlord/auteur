"""CLI orchestration for the netorare pipeline: session → browser → identity."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

from auteur.netorare.browser.server import NetorareServer, ServerError
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.netorare.session import SessionManager, SessionError
from auteur.netorare.validation import validate_choices

logger = logging.getLogger(__name__)


class NetorareError(Exception):
    """Base error for netorare CLI operations."""
    pass


class NetorareCommand:
    """Orchestrates the complete netorare pipeline.

    Workflow:
    1. Create project directory structure
    2. Create netorare session (SessionManager)
    3. Start browser HTTP server (NetorareServer) in subprocess
    4. Open browser to http://localhost:port/?session=...
    5. Poll session for completion (async wait with timeout)
    6. Read final choices from completed session
    7. Validate choices
    8. Generate story_identity.yaml (IdentityGenerator)
    9. Save story_identity.yaml to project/story_identity.yaml
    10. Clean up browser server subprocess
    11. Display success message with next steps
    """

    def __init__(
        self,
        project_path: Path,
        core_id: str = "classic_humiliation",
        provider: str = "anthropic",
        port: int = 8765,
        timeout: float = 3600.0,  # 1 hour default timeout
        debug: bool = False,
    ):
        """Initialize the netorare command.

        Args:
            project_path: Path to project root
            core_id: Core template ID (classic_humiliation, horror, mystery)
            provider: LLM provider (anthropic, openai)
            port: Port for browser server
            timeout: Timeout in seconds for waiting for completion
            debug: Enable debug logging
        """
        self.project_path = Path(project_path)
        self.core_id = core_id
        self.provider = provider
        self.port = port
        self.timeout = timeout
        self.debug = debug

        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)

        # Paths
        self.netorare_dir = self.project_path / "netorare"
        self.session_file = self.netorare_dir / "session.json"
        self.identity_file = self.project_path / "story_identity.yaml"

        # State
        self.session_manager: Optional[SessionManager] = None
        self.server_process: Optional[subprocess.Popen] = None

    def run(self) -> int:
        """Execute the complete netorare pipeline.

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            # Step 1: Validate project path
            self._validate_project_path()
            logger.debug(f"Project path validated: {self.project_path}")

            # Step 2: Create project directory structure
            self._create_project_structure()
            logger.debug(f"Project structure created")

            # Step 3: Create netorare session
            self._create_session()
            logger.debug(f"Session created: {self.session_file}")

            # Step 4: Start browser server in subprocess
            self._start_browser_server()
            logger.debug(f"Browser server started on port {self.port}")

            # Step 5: Open browser
            self._open_browser()
            logger.debug(f"Browser opened")

            # Step 6: Poll for completion
            self._poll_for_completion()
            logger.debug(f"Session marked complete")

            # Step 7: Read and validate choices
            choices = self._read_and_validate_choices()
            logger.debug(f"Choices validated: {len(choices)} phases")

            # Step 8: Generate story_identity.yaml
            identity = self._generate_identity(choices)
            logger.debug(f"Identity generated")

            # Step 9: Save identity file
            self._save_identity(identity)
            logger.debug(f"Identity saved to {self.identity_file}")

            # Step 10: Clean up
            self._cleanup()
            logger.debug(f"Cleanup complete")

            # Step 11: Display success message
            self._display_success()

            return 0

        except NetorareError as e:
            self._cleanup()
            print(f"Error: {e}", file=sys.stderr)
            logger.exception(f"Netorare pipeline failed: {e}")
            return 1
        except KeyboardInterrupt:
            self._cleanup()
            print("\nNetorare pipeline interrupted", file=sys.stderr)
            return 130
        except Exception as e:
            self._cleanup()
            print(f"Unexpected error: {e}", file=sys.stderr)
            logger.exception(f"Unexpected error in netorare pipeline: {e}")
            return 1

    def _validate_project_path(self) -> None:
        """Validate project path is usable."""
        if not self.project_path.exists():
            self.project_path.mkdir(parents=True, exist_ok=True)

        if not self.project_path.is_dir():
            raise NetorareError(f"Project path must be a directory: {self.project_path}")

    def _create_project_structure(self) -> None:
        """Create project directory structure."""
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.netorare_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories as needed
        (self.project_path / ".auteur").mkdir(parents=True, exist_ok=True)

    def _create_session(self) -> None:
        """Create a new netorare session."""
        if self.session_file.exists():
            raise NetorareError(
                f"Session already exists at {self.session_file}. "
                "Use --force to reinitialize."
            )

        try:
            self.session_manager = SessionManager.create_session(
                self.project_path, self.core_id
            )
            logger.info(f"Created session: {self.session_manager.get_state()['id']}")
        except SessionError as e:
            raise NetorareError(f"Failed to create session: {e}")

    def _start_browser_server(self) -> None:
        """Start the browser server in a subprocess."""
        if not self.session_file.exists():
            raise NetorareError(f"Session file not found: {self.session_file}")

        # Load HTML content for the server
        html_path = Path(__file__).parent / "netorare" / "browser" / "index.html"
        if not html_path.exists():
            logger.warning(f"HTML file not found: {html_path}")
            html_content = None
        else:
            try:
                html_content = html_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"Failed to read HTML file: {e}")
                html_content = None

        # Create a simple wrapper script to run the server
        server_code = self._get_server_runner_code()

        # Start the server process
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "-c", server_code],
                env={
                    **subprocess.os.environ,
                    "NETORARE_SESSION_FILE": str(self.session_file),
                    "NETORARE_PORT": str(self.port),
                    "PYTHONUNBUFFERED": "1",
                },
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Give server time to start
            time.sleep(1.0)

            # Check if process is still running
            if self.server_process.poll() is not None:
                _, stderr = self.server_process.communicate()
                raise NetorareError(f"Server failed to start: {stderr}")

            logger.info(f"Browser server started (PID {self.server_process.pid}) on port {self.port}")
        except Exception as e:
            raise NetorareError(f"Failed to start browser server: {e}")

    def _get_server_runner_code(self) -> str:
        """Get Python code to run the server in a subprocess."""
        return """
import sys
import os
from pathlib import Path
from auteur.netorare.browser.server import NetorareServer

session_file = Path(os.environ["NETORARE_SESSION_FILE"])
port = int(os.environ["NETORARE_PORT"])

try:
    server = NetorareServer(session_file=session_file, port=port)
    server.start()
except KeyboardInterrupt:
    sys.exit(0)
except Exception as e:
    print(f"Server error: {e}", file=sys.stderr)
    sys.exit(1)
"""

    def _open_browser(self) -> None:
        """Open browser to the netorare server."""
        url = f"http://localhost:{self.port}/?session={self.session_manager.get_state()['id']}"

        try:
            # Try to open browser
            success = webbrowser.open(url)
            if success:
                logger.info(f"Opened browser: {url}")
            else:
                logger.warning(f"Could not open browser automatically. Visit: {url}")
                print(f"Please open this URL in your browser: {url}", file=sys.stderr)
        except Exception as e:
            logger.warning(f"Failed to open browser: {e}")
            print(f"Please open this URL in your browser: {url}", file=sys.stderr)

    def _poll_for_completion(self) -> None:
        """Poll session for completion with timeout."""
        if not self.session_manager:
            raise NetorareError("Session manager not initialized")

        start_time = time.time()
        poll_interval = 2.0  # seconds

        logger.info(f"Polling for completion (timeout: {self.timeout}s)...")

        while time.time() - start_time < self.timeout:
            # Reload session state from disk
            try:
                manager = SessionManager.load_session(self.session_file)
                if manager.is_complete():
                    logger.info("Session marked as complete")
                    self.session_manager = manager
                    return
            except SessionError as e:
                logger.debug(f"Error loading session: {e}")

            time.sleep(poll_interval)

        raise NetorareError(
            f"Session did not complete within {self.timeout}s. "
            "User may still be making choices in the browser."
        )

    def _read_and_validate_choices(self) -> dict:
        """Read choices from completed session and validate."""
        if not self.session_manager:
            raise NetorareError("Session manager not initialized")

        choices = self.session_manager.get_choices()

        if not choices:
            raise NetorareError("No choices found in completed session")

        # Validate choices
        try:
            from auteur.netorare.core_templates import (
                HumiliationTemplate, HorrorTemplate, MysteryTemplate
            )

            if self.core_id == "classic_humiliation":
                template = HumiliationTemplate()
            elif self.core_id == "horror":
                template = HorrorTemplate()
            elif self.core_id == "mystery":
                template = MysteryTemplate()
            else:
                raise NetorareError(f"Unknown core_id: {self.core_id}")

            is_valid, errors, warnings = validate_choices(template, choices)

            if warnings:
                print("\nWarnings during validation:", file=sys.stderr)
                for warning in warnings:
                    print(f"  - {warning}", file=sys.stderr)

            if not is_valid:
                error_msg = "; ".join(errors)
                raise NetorareError(f"Choices validation failed: {error_msg}")

            logger.info("Choices validated successfully")
            return choices

        except NetorareError:
            raise
        except Exception as e:
            raise NetorareError(f"Validation error: {e}")

    def _generate_identity(self, choices: dict) -> str:
        """Generate story_identity.yaml content from choices."""
        try:
            identity = IdentityGenerator.from_choices(self.core_id, choices)
            yaml_content = IdentityGenerator.to_yaml(identity)
            logger.info("Identity generated successfully")
            return yaml_content
        except ValueError as e:
            raise NetorareError(f"Failed to generate identity: {e}")
        except Exception as e:
            raise NetorareError(f"Unexpected error generating identity: {e}")

    def _save_identity(self, yaml_content: str) -> None:
        """Save generated identity to story_identity.yaml."""
        try:
            self.identity_file.write_text(yaml_content, encoding="utf-8")
            logger.info(f"Identity saved to {self.identity_file}")
        except Exception as e:
            raise NetorareError(f"Failed to save identity file: {e}")

    def _cleanup(self) -> None:
        """Clean up: stop server subprocess and close resources."""
        if self.server_process:
            try:
                self.server_process.terminate()
                # Give process time to terminate gracefully
                try:
                    self.server_process.wait(timeout=5.0)
                except (subprocess.TimeoutExpired, Exception) as e:
                    if isinstance(e, subprocess.TimeoutExpired):
                        self.server_process.kill()
                    else:
                        raise
                logger.info("Browser server stopped")
            except Exception as e:
                logger.warning(f"Error stopping server: {e}")

    def _display_success(self) -> None:
        """Display success message with next steps."""
        print("\n[OK] Netorare pipeline completed successfully!")
        print(f"\nGenerated files:")
        print(f"  - Session: {self.session_file}")
        print(f"  - Identity: {self.identity_file}")
        print(f"\nNext steps:")
        print(f"  1. Validate identity: auteur identity validate {self.identity_file}")
        print(f"  2. Compile blueprint: auteur identity compile {self.identity_file} --output {self.project_path / 'blueprint.yaml'}")
        print(f"  3. Initialize project: auteur init {self.project_path} --from {self.project_path / 'blueprint.yaml'}")


def handle_netorare_init(
    project_path: Path,
    core_id: str = "classic_humiliation",
    provider: str = "anthropic",
    port: int = 8765,
    timeout: float = 3600.0,
    debug: bool = False,
) -> int:
    """Handle 'auteur netorare init' command.

    Args:
        project_path: Path to project directory
        core_id: Core template ID
        provider: LLM provider
        port: Server port
        timeout: Completion timeout in seconds
        debug: Enable debug logging

    Returns:
        Exit code (0 for success)
    """
    command = NetorareCommand(
        project_path=project_path,
        core_id=core_id,
        provider=provider,
        port=port,
        timeout=timeout,
        debug=debug,
    )
    return command.run()
