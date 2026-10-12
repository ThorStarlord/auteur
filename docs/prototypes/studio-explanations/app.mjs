import { normalizeEvidence, entriesForPerspective, connectionsForSelection } from './model.mjs';
const $ = id => document.getElementById(id);
const state = { story: 'paladin', perspective: 'overview', selected: null, genre: null, model: null, history: [], selectionHistory: [] };
const sourceCache = {};
const modes = {
  overview: 'A spatial index of source-scoped proposed architecture elements.',
  anatomy: 'How a genre conventionally aims to deliver its reader promise.',
  comparison: 'What the genre might supply versus what this story proposes to do.',
  mechanism: 'Trace a bounded structural relationship and its intended effect.'
};
const el = (tag, className, text) => {
  const e = document.createElement(tag); if (className) e.className = className;
  if (text !== undefined) e.textContent = text; return e;
};
function selectedItem() { return state.model?.items.find(x => x.id === state.selected) || null; }
function status(msg) { $('provenance-summary').textContent = msg; }
function focusItem(id) {
  if (!state.model.items.some(n => n.id === id)) return;
  if (state.selected && state.selected !== id) state.selectionHistory.push(state.selected);
  if (state.selectionHistory.length > 12) state.selectionHistory.shift();
  state.selected = id;
  $('detail-panel').hidden = true;
  $('back-selection').hidden = !state.selectionHistory.length;
}
function selectItem(id) {
  const node = state.model.items.find(x => x.id === id);
  if (!node) return;
  state.selected = id; showDetail(node);
}
function showDetail(node) {
  $('detail-panel').hidden = false;
  $('detail-title').textContent = node.label;
  $('detail-description').textContent = node.description;
  $('detail-source').textContent = `Source: ${node.source_ref} · ${node.derivation.replaceAll('_', ' ')} · ${node.certainty} · DERIVED / NOT CANON`;
  const links = $('detail-relations'); links.replaceChildren();
  const related = node.genre_links || [];
  if (related.length) links.append(el('div','small-label','GENRE-RELATIVE ROLES'));
  for (const g of related) {
    const source = state.model.genres.find(x => x.id === g.genre_id);
    const p = el('p','source-note',`${source?.label || g.genre_id}: ${g.relation} · ${g.coverage.replaceAll('_',' ')} · ${g.source_ref}`);
    links.append(p);
  }
  for (const edge of connectionsForSelection(state.model, node.id)) {
    const neighborId = edge.source === node.id ? edge.target : edge.source;
    const other = state.model.items.find(x => x.id === neighborId);
    const button = el('button','',`${edge.verb} → ${other.label}`);
    button.type = 'button'; button.addEventListener('click', () => selectItem(neighborId)); links.append(button);
  }
  $('detail-panel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
function renderOverview(root) {
  root.append(el('h2','stage-heading','The story at a glance'));
  root.append(el('p','stage-subtitle','One working proposal, grouped by meaning. Select an element to follow its documented—or explicitly hypothetical—links.'));
  root.append(el('div','overview-note',`${state.model.title} — ${state.model.vision}`));
  const grid = el('div','overview-grid');
  const groups = [['Genres', state.model.genres],['Tropes',state.model.items.filter(x=>x.type==='trope')],
    ['Narrative engines',state.model.items.filter(x=>['engine','structure'].includes(x.type))],
    ['Experience & framing',state.model.items.filter(x=>['emotion','framing'].includes(x.type))]];
  for (const [title, nodes] of groups) {
    const col = el('section','map-column'); col.append(el('h3','',title));
    for (const n of nodes) {
      const button = el('button',`node-button ${n.type || 'genre'}`);
      button.type = 'button'; button.append(el('strong','',n.label), el('small','',n.story_treatment?.replaceAll('_',' ') || n.role));
      button.setAttribute('aria-pressed',String(n.id===state.selected));
      button.addEventListener('click',()=>{ if(n.type) selectItem(n.id); else openPerspective('anatomy',null,n.id); });
      col.append(button);
    } grid.append(col);
  }root.append(grid);
}
async function render() {
  const root = $('explanation-main'); root.replaceChildren();
  const mode = state.perspective;
  $('view-description').textContent = modes[mode];
  $('back-overview').hidden = mode === 'overview';
  $('back-selection').hidden = mode === 'overview' || !state.selectionHistory.length;
  for (const b of document.querySelectorAll('[data-perspective]')) {
    const active = b.dataset.perspective === mode;
    b.setAttribute('aria-selected',String(active)); b.tabIndex = active?0:-1;
  }
  if (mode === 'overview') renderOverview(root);
  else {
    const modules = { anatomy:'./views/anatomy.mjs', comparison:'./views/comparison.mjs', mechanism:'./views/mechanism.mjs' };
    try {
      const view = await import(modules[mode]);
      if (state.perspective !== mode) return;
      if (mode === 'anatomy') view.renderAnatomy(root,state.model,state.genre,(id)=>selectItem(id));
      if (mode === 'comparison') view.renderComparison(root,state.model,state.selected,(id)=>selectItem(id),(id)=>focusItem(id));
      if (mode === 'mechanism') view.renderMechanism(root,state.model,state.selected,(id)=>selectItem(id),(id)=>focusItem(id));
    } catch (error) { root.replaceChildren(el('p','empty-state',`This prototype is unavailable: ${error.message}`)); }
  }
}
function openPerspective(mode,id=null,genre=null) {
  if (!modes[mode]) return;
  state.history.push({perspective:state.perspective,selected:state.selected,genre:state.genre});
  state.perspective=mode;
  if (id) state.selected=id;
  if (genre) state.genre=genre;
  if (mode==='comparison' && !state.model.items.some(n=>n.id===state.selected&&n.type==='trope'))
    state.selected=entriesForPerspective(state.model,'comparison')[0]?.id||null;
  if (mode==='mechanism' && !entriesForPerspective(state.model,'mechanism').some(n=>n.id===state.selected))
    state.selected=entriesForPerspective(state.model,'mechanism')[0]?.id||null;
  $('detail-panel').hidden = true;
  render();
}
async function loadStory(storyId) {
  if (!sourceCache[storyId]) {
    const [story,evidence] = await Promise.all([fetch('./fixtures/'+storyId+'.json').then(r=>r.json()),
      fetch('./fixtures/genre-evidence.json').then(r=>r.json())]);
    sourceCache[storyId] = normalizeEvidence(story,evidence);
  }
  state.story=storyId;state.model=sourceCache[storyId];state.selected=null;state.genre=null;state.history=[];state.selectionHistory=[];
  $('detail-panel').hidden = true;
  $('fixture-note').textContent = state.model.fixture_note;
  status('Illustrative fixture · Proposed, not accepted · Missing genre packs explicitly marked');
  await render();
}
for (const b of document.querySelectorAll('[data-perspective]')) {
  b.addEventListener('click',()=>openPerspective(b.dataset.perspective));
  b.addEventListener('keydown',e=>{
    if(!['ArrowRight','ArrowLeft','Home','End'].includes(e.key))return;
    e.preventDefault();const all=[...document.querySelectorAll('[data-perspective]')];
    const i=all.indexOf(b),next=e.key==='Home'?0:e.key==='End'?all.length-1:(i+(e.key==='ArrowRight'?1:-1)+all.length)%all.length;
    all[next].focus();openPerspective(all[next].dataset.perspective);
  });
}
$('story-select').addEventListener('change',e=>loadStory(e.target.value));
$('back-overview').addEventListener('click',()=>openPerspective('overview'));
$('back-selection').addEventListener('click',()=>{
  if (!state.selectionHistory.length) return;
  state.selected=state.selectionHistory.pop();
  $('detail-panel').hidden=true;render();
});
$('close-details').addEventListener('click',()=>{$('detail-panel').hidden=true;$('explanation-main').focus();});
loadStory($('story-select').value).catch(e=>status(`Could not load fixture: ${e.message}`));
