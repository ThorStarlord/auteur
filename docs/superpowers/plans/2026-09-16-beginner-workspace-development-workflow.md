# Beginner Workspace Development Workflow Implementation Plan

**Goal:** Make Beginner Workspace development one-command and repeatable without replacing Auteur's Python application.

**Architecture:** npm is a private developer launcher. Python remains the application, API, persistence, orchestration, and narrative-authority runtime. A Node supervisor is optional and only restarts the Python child during active development. A workspace helper creates state through the existing HTTP API, never by editing .auteur files.

**Tech Stack:** npm scripts, Node built-ins, Python 3, existing Beginner Workspace HTTP API, pytest, and Node's built-in test runner.

---

## Commands

    npm start
    npm run workspace:new -- --id sealed-elevator-1
    npm run dev

The server remains running across normal tests. A new workspace ID provides clean
persisted state. npm run dev is optional for backend editing and watches Python
source. No release qualification, merge, or publication is part of this plan.

## File map

- Create package.json: private developer commands, no dependencies.
- Create scripts/beginner-workspace.mjs: POST workspace creation command.
- Create scripts/beginner-dev.mjs: optional Python child supervisor.
- Create tests/test_beginner_dev_scripts.py: package/helper contract tests.
- Create tests/beginner-dev-scripts.test.mjs: supervisor lifecycle tests.
- Modify README.md: developer workflow and persistence explanation.
- Do not modify the narrative engine, canonical artifacts, or browser journey.

## Task 1: Define npm commands

Files: package.json and tests/test_beginner_dev_scripts.py.

- [ ] Write a failing test that reads package.json and asserts:

    package["private"] is True
    package["scripts"]["start"] == "node scripts/beginner-dev.mjs"
    package["scripts"]["workspace:new"] == "node scripts/beginner-workspace.mjs"
    package["scripts"]["dev"] == "node scripts/beginner-dev.mjs"

- [ ] Run:

    python -m pytest tests/test_beginner_dev_scripts.py::test_package_scripts_expose_beginner_workflow_commands -q

Expected: FAIL because package.json is absent.

- [ ] Create package.json:

    {
      "name": "auteur-local-workspace-tools",
      "private": true,
      "scripts": {
        "start": "node scripts/beginner-dev.mjs",
        "workspace:new": "node scripts/beginner-workspace.mjs",
        "dev": "node scripts/beginner-dev.mjs"
      }
    }

Do not add npm dependencies.

- [ ] Rerun the test; expected PASS.
- [ ] Commit with:

    git add package.json tests/test_beginner_dev_scripts.py
    git commit -m "chore: define beginner workspace dev commands"

## Task 2: Add fresh workspace creation

Files: scripts/beginner-workspace.mjs and tests/test_beginner_dev_scripts.py.

- [ ] Write failing tests using a local fake HTTP server. Assert the command sends
one POST to /api/beginner/workspaces with:

    {
      "workspace_id": "sealed-elevator-1",
      "command_id": "create-sealed-elevator-1",
      "project_id": "manual-qualification",
      "guidance_genre": "mystery",
      "premise": "A murder mystery in one elevator: six strangers, no supernatural explanation, and the killer never leaves the elevator."
    }

Also assert that missing --id and HTTP 4xx responses exit nonzero.

- [ ] Run:

    python -m pytest tests/test_beginner_dev_scripts.py -k workspace_command -q

Expected: FAIL because the script is absent.

- [ ] Implement the script with Node built-in HTTP/fetch behavior. It must parse
--base-url with default http://127.0.0.1:8791, require --id, default project ID
to the workspace ID, default guidance genre to mystery, default to the sealed
elevator premise, POST the JSON payload, print the workspace URL, and return
nonzero for transport/non-2xx errors. It must not import Auteur internals or
write persistence files.

- [ ] Rerun the focused tests; expected PASS.
- [ ] Verify while the server runs:

    npm run workspace:new -- --id sealed-elevator-manual-2

Expected output includes:
    Created workspace: sealed-elevator-manual-2
    Open: http://127.0.0.1:8791/?workspace=sealed-elevator-manual-2

- [ ] Commit with:

    git add scripts/beginner-workspace.mjs tests/test_beginner_dev_scripts.py
    git commit -m "feat: add fresh beginner workspace command"

