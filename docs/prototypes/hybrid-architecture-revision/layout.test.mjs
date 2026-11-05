import test from 'node:test';
import assert from 'node:assert/strict';
import {compareArchitectureRevision} from './compare.mjs';
import {unionGraphLayout,focusedGraphDiff} from './layout.mjs';
const SHA='a'.repeat(64), NEXT='b'.repeat(64);
function fixture(){return {schema_version:2,summary:'Before',nodes:[
{id:'engine',title:'Engine',category:'engine',summary:'First'},
{id:'wonder',title:'Wonder',category:'theme',summary:'Awe'},
{id:'dread',title:'Dread',category:'theme',summary:'Fear'}],
links:[{id:'first_link',source:'engine',target:'wonder',function:'enables'},
{id:'reverse_link',source:'wonder',target:'engine',function:'constrains'}],
emotion_targets:[],complex_emotions:[],genre_contracts:[],genre_interactions:[],phases:[],open_questions:[]}}
const compare=(a,b)=>compareArchitectureRevision({before:a,after:b,beforeRequestSha:SHA,afterRequestSha:NEXT,expectedPriorSha:SHA});
test('shared nodes retain positions after reorder and new nodes receive reserved positions',()=>{const a=fixture(),b=structuredClone(a);b.nodes.reverse();b.nodes.push({id:'hope',title:'Hope',category:'theme',summary:'Restoration'});const r=unionGraphLayout(compare(a,b),{columns:2});assert.deepEqual(r.beforeGraph.nodes.find(n=>n.id==='engine').position,r.afterGraph.nodes.find(n=>n.id==='engine').position);assert.ok(r.positionsByNodeId.hope);assert.ok(!r.beforeGraph.nodes.some(n=>n.id==='hope'))});
test('link redirection remains separate directed before and after edges',()=>{const a=fixture(),b=structuredClone(a);b.links[0].target='dread';const r=unionGraphLayout(compare(a,b));assert.equal(r.beforeGraph.edges.find(e=>e.id==='first_link').target,'wonder');assert.equal(r.afterGraph.edges.find(e=>e.id==='first_link').target,'dread');assert.equal(r.beforeGraph.edges.find(e=>e.id==='first_link').change,'changed')});
test('focused engine includes only real one hop neighbors and preserves reciprocal links',()=>{const a=fixture(),b=structuredClone(a);const v=focusedGraphDiff(compare(a,b),{kind:'node',id:'engine'});assert.equal(v.beforeNeighborhood.nodes.length,2);assert.equal(v.beforeNeighborhood.edges.length,2);assert.equal(v.missingSide,null)});
test('non-spatial focus exposes fields without invented graph edges',()=>{const a=fixture(),b=structuredClone(a);a.emotion_targets.push({id:'wonder_target',provenance:'agent_proposed',role:'primary',emotion:'joy',intended_effect:'Awe'});b.emotion_targets=structuredClone(a.emotion_targets);b.emotion_targets[0].intended_effect='Wonder';const v=focusedGraphDiff(compare(a,b),{kind:'emotion_target',id:'wonder_target'});assert.equal(v.beforeNeighborhood.edges.length,0);assert.equal(v.fieldChanges[0].field,'intended_effect')});
test('removed element has an absent after-side rather than name-matched replacement',()=>{const a=fixture(),b=structuredClone(a);b.nodes=b.nodes.filter(n=>n.id!=='engine');b.nodes.push({id:'new_engine',title:'Engine',category:'engine',summary:'replacement'});b.links=[];const v=focusedGraphDiff(compare(a,b),{kind:'node',id:'engine'});assert.equal(v.missingSide,'after');assert.equal(v.afterNeighborhood.nodes.length,0)});
test('empty edges and large upper bounded graph remain usable',()=>{const a=fixture(),b=structuredClone(a);a.links=[];b.links=[];for(let i=0;i<77;i++){const n={id:'n'+i,title:'N'+i,category:'engine',summary:'S'};a.nodes.push(n);b.nodes.push(structuredClone(n))}const r=unionGraphLayout(compare(a,b));assert.equal(r.beforeGraph.nodes.length,80);assert.equal(r.beforeGraph.edges.length,0);assert.equal(focusedGraphDiff(compare(a,b),{kind:'node',id:'engine'}).beforeNeighborhood.edges.length,0)});
