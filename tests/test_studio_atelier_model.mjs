// Atelier study model: every drawn relationship is a recorded one, the atlas is deterministic and
// stable, and the three unfolding treatments only move what they say they move.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const repo = new URL('../', import.meta.url);
const browser = new URL('src/auteur/beginner/browser/', repo);
const read = (url) => readFileSync(url, 'utf8');
// Values built inside the vm sandbox carry its prototypes; compare them as plain data.
const plain = (value) => JSON.parse(JSON.stringify(value));

function load() {
  const sandbox = {window: {}};
  runInNewContext(read(new URL('studio_explanations.js', browser)), sandbox);
  runInNewContext(read(new URL('studio_atelier_model.js', browser)), sandbox);
  return sandbox.window.AuteurStudioAtelierModel;
}
const candidate = (path) => {
  const data = JSON.parse(read(new URL(path, repo)));
  return data.candidate || data;
};
const SMALL = candidate('docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json');
const DENSE = candidate('qualification/studio-trace/artifacts/candidate-2.json');

// Resolve a sourceRef such as "phases/p1/genre_activations/g#0/trope_functions/1" against the candidate.
function resolve(c, ref) {
  let here = c;
  for (const raw of ref.split('/')) {
    const segment = raw.split('#')[0];
    if (Array.isArray(here)) {
      const byId = here.find((x) => x && (x.id === segment || x.genre_node_id === segment));
      here = byId !== undefined ? byId : here[Number(segment)];
    } else if (here && typeof here === 'object') here = here[segment];
    else return undefined;
    if (here === undefined || here === null) return undefined;
  }
  return here;
}

for (const [name, c] of [['small', SMALL], ['dense', DENSE]]) {
  test(`${name}: every relationship is recorded in the candidate, none inferred`, () => {
    const M = load();
    const model = M.buildModel(c, 'sha-test');
    assert.ok(model.relations.length > 10);
    for (const r of model.relations) {
      assert.ok(model.byId[r.from] && model.byId[r.to], `endpoints exist for ${r.id}`);
      assert.notEqual(resolve(c, r.sourceRef), undefined, `source ${r.sourceRef} is recorded`);
    }
    // Candidate links appear only with their recorded endpoints.
    for (const r of model.relations.filter((x) => x.sourceKind === 'proposal_edge')) {
      const link = resolve(c, r.sourceRef);
      const ends = [model.byId[r.from].nodeId, model.byId[r.to].nodeId];
      assert.deepEqual(plain(ends), [link.source, link.target]);
    }
  });

  test(`${name}: the atlas is deterministic and selection never changes it`, () => {
    const M = load();
    const model = M.buildModel(c, 'sha-test');
    const relationsBefore = JSON.stringify(model.relations);
    const a = M.layoutAtlas(model, {aspect: 1.4});
    const b = M.layoutAtlas(M.buildModel(c, 'sha-test'), {aspect: 1.4});
    assert.deepEqual(plain(a.positions), plain(b.positions));
    const focus = model.concepts.find((x) => x.facet === 'genres').id;
    for (const treatment of ['A', 'B', 'C']) {
      const hood = M.neighbourhood(model, focus, 2);
      M.compose(model, a, hood, treatment, {width: 846, height: 630, z: 1});
    }
    assert.deepEqual(plain(M.layoutAtlas(model, {aspect: 1.4}).positions), plain(a.positions));
    assert.equal(JSON.stringify(model.relations), relationsBefore, 'composition adds no relationship');
    // Phases follow recorded story order from left to right.
    const xs = plain(model.timeline.map((p) => a.positions[p.id].x));
    assert.deepEqual(xs, [...xs].sort((p, q) => p - q));
  });

  test(`${name}: treatments move only the neighbourhood, and A moves nothing`, () => {
    const M = load();
    const model = M.buildModel(c, 'sha-test');
    const atlas = M.layoutAtlas(model, {aspect: 1.4});
    const focus = model.concepts.filter((x) => x.facet === 'genres')
      .sort((p, q) => model.adjacency[q.id].length - model.adjacency[p.id].length)[0].id;
    const hood = M.neighbourhood(model, focus, 1);
    const inHood = new Set(hood.order);
    const results = {};
    for (const treatment of ['A', 'B', 'C']) {
      const comp = M.compose(model, atlas, hood, treatment, {width: 846, height: 630, z: treatment === 'A' ? 0.5 : 1});
      for (const id of Object.keys(atlas.positions)) {
        if (!inHood.has(id)) assert.deepEqual(plain(comp.targets[id]), plain(atlas.positions[id]), `${treatment} keeps ${id} home`);
      }
      assert.deepEqual(plain(comp.targets[focus]), plain(atlas.positions[focus]), `${treatment} keeps the focus home`);
      assert.ok(comp.moved.every((id) => inHood.has(id)));
      results[treatment] = {comp, measure: M.measure(model, atlas, hood, comp, treatment === 'A' ? 0.5 : 1)};
    }
    assert.equal(results.A.comp.moved.length, 0);
    assert.equal(results.B.comp.moved.length, hood.first.length, 'B composes every first-order neighbour');
    assert.ok(results.C.comp.moved.length <= results.B.comp.moved.length, 'C moves no more than B');
    assert.equal(results.B.measure.labelOverlaps, 0, 'B composition has no estimated label overlap');
    assert.ok(results.C.measure.labelOverlaps <= 1, 'C composition is nearly overlap-free');
  });
}

