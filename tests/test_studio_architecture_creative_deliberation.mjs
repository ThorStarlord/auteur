import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const panelSource=readFileSync(new URL('../src/auteur/beginner/browser/studio_architecture_creative_panel.js',import.meta.url),'utf8');
const bridgeSource=readFileSync(new URL('../src/auteur/beginner/browser/studio_architecture_agent_bridge.js',import.meta.url),'utf8');
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
function setupPanel({withAlternatives=true}={}){
  const document={createElement(tag){return element(tag,this)}},window={};
  runInNewContext(panelSource,{window,document});
  const root=document.createElement('section');
  const alternatives=[],sent=[];
  const options={root,onAction:x=>sent.push(x),onRevise:()=>{},onClear:()=>{},onComplete:()=>{}};
  if(withAlternatives)options.onUseAlternative=x=>alternatives.push(x);
  const panel=window.AuteurStudioCreativePanel.createCreativePanel(options);
  panel.setSelection([{kind:'node',id:'memory_economy',sourceRef:'nodes/3'}],[
    {operation:'explore',label:'Explore',description:'Ask about possibilities'},
  ]);
  return {panel,root,alternatives,sent,document};
}
const readyInquiry={
  status:'ready',request_sha256:INQUIRY,
  result:{analysis:'Two causal variables could change.',recorded_observations:[],uncertainties:[],
    hypotheses:[
      {id:'h1',title:'Communal ledger',description:'The cost is shared among residents.'},
      {id:'h2',title:'Restorable cost',description:'A later survey returns the memory.'},
    ]},
  history:[{request_sha256:'e'.repeat(64),operation:'challenge',author_question:'Where is it weakest?',
    hypotheses:[{id:'h1',title:'Third-option compromise'}]}],
};

test('earlier exchanges are shown as noncanonical text with their alternative IDs',()=>{
  const s=setupPanel();
  s.panel.setInquiryResult(readyInquiry);
  const history=walk(s.root,n=>n.attrs?.['aria-label']==='Earlier creative exchanges')[0];
  const text=JSON.stringify(history);
  assert.match(text,/Earlier exchanges for this source \(noncanonical\)/);
  assert.match(text,/challenge · Where is it weakest\?/);
  assert.match(text,/h1 Third-option compromise/);
});

test('each alternative carries its server ID and an explicit revision-basis action when current',()=>{
  const s=setupPanel();
  s.panel.setInquiryResult(readyInquiry);
  const buttons=walk(s.root,n=>n.dataset?.alternativeId).map(n=>n.dataset.alternativeId);
  assert.deepEqual(buttons,['h1','h2']);
  const labels=walk(s.root,n=>n.tag==='button'&&/revision basis/.test(n.textContent)).map(n=>n.textContent);
  assert.deepEqual(labels,['Use h1 as revision basis','Use h2 as revision basis']);
});

test('choosing an alternative requires a selection and a stated intention, then names the inquiry and ID',()=>{
  const s=setupPanel();
  s.panel.setInquiryResult(readyInquiry);
  const button=walk(s.root,n=>n.dataset?.alternativeId==='h2')[0];
  button.dispatch('click');
  assert.equal(s.alternatives.length,0,'no revision without author intention');
  const status=walk(s.root,n=>n.attrs?.role==='status')[0];
  assert.match(status.textContent,/Write what you want to develop from h2 first/);
  s.panel.setAuthorText('Adopt this direction and rebalance the emotions around it.');
  button.dispatch('click');
  assert.equal(s.alternatives.length,1);
  assert.equal(s.alternatives[0].selectedAlternative.hypothesisId,'h2');
  assert.equal(s.alternatives[0].selectedAlternative.inquiryRequestSha256,INQUIRY);
  assert.equal(s.alternatives[0].anchors[0].id,'memory_economy');
  assert.equal(s.alternatives[0].authorText,'Adopt this direction and rebalance the emotions around it.');
});

test('stale or unfinished inquiries never offer revision-basis actions',()=>{
  const s=setupPanel();
  s.panel.setInquiryResult({...readyInquiry,status:'stale'});
  assert.equal(walk(s.root,n=>n.dataset?.alternativeId).length,0);
  s.panel.setInquiryResult({...readyInquiry,status:'awaiting_host_agent',result:null});
  assert.equal(walk(s.root,n=>n.dataset?.alternativeId).length,0);
});

