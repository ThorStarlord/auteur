/* Read-only three-surface review. No model calls, persistence, or canon acceptance. */
import {unionGraphLayout,focusedGraphDiff} from './studio_architecture_revision_compare.mjs';
const MODES=['summary','compare','focus'];
const LABELS={node:'Narrative entity',link:'Directed relationship',emotion_target:'Emotional target',
  complex_emotion:'Complex emotion',genre_contract:'Genre contract',genre_interaction:'Genre interaction',
  phase:'Narrative phase',summary:'Governing summary'};
const str=value=>typeof value==='string'?value:JSON.stringify(value,null,2);
export function mountRevisionReview(root,{comparison,document:doc=(typeof document!=='undefined'?document:null),initialMode='summary'}={}) {
  if (!doc || !root || comparison?.status!=='ready') throw new Error('A DOM root and ready review are required');
  const layout=unionGraphLayout(comparison);
  let mode=MODES.includes(initialMode)?initialMode:'summary';
  let focus=null, mobileSide='before', filter='', destroyed=false, lastMode='compare', layer='differences';
  const make=(tag,text,cls,id)=>{const el=doc.createElement(tag);if(text!==undefined)el.textContent=str(text);if(cls)el.className=cls;if(id)el.id=id;return el};
  const append=(parent,...children)=>{parent.append(...children);return parent};
  const btn=(text,callback,cls)=>{const b=make('button',text,cls);b.type='button';b.addEventListener('click',callback);return b};
  const labelled=(text)=>make('span',text,'label');
  const changeName=entry=>entry.kind==='summary'?'Governing summary':
    str((entry.afterRecord||entry.beforeRecord)?.title || (entry.afterRecord||entry.beforeRecord)?.emotion || entry.id);
  function choose(item){focus={kind:item.kind,id:item.id};lastMode=mode==='focus'?lastMode:mode;mode='focus';render('focus-back');}
  function switchMode(next){if(!MODES.includes(next))return;if(next!=='focus')lastMode=next;mode=next;render('mode-'+next);}
  function renderSummary(){
    const section=make('section',undefined,'summary','revision-summary');
    append(section,make('h2','What changed in the working architecture?'),
      make('p',comparison.requestedChange?'Requested change: '+comparison.requestedChange:'No recorded revision request text.'),
      make('p','Revised architecture summary (not an agent causal rationale): '+comparison.afterCandidate.summary),
      make('p','The comparison shows observable source differences only. It does not establish creative quality, downstream effects, or accepted-story compliance.','note'));
    const cnt=comparison.summary;
    append(section,make('p',cnt.added+' added · '+cnt.removed+' removed · '+cnt.changed+' changed · '+cnt.unchanged+' unchanged records.','summary-count'));
    for(const warning of cnt.authorDeclaredWarnings)append(section,make('p',warning,'warning'));
    const requirements=make('section',undefined,'requirements');
    append(requirements,make('h3','Requirements to check (not verified)'));
    if(comparison.acceptedConstraints.length){const ul=make('ul');for(const item of comparison.acceptedConstraints)append(ul,append(make('li'),make('span',item)));append(requirements,ul)}
    else append(requirements,make('p','No separately verified accepted constraints supplied to this comparison.'));
    append(section,requirements);
    return section;
  }
  function renderIndex(){
    const box=make('section',undefined,'change-index','change-index');
    append(box,make('h2','Explore changed entities and relationships'));
    const search=make('input',undefined,'index-search','change-search');search.type='search';search.value=filter;
    search.placeholder='Filter by title, category or ID';search.setAttribute('aria-label','Filter changes');
    search.addEventListener('input',()=>{const cursor=search.selectionStart;filter=search.value;render('change-search');const next=doc.getElementById('change-search');if(next&&typeof next.setSelectionRange==='function')next.setSelectionRange(cursor,cursor)});
    append(box,search);
    const list=make('ul',undefined,'change-list');
    const visible=comparison.items.filter(item=>{
      const text=(item.kind+' '+item.id+' '+changeName(item)+' '+item.change).toLowerCase();
      return !filter||text.includes(filter.toLowerCase());
    }).sort((a,b)=>(a.change==='unchanged')-(b.change==='unchanged')||a.kind.localeCompare(b.kind)||a.id.localeCompare(b.id));
    for(const entry of visible){
      const li=make('li',undefined,'change-row');
      const action=btn(changeName(entry)+' · '+(LABELS[entry.kind]||entry.kind)+' · '+entry.change,()=>choose(entry),'change-action');
      action.dataset.changeKind=entry.kind;action.dataset.changeId=entry.id;
      if(focus?.kind===entry.kind&&focus?.id===entry.id)action.setAttribute('aria-current','true');
      append(li,action);append(list,li);
    }
    if(!visible.length)append(box,make('p','No matching source records.'));
    append(box,list);return box;
  }
  function renderGraph(side){
    const graph=side==='before'?layout.beforeGraph:layout.afterGraph;
    const box=make('section',undefined,'architecture-side','side-'+side);box.dataset.side=side;
    append(box,make('h3',side==='before'?'Before — current working architecture':'After — un-applied agent proposal'));
    append(box,make('p',side==='before'?'Request '+comparison.beforeRequestSha:'Request '+comparison.afterRequestSha+' (synthetic in this research fixture)'));
    const scroll=make('div',undefined,'graph-scroll');const canvas=make('div',undefined,'graph-canvas');
    const width=Math.max(600,...Object.values(layout.positionsByNodeId).map(p=>p.x+180));
    canvas.style.width=width+'px';canvas.style.height=Math.max(150,layout.rows*112+48)+'px';
    const svg=doc.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 '+width+' '+Math.max(150,layout.rows*112+48));
    svg.setAttribute('class','graph-edges');svg.setAttribute('aria-hidden','true');
    for(const e of graph.edges){
      const a=layout.positionsByNodeId[e.source],b=layout.positionsByNodeId[e.target];if(!a||!b)continue;
      const path=doc.createElementNS('http://www.w3.org/2000/svg','path');
      const sx=a.x+154,sy=a.y+26,tx=b.x,ty=b.y+26;
      path.setAttribute('d','M '+sx+' '+sy+' Q '+((sx+tx)/2)+' '+((sy+ty)/2-17)+' '+tx+' '+ty);
      path.setAttribute('class','edge '+e.change);svg.appendChild(path);
    }
    append(canvas,svg);
    for(const n of graph.nodes){
      const button=btn(n.title+' · '+n.category,()=>choose(comparison.items.find(item=>item.kind==='node'&&item.id===n.id)),'architecture-node '+n.change);
      button.dataset.graphKind='node';button.dataset.graphId=n.id;button.style.left=n.position.x+'px';button.style.top=n.position.y+'px';
      button.setAttribute('aria-label',side+' '+n.title+' '+n.change+' working narrative entity');
      if(focus?.kind==='node'&&focus?.id===n.id)button.classList.add('is-selected');append(canvas,button);
    }
    append(scroll,canvas);append(box,scroll);
    const links=make('details',undefined,'relationship-index');append(links,make('summary','Inspectable recorded relationships ('+graph.edges.length+')'));
    const list=make('ul');for(const edge of graph.edges){
      const item=comparison.items.find(x=>x.kind===edge.kind&&x.id===edge.id);if(!item)continue;
      const li=make('li');const button=btn((edge.kind==='link'?'Link ':'Genre interaction ')+edge.id+': '+edge.source+' → '+edge.target+' · '+edge.change,()=>choose(item));
      button.dataset.changeKind=item.kind;button.dataset.changeId=item.id;append(li,button);append(list,li);
    }append(links,list);append(box,links);
    return box;
  }
  function renderCompare(){
    const section=make('section',undefined,'comparison','comparison');
    append(section,make('h2','Before and after — separate working snapshots'));
    const label=make('label','Mobile view: ');label.htmlFor='mobile-side';
    const select=make('select',undefined,'mobile-control','mobile-side');for(const [value,text] of [['before','Before'],['after','After'],['differences','Differences']]){const option=make('option',text);option.value=value;append(select,option)}
    select.value=mobileSide;select.addEventListener('change',()=>{mobileSide=select.value;render('mobile-side')});append(label,select);append(section,label);
    const panels=make('div',undefined,'graph-pair');panels.dataset.mobileSide=mobileSide;append(panels,renderGraph('before'),renderGraph('after'));append(section,panels);
    if(mobileSide==='differences')append(section,make('p','Select a changed entry in the source-grounded change index below to inspect exact before/after fields.','mobile-differences'));
    return section;
  }
  function makeValue(label,value){const details=make('details',undefined,'raw-record');append(details,make('summary',label));append(details,make('pre',value===null?'Not present':str(value)));return details}
  function renderOverlay(focused){
    const section=make('section',undefined,'local-overlay','focused-overlay');
    append(section,make('h3','Focused recorded neighborhood — before / after'));
    const tabs=make('nav',undefined,'layer-controls');tabs.setAttribute('aria-label','Focused overlay layers');
    for(const l of ['before','after','differences']){const b=btn(l==='differences'?'Differences':l==='before'?'Before':'After',()=>{layer=l;render('layer-'+l)},'layer-button');b.id='layer-'+l;b.setAttribute('aria-pressed',String(layer===l));append(tabs,b)}
    append(section,tabs);
    const view=make('div',undefined,'overlay-visual');view.dataset.layer=layer;
    const old=focused.beforeNeighborhood, newer=focused.afterNeighborhood;
    const all=[...new Set([...old.nodes.map(x=>x.id),...newer.nodes.map(x=>x.id)])].slice(0,12);
    if(!all.length){append(view,make('p','This component has no spatial graph node; inspect its exact field differences below.'))}
    else{
      const svg=doc.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 640 '+(Math.max(150,Math.ceil(all.length/4)*108)));
      svg.setAttribute('role','img');svg.setAttribute('aria-label','Illustrative local positioning of only recorded before and after relationships; the written field comparison is authoritative.');
      const pos=Object.fromEntries(all.map((id,i)=>[id,{x:15+(i%4)*156,y:10+Math.floor(i/4)*108}]));
      const edges=(list,tag)=>{for(const e of list.edges){const a=pos[e.source],b=pos[e.target];if(!a||!b)continue;const line=doc.createElementNS('http://www.w3.org/2000/svg','line');for(const [key,val] of Object.entries({x1:a.x+55,y1:a.y+28,x2:b.x+55,y2:b.y+28,class:'overlay-edge '+tag}))line.setAttribute(key,String(val));svg.appendChild(line)}};
      if(layer!=='after')edges(old,'before');if(layer!=='before')edges(newer,'after');
      for(const id of all){const p=pos[id];const rect=doc.createElementNS('http://www.w3.org/2000/svg','rect');for(const [k,v] of Object.entries({x:p.x,y:p.y,width:135,height:56,rx:8,class:'overlay-node'}))rect.setAttribute(k,String(v));svg.appendChild(rect);const text=doc.createElementNS('http://www.w3.org/2000/svg','text');text.setAttribute('x',p.x+8);text.setAttribute('y',p.y+30);text.textContent=id.slice(0,20);svg.appendChild(text)}
      append(view,svg);append(view,make('p','Before: '+old.edges.length+' recorded local links. After: '+newer.edges.length+' recorded local links. Edge geometry is not narrative causality.','note'));
    }
    append(section,view);return section;
  }
  function renderFocus(){
    const section=make('section',undefined,'focus-pane','focus-pane');
    append(section,make('h2','Focused semantic difference'));
    const back=btn('Back to '+(lastMode==='compare'?'whole comparison':'summary'),()=>switchMode(lastMode),'focus-back');back.id='focus-back';append(section,back);
    if(!focus){append(section,make('p','Select an item from the change index to inspect precise differences.'));return section}
    const focused=focusedGraphDiff(comparison,focus),item=focused.focus;
    append(section,make('h3',changeName(item)+' · '+(LABELS[item.kind]||item.kind)+' · '+item.change));
    append(section,make('p','Before: '+(item.beforeSourceRef||'not present')+' · request '+comparison.beforeRequestSha));
    append(section,make('p','After: '+(item.afterSourceRef||'not present')+' · request '+comparison.afterRequestSha));
    if(focused.missingSide)append(section,make('p','Absent from '+focused.missingSide+' candidate; no title-based pairing.','warning'));
    append(section,renderOverlay(focused));
    const fields=make('section',undefined,'field-comparison','field-comparison');append(fields,make('h3','Recorded field changes (full values)'));
    if(!item.changedFields.length)append(fields,make('p',item.change==='unchanged'?'No recorded field changes.':'This element exists on only one side; expand the full records below.'));
    for(const f of item.changedFields){const entry=make('article',undefined,'field-delta');append(entry,make('h4',f.field),make('p','Before'),make('pre',f.beforePresent?str(f.beforeValue):'Not present'),make('p','After'),make('pre',f.afterPresent?str(f.afterValue):'Not present'));append(fields,entry)}
    append(section,fields,makeValue('Full Before record',item.beforeRecord),makeValue('Full After record',item.afterRecord));return section;
  }
  function render(focusId){if(destroyed)return;root.replaceChildren();
    append(root,make('p','READ-ONLY WORKING ARCHITECTURE REVIEW · No story canon accepted here.','eyebrow'));
    const menu=make('nav',undefined,'mode-menu');menu.setAttribute('aria-label','Review modes');
    for(const m of MODES){const b=btn(m==='summary'?'Readable summary':m==='compare'?'Compare graphs':'Focused differences',()=>switchMode(m),'mode-button');b.dataset.mode=m;b.id='mode-'+m;b.setAttribute('aria-pressed',String(mode===m));append(menu,b)}append(root,menu);
    append(root,renderSummary());if(mode==='compare')append(root,renderCompare());if(mode==='focus')append(root,renderFocus());append(root,renderIndex());
    append(root,make('p','No visual operation changes working architecture. Applying the entire revision remains a separate explicit Studio action.','note'));
    if(focusId){const target=doc.getElementById(focusId);if(target&&target.focus)target.focus()}
  }
  render();return {setMode:switchMode,selectFocus:select=>{focus={kind:select.kind,id:select.id};mode='focus';render('focus-back')},reset:()=>{focus=null;mode='summary';render()},destroy:()=>{destroyed=true;root.replaceChildren()}};
}