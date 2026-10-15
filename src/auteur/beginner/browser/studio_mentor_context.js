/* A read-only, evidence-labelled view of CURRENT Studio state; never an Identity owner. */
(function(global){
  'use strict';
  function slice(value,max){return typeof value==='string'?value.trim().slice(0,max):'';}
  function textItem(item){return item&&typeof item==='object'?item:null;}
  function project(state,focus,focusKind){
    if(!focus||typeof focus.id!=='string'||!focus.id||!slice(focus.title,120))return null;
    const items=Array.isArray(state?.items)?state.items:[];
    const candidate=state?.architecture;
    const nodes=Array.isArray(candidate?.nodes)?candidate.nodes:[];
    const links=Array.isArray(candidate?.links)?candidate.links:[];
    const candidateReady=state?.architectureSourceStatus===undefined||state.architectureSourceStatus==='ready';
    const sourceSha=candidateReady&&/^[a-f0-9]{64}$/.test(state?.architectureRequestSha||'')?
      state.architectureRequestSha:null;
    const vision=items.find(x=>x.id==='story-vision');
    const visionContent=slice(vision?.content,900);
    const selected=focusKind==='working'?items.find(x=>x.id===focus.id):null;
    const working=items.filter(x=>x.id!=='story-vision'&&x.kind!=='scene')
      .slice(0,8).map(x=>({id:x.id,title:slice(x.title,120),details:slice(x.content,180),
        authority:'author_working',sourceRef:'canvas/items/'+x.id}));
    let declaredEdges=[];
    if(focusKind==='candidate'&&sourceSha){
      declaredEdges=links.reduce((acc,edge,index)=>{
        if(edge?.source!==focus.id&&edge?.target!==focus.id)return acc;
        const counterpart=nodes.find(n=>n.id===(edge.source===focus.id?edge.target:edge.source));
        if(counterpart&&slice(edge.function,100)&&acc.length<8){
          acc.push({title:slice(counterpart.title,120),relationship:slice(edge.function,100),
            sourceRef:'links/'+index,authority:'agent_candidate'});
        }
        return acc;
      },[]);
    }
    const questions=sourceSha&&Array.isArray(candidate?.open_questions)?
      candidate.open_questions.slice(0,3).map((q,i)=>({text:slice(q,240),
        sourceRef:'open_questions/'+i,authority:'agent_candidate'})).filter(x=>x.text):[];
    return {
      focusId:focus.id,focusKind,sourceSha,
      selected:{title:slice(focus.title,120),details:slice(focus.content||focus.summary,400),
        authority:selected?'author_working':'agent_candidate',
        sourceRef:selected?'canvas/items/'+focus.id:(sourceSha?'nodes/'+focus.id:null)},
      storyVision:{text:visionContent,authority:visionContent?'author_working':'not_supplied',
        sourceRef:visionContent?'canvas/items/story-vision':null},
      working,declaredEdges,questions,
      acceptedIdentity:{status:'not_bound',note:'No accepted Identity source is bound to this Studio projection.'},
      genreEvidence:{status:'not_evaluated',note:'Use separately attributed Genre Pack or legacy evidence; candidate ideas are not genre rules.'}
    };
  }
  function hostContext(snapshot){
    if(!snapshot)return null;
    // A compact, labelled context; explicitly NOT a source of accepted story truth.
    return {source_sha:snapshot.sourceSha,focus_id:snapshot.focusId,
      focus_kind:snapshot.focusKind,focus:snapshot.selected,
      author_story_vision:snapshot.storyVision,working_ideas:snapshot.working.slice(0,5),
      proposed_relations:snapshot.declaredEdges,proposed_questions:snapshot.questions,
      accepted_identity_status:snapshot.acceptedIdentity.status,
      genre_evidence_status:snapshot.genreEvidence.status};
  }
  global.AuteurStudioMentorContext={project,hostContext};
})(window);
