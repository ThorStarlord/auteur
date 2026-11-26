// The consequence analysis's presentation: words that say only what the owner recorded. Nothing here judges a proposal.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../src/auteur/beginner/browser/studio_architecture_consequence.js", import.meta.url), "utf8");
const sandbox = { window: {}, console };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(source, sandbox);
const C = sandbox.AuteurStudioConsequence;

test("each standing says whether the analysis is about the proposal on screen, and no other is presented as current", () => {
  assert.match(C.standingWords("current").label, /About this proposal, not yet applied/);
  assert.match(C.standingWords("superseded").label, /earlier proposal/);
  assert.match(C.standingWords("applied").label, /already applied/);
  assert.match(C.standingWords("stale_context").label, /changed after this analysis was asked/);
  assert.notEqual(C.standingWords("superseded").label, C.standingWords("current").label);
  assert.equal(C.standingWords("unknown_state").tone, "note");
});

test("a concern's status keeps the owner's distinction between preserved, transformed, possibly displaced and new", () => {
  assert.equal(C.statusWords("possibly_displaced"), "May be displaced");
  assert.equal(C.statusWords("introduced"), "New concern");
  assert.equal(C.statusWords("transformed"), "Transformed");
  assert.equal(C.statusWords("preserved"), "Still represented");
});

test("an alternative is labelled by its approach, and an unknown approach is shown as the owner wrote it", () => {
  assert.equal(C.approachWords("separate"), "Separate");
  assert.equal(C.approachWords("reframe"), "Reframe");
  assert.equal(C.approachWords("abandon"), "abandon");
});

test("an evidence line names its kind, its Book and its proposal status, and keeps the owner's text", () => {
  const line = C.evidenceLine({ id: "E7", kind: "book_decision", book_number: 24, proposal_status: "reworded",
                                text: "Whether the conversion is a lasting settlement." });
  assert.equal(line, "E7 · Working Book decision (Book 24) · question in proposal: reworded — Whether the conversion is a lasting settlement.");
});

test("a question is worded as the analysis examined it: the proposed wording when there is one", () => {
  const packet = {
    evidence: [
      { id: "E1", kind: "baseline_wording", text: "Is it a lasting settlement?" },
      { id: "E2", kind: "proposed_wording", text: "Does it reach the purchased shares?" },
    ],
    examined_questions: [{ id: "q-conversion-settlement", baseline_evidence: ["E1"], proposed_evidence: ["E2"] }],
  };
  assert.equal(C.questionWording(packet, "q-conversion-settlement"), "Does it reach the purchased shares?");
  assert.equal(C.questionWording({ evidence: [], examined_questions: [] }, "q-missing"), "q-missing");
});

test("a recorded mechanism's provenance is named in the owner's words, and an unknown one is shown as written", () => {
  assert.equal(C.provenanceWords("preserved"), "Preserved in the proposal");
  assert.equal(C.provenanceWords("transformed"), "Transformed by the proposal");
  assert.equal(C.provenanceWords("historical"), "Historical: no longer current");
  assert.equal(C.provenanceWords("inferred"), "inferred");
});

test("version 2 approaches keep the baseline and the proposal apart, and the retired name is labelled as version 1", () => {
  assert.equal(C.approachWords("keep_baseline"), "Keep the baseline concern");
  assert.equal(C.approachWords("accept_proposal"), "Accept the proposal as written");
  assert.match(C.approachWords("retain"), /version 1 wording; its meaning is not fixed/);
});

test("inheritance, reach, stage and basis are named as the owner names them, and a trajectory is never presented as an event", () => {
  assert.equal(C.inheritanceWords("recorded_inheritance"), "Recorded inheritance");
  assert.equal(C.inheritanceWords("unknown_inheritance"), "Unknown inheritance");
  assert.equal(C.reachWords("local"), "Local to this change");
  assert.equal(C.stageWords("long_horizon"), "Long-horizon development");
  assert.equal(C.basisWords("speculative"), "Speculative");
  assert.match(C.REACH.not_established, /Not established by the record/);
});
