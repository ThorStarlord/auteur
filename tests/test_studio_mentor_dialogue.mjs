import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../src/auteur/beginner/browser/studio_mentor_dialogue_controller.js',import.meta.url),'utf8');
class El{
 constructor(id=''){this.id=id;this.hidden=true;this.value='';this.children=[];this.textContent='';
   this.disabled=false;this.events={};this.attributes={};this.style={};}
 replaceChildren(...items){this.children=items}
 appendChild(element){this.children.push(element);return element}
 setAttribute(k,v){this.attributes[k]=v}
 addEventListener(k,v){this.events[k]=v}
}
function fixture(){
 const ids=['unfolding-mentor-dialogue','mentor-author-reply','mentor-send','mentor-refresh',
  'mentor-complete','mentor-dismiss','mentor-status','mentor-request','mentor-advice',
  'mentor-handoff','mentor-response','mentor-working-preview','mentor-working-title',
  'mentor-working-content','mentor-keep','mentor-keep-status'];
 const elements=new Map(ids.map(id=>[id,new El(id)]));
 const doc={getElementById:id=>elements.get(id),createElement:t=>new El(t)};
 const win={};new Function('window','document',source)(win,doc);
 const sha='a'.repeat(64);
 const state={workspace:'architecture',view:'architecture',architectureFacet:'overview',
   fullArchitectureDisplay:'focus',architectureRequestSha:sha,
   unfoldingFocus:{kind:'candidate',id:'g'}};
 const remote={ready:true,failed:false,canvasId:'canvas-test',revision:3};
 const requests=[],statuses=[],saved=[];let dirty=false,flushed=0;
 const advice={focus_id:'g',kind:'explore',summary:'Three distinct options',
   question:'What future should the hero create?',challenge_basis:'conditional_hypothesis',
   directions:[{id:'social',title:'Community restoration',divergence_axis:'social_scale',
     mechanism:'Institutions reproduce help',consequence:'More people can act',
     tradeoff:'The hero shares agency',distinguishing_factor:'Social systems, not solo power',
     source_status:'agent_hypothesis',source_refs:[]}]};
 const pending={status:'awaiting_host_agent',request:{schema:'auteur_host_agent_request_v1',
   request_sha256:'b'.repeat(64)},focus_id:'g',focus_kind:'candidate'};
 const ready={status:'ready',advice,focus_id:'g',focus_kind:'candidate',
   mentor_request_sha256:'b'.repeat(64),canvas_revision:3,
   candidate_request_sha256:'a'.repeat(64),author_reply:''};
 const bridge={state:()=>state,remote:()=>remote,canNavigate:()=>!dirty,
   flush:async()=>{flushed++},
   fetch:async(url,config)=>{
     requests.push({url,config});
     return {ok:true,json:async()=>url.endsWith('/prepare')?pending:
       url.endsWith('/host-agent-response')?ready:ready};
   },
   apiJson:async r=>r.json(),status:s=>statuses.push(s),
   saveWorking:async choice=>{saved.push(choice);return true}};
 const ctrl=win.AuteurStudioMentorDialogueController.create(bridge);
 return {ctrl,elements,state,remote,requests,statuses,saved,pending,ready,bridge,
   setDirty:v=>{dirty=v},flushed:()=>flushed};
}
function p(){return {focusId:'g',sourceSha:'a'.repeat(64)};}