test('Book running heads and display titles are editorial, not raw records', () => {
  const M = load();
  assert.equal(M.bookLabel('opening_books_duration_unknown'), 'OPENING BOOKS');
  assert.equal(M.bookLabel('early_middle_duration_unknown'), 'EARLY MIDDLE');
  assert.equal(M.bookLabel('book_12'), 'BOOK 12');
  assert.equal(M.bookLabel('books_13_14'), 'BOOKS 13–14');
  assert.equal(M.displayTitle('Trope: Signing as Public Exposure'), 'Signing as Public Exposure');
  assert.equal(M.displayTitle('Reader Experience: Earned Trust'), 'Earned Trust');
  assert.equal(M.displayTitle('Literary mystery'), 'Literary mystery');
  const dense = M.buildModel(DENSE, 'sha-test');
  assert.ok(dense.concepts.every((cn) => !/^(Trope|Reader Experience):\s/i.test(cn.title)));
});

test('dense: constellation phases keep story order within each arc', () => {
  const M = load();
  const model = M.buildModel(DENSE, 'sha-test');
  const atlas = M.layoutAtlas(model, {aspect: 1.4});
  const focus = 'genres|genre:genre-procedural';
  const hood = M.neighbourhood(model, focus, 1);
  const comp = M.compose(model, atlas, hood, 'B', {width: 846, height: 630, z: 1});
  const phases = model.timeline.map((p) => p.id).filter((id) => hood.levels[id] === 1);
  for (const side of ['left', 'right']) {
    const inColumn = phases.filter((id) => comp.sides[id] === side);
    const byY = inColumn.slice().sort((a, b) => comp.targets[a].y - comp.targets[b].y);
    assert.deepEqual(plain(byY), plain(inColumn), `${side} arc keeps story order`);
  }
});

test('second-order exploration is bounded and reports what it leaves out', () => {
  const M = load();
  const model = M.buildModel(DENSE, 'sha-test');
  const genre = model.concepts.find((x) => x.facet === 'genres').id;
  const hood = M.neighbourhood(model, genre, 2);
  assert.ok(hood.second.length <= 36);
  assert.ok(hood.second.every((id) => hood.levels[id] === 2));
  assert.ok(hood.hiddenSecond >= 0);
});

