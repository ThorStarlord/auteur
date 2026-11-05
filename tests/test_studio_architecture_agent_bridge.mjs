import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const source=readFileSync(new URL('../src/auteur/beginner/browser/studio_architecture_agent_bridge.js',import.meta.url),'utf8');
const SHA='a'.repeat(64);
function setup(overrides={}){
  const window={};runInNewContext(source,{window,fetch:async()=>({ok:true,json:async()=>({status:'ready'})})});
  let canvas='story-one',candidateSha=SHA;
  const calls=[],inquiries=[],revisions=[];
  const bridge=window.AuteurStudioAgentBridge.createArchitectureAgentBridge({
    canvasId:()=>canvas,
    readProjection:()=>({candidate_request_sha256:candidateSha}),
    fetchJson:async(url,payload)=>{calls.push({url,payload});return {status:'awaiting_host_agent',request:payload}},
    onInquiryResult:p=>inquiries.push(p),
    onRevisionProjection:p=>revisions.push(p),
  });
  return {bridge,calls,inquiries,revisions,setCanvas:x=>canvas=x,setSha:x=>candidateSha=x};
}
test('read-only Explain and Explore prepare an inquiry packet, not an architecture revision',async()=>{
  const s=setup();
  await s.bridge.prepareInquiry({operation:'explore',authorText:'What alternatives?',
    anchors:[{kind:'node',id:'engine'}]});
  assert.equal(s.calls.length,1);
  assert.match(s.calls[0].url,/architecture\/inquiry\/prepare$/);
  assert.equal(s.calls[0].payload.operation,'explore');
  assert.equal(s.calls[0].payload.anchors[0].id,'engine');
  assert.equal(s.calls[0].payload.expected_candidate_request_sha256,SHA);
  assert.equal(s.revisions.length,0);
});
test('explicit holistic Revise uses existing prepare route with exact source-bound intent',async()=>{
  const s=setup();
  await s.bridge.prepareRevision({authorText:'Improve wonder holistically',
    anchors:[{kind:'link',id:'cost_link',field:'function'}]});
  assert.equal(s.calls.length,1);
  assert.match(s.calls[0].url,/architecture\/prepare$/);
  const p=s.calls[0].payload;
  assert.equal(p.instruction,'Improve wonder holistically');
  assert.equal(p.graph_intent.author_text,p.instruction);
  assert.equal(p.graph_intent.operation,'revise');
  assert.equal(p.graph_intent.anchors[0].field,'function');
  assert.equal(s.inquiries.length,0);
});
test('inquiry cannot be accidentally used as Revise',async()=>{
  const s=setup();
  await assert.rejects(s.bridge.prepareInquiry({operation:'revise',
    authorText:'A full new architecture',anchors:[{kind:'node',id:'engine'}]}),/not an inquiry/);
  assert.equal(s.calls.length,0);
});
test('unqualified source context, missing author question and too many anchors fail locally',async()=>{
  const s=setup();
  s.setSha(null);
  await assert.rejects(s.bridge.prepareInquiry({operation:'explore',authorText:'Question',
    anchors:[{kind:'node',id:'engine'}]}),/source identity/);
  assert.equal(s.calls.length,0);
});
test('returned signed response is only forwarded to explicit inquiry completion route',async()=>{
  const s=setup();
  await s.bridge.completeInquiry({request_sha256:'b'.repeat(64),text:'{}'});
  assert.match(s.calls[0].url,/architecture\/inquiry\/host-agent-response$/);
  assert.equal(s.calls[0].payload.request_sha256,'b'.repeat(64));
});
test('reset invalidates late responses after canvas switch',async()=>{
  const window={};runInNewContext(source,{window,fetch:async()=>({ok:true,json:async()=>({})})});
  let finish,seen=[];
  const bridge=window.AuteurStudioAgentBridge.createArchitectureAgentBridge({
    canvasId:()=> 'story-one',readProjection:()=>({candidate_request_sha256:SHA}),
    fetchJson:()=>new Promise(resolve=>finish=resolve),
    onInquiryResult:r=>seen.push(r),
  });
  const promise=bridge.prepareInquiry({operation:'challenge',authorText:'What is missing?',
    anchors:[{kind:'node',id:'engine'}]});
  bridge.reset();
  finish({status:'ready'});await promise;
  assert.equal(seen.length,0);
});
