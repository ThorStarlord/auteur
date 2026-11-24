import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const source=readFileSync(new URL('../src/auteur/beginner/browser/studio_architecture_creative_panel.js',import.meta.url),'utf8');
function element(tag,document){
  return {
    tag,ownerDocument:document,children:[],listeners:{},attrs:{},dataset:{},value:'',textContent:'',
    append(...children){this.children.push(...children)},
    appendChild(child){this.children.push(child);return child},
    replaceChildren(...children){this.children=children},
    setAttribute(key,value){this.attrs[key]=value},
    addEventListener(event,fn){(this.listeners[event]||=[]).push(fn)},
    dispatch(event){for(const fn of this.listeners[event]||[])fn()},
  };
}
function setup(){
  const document={createElement(tag){return element(tag,this)}},window={};
  runInNewContext(source,{window,document});
  const root=document.createElement('section');
  const sent=[],revised=[],completed=[];
  const panel=window.AuteurStudioCreativePanel.createCreativePanel({
    root,onAction:x=>sent.push(x),onRevise:x=>revised.push(x),
    onClear:()=>{},onComplete:x=>completed.push(x),
  });
  const actions=[
    {operation:'inspect',label:'Inspect',description:'Read source'},
    {operation:'trace',label:'Trace',description:'Read relation'},
    {operation:'explore',label:'Explore',description:'Ask about possibilities'},
    {operation:'revise',label:'Revise',description:'Complete working revision'},
  ];
  const selection=[{kind:'node',id:'engine',sourceRef:'nodes/0',label:'Memory Economy'}];
  return {panel,root,sent,revised,completed,selection,actions};
}
function find(root,predicate){return root.children.find(predicate)}
test('panel shows typed anchors and retains edited author text through selection update',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);
  s.panel.setAuthorText('Make the engine more generous');
  s.panel.setSelection([{kind:'link',id:'cost_link',sourceRef:'links/0'}],s.actions);
  assert.equal(s.panel.getAuthorText(),'Make the engine more generous');
  const chips=find(s.root,x=>x.attrs?.['aria-label']==='Selected source anchors');
  assert.match(chips.children[0].textContent,/cost_link/);
});
test('Explore calls inquiry callback, not holistic revision',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);s.panel.setAuthorText('Explore wonder');
  s.panel.setOperation('explore');find(s.root,x=>x.dataset.creativeSubmit).dispatch('click');
  assert.equal(s.sent.length,1);assert.equal(s.revised.length,0);
  assert.equal(s.sent[0].authorText,'Explore wonder');assert.equal(s.sent[0].operation,'explore');
});
test('Revise requires explicit action and calls only revision callback',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);s.panel.setAuthorText('Revise holistically');
  s.panel.setOperation('revise');find(s.root,x=>x.dataset.creativeSubmit).dispatch('click');
  assert.equal(s.revised.length,1);assert.equal(s.sent.length,0);
  assert.equal(s.revised[0].operation,'revise');
});
test('Inspect and Trace work without a natural-language instruction',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);
  const button=find(s.root,x=>x.dataset.creativeSubmit);
  s.panel.setOperation('inspect');button.dispatch('click');
  s.panel.setOperation('trace');button.dispatch('click');
  assert.equal(s.sent.length,2);
});
test('missing author intention never silently prepares an agent inquiry',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);
  s.panel.setOperation('explore');find(s.root,x=>x.dataset.creativeSubmit).dispatch('click');
  assert.equal(s.sent.length,0);
  const status=find(s.root,x=>x.attrs?.role==='status');
  assert.match(status.textContent,/Describe your creative intention/);
});
test('preparation status explicitly distinguishes packet from execution',()=>{
  const s=setup();
  s.panel.setStatus({status:'awaiting_host_agent',request:{role:'studio_architecture_inquiry'}});
  const status=find(s.root,x=>x.attrs?.role==='status');
  assert.match(status.textContent,/not executed/i);
  const packet=s.root.children.find(x=>x.readOnly===true);
  assert.match(packet.value,/studio_architecture_inquiry/);
});
test('inquiry observations, hypotheses and uncertainties remain noncanonical',()=>{
  const s=setup();s.panel.setInquiryResult({status:'ready',result:{
    analysis:'A proposed interpretation',
    recorded_observations:[{kind:'node',id:'engine',claim:'Costs accompany discoveries'}],
    hypotheses:[{title:'Restoration',description:'May restore communities'}],
    uncertainties:['No recorded direct emotional causal link'],
  }});
  const result=s.root.children.find(x=>x.attrs?.['aria-label']==='Inquiry result');
  assert.match(JSON.stringify(result),/noncanonical/);
  assert.match(JSON.stringify(result),/Restoration/);
});
test('validated host-agent response is passed as explicit parsed JSON',()=>{
  const s=setup();
  const response=s.root.children.find(x=>x.attrs?.['aria-label']==='Host-agent inquiry response');
  response.value='{"request_sha256":"abc"}';
  find(s.root,x=>x.textContent==='Validate inquiry response').dispatch('click');
  assert.equal(s.completed.length,1);
  assert.equal(s.completed[0].request_sha256,'abc');
});

const bookEvidence={book_number:24,element_id:'unk-tally-hours',expected_book_request_sha256:'a'.repeat(64),
  expected_element_content_sha256:'b'.repeat(64),kind:'Unresolved',text:'Whether the tally is the hours column.',
  revision_number:1,standing:'undecided',epistemic_status:'unresolved',attribution:'agent_proposed',anchors:['engine']};
