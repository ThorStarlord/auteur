import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const helper=readFileSync(new URL('../src/auteur/beginner/browser/studio_unfolding.js',import.meta.url),'utf8');
const controller=readFileSync(new URL('../src/auteur/beginner/browser/studio_unfolding_controller.js',import.meta.url),'utf8');
const mentorship=readFileSync(new URL('../src/auteur/beginner/browser/studio_mentorship.js',import.meta.url),'utf8');
const mentorContext=readFileSync(new URL('../src/auteur/beginner/browser/studio_mentor_context.js',import.meta.url),'utf8');
class El{
 constructor(id=''){this.id=id;this.children=[];this.hidden=true;this.value='';this.textContent='';this.events={};this.style={};this.attributes={};this.disabled=false;this.dataset={};}
 replaceChildren(...arr){this.children=[...arr]}appendChild(x){this.children.push(x);return x}append(...xs){this.children.push(...xs)}
 setAttribute(k,v){this.attributes[k]=v}getAttribute(k){return this.attributes[k]}addEventListener(k,v){this.events[k]=v}
 focus(){this.didFocus=true}
}
function fixture(){
 const ids=['unfolding-start','unfolding-local','unfolding-ghosts','unfolding-explanation','unfolding-evidence-status',
 'unfolding-role','unfolding-title','unfolding-create','unfolding-more','unfolding-author-edit','unfolding-mentor'];
 const els=new Map(ids.map(id=>[id,new El(id)]));
 const nodeElements=[];
 const doc={getElementById:id=>els.get(id),createElement:tag=>new El(tag),querySelectorAll:()=>nodeElements};
 const win={innerWidth:1440,localStorage:{getItem(){return null},setItem(){}}};
 new Function('window',helper)(win);new Function('window',mentorContext)(win);
 new Function('window',mentorship)(win);
 new Function('window','document',controller)(win,doc);
 const sha='a'.repeat(64);
 const state={workspace:'architecture',view:'architecture',architectureFacet:'overview',architectureRequestSha:sha,
  unfoldingFocus:{kind:'candidate',id:'g'},unfoldingOffset:0,unfoldingInspected:null,unfoldingSaving:false,
  architecture:{nodes:[{id:'g',title:'Progression Fantasy',category:'genre'},
    {id:'t',title:'Earned breakthrough',category:'trope',summary:'Meaningful effort'}],
    links:[{source:'g',target:'t',function:'uses'}]},items:[]};
 const remote={ready:true,failed:false,canvasId:'canvas-1',revision:0,queue:Promise.resolve(),timer:null,savedSnapshot:null};
 let posted=[],saved=[],hostRequests=[],statuses=[];
 const bridge={state:()=>state,remote:()=>remote,position:()=>({x:100,y:200}),newItemId:()=>'manual-item',flush:async()=>{},
  post:async(action,command)=>{posted.push({action,command});return {revision:remote.revision+1,
    items:action==='update-item'?state.items.map(i=>i.id===command.payload.item.id?command.payload.item:i):
       [...state.items,command.payload.item],positions:{},connections:[],deleted:{}}},
  applySaved:doc=>{remote.revision=doc.revision;state.items=doc.items;saved.push(doc)},
  prepare:instr=>hostRequests.push(instr),
  prepareMentor:(projection,purpose)=>hostRequests.push({projection,purpose}),
  resumeMentor:projection=>hostRequests.push({projection,purpose:'resume'}),
  status:text=>statuses.push(text),remember:()=>{}};
 const ctrl=win.AuteurStudioUnfoldingController.create(bridge);
 return{state,remote,ctrl,win,doc,els,posted,saved,hostRequests,statuses,nodeElements,bridge};
}

test('render is read-only and shows declared focus-local ghosts',()=>{
 const f=fixture();f.ctrl.render();
 assert.equal(f.els.get('unfolding-start').hidden,true);
 assert.equal(f.els.get('unfolding-local').hidden,false);
 assert.equal(f.els.get('unfolding-ghosts').children.length,1);
 assert.equal(f.posted.length,0);assert.equal(f.hostRequests.length,0);
});