test('passive render is silent and concealed until explicit author action',()=>{
 const f=fixture();f.ctrl.render();
 assert.equal(f.elements.get('unfolding-mentor-dialogue').hidden,true);
 assert.equal(f.requests.length,0);
});
test('explicit explore prepares local host-agent request, not an auto provider call',async()=>{
 const f=fixture();await f.ctrl.open(p(),'explore');
 assert.equal(f.flushed(),1);assert.equal(f.requests.length,1);
 assert.match(f.requests[0].url,/\/mentor\/prepare$/);
 const posted=JSON.parse(f.requests[0].config.body);
 assert.deepEqual(posted,{focus_id:'g',focus_kind:'candidate',purpose:'explore',author_reply:''});
 assert.equal(f.elements.get('mentor-handoff').hidden,false);
 assert.match(f.elements.get('mentor-status').textContent,/no provider was called automatically/);
});
test('natural-language reply is passed as author text without story mutation',async()=>{
 const f=fixture();await f.ctrl.open(p(),'question');
 f.elements.get('mentor-author-reply').value='Protect a hopeful paladin with independent companions';
 f.elements.get('mentor-author-reply').events.input();
 await f.elements.get('mentor-send').events.click();
 assert.equal(f.requests.length,2);
 assert.equal(JSON.parse(f.requests[1].config.body).purpose,'followup');
 assert.equal(JSON.parse(f.requests[1].config.body).author_reply,
   'Protect a hopeful paladin with independent companions');
});
test('validated advice stays visually provisional and never persists a story change',async()=>{
 const f=fixture();await f.ctrl.open(p(),'explore');
 f.elements.get('mentor-response').value='{"schema":"auteur_host_agent_response_v1"}';
 await f.ctrl.complete();
 assert.match(f.requests.at(-1).url,/\/mentor\/host-agent-response$/);
 assert.equal(f.elements.get('mentor-handoff').hidden,true);
 const advice=f.elements.get('mentor-advice').children;
 assert.ok(advice.some(x=>x.textContent.includes('Noncanonical')));
 assert.ok(advice.some(x=>x.textContent.includes('Three distinct options')));
 assert.ok(advice.some(x=>x.textContent.includes('Nothing here changes')));
});
test('malformed response is rejected before network call',async()=>{
 const f=fixture();await f.ctrl.open(p(),'explore');
 f.elements.get('mentor-response').value='not valid JSON';
 await f.ctrl.complete();
 assert.equal(f.requests.length,1);
 assert.match(f.elements.get('mentor-status').textContent,/HostAgentResponse/);
});
test('stale focused source and dirty author editor prevent preparing mentor',async()=>{
 const f=fixture();f.setDirty(true);await f.ctrl.open(p(),'question');
 assert.equal(f.requests.length,0);
 assert.match(f.elements.get('mentor-status').textContent,/Save working-idea edits/);
 f.setDirty(false);f.state.architectureRequestSha='c'.repeat(64);
 await f.ctrl.open(p(),'explore');
 assert.equal(f.requests.length,0);
});
test('focus changes conceal mentor and preserve the typed reply',async()=>{
 const f=fixture();await f.ctrl.open(p(),'explore');
 f.elements.get('mentor-author-reply').value='My own unpublished intention';
 f.elements.get('mentor-author-reply').events.input();
 f.state.unfoldingFocus={kind:'candidate',id:'another'};f.ctrl.render();
 assert.equal(f.elements.get('unfolding-mentor-dialogue').hidden,true);
 f.state.unfoldingFocus={kind:'candidate',id:'g'};
 await f.ctrl.resume(p());
 assert.equal(f.elements.get('mentor-author-reply').value,'My own unpublished intention');
});

test('AI alternative stays read-only until author reviews and keeps it',async()=>{
 const f=fixture();await f.ctrl.open(p(),'explore');
 f.elements.get('mentor-response').value='{}';await f.ctrl.complete();
 const box=f.elements.get('mentor-advice').children.find(x=>
   x.children.some(y=>y.textContent==='Review as working idea'));
 assert.ok(box);
 box.children.find(y=>y.textContent==='Review as working idea').events.click();
 assert.equal(f.elements.get('mentor-working-preview').hidden,false);
 assert.equal(f.saved.length,0);
 f.elements.get('mentor-working-title').value='My revised direction';
 f.elements.get('mentor-working-content').value='I choose this hopeful variation';
 await f.elements.get('mentor-keep').events.click();
 assert.equal(f.saved.length,1);
 assert.equal(f.saved[0].title,'My revised direction');
 assert.equal(f.saved[0].content,'I choose this hopeful variation');
 assert.equal(f.saved[0].sourceRef,'directions/social');
 assert.equal(f.saved[0].mentorRequestSha,'b'.repeat(64));
});