// Label placement: glyphs never move to make room; a placed label never overprints another label or a
// glyph it may not cover, and the most important label is placed first.
function overlap(a, b) { return a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1; }

test('label placement never overprints and honours priority', () => {
  const M = load();
  const model = M.buildModel(DENSE, 'sha-test');
  const view = {width: 846, height: 630};
  const atlas = M.layoutAtlas(model, {aspect: view.width / view.height, view});
  const again = M.layoutAtlas(M.buildModel(DENSE, 'sha-test'), {aspect: view.width / view.height, view});
  assert.deepEqual(plain(again.positions), plain(atlas.positions), 'viewport-aware layout is deterministic');
  const cam = M.restCamera(atlas, view);
  assert.ok((atlas.width - 150) * cam.z <= view.width, 'the whole story fits the stage at rest');
  const screen = (p) => ({x: (p.x - cam.cx) * cam.z + view.width / 2, y: (p.y - cam.cy) * cam.z + view.height / 2});
  const obstacles = [], items = [];
  for (const cn of model.concepts) {
    const a = screen(atlas.positions[cn.id]);
    obstacles.push({rect: {x0: a.x - 5, y0: a.y - 5, x1: a.x + 5, y1: a.y + 5}, owner: cn.id, soft: cn.tier === 2});
    if (cn.tier === 1) items.push({id: cn.id, x: a.x, y: a.y, gap: 8, priority: cn.degree, overSoft: 'fallback',
      places: ['e', 'w', 'se', 'ne', 'sw', 'nw', 's', 'n'], variants: [{key: 0, w: 96, h: 26}]});
  }
  const bounds = {x0: 4, y0: 4, x1: view.width - 4, y1: view.height - 4};
  const placed = M.placeLabels(items, obstacles, bounds);
  assert.deepEqual(plain(M.placeLabels(items, obstacles, bounds)), plain(placed), 'placement is deterministic');
  const rects = Object.entries(placed).filter(([, r]) => r).map(([id, r]) => ({id, ...r.rect}));
  assert.ok(rects.length > items.length / 2, `most landmarks are named at rest (${rects.length} of ${items.length})`);
  for (let i = 0; i < rects.length; i++) {
    for (let j = i + 1; j < rects.length; j++) assert.ok(!overlap(rects[i], rects[j]), `${rects[i].id} / ${rects[j].id}`);
    for (const o of obstacles) if (!o.soft && o.owner !== rects[i].id) assert.ok(!overlap(rects[i], o.rect), `${rects[i].id} covers ${o.owner}`);
    assert.ok(rects[i].x0 >= bounds.x0 && rects[i].x1 <= bounds.x1 && rects[i].y0 >= bounds.y0 && rects[i].y1 <= bounds.y1);
  }
  // Two labels competing for one place: the more important one keeps it, the other moves aside or stays quiet.
  const duel = M.placeLabels([
    {id: 'minor', x: 100, y: 100, gap: 6, priority: 1, places: ['e'], variants: [{key: 0, w: 80, h: 20}]},
    {id: 'major', x: 100, y: 100, gap: 6, priority: 9, places: ['e'], variants: [{key: 0, w: 80, h: 20}]}], [], null);
  assert.equal(duel.major.place, 'e');
  assert.equal(duel.minor, null);
  // Faded furniture ('hood') may be covered only by the focus neighbourhood itself.
  const furniture = [{rect: {x0: 0, y0: 90, x1: 200, y1: 110}, owner: 'ui', soft: 'hood'}];
  const ambient = M.placeLabels([{id: 'a', x: 50, y: 100, gap: 6, priority: 1, overSoft: 'fallback', places: ['e'],
    variants: [{key: 0, w: 60, h: 18}]}], furniture, null);
  const near = M.placeLabels([{id: 'n', x: 50, y: 100, gap: 6, priority: 1, overSoft: true, places: ['e'],
    variants: [{key: 0, w: 60, h: 18}]}], furniture, null);
  assert.equal(ambient.a, null);
  assert.equal(near.n.place, 'e');
});

