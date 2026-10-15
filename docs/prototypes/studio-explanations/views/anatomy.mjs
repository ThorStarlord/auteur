/** Genre grammar with navigable, attributed uses in this story. */
import {linksForFocus} from '../semantic-links.mjs';
const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
function anchor(link,onNavigate,label){
  const a=el('a','story-link semantic-link',label);a.href=onNavigate.hrefFor(link.target);
  a.dataset.linkId=link.id;a.dataset.navFocus=link.id+'-'+link.target.kind+'-'+link.target.id;
  a.addEventListener('click',event=>{
    if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
    event.preventDefault();onNavigate(link,link.target,event);
  });return a;
}
export function renderAnatomy(root,model,genreId,onNavigate,onFocus,onInspect,links){
  const genre=model.genres.find(g=>g.id===genreId)||model.genres[0];
  root.append(el('div','small-label','PERSPECTIVE A / GENRE ANATOMY'));
  root.append(el('h2','stage-heading','What makes a genre work?'));
  root.append(el('p','stage-subtitle','A convention is a reusable narrative possibility, not a universal recipe or an instruction to the author.'));
  if(!genre){root.append(el('p','empty-state','No genre in this story.'));return;}
  const selector=el('div','selection-controls');
  model.genres.forEach(g=>{
    const b=el('button','',g.label);b.type='button';b.setAttribute('aria-pressed',String(g.id===genre.id));
    b.addEventListener('click',()=>onFocus({kind:'genre',id:g.id}));selector.append(b);
  });root.append(selector);
  const layout=el('div','anatomy-layout'),main=el('section','anatomy-primary');
  const promise=el('div','anatomy-promise');promise.append(el('div','small-label','READER PROMISE'),el('h3','',genre.promise));main.append(promise);
  const engine=el('section','anatomy-engine');engine.append(el('div','small-label','GENRE ENGINE'));
  const cycle=el('div','anatomy-cycle');genre.engine_steps.forEach((step,i)=>{
    if(i)cycle.append(el('span','cycle-arrow','→'));
    const card=el('div','cycle-step');card.append(el('span','cycle-count',String(i+1).padStart(2,'0')),el('strong','',step));cycle.append(card);
  });
  engine.append(cycle,el('p','loop-note','↻ A possible recurring mechanism—not mandatory act boundaries.'));main.append(engine);
  const lower=el('div','anatomy-dual');
  for(const [label,content] of [['TYPICAL PRESSURE',genre.conflict],['POSSIBLE PAYOFF',genre.payoff]]){
    const card=el('section','diagram-card');card.append(el('div','small-label',label),el('p','',content));lower.append(card);
  }
  main.append(lower);layout.append(main);
  const side=el('aside','anatomy-side');side.append(el('div','small-label','SOURCE COVERAGE'));
  const badge=el('div',genre.coverage==='inference_only'?'coverage-alert':'coverage-supported',
    genre.coverage==='inference_only'?'Working hypothesis — no versioned pack':
    genre.coverage==='legacy_contract'?'Legacy genre contract, not a versioned pack':'Source status: '+genre.coverage.replaceAll('_',' '));
  side.append(badge,el('p','source-note',genre.coverage_note),el('p','source-note','Reference: '+genre.source_ref));
  side.append(el('h3','aside-heading','How this story employs it'));
  const declared=linksForFocus(links,{kind:'genre',id:genre.id});
  if(!declared.length)side.append(el('p','muted','No declared links to story elements.'));
  for(const link of declared){
    const node=model.items.find(n=>n.id===link.target.id);if(!node)continue;
    side.append(anchor(link,onNavigate,`Explore how ${genre.label} ${link.verb} ${node.label} · ${link.supportStatus==='hypothesis'?'Hypothesis':'Source-backed proposal'}`));
  }
  layout.append(side);root.append(layout);
}