test('inspecting does not persist; adopting explicitly posts exact CanvasStore command',async()=>{
 const f=fixture();f.ctrl.render();
 const btn=f.els.get('unfolding-ghosts').children[0];btn.events.click();
 assert.equal(f.posted.length,0);
 const panel=f.els.get('unfolding-explanation');
 assert.equal(panel.hidden,false);
 const adopt=panel.children.find(x=>x.textContent==='Adopt into working architecture');
 assert.ok(adopt);await adopt.events.click();
 await new Promise(resolve=>setTimeout(resolve,0));
 assert.equal(f.posted.length,1);
 assert.equal(f.posted[0].action,'adopt-suggestion');
 assert.equal(f.saved.length,1);
 assert.equal(f.saved[0].items[0].architecture_role,'trope');
 assert.deepEqual(f.state.unfoldingFocus,{kind:'working',id:f.saved[0].items[0].id});
 assert.equal(f.statuses.at(-1).includes('not canon'),true);
});

test('manual first-session authoring posts only create-item, no candidate required',async()=>{
 const f=fixture();f.state.architecture=null;f.state.unfoldingFocus=null;
 f.els.get('unfolding-role').value='character';f.els.get('unfolding-title').value='Eira the healer';
 f.ctrl.render();assert.equal(f.els.get('unfolding-start').hidden,false);
 await f.ctrl.create();
 assert.equal(f.posted.length,1);assert.equal(f.posted[0].action,'create-item');
 assert.equal(f.posted[0].command.payload.item.proposal_origin,null);
 assert.equal(f.saved.length,1);assert.equal(f.hostRequests.length,0);
});

test('stale source refuses adoption and never posts a mutation',async()=>{
 const f=fixture();f.ctrl.render();
 const before=f.win.AuteurStudioUnfolding.projectLocalSuggestions(f.state.architecture,f.state.architectureRequestSha,
  f.state.unfoldingFocus,[],[],3,0)[0];
 f.state.architectureRequestSha='b'.repeat(64);
 await f.ctrl.adopt(before);
 assert.equal(f.posted.length,0);
 assert.equal(f.saved.length,0);
});

test('explicit develop alternatives prepares bounded host-agent request without an auto-call',()=>{
 const f=fixture();f.ctrl.render();assert.equal(f.hostRequests.length,0);
 f.ctrl.more();assert.equal(f.hostRequests.length,1);
 assert.equal(f.hostRequests[0].purpose,'explore');
 assert.equal(f.hostRequests[0].projection.focusId,'g');
 assert.equal(f.posted.length,0);
});


test('explicit alternative comparison reaches mentor with source-bound focus even when nearby ghosts exist',()=>{
 const f=fixture();f.ctrl.render();
 assert.equal(f.els.get('unfolding-ghosts').children.length,1);
 f.ctrl.exploreAlternatives();
 assert.equal(f.hostRequests.length,1);
 assert.equal(f.hostRequests[0].purpose,'explore');
 assert.equal(f.hostRequests[0].projection.focusId,'g');
 assert.equal(f.posted.length,0);
});

test('mobile restricts current suggestions and leaves authored ideas intact',()=>{
 const f=fixture();f.win.innerWidth=390;
 f.state.architecture.nodes.push({id:'e',title:'Challenge',category:'engine'});
 f.state.architecture.links.push({source:'g',target:'e',function:'uses'});
 f.ctrl.render();
 assert.ok(f.els.get('unfolding-ghosts').children.length<=2);
 assert.equal(f.state.items.length,0);
});


