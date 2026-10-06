from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_f2_prompt_consumer_probe_preserves_context_authority():
    namespace = runpy.run_path(str(ROOT / "scripts" / "f2_context_prompt_probe.py"))
    assert all(namespace["run_probe"]().values())