// The Focused Constellation presents the phases it is recorded with in recorded story order: left to right
// along the rail on a wide stage, top to bottom in the phone list. Nothing is ordered by nearness.
test('constellation phases follow recorded story chronology', () => {
  const M = load();
  const model = M.buildModel(DENSE, 'sha-test');
  const atlas = M.layoutAtlas(model, {aspect: 1.4});
  const story = (id) => model.timeline.findIndex((p) => p.id === id);
  for (const genre of model.concepts.filter((x) => x.facet === 'genres')) {
    const hood = M.neighbourhood(model, genre.id, 1);
    const phases = hood.first.filter((id) => model.byId[id].facet === 'timeline');
    if (phases.length < 2) continue;
    const wide = M.compose(model, atlas, hood, 'B', {width: 1068, height: 640, z: 1});
    assert.deepEqual(plain(wide.rail), [...phases].sort((a, b) => story(a) - story(b)), `${genre.id}: rail in story order`);
    const xs = wide.rail.map((id) => wide.targets[id].x);
    assert.ok(xs.every((x, i) => i === 0 || x > xs[i - 1]), `${genre.id}: rail runs left to right`);
    const phone = M.compose(model, atlas, hood, 'B', {width: 390, height: 520, z: 1});
    const ys = [...phases].sort((a, b) => story(a) - story(b)).map((id) => phone.targets[id].y);
    assert.ok(ys.every((y, i) => i === 0 || y > ys[i - 1]), `${genre.id}: phone list in story order`);
  }
});

// Presentation drops only a leading kind that repeats the interface; recorded titles and relations stay as recorded.
test('presented names drop only redundant kind prefixes, and Book headings read the recorded scope', () => {
  const M = load();
  const model = M.buildModel(DENSE, 'sha-test');
  const relations = JSON.stringify(model.relations);
  const byTitle = (t) => model.concepts.find((x) => x.recordTitle === t);
  assert.equal(byTitle('Trope: The Bought Seal').name, 'The Bought Seal');
  assert.equal(byTitle('Theme: A Signature Is Not a Proof').name, 'A Signature Is Not a Proof');
  assert.equal(byTitle('Crossing Public Engine: Use as the Real Test').name, 'Crossing Public Engine: Use as the Real Test');
  // A name is the recorded title, its words after a redundant kind, or (reader emotions) the title with its recorded role.
  for (const cn of model.concepts) {
    const rec = cn.recordTitle.toLowerCase(), name = cn.name.toLowerCase();
    assert.ok(rec.endsWith(name) || name.startsWith(rec + ' · '), `${cn.id} keeps its recorded words`);
  }
  assert.equal(JSON.stringify(model.relations), relations);
  assert.deepEqual(plain(M.bookScope('opening_books_duration_unknown')), {text: 'Opening Books', durationUnknown: true});
  assert.deepEqual(plain(M.bookScope('book_12')), {text: 'Book 12', durationUnknown: false});
  assert.deepEqual(plain(M.bookScope('books_13_14')), {text: 'Books 13–14', durationUnknown: false});
  assert.equal(M.bookScope(undefined).text, 'Whole story');
  const atlas = M.layoutAtlas(model, {aspect: 1.4});
  assert.ok(atlas.books.every((b) => !/duration|_/i.test(b.label)), 'no raw scope tokens in Book headings');
});

