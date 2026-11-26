/* Presentation helpers for the Atelier's opportunity discovery: pure words over the owner's projection. Nothing here
   decides anything; each function says what the owner recorded. */
(function(global){'use strict';
  var KINDS={
    thematic_resonance:'Thematic resonance',
    shared_mechanism:'Shared dramatic mechanism',
    productive_tension:'Productive tension',
    overlooked_consequence:'Overlooked consequence',
    narrative_inheritance:'Narrative inheritance',
    productive_independence:'Productive independence',
    consolidation:'Creative consolidation'
  };
  var REFS={
    node:'Architecture element',
    link:'Recorded link',
    genre_interaction:'Genre interaction',
    question:'Open question',
    book_decision:'Working Book decision',
    candidate_opportunity:'Recorded opportunity'
  };

  function kindLabel(kind){return (kind&&KINDS[kind])||null;}

  // The transferability the owner judged now. Never a stored verdict; a question no longer open is said plainly.
  function statusWords(status){
    if(!status)return {label:'Status not read',tone:'note'};
    if(status.state==='transferable')return {label:'Ready to investigate',tone:'ok'};
    if(status.state==='reworded')return {label:'Ready, formulated against an earlier wording',tone:'warn'};
    if(status.state==='not_transferable')return {label:'Cannot be investigated: a question is no longer open',tone:'bad'};
    if(status.state==='no_current_architecture')return {label:'No current working Architecture',tone:'note'};
    return {label:'Not transferable here',tone:'note'};
  }

  // One evidence item, as its kind, its identifier, whether it is still in the Architecture, and the agent's note on it.
  function evidenceLine(item){
    var kind=REFS[item.ref_kind]||item.ref_kind;
    var where=item.book_number!=null?' (Book '+item.book_number+')':'';
    var now=item.present_now===true?'still in the Architecture'
      :item.present_now===false?'no longer in the Architecture'
      :'read again when it is investigated';
    return kind+' · '+item.ref_id+where+' · '+now+'. The agent’s note: '+item.note;
  }

  // Whether the author may take a possibility into deliberation now.
  function canInvestigate(possibility){
    return !!(possibility&&possibility.status&&possibility.status.transferable&&
      !(possibility.decision&&possibility.decision.decision==='declined'));
  }

  global.AuteurAtelierDiscovery={kindLabel:kindLabel,statusWords:statusWords,evidenceLine:evidenceLine,
    canInvestigate:canInvestigate,KINDS:KINDS,REFS:REFS};
})(typeof window!=='undefined'?window:this);
