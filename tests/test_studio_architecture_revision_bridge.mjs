import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const path='src/auteur/beginner/browser/studio_architecture_revision_bridge.js';
const SHA='a'.repeat(64), NEXT='b'.repeat(64);
class Element {
  constructor(){this.hidden=true;this.open=false;this.listeners={};this.children=[]}
  addEventListener(k,cb){this.listeners[k]=cb}
  replaceChildren(...children){this.children=children}
  appendChild(child){this.children.push(child)}
}
function setup(){const context={window:{},Promise};vm.runInNewContext(readFileSync(path,'utf8'),context,{filename:path});const disclosure=new Element(),root=new Element();let active='canvas1',loads=0,rendered=0,destroyed=0;const api=context.window.AuteurStudioRevisionBridge.create({disclosure,root,getCanvasId:()=>active,loadModules:async()=>{loads++;return{compareArchitectureRevision:args=>{assert.equal(args.beforeRequestSha,SHA);assert.equal(args.expectedPriorSha,SHA);return{status:'ready'}},mountRevisionReview:()=>{rendered++;return{destroy:()=>{destroyed++}}}}}});const projection={status:'review_ready',candidate:{schema_version:2},candidate_request_sha256:SHA,review:{request_sha256:NEXT,prior_request_sha256:SHA,candidate:{schema_version:2},requested_change:'More wonder',preserved:{accepted_constraints:[]}}};return{api,disclosure,root,projection,stats:()=>({loads,rendered,destroyed}),setCanvas:v=>active=v}}
test('bridge reveals the experimental comparison only for a matched review_ready baseline',()=>{const s=setup();s.api.update({...s.projection,status:'awaiting_host_agent'},'canvas1');assert.equal(s.disclosure.hidden,true);s.api.update({...s.projection,review:{...s.projection.review,prior_request_sha256:NEXT}},'canvas1');assert.equal(s.disclosure.hidden,true);s.api.update(s.projection,'canvas1');assert.equal(s.disclosure.hidden,false);assert.equal(s.disclosure.open,false)});
test('opening loads real modules only upon explicit opt in',async()=>{const s=setup();s.api.update(s.projection,'canvas1');assert.equal(s.stats().loads,0);s.disclosure.open=true;s.disclosure.listeners.toggle();await new Promise(resolve=>setTimeout(resolve,0));assert.equal(s.stats().loads,1);assert.equal(s.stats().rendered,1)});
test('newer canvas invalidates old comparison without model call',async()=>{const s=setup();s.api.update(s.projection,'canvas1');s.setCanvas('canvas2');s.disclosure.open=true;s.disclosure.listeners.toggle();await new Promise(resolve=>setTimeout(resolve,0));assert.equal(s.stats().rendered,0)});
test('closing and invalidation destroy the previous view',async()=>{const s=setup();s.api.update(s.projection,'canvas1');s.disclosure.open=true;s.disclosure.listeners.toggle();await new Promise(resolve=>setTimeout(resolve,0));s.api.update({...s.projection,status:'awaiting_host_agent'},'canvas1');assert.equal(s.stats().destroyed,1);assert.equal(s.disclosure.hidden,true)});
