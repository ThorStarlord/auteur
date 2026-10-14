import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {projectFullArchitecture} from './projection.mjs';
import {reviewFullArchitecture} from './review.mjs';
const fixture=JSON.parse(readFileSync(new URL('./fixtures/paladin.json',import.meta.url),'utf8'));
const copy=x=>structuredClone(x);

test('empty draft yields actionable author decisions without fictitious complete architecture',()=>{
 const report=reviewFullArchitecture(projectFullArchitecture({candidate:null,workingItems:[]}));
 assert.equal(report.status,'draft');
 assert.ok(report.items.some(x=>x.id==='reader-intention'&&x.state==='open_author_decision'));
 assert.ok(report.items.some(x=>x.id==='book-structure'&&x.state==='open_author_decision'));
 assert.ok(!report.items.some(x=>x.state==='reviewed'));
});

test('missing verified genre pack is informational, not a failure of authored design',()=>{
 const p=projectFullArchitecture(fixture),r=reviewFullArchitecture(p);
 const genre=r.items.find(x=>x.id==='genre-evidence:genre-progress');
 assert.equal(genre.state,'not_established');
 assert.equal(genre.kind,'source_coverage');
 assert.equal(genre.blocksReadiness,false);
});

test('proposal genre emotion does not replace actual authored reader intention',()=>{
 const d=copy(fixture);d.workingItems=d.workingItems.filter(i=>i.architecture_role!=='emotion');
 const r=reviewFullArchitecture(projectFullArchitecture(d));
 assert.equal(r.items.find(x=>x.id==='reader-intention').state,'open_author_decision');
});

test('working but unlinked structural element is specified, not integrated or accepted',()=>{
 const r=reviewFullArchitecture(projectFullArchitecture(fixture));
 const it=r.items.find(x=>x.id==='working-link:author-struct');
 assert.equal(it.state,'specified');
 assert.equal(it.focusTarget,'author-struct');
 assert.equal(r.status,'draft');
});

test('Book review can become ready with authored reader experience, structure and explicit authored link; scenes are optional',()=>{
 const d=copy(fixture);d.workingConnections=[{id:'author-relation',source:'author-emotion',target:'author-struct',label:'guides'}];
 const r=reviewFullArchitecture(projectFullArchitecture(d));
 assert.equal(r.status,'ready_for_author_review');
 assert.ok(r.items.find(x=>x.id==='working-link:author-struct').state==='integrated');
 assert.ok(!r.items.some(x=>x.id==='mandatory-scenes'));
 assert.ok(!('accepted' in r));
});

test('changed request SHA reports adopted stale origin without deleting working idea',()=>{
 const d=copy(fixture);d.requestSha='b'.repeat(64);
 const r=reviewFullArchitecture(projectFullArchitecture(d));
 assert.ok(r.items.some(x=>x.kind==='stale_origin'&&x.focusTarget==='author-struct'));
 assert.equal(r.status,'draft');
});

test('reader review does not mutate any author/source object',()=>{
 const before=JSON.stringify(fixture),p=projectFullArchitecture(fixture),snapshot=JSON.stringify(p);
 reviewFullArchitecture(p);
 assert.equal(JSON.stringify(fixture),before);
 assert.equal(JSON.stringify(p),snapshot);
});
