import test from 'node:test';import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';import vm from 'node:vm';
const window={};vm.runInNewContext(readFileSync(new URL('../src/auteur/beginner/browser/studio_agent_handoff.js',import.meta.url),'utf8'),{window});
const api=window.AuteurStudioAgentHandoff;
const request={request_sha256:'a'.repeat(64)};
test('manual request never implies a connected executor',()=>{
 const p=api.present({status:'awaiting_host_agent',request},{studio_architecture:{attached:false}});
 assert.equal(p.mode,'manual_required');assert.match(p.message,/coding agent/i);
 assert.doesNotMatch(p.message,/generation in progress/i);
});
test('an existing proposal remains available during another request',()=>{
 const p=api.present({status:'awaiting_host_agent',request,candidate:{summary:'Earlier idea'}},null);
 assert.equal(p.mode,'manual_required');assert.equal(p.hasPreviousProposal,true);
});
test('ready, stale, review, and inactive presentations are truthful',()=>{
 assert.equal(api.present({status:'ready',candidate:{summary:'ready'}},null).mode,'ready');
 assert.equal(api.present({status:'review_ready',review:{}},null).mode,'review_ready');
 assert.equal(api.present({status:'stale',candidate:{summary:'old'}},null).mode,'stale');
 assert.equal(api.present({status:'not_started'},null).mode,'not_started');
});
test('poll stops when request or canvas changed and does not invoke stale updates',async()=>{
 let calls=0;let key='canvas-1:'+request.request_sha256;
 const outcome=await api.poll({key,getKey:()=>key,read:async()=>{calls++;key='canvas-2:'+request.request_sha256;return {status:'awaiting_host_agent'};},delay:async()=>{},maxAttempts:3});
 assert.equal(outcome.reason,'context_changed');assert.equal(calls,1);
});
test('poll detects validated response, supports stop and bounded exhaustion',async()=>{
 let count=0;const key='canvas-1:a';
 const ready=await api.poll({key,getKey:()=>key,read:async()=>++count===2?{status:'ready'}:{status:'awaiting_host_agent'},delay:async()=>{},maxAttempts:4});
 assert.equal(ready.reason,'ready');assert.equal(count,2);
 const exhausted=await api.poll({key,getKey:()=>key,read:async()=>({status:'awaiting_host_agent'}),delay:async()=>{},maxAttempts:2});
 assert.equal(exhausted.reason,'exhausted');
 let stop=true;
 const stopped=await api.poll({key,getKey:()=>key,shouldStop:()=>stop,read:async()=>{throw Error('must not fetch');},delay:async()=>{}});
 assert.equal(stopped.reason,'stopped');
});