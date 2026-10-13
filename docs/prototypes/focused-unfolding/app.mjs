import {projectFullArchitecture} from '../full-architecture/projection.mjs';
import {reviewFullArchitecture} from '../full-architecture/review.mjs';
import {renderFullArchitecture} from './full-view.mjs';
import {renderReviewArchitecture} from './review-view.mjs';
import paladinFixture from '../full-architecture/fixtures/paladin.json' with { type: 'json' };
import {createDemoState,createAnchor,selectFocus,suggestForFocus,inspectGhost,adoptGhost,dismissGhost,
        replaceSourceRevision,collapseCluster,returnFocus,editWorkingNode} from './model.mjs';

const $=id=>document.getElementById(id);
let story=createDemoState(),ghostOffset=0,expandedWhy=false,revisionNo=1;
let architectureMode='focus', expandedGenre=null, modeBeforeReview='full';
function fullProjection(){
  const workingItems=story.nodes.map(n=>({id:n.id,title:n.title,content:'',kind:'note',
    architecture_role:n.role,needsReview:!!n.needsReview,
    proposal_origin:n.origin?{request_sha:n.origin.requestSha,source_ref:n.origin.sourceRef,
      source_kind:n.origin.sourceKind,focus_id:n.sourceFocusId}:null}));
  // This preview's genre contracts and phases are labelled illustrative proposal hypotheses.
  const source=structuredClone(paladinFixture);
  return projectFullArchitecture({...source,workingItems,requestSha:paladinFixture.requestSha,
    canvasRevision:story.nextSerial-1,workingSourceRevision:story.revision,acceptedIdentity:null,acceptedStructure:null});
}
function moveMode(next){
  if(!['focus','full','review'].includes(next))throw Error('Unknown architecture mode');
  architectureMode=next;render();
  if(next==='focus')$('mode-focus').focus();else if(next==='full')$('mode-full').focus();
}
function focusFromFull(ref){
  if(!story.nodes.some(n=>n.id===ref)){note('Source-linked author item unavailable; no title-based replacement.');return;}
  story=selectFocus(story,ref);ghostOffset=0;architectureMode='focus';render();
  note('Returned to source-linked working idea without changing story canon.');
}
function renderFullMode(){
  const isFocus=architectureMode==='focus',isReview=architectureMode==='review';
  $('focus-layout').hidden=!isFocus;$('full-architecture').hidden=isFocus||isReview;
  $('review-full-architecture').hidden=!isReview;$('mode-focus').setAttribute('aria-pressed',String(isFocus));
  $('mode-full').setAttribute('aria-pressed',String(!isFocus));
  $('mode-focus').hidden=false;$('mode-full').hidden=false;
  if(isFocus)return renderGraph();
  const projection=fullProjection();
  if(isReview){renderReviewArchitecture($('review-full-architecture'),reviewFullArchitecture(projection),{
    onFocusRef:focusFromFull,onReturn:()=>moveMode(modeBeforeReview)});return;}
  renderFullArchitecture($('full-architecture'),projection,{
    expandedGenre,onToggleGenre:id=>{expandedGenre=id;renderFullMode();},onFocusRef:focusFromFull,
    onReview:()=>{modeBeforeReview='full';moveMode('review');}});
}

