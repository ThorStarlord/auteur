/** Deterministic, read-only Full Architecture projection. No canonical or provider writes. */
const asArray=v=>Array.isArray(v)?v:[];
const copy=v=>v==null?v:structuredClone(v);
const nonempty=v=>typeof v==='string'&&v.trim().length>0;
const ref=(prefix,id)=>`${prefix}/${id}`;
const labels=new Set(['joy','sadness','fear','anger','disgust','surprise']);

export function sourceFingerprint(input={}) {
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
  asArray(c.primary_excitement_beats).forEach((v,i)=>add('primary_excitement_beats','structure',typeof v==='string'?v:v.description,i));
  asArray(c.setup_contract?.minimum_setup_beats).forEach((v,i)=>add('setup_contract/minimum_setup_beats','structure',typeof v==='string'?v:v.description,i));
  return morphology;
}

export function projectFullArchitecture(input={}) {
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
