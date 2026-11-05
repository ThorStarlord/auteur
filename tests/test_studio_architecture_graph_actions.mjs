import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const source=readFileSync(new URL('../src/auteur/beginner/browser/studio_architecture_graph_actions.js',import.meta.url),'utf8');
function api(){const window={};runInNewContext(source,{window});return window.AuteurStudioGraphActions}
function fixture(){return {
  schema_version:2, nodes:[
    {id:'engine',title:'Memory Economy',category:'engine',summary:'Discovery has a cost',parent_id:null},
    {id:'mystery',title:'Mystery',category:'genre',summary:'Curiosity',parent_id:'engine'}],
  links:[{id:'cost_link',source:'engine',target:'mystery',function:'raises the cost'}],
  genre_interactions:[],
  emotion_targets:[{id:'wonder',emotion:'joy',intended_effect:'Awe'}],
  complex_emotions:[],
  genre_contracts:[{genre_node_id:'mystery',emotion_target_ids:['wonder'],complex_emotion_ids:[],narrative_engine:'Question and discovery'}],
  phases:[{id:'opening',genre_activations:[{genre_node_id:'mystery'}],parallel_with:[]}]
}}
test('directed architecture link has exact source identity and direction',()=>{
  const view=api().projectGraphSelection(fixture(),[{kind:'link',id:'cost_link'}]);
  assert.equal(view.anchors[0].sourceRef,'links/0');
  assert.equal(view.recordedRelations[0].source,'engine');
  assert.equal(view.recordedRelations[0].target,'mystery');
});
test('engine-to-emotion pair is not fabricated into an ArchitectureLink',()=>{
  const view=api().projectGraphSelection(fixture(),[{kind:'node',id:'engine'},{kind:'emotion_target',id:'wonder'}]);
  assert.equal(view.missingRelation,true);
  assert.equal(view.directRelations.length,0);
});
test('recorded genre contract emotion reference remains a source-backed reference',()=>{
  const view=api().projectGraphSelection(fixture(),[{kind:'genre_contract',id:'mystery'},{kind:'emotion_target',id:'wonder'}]);
  assert.equal(view.missingRelation,false);
  assert.equal(view.directRelations[0].kind,'recorded_reference');
  assert.equal(view.directRelations[0].field,'emotion_target_ids');
});
test('top-level component field is addressable without inventing a new node',()=>{
  const view=api().projectGraphSelection(fixture(),[{kind:'emotion_target',id:'wonder',field:'intended_effect'}]);
  assert.equal(view.anchors[0].componentValue,'Awe');
  assert.equal(view.anchors[0].kind,'emotion_target');
});
test('phase activation is selectable as qualified recorded reference',()=>{
  const view=api().projectGraphSelection(fixture(),[{kind:'phase',id:'opening',
    reference:{field:'genre_activations',target_kind:'genre_contract',target_id:'mystery'}}]);
  assert.equal(view.anchors[0].reference.kind,'recorded_reference');
});
test('title does not substitute for stable ID when source is absent',()=>{
  assert.throws(()=>api().projectGraphSelection(fixture(),[{kind:'node',id:'Memory Economy'}]),/not recorded/);
});
test('contextual creative actions include an explicit holistic revision',()=>{
  const actions=api().availableGraphActions(fixture(),[{kind:'node',id:'engine'}]);
  assert(actions.some(a=>a.operation==='revise'));
  assert(actions.some(a=>a.operation==='explore'));
  assert(actions.every(a=>a.mutatesWorking===false));
});
test('Connect-to-Ask requires two graph anchors and describes missing relation honestly',()=>{
  const actions=api().availableGraphActions(fixture(),[
    {kind:'node',id:'engine'},{kind:'emotion_target',id:'wonder'}]);
  const action=actions.find(a=>a.operation==='connect_to_ask');
  assert(action);
  assert.match(action.description,/No recorded relation/);
  assert(!api().availableGraphActions(fixture(),[{kind:'node',id:'engine'}])
    .some(a=>a.operation==='connect_to_ask'));
});
test('source array reorder updates browser-facing sourceRef without changing the stable ID',()=>{
  const source=fixture();source.nodes.reverse();
  const view=api().projectGraphSelection(source,[{kind:'node',id:'engine'}]);
  assert.equal(view.anchors[0].sourceRef,'nodes/1');
});
test('duplicate and oversized anchor sets fail closed',()=>{
  assert.throws(()=>api().projectGraphSelection(fixture(),[{kind:'node',id:'engine'},{kind:'node',id:'engine'}]),/Duplicate/);
  assert.throws(()=>api().projectGraphSelection(fixture(),new Array(4).fill({kind:'node',id:'engine'})),/one to three/i);
});
