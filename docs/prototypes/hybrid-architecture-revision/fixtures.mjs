/* Recorded PR #510 candidate is the baseline; all After values are synthetic. */
import {compareArchitectureRevision} from './compare.mjs';
const ROOT='/docs/qualification-evidence/agent-first-ontology-20261103/';
const NEW_SHA='d'.repeat(64); // Explicitly synthetic, never a real HostAgentRequest.
export async function loadReviewFixture(name='holistic',{fetcher=fetch}={}) {
  const read=async file=>{
    const response=await fetcher(ROOT+file);
    if (!response.ok) throw new Error('Fixture unavailable: '+file);
    return response.json();
  };
  const [before,request]=await Promise.all([
    read('rich-vision-candidate.json'),read('rich-vision-request.json'),
  ]);
  if (before.schema_version!==2 || !/^[a-f0-9]{64}$/.test(request.request_sha256)) {
    throw new Error('Recorded fixture contract unavailable');
  }
  const after=structuredClone(before);
  const edit=(collection,id,field,value)=>{
    const key=collection==='genre_contracts'?'genre_node_id':'id';
    const entry=after[collection].find(x=>x[key]===id);
    if (!entry) throw new Error('Fixture element not found: '+collection+'/'+id);
    entry[field]=value;
  };
  if (name==='holistic'||name==='semantic') {
    edit('nodes','memory_economy','summary',
      'The cost of knowledge remains, while extraordinary discoveries also create collective wonder.');
    edit('emotion_targets','wonder','intended_effect',
      'Wonder dominates dread without removing the price of discovery.');
    edit('genre_contracts','literary_mystery','narrative_engine',
      'Each answer uncovers beauty and raises an intimate mystery.');
    edit('phases',after.phases[0].id,'narrative_function',
      'Establish wonder and loss as mutually reinforcing promises.');
    edit('complex_emotions','uneasy_wonder','context',
      'Beauty is discovered without denying the memories lost.');
  }
  if (name==='holistic'||name==='redirect') {
    edit('links','engine_drives_cost','target','wonder_promise');
  }
  if (name==='summary') after.summary='Synthetic summary-only change: more wonder.';
  if (!['holistic','semantic','redirect','summary','noop'].includes(name)) {
    throw new Error('Unknown synthetic fixture variant');
  }
  const requestedChange='Make wonder dominant while preserving mystery and the cost of discovery.';
  return {
    comparison:compareArchitectureRevision({
      before,after,beforeRequestSha:request.request_sha256,afterRequestSha:NEW_SHA,
      expectedPriorSha:request.request_sha256,requestedChange,
    }),
    label:'RECORDED BASELINE / SYNTHETIC PROPOSED REVISION — no agent executed',
    synthetic:true,
  };
}
