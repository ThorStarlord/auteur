# Proposed protected dependency change: Playwright as a dev/test dependency

**Status:** prepared for the human-maintained protected route. Not applied. `pyproject.toml` and `uv.lock` are protected (`FACTORY_RULES.md`); an autonomous builder must not edit or merge them.

## Change

1. `pyproject.toml` — add Playwright to the `dev` extra only (not runtime dependencies):

   ```diff
   -dev = ["pytest>=8.0,<9", "pytest-xdist>=3.0,<4", "ruff>=0.4.0,<1"]
   +dev = ["pytest>=8.0,<9", "pytest-xdist>=3.0,<4", "ruff>=0.4.0,<1", "playwright>=1.64,<2"]
   ```

   Patch: `playwright-dev-dependency.patch` (verified with `git apply --check` against the combined candidate).

2. `uv.lock` — regenerate with `uv lock` after applying step 1. Patch of the regenerated lock: `uv-lock-playwright.patch`.

## Justification

- Two collected test modules import `playwright.sync_api` at module import time: `tests/test_focused_unfolding_browser.py` and `tests/test_studio_semantic_browser.py`. Without the package they error at collection and the validator's unit gate fails.
- Two qualification scripts also import it: `scripts/studio_stage_b_check.py` and `scripts/studio_architecture_e2e.py`.
- Qualified version: Playwright **1.64.0**, the version used by the earlier Studio qualification. `>=1.64,<2` is the owner-specified range and includes it.

## Review points the human must decide

1. **pytest version change in the lock.** The existing `uv.lock` pins `pytest 9.1.1`, which violates the declared `pytest>=8.0,<9`. Regenerating the lock moves it to `pytest 8.4.2`. Either accept 8.4.2 (matches the declared constraint and the validation venv used for the diagnostic) or change the declared constraint. This is a behaviour-relevant change to the test runner; it is not a silent side effect.
2. **Lock scope.** The original lock has no `pytest-xdist` or `ruff` entries, so regeneration adds the full `dev` tree. Confirm this is wanted.
3. **CI browser binaries (protected `.github/*`).** Installing the Python package does not install Chromium. The validation and release workflows run `python -m pip install -e ".[dev]"` only. The Browser tests launch Playwright's managed Chromium unless `CHROMIUM_PATH` is set, so CI needs an explicit step such as `python -m playwright install --with-deps chromium` before the test steps. Without it, the Browser tests will still fail in CI even after this change. This is a separate protected workflow edit.

## Installation and verification

```bash
python -m pip install -e ".[dev]"
python -m playwright install --with-deps chromium
python -c "from playwright.sync_api import sync_playwright; print('playwright ok')"
python -m pytest -q tests/test_focused_unfolding_browser.py tests/test_studio_semantic_browser.py
```

## Evidence this is required

Before this change the validator's unit rung failed with `ModuleNotFoundError: No module named 'playwright'` in the factory interpreter (see the validator logs listed in the evidence PR). The same tests pass with Playwright 1.64.0 installed in an isolated validation environment (see the validation log).