test('narrative structure and story pathways state only recorded facts, never degree', () => {
  const M = load();
  const dense = M.buildModel(DENSE, 'sha');
  const s = M.narrativeStructure(dense);
  // Counterexample: the governing genre is not the most connected, and roles still follow the contract.
  const fixture = structuredClone(SMALL);
  const gov = fixture.genre_contracts.find((g) => g.role === 'governing');
  const sup = fixture.genre_contracts.find((g) => g.role === 'supporting');
  fixture.links = fixture.links.filter((l) => l.source !== gov.genre_node_id && l.target !== gov.genre_node_id);
  for (let i = 0; i < 12; i += 1) fixture.links.push({id: 'extra-' + i, source: sup.genre_node_id, target: fixture.nodes[i % fixture.nodes.length].id, function: 'recorded test link ' + i});
  const fm = M.buildModel(fixture, 'sha');
  const govId = 'genres|genre:' + gov.genre_node_id, supId = 'genres|genre:' + sup.genre_node_id;
  assert.ok(fm.byId[supId].degree > fm.byId[govId].degree);
  const fs = M.narrativeStructure(fm);
  assert.deepEqual(plain(fs.governing), [govId]);
  assert.equal(fs.roles[supId].role, 'supporting');
  assert.equal(fs.roles[govId].sourceRef, 'genre_contracts/' + gov.genre_node_id + '/role');
  // Structural anchor from recorded parent_id only; interpretations stay agent readings.
  assert.ok(s.anchors.includes('structure|structure-node:engine-risk-transfer'));
  assert.equal(s.contains['structure|structure-node:engine-risk-transfer'].length, 8); // 6 engines + 2 tropes record it as parent
  for (const list of Object.values(s.interpretations)) for (const it of list) assert.equal(it.status, 'agent interpretation');
  // Every pathway segment resolves to a recorded relation; unsupported phases are 'none', not inferred.
  for (const cn of dense.concepts) {
    const p = M.storyPathway(dense, cn.id);
    for (const ph of p.phases) {
      for (const r of ph.relations) assert.ok(dense.relById[r], r);
      for (const l of ph.locals) assert.ok(dense.relById[l.relation] && dense.byId[l.id]);
      if (ph.status === 'none') assert.equal(ph.relations.length + ph.locals.length + ph.evidence.length, 0);
      // Every occurrence names the record that states it.
      for (const e of ph.evidence) assert.ok(resolve(DENSE, e.sourceRef.split('#')[0]) !== undefined, e.sourceRef);
      if (ph.phaseRole) assert.ok(resolve(DENSE, ph.phaseRole.sourceRef));
    }
  }
  // Civic daily-life: activated in phases 1, 5, 8, 9 and listed with a role in 2 and 4; background to governing.
  const civic = M.storyPathway(dense, 'genres|genre:genre-civic-life');
  assert.deepEqual(plain(civic.phases.map((x) => x.status === 'recorded' ? 1 : 0)), [1, 1, 0, 1, 1, 0, 0, 1, 1]);
  assert.deepEqual(plain(civic.phases.map((x) => x.phaseRole && x.phaseRole.role)),
    ['background', 'background', null, 'background', 'locally_dominant', null, null, 'supporting', 'governing']);
  assert.deepEqual(plain(civic.phases[1].kinds), ['role']);
  assert.deepEqual(plain(civic.phases[0].kinds), ['relation', 'role']);
  // Recorded parallel phases are carried with each phase, from either side's record.
  assert.deepEqual(plain(civic.phases[0].parallel), ['timeline|phase:phase-bought-seal']);
  assert.deepEqual(plain(civic.phases[1].parallel), ['timeline|phase:phase-first-signature']);
  assert.deepEqual(plain(civic.phases[2].parallel), []);
  // The central mechanism has recorded structure but no phase records it: no pathway, not 'absent'.
  const engine = M.storyPathway(dense, 'structure|structure-node:engine-risk-transfer');
  assert.equal(engine.available, false);
  assert.ok(engine.phases.every((x) => x.status === 'none'));
  // A function recorded inside one phase occurs there only.
  const local = dense.concepts.find((x) => x.tier === 2 && x.phaseId);
  assert.equal(M.storyPathway(dense, local.id).recorded, 1);
});