test('an author-owned working node is editable in the same graph without losing provenance',async()=>{
 const f=fixture();
 f.state.items=[{id:'working',kind:'note',title:'Old working idea',content:'Editable',group:'Narrative Architecture',
  architecture_role:'trope',proposal_origin:{request_sha:'a'.repeat(64),source_ref:'links/0',source_kind:'proposal_edge',focus_id:'g'}}];
 f.state.unfoldingFocus={kind:'working',id:'working'};
 f.ctrl.render();
 const edit=f.els.get('unfolding-author-edit');assert.equal(edit.hidden,false);
 const field=edit.children.find(x=>x.id==='unfolding-edit-title');
 const text=edit.children.find(x=>x.id==='unfolding-edit-content');
 assert.ok(field);assert.ok(text);
 field.value='Reimagined generosity';text.value='Author authored meaning';
 const save=edit.children.find(x=>x.textContent==='Save working idea');assert.ok(save);
 await save.events.click();
 assert.equal(f.posted.length,1);
 assert.equal(f.posted[0].action,'update-item');
 assert.equal(f.posted[0].command.payload.item.title,'Reimagined generosity');
 assert.equal(f.posted[0].command.payload.item.content,'Author authored meaning');
 assert.equal(f.posted[0].command.payload.item.proposal_origin.source_ref,'links/0');
 assert.equal(f.saved.length,1);
});


test('desktop suggestion panel follows the focused graph node instead of being globally fixed',()=>{
 const f=fixture();
 const viewport=f.els.get('viewport')||new El('viewport');
 viewport.getBoundingClientRect=()=>({left:10,top:80,right:1110,bottom:780,width:1100,height:700});
 f.els.set('viewport',viewport);
 const node=new El('anchor');node.dataset.itemId='g';
 node.getBoundingClientRect=()=>({left:120,top:240,right:285,bottom:320,width:165,height:80});
 f.nodeElements.push(node);
 f.ctrl.render();
 const local=f.els.get('unfolding-local');
 assert.ok(local.style.left.endsWith('px'));
 assert.ok(local.style.top.endsWith('px'));
 assert.equal(local.style.right,'auto');
 f.win.innerWidth=390;f.ctrl.render();
 assert.equal(local.style.left,'');
 assert.equal(local.style.top,'');
});


test('keyboard focus stays on the same suggestion after opening its explanation',()=>{
 const f=fixture();f.ctrl.render();
 const old=f.els.get('unfolding-ghosts').children[0];old.events.click();
 const next=f.els.get('unfolding-ghosts').children[0];
 assert.notEqual(next,old);
 assert.equal(next.getAttribute('aria-pressed'),'true');
 assert.equal(next.didFocus,true);
});

test('mentor starts with source-local Explore and never mutates on passive render',()=>{
 const f=fixture();f.ctrl.render();
 const panel=f.els.get('unfolding-mentor');
 assert.equal(panel.hidden,false);
 assert.equal(panel.children[0].children[1].children[1].getAttribute('aria-pressed'),'true');
 assert.equal(f.els.get('unfolding-ghosts').hidden,false);
 assert.equal(f.posted.length,0);assert.equal(f.hostRequests.length,0);
});

test('Learn and Challenge change only mentor presentation, not unsaved working edits',()=>{
 const f=fixture();
 f.state.items=[{id:'working',title:'Generosity',kind:'note',architecture_role:'theme',content:'Kept',
  proposal_origin:{request_sha:'a'.repeat(64),source_ref:'links/0',source_kind:'proposal_edge',focus_id:'g'}}];
 f.state.unfoldingFocus={kind:'working',id:'working'};
 f.ctrl.render();
 const edit=f.els.get('unfolding-author-edit'),area=edit.children.find(x=>x.id==='unfolding-edit-content');
 area.value='Unsaved author thought';
 const buttons=f.els.get('unfolding-mentor').children[0].children[1].children;
 buttons[0].events.click();
 assert.equal(area.value,'Unsaved author thought');
 assert.equal(edit.children.find(x=>x.id==='unfolding-edit-content'),area);
 assert.equal(f.els.get('unfolding-ghosts').hidden,true);
 f.els.get('unfolding-mentor').children[0].children[1].children[3].events.click();
 assert.equal(area.value,'Unsaved author thought');
 assert.equal(f.posted.length,0);
});

