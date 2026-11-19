"""The local Studio server accepts a full parallel page load, and a page whose scripts did not all arrive says so."""
import os
import socket

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer


def test_server_queues_a_full_parallel_page_load_while_accept_is_busy(tmp_path):
    # Constructed but not yet serving: every connection must wait in the listen queue, as during a busy accept.
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    sockets, refused = [], 0
    try:
        for _ in range(25):  # a Studio page requests ~20 scripts and styles; browsers open several per host
            client = socket.socket()
            client.settimeout(2)
            try:
                client.connect(("127.0.0.1", server.port))
                sockets.append(client)
            except OSError:
                refused += 1
                client.close()
        assert refused == 0
    finally:
        for client in sockets:
            client.close()
        server._httpd.server_close()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


def test_a_refused_studio_script_is_reported_instead_of_a_silent_half_loaded_canvas(tmp_path, browser):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    page = browser.new_page()
    writes = []
    page.on("request", lambda r: r.method == "POST" and writes.append(r.url))
    try:
        page.route("**/studio_unfolding.js", lambda route: route.abort("connectionrefused"))
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=ferry-story")
        page.wait_for_function("document.querySelector('#status').textContent.includes('did not load completely')")
        assert "Reload" in page.locator("#status").inner_text()
        page.wait_for_timeout(500)
        assert "did not load completely" in page.locator("#status").inner_text()
        assert writes == []  # the canvas is neither opened nor saved
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
