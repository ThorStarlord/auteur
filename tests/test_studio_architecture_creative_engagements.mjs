import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

// The evidence an inquiry was asked with, and the owner's standing for it, from the reference-stewardship Exercise B.
const panelSource=readFileSync(new URL('../src/auteur/beginner/browser/studio_architecture_creative_panel.js',import.meta.url),'utf8');
const EVIDENCE=new URL('../docs/qualification-evidence/narrative-reference-stewardship-20261127/reproduce/exercise-b/',import.meta.url);
const packet=JSON.parse(readFileSync(new URL('packet-B.json',EVIDENCE),'utf8'));
const standing=JSON.parse(readFileSync(new URL('standing-B.json',EVIDENCE),'utf8'));
const SHA='c'.repeat(64),INQUIRY='d'.repeat(64);

function element(tag,document){
  return {
    tag,ownerDocument:document,children:[],listeners:{},attrs:{},dataset:{},value:'',textContent:'',
    append(...children){this.children.push(...children)},
    replaceChildren(...children){this.children=children},
    setAttribute(key,value){this.attrs[key]=value},
    addEventListener(event,fn){(this.listeners[event]||=[]).push(fn)},
    dispatch(event){for(const fn of this.listeners[event]||[])fn()},
  };
}
function walk(node,predicate,found=[]){
  if(predicate(node))found.push(node);
  for(const child of node.children||[])walk(child,predicate,found);
  return found;
}
function text(node){
  if(node.textContent)return node.textContent;
  return (node.children||[]).map(text).join(' ');
}
function panelWithEvidence(){
  const document={createElement(tag){return element(tag,this)}},window={};
  runInNewContext(panelSource,{window,document});
  const root=document.createElement('section');
  const panel=window.AuteurStudioCreativePanel.createCreativePanel({root,onAction:()=>{},onRevise:()=>{},onClear:()=>{},onComplete:()=>{}});
  panel.setSelection([{kind:'node',id:'memory_economy',sourceRef:'nodes/3'}],[
    {operation:'compare',label:'Compare',description:'Compare the questions'}]);
  panel.setInquiryResult({status:'ready',request_sha256:INQUIRY,result:{
    analysis:'The records do not establish one problem.',recorded_observations:[],uncertainties:[],hypotheses:[],
    deliberation:packet,deliberation_standing:standing}});
  return {root};
}

test('an element association is shown as engagement with its own status, never as a decision',()=>{
  const {root}=panelWithEvidence();
  const evidence=walk(root,n=>n.dataset?.deliberation==='true')[0];
  assert.ok(evidence,'the evidence this answer was given is present');
  const lines=walk(evidence,n=>n.dataset?.basis==='book_element_association');
  const all=lines.map(text).join('\n');
  assert.match(all,/Book 24 · Working Book element that engages this question \(an association: engagement only\)/);
  assert.match(all,/Book 25 · Working Book element that engages this question/);
  assert.match(all,/the element reads as it did/);
  assert.doesNotMatch(all,/decision/i,'an element association is not described as a decision');
});

test('a positional name and an element co-reference are each labelled for what they are',()=>{
  const {root}=panelWithEvidence();
  const evidence=walk(root,n=>n.dataset?.deliberation==='true')[0];
  const all=text(evidence);
  // Exercise B's packet holds no tied positional name; the untied count is stated as a gap, never filled in.
  assert.match(all,/names a question by position at a version that recorded no identity/);
  assert.match(all,/Missing or unreadable history|Nothing ties that name/);
  assert.match(all,/records decisions about 2 of these questions/,'a decision co-reference keeps its own wording');
});

test('a decision keeps the decision wording and an element keeps the element wording',()=>{
  const {root}=panelWithEvidence();
  const evidence=walk(root,n=>n.dataset?.deliberation==='true')[0];
  const decisions=walk(evidence,n=>n.dataset?.basis==='book_decision').map(text).join('\n');
  assert.match(decisions,/Working Book decision \(a noncanonical proposal\)/);
  assert.doesNotMatch(decisions,/engages this question/);
});
