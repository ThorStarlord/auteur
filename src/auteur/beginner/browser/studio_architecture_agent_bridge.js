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
      anchors:anchors.map(a=>{const copy={kind:a.kind,id:a.id};if(a.field)copy.field=a.field;if(a.field&&Number.isInteger(a.index))copy.index=a.index;
        if(a.reference)copy.reference={field:a.reference.field,target_kind:a.reference.target_kind,target_id:a.reference.target_id};return copy}),author_text:authorText};
  };
  async function prepareInquiry({anchors,operation,authorText,bookEvidence,fromDiscovery}){
    if(!['explain','challenge','explore','compare','connect_to_ask'].includes(operation))throw Error('revise is not an inquiry operation; only read-only operations allowed');
    const payload=graphIntent({anchors,operation,authorText}),token=++generation;
    // Book evidence travels as its own field, never inside the author's question.
    if(bookEvidence)payload.book_evidence={book_number:bookEvidence.book_number,element_id:bookEvidence.element_id,
      expected_book_request_sha256:bookEvidence.expected_book_request_sha256,
      expected_element_content_sha256:bookEvidence.expected_element_content_sha256};
    // A possibility taken from discovery is named by its request and possibility id; the owner checks it.
    if(fromDiscovery)payload.from_discovery={request_sha256:fromDiscovery.requestSha256,possibility_id:fromDiscovery.possibilityId};
    const result=await post(url('/inquiry/prepare'),payload);
    if(token===generation&&onInquiryResult)onInquiryResult(result);return result;
  }
  async function completeInquiry(response){const token=++generation;
    const result=await post(url('/inquiry/host-agent-response'),response);
    if(token===generation&&onInquiryResult)onInquiryResult(result);return result;
  }
  async function prepareRevision({anchors,authorText,selectedAlternative}){
    const intent=graphIntent({anchors,operation:'revise',authorText}),token=++generation;
    const body={instruction:authorText,graph_intent:intent};
    if(selectedAlternative){
      if(!selectedAlternative.inquiryRequestSha256||!selectedAlternative.hypothesisId)throw Error('Selected alternative needs its inquiry and ID');
      body.selected_alternative={inquiry_request_sha256:selectedAlternative.inquiryRequestSha256,hypothesis_id:selectedAlternative.hypothesisId};
    }
    const result=await post(url('/prepare'),body);
    if(token===generation&&onRevisionProjection)onRevisionProjection(result);return result;
  }
  async function refresh(){const token=++generation;const response=await fetch(url('/inquiry'));const result=await response.json();
    if(!response.ok)throw Error(result.error||'Inquiry refresh failed');
    if(token===generation&&onInquiryResult)onInquiryResult(result);return result;}
  return{prepareInquiry,completeInquiry,prepareRevision,refresh,reset:()=>{generation+=1}};
 }
 global.AuteurStudioAgentBridge={createArchitectureAgentBridge};
})(window);
