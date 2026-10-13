/** Derived decision review; no acceptance, persistence or provider actions. */
const rvEl=(tag,cls,value)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(value!==undefined)e.textContent=value;return e;};
function renderReviewArchitecture(root,report,{onFocusRef,onReturn}){
  root.replaceChildren();
  root.append(rvEl('p','eyebrow','REVIEW THE WHOLE STORY'),rvEl('h2','','Review Full Architecture'),
    rvEl('p','review-status',report.status==='ready_for_author_review'?'Ready for author review — not accepted canon':'Working design — open decisions remain'),
    rvEl('p','review-intro',report.summary));
  const toolbar=rvEl('div','review-actions'),back=rvEl('button','','Return to architecture');back.type='button';
  back.addEventListener('click',onReturn);toolbar.appendChild(back);root.appendChild(toolbar);
  const list=rvEl('div','review-items');
  for(const item of report.items){
    const row=rvEl('article','review-item');
    row.append(rvEl('strong','',item.id.replaceAll('-',' ').replaceAll(':',' · ').replace(/^./,c=>c.toUpperCase())),
      rvEl('span','review-state',item.state.replaceAll('_',' ')),rvEl('p','',item.why));
    if(item.focusTarget&&!item.focusTarget.startsWith('genre:')){
      const focus=rvEl('button','','Work on this decision');focus.type='button';focus.addEventListener('click',()=>onFocusRef(item.focusTarget));row.appendChild(focus);
    }
    list.appendChild(row);
  }
  root.appendChild(list);
  root.appendChild(rvEl('p','review-disclaimer','Unknown Genre Pack coverage is not an authoring failure. Optional scene planning is not required. Reviewing cannot accept story canon.'));
}
