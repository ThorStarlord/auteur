/** Candidate A: compact grammar of a genre's possible promises and recurring engine. */
const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};

export function renderAnatomy(root,model,genreId,onSelect){
  const genre=model.genres.find(g=>g.id===genreId)||model.genres[0];
  root.append(el('div','small-label','PERSPECTIVE A / GENRE ANATOMY'));
  root.append(el('h2','stage-heading','What makes a genre work?'));
  root.append(el('p','stage-subtitle','A convention is a reusable narrative possibility, not a universal recipe or an instruction to the author.'));
  const selector=el('div','selection-controls');
  model.genres.forEach(g=>{const b=el('button','',g.label);b.type='button';b.setAttribute('aria-pressed',String(g.id===genre.id));b.addEventListener('click',()=>renderAnatomyAfterChoice(root,model,g.id,onSelect));selector.append(b);});root.append(selector);
  const layout=el('div','anatomy-layout'); const main=el('section','anatomy-primary');
  const promise=el('div','anatomy-promise');promise.append(el('div','small-label','READER PROMISE'),el('h3','',genre.promise));main.append(promise);
  const engine=el('section','anatomy-engine');engine.append(el('div','small-label','GENRE ENGINE'));
  const cycle=el('div','anatomy-cycle');genre.engine_steps.forEach((step,i)=>{if(i)cycle.append(el('span','cycle-arrow','→'));const card=el('div','cycle-step');card.append(el('span','cycle-count',String(i+1).padStart(2,'0')),el('strong','',step));cycle.append(card);});
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
  const matches=model.items.filter(n=>n.genre_links.some(l=>l.genre_id===genre.id));
  if(!matches.length)side.append(el('p','muted','No declared links to story elements.'));
  for(const node of matches){const b=el('button','story-link',node.label);b.type='button';b.addEventListener('click',()=>onSelect(node.id));side.append(b);}
  layout.append(side);root.append(layout);
}
function renderAnatomyAfterChoice(root,model,genreId,onSelect){root.replaceChildren();renderAnatomy(root,model,genreId,onSelect);}