test('question becomes an editable working item only after explicit keep',async()=>{
 const f=fixture();f.ctrl.render();
 f.els.get('unfolding-mentor').children[0].children[1].children[2].events.click();
 const body=f.els.get('unfolding-mentor').children[1];
 const keep=body.children.find(x=>x.textContent==='Keep question as an editable working idea');
 assert.ok(keep);assert.equal(f.posted.length,0);
 await keep.events.click();
 assert.equal(f.posted.length,1);
 assert.equal(f.posted[0].action,'create-item');
 assert.equal(f.posted[0].command.payload.item.kind,'question');
 assert.equal(f.posted[0].command.payload.item.proposal_origin,null);
 assert.match(f.posted[0].command.payload.item.content,/proposal links|expectations/i);
 assert.equal(f.saved.length,1);
});

test('stale question refuses persistence and does not claim a save',async()=>{
 const f=fixture();f.ctrl.render();
 f.els.get('unfolding-mentor').children[0].children[1].children[2].events.click();
 const keep=f.els.get('unfolding-mentor').children[1].children.find(x=>x.textContent.includes('Keep question'));
 f.state.architectureRequestSha='b'.repeat(64);
 await keep.events.click();
 assert.equal(f.posted.length,0);
 assert.match(f.statuses.at(-1),/source changed/);
});

test('fresh divergent reasoning is explicit, source-scoped, and does not call on render',()=>{
 const f=fixture();f.state.architecture.links=[];
 f.els.set('vision-text',Object.assign(new El('vision-text'),{value:'A generous hopeful hero'}));
 f.ctrl.render();assert.equal(f.hostRequests.length,0);
 f.els.get('unfolding-mentor').children[0].children[1].children[1].events.click();
 const body=f.els.get('unfolding-mentor').children[1];
 const request=body.children.find(x=>x.textContent.includes('Develop divergent'));
 assert.ok(request);request.events.click();
 assert.equal(f.hostRequests.length,1);
 assert.equal(f.hostRequests[0].purpose,'explore');
 assert.equal(f.hostRequests[0].projection.sourceSha,'a'.repeat(64));
 assert.equal(f.posted.length,0);
});

test('declared source tension prompts a conditional challenge, not a canon verdict',()=>{
 const f=fixture();f.state.architecture.links=[{source:'g',target:'t',function:'contrasts'}];
 f.ctrl.render();
 const panel=f.els.get('unfolding-mentor');
 assert.equal(panel.children[0].children[1].children[3].getAttribute('aria-pressed'),'true');
 assert.ok(panel.children[1].children.some(x=>x.textContent.includes('Not an accepted contradiction')));
 assert.equal(f.posted.length,0);assert.equal(f.hostRequests.length,0);
});

test('teaching navigation cannot leave an unsaved working idea behind',()=>{
 const f=fixture();let navigations=0;
 f.doc.querySelector=selector=>{
   assert.match(selector,/data-architecture-facet="genres"/);
   return {click:()=>{navigations++;}};
 };
 f.state.items=[{id:'author-genre',kind:'note',title:'Chosen genre',content:'Author details',
   architecture_role:'genre',proposal_origin:null}];
 f.state.unfoldingFocus={kind:'working',id:'author-genre'};
 f.ctrl.render();
 const input=f.els.get('unfolding-author-edit').children.find(x=>x.id==='unfolding-edit-content');
 input.value='Unsaved change';
 const button=f.els.get('unfolding-mentor').children[1].children.find(x=>
   x.textContent==='See related architecture perspective');
 assert.ok(button);button.events.click();
 assert.equal(navigations,0);
 assert.match(f.statuses.at(-1),/Save your working-idea edits/);
 input.value='Author details';button.events.click();
 assert.equal(navigations,1);
});

test('mentor mode changes restore keyboard focus to the selected mode',()=>{
 const f=fixture();f.ctrl.render();
 const previous=f.els.get('unfolding-mentor').children[0].children[1].children[0];
 previous.events.click();
 const current=f.els.get('unfolding-mentor').children[0].children[1].children[0];
 assert.notEqual(previous,current);
 assert.equal(current.getAttribute('aria-pressed'),'true');
 assert.equal(current.didFocus,true);
 assert.equal(f.posted.length,0);
});

