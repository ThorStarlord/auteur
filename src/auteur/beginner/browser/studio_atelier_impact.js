/* Living Narrative Atelier — what Architecture changes mean for the working Books (opt-in, read-only).
   Pure helpers over the working Book records in the Studio's series-context projection. Every fact comes
   from a Working Book record and its owner: which Architecture concepts a Book records a reference to, by
   node id; whether each is unchanged, changed or no longer present, judged by the fingerprint the Book
   kept; the version it recorded, when a kept record still holds that exact fingerprint; and the Book's own
   freshness. A changed reference is evidence to re-read, never a verdict on the story; a Book that records
   no reference to a concept is not shown to be independent of it; an unreadable Book is never "unaffected".
   Nothing here writes, links or decides anything. */
(function(global){
  'use strict';
  var SERIES=global.AuteurAtelierSeries||{},BOOK=global.AuteurAtelierBook||{};
  var COLLECTION=SERIES.COLLECTION||{};
  var FIELD={title:'name',category:'kind',summary:'description',scope:'scope',parent_id:'parent'};

  function plural(n,word,many){return n+' '+(n===1?word:(many||word+'s'));}
  function andList(xs){xs=(xs||[]).filter(Boolean);if(xs.length<3)return xs.join(' and ');return xs.slice(0,-1).join(', ')+' and '+xs[xs.length-1];}
  function clip(text,n){return BOOK.clip?BOOK.clip(text,n):String(text==null?'':text).slice(0,n||90);}

  // A recorded concept's name: the atlas's own name while it is present, else the version the Book recorded.
  function refName(ref,nameOf){
    var live=ref.present&&nameOf?nameOf(ref.node_id):null;
    return live||(ref.current&&ref.current.title)||(ref.recorded&&ref.recorded.title)||ref.node_id;
  }
  function citing(ref,withIds){
    return (ref.elements||[]).map(function(e){return (COLLECTION[e.collection]||String(e.collection).replace(/[._]/g,' '))+
      (withIds?' '+e.id:'')+(e.via==='name_source'?' (takes its name from it)':'')+' · “'+clip(e.text,70)+'”';})
      .concat((ref.edges||[]).map(function(e){return 'Link · '+e.source_element+' '+String(e.dependency).replace(/_/g,' ')+' it';}));
  }

  // One working Book, its recorded references sorted by what the owner established about each.
  function entry(book){
    if(book.state!=='working')return {book:book,number:book.book_number,state:'unreadable',reason:book.reason,
      architectureUnreadable:book.cause==='architecture'};
    var by={changed:[],removed:[],unrecorded:[],unchanged:[],architecture_unavailable:[]};
    (book.references||[]).forEach(function(r){(by[r.status]||by.unrecorded).push(r);});
    return {book:book,number:book.book_number,state:'working',changed:by.changed,removed:by.removed,
      noArchitecture:by.architecture_unavailable.length>0,
      unrecorded:by.unrecorded,unchanged:by.unchanged,architectureChanged:!!book.series_changed,
      sourceChanged:!!book.source_changed,since:book.architecture_revisions_since,
      flagged:by.changed.length+by.removed.length>0,outOfDate:book.freshness!=='ready'};
  }

  // Every working Book of the canvas, grouped by what is recorded. Counts and groups only: no score.
  function summarize(ctx){
    var w=ctx&&ctx.sources&&ctx.sources.working_books;if(!w)return null;
    var entries=(w.books||[]).map(entry),working=entries.filter(function(e){return e.state==='working';});
    var concepts={},order=[];
    working.forEach(function(e){e.changed.concat(e.removed).forEach(function(r){
      if(!concepts[r.node_id]){concepts[r.node_id]={node_id:r.node_id,status:r.status,ref:r,books:[]};order.push(r.node_id);}
      concepts[r.node_id].books.push(e.number);});});
    return {state:w.state,reason:w.reason||null,entries:entries,revisions:w.architecture_revisions||0,
      flagged:working.filter(function(e){return e.flagged;}),
      outOfDateOnly:working.filter(function(e){return !e.flagged&&e.outOfDate;}),
      current:working.filter(function(e){return !e.flagged&&!e.outOfDate;}),
      unreadable:entries.filter(function(e){return e.state!=='working';}),
      concepts:order.map(function(k){return concepts[k];}),
      without:w.without_working_book||[],requestedOnly:w.requested_only||[]};
  }
  // Something worth showing: a Book to reconsider, one out of date, one unreadable, or one never recorded.
  function noteworthy(sum){return !!sum&&(sum.state==='unreadable'||sum.flagged.length>0||sum.outOfDateOnly.length>0||sum.unreadable.length>0);}

  function sinceLine(e){
    if(e.state!=='working'||!e.architectureChanged||e.noArchitecture)return '';
    if(e.since===null||e.since===undefined)return e.book.architecture_chain_complete===false?
      'How many Architecture revisions ago it was written cannot be told: the revision history could not be read in full.':
      'Written against a working Architecture version that is not on its current revision chain.';
    return 'Written against the working Architecture as it was '+plural(e.since,'applied revision')+' ago.';
  }
  // What is established about one Book, line by line, each line one kind of fact.
  function lines(e,nameOf){
    if(e.state!=='working')return [{tone:'bad',text:e.architectureUnreadable?
      'The working Architecture’s record cannot be read, so whether this Book is affected cannot be told.':
      'Its working record is damaged and cannot be read, so whether it is affected cannot be told.'}];
    var out=[];
    if(e.noArchitecture)return [{tone:'bad',text:'The working Architecture cannot be read, so whether the concepts it cites changed cannot be told.'}];
    if(e.changed.length)out.push({tone:'warn',text:'Cites '+plural(e.changed.length,'concept')+' that changed after it was written: '+
      andList(e.changed.map(function(r){return '“'+refName(r,nameOf)+'”';}))+'.'});
    if(e.removed.length)out.push({tone:'warn',text:'Cites '+plural(e.removed.length,'concept')+' no longer in the working Architecture: '+
      andList(e.removed.map(function(r){return '“'+refName(r,nameOf)+'”';}))+'.'});
    if(!e.flagged&&e.architectureChanged)out.push({tone:'warn',text:'The Architecture changed after it was written, but every concept it cites is unchanged. '+
      'That shows its recorded references did not change, not that the Book is unaffected.'+
      (notCitedCount(e)?' What changed is not cited by it: '+notCitedNames(e,4)+'.':'')});
    if(e.unrecorded.length)out.push({tone:'warn',text:'For '+plural(e.unrecorded.length,'concept')+' it cites, the version it was written against is not recorded, so whether '+
      (e.unrecorded.length===1?'it':'they')+' changed cannot be told.'});
    if(e.sourceChanged)out.push({tone:'warn',text:'Its own source items in the canvas changed after it was written. That is a change to the Book’s source, not to the Architecture.'});
    if(!out.length)out.push({tone:'ok',text:'Written against the current working Architecture.'});
    return out;
  }
  function notCited(e){var n=e.book&&e.book.architecture_changes_not_cited;return n?{changed:n.changed||[],removed:n.removed||[],added:n.added||[]}:null;}
  function notCitedCount(e){var n=notCited(e);return n?n.changed.length+n.removed.length+n.added.length:0;}
  function notCitedNames(e,max){var n=notCited(e);if(!n)return '';
    var all=n.changed.map(function(x){return '“'+x.title+'” (changed)';}).concat(n.removed.map(function(x){return '“'+x.title+'” (removed)';}),
      n.added.map(function(x){return '“'+x.title+'” (new)';}));
    return all.length>max?all.slice(0,max).join(', ')+' and '+(all.length-max)+' more':andList(all);}
  // How many Books cite one concept, short once the list grows.
  function citedBy(books){return books.length>4?'cited by '+books.length+' Books':'cited by '+andList(books.map(function(n){return 'Book '+n;}));}
  // What a changed or removed concept was, and what it is now, from the two records.
  function conceptChange(ref){
    var was=ref.recorded,now=ref.current;
    return {status:ref.status,was:was,now:now,known:!!was,
      fields:(ref.fields_changed||[]).map(function(f){return FIELD[f]||f.replace(/_/g,' ');}),
      titleChanged:!!(was&&now&&was.title!==now.title),
      summary:was&&now&&was.summary!==now.summary&&BOOK.wordDiff?BOOK.wordDiff(was.summary,now.summary):null};
  }

  // The author's starting words for a whole-Book revision, built only from recorded evidence. The author
  // edits them before anything is prepared; nothing here asserts what the Book must become.
  function reconcileDraft(e,nameOf){
    var n=e.number,out=[(e.architectureChanged?'Reconcile working Book '+n+' with the revised working Architecture.':
      'Bring working Book '+n+' up to date with its changed source items.')+' What its record shows:'];
    e.changed.forEach(function(r){var c=conceptChange(r);out.push('- “'+refName(r,nameOf)+'” changed after this Book was written'+
      (c.fields.length?' (its '+andList(c.fields)+')':'')+'. Cited by: '+clip(citing(r,true).join('; '),600)+'.');});
    e.removed.forEach(function(r){out.push('- “'+refName(r,nameOf)+'” is no longer in the working Architecture. Cited by: '+clip(citing(r,true).join('; '),600)+'.');});
    if(!e.flagged&&e.architectureChanged)out.push('- The Architecture changed after this Book was written, but every concept it cites is unchanged.');
    if(notCitedCount(e))out.push('- Also changed in the Architecture since, and not cited by this Book: '+notCitedNames(e,12)+
      '. Check whether the Book should take '+(notCitedCount(e)===1?'it':'them')+' into account; otherwise keep it as written.');
    if(e.sourceChanged)out.push('- Its own source items changed in the canvas; read them again.');
    out.push((e.flagged?'Re-read these elements against the current Architecture and decide what, if anything, should change. Keep what still holds, ':
      'Change only what the current Architecture requires, if anything. ')+(e.removed.length?'stop citing concepts that are gone, ':'')+
      'and leave author decisions open. Whether the story still works is mine to judge.');
    var text=out.join('\n');return text.length>3900?text.slice(0,3899)+'…':text;
  }
  // A question for the existing coding-agent panel: an investigation, never a change.
  function inquiryDraft(e,ref,nameOf){
    var c=conceptChange(ref),name=refName(ref,nameOf);
    return 'Working Book '+e.number+' cites “'+name+'”, which changed after the Book was written'+(c.fields.length?' (its '+andList(c.fields)+')':'')+
      '. It is cited by: '+clip(citing(ref).join('; '),500)+'. As a hypothesis to test, not a finding: what might this change mean for those elements '+
      'and for the Book? Say what you are unsure of, and change nothing.';
  }

  var OVERVIEW_NOTE='Each Book records which Architecture concepts it refers to and the version it was written against. A cited concept that changed '+
    'is worth re-reading; it does not mean the Book no longer works. A Book that records no reference to a concept is not shown to be independent of it.';

  global.AuteurAtelierImpact={entry:entry,summarize:summarize,noteworthy:noteworthy,lines:lines,sinceLine:sinceLine,refName:refName,
    citing:citing,conceptChange:conceptChange,notCited:notCited,notCitedNames:notCitedNames,citedBy:citedBy,reconcileDraft:reconcileDraft,inquiryDraft:inquiryDraft,andList:andList,plural:plural,
    OVERVIEW_NOTE:OVERVIEW_NOTE};
})(typeof window!=='undefined'?window:this);
