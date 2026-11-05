/* Persistent contextual creative-agent panel; requests are explicit and source-labeled. */
(function(global){'use strict';
 function createCreativePanel({root,onAction,onRevise,onClear,onComplete}={}){
  if(!root||typeof onAction!=='function'||typeof onRevise!=='function')throw Error('Creative panel requires callbacks');
  const doc=root.ownerDocument||document,make=(tag,text)=>{const e=doc.createElement(tag);if(text!==undefined)e.textContent=text;return e};
  let anchors=[],actions=[],operation='explore';
  const heading=make('h3','Creative interaction with your coding agent');
  const notice=make('p','Working architecture only · No story canon accepted here.');
  const chips=make('div');chips.setAttribute('aria-label','Selected source anchors');
  const menu=make('div');menu.setAttribute('aria-label','Creative actions');
  const instruction=make('textarea');instruction.setAttribute('aria-label','Your creative intention');instruction.maxLength=4000;instruction.rows=3;
  instruction.placeholder='What would you like to understand or change about this selection?';
  const submit=make('button','Ask coding agent (no revision)');submit.type='button';submit.dataset.creativeSubmit='true';
  const status=make('p','No host-agent request prepared.');status.setAttribute('role','status');status.setAttribute('aria-live','polite');
  const packetLabel=make('label','Prepared host-agent request (copy to your coding agent; not executed)');
  const packet=make('textarea');packet.setAttribute('aria-label','Prepared host-agent request');packet.readOnly=true;packet.rows=5;
  const responseLabel=make('label','Paste signed host-agent response JSON to validate the inquiry');
  const response=make('textarea');response.setAttribute('aria-label','Host-agent inquiry response');response.rows=4;
  const complete=make('button','Validate inquiry response');complete.type='button';
  const result=make('section');result.setAttribute('aria-label','Inquiry result');
  const clear=make('button','Clear graph selection');clear.type='button';
  root.append(heading,notice,chips,menu,instruction,submit,status,packetLabel,packet,responseLabel,response,complete,result,clear);
  const agentOperations=new Set(['explain','challenge','explore','compare','connect_to_ask']);
  function updateSubmit(){const isRevision=operation==='revise';submit.textContent=isRevision?'Request holistic revision':
    agentOperations.has(operation)?'Ask coding agent (no revision)':operation==='trace'?'Trace recorded relationships':'Inspect recorded source';}
  function choose(next){if(!actions.some(a=>a.operation===next))throw Error('Action not available for source');operation=next;updateMenu();updateSubmit();}
  function updateMenu(){menu.replaceChildren();for(const a of actions){const b=make('button',a.label);b.type='button';b.dataset.operation=a.operation;
    b.setAttribute('aria-pressed',String(operation===a.operation));b.title=a.description||'';
    b.addEventListener('click',()=>choose(a.operation));menu.append(b);}}
  function setSelection(next,available){anchors=next.slice();actions=(available||[]).slice();
    chips.replaceChildren();for(const a of anchors){const item=make('span',a.kind+' · '+a.id+(a.field?' / '+a.field:''));
      item.title=a.sourceRef||'Source reference will be verified on the server';item.className='creative-anchor-chip';chips.append(item)}
    if(!actions.some(a=>a.operation===operation))operation=actions.find(a=>agentOperations.has(a.operation))?.operation||actions[0]?.operation||'explore';
    updateMenu();updateSubmit();
  }
  submit.addEventListener('click',()=>{if(!anchors.length){status.textContent='Select a recorded graph element first.';return}
    const authorText=instruction.value;if(!authorText.trim()){status.textContent='Describe your creative intention first.';return}
    const payload={operation,anchors:anchors.slice(),authorText};
    if(operation==='revise')onRevise(payload);
    else if(onAction)onAction(payload);
  });
  complete.addEventListener('click',()=>{try{if(onComplete)onComplete(JSON.parse(response.value));}catch(error){status.textContent='Response JSON could not be read: '+error.message;}});
  clear.addEventListener('click',()=>{anchors=[];actions=[];chips.replaceChildren();menu.replaceChildren();if(onClear)onClear();});
  function setStatus(projection){const value=typeof projection==='string'?{status:projection}:projection||{};
    const s=value.status||'not_started';status.textContent=s==='awaiting_host_agent'?
      'Host-agent request prepared, not executed. Copy the packet to your active coding agent.':
      s==='ready'?'Validated inquiry response received. No architecture revision or story acceptance.':
      s==='stale'||s==='guidance_changed'?'Source context changed. This inquiry is historical; prepare a new request.':
      s==='error'? 'Inquiry error; no new architecture was applied.': 'Inquiry status: '+s+'.';
    packet.value=value.request?JSON.stringify(value.request,null,2):'';
  }
  function setInquiryResult(value){setStatus(value);result.replaceChildren();const response=value?.result;
    if(!response)return;
    const h=make('h4','Agent interpretation — noncanonical');result.append(h,make('p',response.analysis||''));
    const list=(title,items,render)=>{const hd=make('h5',title);result.append(hd);const ul=make('ul');
      for(const item of items||[]){ul.append(make('li',render(item)))}result.append(ul)};
    list('Recorded source claims (not causal proof)',response.recorded_observations, x=>x.claim+' ('+x.kind+':'+x.id+')');
    list('Creative hypotheses',response.hypotheses,x=>x.title+': '+x.description);
    list('Uncertainties',response.uncertainties,x=>x);
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
  updateSubmit();return {setSelection,setStatus,setInquiryResult,setLocalInspection,setAuthorText:text=>{instruction.value=text},
    setOperation:choose,getAuthorText:()=>instruction.value,reset:()=>{anchors=[];actions=[];chips.replaceChildren();menu.replaceChildren();result.replaceChildren();status.textContent='No host-agent request prepared.';packet.value='';},
    destroy:()=>root.replaceChildren()};
 }
 global.AuteurStudioCreativePanel={createCreativePanel};
})(window);
