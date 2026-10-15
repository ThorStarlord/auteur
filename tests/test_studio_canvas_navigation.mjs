import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../src/auteur/beginner/browser/studio.js',import.meta.url),'utf8');
const begin=source.indexOf('  function navigateCanvas(canvasId) {');
const end=source.indexOf('  function openRemote() {',begin);
assert.ok(begin>0&&end>begin,'Expected concrete Studio canvas navigation implementation');
const segment=source.slice(begin,end);
function fixture({dirty=false,unsaved=false,failed=false}={}){
  const remote={ready:true,failed,canvasId:'canvas-a',timer:null,queue:Promise.resolve()};
  const picker={disabled:false,value:'canvas-b'};
  const notices=[],navigation=[];
  const window={location:{assign:url=>navigation.push(url)}};
  const nav=new Function('remote','status','mentorEditorClean','hasUnsavedChanges','queueSave',
    '$','window','canvasUrl','clearTimeout',segment+'\nreturn navigateCanvas;')(
    remote,s=>notices.push(s),()=>!dirty,()=>unsaved,()=>Promise.resolve(),
    id=>id==='canvas-picker'?picker:null,window,id=>'/studio.html?canvas='+id,()=>{});
  return {nav,remote,picker,notices,navigation};
}
async function drain(){await Promise.resolve();await Promise.resolve();await Promise.resolve();}

test('unsaved focused working draft blocks canvas switch before navigation',async()=>{
 const f=fixture({dirty:true});
 f.nav('canvas-b');await drain();
 assert.equal(f.navigation.length,0);
 assert.equal(f.picker.value,'canvas-a');
 assert.match(f.notices.at(-1),/Save your edited working idea/);
});
test('hidden working draft blocks canvas switch after queued saves',async()=>{
 const f=fixture({unsaved:true});
 f.nav('canvas-b');await drain();
 assert.equal(f.navigation.length,0);
 assert.equal(f.picker.disabled,false);
 assert.equal(f.picker.value,'canvas-a');
 assert.match(f.notices.at(-1),/Working edits or drafts remain unsaved/);
});
test('clean working state permits normal canvas navigation',async()=>{
 const f=fixture();
 f.nav('canvas-b');await drain();
 assert.deepEqual(f.navigation,['/studio.html?canvas=canvas-b']);
});
test('failed persisted write never permits canvas navigation',async()=>{
 const f=fixture({failed:true});
 f.nav('canvas-b');await drain();
 assert.equal(f.navigation.length,0);
 assert.match(f.notices.at(-1),/Export a backup/);
});