const narrow=()=>window.innerWidth<=480?2:3;
const element=(tag,cls,text)=>{const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node;};
const activeFocus=()=>story.nodes.find(n=>n.id===story.focusId);
const focusTitle=()=>activeFocus()?.title||'Choose a starting idea';
const note=text=>{$('announcement').textContent=text;};
function presentGhost(id){try{story=inspectGhost(story,id);expandedWhy=false;render();}catch(e){note(e.message);}}
function focusWorking(id){try{story=selectFocus(story,id);ghostOffset=0;expandedWhy=false;render();note('Exploring possible directions around '+focusTitle()+'.');}catch(e){note(e.message);}}
function makeWorking(node){
  const wrapper=element('div','node-wrapper');
  const btn=element('button','working-node'+(story.focusId===node.id?' selected':'')+(node.needsReview?' needs-review':''));
  btn.type='button';btn.setAttribute('aria-pressed',String(story.focusId===node.id));
  btn.append(element('span','node-label',node.title),element('span','node-state',node.needsReview?'Working · needs review':'Working · not canon'));
  btn.addEventListener('click',()=>focusWorking(node.id));wrapper.append(btn);return wrapper;
}
function makeGhost(ghost){
  const wrapper=element('div','ghost-wrapper');
  wrapper.append(element('span','ghost-arrow','⇢'));
  const btn=element('button','ghost-card');btn.type='button';
  btn.setAttribute('aria-pressed',String(story.inspectedGhostId===ghost.id));
  btn.append(element('span','node-label',ghost.title),element('span','node-state','Suggested · '+ghost.targetRole),
    element('small','','Provisional hypothesis'));
  btn.addEventListener('click',()=>presentGhost(ghost.id));wrapper.append(btn);return wrapper;
}
function drawGhostEdges(){
  const svg=$('ghost-connections');svg.replaceChildren();
  if(!story.focusId||narrow()===2)return;
  const target=document.querySelector('.working-node.selected');if(!target)return;
  const frame=$('graph-content').getBoundingClientRect(),origin=target.getBoundingClientRect();
  svg.setAttribute('viewBox',`0 0 ${frame.width} ${frame.height}`);
  const x1=origin.right-frame.left,y1=origin.top-frame.top+origin.height/2;
  document.querySelectorAll('.ghost-card').forEach(button=>{
    const dest=button.getBoundingClientRect();const x2=dest.left-frame.left,y2=dest.top-frame.top+dest.height/2;
    const path=document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('class','ghost-edge');path.setAttribute('fill','none');path.setAttribute('stroke','#ae8ac9');
    path.setAttribute('stroke-width','1.8');path.setAttribute('stroke-dasharray','5 5');
    const bend=Math.max(14,Math.abs(x2-x1)*.43);
    path.setAttribute('d',`M ${x1} ${y1} C ${x1+bend} ${y1}, ${x2-bend} ${y2}, ${x2} ${y2}`);
    svg.appendChild(path);
  });
}
function renderGraph(){
  const hasNodes=!!story.nodes.length;
  $('start-prompt').hidden=hasNodes;$('graph-content').hidden=!hasNodes;
  $('previous-focus').hidden=!story.history.length;$('edit-focus').hidden=!hasNodes;
  $('collapse-branch').hidden=!hasNodes||story.nodes.filter(n=>n.sourceFocusId===story.nodes[0].id).length<1;
  $('collapse-branch').textContent=story.collapsed.includes(story.nodes[0]?.id)?'Expand this branch':'Collapse this branch';
  $('current-focus').textContent=focusTitle();
  $('focus-heading').textContent=hasNodes?focusTitle():'';
  if(!hasNodes){$('focus-explainer').hidden=true;$('focus-guide').hidden=false;return;}
  const working=$('working-layer'),ghosts=$('ghost-layer');working.replaceChildren();ghosts.replaceChildren();
  const root=story.nodes[0],collapsed=story.collapsed.includes(root.id);
  const visible=story.nodes.filter(n=>!collapsed||n.id===root.id||n.sourceFocusId!==root.id);
  visible.forEach(node=>working.append(makeWorking(node)));
  const hiddenCount=story.nodes.length-visible.length;
  $('collapsed-indicator').hidden=!hiddenCount;
  $('collapsed-indicator').textContent=`${hiddenCount} working idea${hiddenCount===1?'':'s'} collapsed · Expand this branch to revisit them.`;
  const total=3,limit=narrow();const selected=suggestForFocus(story,limit,ghostOffset);
  if(!selected.length&&ghostOffset>0){ghostOffset=0;return renderGraph();}
  selected.forEach(ghost=>ghosts.append(makeGhost(ghost)));
  if(!selected.length)ghosts.append(element('p','muted','No more supported proposals for this focus. You can add your own idea or choose another focus.'));
  const more=suggestForFocus(story,limit,ghostOffset+limit);
  $('more-alternatives').hidden=!more.length && ghostOffset===0;
  $('more-alternatives').textContent=more.length?'Explore more alternatives ↗':'Return to first suggestions ↶';
  renderExplanation();
  requestAnimationFrame(drawGhostEdges);
}
function renderExplanation(){
  const ghost=suggestForFocus(story,3,0).concat(suggestForFocus(story,3,3)).find(x=>x.id===story.inspectedGhostId);
  $('focus-explainer').hidden=!ghost;$('focus-guide').hidden=!!ghost;
  if(!ghost)return;
  $('explain-title').textContent=ghost.title;
  $('explain-why').textContent=`Proposed relationship to “${focusTitle()}”: ${ghost.why}.`;
  $('explain-details').hidden=!expandedWhy;
  $('explain-details').textContent=ghost.caveat+' This connection is illustrative and has not been validated as a genre convention or reader-response outcome.';
  $('explain-source').textContent=`Illustrative source: ${ghost.sourceRef} · ${ghost.requestSha}. Not accepted story.`;
}
function render(){renderFullMode();}
function start(role,title){
  try{story=createAnchor(story,role,title);ghostOffset=0;$('alternative-form').hidden=true;$('edit-form').hidden=true;render();note('Created an editable working idea. Explore nearby provisional suggestions.');}
  catch(e){note(e.message);}
}
$('mode-focus').addEventListener('click',()=>moveMode('focus'));
$('mode-full').addEventListener('click',()=>moveMode('full'));
$('start-emotion').addEventListener('click',()=>start('emotion','Joy through generous heroism'));
$('start-elsewhere').addEventListener('click',()=>{$('start-prompt').hidden=true;$('alternative-form').hidden=false;$('anchor-title').focus();});
$('cancel-anchor').addEventListener('click',()=>{$('alternative-form').hidden=true;$('start-prompt').hidden=false;});
$('create-anchor').addEventListener('click',()=>start($('anchor-role').value,$('anchor-title').value));
$('previous-focus').addEventListener('click',()=>{story=returnFocus(story);ghostOffset=0;render();note('Returned to previous creative focus.');});
$('edit-focus').addEventListener('click',()=>{const n=activeFocus();if(!n)return;$('edit-title').value=n.title;$('edit-form').hidden=false;$('graph-content').hidden=true;$('edit-title').focus();});
$('cancel-edit').addEventListener('click',()=>{$('edit-form').hidden=true;render();});
$('save-edit').addEventListener('click',()=>{try{story=editWorkingNode(story,story.focusId,$('edit-title').value);ghostOffset=0;$('edit-form').hidden=true;render();note('Revised working intention. Related adopted ideas remain and may need review.');}catch(e){note(e.message);}});
$('explore-ghost').addEventListener('click',()=>{expandedWhy=!expandedWhy;renderExplanation();note('Review the hypothesis, evidence, and caveat before adopting.');});
$('adopt-ghost').addEventListener('click',()=>{try{story=adoptGhost(story,story.inspectedGhostId);ghostOffset=0;render();note('Added as a working idea, not accepted story canon. Select it to unfold new possibilities.');}catch(e){note(e.message);}});
$('dismiss-ghost').addEventListener('click',()=>{try{story=dismissGhost(story,story.inspectedGhostId);ghostOffset=0;render();note('Dismissed this source-local suggestion only. Your working ideas are unchanged.');}catch(e){note(e.message);}});
$('collapse-branch').addEventListener('click',()=>{const root=story.nodes[0];if(!root)return;story=collapseCluster(story,root.id,!story.collapsed.includes(root.id));render();});
$('more-alternatives').addEventListener('click',()=>{const limit=narrow();ghostOffset=suggestForFocus(story,limit,ghostOffset+limit).length?ghostOffset+limit:0;story={...story,inspectedGhostId:null};render();note(ghostOffset?'Exploring an additional local suggestion.':'Returned to initial local possibilities.');});
$('revise-source').addEventListener('click',()=>{revisionNo++;story=replaceSourceRevision(story,`demo-paladin-v${revisionNo}`);ghostOffset=0;render();note('A new revision invalidated the old provisional branches. Adopted working ideas remain unchanged.');});
window.addEventListener('resize',()=>{ghostOffset=0;render();});
render();
