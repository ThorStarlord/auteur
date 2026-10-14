import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const browser=new URL('../src/auteur/beginner/browser/',import.meta.url);
const files=['studio_unfolding.js','studio_mentor_context.js','studio_mentorship.js',
 'studio_unfolding_controller.js','studio_mentor_dialogue_controller.js'];
const source=files.map(x=>readFileSync(new URL(x,browser),'utf8'));
class El{
 constructor(id=''){this.id=id;this.hidden=true;this.children=[];this.textContent='';
   this.value='';this.style={};this.dataset={};this.events={};this.attributes={};this.disabled=false;}
 replaceChildren(...xs){this.children=xs}
 appendChild(x){this.children.push(x);return x}
 append(...xs){this.children.push(...xs)}
 setAttribute(k,v){this.attributes[k]=v}
 getAttribute(k){return this.attributes[k]}
 addEventListener(k,v){this.events[k]=v}
 focus(){this.didFocus=true}
}
function setup(){
 const win={innerWidth:1440,localStorage:{getItem(){return null},setItem(){}}};
 source.slice(0,3).forEach(s=>new Function('window',s)(win));
 const ids=['unfolding-start','unfolding-local','unfolding-ghosts','unfolding-explanation',
 'unfolding-evidence-status','unfolding-role','unfolding-title','unfolding-create',
 'unfolding-more','unfolding-author-edit','unfolding-mentor','vision-text',
 'unfolding-mentor-dialogue','mentor-author-reply','mentor-send','mentor-refresh',
 'mentor-complete','mentor-dismiss','mentor-status','mentor-request','mentor-advice',
 'mentor-handoff','mentor-response','mentor-working-preview','mentor-working-title',
 'mentor-working-content','mentor-keep','mentor-keep-status'];
 const els=new Map(ids.map(id=>[id,new El(id)]));
 const doc={getElementById:id=>els.get(id),querySelectorAll:()=>[],
  querySelector:()=>null,createElement:tag=>new El(tag)};
 source.slice(3).forEach(s=>new Function('window','document',s)(win,doc));
 const sha='a'.repeat(64);
 const state={workspace:'architecture',view:'architecture',architectureFacet:'overview',
  fullArchitectureDisplay:'focus',architectureRequestSha:sha,
  unfoldingFocus:{kind:'candidate',id:'g'},unfoldingOffset:0,unfoldingInspected:null,
  unfoldingSaving:false,
  items:[{id:'story-vision',kind:'note',title:'Vision',
   content:'Heroism through generosity, hope and companion independence'}],
  architecture:{nodes:[
   {id:'g',title:'Generosity',category:'theme',summary:'Growth through helping others'},
   {id:'agency',title:'Companion agency',category:'trope',summary:'Independent choices'}],
   links:[{source:'g',target:'agency',function:'contrasts'}],
   open_questions:['How does his significance grow as companions gain agency?']}};
 const remote={ready:true,failed:false,canvasId:'paladin',revision:2};
 const writes=[],requests=[],statuses=[];let serial=0;
 const dialogueInfo={
  mentor_request_sha256:'b'.repeat(64),canvas_revision:2,
  candidate_request_sha256:sha,focus_id:'g',focus_kind:'candidate',
  author_reply:'Companions should become independent while he remains a beloved hero.'};
 const answer={focus_id:'g',kind:'explore',
  summary:'Companion independence can increase heroic importance.',
  author_reply_interpretation:'His generosity expands collective freedom.',
  challenge_basis:'conditional_hypothesis',
  directions:[{id:'community',title:'Community restoration',
    distinguishing_factor:'Institutions grow instead of only individual power',
    divergence_axis:'social_scale',mechanism:'Help creates mutual aid institutions.',
    consequence:'More people act independently.',tradeoff:'The protagonist shares agency.',
    source_status:'agent_hypothesis',source_refs:[]}]};
 const mentorResult={...dialogueInfo,status:'ready',advice:answer};
 const unfolding=win.AuteurStudioUnfoldingController.create({
  state:()=>state,remote:()=>remote,position:()=>({x:100,y:100}),
  newItemId:()=> 'choice-'+(++serial),flush:async()=>{},
  post:async(action,cmd)=>{
   writes.push({action,cmd});
   return {revision:remote.revision+1,items:[...state.items,cmd.payload.item],
     positions:{},connections:[],deleted:{}};},
  applySaved:doc=>{state.items=doc.items;remote.revision=doc.revision;},
  prepare:()=>{throw Error('Full architecture must not be regenerated for mentoring')},
  prepareMentor:()=>{throw Error('Dialogue handles the scoped API directly')},
  status:x=>statuses.push(x),remember:()=>{}
 });
 const dialogue=win.AuteurStudioMentorDialogueController.create({
  state:()=>state,remote:()=>remote,canNavigate:()=>true,flush:async()=>{},
  saveWorking:choice=>unfolding.keepMentorIdea(choice),
  fetch:async(url,init)=>{
   requests.push({url,init});
   return {json:async()=>url.endsWith('/prepare')?
    {...dialogueInfo,status:'awaiting_host_agent',request:{request_sha256:'b'.repeat(64)}}:
    mentorResult};
  },
  apiJson:async r=>r.json(),status:x=>statuses.push(x)
 });
 return {win,els,state,remote,unfolding,dialogue,writes,requests,statuses,mentorResult};
}
test('synthetic story journey connects focus, reply, preview, keep and re-entry',async()=>{
 const f=setup();f.unfolding.render();f.dialogue.render();
 assert.equal(f.state.mentorMode,'challenge');
 assert.equal(f.requests.length,0);assert.equal(f.writes.length,0);
 const focus={focusId:'g',sourceSha:'a'.repeat(64)};
 await f.dialogue.open(focus,'challenge');
 assert.equal(f.requests.length,1);
 assert.equal(JSON.parse(f.requests[0].init.body).purpose,'challenge');
 f.els.get('mentor-author-reply').value=f.mentorResult.author_reply;
 f.els.get('mentor-author-reply').events.input();
 await f.els.get('mentor-send').events.click();
 assert.equal(JSON.parse(f.requests[1].init.body).author_reply,f.mentorResult.author_reply);
 f.els.get('mentor-response').value='{"schema":"auteur_host_agent_response_v1"}';
 await f.dialogue.complete();
 const box=f.els.get('mentor-advice').children.find(x=>
   x.children.some(y=>y.textContent==='Review as working idea'));
 assert.ok(box);
 box.children.find(y=>y.textContent==='Review as working idea').events.click();
 assert.equal(f.writes.length,0);
 f.els.get('mentor-working-title').value='Flourishing communities';
 f.els.get('mentor-working-content').value='The hero creates a society of free companions.';
 await f.els.get('mentor-keep').events.click();
 assert.equal(f.writes.length,1);
 assert.equal(f.writes[0].action,'create-item');
 assert.equal(f.writes[0].cmd.payload.item.content,
  'The hero creates a society of free companions.');
 assert.equal(f.writes[0].cmd.payload.item.proposal_origin.source_kind,'host_agent_suggestion');
 assert.equal(f.writes[0].cmd.payload.item.proposal_origin.source_ref,'directions/community');
 assert.equal(f.remote.revision,3);
 assert.equal(f.state.items.length,2);
 assert.equal(f.state.unfoldingFocus.kind,'working');
 f.state.fullArchitectureDisplay='full';f.dialogue.render();
 assert.equal(f.els.get('unfolding-mentor-dialogue').hidden,true);
 f.state.workspace='realization';f.dialogue.render();
 assert.equal(f.state.items[1].title,'Flourishing communities');
 f.state.workspace='architecture';f.state.fullArchitectureDisplay='focus';
 f.unfolding.render();
 assert.equal(f.state.items[1].content,'The hero creates a society of free companions.');
});
test('synthetic stale author revision refuses an old mentor option',async()=>{
 const f=setup(),focus={focusId:'g',sourceSha:'a'.repeat(64)};
 await f.dialogue.open(focus,'explore');
 f.els.get('mentor-response').value='{}';await f.dialogue.complete();
 f.remote.revision++;
 const box=f.els.get('mentor-advice').children.find(x=>
   x.children.some(y=>y.textContent==='Review as working idea'));
 box.children.find(y=>y.textContent==='Review as working idea').events.click();
 assert.equal(f.els.get('mentor-working-preview').hidden,true);
 assert.equal(f.writes.length,0);
});
