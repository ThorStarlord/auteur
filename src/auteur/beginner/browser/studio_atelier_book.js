/* Living Narrative Atelier — developing one working Book through its own owner (opt-in).
   Pure helpers over the Studio's Book-development projection, which is the Working Book Architecture
   owner's own lifecycle: prepare → the coding agent's response → review → explicit Apply.
   Nothing here decides anything. Phases, applicability, consequences and standing are the owner's;
   these helpers only say them in words. A mechanical reference is a dependency to inspect, never a
   narrative consequence, and an author decision a revision touches stays the author's. */
(function(global){
  'use strict';
  var SERIES=global.AuteurAtelierSeries||{};
  var COLLECTION=Object.assign({typed_edges:'Typed edge'},SERIES.COLLECTION||{});
  var AUTHORITY=SERIES.AUTHORITY||{};
  var CHANGE={interpretive:'Its wording or interpretation changed',working_status:'Its working status changed',
    withdrawal:'Withdrawn from the working proposal',representation:'Only how its support is labelled changed',
    representation_reclassified_from_legacy:'Restated in the explicit form (what supports it, and where it stands)',
    mechanical:'Only its references changed'};
  var FIELD={text:'wording',interpretation:'interpretation',attribution:'what supports it',epistemic_status:'working status',
    provenance:'legacy label',refs:'references',reversal:'reversal',title:'title',question:'question',pressure:'pressure',
    function:'stated function',dependency:'kind of link',target:'what it points to',source:'where it starts',
    condition:'condition',consequence:'consequence',changed_state:'changed state',choice:'choice',
    new_possibility:'new possibility',rationale:'rationale',name_source:'name source',kind:'kind'};
  // The worded fields that differ between two readings of one element, the main wording first.
  function wordedChanges(before,after){
    var b=before&&before.fields||{},a=after&&after.fields||{},keys=[];
    Object.keys(b).concat(Object.keys(a)).forEach(function(k){if(keys.indexOf(k)<0&&b[k]!==a[k])keys.push(k);});
    keys.sort(function(x,y){return (x==='text'?0:x==='function'?1:2)-(y==='text'?0:y==='function'?1:2);});
    return keys.map(function(k){return {field:FIELD[k]||k.replace(/_/g,' '),key:k,before:b[k]==null?null:b[k],after:a[k]==null?null:a[k]};});
  }

  function clip(text,n){text=String(text==null?'':text).replace(/\s+/g,' ').trim();n=n||90;
    return text.length>n?text.slice(0,n-1).replace(/\s+\S*$/,'')+'…':text;}
  // Elements arrive as the owner's list or as a map by id; both read the same.
  function index(elements){if(elements&&!Array.isArray(elements))return elements;
    var map={};(elements||[]).forEach(function(e){map[e.id]=e;});return map;}
  function kind(collection){return COLLECTION[collection]||String(collection||'Element').replace(/[._]/g,' ');}
  // A Book element in words: its kind and the start of what it says. The id stays available beside it.
  function elementLabel(elements,id){var e=index(elements)[id];
    if(!e)return id;var what=e.title||e.text;return kind(e.collection)+(what?' · “'+clip(what,70)+'”':'');}
  function labels(elements,ids){var map=index(elements);return (ids||[]).map(function(id){return elementLabel(map,id);});}
  function plural(n,word,many){return n+' '+(n===1?word:(many||word+'s'));}

  // Where the Book's own revision lifecycle stands, as the owner reports it.
  function phaseLine(phase,n){
    switch(phase){
      case 'awaiting_coding_agent':return {tone:'warn',text:'A revision request for Book '+n+' is waiting for your coding agent. Nothing in the Book has changed.'};
      case 'review_ready':return {tone:'warn',text:'Your coding agent’s revision of Book '+n+' is ready for your review. The working Book is unchanged until you apply it.'};
      case 'review_blocked':return {tone:'bad',text:'Your coding agent’s revision of Book '+n+' cannot be applied as it is: it changed elements outside what you allowed.'};
      case 'stale':return {tone:'bad',text:'A revision request for Book '+n+' no longer matches the Book or its sources, so it cannot be completed or applied.'};
      case 'unreadable':return {tone:'bad',text:'Book '+n+'’s pending request could not be read, so its state is not shown.'};
      default:return null;
    }
  }
  function staleReason(pending){if(!pending)return '';var r=[];
    if(pending.book_changed)r.push('the working Book changed after it was prepared');
    if(pending.context_changed)r.push('the working Architecture or the Book’s source changed after it was prepared');
    return r.join(', and ');}

  // What a targeted request permits: the chosen elements and the elements that refer to them (the owner's rule).
  function scopeSentence(scope,elements){
    if(!scope)return '';
    var extra=(scope.dependents||[]).length;
    return extra?'Your coding agent may change '+(scope.targets.length===1?'this element':'these '+scope.targets.length+' elements')+
      ' and the '+plural(extra,'element')+' that refer'+(extra===1?'s':'')+' to '+(scope.targets.length===1?'it':'them')+
      ', so those references can be kept true. Every other element must stay exactly as it is.':
      'Your coding agent may change only '+(scope.targets.length===1?'this element':'these elements')+'. Every other element must stay exactly as it is.';
  }

  // The owner's review, said in words. Mechanical links stay links to inspect; nothing becomes causation.
  function reviewDigest(review,elements,conceptName,reviewElements){
    // Elements are named from the working Book, and new ones from the reviewed candidate.
    var map=index(elements),cand=index(reviewElements||[]),name=conceptName||function(id){return id;};
    var both=Object.assign({},cand,map);
    function label(id){return elementLabel(both,id);}
    var ch=review.changes||{added:[],changed:[],removed:[]};
    return {
      fromRevision:review.baseline&&review.baseline.revision_number,toRevision:review.revision_number,
      mode:review.mode,instruction:review.instruction,applicable:!!review.applicable,
      permitted:review.permitted_ids?labels(map,review.permitted_ids):null,
      changed:(ch.changed||[]).map(function(c){
        var worded=cand[c.id]?wordedChanges(map[c.id],cand[c.id]):(c.before_text!=null?[{field:'wording',key:'text',before:c.before_text,after:c.after_text}]:[]);
        // The owner calls a change with no new statement text mechanical; a link whose stated function changed is reworded.
        var reworded=c.classification==='mechanical'&&worded.some(function(w){return w.key==='function';});
        return {id:c.id,label:label(c.id),kind:reworded?'The wording of this link changed':(CHANGE[c.classification]||c.classification),
          classification:c.classification,before:c.before_text,after:c.after_text,worded:worded,
          fields:(c.fields_changed||[]).map(function(f){return FIELD[f]||f.replace(/_/g,' ');})};}),
      added:(ch.added||[]).map(function(a){var e=cand[a.id];return {id:a.id,label:e?elementLabel(cand,a.id):kind(a.collection)+' · '+a.id,
        text:e?(e.fields&&(e.fields.text||e.fields.function))||e.text||'':'',refersTo:(a.references||[]).map(label)};}),
      removed:(ch.removed||[]).map(function(r){return {id:r.id,label:label(r.id)};}),
      preserved:review.preserved?review.preserved.count:0,
      unexpected:(review.unexpected_changes||[]).map(function(u){return {id:u.id,label:map[u.id]?label(u.id):u.id,
        text:(map[u.id]?label(u.id):u.id)+' — '+(u.change==='added'?'added':u.change)+': '+u.reason};}),
      reread:(review.consequence_candidates||[]).map(function(c){return label(c.id)+' refers to '+c.via.map(label).join(' and ')+
        ', which this revision changes. Re-read it: the reference is recorded, whether it still holds is not.';})
        .concat((review.dependency_implications||[]).map(function(i){return label(i.from)+' refers to '+label(i.to)+'.';})),
      series:(review.series_consequences||[]).map(function(s){var who=s.cited_by.map(label).join(', ');
        return s.exists_in_series?{tone:'note',text:'“'+name(s.series_node_id)+'” is cited by '+who+'. The Architecture is unchanged; check that the Book still fits it.'}:
          {tone:'bad',text:who+' cites '+s.series_node_id+', which the working Architecture no longer records.'};}),
      decisions:(review.author_decisions||[]).map(function(d){return label(d.decision_id)+' is touched by '+d.touched_by.map(label).join(', ')+
        '. It stays yours to decide; this revision does not decide it.';}),
      authority:(review.authority_changes||[]).map(function(a){return label(a.id)+': '+(AUTHORITY[a.before]||a.before)+' → '+(AUTHORITY[a.after]||a.after)+'.';}),
      unresolved:(review.unresolved_effects||[]).map(function(u){return label(u.id)+': its wording changed but the Book records no dependency for it, so what follows from the change is not established.';}),
      identity:[['Review of request',review.request_sha256],['Baseline Book request',review.baseline&&review.baseline.request_sha256],
        ['Baseline content',review.baseline&&review.baseline.content_sha256],['Baseline revision',review.baseline&&String(review.baseline.revision_number)],
        ['Scope',review.mode==='holistic'?'whole Book (holistic)':'targeted']],
      note:review.note
    };
  }
  // A blocked review can be prepared again with the elements it touched outside the scope allowed too.
  function widenedTargets(review,elements){var map=index(elements),out=(review.permitted_ids||[]).filter(function(id){return map[id];});
    (review.unexpected_changes||[]).forEach(function(u){if(map[u.id]&&out.indexOf(u.id)<0)out.push(u.id);});
    return out.filter(function(id){return map[id].collection!=='typed_edges';});}

  // What the author can give a coding agent. It names the owner's own commands; it runs nothing.
  function agentMessage(handoff,n,canvas,pending){
    if(!handoff)return '';
    return 'Please fulfil the pending Working Book '+n+' revision request in the Auteur canvas “'+canvas+'”'+
      (pending&&pending.instruction?' (“'+clip(pending.instruction,140)+'”)':'')+'.\n'+
      '1. Read the request: '+handoff.show+'\n'+
      '2. Write the complete revised Book '+n+' as one JSON object. Change only the permitted elements, and restate each element you change in the explicit form.\n'+
      '3. Submit it: '+handoff.complete+'\n'+
      'Submitting stores a review for me to read; it does not change the working Book. Guide: '+handoff.guide;
  }
  function shortSha(sha){return sha?String(sha).slice(0,12):'';}

  global.AuteurAtelierBook={CHANGE:CHANGE,elementLabel:elementLabel,labels:labels,phaseLine:phaseLine,staleReason:staleReason,
    scopeSentence:scopeSentence,reviewDigest:reviewDigest,wordedChanges:wordedChanges,widenedTargets:widenedTargets,agentMessage:agentMessage,
    shortSha:shortSha,clip:clip,kind:kind};
})(typeof window!=='undefined'?window:this);