test('keeping mentor advice requires explicit source-scoped CanvasStore mutation',async()=>{
 const f=fixture();
 const chosen={focusId:'g',candidateSha:'a'.repeat(64),canvasRevision:0,
   mentorRequestSha:'b'.repeat(64),sourceRef:'directions/social',
   title:'Community restoration',content:'A hopeful author-approved working mechanism'};
 f.ctrl.render();assert.equal(f.posted.length,0);
 const success=await f.ctrl.keepMentorIdea(chosen);
 assert.equal(success,true);
 assert.equal(f.posted.length,1);
 assert.equal(f.posted[0].action,'create-item');
 const item=f.posted[0].command.payload.item;
 assert.equal(item.kind,'note');
 assert.equal(item.proposal_origin.source_kind,'host_agent_suggestion');
 assert.equal(item.proposal_origin.request_sha,'b'.repeat(64));
 assert.equal(item.proposal_origin.source_ref,'directions/social');
 assert.equal(item.proposal_origin.focus_id,'g');
 assert.equal(item.content,chosen.content);
 assert.equal(f.saved.length,1);
});

test('mentor working choice fails closed on stale revision and invalid provenance',async()=>{
 const f=fixture(),base={focusId:'g',candidateSha:'a'.repeat(64),canvasRevision:0,
   mentorRequestSha:'b'.repeat(64),sourceRef:'directions/social',
   title:'Alternative',content:'Body'};
 f.remote.revision=1;
 assert.equal(await f.ctrl.keepMentorIdea(base),false);
 assert.equal(await f.ctrl.keepMentorIdea({...base,canvasRevision:1,mentorRequestSha:'broken'}),false);
 assert.equal(await f.ctrl.keepMentorIdea({...base,canvasRevision:1,sourceRef:'links/200'}),false);
 assert.equal(f.posted.length,0);
 assert.equal(f.saved.length,0);
});

test('mentor modes are progressively disclosed, with voluntary quiet guidance',()=>{
 const f=fixture();f.ctrl.render();
 const host=f.els.get('unfolding-mentor'),modes=host.children[0];
 assert.equal(modes.id,'details');
 assert.equal(modes.open,false);
 assert.match(modes.children[0].textContent,/Mentor · Explore/);
 const quiet=host.children.find(x=>x.textContent==='Hide mentor guidance');
 assert.ok(quiet);quiet.events.click();
 assert.equal(f.state.mentorQuiet,true);
 assert.equal(f.els.get('unfolding-ghosts').hidden,true);
 assert.equal(f.posted.length,0);
 assert.equal(f.hostRequests.length,0);
 const restore=host.children[0];
 assert.equal(restore.textContent,'Show contextual mentorship');
 restore.events.click();
 assert.equal(f.state.mentorQuiet,false);
 assert.equal(f.els.get('unfolding-ghosts').hidden,false);
});

test('working editor text is protected from a mentor choice or question creation',async()=>{
 const f=fixture();
 f.state.items=[{id:'working',kind:'note',title:'Original title',content:'Original details',
   architecture_role:'theme'}];
 f.state.unfoldingFocus={kind:'working',id:'working'};
 f.ctrl.render();
 const editor=f.els.get('unfolding-author-edit');
 const detail=editor.children.find(x=>x.id==='unfolding-edit-content');
 assert.ok(detail);
 detail.value='Important unsaved author wording';
 const choice={focusId:'working',candidateSha:'a'.repeat(64),canvasRevision:0,
   mentorRequestSha:'b'.repeat(64),sourceRef:'directions/social',
   title:'Mentor alternative',content:'Noncanonical option'};
 assert.equal(await f.ctrl.keepMentorIdea(choice),false);
 assert.equal(f.posted.length,0);
 assert.equal(detail.value,'Important unsaved author wording');
 const modes=f.els.get('unfolding-mentor').children[0].children[1].children;
 modes[2].events.click();
 const question=f.els.get('unfolding-mentor').children[1].children.find(x=>
   x.textContent.includes('Keep question'));
 await question.events.click();
 assert.equal(f.posted.length,0);
 assert.equal(detail.value,'Important unsaved author wording');
 assert.ok(f.statuses.some(x=>x.includes('Save the unsaved working-idea text')));
});

