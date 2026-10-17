# Protected dependency and CI change proposal (for the human-maintained route)

Status: prepared, not applied. `pyproject.toml`, `uv.lock` and `.github/*` are protected (`FACTORY_RULES.md`). An autonomous builder must not edit or merge them. These files are reviewable patches only.

## What is in this proposal

| File | Target | Applies to |
|---|---|---|
| `playwright-dev-dependency.patch` | `pyproject.toml` | adds `playwright>=1.64,<2` to the `dev` extra only |
| `uv-lock-playwright.patch` | `uv.lock` | regenerated lock for the proposed `pyproject.toml` |
| `ci-playwright-browser-install.patch` | `.github/workflows/{validation,stabilization,release-qualification}.yml` | Chromium install steps per runner OS |

Verified with `git apply --check` against the combined candidate `fdcf39cb` (tree `c4b88445`).

## Existing lockfile inconsistencies (found on `origin/main` before any change)

`uv lock --check` against the **original** `pyproject.toml` and `uv.lock` exits 1: the lock needs updating. Per-constraint check results:

| Declared requirement | Locked version | Status |
|---|---|---|
| `markdown-it-py>=3.0,<4` (runtime) | not in lock | **missing** |
| `pytest>=8.0,<9` (dev) | 9.1.1 | **violates** |
| `pytest-xdist>=3.0,<4` (dev and `all`) | not in lock | **missing** |
| `ruff>=0.4.0,<1` (dev) | not in lock | **missing** |
| `openai>=1.40,<2` (`openai` and `all`) | 2.45.0 | **violates** |
| `pydantic`, `pyyaml`, `anthropic` | in range | ok |

Consequences:

- **`markdown-it-py` is a real runtime defect for locked installs.** `src/auteur/publish.py` imports `markdown_it` at module load, so a clean install from this lock cannot import the publish module.
- The pytest pin (9.1.1) and the openai pin (2.45.0) both violate their declared constraints. They are not Playwright side effects.
- The lock also has a stale project version (`auteur 0.1.0`, while `pyproject.toml` says `1.0.0`).
- CI does not consume `uv.lock`. All three workflows install with `python -m pip install -e ".[dev]"`, which resolves from `pyproject.toml`. So the lock problems affect `uv`-based installs, not the CI test path.

## Effect of regenerating the lock (`uv-lock-playwright.patch`)

Version changes from the original lock to the proposed lock:

- Added: `playwright 1.64.0` with `pyee 14.0.0` and `greenlet 3.5.6`.
- Added: `markdown-it-py 3.0.0`, `mdurl 0.1.2`.
- Added: `pytest-xdist 3.8.0`, `execnet 2.1.2`, `ruff 0.17.1`.
- Changed: `pytest 9.1.1 → 8.4.2` (satisfies `<9`).
- Changed: `openai 2.45.0 → 1.109.1` (satisfies `<2`).
- Project version: `auteur 0.1.0 → 1.0.0`.

Result: `uv lock --check` exits 0 for the proposed pair, and all 12 declared constraints are satisfied.

### Review points the human must decide

1. **openai major-version move in a runtime extra (2.45.0 → 1.109.1).** Required to satisfy the declared `<2`. Verified only in part: the openai-related test module (`tests/test_llm_retrying.py`, 14 tests, mocked `openai.OpenAI`) passes against 1.109.1 with exit 0. No live API call was made. Decide whether the `openai` extra needs a live check.
2. **pytest 9 → 8.** Required by the declared `<9`. Either accept 8.4.2, or change the declared constraint. This changes the test runner's major version.
3. **Lock scope.** Regeneration adds the full `dev` tree, which the original lock never contained.

## Playwright and CI browser install

- Playwright belongs in dev/test only. Two collected test modules and two qualification scripts import `playwright.sync_api`.
- The Browser tests launch Playwright's managed Chromium unless `CHROMIUM_PATH` is set. Installing the Python package does not install Chromium, so CI needs an explicit install step.
- Platform-specific commands (verified on Windows only; Linux and macOS not executed locally):
  - Windows and macOS: `python -m playwright install chromium`.
  - Linux only: `python -m playwright install --with-deps chromium`. `--with-deps` installs system packages.
  - Windows check run locally: `python -m playwright install chromium --with-deps --dry-run` prints `powershell.exe ... install_media_pack.ps1`. So `--with-deps` runs a Windows-specific PowerShell script there. That is why it is restricted to `runner.os == 'Linux'`. The patch uses `if: runner.os == 'Linux'` and `if: runner.os != 'Linux'`.
  - The real Windows install ran here as an idempotent check; it exited 0 and printed no output.

## Installation and verification (human, after applying the patches)

```bash
python -m pip install -e ".[dev]"
python -m playwright install chromium
python -m pytest -q tests/test_focused_unfolding_browser.py tests/test_studio_semantic_browser.py
```

On Linux CI add `--with-deps` to the Chromium install, as in the patch.

## Authority boundary

Nothing here is applied, merged, or released by the builder. The owner decision on #455 requires this change to go through the human-maintained protected route.
