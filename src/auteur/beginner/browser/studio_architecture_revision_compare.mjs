/* Pure, noncanonical comparison of two ArchitectureCandidate v2 snapshots. */
const COLLECTIONS = Object.freeze([
  ['node', 'nodes', 'id'], ['link', 'links', 'id'],
  ['emotion_target', 'emotion_targets', 'id'],
  ['complex_emotion', 'complex_emotions', 'id'],
  ['genre_contract', 'genre_contracts', 'genre_node_id'],
  ['genre_interaction', 'genre_interactions', 'id'], ['phase', 'phases', 'id'],
]);
const SHA = /^[a-f0-9]{64}$/;
const comparable = value => {
  if (Array.isArray(value)) return value.map(comparable);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map(key => [key, comparable(value[key])]));
  }
  return value;
};
const equal = (a, b) => JSON.stringify(comparable(a)) === JSON.stringify(comparable(b));
function validate(candidate, label) {
  if (!candidate || candidate.schema_version !== 2 || !Array.isArray(candidate.nodes)) {
    throw new Error(`${label} must be an ArchitectureCandidate v2 with nodes`);
  }
  for (const [kind, collection, idKey] of COLLECTIONS) {
    const entries = candidate[collection];
    if (!Array.isArray(entries)) throw new Error(`${label}.${collection} is not an array`);
    const seen = new Set();
    for (const entry of entries) {
      const id = entry?.[idKey];
      if (typeof id !== 'string' || !id || seen.has(id)) {
        throw new Error(`Invalid or duplicate ${kind} source identity in ${label}`);
      }
      seen.add(id);
    }
  }
  if (typeof candidate.summary !== 'string') throw new Error(`${label}.summary is missing`);
}
function indexRecords(candidate, collection, idKey) {
  return new Map(candidate[collection].map((record, index) => [record[idKey], {record, index}]));
}
function fieldChanges(before, after) {
  if (!before || !after) return [];
  return [...new Set([...Object.keys(before), ...Object.keys(after)])].sort().flatMap(field => {
    const beforePresent = Object.hasOwn(before, field);
    const afterPresent = Object.hasOwn(after, field);
    if (beforePresent === afterPresent && equal(before[field], after[field])) return [];
    return [{field, beforePresent, afterPresent,
      beforeValue: beforePresent ? before[field] : null,
      afterValue: afterPresent ? after[field] : null}];
  });
}
export function compareArchitectureRevision({before, after, beforeRequestSha, afterRequestSha,
  expectedPriorSha, requestedChange = '', acceptedConstraints = []} = {}) {
  if (![beforeRequestSha, afterRequestSha, expectedPriorSha].every(s => typeof s === 'string' && SHA.test(s))) {
    throw new Error('Valid before, after and expected baseline request SHAs are required');
  }
  if (beforeRequestSha !== expectedPriorSha) throw new Error('Revision baseline request SHA mismatch');
  validate(before, 'Before candidate'); validate(after, 'After candidate');
  const items = [];
  for (const [kind, collection, idKey] of COLLECTIONS) {
    const old = indexRecords(before, collection, idKey);
    const fresh = indexRecords(after, collection, idKey);
    for (const id of new Set([...old.keys(), ...fresh.keys()])) {
      const a = old.get(id), b = fresh.get(id);
      const change = !a ? 'added' : !b ? 'removed' : equal(a.record, b.record) ? 'unchanged' : 'changed';
      items.push({kind,id,key:`${kind}:${id}`,change,
        beforeRecord:a?.record ?? null, afterRecord:b?.record ?? null,
        beforeSourceRef:a ? `${collection}/${a.index}` : null,
        afterSourceRef:b ? `${collection}/${b.index}` : null,
        changedFields:fieldChanges(a?.record,b?.record),
      });
    }
  }
  items.push({kind:'summary',id:'summary',key:'summary:summary',
    change: before.summary === after.summary ? 'unchanged' : 'changed',
    beforeRecord:{summary:before.summary},afterRecord:{summary:after.summary},
    beforeSourceRef:'summary',afterSourceRef:'summary',
    changedFields:before.summary===after.summary?[]:[{field:'summary',beforePresent:true,
      afterPresent:true,beforeValue:before.summary,afterValue:after.summary}]});
  const counts = {added:0,removed:0,changed:0,unchanged:0};
  const byKind = {};
  for (const item of items) {
    counts[item.change] += 1;
    if (!byKind[item.kind]) byKind[item.kind] = {added:0,removed:0,changed:0,unchanged:0};
    byKind[item.kind][item.change] += 1;
  }
  const authorDeclaredWarnings = items.filter(item => item.kind==='emotion_target'
    && item.beforeRecord?.provenance==='author_declared'
    && item.change!=='unchanged').map(item =>
    `Author-declared emotional target ${item.id} is ${item.change}; inspect its recorded fields.`);
  return {status:'ready',authority:'working_architecture_comparison_not_story_impact',
    beforeRequestSha,afterRequestSha,requestedChange,
    acceptedConstraints:Array.isArray(acceptedConstraints)?acceptedConstraints:[],
    summary:{...counts,byKind,authorDeclaredWarnings},items,
    graph:{before:{nodes:before.nodes,links:before.links,genre_interactions:before.genre_interactions},
      after:{nodes:after.nodes,links:after.links,genre_interactions:after.genre_interactions}},
    beforeCandidate:before,afterCandidate:after};
}
export {COLLECTIONS};