function loadWithActions() {
  const sandbox = {window: {}};
  runInNewContext(read(new URL('studio_explanations.js', browser)), sandbox);
  runInNewContext(read(new URL('studio_atelier_model.js', browser)), sandbox);
  runInNewContext(read(new URL('studio_architecture_graph_actions.js', browser)), sandbox);
  return {M: sandbox.window.AuteurStudioAtelierModel, A: sandbox.window.AuteurStudioGraphActions};
}

test('every atlas concept hands its own recorded source to the inquiry contract, at its own precision', () => {
  const {M, A} = loadWithActions();
  for (const c of [SMALL, DENSE]) {
    const model = M.buildModel(c, 'sha');
    let anchored = 0;
    for (const cn of model.concepts) {
      const s = M.sourceAnchor(model, cn.id);
      assert.ok(s.anchor, cn.id + ' has no anchor: ' + s.reason);
      // The Studio's own resolver accepts it, so the server will too.
      const view = A.projectGraphSelection(c, [plain(s.anchor)]);
      assert.equal(view.anchors.length, 1);
      anchored += 1;
    }
    assert.equal(anchored, model.concepts.length);
  }
  const model = M.buildModel(DENSE, 'sha');
  // A contract trope function is one entry, not the whole list, and not the trope node it repeats.
  const fn = plain(M.sourceAnchor(model, 'tropes|trope:genre-craft-thriller:0'));
  assert.deepEqual(fn.anchor, {kind: 'genre_contract', id: 'genre-craft-thriller', field: 'trope_functions', index: 0});
  assert.equal(fn.precision, 'entry');
  assert.equal(fn.quote, 'the first crosser');
  assert.equal(fn.sourceRef, 'genre_contracts/genre-craft-thriller/trope_functions/0');
  const node = plain(M.sourceAnchor(model, 'tropes|trope-node:trope-first-crosser'));
  assert.deepEqual(node.anchor, {kind: 'node', id: 'trope-first-crosser'});
  // A phase-local function is addressed through its recorded activation.
  const local = plain(M.sourceAnchor(model, 'tropes|phase-trope:phase-first-crosser:genre-craft-thriller:0'));
  assert.deepEqual(local.anchor, {kind: 'phase', id: 'phase-first-crosser',
    reference: {field: 'genre_activations', target_kind: 'genre_contract', target_id: 'genre-craft-thriller'}});
  assert.equal(local.precision, 'activation');
  assert.deepEqual(plain(M.sourceAnchor(model, 'structure|structure:genre-procedural:1').anchor),
    {kind: 'genre_contract', id: 'genre-procedural', field: 'structural_pattern'});
  assert.equal(M.sourceAnchor(model, 'nothing|here').anchor, null);
});

test('a phase that activates one genre twice is addressed as the whole activation list, and says so', () => {
  const {M, A} = loadWithActions();
  const c = JSON.parse(JSON.stringify(DENSE));
  const phase = c.phases.find((p) => p.id === 'phase-first-crosser');
  phase.genre_activations.push(JSON.parse(JSON.stringify(phase.genre_activations.find((a) => a.genre_node_id === 'genre-craft-thriller'))));
  const model = M.buildModel(c, 'sha');
  const s = plain(M.sourceAnchor(model, 'tropes|phase-trope:phase-first-crosser:genre-craft-thriller:0'));
  assert.deepEqual(s.anchor, {kind: 'phase', id: 'phase-first-crosser', field: 'genre_activations'});
  assert.equal(s.precision, 'field');
  assert.equal(A.projectGraphSelection(c, [s.anchor]).anchors.length, 1);
});