## Task 3: Add optional backend watching

Files: scripts/beginner-dev.mjs and tests/beginner-dev-scripts.test.mjs.

- [ ] Write failing Node tests with an injected fake child factory. Verify:

    test("starts Python with the repository project", async () => {
      const child = await runSupervisor({ watch: false, childFactory });
      assert.deepEqual(child.spawnArgs, [
        "-m", "auteur.beginner.server", "--project", repoRoot, "--port", "8791"
      ]);
      await child.stop();
    });

    test("watch mode restarts after a Python file changes", async () => {
      const child = await runSupervisor({ watch: true, files: [backendFile], childFactory });
      touch(backendFile);
      await waitFor(() => child.spawnCount === 2);
      await child.stop();
    });

    test("shutdown kills the child exactly once", async () => {
      const child = await runSupervisor({ watch: true, childFactory });
      await child.stop();
      assert.equal(child.killCount, 1);
    });

Tests must not start Auteur or use unbounded sleeps.

- [ ] Run:

    node --test tests/beginner-dev-scripts.test.mjs

Expected: FAIL because the supervisor is absent.

- [ ] Implement the supervisor. Resolve the root from process.cwd(). Use
AUTEUR_PYTHON when present, otherwise python on Windows and python3 elsewhere.
Spawn:

    -m auteur.beginner.server --project <repoRoot> --port 8791

Forward child output and exit status. Support opt-in --watch. Watch only
src/auteur/beginner Python files and src/auteur/mystery Python files. Poll at
500 ms or slower, keep one child alive, restart once per detected mtime change,
and clean up on SIGINT and SIGTERM. Do not watch .auteur, data, artifacts,
uv.lock, or tests.

Both npm start and npm run dev use the same supervisor. npm start runs without
watching; npm run dev enables watching. In both modes the child process is the
existing Python Beginner server.

- [ ] Rerun Node tests; expected PASS.
- [ ] Manually verify:

    npm run dev

Edit a watched Python file, confirm one restart, then press Ctrl+C and confirm
port 8791 is freed.
- [ ] Commit with:

    git add scripts/beginner-dev.mjs tests/beginner-dev-scripts.test.mjs
    git commit -m "chore: add optional beginner server watcher"

## Task 4: Document the workflow

Files: README.md and tests/test_beginner_dev_scripts.py.

- [ ] Write a failing test requiring README to contain npm start, npm run
workspace:new, npm run dev, 127.0.0.1:8791, and the phrase new workspace ID.
- [ ] Run the focused test; expected FAIL.
- [ ] Add a concise README section:

    cd H:\GithubRepositories\auteur\.worktrees\beginner-workspace-vslice
    $env:PYTHONPATH="$(Get-Location);$(Join-Path (Get-Location) 'src')"
    npm start

In a second terminal:

    npm run workspace:new -- --id sealed-elevator-test-1

Open the printed URL. Explain that the server stays running, a new workspace ID
creates clean persisted state, a browser refresh handles browser-only changes,
and npm run dev is for active Python development.
- [ ] Rerun the test; expected PASS.
- [ ] Commit with:

    git add README.md tests/test_beginner_dev_scripts.py
    git commit -m "docs: document beginner workspace development workflow"

## Task 5: Bounded verification

- [ ] Run:

    python -m pytest tests/test_beginner_dev_scripts.py -q
    node --test tests/beginner-dev-scripts.test.mjs
    node --check scripts/beginner-workspace.mjs
    node --check scripts/beginner-dev.mjs

- [ ] Run the existing Beginner boundary suite:

    python -m pytest tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_qualification.py -q

- [ ] Verify:

    git status --short --branch
    git diff --check
    git diff -- uv.lock
    git rev-parse HEAD

Expected: only planned files changed, uv.lock is untouched, main is untouched,
and human usability qualification remains pending.

## Out of scope

Replacing Python with Node; frontend frameworks; npm dependencies just for
watching; automatic workspace deletion; changes to canonical authority,
staleness, or session semantics; browser redesign; release qualification;
publication; merging PR #233.

## Self-review

This plan covers all three recommendations: npm start, fresh workspace creation,
and optional backend watching. npm is convenience only; Python remains the
authoritative runtime. Fresh state uses the public API. Watching is opt-in and
excluded from qualification so evidence stays deterministic.
