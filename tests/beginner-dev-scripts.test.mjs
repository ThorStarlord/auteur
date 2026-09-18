import assert from "node:assert/strict";
import { EventEmitter } from "node:events";
import { mkdtemp, writeFile, utimes } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { runSupervisor } from "../scripts/beginner-dev.mjs";
import { createWorkspace } from "../scripts/beginner-workspace.mjs";

function fakeFactory(calls) {
  return (_command, args) => {
    const child = new EventEmitter();
    child.killed = false;
    child.kill = () => { child.killed = true; calls.kills += 1; };
    calls.args = args;
    calls.spawns += 1;
    return child;
  };
}

test("starts the Python Beginner server with the repository project", async () => {
  const root = await mkdtemp(join(tmpdir(), "auteur-dev-"));
  const file = join(root, "backend.py");
  await writeFile(file, "x = 1\n");
  const calls = { spawns: 0, kills: 0 };
  const supervisor = await runSupervisor({ root, files: [file], childFactory: fakeFactory(calls) });
  assert.deepEqual(calls.args, ["-m", "auteur.beginner.server", "--project", root, "--port", "8791"]);
  await supervisor.stop();
  assert.equal(calls.kills, 1);
});

test("watch mode restarts after a Python file changes", async () => {
  const root = await mkdtemp(join(tmpdir(), "auteur-dev-"));
  const file = join(root, "backend.py");
  await writeFile(file, "x = 1\n");
  const calls = { spawns: 0, kills: 0 };
  const supervisor = await runSupervisor({ root, files: [file], watch: true, intervalMs: 20, childFactory: fakeFactory(calls) });
  const now = new Date(Date.now() + 2000);
  await utimes(file, now, now);
  await new Promise((resolve) => setTimeout(resolve, 80));
  await supervisor.stop();
  assert.equal(calls.spawns, 2);
  assert.equal(calls.kills, 2);
});

test("workspace command posts the mystery creation payload", async () => {
  let request;
  const fakeFetch = async (url, options) => {
    request = { url, options };
    return { ok: true, status: 201, json: async () => ({ workspace: { workspace_id: "demo-1" } }) };
  };
  const result = await createWorkspace(["--id", "demo-1"], fakeFetch);
  const payload = JSON.parse(request.options.body);
  assert.equal(request.url, "http://127.0.0.1:8791/api/beginner/workspaces");
  assert.equal(payload.workspace_id, "demo-1");
  assert.equal(payload.guidance_genre, "mystery");
  assert.match(result.url, /workspace=demo-1$/);
});

test("workspace script has a Windows-safe executable entrypoint", async () => {
  const result = await import("../scripts/beginner-workspace.mjs");
  assert.equal(typeof result.createWorkspace, "function");
});
