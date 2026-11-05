/* Host-agent-neutral graph intent bridge. Preparing a packet does not execute an agent. */
(function(global){'use strict';
 function createArchitectureAgentBridge({canvasId,fetchJson,readProjection,onInquiryResult,onRevisionProjection}={}){
  if(typeof canvasId!=='function'||typeof readProjection!=='function')throw Error('Graph agent bridge requires canvas identity and architecture projection');
  const post=fetchJson||(async(url,payload)=>{const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(payload)});const data=await response.json();if(!response.ok)throw Error(data.error||'Graph agent request failed');return data});
  let generation=0;
  const url=tail=>'/api/beginner/studio/canvases/'+encodeURIComponent(canvasId())+'/architecture'+tail;
  const graphIntent=({anchors,operation,authorText})=>{
    const sha=readProjection()?.candidate_request_sha256;
    if(!/^[a-f0-9]{64}$/.test(sha||''))throw Error('No current architecture source identity');
    if(!Array.isArray(anchors)||anchors.length<1||anchors.length>3)throw Error('One to three anchors required');
    if(typeof authorText!=='string'||!authorText.trim()||authorText.length>4000)throw Error('Meaningful bounded author intention required');
    return{version:1,canvas_id:canvasId(),operation,expected_candidate_request_sha256:sha,
      anchors:anchors.map(a=>{const copy={kind:a.kind,id:a.id};if(a.field)copy.field=a.field;
        if(a.reference)copy.reference={field:a.reference.field,target_kind:a.reference.target_kind,target_id:a.reference.target_id};return copy}),author_text:authorText};
  };
  async function prepareInquiry({anchors,operation,authorText}){
    if(!['explain','challenge','explore','compare','connect_to_ask'].includes(operation))throw Error('revise is not an inquiry operation; only read-only operations allowed');
    const payload=graphIntent({anchors,operation,authorText}),token=++generation;
    const result=await post(url('/inquiry/prepare'),payload);
    if(token===generation&&onInquiryResult)onInquiryResult(result);return result;
  }
  async function completeInquiry(response){const token=++generation;
    const result=await post(url('/inquiry/host-agent-response'),response);
    if(token===generation&&onInquiryResult)onInquiryResult(result);return result;
  }
  async function prepareRevision({anchors,authorText}){
    const intent=graphIntent({anchors,operation:'revise',authorText}),token=++generation;
    const result=await post(url('/prepare'),{instruction:authorText,graph_intent:intent});
    if(token===generation&&onRevisionProjection)onRevisionProjection(result);return result;
  }
  async function refresh(){const token=++generation;const response=await fetch(url('/inquiry'));const result=await response.json();
    if(!response.ok)throw Error(result.error||'Inquiry refresh failed');
    if(token===generation&&onInquiryResult)onInquiryResult(result);return result;}
  return{prepareInquiry,completeInquiry,prepareRevision,refresh,reset:()=>{generation+=1}};
 }
 global.AuteurStudioAgentBridge={createArchitectureAgentBridge};
})(window);
