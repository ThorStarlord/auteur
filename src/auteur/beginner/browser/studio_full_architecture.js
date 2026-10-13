/* Generated from tested Full Architecture ESM sources. SHA256 4dd151034879399048fd01baa7a6a085963abce9716ca7c1f58c2df47d0f05b4
   Regenerate: node scripts/build_full_architecture_bundle.mjs */
(function(global){
'use strict';
/** Deterministic, read-only Full Architecture projection. No canonical or provider writes. */
const asArray=v=>Array.isArray(v)?v:[];
const copy=v=>v==null?v:structuredClone(v);
const nonempty=v=>typeof v==='string'&&v.trim().length>0;
const ref=(prefix,id)=>`${prefix}/${id}`;
const labels=new Set(['joy','sadness','fear','anger','disgust','surprise']);

function sourceFingerprint(input={}) {
  return {
    requestSha: input.requestSha||null,
    canvasRevision: Number.isInteger(input.canvasRevision)?input.canvasRevision:null,
    acceptedIdentityRevision: input.acceptedIdentity?.revision??null,
    acceptedStructureRevision: input.acceptedStructure?.revision??null,
    packs: asArray(input.genreEvidence).filter(e=>e?.pack).map(e=>({genreId:e.genreId,
      packId:e.pack.pack_id||null,version:e.pack.version||null,
      contentHash:e.contentHash||null,applicability:e.applicability||null})),
  };
}

function packIsVerified(e) {
  return !!e&&nonempty(e.genreId)&&e.applicability==='applicable'&&
    e.verified===true&&/^[a-f0-9]{64}$/.test(e.contentHash||'')&&
    nonempty(e.pack?.pack_id)&&nonempty(e.pack?.version);
}

function fromPack(e) {
  const pack=e.pack, base=`genre_packs/${pack.pack_id}/${pack.version}`;
  const morphology=[];
  function push(list,kind,name,desc='description'){
    asArray(pack[list]).forEach((item,i)=>{
      if(!nonempty(item[name]))return;
      morphology.push({id:`${e.genreId}:${list}:${item.id||i}`,title:item[name],detail:item[desc]||'',
        kind,genreId:e.genreId,ruleStrength:item.strength||null,
        sourceRef:`${base}/${list}/${item.id||i}`,sourceKind:'versioned_pack',authority:'verified_pack',
        contentHash:e.contentHash,packId:pack.pack_id,packVersion:pack.version});
    });
  }
  push('audience_promises','reader_promise','description');
  push('emotional_targets','emotion','name');
  push('core_conventions','trope','description');
  push('narrative_engines','engine','name');
  push('escalation_patterns','structure','name');
  push('resolution_patterns','payoff','name');
  return morphology;
}

function fromLegacy(e) {
  const c=e.contract||{},id=e.genreId,source=e.sourceRef||`legacy/${id}`;
  const morphology=[];
  const add=(name,kind,value,i=0)=>{
    if(!nonempty(value))return;
    morphology.push({id:`${id}:${name}:${i}`,title:value,detail:'Legacy contract evidence',kind,
      genreId:id,ruleStrength:null,sourceRef:`${source}/${name}/${i}`,
      sourceKind:'legacy_contract',authority:'legacy_convention'});
  };
  add('audience_product','reader_promise',c.audience_product);
  asArray(c.required_tropes).forEach((v,i)=>add('required_tropes','trope',typeof v==='string'?v:v.description,i));
  asArray(c.optional_tropes).forEach((v,i)=>add('optional_tropes','trope',typeof v==='string'?v:v.description,i));
  asArray(c.default_engine_biases).forEach((v,i)=>add('default_engine_biases','engine',typeof v==='string'?v:v.description,i));
  return morphology;
}

function projectFullArchitecture(input={}) {
  const c=input.candidate||{},nodes=asArray(c.nodes),nodeMap=new Map(nodes.map(n=>[n.id,n]));
  const fingerprint=sourceFingerprint(input),contracts=asArray(c.genre_contracts);
  const source = {requestSha:input.requestSha||null,revision:fingerprint.canvasRevision};
  const genreMap=new Map();
  function ensureGenre(id) {
    if(!nonempty(id))return null;
    if(!genreMap.has(id))genreMap.set(id,{
      genreId:id,title:nodeMap.get(id)?.title||id,role:'unassigned',
      packCoverage:{status:'unknown'},morphology:[],candidateInterpretations:[],usage:[],
      sourceRef:nodeMap.has(id)?ref('nodes',id):null});
    return genreMap.get(id);
  }
  for(const n of nodes.filter(n=>n.category==='genre'))ensureGenre(n.id);
  for(const ct of contracts){
    const g=ensureGenre(ct.genre_node_id);if(!g)continue;
    g.role=ct.role||'unassigned';
    const sourceRef=ref('genre_contracts',ct.genre_node_id);
    const entry=(kind,title,path,i)=>{
      if(!nonempty(title))return;
      g.candidateInterpretations.push({id:`${ct.genre_node_id}:${path}:${i}`,kind,title,
        genreId:ct.genre_node_id,sourceKind:'architecture_candidate',sourceRef:`${sourceRef}/${path}${i==null?'':'/'+i}`,
        authority:'candidate_genre_interpretation',requestSha:source.requestSha});
    };
    asArray(ct.trope_functions).forEach((x,i)=>entry('trope',x,'trope_functions',i));
    entry('engine',ct.narrative_engine,'narrative_engine');
    entry('structure',ct.structural_pattern,'structural_pattern');
    asArray(ct.payoff_expectations).forEach((x,i)=>entry('payoff',x,'payoff_expectations',i));
    asArray(ct.emotion_target_ids).forEach((id,i)=>{
      const t=asArray(c.emotion_targets).find(t=>t.id===id);
      if(t)entry('emotion',t.emotion,'emotion_target_ids',i);
    });
  }
  asArray(input.genreEvidence).forEach(e=>{
    const g=ensureGenre(e?.genreId);if(!g)return;
    if(packIsVerified(e)){
      g.packCoverage={status:'verified_pack',packId:e.pack.pack_id,version:e.pack.version,contentHash:e.contentHash};
      g.morphology.push(...fromPack(e));
    }else g.packCoverage={status:'unverified',reason:'Missing verified pack version, content hash or applicability'};
  });
  asArray(input.legacyEvidence).forEach(e=>{
    const g=ensureGenre(e?.genreId);if(g)g.morphology.push(...fromLegacy(e));
  });

  const typedLinks=asArray(c.links).flatMap((edge,i)=>{
    if(!nonempty(edge?.source)||!nonempty(edge?.target)||!nodeMap.has(edge.source)||
       !nodeMap.has(edge.target)||!nonempty(edge.function))return [];
    return [{id:edge.id||`link-${i}`,from:edge.source,to:edge.target,verb:edge.function,
      sourceRef:`links/${i}`,sourceKind:'architecture_candidate',authority:'agent_proposal',
      requestSha:source.requestSha}];
  });
  const workingItems=asArray(input.workingItems),storySpecific=workingItems.filter(i=>nonempty(i.architecture_role)).map(i=>{
    const origin=i.proposal_origin;
    const originExpected=origin?.source_kind==='illustrative_model_hypothesis'?input.workingSourceRevision:source.requestSha;
    const linkedRefs=asArray(input.workingConnections).filter(e=>e.source===i.id||e.target===i.id).map(e=>e.id);
    return {itemId:i.id,title:i.title,role:i.architecture_role,detail:i.content||'',
      classification:origin?'candidate_derived_working':'unattributed_or_unknown',
      authority:'author_working',canonical:false,sourceRef:origin?.source_ref||null,
      originRequestSha:origin?.request_sha||null,sourceKind:origin?.source_kind||'author_intent',
      linkedRefs,needsReview:!!i.needsReview||!!(origin?.request_sha&&originExpected&&origin.request_sha!==originExpected),
      reason:origin?'Attributed to original proposal; later edits may differ.':
        'Author working idea; relationship to available genre morphology not established.'};
  });
  const basicTargets=asArray(c.emotion_targets).filter(t=>labels.has(t.emotion)).map(t=>({
    id:t.id,emotion:t.emotion,role:t.role,intendedEffect:t.intended_effect,
    elicitingCondition:t.eliciting_condition,aestheticStrategy:t.aesthetic_strategy,
    provenance:t.provenance,sourceRef:`emotion_targets/${t.id}`,
    authority:'architecture_candidate',requestSha:source.requestSha}));
  const phases=asArray(c.phases).map(p=>({
    id:p.id,title:p.title,order:p.order,role:p.narrative_function||'',scope:p.scope||'whole_story',
    readerExperience:p.reader_experience||null,parallelWith:asArray(p.parallel_with),
    genreActivations:asArray(p.genre_activations).map(a=>({genreId:a.genre_node_id,
      basicEmotions:asArray(a.basic_emotions),tropeFunctions:asArray(a.trope_functions),
      structuralFunction:a.structural_function,sourceRef:`phases/${p.id}/genre_activations/${a.genre_node_id}`})),
    sourceRef:`phases/${p.id}`,authority:'architecture_candidate'}))
    .sort((a,b)=>(a.order??0)-(b.order??0));
  const interactions=asArray(c.genre_interactions).map(i=>({id:i.id,from:i.source_genre_id,to:i.target_genre_id,
    verb:i.kind,mechanism:i.mechanism,risk:i.risk||null,sourceRef:`genre_interactions/${i.id}`,authority:'architecture_candidate'}));
  const richExperiences=[];
  const target=input.acceptedIdentity?.target_experience;
  if(nonempty(target))richExperiences.push(target);
  return {
    fingerprint,
    identity:{working:storySpecific.filter(x=>['emotion','premise','genre','theme'].includes(x.role)),
      accepted:input.acceptedIdentity?{status:'available',value:copy(input.acceptedIdentity)}:{status:'unavailable_source'},
      summary:c.summary||null,genres:[...genreMap.values()].map(g=>({genreId:g.genreId,title:g.title,role:g.role}))},
    genreViews:[...genreMap.values()],storySpecific,
    structure:{engines:nodes.filter(n=>n.category==='engine'||n.category==='structure').map(n=>({id:n.id,title:n.title,detail:n.summary,sourceRef:`nodes/${n.id}`,authority:'architecture_candidate'})),
      phases,interactions,explicitLinks:typedLinks,workingLinks:copy(asArray(input.workingConnections)),
      accepted:input.acceptedStructure?copy(input.acceptedStructure):null},
    emotionalDesign:{basicTargets,richExperiences,trajectory:phases.filter(p=>p.readerExperience).map(p=>({phaseId:p.id,experience:p.readerExperience}))},
    typedLinks,
    issues:[...asArray(c.open_questions).map((s,i)=>({id:`question-${i}`,kind:'author_decision',state:'open_author_decision',why:s,sourceRef:`open_questions/${i}`}))],
  };
}

/** Read-only, actionable Book design coverage — never a quality or acceptance score. */
const arr=v=>Array.isArray(v)?v:[];
function reviewFullArchitecture(projection) {
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

/** The full Book architecture is a read-only view of the same working decisions. */
const faEl=(tag,cls,value)=>{const node=document.createElement(tag);if(cls)node.className=cls;if(value!==undefined)node.textContent=value;return node;};
function renderFullArchitecture(root,projection,{expandedGenre,onToggleGenre,onFocusRef,onReview}) {
  root.replaceChildren();
  const hero=faEl('header','full-hero');
  hero.append(faEl('p','eyebrow','THE LIVING STORY · COMPLETE BOOK DESIGN'),
    faEl('h2','', 'The full narrative architecture'),
    faEl('p','full-hero-lede',projection.identity.summary||'The story blueprint begins with your author-owned decisions.'));
  const actions=faEl('div','full-hero-actions');
  const review=faEl('button','btn-primary','Review Full Architecture');review.type='button';
  review.addEventListener('click',onReview);actions.appendChild(review);hero.appendChild(actions);root.appendChild(hero);
  const grid=faEl('div','full-grid');
  const section=(title,label)=>{
    const area=faEl('section','full-cluster');
    area.append(faEl('p','cluster-eyebrow',label),faEl('h3','',title));grid.appendChild(area);return area;
  };
  const empty=(container,text)=>container.appendChild(faEl('p','source-empty',text));
  const identity=section('Identity & reader experience','01 · THE STORY PROMISE');
  const intentions=projection.identity.working;
  if(!intentions.length)empty(identity,'No author working ideas yet. Start in Focus to define your reader intention, premise or theme.');
  else for(const item of intentions) {
    const row=faEl('button','full-source-action',item.title+' · Working, not canon');
    row.addEventListener('click',()=>onFocusRef(item.itemId));identity.appendChild(row);
  }
  const readerTargets=projection.emotionalDesign.basicTargets;
  if(readerTargets.length){identity.appendChild(faEl('h4','','Target basic reader emotions · proposed architecture'));
    const tags=faEl('div','full-chips');readerTargets.forEach(t=>tags.appendChild(faEl('span','full-chip',
      `${t.emotion} · ${t.role} · ${t.provenance.replace(/_/g,' ')}`)));identity.appendChild(tags);
  }else empty(identity,'Target basic reader emotions have not been specified in the candidate.');
  if(projection.emotionalDesign.richExperiences.length)
    identity.appendChild(faEl('p','source-note','Richer intended experience: '+projection.emotionalDesign.richExperiences.join('; ')));
  const genres=section('Genre constellation & morphology','02 · GENRE-RELATIVE EVIDENCE');
  if(!projection.genreViews.length)empty(genres,'Genre morphology not established. No source-backed genre has been selected.');
  for(const genre of projection.genreViews){
    const wrap=faEl('div','genre-record');
    const toggle=faEl('button','genre-toggle',`${genre.title} · ${genre.role} · ${genre.packCoverage.status==='verified_pack'?'Verified Pack':'Genre morphology not established'}`);
    toggle.type='button';toggle.setAttribute('aria-expanded',String(expandedGenre===genre.genreId));
    toggle.addEventListener('click',()=>onToggleGenre(expandedGenre===genre.genreId?null:genre.genreId));
    wrap.appendChild(toggle);
    if(expandedGenre===genre.genreId){
      const detail=faEl('div','genre-details');
      if(genre.packCoverage.status==='verified_pack'){
        detail.appendChild(faEl('p','source-note',`Verified Pack: ${genre.packCoverage.packId} v${genre.packCoverage.version} · ${genre.packCoverage.contentHash}`));
        for(const evidence of genre.morphology){
          const item=faEl('p','genre-evidence',`${evidence.kind}: ${evidence.title} · ${evidence.ruleStrength||'no rule strength'} · ${evidence.sourceKind}`);
          detail.appendChild(item);
        }
      } else detail.appendChild(faEl('p','source-empty','Genre morphology not established by an attached, applicable, versioned Genre Pack.'));
      const legacy=genre.morphology.filter(m=>m.sourceKind==='legacy_contract');
      for(const item of legacy)detail.appendChild(faEl('p','genre-evidence',`${item.kind}: ${item.title} · Legacy contract · ${item.sourceRef}`));
      detail.appendChild(faEl('h4','','Candidate interpretation · not verified morphology'));
      for(const item of genre.candidateInterpretations)
        detail.appendChild(faEl('p','candidate-morphology',`${item.kind}: ${item.title} · Source: ${item.sourceRef}`));
      if(!genre.candidateInterpretations.length)empty(detail,'No proposed conventions, emotional targets or structure for this genre.');
      wrap.appendChild(detail);
    }
    genres.appendChild(wrap);
  }
  const additions=section('Story-specific additions','03 · THE AUTHOR’S CHOICES');
  const storySpecific=projection.storySpecific;
  if(!storySpecific.length)empty(additions,'No author working ideas yet. Proposals are not automatically adopted.');
  storySpecific.forEach(item=>{
    const link=faEl('button','full-source-action',`${item.title} · ${item.role} · Working, not canon`);
    link.addEventListener('click',()=>onFocusRef(item.itemId));additions.appendChild(link);
    additions.appendChild(faEl('p','source-note',
      `${item.needsReview?'Needs review · ':''}${item.classification.replaceAll('_',' ')}${item.linkedRefs.length?' · Linked through recorded working relationships':' · Author relationship not yet recorded'}`));
  });
  const structure=section('Narrative engines & Book structure','04 · INTEGRATED STORY DESIGN');
  if(!projection.structure.engines.length&&!projection.structure.phases.length)empty(structure,'Book structure is not yet specified. Scene planning remains optional.');
  for(const engine of projection.structure.engines)
    structure.appendChild(faEl('p','full-struct',`Proposed engine: ${engine.title} · ${engine.sourceRef}`));
  const phases=faEl('ol','full-phases');
  for(const phase of projection.structure.phases){
    const li=faEl('li','',phase.title);
    li.appendChild(faEl('span','phase-details',phase.role+' · '+phase.genreActivations.map(x=>x.genreId).join(', ')));
    phases.appendChild(li);
  }
  structure.appendChild(phases);
  if(projection.structure.interactions.length){structure.appendChild(faEl('h4','','Genre interactions · proposed'));
    projection.structure.interactions.forEach(item=>structure.appendChild(faEl('p','source-note',
      `${item.from} ${item.verb} ${item.to}: ${item.mechanism}`)));
  }
  const explicit=section('Explicit relationships','05 · CONNECTIONS, NOT ASSUMPTIONS');
  if(!projection.typedLinks.length)empty(explicit,'No evidence-linked connections have been supplied.');
  for(const link of projection.typedLinks)explicit.appendChild(faEl('p','full-struct',
    `${link.from} → ${link.verb} → ${link.to} · ${link.sourceRef} · Proposal, not canon`));
  root.appendChild(grid);
  const foot=faEl('p','full-source-foot','Genre Pack evidence and proposed genre interpretations are separate. Story-specific means relative to available sources, never proven globally original. No story canon is accepted here.');root.appendChild(foot);
}

/** Derived decision review; no acceptance, persistence or provider actions. */
const rvEl=(tag,cls,value)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(value!==undefined)e.textContent=value;return e;};
function renderReviewArchitecture(root,report,{onFocusRef,onReturn}){
  root.replaceChildren();
  root.append(rvEl('p','eyebrow','REVIEW THE WHOLE STORY'),rvEl('h2','','Review Full Architecture'),
    rvEl('p','review-status',report.status==='ready_for_author_review'?'Ready for author review — not accepted canon':'Working design — open decisions remain'),
    rvEl('p','review-intro',report.summary));
  const toolbar=rvEl('div','review-actions'),back=rvEl('button','','Return to architecture');back.type='button';
  back.addEventListener('click',onReturn);toolbar.appendChild(back);root.appendChild(toolbar);
  const list=rvEl('div','review-items');
  for(const item of report.items){
    const row=rvEl('article','review-item');
    row.append(rvEl('strong','',item.id.replaceAll('-',' ').replaceAll(':',' · ').replace(/^./,c=>c.toUpperCase())),
      rvEl('span','review-state',item.state.replaceAll('_',' ')),rvEl('p','',item.why));
    if(item.focusTarget&&!item.focusTarget.startsWith('genre:')){
      const focus=rvEl('button','','Work on this decision');focus.type='button';focus.addEventListener('click',()=>onFocusRef(item.focusTarget));row.appendChild(focus);
    }
    list.appendChild(row);
  }
  root.appendChild(list);
  root.appendChild(rvEl('p','review-disclaimer','Unknown Genre Pack coverage is not an authoring failure. Optional scene planning is not required. Reviewing cannot accept story canon.'));
}

global.AuteurStudioFullArchitecture={project:projectFullArchitecture,review:reviewFullArchitecture,renderFull:renderFullArchitecture,renderReview:renderReviewArchitecture};
})(window);
