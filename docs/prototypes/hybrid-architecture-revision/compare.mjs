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
    throw new Error(label + ' must be an ArchitectureCandidate v2 with nodes');
  }
  for (const [kind, collection, idKey] of COLLECTIONS) {
    const entries = candidate[collection];
    if (!Array.isArray(entries)) throw new Error(label + '.' + collection + ' is not an array');
    const seen = new Set();
    for (const entry of entries) {
      const id = entry?.[idKey];
      if (typeof id !== 'string' || !id || seen.has(id)) {
        throw new Error('Invalid or duplicate ' + kind + ' source identity in ' + label);
      }
      seen.add(id);
    }
  }
  if (typeof candidate.summary !== 'string') throw new Error(label + '.summary is missing');
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
      items.push({kind,id,key:kind + ':' + id,change,
        beforeRecord:a?.record ?? null, afterRecord:b?.record ?? null,
        beforeSourceRef:a ? collection + '/' + a.index : null,
        afterSourceRef:b ? collection + '/' + b.index : null,
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
    'Author-declared emotional target ' + item.id + ' is ' + item.change + '; inspect its recorded fields.');
  return {status:'ready',authority:'working_architecture_comparison_not_story_impact',
    beforeRequestSha,afterRequestSha,requestedChange,
    acceptedConstraints:Array.isArray(acceptedConstraints)?acceptedConstraints:[],
    summary:{...counts,byKind,authorDeclaredWarnings},items,
    graph:{before:{nodes:before.nodes,links:before.links,genre_interactions:before.genre_interactions},
      after:{nodes:after.nodes,links:after.links,genre_interactions:after.genre_interactions}},
    beforeCandidate:before,afterCandidate:after};
}
export {COLLECTIONS};
