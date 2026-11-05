import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const source=readFileSync(new URL('../src/auteur/beginner/browser/studio_architecture_creative_feedback.js',import.meta.url),'utf8');
const SHA='a'.repeat(64), NEXT='b'.repeat(64);
function setup(){
  const window={};runInNewContext(source,{window});
  let current={schema_version:2,nodes:[{id:'engine'}],links:[{id:'cost_link'}],emotion_targets:[]},
    canvas='story-one';
  const selected=[],opened=[],rendered=[];
  const controller=window.AuteurStudioCreativeFeedback.createCreativeFeedbackController({
    getCandidate:()=>current,getCanvasId:()=>canvas,
    selectGraphFocus:x=>selected.push(x),
    openHybridReview:x=>opened.push(x),
    renderInquiry:x=>rendered.push(x),
  });
  const anchor={kind:'link',id:'cost_link'};
  const receipt={canvas_id:canvas,expected_candidate_request_sha256:SHA,anchors:[anchor],
    operation:'revise',author_text:'Rebalance the relationship'};
  return{controller,selected,opened,rendered,anchor,receipt,
    changeCanvas:x=>canvas=x,changeCandidate:x=>current=x};
}
test('successful inquiry returns to recorded typed source selection',()=>{
  const s=setup();const projection={status:'ready',result:{intent:s.receipt,analysis:'An interpretation'}};
  assert.equal(s.controller.onInquiry(projection,SHA),true);
  assert.equal(s.selected[0].kind,'link');assert.equal(s.selected[0].id,'cost_link');
  assert.equal(s.rendered.length,1);assert.equal(s.opened.length,0);
});
test('inquiry result cannot focus an outdated candidate request SHA',()=>{
  const s=setup();const projection={status:'ready',result:{intent:s.receipt}};
  assert.equal(s.controller.onInquiry(projection,NEXT),false);assert.equal(s.selected.length,0);
});
test('inquiry cannot leak an old canvas selection',()=>{
  const s=setup();s.changeCanvas('other-story');
  assert.equal(s.controller.onInquiry({status:'ready',result:{intent:s.receipt}},SHA),false);
  assert.equal(s.selected.length,0);
});
test('holistic revision reopens the existing hybrid comparison at the selected link',()=>{
  const s=setup();const projection={status:'review_ready',candidate_request_sha256:SHA,
    review:{prior_request_sha256:SHA,graph_intent_receipt:s.receipt}};
  assert.equal(s.controller.onReviewReady(projection),true);
  assert.equal(s.opened[0].kind,'link');assert.equal(s.opened[0].id,'cost_link');
});
test('stale or unrelated review cannot claim selected context',()=>{
  const s=setup();assert.equal(s.controller.onReviewReady({status:'review_ready',
    candidate_request_sha256:NEXT,
    review:{prior_request_sha256:SHA,graph_intent_receipt:s.receipt}}),false);
  assert.equal(s.opened.length,0);
});
test('missing source remains visibly absent; never title-matches to a replacement',()=>{
  const s=setup();s.changeCandidate({schema_version:2,nodes:[{id:'replacement',title:'Cost Link'}],links:[]});
  assert.equal(s.controller.onInquiry({status:'ready',result:{intent:s.receipt}},SHA),true);
  assert.equal(s.selected.length,0);
});
test('destroy makes the controller inert',()=>{
  const s=setup();s.controller.destroy();
  assert.equal(s.controller.onReviewReady({status:'review_ready',candidate_request_sha256:SHA,
    review:{prior_request_sha256:SHA,graph_intent_receipt:s.receipt}}),false);
  assert.equal(s.opened.length,0);
});
