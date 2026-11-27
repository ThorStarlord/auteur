/* Persistent contextual creative-agent panel; requests are explicit and source-labeled. */
(function(global){'use strict';
 function createCreativePanel({root,onAction,onRevise,onClear,onComplete,onUseAlternative}={}){
  if(!root||typeof onAction!=='function'||typeof onRevise!=='function')throw Error('Creative panel requires callbacks');
  const doc=root.ownerDocument||document,make=(tag,text)=>{const e=doc.createElement(tag);if(text!==undefined)e.textContent=text;return e};
  let anchors=[],actions=[],operation='explore',evidence=null,sentText=null,discoveryOrigin=null;
  const heading=make('h3','Creative interaction with your coding agent');
  const notice=make('p','Working architecture only · No story canon accepted here.');
  const chips=make('div');chips.setAttribute('aria-label','Selected source anchors');
  const menu=make('div');menu.setAttribute('aria-label','Creative actions');
  // Book evidence the author brought from a working Book: shown apart from the question, sent apart from it.
  // The discovered possibility this investigation came from, shown so the author knows what it was taken from.
  const originNote=make('p');originNote.className='creative-origin';originNote.hidden=true;
  const evidenceBox=make('section');evidenceBox.setAttribute('aria-label','Book evidence');evidenceBox.className='creative-book-evidence';evidenceBox.hidden=true;
  const instruction=make('textarea');instruction.setAttribute('aria-label','Your creative intention');instruction.maxLength=4000;instruction.rows=3;
  instruction.placeholder='What would you like to understand or change about this selection?';
  const submit=make('button','Ask coding agent (no revision)');submit.type='button';submit.dataset.creativeSubmit='true';
  const status=make('p','No host-agent request prepared.');status.setAttribute('role','status');status.setAttribute('aria-live','polite');
  const packetLabel=make('label','Prepared host-agent request (copy to your coding agent; not executed)');
  const packet=make('textarea');packet.setAttribute('aria-label','Prepared host-agent request');packet.readOnly=true;packet.rows=5;
  const responseLabel=make('label','Paste signed host-agent response JSON to validate the inquiry');
  const response=make('textarea');response.setAttribute('aria-label','Host-agent inquiry response');response.rows=4;
  const complete=make('button','Validate inquiry response');complete.type='button';
  const history=make('section');history.setAttribute('aria-label','Earlier creative exchanges');
  const lineage=make('section');lineage.setAttribute('aria-label','Superseded creative exchanges');
  const result=make('section');result.setAttribute('aria-label','Inquiry result');
  const clear=make('button','Clear graph selection');clear.type='button';
  root.append(heading,notice,chips,originNote,evidenceBox,menu,instruction,submit,status,packetLabel,packet,responseLabel,response,complete,history,lineage,result,clear);
  const agentOperations=new Set(['explain','challenge','explore','compare','connect_to_ask']);
  function updateSubmit(){const isRevision=operation==='revise';submit.textContent=isRevision?'Request holistic revision':
    agentOperations.has(operation)?'Ask coding agent (no revision)':operation==='trace'?'Trace recorded relationships':'Inspect recorded source';}
  function choose(next){if(!actions.some(a=>a.operation===next))throw Error('Action not available for source');operation=next;updateMenu();updateSubmit();}
  function updateMenu(){menu.replaceChildren();for(const a of actions){const b=make('button',a.label);b.type='button';b.dataset.operation=a.operation;
    b.setAttribute('aria-pressed',String(operation===a.operation));b.title=a.description||'';
    b.addEventListener('click',()=>choose(a.operation));menu.append(b);}}
  function renderEvidence(){evidenceBox.replaceChildren();evidenceBox.hidden=!evidence;if(!evidence)return;
    evidenceBox.append(make('h4','Book evidence · from working Book '+evidence.book_number));
    evidenceBox.append(make('p',evidence.kind+' · “'+evidence.text+'”'));
    evidenceBox.append(make('p','Working Book proposal ('+(evidence.standing||'working')+', '+(evidence.epistemic_status||'')+') · working revision '+
      evidence.revision_number+' · element '+evidence.element_id+'. It goes to your coding agent as Book evidence, not as your question and not as Architecture fact.'));
    const drop=make('button','Ask without this evidence');drop.type='button';drop.addEventListener('click',()=>{evidence=null;renderEvidence();});
    evidenceBox.append(drop);
  }
  function setBookEvidence(next){evidence=next?Object.assign({},next):null;renderEvidence();}
  function renderOrigin(){
    originNote.hidden=!discoveryOrigin;
    if(!discoveryOrigin){originNote.textContent='';return}
    originNote.textContent=discoveryOrigin.kind==='consequence'
      ?'From an alternative a consequence analysis of this proposal set out: “'+discoveryOrigin.title+'” ('+discoveryOrigin.approach+'). Its question is the analysis’s suggested wording, not yours: “'+discoveryOrigin.suggestion+'”. Investigating it changes nothing in the Architecture.'
      :'From a discovered possibility: “'+discoveryOrigin.title+'”. Discovery proposed it as advisory; this investigation is yours to direct.';
  }
  function setDiscoveryOrigin(next){discoveryOrigin=next?Object.assign({},next):null;renderOrigin();}
  function setConsequenceOrigin(next){discoveryOrigin=next?Object.assign({kind:'consequence'},next):null;renderOrigin();}
  function setSelection(next,available){anchors=next.slice();actions=(available||[]).slice();
    // A possibility's origin holds only for its own questions; any other selection drops it, never rebinding it.
    if(discoveryOrigin&&!(anchors.length===discoveryOrigin.questions.length&&anchors.every(a=>discoveryOrigin.questions.includes(a.id))))setDiscoveryOrigin(null);
    // Book evidence belongs to the concepts the Book records; another selection drops it.
    if(evidence&&!anchors.every(a=>a.kind==='node'&&(evidence.anchors||[]).includes(a.id))){evidence=null;renderEvidence();}
    chips.replaceChildren();for(const a of anchors){const item=make('span',a.kind+' · '+a.id+(a.field?' / '+a.field:'')+(a.index!=null?' · entry '+(a.index+1):''));
      item.title=a.sourceRef||'Source reference will be verified on the server';item.className='creative-anchor-chip';chips.append(item)}
    if(!actions.some(a=>a.operation===operation))operation=actions.find(a=>agentOperations.has(a.operation))?.operation||actions[0]?.operation||'explore';
    updateMenu();updateSubmit();
  }
  submit.addEventListener('click',()=>{if(!anchors.length){status.textContent='Select a recorded graph element first.';return}
    const authorText=instruction.value;if(!authorText.trim()&&!['inspect','trace'].includes(operation)){status.textContent='Describe your creative intention first.';return}
    const payload={operation,anchors:anchors.slice(),authorText};
    if(discoveryOrigin&&discoveryOrigin.kind!=='consequence'&&agentOperations.has(operation))payload.fromDiscovery=Object.assign({},discoveryOrigin);
    if(operation!=='revise')sentText=authorText;
    if(evidence&&agentOperations.has(operation))payload.bookEvidence=Object.assign({},evidence);
    if(operation==='revise')onRevise(payload);
    else if(onAction)onAction(payload);
  });
  complete.addEventListener('click',()=>{try{if(onComplete)onComplete(JSON.parse(response.value));}catch(error){status.textContent='Response JSON could not be read: '+error.message;}});
  clear.addEventListener('click',()=>{anchors=[];actions=[];evidence=null;renderEvidence();chips.replaceChildren();menu.replaceChildren();if(onClear)onClear();});
  function chooseAlternative(hypothesisId,inquirySha){
    if(!anchors.length){status.textContent='Select a recorded graph element first.';return}
    const authorText=instruction.value;
    if(!authorText.trim()){status.textContent='Write what you want to develop from '+hypothesisId+' first.';
      if(instruction.focus){instruction.focus({preventScroll:true});if(instruction.scrollIntoView)instruction.scrollIntoView({block:'center'});}return}
    if(onUseAlternative)onUseAlternative({anchors:anchors.slice(),authorText,
      selectedAlternative:{inquiryRequestSha256:inquirySha,hypothesisId:hypothesisId}});
  }
  function renderHistory(entries){history.replaceChildren();
    if(!Array.isArray(entries)||!entries.length)return;
    history.append(make('h4','Earlier exchanges for this source (noncanonical)'));
    for(const entry of entries.slice(0,8)){
      const box=make('div');box.dataset.exchangeSha=entry.request_sha256||'';
      box.append(make('strong',(entry.operation||'inquiry')+' · '+(entry.author_question||'')));
      const alternatives=(entry.hypotheses||[]).map(h=>(h.id||'')+' '+h.title).join('; ');
      if(alternatives)box.append(make('p','Alternatives: '+alternatives));
      history.append(box);
    }
  }
  function renderLineage(entries){lineage.replaceChildren();
    if(!Array.isArray(entries)||!entries.length)return;
    lineage.append(make('h4','Earlier exchanges on a superseded architecture (historical; not selectable)'));
    for(const entry of entries.slice(0,8)){
      const box=make('div');box.dataset.supersededExchangeSha=entry.request_sha256||'';
      box.append(make('strong',(entry.operation||'inquiry')+' · '+(entry.author_question||'')));
      const alternatives=(entry.hypotheses||[]).map(h=>(h.id||'')+' '+h.title).join('; ');
      if(alternatives)box.append(make('p','Alternatives: '+alternatives));
      lineage.append(box);
    }
  }
  function setStatus(projection){const value=typeof projection==='string'?{status:projection}:projection||{};
    const s=value.status||'not_started';status.textContent=s==='awaiting_host_agent'?
      'Host-agent request prepared, not executed. Copy the packet to your active coding agent.':
      s==='ready'?'Validated inquiry response received. No architecture revision or story acceptance.':
      s==='refreshing'?'Architecture source changed. Reloading this source’s exchanges.':
      s==='stale'&&(value.book_evidence_status==='changed'||value.book_evidence_status==='unreadable')?
        'The working Book element this was asked with changed or cannot be read. This inquiry is historical; take it to your coding agent again from the Book.':
      s==='stale'||s==='guidance_changed'?'Source context changed. This inquiry is historical; prepare a new request.':
      s==='error'? 'Inquiry error; no new architecture was applied.': s==='not_started'?'No question asked yet.':'Inquiry status: '+s+'.';
    packet.value=value.request?JSON.stringify(value.request,null,2):'';
    // Evidence the owner reports changed is not offered again as if it were the Book's record.
    if(evidence&&(value.book_evidence_status==='changed'||value.book_evidence_status==='unreadable')){evidence=null;renderEvidence();}
    renderHistory(value.history);
    renderLineage(value.superseded_history);
  }
  // What the recorded-history packet of a comparison was, grouped by basis. Labels say what kind of evidence each item is;
  // nothing here is the answer, and a Book decision's identity basis says whether the author stated it or the owner matched it.
  const BASIS_WORDS={current_wording:'Current wording',recorded_wording:'Recorded wording',recorded_change:'Recorded change',
    recorded_absence:'Not recorded in this revision',recorded_reason:'The author’s request then',
    recorded_selected_alternative:'Alternative the author chose then (a historical agent interpretation)',
    book_decision:'Working Book decision (a noncanonical proposal)',recorded_co_reference:'Recorded reference',
    book_element_association:'Working Book element that engages this question (an association: engagement only)',
    recorded_element_co_reference:'Recorded element association with two of these questions (a fact about one element’s record)',
    positional_observation:'Positional name in Book prose (an observation, not a reference)',
    named_gap:'Missing or unreadable history'};
  const STANDING_WORDS={current:'the decision stands as it did',book_revised:'the Book has been revised since; this decision reads as it did',
    decision_changed:'the decision has changed since',decision_gone:'the decision is no longer recorded',unreadable:'the Book cannot be read now'};
  // An element association's standing is the element's own, not a decision's.
  const ENGAGEMENT_STANDING={current:'the element reads as it did',book_revised:'the Book has been revised since; the element reads as it did',
    element_changed:'the element has changed since it was read',association_gone:'the element no longer records this association',
    unreadable:'the Book cannot be read now'};
  function deliberationEvidence(packet,standing){
    const box=make('details');box.className='creative-deliberation';box.dataset.deliberation='true';
    box.append(make('summary','Evidence this answer was given · '+(packet.questions||[]).length+' open questions · recorded history'));
    box.append(make('p','Each line says what kind of evidence it is. The answer above is an agent interpretation, not part of this record.'));
    const standingBy={};(standing||[]).forEach(row=>{standingBy[row.kind==='book_element_association'?
      row.book_number+':'+row.element_id+':'+row.question_id:row.book_number+':'+row.decision_id]=row.standing;});
    for(const q of packet.questions||[]){
      const section=make('section');section.className='creative-deliberation-question';
      section.append(make('h5',BASIS_WORDS.current_wording+' · “'+(q.current?.text||'')+'”'));
      for(const item of q.history||[]){
        const line=make('p');line.dataset.basis=item.basis;
        let words=BASIS_WORDS[item.basis]||String(item.basis||'');
        if(item.change)words+=' · '+String(item.change).replace(/_/g,' ');
        if(item.from_revision!=null)words+=' · revision '+item.from_revision+(item.to_revision!==item.from_revision?'–'+item.to_revision:'');
        if(item.text)words+=' · “'+item.text+'”';
        if(item.note)words+=' · '+item.note;
        line.textContent=words;line.dataset.basis=String(item.basis||'');section.append(line);
        if(item.reason){
          const reason=make('p');reason.dataset.basis='recorded_reason';
          reason.textContent=BASIS_WORDS.recorded_reason+' · '+(item.reason.instruction?'“'+item.reason.instruction+'”':'none recorded')+
            (item.reason.note?' · '+item.reason.note:'');
          section.append(reason);
          if(item.reason.selected_alternative){const chosen=make('p');chosen.dataset.basis='recorded_selected_alternative';
            chosen.textContent=BASIS_WORDS.recorded_selected_alternative+' · '+(item.reason.selected_alternative.title||'');section.append(chosen);}
        }
      }
      for(const book of q.books||[]){
        const decision=make('p');decision.dataset.basis='book_decision';
        const owner=book.identity_basis==='recorded_by_decision'?'the decision names this question itself':
          'the Book owner matched it to this question from the version it names; the author did not state that';
        const now=STANDING_WORDS[standingBy[book.book_number+':'+book.decision_id]];
        decision.textContent='Book '+book.book_number+' · '+BASIS_WORDS.book_decision+' · “'+(book.decision_text||'')+'” · '+owner+
          (now?' · '+now:'');
        section.append(decision);
      }
      for(const item of q.engagements||[]){
        const line=make('p');line.dataset.basis='book_element_association';
        const now=ENGAGEMENT_STANDING[standingBy[item.book_number+':'+item.element_id+':'+q.id]];
        const authority=[item.attribution,item.epistemic_status,item.commitment_authority].filter(Boolean).join(' · ');
        line.textContent='Book '+item.book_number+' · '+BASIS_WORDS.book_element_association+' · '+(item.collection||'element')+' · “'+
          (item.element_text||'')+'” · the element’s own status: '+authority+(now?' · '+now:'');
        section.append(line);
        for(const dep of item.dependencies||[]){const d=make('p');d.dataset.basis='book_element_association';
          d.textContent='   The Book records a dependency: '+(dep.direction==='to'?'it gives to ':'it receives from ')+dep.other+' ('+dep.dependency+')'+
            (dep.function?' · '+dep.function:'');section.append(d);}
      }
      box.append(section);
    }
    for(const co of packet.co_references||[]){const line=make('p');line.dataset.basis=co.basis==='recorded_element_co_reference'?'recorded_element_co_reference':'recorded_co_reference';
      line.textContent=co.basis==='recorded_element_co_reference'?
        'Book '+co.book_number+': one element records associations with '+(co.question_ids||[]).length+' of these questions. The record does not say the questions are related in the story.':
        'Book '+co.book_number+' records decisions about '+(co.question_ids||[]).length+' of these questions. This is a recorded reference, not a relationship in the story.';
      box.append(line);}
    for(const obs of packet.positional_observations||[]){const line=make('p');line.dataset.basis='positional_observation';
      line.textContent='Book '+obs.book_number+' · '+BASIS_WORDS.positional_observation+' · “'+obs.phrase+'” in '+(obs.collection||'the prose')+
        ', read as position '+obs.position+' at the version the prose was written against. Nothing is recorded from it.';
      box.append(line);}
    for(const gap of packet.named_gaps||[]){const line=make('p');line.dataset.basis='named_gap';line.textContent=gap.note;box.append(line);}
    return box;
  }
  function setInquiryResult(value){setStatus(value);result.replaceChildren();const response=value?.result;
    // Once alternatives arrive, the field is for what to develop: the question already sent is not reused as
    // a revision instruction by an unthinking click.
    if(response&&value.status==='ready'&&(response.hypotheses||[]).length&&sentText!==null&&instruction.value===sentText){
      instruction.value='';sentText=null;}
    if(response&&(response.hypotheses||[]).length)instruction.placeholder='Write what you want to develop from one alternative, then choose it below.';
    if(!response)return;
    const h=make('h4','Agent interpretation — noncanonical');h.tabIndex=-1;h.dataset.inquiryAnswer='true';h.className='creative-answer-title';result.append(h);
    const asked=(response.intent&&response.intent.author_text)||'';
    if(asked){const a=make('p','Answer to: “'+(asked.length>160?asked.slice(0,159)+'…':asked)+'”'+
      (response.book_evidence?' · asked with Book '+((response.book_evidence.book||{}).book_number)+' evidence':''));a.className='creative-asked';result.append(a);}
    if(response.deliberation)result.append(deliberationEvidence(response.deliberation,response.deliberation_standing));
    // Which Book evidence the question was asked with, and whether it is still current, comes before the answer.
    if(response.book_evidence){const be=response.book_evidence,bk=be.book||{},el=be.element||{};
      const changed=value.book_evidence_status==='changed'||value.book_evidence_status==='unreadable';
      const line=make('p','Asked with Book evidence: working Book '+bk.book_number+', revision '+bk.revision_number+', element '+el.id+'. '+
        (changed?'The Book has changed since, or cannot be read: this evidence is historical, not its present record.':'It is still the Book’s current record.'));
      line.dataset.bookEvidenceStatus=value.book_evidence_status||'';line.className='creative-evidence-status'+(changed?' is-historical':'');result.append(line);}
    // The agent's interpretation and the records it cites sit side by side on a wide desk, so what is read
    // into the story and what the records hold stay visibly apart.
    const pair=make('div');pair.className='creative-pair';result.append(pair);
    const readingCol=make('div');readingCol.className='creative-reading';pair.append(readingCol);
    const reading=make('p',response.analysis||'');reading.className='creative-interpretation';readingCol.append(reading);
    const evidenceCol=make('div');evidenceCol.className='creative-records';
    const list=(title,items,render,cls,into)=>{if(!items||!items.length)return;const target=into||result;const hd=make('h5',title);target.append(hd);const ul=make('ul');if(cls)ul.className=cls;
      for(const item of items||[]){ul.append(make('li',render(item)))}target.append(ul)};
    list('Recorded source claims (not causal proof)',response.recorded_observations, x=>x.claim+' ('+x.kind+':'+x.id+')','creative-claims',evidenceCol);
    if(evidenceCol.children.length)pair.append(evidenceCol);
    const historical=response.book_evidence&&(value.book_evidence_status==='changed'||value.book_evidence_status==='unreadable');
    if((response.hypotheses||[]).length){result.append(make('h5','Creative alternatives (noncanonical)'));
      const how=make('p','Choosing one prepares a revision request with the words in “Your creative intention” above; nothing is applied until you review and apply it.');
      how.className='creative-choose-how';result.append(how);}
    if(historical&&(response.hypotheses||[]).length)result.append(make('p','The Book evidence these were asked with has changed since. '+
      'A revision developed from one of them carries that evidence marked historical.'));
    const alternatives=make('ul');alternatives.className='creative-alternatives';result.append(alternatives);
    (response.hypotheses||[]).forEach((x,index)=>{const id=x.id||('h'+(index+1));
      const varies=x.divergence_axis?' (varies '+x.divergence_axis.replace(/_/g,' ')+')':'';
      // Each alternative reads as its own option: a title, the dimension it varies, then what it proposes.
      const item=make('li');item.className='creative-alternative';
      const name=make('strong',id+' · '+x.title);name.className='creative-alternative-title';item.append(name);
      if(varies){const axis=make('span',varies.trim());axis.className='creative-axis';item.append(axis);}
      const desc=make('p',x.description);desc.className='creative-alternative-description';item.append(desc);
      alternatives.append(item);
      if(onUseAlternative&&value.status==='ready'&&value.request_sha256){
        const use=make('button','Use '+id+' as revision basis (prepares a revision request)');use.type='button';use.dataset.alternativeId=id;
        use.addEventListener('click',()=>chooseAlternative(id,value.request_sha256));item.append(use);
      }});
    list('Uncertainties',response.uncertainties,x=>x,'creative-uncertainties');
    if((response.hypotheses||[]).length){const none=make('p','Developing none of these alternatives leaves the Architecture as it is'+
      (response.book_evidence?'; the Book keeps its own record either way.':'.'));none.className='creative-decline';result.append(none);}
  }
  function setLocalInspection(projection){
    status.textContent='Local source inspection only — no host-agent request sent.';
    result.replaceChildren();result.append(make('h4','Recorded source information'));
    for(const anchor of projection.anchors||[])result.append(make('p',anchor.kind+':'+anchor.id+' · '+anchor.sourceRef));
    if(projection.missingRelation)result.append(make('p','No recorded relation between the selected elements.'));
    const list=make('ul');for(const relation of projection.recordedRelations||[]){
      list.append(make('li',relation.kind+' · '+(relation.id||relation.field)+' · '+relation.sourceRef));
    }result.append(list);
  }
  function invalidateResult(){result.replaceChildren();history.replaceChildren();lineage.replaceChildren();}
  // Bring the current answer to the author: its heading takes focus and comes into view.
  function focusResult(){const h=result.children&&result.children[0];if(h&&h.focus){h.focus({preventScroll:true});if(h.scrollIntoView)h.scrollIntoView({block:'start'});}}
  updateSubmit();return {setSelection,setDiscoveryOrigin,setConsequenceOrigin,setStatus,setInquiryResult,setLocalInspection,invalidateResult,setBookEvidence,getBookEvidence:()=>evidence,focusResult,setAuthorText:text=>{instruction.value=text},
    setOperation:choose,getAuthorText:()=>instruction.value,reset:()=>{anchors=[];actions=[];evidence=null;renderEvidence();chips.replaceChildren();menu.replaceChildren();result.replaceChildren();history.replaceChildren();status.textContent='No host-agent request prepared.';packet.value='';},
    destroy:()=>root.replaceChildren()};
 }
 global.AuteurStudioCreativePanel={createCreativePanel};
})(window);
