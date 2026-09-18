import { createWorkspace } from "../beginner-workspace.mjs";

const TEST = {
  id: "sealed-elevator-human-5daa",
  projectId: "manual-qualification-retest",
  premise: "A murder mystery in one elevator: six strangers, no supernatural explanation, and the killer never leaves the elevator.",
};

const { url } = await createWorkspace([
  "--id", TEST.id,
  "--project-id", TEST.projectId,
  "--premise", TEST.premise,
]);

console.log(`Qualification workspace ready: ${TEST.id}`);
console.log(`Open: ${url}`);
