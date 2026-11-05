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
