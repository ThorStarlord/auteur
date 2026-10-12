import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const helper=readFileSync(new URL('../src/auteur/beginner/browser/studio_unfolding.js',import.meta.url),'utf8');
const controller=readFileSync(new URL('../src/auteur/beginner/browser/studio_unfolding_controller.js',import.meta.url),'utf8');
class El{
 constructor(id=''){this.id=id;this.children=[];this.hidden=true;this.value='';this.textContent='';this.events={};this.style={};this.attributes={};this.disabled=false;this.dataset={};}
 replaceChildren(...arr){this.children=[...arr]}appendChild(x){this.children.push(x);return x}append(...xs){this.children.push(...xs)}
 setAttribute(k,v){this.attributes[k]=v}getAttribute(k){return this.attributes[k]}addEventListener(k,v){this.events[k]=v}
 focus(){this.didFocus=true}
}
function fixture(){
 const ids=['unfolding-start','unfolding-local','unfolding-ghosts','unfolding-explanation','unfolding-evidence-status',
 'unfolding-role','unfolding-title','unfolding-create','unfolding-more','unfolding-author-edit'];
 const els=new Map(ids.map(id=>[id,new El(id)]));
 const nodeElements=[];
 const doc={getElementById:id=>els.get(id),createElement:tag=>new El(tag),querySelectorAll:()=>nodeElements};
 const win={innerWidth:1440,localStorage:{getItem(){return null},setItem(){}}};
 new Function('window',helper)(win);new Function('window','document',controller)(win,doc);
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
  prepare:instr=>hostRequests.push(instr),status:text=>statuses.push(text),remember:()=>{}};
 const ctrl=win.AuteurStudioUnfoldingController.create(bridge);
 return{state,remote,ctrl,win,els,posted,saved,hostRequests,statuses,nodeElements};
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
 assert.match(f.hostRequests[0],/NONCANONICAL/);
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
