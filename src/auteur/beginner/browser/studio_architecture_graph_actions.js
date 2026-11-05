/* Deterministic browser projection of recorded semantic graph targets.
 * This is presentation only; the server re-resolves every source identity.
 */
(function(global){
  'use strict';
  var TYPES={node:['nodes','id'],link:['links','id'],genre_interaction:['genre_interactions','id'],
    emotion_target:['emotion_targets','id'],complex_emotion:['complex_emotions','id'],
    genre_contract:['genre_contracts','genre_node_id'],phase:['phases','id']};
  var REFERENCES=[['node','parent_id','node'],['genre_contract','emotion_target_ids','emotion_target'],
    ['genre_contract','complex_emotion_ids','complex_emotion'],['phase','genre_activations','genre_contract'],
    ['phase','parallel_with','phase']];
  var VISIBLE_ACTIONS={
    node:['inspect','trace','challenge','explore','revise'],
    link:['inspect','trace','challenge','explore','revise'],
    genre_interaction:['inspect','trace','challenge','explore','revise'],
    emotion_target:['inspect','trace','explain','explore','revise'],
    complex_emotion:['inspect','trace','explain','explore','revise'],
    genre_contract:['inspect','trace','challenge','explore','revise'],
    phase:['inspect','trace','challenge','explore','revise'],
  };
  var LABELS={inspect:'Inspect recorded source',trace:'Trace recorded relationships',
    explain:'Explain this narrative role',challenge:'Challenge this design',
    explore:'Explore possibilities',compare:'Compare meanings',
    connect_to_ask:'Explore possible relationship',revise:'Request holistic revision'};
  function array(x){return Array.isArray(x)?x:[];}
  function address(candidate,a){
    var cfg=TYPES[a.kind];if(!cfg)throw Error('Unknown source kind');
    var rows=array(candidate?.[cfg[0]]);
    var i=rows.findIndex(x=>x&&x[cfg[1]]===a.id);
    if(i<0)throw Error('Selected source not recorded: '+a.kind+':'+a.id);
    var record=rows[i];
    var result={kind:a.kind,id:a.id,sourceRef:cfg[0]+'/'+i,record:record,
      label:record.title||record.emotion||record.id||record.genre_node_id||a.id};
    if(a.field){if(!Object.prototype.hasOwnProperty.call(record,a.field))throw Error('Component field not recorded');result.field=a.field;result.componentValue=record[a.field];}
    if(a.reference){
      var type=REFERENCES.find(x=>x[0]===a.kind&&x[1]===a.reference.field&&x[2]===a.reference.target_kind);
      if(!type)throw Error('Reference type not recorded');
      var values=type[1]==='genre_activations'?array(record.genre_activations).map(x=>x.genre_node_id):
        type[1]==='parent_id'?(record.parent_id?[record.parent_id]:[]):array(record[type[1]]);
      if(values.filter(x=>x===a.reference.target_id).length!==1)throw Error('Reference not uniquely recorded');
      result.reference={...a.reference,kind:'recorded_reference'};
    }
    return result;
  }
  function explicit(candidate){
    var links=array(candidate.links).map((l,i)=>({kind:'link',id:l.id,source:l.source,target:l.target,
      function:l.function,sourceRef:'links/'+i,authority:'recorded'}));
    var genres=array(candidate.genre_interactions).map((l,i)=>({kind:'genre_interaction',id:l.id,
      source:l.source_genre_id,target:l.target_genre_id,function:l.mechanism,
      interactionKind:l.kind,sourceRef:'genre_interactions/'+i,authority:'recorded'}));
    var refs=[];
    for(var x of REFERENCES){
      var ownerKind=x[0],field=x[1],targetKind=x[2],cfg=TYPES[ownerKind];
      array(candidate[cfg[0]]).forEach(function(owner,i){
        var ownerId=owner[cfg[1]],values=field==='parent_id'?(owner.parent_id?[owner.parent_id]:[]):
          field==='genre_activations'?array(owner.genre_activations).map(a=>a.genre_node_id):array(owner[field]);
        values.forEach(function(id){if(typeof id==='string')refs.push({kind:'recorded_reference',
          ownerKind:ownerKind,ownerId:ownerId,field:field,targetKind:targetKind,targetId:id,
          sourceRef:cfg[0]+'/'+i,authority:'recorded'});});
      });
    }
    return links.concat(genres,refs);
  }
  function incident(r,a){
    if(r.kind==='recorded_reference')return (r.ownerKind===a.kind&&r.ownerId===a.id)||
      (r.targetKind===a.kind&&r.targetId===a.id);
    return (r.kind===a.kind&&r.id===a.id)||
      (a.kind==='node'&&(r.source===a.id||r.target===a.id));
  }
  function between(r,a,b){
    if(r.kind==='recorded_reference')return ((r.ownerKind===a.kind&&r.ownerId===a.id&&r.targetKind===b.kind&&r.targetId===b.id)||
      (r.ownerKind===b.kind&&r.ownerId===b.id&&r.targetKind===a.kind&&r.targetId===a.id));
    return a.kind==='node'&&b.kind==='node'&&
      ((r.source===a.id&&r.target===b.id)||(r.source===b.id&&r.target===a.id));
  }
  function projectGraphSelection(candidate,selections){
    if(!candidate||candidate.schema_version!==2)throw Error('ArchitectureCandidate v2 required');
    if(!Array.isArray(selections)||!selections.length||selections.length>3)throw Error('Select one to three anchors');
    var anchors=selections.map(a=>address(candidate,a));
    var keys=anchors.map(a=>[a.kind,a.id,a.field||'',a.reference?.field||'',a.reference?.target_id||''].join(':'));
    if(new Set(keys).size!==keys.length)throw Error('Duplicate graph selection');
    var all=explicit(candidate);
    var recordedRelations=all.filter(r=>anchors.some(a=>incident(r,a)));
    var directRelations=anchors.length===2?all.filter(r=>between(r,anchors[0],anchors[1])):[];
    return {anchors:anchors,recordedRelations:recordedRelations,directRelations:directRelations,
      missingRelation:anchors.length===2&&!directRelations.length};
  }
  function traceRecordedRelationships(candidate,anchor,{maxHops=1}={}){
    if(maxHops!==1)throw Error('Only recorded one-hop relationships supported');
    return projectGraphSelection(candidate,[anchor]).recordedRelations;
  }
  function availableGraphActions(candidate,anchors){
    var model=projectGraphSelection(candidate,anchors),kind=model.anchors[0].kind;
    var operations=model.anchors.length===1?VISIBLE_ACTIONS[kind].slice():
      ['inspect','trace','challenge','explore','compare','revise'];
    if(model.anchors.length===2)operations.splice(operations.indexOf('compare'),0,'connect_to_ask');
    return operations.map((operation,i)=>({operation:operation,label:LABELS[operation],
      description:operation==='connect_to_ask'?(model.missingRelation?'No recorded relation; ask about a possibility':'Question a recorded connection'):
        operation==='revise'?'Prepares a complete, reviewable working revision':'Read or inquire without changing architecture',
      kind:i<4?'primary':'additional',mutatesWorking:false}));
  }
  global.AuteurStudioGraphActions={projectGraphSelection,traceRecordedRelationships,availableGraphActions};
})(window);
