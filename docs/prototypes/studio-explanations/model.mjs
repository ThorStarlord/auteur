/** Pure, read-only, evidence-preserving projection shared by all three visual experiments. */
const perspectives = new Set(['overview', 'anatomy', 'comparison', 'mechanism']);
const treatments = new Set(['proposed_adoption', 'proposed_adaptation', 'proposed_story_specific', 'proposed_subversion', 'unresolved']);
const statuses = new Set(['source_backed', 'hypothesis']);

export function normalizeEvidence(story, genreEvidence) {
  if (story?.authority_status !== 'DERIVED / NOT CANON') throw new Error('Only noncanonical candidates are allowed');
  const byId = new Map();
  const genres = story.genres.map(g => {
    if (!g.id || byId.has(`g:${g.id}`)) throw new Error(`Duplicate genre ${g.id}`);
    byId.set(`g:${g.id}`, true);
    const evidence = genreEvidence[g.id] || { coverage: 'missing', pack_version: null, source_ref: 'No curated genre source' };
    return { ...g, coverage: evidence.coverage, pack_version: evidence.pack_version ?? null,
      source_ref: evidence.source_ref, legacy_rule_field: evidence.legacy_rule_field ?? null,
      coverage_note: evidence.note || 'No independently verified genre rules available.' };
  });
  const genreById = new Set(genres.map(g => g.id));
  const seen = new Set();
  const items = story.nodes.map(n => {
    if (!n.id || seen.has(n.id)) throw new Error(`Duplicate node ${n.id}`);
    if (!treatments.has(n.story_treatment)) throw new Error(`Invalid treatment ${n.id}`);
    if (!n.source_ref) throw new Error(`Missing node provenance ${n.id}`);
    seen.add(n.id);
    return { ...n, genre_links: [] };
  });
  const itemById = new Map(items.map(n => [n.id, n]));
  for (const link of story.genre_links || []) {
    if (!itemById.has(link.node_id) || !genreById.has(link.genre_id)) throw new Error(`Unknown genre link ${link.node_id}/${link.genre_id}`);
    if (!link.source_ref) throw new Error('Genre relationship requires source_ref');
    const coverage = genres.find(g => g.id === link.genre_id).coverage;
    if (link.source_kind === 'model_inference' && link.rule_strength !== null) throw new Error('Inference cannot claim source-backed rule strength');
    if (link.source_kind === 'legacy_contract' && link.rule_strength !== null) throw new Error('Legacy contracts do not confer Genre Pack rule strengths');
    if (link.source_kind === 'legacy_contract' && coverage !== 'legacy_contract') throw new Error('Provenance coverage mismatch for legacy contract');
    if (link.source_kind === 'genre_pack' && coverage !== 'pack_backed') throw new Error('Provenance coverage mismatch for genre pack');
    if (link.rule_strength !== null && coverage !== 'pack_backed') throw new Error('Unverified source cannot assign genre rule strength');
    itemById.get(link.node_id).genre_links.push({ ...link, coverage });
  }
  const proposal_edges = (story.proposal_edges || []).map(edge => {
    for (const key of ['source', 'target']) if (!itemById.has(edge[key])) throw new Error(`Unknown edge endpoint ${edge[key]}`);
    if (!edge.source_ref || !statuses.has(edge.support_status)) throw new Error('Edge missing warrant/status');
    return { ...edge };
  });
  return { story_id: story.story_id, title: story.title, vision: story.vision,
    scenario: story.scenario, fixture_note: story.fixture_note, authority_status: story.authority_status,
    illustrative: true, genres, items, proposal_edges, phases: (story.phases || []).map(p => ({ ...p })) };
}

export function entriesForPerspective(model, perspective) {
  if (!perspectives.has(perspective)) throw new Error(`Unknown perspective ${perspective}`);
  if (perspective === 'anatomy') return model.genres;
  if (perspective === 'comparison') return model.items.filter(n => n.type === 'trope');
  if (perspective === 'mechanism') return model.items.filter(n => n.type === 'trope' || n.type === 'engine' || n.type === 'structure');
  return model.items;
}

export function connectionsForSelection(model, itemId) {
  return model.proposal_edges.filter(edge => edge.source === itemId || edge.target === itemId);
}