test('without an alternative handler the panel offers no revision-basis action',()=>{
  const s=setupPanel({withAlternatives:false});
  s.panel.setInquiryResult(readyInquiry);
  assert.equal(walk(s.root,n=>n.dataset?.alternativeId).length,0);
});

test('bridge sends the selected alternative as a server-validated snake_case field',async()=>{
  const window={};runInNewContext(bridgeSource,{window,fetch:async()=>({ok:true,json:async()=>({})})});
  const calls=[];
  const bridge=window.AuteurStudioAgentBridge.createArchitectureAgentBridge({
    canvasId:()=>'memory-economy',
    readProjection:()=>({candidate_request_sha256:SHA}),
    fetchJson:async(url,payload)=>{calls.push({url,payload});return {status:'awaiting_host_agent'}},
  });
  await bridge.prepareRevision({anchors:[{kind:'node',id:'memory_economy'}],authorText:'Adopt h2.',
    selectedAlternative:{inquiryRequestSha256:INQUIRY,hypothesisId:'h2'}});
  assert.equal(calls[0].payload.selected_alternative.inquiry_request_sha256,INQUIRY);
  assert.equal(calls[0].payload.selected_alternative.hypothesis_id,'h2');
  assert.equal(calls[0].payload.graph_intent.operation,'revise');
  await bridge.prepareRevision({anchors:[{kind:'node',id:'memory_economy'}],authorText:'Plain revision.'});
  assert.equal('selected_alternative' in calls[1].payload,false,'legacy revision payload is unchanged');
});

test('superseded exchanges are shown as historical lineage with no selectable alternatives',()=>{
  const s=setupPanel();
  const superseded=[{request_sha256:'f'.repeat(64),operation:'explore',
    author_question:'What other mechanisms could drive the allocation?',
    hypotheses:[{id:'h1',title:'Rotating stewardship'},{id:'h2',title:'Expiring claims'}]}];
  s.panel.setStatus({status:'stale',history:[],superseded_history:superseded});
  const lineage=walk(s.root,n=>n.attrs?.['aria-label']==='Superseded creative exchanges')[0];
  assert.match(JSON.stringify(lineage),/superseded architecture/);
  assert.match(JSON.stringify(lineage),/What other mechanisms could drive the allocation\?/);
  assert.match(JSON.stringify(lineage),/h2 Expiring claims/);
  assert.equal(walk(s.root,n=>n.dataset?.alternativeId).length,0,'historical alternatives are never selectable');
});

test('invalidating a stale result clears alternatives but keeps the author text',()=>{
  const s=setupPanel();
  s.panel.setInquiryResult(readyInquiry);
  s.panel.setAuthorText('Adopt expiring claims.');
  assert.equal(walk(s.root,n=>n.dataset?.alternativeId).length,2);
  s.panel.invalidateResult();
  assert.equal(walk(s.root,n=>n.dataset?.alternativeId).length,0);
  assert.equal(s.panel.getAuthorText(),'Adopt expiring claims.');
  const lineage=walk(s.root,n=>n.attrs?.['aria-label']==='Superseded creative exchanges')[0];
  assert.equal(lineage.children.length,0);
});

test('realization action forwards a selected typed relationship without revising architecture',()=>{
  const document={createElement(tag){return element(tag,this)}},window={};
  runInNewContext(panelSource,{window,document});
  const root=document.createElement('section'),realized=[];
  const panel=window.AuteurStudioCreativePanel.createCreativePanel({
    root,onAction:()=>{},onRevise:()=>{},onClear:()=>{},
    onRealize:payload=>realized.push(payload),
  });
  panel.setSelection([{kind:'link',id:'engine_drives_cost',sourceRef:'links/3'}],[
    {operation:'explain',label:'Explain',description:'Explain a relationship'},
  ]);
  const buttons=walk(root,n=>n.tag==='button'&&n.textContent==='Develop Story Realization from this meaning');
  assert.equal(buttons.length,1);
  assert.equal(buttons[0].disabled,false);
  buttons[0].dispatch('click');
  assert.equal(realized.length,1);
  assert.equal(realized[0].anchors[0].kind,'link');
  assert.equal(realized[0].anchors[0].id,'engine_drives_cost');
  assert.equal(walk(root,n=>n.dataset?.creativeSubmit==='true').length,1);
});