test('working editor can still explicitly save its own dirty contents',async()=>{
 const f=fixture();
 f.state.items=[{id:'working',kind:'note',title:'Original title',content:'Original details'}];
 f.state.unfoldingFocus={kind:'working',id:'working'};
 f.ctrl.render();
 const editor=f.els.get('unfolding-author-edit');
 editor.children.find(x=>x.id==='unfolding-edit-content').value='Revised author prose';
 const save=editor.children.find(x=>x.textContent==='Save working idea');
 assert.ok(save);
 await save.events.click();
 assert.equal(f.posted.length,1);
 assert.equal(f.posted[0].action,'update-item');
 assert.equal(f.posted[0].command.payload.item.content,'Revised author prose');
});

test('stale candidate does not expose mentor links or auto-trigger a new request',()=>{
 const f=fixture();
 f.state.architectureSourceStatus='stale';
 f.ctrl.render();
 assert.equal(f.els.get('unfolding-mentor').hidden,true);
 assert.equal(f.hostRequests.length,0);
 assert.equal(f.posted.length,0);
 f.state.architectureSourceStatus='ready';
 f.ctrl.render();
 assert.equal(f.els.get('unfolding-mentor').hidden,false);
});

test('author working mentor choice is allowed without a current candidate source',async()=>{
 const f=fixture();
 f.state.items=[{id:'my-idea',kind:'note',title:'Author idea',content:'My source'}];
 f.state.unfoldingFocus={kind:'working',id:'my-idea'};
 f.state.architectureSourceStatus='stale';
 f.ctrl.render();
 assert.equal(f.els.get('unfolding-mentor').hidden,false);
 const choice={focusId:'my-idea',candidateSha:null,canvasRevision:0,
   mentorRequestSha:'b'.repeat(64),sourceRef:'interpretation',
   title:'Author-reviewed meaning',content:'An editable working interpretation'};
 assert.equal(await f.ctrl.keepMentorIdea(choice),true);
 assert.equal(f.posted.length,1);
 assert.equal(f.posted[0].action,'create-item');
 assert.equal(f.posted[0].command.payload.item.proposal_origin.source_ref,'interpretation');
});

test('unrelated rerenders preserve a working idea title and body before explicit save',()=>{
 const f=fixture();
 f.state.items=[{id:'working',kind:'note',title:'Stored title',content:'Stored body'}];
 f.state.unfoldingFocus={kind:'working',id:'working'};
 f.ctrl.render();
 const editor=()=>f.els.get('unfolding-author-edit');
 editor().children.find(x=>x.id==='unfolding-edit-title').value='My unsaved title';
 editor().children.find(x=>x.id==='unfolding-edit-content').value='My unsaved body';
 f.ctrl.render();
 assert.equal(editor().children.find(x=>x.id==='unfolding-edit-title').value,'My unsaved title');
 assert.equal(editor().children.find(x=>x.id==='unfolding-edit-content').value,'My unsaved body');
 assert.equal(f.ctrl.hasUnsavedWorkingDrafts(),true);
 assert.equal(f.posted.length,0);
});

