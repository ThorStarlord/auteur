/** One-hop mechanism paths. A link is navigable only when in the source record. */
import {connectionsForSelection} from '../model.mjs';
import {linksForFocus} from '../semantic-links.mjs';
const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
function anchor(link,onNavigate,label){
  const a=el('a','mechanism-node semantic-link',label);a.href=onNavigate.hrefFor(link.target);
  a.dataset.linkId=link.id;a.dataset.navFocus=link.id+'-'+link.target.kind+'-'+link.target.id;
  a.addEventListener('click',event=>{
    if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
    event.preventDefault();onNavigate(link,link.target,event);
  });return a;
}
export function renderMechanism(root,model,itemId,onNavigate,onFocus,onInspect,links){
  const choices=model.items.filter(n=>['trope','engine','structure'].includes(n.type));
  const current=choices.find(n=>n.id===itemId)||choices[0];
  root.append(el('div','small-label','PERSPECTIVE C / NARRATIVE MECHANISM'));
  root.append(el('h2','stage-heading','What makes the story move?'));
  root.append(el('p','stage-subtitle','Follow one proposed mechanism at a time. Arrows appear only for explicitly recorded relationships; intended effects are not guaranteed outcomes.'));
  const nav=el('div','selection-controls');
  for(const item of choices){
    const b=el('button','',item.label);b.type='button';b.setAttribute('aria-pressed',String(item.id===current?.id));
    b.addEventListener('click',()=>onFocus({kind:'item',id:item.id}));nav.append(b);
  }root.append(nav);
  if(!current){root.append(el('p','empty-state','No mechanisms recorded in this fixture.'));return;}
  const focus=el('section','mechanism-focus');focus.append(el('div','small-label','SELECTED NARRATIVE ELEMENT'),el('h3','',current.label));
  focus.append(el('p','',current.description));root.append(focus);
  const declared=connectionsForSelection(model,current.id),targets=linksForFocus(links,{kind:'item',id:current.id});
  if(!declared.length){root.append(el('div','empty-state','No supported relationship is recorded for this element; a missing arrow means unknown, not incompatible.'));return;}
  const stage=el('section','mechanism-connections'),textList=document.createElement('ol');textList.className='mechanism-text-equivalent';
  for(const edge of declared){
    const from=model.items.find(x=>x.id===edge.source),to=model.items.find(x=>x.id===edge.target);
    const neighbor=from.id===current.id?to:from;
    const link=targets.find(l=>l.target.kind==='item'&&l.target.id===neighbor.id&&l.sourceRef===edge.source_ref);
    const row=el('article','mechanism-row'),diagram=el('div','mechanism-track');
    const present=(n)=>n.id===current.id?el('span','mechanism-node selected-mechanism-node',n.label):
      link?anchor(link,onNavigate,`Explore ${n.label}`):el('span','mechanism-node',n.label);
    const verb=el('div','mechanism-verb');verb.append(el('span','mechanism-arrow','→'),el('strong','',edge.verb));
    diagram.append(present(from),verb,present(to));row.append(diagram);
    row.append(el('div',edge.support_status==='source_backed'?'link-status backed':'link-status hypothesis',
      edge.support_status==='source_backed'?'SOURCE-BACKED RELATION':'HYPOTHESIS · NOT PROVEN'));
    row.append(el('p','mechanism-explanation',edge.explanation));
    row.append(el('p','source-note','Declared source: '+edge.source_ref));stage.append(row);
    const li=el('li','',`${from.label} ${edge.verb} ${to.label}. ${edge.explanation}. ${edge.support_status==='source_backed'?'Source-backed proposal':'Hypothesis; not proven'}. Source: ${edge.source_ref}`);
    textList.append(li);
  }
  root.append(stage);const details=document.createElement('details');details.className='mechanism-accessible';
  details.append(el('summary','', 'Read all relationships as text'),textList);root.append(details);
  const inspect=el('button','inspect-link-source','Inspect source of selected element');inspect.type='button';inspect.addEventListener('click',()=>onInspect(current.id));root.append(inspect);
}
