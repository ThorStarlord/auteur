import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {normalizeEvidence} from './model.mjs';
import {deriveSemanticLinks} from './semantic-links.mjs';
import {visitRoute,returnRoute,reconcileRoute,serializeFixtureRoute,parseFixtureRoute} from './navigation-state.mjs';
const json=x=>JSON.parse(readFileSync(new URL(x,import.meta.url),'utf8'));
const model=normalizeEvidence(json('./fixtures/paladin.json'),json('./fixtures/genre-evidence.json'));
const links=deriveSemanticLinks(model);
const start={storyId:'paladin',perspective:'anatomy',focus:{kind:'genre',id:'progression_fantasy'},viaLinkId:null,trail:[]};
const target={perspective:'comparison',focus:{kind:'item',id:'earn'}};

test('returns to exact prior perspective, genre, scroll, and focus origin',()=>{
 const route=visitRoute(start,target,links[0].id,{scrollY:361,focusLocator:'data-link-earn'});
 assert.equal(route.trail.length,1);
 assert.equal(route.trail[0].scrollY,361);
 const back=returnRoute(route);
 assert.deepEqual(back.focus,start.focus);
 assert.equal(back.perspective,'anatomy');
 assert.equal(back.returnFocusLocator,'data-link-earn');
 assert.equal(back.returnScrollY,361);
 assert.equal(back.trail.length,0);
});

test('identical consecutive semantic click does not manufacture a second crumb',()=>{
 const first=visitRoute(start,target,links[0].id,{});
 assert.deepEqual(visitRoute(first,target,links[0].id,{}),first);
});

test('the trail is bounded to twelve snapshots',()=>{
 let route=start;
 for(let i=0;i<15;i++)route=visitRoute(route,{perspective:i%2?'anatomy':'comparison',focus:{kind:'item',id:i%2?'generosity':'earn'}},String(i),{});
 assert.equal(route.trail.length,12);
});

test('unknown or replaced source is unavailable rather than remapped by title',()=>{
 const broken={...start,perspective:'comparison',focus:{kind:'item',id:'retired'},viaLinkId:null};
 const res=reconcileRoute(broken,model,links);
 assert.match(res.issue,/unavailable/i);
 assert.equal(res.route.perspective,'overview');
 assert.equal(res.route.focus,null);
 const revised=reconcileRoute(visitRoute(start,target,'edge:vanished-source',{}),model,links);
 assert.match(revised.issue,/source|unavailable/i);
});

test('direct-load hash has no fabricated trail or previous destination',()=>{
 const partial=parseFixtureRoute('#story=paladin&view=comparison&kind=item&key=earn');
 assert.deepEqual(partial,{storyId:'paladin',perspective:'comparison',focus:{kind:'item',id:'earn'},viaLinkId:null,trail:[]});
 assert.deepEqual(returnRoute(partial),partial);
});

test('serializing the fixture route exposes no story prose and rejects disallowed IDs',()=>{
 assert.equal(serializeFixtureRoute({...start,focus:{kind:'item',id:'earn'}}),'#story=paladin&view=anatomy&kind=item&key=earn');
 assert.equal(parseFixtureRoute('#story=paladin&view=comparison&kind=item&key=%3Cscript%3E'),null);
 assert.equal(parseFixtureRoute('#story=private-story&view=overview'),null);
 assert.ok(!serializeFixtureRoute(start).includes('Progression Fantasy'));
});

test('state updates are immutable',()=>{
 const old=JSON.stringify(start);const newRoute=visitRoute(start,target,'x',{scrollY:0});
 assert.equal(JSON.stringify(start),old);
 assert.notEqual(newRoute,start);
});
