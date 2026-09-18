#!/usr/bin/env node

import { readdir, stat } from "node:fs/promises";
import { join, resolve } from "node:path";
import { spawn } from "node:child_process";

async function pythonFiles(root) {
  const result = [];
  async function visit(directory) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) await visit(path);
      else if (entry.isFile() && entry.name.endsWith(".py")) result.push(path);
    }
  }
  await visit(join(root, "src", "auteur", "beginner"));
  await visit(join(root, "src", "auteur", "mystery"));
  return result;
}

async function snapshot(files) {
  const values = await Promise.all(files.map(async (file) => [file, (await stat(file)).mtimeMs]));
  return new Map(values);
}

export async function runSupervisor({
  root = process.cwd(),
  watch = false,
  childFactory = spawn,
  intervalMs = 500,
  files = null,
} = {}) {
  const repoRoot = resolve(root);
  const python = process.env.AUTEUR_PYTHON || (process.platform === "win32" ? "python" : "python3");
  const args = ["-m", "auteur.beginner.server", "--project", repoRoot, "--port", "8791"];
  const pythonPath = [repoRoot, join(repoRoot, "src"), process.env.PYTHONPATH].filter(Boolean).join(process.platform === "win32" ? ";" : ":");
  const childOptions = { cwd: repoRoot, stdio: "inherit", env: { ...process.env, PYTHONPATH: pythonPath } };
  let child = childFactory(python, args, childOptions);
  let currentFiles = files || await pythonFiles(repoRoot);
  let known = await snapshot(currentFiles);
  let timer = null;
  let stopping = false;

  const restart = async () => {
    if (stopping) return;
    child.kill();
    child = childFactory(python, args, childOptions);
  };
  if (watch) {
    timer = setInterval(async () => {
      try {
        currentFiles = files || await pythonFiles(repoRoot);
        const next = await snapshot(currentFiles);
        const changed = next.size !== known.size || [...next].some(([file, mtime]) => known.get(file) !== mtime);
        known = next;
        if (changed) await restart();
      } catch (error) {
        console.error(`Watcher error: ${error.message}`);
      }
    }, intervalMs);
  }
  return {
    child,
    async stop() {
      stopping = true;
      if (timer) clearInterval(timer);
      if (child && !child.killed) child.kill();
    },
  };
}

async function main() {
  const supervisor = await runSupervisor({ watch: process.argv.includes("--watch") });
  const stop = async () => { await supervisor.stop(); process.exit(0); };
  process.once("SIGINT", stop);
  process.once("SIGTERM", stop);
  supervisor.child.once("exit", (code) => { if (!process.argv.includes("--watch")) process.exit(code ?? 1); });
}

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].replaceAll("\\", "/"))) main().catch((error) => { console.error(error.message); process.exitCode = 1; });
