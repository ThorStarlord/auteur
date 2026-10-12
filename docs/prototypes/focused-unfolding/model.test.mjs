import test from 'node:test';
import assert from 'node:assert/strict';
import {createDemoState,createAnchor,selectFocus,suggestForFocus,inspectGhost,adoptGhost,dismissGhost,
        replaceSourceRevision,collapseCluster,returnFocus,editWorkingNode} from './model.mjs';

const seeded = () => createAnchor(createDemoState(), 'emotion', 'Joy through generous heroism');

test('an empty graph invites author-owned emotion or an alternative anchor',()=>{
  const s=createDemoState();
  assert.equal(s.focusId,null);
  assert.equal(s.nodes.length,0);
  const p=createAnchor(s,'premise','A reluctant knight must protect a village');
  assert.equal(p.nodes[0].role,'premise');
  assert.equal(p.nodes[0].authority,'author_working');
  assert.equal(p.nodes[0].canonical,false);
  assert.equal(s.nodes.length,0);
});

test('selected emotional intention reveals at most three source-scoped hypotheses',()=>{
  const s=seeded(), items=suggestForFocus(s,3);
  assert.equal(items.length,3);
  assert.ok(items.every(x=>x.supportStatus==='hypothesis'&&x.sourceRef&&x.requestSha===s.revision));
  assert.ok(items.every(x=>x.originFocusId===s.focusId));
  assert.equal(suggestForFocus(s,2).length,2);
});

test('an author can start from a character without specifying an emotion',()=>{
  const s=createAnchor(createDemoState(),'character','Eira the healer');
  assert.equal(s.focusId,s.nodes[0].id);
  assert.equal(s.nodes[0].role,'character');
  assert.equal(suggestForFocus(s).length,3);
});

test('inspecting a ghost does not author, adopt, or persist a node',()=>{
  const s=seeded(), id=suggestForFocus(s)[0].id;
  const next=inspectGhost(s,id);
  assert.equal(next.inspectedGhostId,id);
  assert.equal(next.nodes.length,1);
  assert.deepEqual(next.edges,[]);
  assert.equal(s.inspectedGhostId,null);
});

test('adopting creates exactly one editable noncanonical working item without asserting an edge',()=>{
  const s=seeded(), ghost=suggestForFocus(s)[0];
  const once=adoptGhost(s,ghost.id), twice=adoptGhost(once,ghost.id);
  assert.equal(once.nodes.length,2);
  assert.equal(twice.nodes.length,2);
  const node=once.nodes.at(-1);
  assert.equal(node.authority,'author_working');
  assert.equal(node.canonical,false);
  assert.equal(node.origin.sourceRef,ghost.sourceRef);
  assert.equal(node.role,ghost.targetRole);
  assert.deepEqual(once.edges,[]);
  assert.equal(suggestForFocus(once).some(x=>x.id===ghost.id),false);
});

test('focusing an adopted trope unfolds its own local structural options',()=>{
  const s=seeded(), suggestion=suggestForFocus(s)[0];
  const adopted=adoptGhost(s,suggestion.id);
  const focus=selectFocus(adopted,adopted.nodes.at(-1).id);
  const neighbors=suggestForFocus(focus);
  assert.ok(neighbors.length>=2&&neighbors.length<=3);
  assert.ok(neighbors.some(g=>g.targetRole==='structure'));
  assert.ok(neighbors.every(g=>g.originFocusId===focus.focusId));
  assert.equal(returnFocus(focus).focusId,s.focusId);
});

test('focusing a different concept clears prior provisional selection without deleting nodes',()=>{
  const s=seeded(), first=suggestForFocus(s)[0];
  const adopted=adoptGhost(s,first.id);
  const focus=selectFocus(adopted,adopted.nodes.at(-1).id);
  assert.equal(focus.inspectedGhostId,null);
  assert.ok(!suggestForFocus(focus).some(x=>x.originFocusId===adopted.focusId));
  assert.equal(focus.nodes.length,2);
});

test('dismissal hides a focus-local suggestion and leaves working notes intact',()=>{
  const s=seeded(), id=suggestForFocus(s)[0].id;
  const dismissed=dismissGhost(s,id);
  assert.equal(dismissed.nodes.length,1);
  assert.ok(!suggestForFocus(dismissed).some(x=>x.id===id));
  assert.equal(suggestForFocus(s).length,3);
});

test('changing source revision expires ghosts without destroying working author decisions',()=>{
  const s=seeded(), g=suggestForFocus(s)[0];
  const adopted=adoptGhost(s,g.id), changed=replaceSourceRevision(adopted,'demo-paladin-v2');
  assert.equal(changed.nodes.length,2);
  assert.equal(changed.nodes.at(-1).origin.requestSha,'demo-paladin-v1');
  assert.equal(changed.inspectedGhostId,null);
  assert.ok(!suggestForFocus(changed).some(x=>x.id===g.id));
  assert.throws(()=>adoptGhost(changed,g.id),/unavailable|stale/i);
});

test('collapsing is visual only and never mutates working items or connections',()=>{
  const s=seeded(), a=adoptGhost(s,suggestForFocus(s)[0].id);
  const collapsed=collapseCluster(a,s.focusId,true),expanded=collapseCluster(collapsed,s.focusId,false);
  assert.equal(collapsed.nodes.length,a.nodes.length);
  assert.deepEqual(collapsed.edges,a.edges);
  assert.ok(collapsed.collapsed.includes(s.focusId));
  assert.deepEqual(expanded.nodes,a.nodes);
  assert.ok(!expanded.collapsed.includes(s.focusId));
});

test('editing an upstream emotional goal does not rewrite adopted downstream ideas',()=>{
  const s=seeded(),a=adoptGhost(s,suggestForFocus(s)[0].id);
  const b=editWorkingNode(a,s.focusId,'Hope restored through helping strangers');
  assert.equal(b.nodes.at(-1).title,a.nodes.at(-1).title);
  assert.equal(b.nodes[0].title,'Hope restored through helping strangers');
  assert.ok(b.nodes.at(-1).needsReview);
  assert.equal(b.nodes.length,a.nodes.length);
});

test('unknown or retired ghost identity cannot be adopted',()=>{
  assert.throws(()=>adoptGhost(seeded(),'ghost:bogus'),/unavailable|stale/i);
  assert.throws(()=>selectFocus(seeded(),'missing-node'),/Unknown focus/);
});

test('explicit alternatives reveal an additional local ghost that can be adopted',()=>{
  const s=seeded(),first=suggestForFocus(s,3),more=suggestForFocus(s,3,3);
  assert.equal(first.length,3);
  assert.equal(more.length,1);
  assert.notEqual(more[0].id,first[0].id);
  const explored=inspectGhost(s,more[0].id),adopted=adoptGhost(explored,more[0].id);
  assert.equal(adopted.nodes.length,2);
});
