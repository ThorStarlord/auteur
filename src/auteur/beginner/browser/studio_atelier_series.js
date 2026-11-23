/* Living Narrative Atelier — Series and Book context (opt-in, read-only).
   Pure helpers over the Studio's series-context projection. A concept is joined to a Book plan only by
   a reference that Book records to the concept's own node id; nothing is joined by equal wording, and
   the project's Series plan and Directions are never joined to a concept or to each other.
   Nothing here writes, accepts or links anything. */
(function(global){
  'use strict';
  var COLLECTION={function:'Book function',inherited:'Inherited Series condition',engines:'Engine',agents:'Agent',
    choice:'Central choice','choice.options':'Choice option','choice.costs_kept_visible':'Cost kept visible',
    'choice.transformation':'Transformation',local_resolution:'Local resolution',series_consequences:'Consequence for the Series',
    later_possibilities:'Later possibility',assumptions:'Assumption',alternatives:'Alternative',unresolved:'Unresolved',
    open_author_decisions:'Open author decision'};
  // What the Working Book owner says each element's standing is. None of these is a commitment.
  var AUTHORITY={agent_working:'agent working proposal',undecided:'undecided',author_reserved:'reserved for the author',
    not_adopted:'hypothetical, not adopted',not_established:'source not established',withdrawn:'withdrawn'};
  var DEPENDENCY={sets_up:'sets up',pays_off:'pays off',depends_on:'depends on',pressures:'pressures',
    contradicts:'contradicts',transforms:'transforms'};

  function sources(ctx){return ctx&&ctx.sources||{};}
  function books(ctx){var w=sources(ctx).working_books;return w&&w.books||[];}

  // Every recorded reference to one Architecture node, Book by Book, exactly as each Book records it.
  function forNode(ctx,nodeId){
    if(!nodeId)return [];
    var out=[];
    books(ctx).forEach(function(book){
      if(book.state!=='working')return;
      (book.references||[]).forEach(function(ref){if(ref.node_id===nodeId)out.push({book:book,ref:ref});});
    });
    return out;
  }
  function count(ref){return {elements:(ref.elements||[]).length,edges:(ref.edges||[]).length};}
  function plural(n,word,many){return n+' '+(n===1?word:(many||word+'s'));}
  function refSummary(ref){var c=count(ref),parts=[];
    if(c.elements)parts.push(plural(c.elements,'element'));if(c.edges)parts.push(plural(c.edges,'typed edge'));
    return parts.join(' and ')||'a reference';}

  // The Working Book owner's own freshness, said plainly. It compares the Book with the current
  // working Architecture; it is not acceptance and not a judgement of the Book.
  function bookFreshness(book){
    var lines=[];
    if(book.freshness==='ready')lines.push({tone:'ok',text:'Written against the current working Architecture.'});
    else{
      if(book.series_changed)lines.push({tone:'warn',text:'Written against an earlier working Architecture request; the Architecture has changed since.'});
      if(book.source_changed)lines.push({tone:'warn',text:'Its Book source items in the canvas changed after it was written.'});
    }
    if(book.semantic_impact==='suspect')lines.push({tone:'warn',text:'Some concepts it refers to were reworded or changed after it was written.'});
    if(book.semantic_impact==='contradictory')lines.push({tone:'bad',text:'A concept it refers to is no longer in the working Architecture.'});
    return lines;
  }
  function refStanding(ref){
    if(!ref.present)return {tone:'bad',text:'No longer in the working Architecture.'};
    if(ref.changed_since_book)return {tone:'warn',text:'This concept changed after the Book was written.'};
    if(ref.changed_since_book===false)return {tone:'ok',text:'This concept is unchanged in the Architecture since the Book was written.'};
    return null;
  }

  // The Book Direction owner records which Series Direction revision it was accepted against.
  function directionBookFreshness(book){
    if(book.freshness==='current')return {tone:'ok',text:'Accepted against the current Series Direction (revision '+book.current_series_revision+').'};
    if(book.freshness==='series_direction_revised')return {tone:'warn',
      text:'Accepted against Series Direction revision '+book.accepted_against_series_revision+'; the Series Direction is now revision '+
        book.current_series_revision+'. Whether it needs review is for its owner to decide.'};
    return {tone:'warn',text:'Accepted against Series Direction revision '+book.accepted_against_series_revision+
      '; the current Series Direction does not verify, so whether this is current cannot be told.'};
  }

  // What the project keeps, owner by owner, for a one-line orientation. Counts only; no linking.
  function projectSummary(ctx){
    var s=sources(ctx),out=[];
    var plan=s.series_plan,dir=s.series_direction;
    if(plan&&plan.state==='available')out.push({owner:'series_plan',tone:'ok',text:'Series plan “'+plan.title+'” · '+
      plural(plan.books.length,'Book plan')+', '+plural(plan.setups.length,'setup')+', '+plural(plan.payoffs.length,'payoff')+
      ' · author-declared, '+plan.path});
    else if(plan&&(plan.state==='invalid'||plan.state==='unreadable'))out.push({owner:'series_plan',tone:'bad',text:plan.path+' could not be read as a Series plan.'});
    if(dir&&dir.state!=='absent'){
      var ser=dir.series||{},acc=(dir.books||[]).filter(function(b){return b.state==='accepted';}).length;
      var parts=[];
      if(ser.state==='accepted')parts.push('Series Direction “'+ser.title+'” accepted, revision '+ser.revision);
      else if(ser.state==='unverified')parts.push('a Series Direction that no longer matches its acceptance record');
      if(acc)parts.push(plural(acc,'accepted Book Direction'));
      if(dir.state==='unreadable')parts.push('Series journey records that could not be read');
      out.push({owner:'series_direction',tone:ser.state==='unverified'?'bad':'ok',text:parts.join(' · ')||'Series journey records'});
    }
    return out;
  }
  function workingBooks(ctx){return books(ctx).filter(function(b){return b.state==='working';});}
  // A Book (or the whole Book source) that could not be read is reported: it may hold a reference.
  function unreadableBooks(ctx){
    var w=sources(ctx).working_books;
    if(w&&w.state==='unreadable')return ['The working Book architectures could not be read, so whether one records this concept cannot be told.'];
    return books(ctx).filter(function(b){return b.state!=='working';}).map(function(b){
      return 'Book '+b.book_number+'’s working architecture could not be read, so whether it records this concept cannot be told.';});
  }
  // Proposal files the Series journey keeps; which one is behind an accepted record is known only when it verifies.
  function proposalNote(dir){
    var files=dir.proposal_files||{},total=(files.series_direction||0)+(files.book_direction||0);
    var other=dir.other_proposals||{},n=(other.series_direction||0)+(other.book_direction||0);
    var accepted=(dir.series&&dir.series.state==='accepted')||(dir.books||[]).some(function(b){return b.state==='accepted';});
    if(!total)return 'The Series journey keeps no proposal files.';
    if(!accepted)return 'The Series journey keeps '+plural(total,'proposal file')+' and no accepted record. Proposals are not plans, and they are not shown.';
    if(!dir.proposals_accounted)return 'The Series journey keeps '+plural(total,'proposal file')+'. A record here does not verify, so which proposal is behind it cannot be told. Proposals are not shown.';
    return n?'The Series journey also keeps '+plural(n,'proposal file')+' besides those behind the accepted records shown here. They are earlier or were never accepted, and they are not shown.':
      'Each proposal file the Series journey keeps is behind an accepted record shown here.';
  }

  // Plain words for a hypothesis the author may ask the coding agent to investigate. It names the source
  // so the agent can read it; it asserts no link.
  function hypothesisDraft(conceptTitle,recordLabel,source){
    return 'Investigate as a hypothesis, not a recorded link: does “'+conceptTitle+'” relate to '+recordLabel+
      ' ('+source.path+(source.ref?' · '+source.ref:'')+')? Read that source directly. Nothing in either records a link, '+
      'so describe any connection as a possibility for me to judge, and change nothing.';
  }
  function shortHash(h){if(!h)return '';var t=String(h).replace(/^sha256:/,'');return 'sha256:'+t.slice(0,10);}
  function sourceLine(src){
    if(!src)return '';
    var parts=[src.path+(src.ref?' · '+src.ref:'')];
    if(src.revision!==null&&src.revision!==undefined)parts.push('revision '+src.revision);
    if(src.content_hash)parts.push(shortHash(src.content_hash));
    return parts.join(' · ');
  }

  global.AuteurAtelierSeries={forNode:forNode,count:count,refSummary:refSummary,bookFreshness:bookFreshness,refStanding:refStanding,
    directionBookFreshness:directionBookFreshness,projectSummary:projectSummary,workingBooks:workingBooks,
    hypothesisDraft:hypothesisDraft,unreadableBooks:unreadableBooks,proposalNote:proposalNote,sourceLine:sourceLine,shortHash:shortHash,plural:plural,
    COLLECTION:COLLECTION,AUTHORITY:AUTHORITY,DEPENDENCY:DEPENDENCY};
})(window);
