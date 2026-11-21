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
