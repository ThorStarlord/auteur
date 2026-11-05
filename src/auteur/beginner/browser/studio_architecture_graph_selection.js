/* Source-identifiable graph selection with an equivalent linear relationship index. */
(function(global){'use strict';
 function createGraphSelectionController({getCandidate,getRequestSha,graphRoot,indexRoot,inspectorRoot,onSelect}){
  if(!getCandidate||!getRequestSha||!graphRoot||!indexRoot||!inspectorRoot||!onSelect)throw Error('Graph selection dependencies unavailable');
  const doc=indexRoot.ownerDocument||document;
  let anchors=[],sourceSha=getRequestSha()||null,destroyed=false;
  const make=(tag,text)=>{const e=doc.createElement(tag);if(text!==undefined)e.textContent=text;return e;};
  const filter=make('input');filter.type='text';filter.setAttribute('aria-label','Filter relationships');filter.placeholder='Find a recorded relationship';
  const list=make('div');list.setAttribute('aria-label','Recorded relationship index');
  indexRoot.append(filter,list);
  const kindMap={node:'nodes',link:'links',genre_interaction:'genre_interactions',emotion_target:'emotion_targets',
   complex_emotion:'complex_emotions',genre_contract:'genre_contracts',phase:'phases'};
  const idKey=kind=>kind==='genre_contract'?'genre_node_id':'id';
  const same=(a,b)=>a.kind===b.kind&&a.id===b.id&&(a.field||'')===(b.field||'')&&
   JSON.stringify(a.reference||null)===JSON.stringify(b.reference||null);
  function exists(a){const c=getCandidate();if(!c||c.schema_version!==2)return false;
   const row=(c[kindMap[a.kind]]||[]).find(x=>x[idKey(a.kind)]===a.id);if(!row)return false;
   if(a.field&&!Object.prototype.hasOwnProperty.call(row,a.field))return false;
   if(a.reference){const field=a.reference.field,v=row[field];
    const values=field==='genre_activations'?Array.isArray(v)?v.map(x=>x.genre_node_id):[]:
       field==='parent_id'?(v?[v]:[]):Array.isArray(v)?v:[];
    if(values.filter(x=>x===a.reference.target_id).length!==1)return false;
   }return true;
  }
  function select(anchor,{append=false}={}){
   if(destroyed) return [];
   const next={kind:anchor.kind,id:anchor.id};if(anchor.field)next.field=anchor.field;
   if(anchor.reference)next.reference={...anchor.reference};
   if(!exists(next))throw Error('Selected source not recorded on current candidate');
   if(getRequestSha()!==sourceSha){sourceSha=getRequestSha();anchors=[];onSelect([]);}
   let newAnchors=append?anchors.slice():[];
   if(!newAnchors.some(x=>same(x,next)))newAnchors.push(next);
   if(newAnchors.length>3)throw Error('Select at most three semantic anchors');
   anchors=newAnchors;renderComponents();onSelect(anchors.slice());return anchors.slice();
  }
  function clear(){anchors=[];renderComponents();onSelect([])}
  function labelledField(field){return field.replace(/_/g,' ').replace(/\b\w/,x=>x.toUpperCase());}
  function renderComponents(){inspectorRoot.replaceChildren();const a=anchors.at(-1);if(!a)return;
   const rows=getCandidate()?.[kindMap[a.kind]]||[],record=rows.find(x=>x[idKey(a.kind)]===a.id);
   if(!record)return;
   const h=make('h4','Components of '+(record.title||record.id||record.genre_node_id));inspectorRoot.append(h);
   Object.keys(record).filter(k=>k!=='id'&&k!=='genre_node_id').forEach(field=>{
    const b=make('button',labelledField(field));b.type='button';b.dataset.componentField=field;
    b.title=typeof record[field]==='string'?record[field].slice(0,350):'Inspect recorded component';
    b.addEventListener('click',()=>select({kind:a.kind,id:a.id,field},{append:false}));
    inspectorRoot.append(b);
   });
  }
  function renderIndex(){const focus=doc.activeElement===filter;const value=filter.value.toLowerCase();list.replaceChildren();
   const c=getCandidate();if(!c||c.schema_version!==2)return;
   const items=[];
   (c.links||[]).forEach(edge=>items.push({kind:'link',id:edge.id,
    text:(edge.id+' '+edge.source+' → '+edge.target+' : '+edge.function)}));
   (c.genre_interactions||[]).forEach(edge=>items.push({kind:'genre_interaction',id:edge.id,
    text:edge.id+' '+edge.source_genre_id+' → '+edge.target_genre_id+' : '+edge.mechanism}));
   (c.genre_contracts||[]).forEach(owner=>{
    for(const [field,kind] of [['emotion_target_ids','emotion_target'],['complex_emotion_ids','complex_emotion']]){
     for(const id of owner[field]||[])items.push({kind:'genre_contract',id:owner.genre_node_id,
       reference:{field,target_kind:kind,target_id:id},text:owner.genre_node_id+' '+field+' → '+id});
    }
   });
   (c.phases||[]).forEach(owner=>{
    for(const entry of owner.genre_activations||[])items.push({kind:'phase',id:owner.id,
      reference:{field:'genre_activations',target_kind:'genre_contract',target_id:entry.genre_node_id},
      text:owner.id+' activates '+entry.genre_node_id});
    for(const id of owner.parallel_with||[])items.push({kind:'phase',id:owner.id,
      reference:{field:'parallel_with',target_kind:'phase',target_id:id},text:owner.id+' parallel to '+id});
   });
   (c.nodes||[]).forEach(owner=>{if(owner.parent_id)items.push({kind:'node',id:owner.id,
     reference:{field:'parent_id',target_kind:'node',target_id:owner.parent_id},text:owner.id+' child of '+owner.parent_id});});
   items.filter(item=>item.text.toLowerCase().includes(value)).slice(0,250).forEach(item=>{
    const b=make('button',item.text);b.type='button';b.dataset.graphRelationKind=item.kind;b.dataset.graphRelationId=item.id;
    b.addEventListener('click',()=>select(item));list.append(b);
   });
   if(!list.children.length)list.append(make('p','No recorded relations match this filter.'));
   if(focus)filter.focus();
  }
  const graphClick=e=>{const target=e.target?.closest?.('[data-architecture-link-id],[data-genre-interaction-id]');if(!target)return;
   const id=target.getAttribute('data-architecture-link-id')||target.getAttribute('data-genre-interaction-id');
   const kind=target.hasAttribute('data-architecture-link-id')?'link':'genre_interaction';
   try{select({kind,id},{append:e.shiftKey||e.ctrlKey});e.stopPropagation()}catch(_){clear()}
  };
  const onFilter=()=>renderIndex();
  graphRoot.addEventListener('click',graphClick);filter.addEventListener('input',onFilter);
  function onCandidateChange(){if(getRequestSha()!==sourceSha){sourceSha=getRequestSha();clear()}
    else if(anchors.some(a=>!exists(a)))clear();renderIndex();renderComponents()}
  function destroy(){destroyed=true;graphRoot.removeEventListener('click',graphClick);filter.removeEventListener('input',onFilter);
    indexRoot.replaceChildren();inspectorRoot.replaceChildren();anchors=[];}
  renderIndex();return {select,clear,onCandidateChange,destroy,getSelection:()=>anchors.slice()};
 }
 global.AuteurStudioGraphSelection={createGraphSelectionController};
})(window);