test('focus switches preserve draft until author returns and explicitly saves',async()=>{
 const f=fixture();
 f.state.items=[{id:'working',kind:'note',title:'Stored title',content:'Stored body'}];
 f.state.unfoldingFocus={kind:'working',id:'working'};
 f.ctrl.render();
 let edit=f.els.get('unfolding-author-edit');
 edit.children.find(x=>x.id==='unfolding-edit-content').value='Important unsaved text';
 f.state.unfoldingFocus={kind:'candidate',id:'g'};f.ctrl.render();
 assert.equal(f.ctrl.hasUnsavedWorkingDrafts(),true);
 assert.equal(f.posted.length,0);
 f.state.unfoldingFocus={kind:'working',id:'working'};f.ctrl.render();
 edit=f.els.get('unfolding-author-edit');
 assert.equal(edit.children.find(x=>x.id==='unfolding-edit-content').value,'Important unsaved text');
 await edit.children.find(x=>x.textContent==='Save working idea').events.click();
 assert.equal(f.posted.length,1);
 assert.equal(f.posted[0].action,'update-item');
 assert.equal(f.posted[0].command.payload.item.content,'Important unsaved text');
 assert.equal(f.ctrl.hasUnsavedWorkingDrafts(),false);
});

test('hidden dirty drafts prevent adopting alternatives from another focus',async()=>{
 const f=fixture();
 f.state.items=[{id:'working',kind:'note',title:'Source',content:'Unedited'}];
 f.state.unfoldingFocus={kind:'working',id:'working'};f.ctrl.render();
 f.els.get('unfolding-author-edit').children
   .find(x=>x.id==='unfolding-edit-content').value='Not yet saved';
 f.state.unfoldingFocus={kind:'candidate',id:'g'};f.ctrl.render();
 const ghost=f.els.get('unfolding-ghosts').children[0];
 ghost.events.click();
 const adopt=f.els.get('unfolding-explanation').children
   .find(x=>x.textContent==='Adopt into working architecture');
 await adopt.events.click();
 assert.equal(f.posted.length,0);
 assert.equal(f.ctrl.hasUnsavedWorkingDrafts(),true);
 assert.ok(f.statuses.some(x=>x.includes('unsaved working-idea text')));
});

test('drafts are keyed by canvas and cannot contaminate another canvas',()=>{
 const f=fixture();
 f.state.items=[{id:'shared',kind:'note',title:'First',content:'First canvas'}];
 f.state.unfoldingFocus={kind:'working',id:'shared'};f.ctrl.render();
 f.els.get('unfolding-author-edit').children
   .find(x=>x.id==='unfolding-edit-content').value='Unsaved first canvas draft';
 f.remote.canvasId='canvas-2';
 f.state.items=[{id:'shared',kind:'note',title:'Second',content:'Second canvas'}];
 f.ctrl.render();
 assert.equal(f.els.get('unfolding-author-edit').children
   .find(x=>x.id==='unfolding-edit-content').value,'Second canvas');
 assert.equal(f.ctrl.hasUnsavedWorkingDrafts(),false);
 f.remote.canvasId='canvas-1';
 f.state.items=[{id:'shared',kind:'note',title:'First',content:'First canvas'}];
 f.ctrl.render();
 assert.equal(f.els.get('unfolding-author-edit').children
   .find(x=>x.id==='unfolding-edit-content').value,'Unsaved first canvas draft');
});

test('failed working-editor save retains exact draft and never announces success',async()=>{
 const f=fixture();
 f.state.items=[{id:'working',kind:'note',title:'Stored',content:'Old body'}];
 f.state.unfoldingFocus={kind:'working',id:'working'};
 f.ctrl.render();
 const editor=f.els.get('unfolding-author-edit');
 editor.children.find(x=>x.id==='unfolding-edit-content').value='Irreplaceable author text';
 f.bridge.post=async()=>{throw Error('simulated disk failure')};
 await editor.children.find(x=>x.textContent==='Save working idea').events.click();
 const after=f.els.get('unfolding-author-edit');
 assert.equal(after.children.find(x=>x.id==='unfolding-edit-content').value,'Irreplaceable author text');
 assert.equal(f.state.items[0].content,'Old body');
 assert.equal(f.ctrl.hasUnsavedWorkingDrafts(),true);
 assert.equal(f.saved.length,0);
 assert.ok(f.statuses.some(x=>x.includes('simulated disk failure')));
});