test('a revision delta compares recorded identities, never titles, and reports what the records changed', () => {
  const M = load();
  const before = M.buildModel(DENSE, 'one');
  const c = JSON.parse(JSON.stringify(DENSE));
  const craft = c.genre_contracts.find((g) => g.genre_node_id === 'genre-craft-thriller');
  craft.trope_functions[0] = 'a stranger crossing tests the craftsman before any certificate does';
  craft.trope_function_refs = [{function_index: 0, trope_node_id: 'trope-first-crosser'}];
  const after = M.buildModel(c, 'two');
  const d = plain(M.revisionDelta(before, after));
  assert.deepEqual(d.added, []);
  assert.deepEqual(d.removed, []);
  // The contract's own record changed too (its list and its references); every recorded field counts.
  assert.deepEqual(d.reworded.map((x) => [x.id, x.titleChanged, x.positional, x.fields]), [
    ['genres|genre:genre-craft-thriller', false, false, ['trope_functions', 'trope_function_refs']],
    ['tropes|trope:genre-craft-thriller:0', true, true, []]]);
  assert.equal(d.reworded[1].before, 'the first crosser');
  assert.deepEqual(d.relationsAdded.map((r) => [r.from, r.verb, r.to, r.sourceRef]), [[
    'tropes|trope:genre-craft-thriller:0', 'realises trope', 'tropes|trope-node:trope-first-crosser',
    'genre_contracts/genre-craft-thriller/trope_function_refs/0']]);
  assert.deepEqual(d.relationsRemoved, []);
  assert.deepEqual(Object.keys(d.touched).sort(), ['genres|genre:genre-craft-thriller',
    'tropes|trope-node:trope-first-crosser', 'tropes|trope:genre-craft-thriller:0']);
  // The same records under a new request SHA are no change at all.
  const same = plain(M.revisionDelta(before, M.buildModel(DENSE, 'three')));
  assert.equal(same.reworded.length + same.added.length + same.relationsAdded.length + same.relationsRemoved.length, 0);
});

test('fields the atlas does not draw still count as changes, and the layout basis follows story order', () => {
  const M = load();
  const before = M.buildModel(DENSE, 'one');
  const c = JSON.parse(JSON.stringify(DENSE));
  c.genre_contracts.find((g) => g.genre_node_id === 'genre-procedural').payoff_expectations[0] = 'a different payoff';
  const d = plain(M.revisionDelta(before, M.buildModel(c, 'two')));
  assert.deepEqual(d.reworded.map((x) => [x.id, x.fields]), [['genres|genre:genre-procedural', ['payoff_expectations']]]);
  assert.equal(M.layoutBasis(before), M.layoutBasis(M.buildModel(c, 'two')));
  // Reordering phases changes what the layout is computed from, so the atlas cannot be kept as it was.
  const r = JSON.parse(JSON.stringify(DENSE));
  const first = r.phases.find((p) => p.order === 1), last = r.phases.reduce((a, b) => (a.order > b.order ? a : b));
  [first.order, last.order] = [last.order, first.order];
  assert.notEqual(M.layoutBasis(before), M.layoutBasis(M.buildModel(r, 'three')));
  assert.ok(plain(M.revisionDelta(before, M.buildModel(r, 'three'))).reworded.some((x) => x.fields.includes('order')));
});

test('a reordered list is reported per position, never as the same entry moving', () => {
  const M = load();
  const before = M.buildModel(DENSE, 'one');
  const c = JSON.parse(JSON.stringify(DENSE));
  const proc = c.genre_contracts.find((g) => g.genre_node_id === 'genre-procedural');
  proc.trope_functions = [proc.trope_functions[1], proc.trope_functions[0], proc.trope_functions[2]];
  const d = plain(M.revisionDelta(before, M.buildModel(c, 'two')));
  const entries = d.reworded.filter((x) => x.positional).map((x) => [x.id, x.before, x.after]);
  assert.deepEqual(entries, [
    ['tropes|trope:genre-procedural:0', 'signing as public exposure', 'the first crosser'],
    ['tropes|trope:genre-procedural:1', 'the first crosser', 'signing as public exposure']]);
  assert.ok(d.reworded.every((x) => !('moved' in x)));  // no identity is inferred from equal words
});
