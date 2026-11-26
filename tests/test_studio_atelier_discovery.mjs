// The Atelier's discovery presentation: words that say only what the owner recorded.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../src/auteur/beginner/browser/studio_atelier_discovery.js", import.meta.url), "utf8");
const sandbox = { window: {}, console };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(source, sandbox);
const D = sandbox.AuteurAtelierDiscovery;

test("a transferable possibility says it is ready and can be investigated", () => {
  const status = { transferable: true, state: "transferable" };
  assert.equal(D.statusWords(status).label, "Ready to investigate");
  assert.equal(D.canInvestigate({ status }), true);
});

test("a reworded possibility says it was formulated against an earlier wording, and stays investigable", () => {
  const status = { transferable: true, state: "reworded" };
  assert.match(D.statusWords(status).label, /earlier wording/);
  assert.equal(D.canInvestigate({ status }), true);
});

test("a possibility whose question is no longer open cannot be investigated, and says why", () => {
  const status = { transferable: false, state: "not_transferable" };
  assert.match(D.statusWords(status).label, /no longer open/);
  assert.equal(D.canInvestigate({ status }), false);
});

test("a declined possibility is not offered for investigation until it is reopened", () => {
  const status = { transferable: true, state: "transferable" };
  assert.equal(D.canInvestigate({ status, decision: { decision: "declined" } }), false);
  assert.equal(D.canInvestigate({ status, decision: null }), true);
});

test("evidence says whether it is still in the Architecture, and keeps the agent's note labelled as the agent's", () => {
  const line = D.evidenceLine({ ref_kind: "node", ref_id: "eng_ledger", book_number: null, present_now: true, note: "Records hours." });
  assert.match(line, /Architecture element · eng_ledger · still in the Architecture/);
  assert.match(line, /The agent’s note: Records hours\./);
  const book = D.evidenceLine({ ref_kind: "book_decision", ref_id: "dec-x", book_number: 24, present_now: null, note: "n" });
  assert.match(book, /Working Book decision · dec-x \(Book 24\) · read again when it is investigated/);
});

test("kind labels are the reasoning guidance's names, and an absent kind has no label", () => {
  assert.equal(D.kindLabel("shared_mechanism"), "Shared dramatic mechanism");
  assert.equal(D.kindLabel(null), null);
});
