/** Read-only, actionable Book design coverage — never a quality or acceptance score. */
const arr=v=>Array.isArray(v)?v:[];
export function reviewFullArchitecture(projection) {
  if(!projection||typeof projection!=='object')throw Error('Full architecture projection required');
  const items=[];
  const add=(id,kind,state,why,focusTarget=null,blocksReadiness=false,sourceRefs=[])=>{
    items.push({id,kind,state,why,focusTarget,blocksReadiness,sourceRefs});
  };
  const working=arr(projection.storySpecific);
  const reader=working.find(x=>x.role==='emotion')||projection.identity?.accepted?.value;
  const struct=working.find(x=>x.role==='structure')||projection.structure?.accepted;
  add('reader-intention','author_decision',reader?'specified':'open_author_decision',
    reader?'The author has a reader-facing working or accepted intention.':'Choose the reader experience this Book should aim to create.',
    working.find(x=>x.role==='emotion')?.itemId||null,!reader);
  add('book-structure','author_decision',struct?'specified':'open_author_decision',
    struct?'The author has a working or accepted Book-level structural idea.':'Specify a renewable narrative engine or Book-level structure.',
    working.find(x=>x.role==='structure')?.itemId||null,!struct);
  for(const genre of arr(projection.genreViews)) {
    const verified=genre.packCoverage?.status==='verified_pack';
    add(`genre-evidence:${genre.genreId}`,'source_coverage',verified?'specified':'not_established',
      verified?'Versioned, applicable genre evidence is supplied.':'Available evidence does not establish verified Pack morphology for this genre.',
      `genre:${genre.genreId}`,false,genre.morphology.map(m=>m.sourceRef));
  }
  for(const item of working) {
    if(item.needsReview) add(`stale-origin:${item.itemId}`,'stale_origin','open_author_decision',
      'A source revision or upstream decision changed. Review this author-owned idea before relying on its previous source.',
      item.itemId,true,item.sourceRef?[item.sourceRef]:[]);
    if(['structure','trope','theme','conflict'].includes(item.role)){
      add(`working-link:${item.itemId}`,'author_connection',item.linkedRefs.length?'integrated':'specified',
        item.linkedRefs.length?'This authored idea is connected through an explicit working link.':
          'The author has this working idea, but has not yet recorded how it connects to other authored decisions.',
        item.itemId,false,item.linkedRefs);
    }
  }
  for(const issue of arr(projection.issues)){
    add(`question:${issue.id}`,'author_decision','open_author_decision',issue.why,issue.focusTarget||null,false,
      issue.sourceRef?[issue.sourceRef]:[]);
  }
  // Readiness is a decision to review an authored Book design; not acceptance.
  // Require one explicit connection between authored reader goal and structural idea.
  const readId=working.find(x=>x.role==='emotion')?.itemId;
  const structId=working.find(x=>x.role==='structure')?.itemId;
  const connects=arr(projection.structure?.workingLinks).some(l=>
    (l.source===readId&&l.target===structId)||(l.target===readId&&l.source===structId));
  const blocking=items.some(x=>x.blocksReadiness);
  const ready=!!reader&&!!struct&&(connects||!!(projection.identity?.accepted?.value&&projection.structure?.accepted))&&!blocking;
  return {status:ready?'ready_for_author_review':'draft',items,
    summary:ready?'Book Identity and Structure have an explicit authored connection and are ready for author review, not automatically accepted.':
      'The working Book design has open author decisions or unintegrated reader experience and structure. Scene planning remains optional.',
    sourceFingerprint:structuredClone(projection.fingerprint)};
}
