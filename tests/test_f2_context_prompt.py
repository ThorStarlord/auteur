from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_f2_prompt_consumer_probe_preserves_context_authority():
    namespace = runpy.run_path(str(ROOT / "scripts" / "f2_context_prompt_probe.py"))
    assert all(namespace["run_probe"]().values())


def test_f2_probe_leaves_the_checkout_untouched():
    bible_path = ROOT / ".auteur" / "f2-prompt-probe-bible.json"
    existed_before = bible_path.exists()
    namespace = runpy.run_path(str(ROOT / "scripts" / "f2_context_prompt_probe.py"))
    assert all(namespace["run_probe"]().values())
    assert bible_path.exists() == existed_before
