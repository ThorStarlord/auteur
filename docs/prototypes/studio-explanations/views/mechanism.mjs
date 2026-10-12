/** Candidate C: only fixture-explicit functional links can form visible arrows. */
import {connectionsForSelection} from '../model.mjs';
const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
export function renderMechanism(root,model,itemId,onSelect,onFocus){
  const choices=model.items.filter(n=>['trope','engine','structure'].includes(n.type));
  const current=choices.find(n=>n.id===itemId)||choices[0];
  root.append(el('div','small-label','PERSPECTIVE C / NARRATIVE MECHANISM'));
  root.append(el('h2','stage-heading','What makes the story move?'));
  root.append(el('p','stage-subtitle','Follow one proposed mechanism at a time. Arrows appear only for explicitly recorded relationships; intended effects are not guaranteed outcomes.'));
  const nav=el('div','selection-controls');
  for(const item of choices){const b=el('button','',item.label);b.type='button';b.setAttribute('aria-pressed',String(item.id===current?.id));
    b.addEventListener('click',()=>{root.replaceChildren();renderMechanism(root,model,item.id,onSelect,onFocus);onFocus(item.id);});nav.append(b);}
  root.append(nav);
  if(!current){root.append(el('p','empty-state','No mechanisms recorded in this fixture.'));return;}
  const focus=el('section','mechanism-focus');focus.append(el('div','small-label','SELECTED NARRATIVE ELEMENT'),el('h3','',current.label));
  focus.append(el('p','',current.description));root.append(focus);
  const declared=connectionsForSelection(model,current.id);
  if(!declared.length){
    root.append(el('div','empty-state','No supported relationship is recorded for this element; a missing arrow means unknown, not incompatible.'));
    return;
  }
  const stage=el('section','mechanism-connections');const textList=document.createElement('ol');textList.className='mechanism-text-equivalent';
  for(const edge of declared){
    const from=model.items.find(x=>x.id===edge.source),to=model.items.find(x=>x.id===edge.target);
    const row=el('article','mechanism-row');const diagram=el('div','mechanism-track');
    const a=el('button','mechanism-node');a.type='button';a.textContent=from.label;a.addEventListener('click',()=>{root.replaceChildren();renderMechanism(root,model,from.id,onSelect,onFocus);onFocus(from.id);});
    const verb=el('div','mechanism-verb');verb.append(el('span','mechanism-arrow','→'),el('strong','',edge.verb));
    const b=el('button','mechanism-node');b.type='button';b.textContent=to.label;b.addEventListener('click',()=>{root.replaceChildren();renderMechanism(root,model,to.id,onSelect,onFocus);onFocus(to.id);});
    diagram.append(a,verb,b);row.append(diagram);
    row.append(el('div',edge.support_status==='source_backed'?'link-status backed':'link-status hypothesis',
      edge.support_status==='source_backed'?'SOURCE-BACKED RELATION':'HYPOTHESIS · NOT PROVEN'));
    row.append(el('p','mechanism-explanation',edge.explanation));
    row.append(el('p','source-note','Declared source: '+edge.source_ref));stage.append(row);
    const li=el('li','',`${from.label} ${edge.verb} ${to.label}. ${edge.explanation}. ${edge.support_status==='source_backed'?'Source-backed proposal':'Hypothesis; not proven'}. Source: ${edge.source_ref}`);textList.append(li);
  }
  root.append(stage);const details=document.createElement('details');details.className='mechanism-accessible';
  details.append(el('summary','', 'Read all relationships as text'),textList);root.append(details);
}