test('stale canvas prevents even the working preview, not just saving',async()=>{
 const f=fixture();await f.ctrl.open(p(),'explore');f.elements.get('mentor-response').value='{}';
 await f.ctrl.complete();f.remote.revision=4;
 const box=f.elements.get('mentor-advice').children.find(x=>
   x.children.some(y=>y.textContent==='Review as working idea'));
 box.children.find(y=>y.textContent==='Review as working idea').events.click();
 assert.equal(f.elements.get('mentor-working-preview').hidden,true);
 assert.match(f.elements.get('mentor-status').textContent,/stale/);
 assert.equal(f.saved.length,0);
});

test('author reply and AI interpretation stay separately attributed in preview',async()=>{
 const f=fixture();f.ready.author_reply='Keep the protagonist beloved';
 f.ready.advice.author_reply_interpretation='Heroism becomes an enabling social force';
 await f.ctrl.open(p(),'question');f.elements.get('mentor-response').value='{}';
 await f.ctrl.complete();
 const button=f.elements.get('mentor-advice').children.find(x=>
   x.textContent==='Review interpretation as working idea');
 assert.ok(button);button.events.click();
 assert.match(f.elements.get('mentor-working-content').value,/AUTHOR ANSWER \(verbatim\)/);
 assert.match(f.elements.get('mentor-working-content').value,/Keep the protagonist beloved/);
 assert.match(f.elements.get('mentor-working-content').value,/AI INTERPRETATION/);
 assert.equal(f.saved.length,0);
});

test('ready advice becomes visibly stale after working-canvas revision changes',async()=>{
 const f=fixture();await f.ctrl.open(p(),'explore');
 f.elements.get('mentor-response').value='{}';await f.ctrl.complete();
 assert.ok(f.elements.get('mentor-advice').children.length>0);
 f.remote.revision++;
 f.ctrl.render();
 assert.equal(f.elements.get('mentor-advice').children.length,0);
 assert.equal(f.elements.get('mentor-working-preview').hidden,true);
 assert.equal(f.elements.get('mentor-complete').disabled,true);
 assert.match(f.elements.get('mentor-status').textContent,/advice is stale/);
 assert.equal(f.saved.length,0);
});

test('refreshing a stale server result cannot resurrect old ready advice',async()=>{
 const f=fixture();await f.ctrl.open(p(),'explore');
 f.elements.get('mentor-response').value='{}';await f.ctrl.complete();
 assert.ok(f.elements.get('mentor-advice').children.length>0);
 f.bridge.fetch=async()=>({
   ok:true,json:async()=>({status:'stale',focus_id:'g',focus_kind:'candidate'})
 });
 await f.ctrl.resume(p());
 assert.equal(f.elements.get('mentor-advice').children.length,0);
 assert.match(f.elements.get('mentor-status').textContent,/response is stale/);
 assert.equal(f.saved.length,0);
});

test('dirty working editor cannot be discarded by keeping a mentor suggestion',async()=>{
 const f=fixture();
 await f.ctrl.open(p(),'explore');
 f.elements.get('mentor-response').value='{}';
 await f.ctrl.complete();
 const box=f.elements.get('mentor-advice').children.find(x=>
   x.children.some(y=>y.textContent==='Review as working idea'));
 box.children.find(y=>y.textContent==='Review as working idea').events.click();
 assert.equal(f.elements.get('mentor-working-preview').hidden,false);
 f.setDirty(true);
 await f.elements.get('mentor-keep').events.click();
 assert.equal(f.saved.length,0);
 assert.match(f.elements.get('mentor-keep-status').textContent,
   /Save your working-idea edits/);
 assert.equal(f.elements.get('mentor-working-preview').hidden,false);
});
