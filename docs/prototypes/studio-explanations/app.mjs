import {normalizeEvidence,entriesForPerspective,connectionsForSelection} from './model.mjs';
import {deriveSemanticLinks,linksForFocus,preferredPerspective} from './semantic-links.mjs';
import {visitRoute,returnRoute,reconcileRoute,serializeFixtureRoute,parseFixtureRoute} from './navigation-state.mjs';

const $=id=>document.getElementById(id);
const modes={
  overview:'A spatial index of source-scoped proposed architecture elements.',
  anatomy:'How a genre conventionally aims to deliver its reader promise.',
  comparison:'What the genre might supply versus what this story proposes to do.',
  mechanism:'Trace a bounded structural relationship and its intended effect.'
};
const state={story:'paladin',model:null,links:[],route:null,renderSerial:0};
const cache={};
const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
const same=(a,b)=>a?.kind===b?.kind&&a?.id===b?.id;
const nameOf=f=>f?.kind==='genre'?state.model?.genres.find(g=>g.id===f.id)?.label:
  f?.kind==='item'?state.model?.items.find(n=>n.id===f.id)?.label:null;
const current=()=>state.route;
const defaultFocus=(perspective)=>{
  if(perspective==='anatomy')return state.model.genres[0]?{kind:'genre',id:state.model.genres[0].id}:null;
  if(['comparison','mechanism'].includes(perspective)){
    const first=entriesForPerspective(state.model,perspective)[0];return first?{kind:'item',id:first.id}:null;
  }
  return null;
};
function focusFor(perspective,focus){
  if(!focus)return defaultFocus(perspective);
  if(perspective==='anatomy')return focus.kind==='genre'?focus:defaultFocus(perspective);
  if(perspective==='comparison')return focus.kind==='item'&&state.model.items.some(i=>i.id===focus.id&&i.type==='trope')?focus:defaultFocus(perspective);
  if(perspective==='mechanism')return focus.kind==='item'&&entriesForPerspective(state.model,'mechanism').some(i=>i.id===focus.id)?focus:defaultFocus(perspective);
  return focus;
}
function historyState(replace=false){
  const url=serializeFixtureRoute(state.route);
  if(replace)window.history.replaceState({route:state.route},'',url);
  else window.history.pushState({route:state.route},'',url);
}
function setFocus(ref){
  const target=focusFor(current().perspective,ref);
  if(same(target,current().focus))return;
  state.route={...current(),focus:target,viaLinkId:null};
  $('detail-panel').hidden=true;
  historyState(true);render();
}
function inspect(id){
  const node=state.model.items.find(i=>i.id===id);
  if(!node)return;
  $('detail-panel').hidden=false;
  $('detail-title').textContent=node.label;
  $('detail-description').textContent=node.description;
  $('detail-source').textContent=`Source: ${node.source_ref} · ${node.derivation.replaceAll('_',' ')} · ${node.certainty} · DERIVED / NOT CANON`;
  const list=$('detail-relations');list.replaceChildren();
  for(const link of linksForFocus(state.links,{kind:'item',id})){
    const target=nameOf(link.target);if(!target)continue;
    const p=el('p','source-note',`${link.verb} ${target} · ${link.supportStatus==='hypothesis'?'Hypothesis':'Source-backed proposal'} · ${link.sourceRef}`);
    list.append(p);
  }
  $('detail-panel').scrollIntoView({behavior:'smooth',block:'nearest'});
}
function navigateByLink(link,destination,event){
  const from=current()?.focus;
  if(!from||!linksForFocus(state.links,from).some(l=>l.id===link.id&&same(l.target,destination)))return;
  const view=preferredPerspective(state.model,destination);
  if(!view){showUnavailable('This connection has no supported explanatory destination.');return;}
  const snapshot={scrollY:window.scrollY,focusLocator:event?.currentTarget?.dataset?.navFocus||null};
  state.route=visitRoute(current(),{perspective:view,focus:destination},link.id,snapshot);
  $('detail-panel').hidden=true;
  historyState();render(true);
}
function linkHref(ref){const view=preferredPerspective(state.model,ref);return view?serializeFixtureRoute({storyId:state.story,perspective:view,focus:ref}):'#';}
function linkCallback(){const cb=(link,target,event)=>navigateByLink(link,target,event);cb.hrefFor=linkHref;return cb;}
function semanticLink(root,link,target,copy){
  const a=el('a','semantic-link',copy);
  a.href=linkHref(target);a.dataset.navFocus=link.id+'-'+target.kind+'-'+target.id;
  a.dataset.linkId=link.id;
  a.addEventListener('click',event=>{
    if(event.button!==0||event.ctrlKey||event.metaKey||event.altKey||event.shiftKey)return;
    event.preventDefault();navigateByLink(link,target,event);
  });root.append(a);return a;
}
function showUnavailable(message){const alert=$('navigation-unavailable');alert.textContent=message;alert.hidden=false;}
function renderOverview(root){
  root.append(el('h2','stage-heading','The story at a glance'));
  root.append(el('p','stage-subtitle','One working proposal, grouped by meaning. Follow only recorded or explicitly hypothetical links.'));
  root.append(el('div','overview-note',`${state.model.title} — ${state.model.vision}`));
  const grid=el('div','overview-grid');
  const groups=[['Genres',state.model.genres],['Tropes',state.model.items.filter(x=>x.type==='trope')],
    ['Narrative engines',state.model.items.filter(x=>['engine','structure'].includes(x.type))],
    ['Experience & framing',state.model.items.filter(x=>['emotion','framing'].includes(x.type))]];
  for(const [title,nodes] of groups){
    const col=el('section','map-column');col.append(el('h3','',title));
    for(const n of nodes){
      const ref={kind:n.type?'item':'genre',id:n.id};
      const button=el('button',`node-button ${n.type||'genre'}`);button.type='button';
      button.append(el('strong','',n.label),el('small','',n.story_treatment?.replaceAll('_',' ')||n.role));
      button.setAttribute('aria-pressed',String(same(ref,current().focus)));
      button.addEventListener('click',()=>{
        if(ref.kind==='genre')openPerspective('anatomy',ref);
        else {setFocus(ref);inspect(ref.id);}
      });col.append(button);
    }grid.append(col);
  }root.append(grid);
  // A visited item remains explorable without automatically opening the inspector.
  if(current().focus?.kind==='item'){
    const region=el('section','overview-related');region.append(el('h3','','Related explanations'));
    const relations=linksForFocus(state.links,current().focus);
    if(!relations.length)region.append(el('p','muted','No declared relationship for this element.'));
    for(const link of relations){
      const target=nameOf(link.target);
      semanticLink(region,link,link.target,`${link.verb} → ${target} · ${link.supportStatus==='hypothesis'?'Hypothesis':'Source-backed proposal'}`);
    }
    root.append(region);
  }
}
function renderArrivalContext(){
  const context=$('arrival-context'),trail=$('semantic-trail'),returnButton=$('semantic-return');
  const route=current(),crumbs=route.trail||[];
  trail.replaceChildren();context.replaceChildren();
  returnButton.hidden=!crumbs.length;
  $('back-overview').hidden=route.perspective==='overview';
  if(crumbs.length){
    const older=crumbs.slice(0,-3),recent=crumbs.slice(-3);
    if(older.length){
      const details=el('details','earlier-hops');const summary=el('summary','','Earlier ('+older.length+')');details.append(summary);
      older.forEach((entry,i)=>{const b=el('button','crumb',nameOf(entry.focus)||entry.perspective);b.type='button';b.addEventListener('click',()=>jumpTrail(i));details.append(b);});
      trail.append(details);
    }
    recent.forEach((entry,i)=>{
      const b=el('button','crumb',nameOf(entry.focus)||entry.perspective);b.type='button';
      b.addEventListener('click',()=>jumpTrail(older.length+i));trail.append(b);
    });
    trail.append(el('span','crumb-current',nameOf(route.focus)||route.perspective));
  }
  trail.hidden=!crumbs.length;
  if(!route.viaLinkId||!crumbs.length){context.hidden=true;return;}
  const origin=crumbs[crumbs.length-1].focus;
  const link=linksForFocus(state.links,origin).find(l=>l.id===route.viaLinkId&&same(l.target,route.focus));
  if(!link){context.hidden=true;showUnavailable('The source of this relationship is unavailable. Return to an earlier view.');return;}
  const summary=el('p','',`From “${nameOf(origin)}” → ${link.verb} → “${nameOf(route.focus)}”`);
  const status=el('small','source-note',`${link.supportStatus==='hypothesis'?'Hypothesis · not a verified genre rule':'Source-backed proposal · not accepted'} · ${link.sourceRef}`);
  const inspectButton=el('button','inspect-link-source','Inspect source');inspectButton.type='button';
  inspectButton.addEventListener('click',()=>{const source=link.target.kind==='item'?link.target:origin; if(source?.kind==='item')inspect(source.id);});
  context.append(summary,status,inspectButton);context.hidden=false;
}
function jumpTrail(index){
  let route=current();const steps=route.trail.length-index;
  for(let n=0;n<steps;n++)route=returnRoute(route);
  state.route=route;historyState();render(true);
}
function returnToPrevious(){
  if(!current().trail.length)return;
  state.route=returnRoute(current());
  // Browser history stays coherent: both physical Back and explicit Back restore the previous state.
  window.history.back();
}
function openPerspective(perspective,requested=null){
  if(!modes[perspective])return;
  state.route={...current(),perspective,focus:focusFor(perspective,requested),viaLinkId:null,trail:[]};
  $('detail-panel').hidden=true;historyState();render(true);
}
let pendingFocus=null;
async function render(focusHeading=false){
  const serial=++state.renderSerial,root=$('explanation-main');root.replaceChildren();
  const mode=current().perspective;
  $('view-description').textContent=modes[mode];
  $('navigation-unavailable').hidden=true;
  for(const b of document.querySelectorAll('[data-perspective]')){
    const active=b.dataset.perspective===mode;b.setAttribute('aria-selected',String(active));b.tabIndex=active?0:-1;
  }
  renderArrivalContext();
  const chosen=current().focus;
  if(mode==='overview')renderOverview(root);
  else{
    const files={anatomy:'./views/anatomy.mjs',comparison:'./views/comparison.mjs',mechanism:'./views/mechanism.mjs'};
    try{
      const view=await import(files[mode]);if(serial!==state.renderSerial)return;
      const callback=linkCallback();const focus=ref=>setFocus(ref);const inspectItem=id=>inspect(id);
      if(mode==='anatomy')view.renderAnatomy(root,state.model,chosen?.id,callback,focus,inspectItem,state.links);
      if(mode==='comparison')view.renderComparison(root,state.model,chosen?.id,callback,focus,inspectItem,state.links);
      if(mode==='mechanism')view.renderMechanism(root,state.model,chosen?.id,callback,focus,inspectItem,state.links);
    }catch(error){root.replaceChildren(el('p','empty-state',`This perspective is unavailable: ${error.message}`));}
  }
  if(serial!==state.renderSerial)return;
  const h=root.querySelector('h2');if(h){h.tabIndex=-1;if(focusHeading)h.focus({preventScroll:true});}
  const r=current();if(r.returnFocusLocator){
    const target=[...document.querySelectorAll('[data-nav-focus]')].find(e=>e.dataset.navFocus===r.returnFocusLocator);
    if(target)target.focus({preventScroll:true});
  }
  if(r.returnScrollY!==undefined && r.returnScrollY!==null)window.scrollTo({top:r.returnScrollY,behavior:'instant'});
}
async function loadStory(storyId,desired=null,replace=true){
  if(!cache[storyId]){
    const [story,evidence]=await Promise.all([fetch('./fixtures/'+storyId+'.json').then(r=>{if(!r.ok)throw Error('Missing story');return r.json();}),
      fetch('./fixtures/genre-evidence.json').then(r=>r.json())]);
    cache[storyId]=normalizeEvidence(story,evidence);
  }
  state.story=storyId;state.model=cache[storyId];state.links=deriveSemanticLinks(state.model);
  const candidate=desired || {storyId,perspective:'overview',focus:null,viaLinkId:null,trail:[]};
  const checked=reconcileRoute(candidate,state.model,state.links);
  state.route={...checked.route,focus:focusFor(checked.route.perspective,checked.route.focus)};
  $('story-select').value=storyId;
  $('detail-panel').hidden=true;
  $('fixture-note').textContent=state.model.fixture_note;
  $('provenance-summary').textContent='Illustrative fixture · Proposed, not accepted · Missing genre packs explicitly marked';
  historyState(replace);
  await render();
  if(checked.issue)showUnavailable(checked.issue);
}
for(const b of document.querySelectorAll('[data-perspective]')){
  b.addEventListener('click',()=>openPerspective(b.dataset.perspective));
  b.addEventListener('keydown',e=>{
    if(!['ArrowRight','ArrowLeft','Home','End'].includes(e.key))return;
    e.preventDefault();const all=[...document.querySelectorAll('[data-perspective]')],i=all.indexOf(b);
    const next=e.key==='Home'?0:e.key==='End'?all.length-1:(i+(e.key==='ArrowRight'?1:-1)+all.length)%all.length;
    all[next].focus();openPerspective(all[next].dataset.perspective);
  });
}
$('story-select').addEventListener('change',e=>loadStory(e.target.value,null,false));
$('back-overview').addEventListener('click',()=>openPerspective('overview'));
$('semantic-return').addEventListener('click',returnToPrevious);
$('close-details').addEventListener('click',()=>{$('detail-panel').hidden=true;$('explanation-main').focus();});
window.addEventListener('popstate',event=>{
  const route=event.state?.route || parseFixtureRoute(window.location.hash);
  if(route && (!state.model || route.storyId!==state.story))loadStory(route.storyId,route,true).catch(e=>showUnavailable(e.message));
  else if(route){
    const before=current(),checked=reconcileRoute(route,state.model,state.links);
    let next={...checked.route,focus:focusFor(checked.route.perspective,checked.route.focus)};
    // Browser Back restores the invoking link's actual focus, not just the view title.
    if(before?.trail?.length){
      const prior=returnRoute(before);
      if(prior.storyId===next.storyId && prior.perspective===next.perspective && same(prior.focus,next.focus))
        next={...next,returnFocusLocator:prior.returnFocusLocator,returnScrollY:prior.returnScrollY};
    }
    state.route=next;
    $('detail-panel').hidden=true;render(true).then(()=>{if(checked.issue)showUnavailable(checked.issue);});
  }
});
const initial=parseFixtureRoute(window.location.hash);
loadStory(initial?.storyId||$('story-select').value,initial,true).catch(error=>showUnavailable(`Could not load story: ${error.message}`));
