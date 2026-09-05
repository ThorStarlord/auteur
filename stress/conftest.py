"""Stress-test conftest: marker registration + opt-in execution.

Stress tests never run in a default ``pytest`` session. They execute only when
``AUTEUR_STRESS=1`` is set in the environment; the optional scale knob is
``AUTEUR_STRESS_SCALE`` (``smoke`` | ``full``, default ``full``).
"""

from __future__ import annotations

import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "stress: heavy offline stress scenario; opt in with AUTEUR_STRESS=1",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if os.environ.get("AUTEUR_STRESS") == "1":
        return
    skip = pytest.mark.skip(
        reason="stress tests are opt-in: set AUTEUR_STRESS=1 to run them"
    )
    for item in items:
        if "stress" in item.keywords:
            item.add_marker(skip)
