/** Candidate B: genre-relative convention and story-specific treatment are separate axes. */
const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
const treatmentLabels={proposed_adoption:'Adopts a familiar possibility',proposed_adaptation:'Adapts a familiar possibility',proposed_story_specific:'Story-specific variation',proposed_subversion:'Proposes a deliberate reversal',unresolved:'Treatment not yet decided'};
export function renderComparison(root,model,itemId,onSelect,onFocus){
  const tropes=model.items.filter(n=>n.type==='trope');
  const item=tropes.find(n=>n.id===itemId)||tropes[0];
  root.append(el('div','small-label','PERSPECTIVE B / CONVENTION VS. INVENTION'));
  root.append(el('h2','stage-heading','Where does the genre end—and this story begin?'));
  root.append(el('p','stage-subtitle','Compare conventions with the proposed treatment. A convention may serve several genres differently; undocumented does not mean incompatible or original.'));
  const select=el('div','selection-controls');for(const trope of tropes){
    const button=el('button','',trope.label);button.type='button';button.setAttribute('aria-pressed',String(item.id===trope.id));
    button.addEventListener('click',()=>{root.replaceChildren();renderComparison(root,model,trope.id,onSelect,onFocus);onFocus(trope.id);});select.append(button);
  }root.append(select);
  if(!item){root.append(el('p','empty-state','No proposed trope in this fixture.'));return;}
  const grid=el('div','comparison-layout');const left=el('section','comparison-col compare-left');
  left.append(el('div','small-label','GENRE KNOWLEDGE'),el('h3','contrast-title','What a genre may supply'));
  if(!item.genre_links.length)left.append(el('p','empty-state','No documented genre relationship. Unknown is not an exclusion.'));
  for(const link of item.genre_links){
    const genre=model.genres.find(g=>g.id===link.genre_id), card=el('article','comparison-source');
    card.append(el('strong','',genre.label),el('span','tag soft',link.relation.replaceAll('_',' ')));
    card.append(el('p','',link.coverage==='inference_only'?'Not classified by a versioned pack — a working hypothesis, not a rule.':
      link.coverage==='legacy_contract'?'Legacy contract context; not a universal genre requirement.':'Evidence category: '+link.coverage));
    card.append(el('p','source-note',`Evidence: ${link.source_ref} · Rule strength: ${link.rule_strength||'not established'}`));
    left.append(card);
  }
  const right=el('section','comparison-col compare-right');right.append(el('div','small-label','THIS STORY PROPOSES'));
  right.append(el('h3','contrast-title',item.label));right.append(el('div','treatment-label',treatmentLabels[item.story_treatment]));
  right.append(el('p','story-statement',item.description));
  right.append(el('p','source-note',`Story interpretation: ${item.derivation.replaceAll('_',' ')} · ${item.certainty} · ${item.source_ref}`));
  right.append(el('p','subtle-warning','Story-specific means distinctive within this proposal, not proven original in literature.'));
  const central=el('span','compare-bridge','⇄');central.setAttribute('aria-label','Compare the genre and this story');
  grid.append(left,central,right);root.append(grid);
  const synthesis=el('section','comparison-synthesis');synthesis.append(el('div','small-label','HOW THEY MEET'));
  const functions=item.genre_links.map(l=>model.genres.find(g=>g.id===l.genre_id)?.label+' '+l.relation+' this element.');
  synthesis.append(el('p','',functions.length?functions.join(' '):'No genre-specific function is supported by this fixture.'));
  const inspect=el('button','', 'Inspect provenance and neighboring mechanisms ↗');inspect.type='button';
  inspect.addEventListener('click',()=>onSelect(item.id));synthesis.append(inspect);root.append(synthesis);
}
