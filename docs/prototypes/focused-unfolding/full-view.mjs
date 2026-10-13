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