/* Stable, read-only graph presentation; never infers semantic edges. */
function edgesFor(candidate, items) {
  const nodes = new Set(candidate.nodes.map(n => n.id));
  const changes = new Map(items.map(i => [i.key, i.change]));
  return [...candidate.links.map(e=>({kind:'link',...e})),
    ...candidate.genre_interactions.map(e=>({kind:'genre_interaction',...e,
      source:e.source_genre_id,target:e.target_genre_id,function:e.mechanism}))]
    .filter(e=>nodes.has(e.source)&&nodes.has(e.target))
    .map(e=>({...e,key:e.kind+':'+e.id,change:changes.get(e.kind+':'+e.id)||'unchanged'}));
}
export function unionGraphLayout(comparison,{columns=6}={}) {
  if (!comparison || comparison.status!=='ready') throw new Error('Ready comparison required');
  if (!Number.isInteger(columns)||columns<1) throw new Error('Positive integer columns required');
  const before=comparison.graph.before,after=comparison.graph.after;
  const ids=[...new Set([...before.nodes.map(n=>n.id),...after.nodes.map(n=>n.id)])].sort();
  const positionsByNodeId=Object.fromEntries(ids.map((id,index)=>[id,
    {x:24+(index%columns)*192,y:24+Math.floor(index/columns)*112}]));
  const status=new Map(comparison.items.map(i=>[i.key,i.change]));
  const project=c=>({nodes:c.nodes.map(n=>({...n,position:positionsByNodeId[n.id],
    key:'node:'+n.id,change:status.get('node:'+n.id)||'unchanged'})),edges:edgesFor(c,comparison.items)});
  return {positionsByNodeId,beforeGraph:project(before),afterGraph:project(after),
    columns,rows:Math.ceil(ids.length/columns)};
}
export function focusedGraphDiff(comparison,{kind,id}={}) {
  if (!comparison || comparison.status!=='ready') throw new Error('Ready comparison required');
  const focus=comparison.items.find(i=>i.kind===kind&&i.id===id);
  if (!focus) throw new Error('Requested typed focus not found');
  const oneHop=(candidate,side)=>{
    const item=side==='before'?focus.beforeRecord:focus.afterRecord;
    if (!item) return {nodes:[],edges:[]};
    const graph=side==='before'?comparison.graph.before:comparison.graph.after;
    const edges=edgesFor(graph,comparison.items);
    const focusEdges=kind==='node'?edges.filter(e=>e.source===id||e.target===id)
      : (kind==='link'||kind==='genre_interaction')?edges.filter(e=>e.kind===kind&&e.id===id):[];
    const ids=new Set(focusEdges.flatMap(e=>[e.source,e.target]));
    if (kind==='node') ids.add(id);
    return {nodes:graph.nodes.filter(n=>ids.has(n.id)),edges:focusEdges};
  };
  return {focus,beforeNeighborhood:oneHop(comparison,'before'),
    afterNeighborhood:oneHop(comparison,'after'),fieldChanges:focus.changedFields,
    missingSide:!focus.beforeRecord?'before':!focus.afterRecord?'after':null};
}