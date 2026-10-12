/* Source-scoped, read-only focused unfolding adapter; never invokes a model. */
(function(global){
  'use strict';
  var roleMap={genre:'genre',trope:'trope',engine:'structure',structure:'structure',reader_experience:'emotion',
    theme:'theme',conflict:'conflict',relationship:'relationship',setting:'setting',premise:'premise',character:'other'};
  var allowedRoles=new Set(['emotion','trope','structure','genre','premise','theme','conflict',
    'setting','relationship','other']);
  var sourceSha=/^[a-f0-9]{64}$/;
  function nodeById(candidate,id){return (candidate.nodes||[]).find(function(n){return n.id===id;});}
  function recoverCandidateFocus(candidate,sha,focus,workingItems){
    if(!focus)return null;
    if(focus.kind==='candidate')return nodeById(candidate,focus.id)?focus.id:null;
    if(focus.kind!=='working')return null;
    var working=workingItems.find(function(item){return item.id===focus.id;});
    var origin=working&&working.proposal_origin;
    if(!origin||origin.request_sha!==sha||!/^links\/[0-9]+$/.test(origin.source_ref))return null;
    var index=Number(origin.source_ref.slice(6)),edge=(candidate.links||[])[index];
    if(!edge||!nodeById(candidate,origin.focus_id))return null;
    return edge.source===origin.focus_id?edge.target:edge.target===origin.focus_id?edge.source:null;
  }
  function projectLocalSuggestions(candidate,requestSha,focus,workingItems,dismissed,limit,offset){
    if(!candidate||!sourceSha.test(requestSha||''))return [];
    workingItems=workingItems||[];dismissed=dismissed||[];
    var currentId=recoverCandidateFocus(candidate,requestSha,focus,workingItems),nodes=candidate.nodes||[];
    if(!currentId)return [];
    var fromWorking=focus.kind==='working',self=fromWorking?workingItems.find(function(n){return n.id===focus.id;}):null;
    var priorSource=self&&self.proposal_origin&&self.proposal_origin.source_ref;
    var proposals=[];
    (candidate.links||[]).forEach(function(edge,i){
      if(!edge.function||!(edge.source===currentId||edge.target===currentId)||
          (fromWorking&&priorSource==='links/'+i))return;
      var reversed=edge.target===currentId,otherId=reversed?edge.source:edge.target,other=nodeById(candidate,otherId);
      if(!other||!other.title)return;
      var ref='links/'+i,code=requestSha+':'+currentId+':'+ref+':'+otherId;
      if(dismissed.includes(code)||workingItems.some(function(n){var o=n.proposal_origin;
        return o&&o.request_sha===requestSha&&o.source_ref===ref&&o.focus_id===currentId;
      }))return;
      proposals.push({id:code,focusId:currentId,originFocusId:focus.id,targetNodeId:other.id,title:other.title,
        description:other.summary||'',targetRole:roleMap[other.category]||'other',
        relationshipVerb:reversed?'related through “'+edge.function+'”':edge.function,
        sourceRef:ref,sourceKind:'proposal_edge',supportStatus:'source_backed_proposal',
        requestSha:requestSha,canonical:false});
    });
    var n=Math.max(0,Math.min(3,Number.isFinite(limit)?Math.floor(limit):3));
    var begin=Math.max(0,Math.floor(offset)||0);
    return proposals.slice(begin,begin+n);
  }
  function hash16(text){
    function fnv(str){var h=0x811c9dc5;for(var i=0;i<str.length;i++){
      h^=str.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;
    }return h.toString(16).padStart(8,'0');}
    return fnv(text)+fnv(text.split('').reverse().join(''));
  }
  function safePosition(position){
    var x=position&&position.x,y=position&&position.y;
    if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>1400||y<0||y>1040)throw Error('Invalid working position');
    return {x:x,y:y};
  }
  function buildAdoptionCommand(ghost,position){
    if(!ghost||!sourceSha.test(ghost.requestSha||'')||!/^links\/[0-9]+$/.test(ghost.sourceRef||'')||
       !allowedRoles.has(ghost.targetRole)||!ghost.focusId||!ghost.title||ghost.title.length>120)
      throw Error('Invalid source-bound suggestion sha / relation');
    var token=hash16(ghost.id),id='unfold-'+token;
    return {commandId:'adopt-'+token,
      payload:{item:{id:id,kind:'note',title:ghost.title,content:ghost.description||'',
        group:'Narrative Architecture',architecture_role:ghost.targetRole,
        proposal_origin:{request_sha:ghost.requestSha,source_ref:ghost.sourceRef,
          source_kind:'proposal_edge',focus_id:ghost.focusId}},position:safePosition(position)}};
  }
  function buildManualAnchorCommand(role,title,operationId,position){
    if(!allowedRoles.has(role))throw Error('Unknown authoring role');
    if(!title||!String(title).trim()||String(title).trim().length>120)throw Error('Invalid working idea title');
    if(!/^[a-z0-9][a-z0-9_-]{0,70}$/.test(operationId||''))throw Error('Invalid local operation id');
    return {commandId:'create-'+operationId,payload:{item:{id:operationId,kind:'note',title:String(title).trim(),content:'',
      group:'Narrative Architecture',architecture_role:role,proposal_origin:null},position:safePosition(position)}};
  }
  global.AuteurStudioUnfolding={projectLocalSuggestions:projectLocalSuggestions,buildAdoptionCommand:buildAdoptionCommand,
    buildManualAnchorCommand:buildManualAnchorCommand};
})(window);
