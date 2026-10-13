/* Read-only Narrative Architecture explanation projection; source-scoped to request SHA. */
(function(global){
  'use strict';
  var types={genre:'genres',trope:'tropes',structure:'structure',engine:'structure',reader_experience:'emotions'};
  function project(candidate,requestSha,packEvidence){
    var c=candidate||{}, nodes=c.nodes||[],contracts=c.genre_contracts||[],phases=c.phases||[];
    var packet={requestSha:requestSha||null,packCoverage:packEvidence?'supplied':'unknown',
      genres:[],tropes:[],structure:[],emotions:[],timeline:[],links:[]};
    var nmap={};nodes.forEach(function(n){nmap[n.id]=n;});
    function name(id){return nmap[id]?nmap[id].title:id;}
    function add(facet,entry){packet[facet].push(entry);return entry;}
    var keys={};
    function record(facet,entry){keys[facet+':'+entry.key]=entry;return add(facet,entry);}
    function link(fromFacet,fromKey,toFacet,toKey,verb,sourceRef,sourceKind,details){
      if(!sourceRef||!verb)return;
      packet.links.push({id:requestSha+':'+sourceRef+':'+fromKey+':'+toKey,
        fromFacet:fromFacet,fromKey:fromKey,targetFacet:toFacet,targetKey:toKey,
        relationVerb:verb,sourceRef:sourceRef,sourceKind:sourceKind||'architecture_proposal',
        supportStatus:'source_backed_proposal',explanation:details||verb,requestSha:requestSha});
    }
    nodes.forEach(function(n){
      if(n.category==='genre'){
        var hasContract=contracts.some(function(c){return c.genre_node_id===n.id;});
        if(!hasContract)record('genres',{key:'genre-node:'+n.id,title:n.title,detail:n.summary||'',nodeId:n.id,
          sourceRef:'nodes/'+n.id,role:'proposed',coverageMessage:'No verified pack attached to this proposal.'});
      }
      if(n.category==='trope')record('tropes',{key:'trope-node:'+n.id,title:n.title,detail:n.summary||'',nodeId:n.id,
        sourceRef:'nodes/'+n.id,role:'node',ownerGenreId:null});
      if(['structure','engine'].includes(n.category))record('structure',{key:'structure-node:'+n.id,title:n.title,
        detail:n.summary||'',nodeId:n.id,sourceRef:'nodes/'+n.id,role:n.category});
    });
    contracts.forEach(function(c){
      var id=c.genre_node_id,g='genre:'+id;
      var evidence=packEvidence&&packEvidence[id];
      record('genres',{key:g,title:name(id),detail:c.narrative_engine||'',nodeId:id,
        sourceRef:'genre_contracts/'+id,role:c.role||'proposed',contract:c,
        coverageMessage:evidence&&evidence.verified?'Verified external genre evidence attached: '+evidence.source_ref:
          'No verified pack attached. These are working proposal interpretations, not universal genre requirements.'});
      (c.trope_functions||[]).forEach(function(phrase,i){
        var key='trope:'+id+':'+i,src='genre_contracts/'+id+'/trope_functions/'+i;
        record('tropes',{key:key,title:phrase,detail:phrase,ownerGenreId:id,sourceRef:src,role:'contract function'});
        link('genres',g,'tropes',key,'lists trope function',src,'genre_contract');
      });
      [['narrative_engine',c.narrative_engine],['structural_pattern',c.structural_pattern]].forEach(function(part,i){
        if(!part[1])return;
        var key='structure:'+id+':'+i,src='genre_contracts/'+id+'/'+part[0];
        record('structure',{key:key,title:part[1],detail:part[1],ownerGenreId:id,sourceRef:src,role:part[0]});
        link('genres',g,'structure',key,'describes '+part[0].replace(/_/g,' '),src,'genre_contract');
      });
      (c.emotion_target_ids||[]).forEach(function(emotionId){
        var e=(c.emotion_target_ids||[]).indexOf(emotionId),src='genre_contracts/'+id+'/emotion_target_ids/'+e;
        link('genres',g,'emotions','emotion:'+emotionId,'targets reader emotion',src,'genre_contract');
      });
    });
    (c.emotion_targets||[]).forEach(function(t){
      record('emotions',{key:'emotion:'+t.id,title:t.emotion,detail:t.intended_effect||'',sourceRef:'emotion_targets/'+t.id,role:t.role});
    });
    phases.forEach(function(p){
      record('timeline',{key:'phase:'+p.id,title:p.title,detail:p.narrative_function||'',phaseId:p.id,
        sourceRef:'phases/'+p.id,role:'phase'});
      (p.genre_activations||[]).forEach(function(a){
        var id=a.genre_node_id;
        (a.trope_functions||[]).forEach(function(t,i){
          var key='phase-trope:'+p.id+':'+id+':'+i,src='phases/'+p.id+'/genre_activations/'+id+'/trope_functions/'+i;
          record('tropes',{key:key,title:t,detail:t,ownerGenreId:id,phaseId:p.id,sourceRef:src,role:'phase trope'});
          link('timeline','phase:'+p.id,'tropes',key,'uses local trope function',src,'phase');
        });
        if(a.structural_function){
          var key='phase-structure:'+p.id+':'+id,src='phases/'+p.id+'/genre_activations/'+id+'/structural_function';
          record('structure',{key:key,title:a.structural_function,detail:a.structural_function,
            ownerGenreId:id,phaseId:p.id,sourceRef:src,role:'phase structure'});
          link('timeline','phase:'+p.id,'structure',key,'uses local structural function',src,'phase');
        }
      });
    });
    function nodeRef(nodeId){
      var n=nmap[nodeId];if(!n)return null;
      var facet=types[n.category];if(!facet)return null;
      if(facet==='genres')return {facet:facet,key:contracts.some(function(c){return c.genre_node_id===nodeId;})?'genre:'+nodeId:'genre-node:'+nodeId};
      return {facet:facet,key:(facet==='tropes'?'trope-node:':'structure-node:')+nodeId};
    }
    (c.links||[]).forEach(function(e,i){
      var from=nodeRef(e.source),to=nodeRef(e.target);
      if(from&&to&&e.function)link(from.facet,from.key,to.facet,to.key,e.function,'links/'+i,'proposal_edge');
    });
    // Only links with both original source-local endpoints are navigable.
    packet.links=packet.links.filter(function(l){return keys[l.fromFacet+':'+l.fromKey]&&keys[l.targetFacet+':'+l.targetKey];});
    return packet;
  }
  function resolve(packet,facet,key,expectedRequestSha){
    if(!packet||!expectedRequestSha||packet.requestSha!==expectedRequestSha||!
        ['genres','tropes','structure','emotions','timeline'].includes(facet))return null;
    return packet[facet].find(function(e){return e.key===key;})||null;
  }
  function linksFor(packet,ref){
    if(!packet||!ref||!resolve(packet,ref.facet,ref.key,packet.requestSha))return [];
    var output=[];
    packet.links.forEach(function(l){
      if(l.fromFacet===ref.facet&&l.fromKey===ref.key)output.push(Object.assign({},l,{direction:'forward'}));
      else if(l.targetFacet===ref.facet&&l.targetKey===ref.key){
        output.push(Object.assign({},l,{id:l.id,direction:'reverse',relationVerb:'related through “'+l.relationVerb+'”',
          fromFacet:l.targetFacet,fromKey:l.targetKey,targetFacet:l.fromFacet,targetKey:l.fromKey}));
      }
    });
    return output;
  }
  global.AuteurStudioExplanations={project:project,resolve:resolve,linksFor:linksFor};
})(window);
