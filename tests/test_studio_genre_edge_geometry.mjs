import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

// Execute Studio's actual pure geometry helper; avoid duplicating its formula.
const script=readFileSync(new URL('../src/auteur/beginner/browser/studio.js',import.meta.url),'utf8');
const begin=script.indexOf('  function genreInteractionCurveGeometry(');
const end=script.indexOf('\n  function drawEdges() {',begin);
assert.ok(begin!==-1&&end>begin,'Studio genre geometry helper must be available');
const curveGeometry=new Function(script.slice(begin,end)+'\nreturn genreInteractionCurveGeometry;')();

test('horizontal genre interactions attach to node edges, not top-left corners',()=>{
 const from={x:40,y:40},to={x:228,y:40};
 const curve=curveGeometry(from,to,from,to,10);
 assert.deepEqual(curve.start,{x:204,y:74});
 assert.deepEqual(curve.end,{x:228,y:74});
 assert.deepEqual(curve.control,{x:216,y:84});
});

test('reverse-direction interactions have distinct paths and correctly directed endpoints',()=>{
 const a={x:40,y:40},b={x:228,y:40};
 const forward=curveGeometry(a,b,a,b,-10);
 const backward=curveGeometry(b,a,a,b,10);
 assert.deepEqual(backward.start,forward.end);
 assert.deepEqual(backward.end,forward.start);
 assert.equal(forward.control.y,64);
 assert.equal(backward.control.y,84);
});

test('vertical genre interactions attach to source bottom and target top',()=>{
 const from={x:40,y:40},to={x:40,y:140};
 const curve=curveGeometry(from,to,from,to,10);
 assert.deepEqual(curve.start,{x:122,y:108});
 assert.deepEqual(curve.end,{x:122,y:140});
 assert.deepEqual(curve.control,{x:112,y:124});
});
