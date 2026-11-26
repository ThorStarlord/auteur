/* Living Narrative Atelier — the working Architecture's open questions (opt-in, read-only).
   Pure helpers over the read projection of the Architecture owner (studio_architecture_question_projection):
   continuing questions with an established identity, wording-only questions that have none, and questions no
   longer open. Each formulation, reason and Book reference is said as the owner recorded it. Identity is never
   inferred from wording, a removal is never an answer, and an unreadable history is said to be unreadable.
   Nothing here writes, accepts, settles or asks anything. */
(function(global){
  'use strict';
  var B=global.AuteurAtelierBook||{};

  function plural(n,word,many){return n+' '+(n===1?word:(many||word+'s'));}
  function clip(text,n){text=String(text==null?'':text).replace(/\s+/g,' ').trim();n=n||140;
    return text.length>n?text.slice(0,n-1).replace(/\s+\S*$/,'')+'…':text;}
  function shortSha(sha){return sha?String(sha).slice(0,8):'';}
  function numbered(data){return !!(data&&data.current&&data.current.numbered);}

  // A version in words. A complete history numbers its revisions; otherwise a version is named by its digest.
  function label(v){
    if(!v)return 'an earlier revision';
    return v.revision_number!==null&&v.revision_number!==undefined?'revision '+v.revision_number:'version '+shortSha(v.request_sha256);
  }
  function Label(v){var s=label(v);return s.charAt(0).toUpperCase()+s.slice(1);}
  // A run of versions, as one phrase. The span keeps each version; the phrase only summarises them.
  function rangeOf(span){
    var from=span.from_revision,to=span.to_revision,n=span.versions?span.versions.length:1;
    if(from===null||from===undefined||to===null||to===undefined)
      return n>1?plural(n,'version'):label(span.versions&&span.versions[0]);
    if(from===to)return 'revision '+from;
    return 'revisions '+from+'–'+to;
  }

  // Which of the owner's identity-bearing questions the author may ask about, as the owner allows it.
  function isAskable(q,data){return !!(q&&q.standing==='continuing'&&q.id&&data&&data.current&&!q.removed);}

  // The question as an Architecture reading: its standing, said once, with what its history can and cannot show.
  function gapLines(history){
    var out=[];
    (history&&history.gaps||[]).forEach(function(g){
      if(g==='chain_incomplete')out.push({tone:'warn',text:'Some earlier revisions cannot be reached, so the history shown may be incomplete.'});
      else if(g==='unreadable_before_first_recorded')out.push({tone:'warn',text:'A revision from before this identity was recorded cannot be read, so whether the question was open then is not shown.'});
      else if(g==='unreadable_within')out.push({tone:'warn',text:'A revision inside this question’s history cannot be read, so the history around it is not shown as continuous.'});
    });
    return out;
  }
  function standing(q,data){
    if(!q)return [];
    if(q.standing==='continuing'){
      var h=q.history||{};
      var first=h.first_recorded_in?Label(h.first_recorded_in):null;
      var text=h.introduced_in_recorded_history&&first?
        'Continuing question. Its identity was first recorded in '+label(h.first_recorded_in)+'; the revisions since are shown below.':
        first?'Continuing question. Its identity is recorded from '+label(h.first_recorded_in)+' on; what came before cannot be read in full.':
        'Continuing question. Its identity is recorded in the current revision only.';
      return [{tone:h.complete?'ok':'warn',text:text}].concat(gapLines(h));
    }
    if(q.standing==='wording_only'){
      var lines=[{tone:'note',text:'Wording only. This question has no recorded identity yet, so it cannot be followed across revisions or asked about as a continuing question. '+
        'An identity is established only when a revision names it.'}];
      return lines.concat(gapLines(q.history));
    }
    if(q.standing==='no_longer_open'){
      var last=(q.spans||[]).filter(function(s){return s.kind==='absent';})[0];
      var when=last?' since '+label({revision_number:last.from_revision,request_sha256:last.versions[0].request_sha256}):'';
      return [{tone:'warn',text:'No longer open in the working Architecture'+when+'. Removing it is not an answer, and nothing here says it was settled.'}]
        .concat(gapLines(q.history));
    }
    return [];
  }
  function askNote(q,data){
    if(isAskable(q,data))return null;
    if(!q)return null;
    if(q.standing==='wording_only')return 'It needs a recorded identity before it can be asked about as a continuing question.';
    if(q.standing==='no_longer_open')return 'A question no longer open cannot be asked about. Asking about what remains is the author’s choice, not a question’s.';
    return null;
  }

  // The reason one version records for its own change: the author's words, or the alternative the author chose.
  function reasonLines(reason){
    if(!reason)return ['The record gives no reason for this change.'];
    if(!reason.readable)return ['The request that made this revision cannot be read, so no reason is shown.'];
    var out=[];
    if(reason.instruction)out.push('Your revision request: “'+clip(reason.instruction,220)+'”');
    if(reason.selected_alternative&&reason.selected_alternative.title)
      out.push('The alternative you chose in the coding-agent desk: “'+clip(reason.selected_alternative.title,140)+'”');
    if(!out.length)out.push('The record gives no reason for this change.');
    return out;
  }
  var CHANGE={
    introduced:'first recorded',
    moved:'moved, same wording',
    reworded:'reworded, same position',
    moved_and_reworded:'moved and reworded',
    removed:'no longer open',
    unverified:'whether it changed cannot be told'
  };
  // One span of the history, said plainly. Unchanged runs say how long they lasted; the versions stay in the record.
  function spanHead(span){
    var r=rangeOf(span),first=span.versions&&span.versions[0],last=span.versions&&span.versions[span.versions.length-1];
    var held=span.versions&&span.versions.length>1&&last?' · wording unchanged through '+label(last):'';
    switch(span.kind){
      case 'present':
        // A change across a version that cannot be read is not claimed either way: it is said, and not counted.
        if(span.change==='unverified')return {tone:'note',text:Label(first)+' · recorded; the version before it cannot be read, so whether it changed is not shown'+(held?'; kept through '+label(last):'')};
        if(span.change==='introduced')return {tone:'ok',text:'First recorded in '+label(first)+held};
        if(span.change&&CHANGE[span.change])return {tone:'warn',text:Label(first)+' · '+CHANGE[span.change]+(held?'; kept through '+label(last):'')};
        return {tone:'note',text:(span.versions.length>1?'Wording unchanged · ':'Recorded · ')+r};
      case 'absent':
        return {tone:'warn',text:'Not in the working Architecture · '+r+'. Removing it is not an answer.'};
      case 'no_identity':
        return {tone:'note',text:'Wording only · '+r+' · no identity recorded'};
      case 'unreadable':
        return {tone:'bad',text:'Cannot be read · '+r+'. What the question said there is not shown.'};
      default:return {tone:'note',text:r};
    }
  }
  function spanVersions(span){
    return (span.versions||[]).map(function(v){return {label:label(v),sha:v.request_sha256||''};});
  }

  // Relationship of one Book decision to the question, as the Book owner states it. Reconsideration may be
  // warranted; the Book is never declared inconsistent, and a removal is never an answer.
  function bookRelation(ref){
    switch(ref&&ref.state){
      case 'current_wording':return {tone:'ok',text:'The decision refers to this question as it now stands.'};
      case 'moved':return {tone:'note',text:'The question now sits at another position with the same wording. The decision still refers to it by identity.'};
      case 'reworded':return {tone:'warn',text:'The decision was written against an earlier wording of this question. The question kept its identity, so this may warrant reconsideration. The Book is not declared inconsistent.'};
      case 'moved_and_reworded':return {tone:'warn',text:'The question has moved and been reworded since the decision was written. This may warrant reconsideration. The Book is not declared inconsistent.'};
      case 'removed':return {tone:'warn',text:'The question is no longer open in the Architecture. Removing it is not an answer, and nothing here decides what the Book should do.'};
      case 'version_unavailable':return {tone:'bad',text:'The Architecture version this decision was written against cannot be read, so its question cannot be followed here.'};
      case 'binding_mismatch':return {tone:'bad',text:'The recorded binding does not match the Architecture version the decision names, so this reference cannot be trusted.'};
      default:return null;
    }
  }
  // The shape the existing Book-originated inquiry takes, from a projected Book reference.
  function bookAskRef(ref){
    return {question_id:ref.question_id,decision_id:ref.decision_id,state:ref.state,
      recorded_text:ref.recorded&&ref.recorded.text,recorded_index:ref.recorded&&ref.recorded.index,
      current_text:ref.current&&ref.current.text,current_index:ref.current&&ref.current.index};
  }

  // Counts for the overview: how often a question's wording or position changed, and where it is recorded.
  function changeCount(q){
    return (q.spans||[]).filter(function(s){return s.kind==='present'&&s.change&&s.change!=='introduced'&&s.change!=='unverified';}).length;
  }
  function booksOf(q){return (q&&q.books)||[];}
  // A continuing identity is the default and needs no chip of its own: the list groups it, and the question says it.
  // Only what sets a question apart is marked: wording without identity, a removal, a change, an incomplete history.
  function chipsFor(q){
    var out=[];
    if(q.standing==='continuing'){
      var c=changeCount(q);
      if(c)out.push({tone:'note',text:plural(c,'change')});
    }else if(q.standing==='wording_only')out.push({tone:'note',text:'Wording only'});
    else if(q.standing==='no_longer_open')out.push({tone:'warn',text:'No longer open'});
    if(q.history&&!q.history.complete&&q.standing!=='wording_only')out.push({tone:'warn',text:'History incomplete'});
    var b=booksOf(q).length;
    if(b)out.push({tone:'note',text:plural(b,'Book decision')});
    return out;
  }
  function overviewNote(data){
    var n=(data.questions||[]).length;
    if(!n)return 'The working Architecture records no open questions.';
    return 'Open questions are the working Architecture’s, not answers. A continuing question keeps its identity across revisions, and its earlier formulations stay with it. Reading a question changes nothing.';
  }
  // Groups for the list of all questions: continuing first, then wording only, then those no longer open.
  function groups(data){
    var qs=data&&data.questions||[],gone=data&&data.no_longer_open||[];
    return {
      continuing:qs.filter(function(q){return q.standing==='continuing';}),
      wording:qs.filter(function(q){return q.standing==='wording_only';}),
      gone:gone
    };
  }
  // Find the question a view names: by its identity, or by position for a question with none.
  function find(data,view){
    if(!data||!view)return null;
    var pool=(data.questions||[]).concat(data.no_longer_open||[]);
    if(view.id)return pool.filter(function(q){return q.id===view.id;})[0]||null;
    return (data.questions||[]).filter(function(q){return !q.id&&q.index===view.index;})[0]||null;
  }
  function keyOf(q){return q.id?'question:'+q.id:'question:index:'+q.index;}

  // Suggested words for the coding-agent desk. They are offered in an empty field and are never sent.
  var SUGGEST={
    explore:'Propose two or more materially different formulations of this question, and say what each would change for the story and for the reader.',
    challenge:'What does this formulation assume, and what would be lost if it stayed exactly as written?',
    explain:'In the author’s terms, what does this question ask?'
  };
  var OPERATIONS=[['explore','Explore alternative formulations'],['challenge','Challenge this formulation'],['explain','Explain what it asks']];

  // Comparing two or three open questions. Suggestions fill an empty field only; the author edits or replaces them,
  // and nothing is sent until the author asks.
  var COMPARE_SUGGEST={
    compare:'Do these questions’ current formulations conceal a shared creative problem?',
    connect_to_ask:'How might these two unresolved questions influence each other’s development?',
    challenge:'Are the creative commitments behind these questions compatible, or should they stay independent? Say what connecting them would cost.',
    explore:'Could one dramatic mechanism help develop all of these questions? Propose alternatives that differ in what each would make possible and what it would cost.'
  };
  var COMPARE_OPERATIONS=[['compare','Compare their meanings'],['connect_to_ask','Explore a possible relationship'],
    ['challenge','Challenge their assumptions'],['explore','Explore shared alternatives']];
  // The owner asks connect_to_ask for exactly two questions; the other operations take two or three.
  function compareOperations(count){return COMPARE_OPERATIONS.filter(function(op){return op[0]!=='connect_to_ask'||count===2;});}
  // Add a question to the comparison, or remove it if it is already there. The owner's limit is three anchors.
  function toggleComparison(list,q){
    if(list.some(function(x){return x.id===q.id;}))return {list:list.filter(function(x){return x.id!==q.id;}),full:false};
    if(list.length>=3)return {list:list,full:true};
    return {list:list.concat([{id:q.id,title:q.text,index:q.index}]),full:false};
  }

  // The shortest honest account of how a Book references a question, for the Book's row.
  function bookFreshnessNote(book){
    if(!book)return null;
    if(book.freshness==='ready')return null;
    return 'This Book is out of date with the working Architecture or its own sources. Its decision is shown as the Book recorded it.';
  }

  global.AuteurAtelierQuestions={
    plural:plural,clip:clip,label:label,Label:Label,rangeOf:rangeOf,numbered:numbered,
    isAskable:isAskable,standing:standing,askNote:askNote,gapLines:gapLines,
    reasonLines:reasonLines,spanHead:spanHead,spanVersions:spanVersions,
    bookRelation:bookRelation,bookAskRef:bookAskRef,changeCount:changeCount,booksOf:booksOf,
    chipsFor:chipsFor,overviewNote:overviewNote,groups:groups,find:find,keyOf:keyOf,
    SUGGEST:SUGGEST,OPERATIONS:OPERATIONS,bookFreshnessNote:bookFreshnessNote,
    COMPARE_SUGGEST:COMPARE_SUGGEST,COMPARE_OPERATIONS:COMPARE_OPERATIONS,compareOperations:compareOperations,
    toggleComparison:toggleComparison,
    CHANGE:CHANGE,wordDiff:B.wordDiff||null
  };
})(typeof window!=='undefined'?window:this);