function submit(s){find(s.root,x=>x.dataset?.creativeSubmit==='true').dispatch('click');}
test('Book evidence is shown apart from the question and sent as its own field with an inquiry',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);s.panel.setBookEvidence(bookEvidence);
  const box=find(s.root,x=>x.attrs?.['aria-label']==='Book evidence');
  assert.equal(box.hidden,false);
  assert.match(box.children.map(c=>c.textContent).join(' '),/not as your question and not as Architecture fact/);
  s.panel.setAuthorText('Should the Ledger engine decide this?');s.panel.setOperation('explore');submit(s);
  assert.equal(s.sent.length,1);
  assert.equal(s.sent[0].authorText,'Should the Ledger engine decide this?');
  assert.equal(s.sent[0].bookEvidence.element_id,'unk-tally-hours');
});
test('a holistic revision request does not carry Book evidence',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);s.panel.setBookEvidence(bookEvidence);
  s.panel.setAuthorText('Revise it.');s.panel.setOperation('revise');submit(s);
  assert.equal(s.revised.length,1);assert.equal(s.revised[0].bookEvidence,undefined);
});
test('selecting a concept the Book element does not record drops its evidence',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);s.panel.setBookEvidence(bookEvidence);
  s.panel.setSelection([{kind:'node',id:'other',sourceRef:'nodes/1'}],s.actions);
  assert.equal(s.panel.getBookEvidence(),null);
  s.panel.setSelection(s.selection,s.actions);s.panel.setAuthorText('Ask.');s.panel.setOperation('explore');submit(s);
  assert.equal(s.sent[0].bookEvidence,undefined);
});
test('an answer asked with Book evidence says whether that evidence is still current',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);
  const result={schema_version:1,analysis:'A.',recorded_observations:[],uncertainties:[],
    hypotheses:[{id:'h1',title:'Descriptive column',description:'The hours describe care.',divergence_axis:'structure'}],
    book_evidence:{book:{book_number:24,revision_number:1},element:{id:'unk-tally-hours'}}};
  s.panel.setInquiryResult({status:'ready',request_sha256:'c'.repeat(64),result,book_evidence_status:'changed'});
  const section=find(s.root,x=>x.attrs?.['aria-label']==='Inquiry result');
  const text=section.children.map(c=>c.textContent).join(' ');
  assert.match(text,/this evidence is historical, not its present record/);
  assert.match(text,/Developing none of these alternatives leaves the Architecture as it is/);
});

test('alternatives read as separate options, and the decline note appears only when there are alternatives',()=>{
  const s=setup();s.panel.setSelection(s.selection,s.actions);
  const base={schema_version:1,analysis:'A.',recorded_observations:[],uncertainties:[]};
  s.panel.setInquiryResult({status:'ready',request_sha256:'c'.repeat(64),result:{...base,hypotheses:[
    {id:'h1',title:'One',description:'First.',divergence_axis:'structure'},{id:'h2',title:'Two',description:'Second.',divergence_axis:'theme'}]}});
  const section=find(s.root,x=>x.attrs?.['aria-label']==='Inquiry result');
  const list=section.children.find(c=>c.className==='creative-alternatives');
  assert.deepEqual(list.children.map(li=>li.children[0].textContent),['h1 · One','h2 · Two']);
  assert.ok(section.children.some(c=>c.className==='creative-decline'));
  s.panel.setInquiryResult({status:'ready',request_sha256:'c'.repeat(64),result:{...base,hypotheses:[]}});
  const again=find(s.root,x=>x.attrs?.['aria-label']==='Inquiry result');
  assert.ok(!again.children.some(c=>c.className==='creative-decline'));
});

test('after an answer arrives, the question already sent is not reused as a revision instruction',()=>{
  const sent=[],used=[];
  const document={createElement(tag){return element(tag,this)}},window={};
  runInNewContext(source,{window,document});
  const root=document.createElement('section');
  const panel=window.AuteurStudioCreativePanel.createCreativePanel({root,onAction:x=>sent.push(x),onRevise:()=>{},
    onUseAlternative:x=>used.push(x)});
  panel.setSelection([{kind:'node',id:'engine',sourceRef:'nodes/0'}],[{operation:'explore',label:'Explore'}]);
  panel.setAuthorText('Does this belong to the Architecture?');panel.setOperation('explore');
  find(root,x=>x.dataset?.creativeSubmit==='true').dispatch('click');
  assert.equal(sent.length,1);
  panel.setInquiryResult({status:'ready',request_sha256:'d'.repeat(64),result:{schema_version:1,analysis:'A.',recorded_observations:[],
    uncertainties:[],hypotheses:[{id:'h1',title:'One',description:'First.',divergence_axis:'structure'}]}});
  assert.equal(panel.getAuthorText(),'');
  const section=find(root,x=>x.attrs?.['aria-label']==='Inquiry result');
  const list=section.children.find(c=>c.className==='creative-alternatives');
  list.children[0].children.find(c=>c.dataset?.alternativeId==='h1').dispatch('click');
  assert.equal(used.length,0,'an empty instruction prepares nothing');
  panel.setAuthorText('Develop h1 as a clarification.');
  list.children[0].children.find(c=>c.dataset?.alternativeId==='h1').dispatch('click');
  assert.equal(used.length,1);assert.equal(used[0].authorText,'Develop h1 as a clarification.');
});
