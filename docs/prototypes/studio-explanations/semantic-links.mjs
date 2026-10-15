/** Navigation projection of existing proposal relationships. Never infer an extra edge. */
const same = (a,b) => a?.kind===b?.kind && a?.id===b?.id;
const itemRef = id => ({kind:'item',id});
const genreRef = id => ({kind:'genre',id});

export function deriveSemanticLinks(model) {
  const links=[];
  for (const item of model.items) {
    for (const relation of item.genre_links || []) {
      const from=genreRef(relation.genre_id),to=itemRef(item.id);
      links.push({id:`genre:${relation.genre_id}:${item.id}:${relation.source_ref}`,
        originalFrom:from,originalTo:to,verb:relation.relation,
        explanation:`${model.genres.find(g=>g.id===relation.genre_id)?.label} ${relation.relation} ${item.label}.`,
        sourceRef:relation.source_ref,sourceKind:relation.source_kind,
        supportStatus:relation.source_kind==='model_inference'?'hypothesis':'source_backed',
        ruleStrength:relation.rule_strength ?? null,coverage:relation.coverage,
        ownerGenreId:relation.genre_id});
    }
  }
  for (const [n,edge] of model.proposal_edges.entries()) {
    links.push({id:`edge:${n}:${edge.source_ref}`,originalFrom:itemRef(edge.source),originalTo:itemRef(edge.target),
      verb:edge.verb,explanation:edge.explanation,sourceRef:edge.source_ref,
      sourceKind:'proposal_edge',supportStatus:edge.support_status,ruleStrength:null});
  }
  return links;
}

/** A reverse traversal refers to the SAME source edge, never a new causal claim. */
export function linksForFocus(links,focus) {
  if(!focus) return [];
  const output=[];
  for(const link of links){
    const forward=same(focus,link.originalFrom),reverse=same(focus,link.originalTo);
    if(!forward&&!reverse)continue;
    output.push({...link,from:focus,
      target:forward?link.originalTo:link.originalFrom,
      verb:forward?link.verb:(link.originalFrom.kind==='genre'
        ? ({uses:'is used by',supports:'is supported by',adapts:'is adapted by'}[link.verb]||`has recorded relation “${link.verb}” with`)
        : `receives “${link.verb}” from`),
      direction:forward?'forward':'reverse'});
  }
  return output;
}

export function preferredPerspective(model,target) {
  if(target?.kind==='genre')return model.genres.some(g=>g.id===target.id)?'anatomy':null;
  if(target?.kind!=='item')return null;
  const item=model.items.find(n=>n.id===target.id);
  if(!item)return null;
  if(item.type==='trope')return 'comparison';
  if(item.type==='engine'||item.type==='structure')return 'mechanism';
  return 'overview';
}
