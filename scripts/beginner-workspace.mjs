#!/usr/bin/env node

const DEFAULT_BASE_URL = "http://127.0.0.1:8791";
const DEFAULT_PREMISE =
  "A murder mystery in one elevator: six strangers, no supernatural explanation, and the killer never leaves the elevator.";

function parseArgs(argv) {
  const args = { baseUrl: DEFAULT_BASE_URL, projectId: null, premise: DEFAULT_PREMISE, id: null };
  for (let index = 0; index < argv.length; index += 1) {
    const flag = argv[index];
    if (flag === "--base-url") args.baseUrl = argv[++index];
    else if (flag === "--project-id") args.projectId = argv[++index];
    else if (flag === "--premise") args.premise = argv[++index];
    else if (flag === "--id") args.id = argv[++index];
    else throw new Error(`unknown argument: ${flag}`);
  }
  if (!args.id) throw new Error("--id is required");
  if (!args.projectId) args.projectId = args.id;
  return args;
}

export async function createWorkspace(argv = process.argv.slice(2), fetchImpl = fetch) {
  const args = parseArgs(argv);
  const response = await fetchImpl(`${args.baseUrl.replace(/\/$/, "")}/api/beginner/workspaces`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      workspace_id: args.id,
      command_id: `create-${args.id}`,
      project_id: args.projectId,
      guidance_genre: "mystery",
      premise: args.premise,
    }),
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body?.error || `workspace creation failed (${response.status})`);
  const url = `${args.baseUrl.replace(/\/$/, "")}/?workspace=${encodeURIComponent(args.id)}`;
  return { body, url };
}

if (import.meta.url === `file://${process.argv[1].replaceAll("\\", "/")}`) {
  createWorkspace().then(({ body, url }) => {
    console.log(`Created workspace: ${body.workspace.workspace_id}`);
    console.log(`Open: ${url}`);
  }).catch((error) => {
    console.error(`Workspace creation failed: ${error.message}`);
    process.exitCode = 1;
  });
}
