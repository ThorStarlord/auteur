/* Consequences of a pending working revision, as the owner recorded them. Presentation only: every word here states what
   the owner read, and nothing here judges the proposal, accepts it, or applies it. Built with text nodes only. */
(function(global){'use strict';
  var STATUS={preserved:'Still represented',transformed:'Transformed',possibly_displaced:'May be displaced',introduced:'New concern'};
  var APPROACH={replace:'Replace',integrate:'Integrate',separate:'Separate',retain:'Retain',defer:'Defer',reframe:'Reframe'};
  var INTENT={
    instruction_names_it:'Your instruction names this concern.',
    selected_alternative_names_it:'The alternative you chose names this concern.',
    not_established:'Whether this was intended is not established by the record.'
  };
  var STANDING={
    current:{label:'About this proposal, not yet applied.',tone:'ok'},
    applied:{label:'About a revision already applied. The Architecture now holds it; this is its historical reading.',tone:'note'},
    superseded:{label:'About an earlier proposal. It is not the proposal on screen.',tone:'warn'},
    stale_context:{label:'The working context changed after this analysis was asked. It is kept as earlier evidence only.',tone:'warn'}
  };
  var KIND={
    instruction:'Your instruction',selected_alternative:'Alternative you chose',discovery_origin:'Discovered possibility',
    author_vision:'Story Vision',accepted_constraint:'Accepted constraint',accepted_not_this:'Accepted “not this”',
    baseline_wording:'Earlier wording (applied)',proposed_wording:'Proposed wording',removed:'Question the proposal removes',
    recorded_history:'Recorded history',book_decision:'Working Book decision',proposed_component:'Changed component',
    recorded_phase:'Narrative phase',working_book:'Working Book (title)',named_gap:'Missing or unreadable'
  };
  var FOCUS_FALLBACK='.consequence-error,.consequence-notice,.consequence-standing,.consequence-heading';

  function statusWords(status){return STATUS[status]||status;}
  function standingWords(standing){return STANDING[standing]||{label:'Standing not read.',tone:'note'};}
  function approachWords(approach){return APPROACH[approach]||approach;}
  function intentWords(intent){return INTENT[intent]||null;}
  function kindWords(kind){return KIND[kind]||kind;}

  function evidenceMap(packet){var map={};((packet&&packet.evidence)||[]).forEach(function(e){map[e.id]=e;});return map;}

  // A question as the analysis examined it: the proposed wording when the proposal has one, else the earlier wording.
  function questionWording(packet,identifier){
    var row=((packet&&packet.examined_questions)||[]).find(function(r){return r.id===identifier;});
    var map=evidenceMap(packet);
    var ids=row?(row.proposed_evidence||[]).concat(row.baseline_evidence||[]):[];
    var item=ids.map(function(id){return map[id];}).find(function(e){
      return e&&(e.kind==='proposed_wording'||e.kind==='baseline_wording');
    });
    return item?item.text:identifier;
  }

  // One fact the owner recorded, with its identifier. The text is the owner's; the kind names what sort of fact it is.
  function evidenceLine(item){
    var tail=item.book_number!=null?' (Book '+item.book_number+')':'';
    var status=item.proposal_status?' · proposal: '+item.proposal_status.replace(/_/g,' '):'';
    return item.id+' · '+kindWords(item.kind)+tail+status+' — '+(item.text||'');
  }

  function el(tag,className,text){
    var node=document.createElement(tag);
    if(className)node.className=className;
    if(text!=null)node.textContent=text;
    return node;
  }

  function sectionHead(title){return el('h4','consequence-heading',title);}

  function evidenceDisclosure(packet,ids,label){
    var map=evidenceMap(packet);
    var details=el('details','consequence-evidence');
    details.appendChild(el('summary',null,label||'Evidence this rests on'));
    var list=el('ul',null);
    (ids||[]).forEach(function(id){
      var item=map[id];
      list.appendChild(el('li',null,item?evidenceLine(item):id+' (not in this request)'));
    });
    details.appendChild(list);
    return details;
  }

  function standingLine(standing){
    var words=standingWords(standing);
    return el('p','consequence-standing consequence-tone-'+words.tone,words.label);
  }

  function concernBlock(concern,packet){
    var item=el('li','consequence-concern consequence-status-'+concern.status);
    item.appendChild(el('p','consequence-concern-title',concern.title));
    item.appendChild(el('span','consequence-chip',statusWords(concern.status)));
    if(concern.earlier)item.appendChild(el('p','consequence-earlier','Earlier: '+concern.earlier));
    if(concern.proposed)item.appendChild(el('p','consequence-proposed','Proposed: '+concern.proposed));
    item.appendChild(el('p','consequence-reading','Reading (agent interpretation): '+concern.reading));
    if(intentWords(concern.intent))item.appendChild(el('p','consequence-intent',intentWords(concern.intent)));
    if(concern.competing_reading)item.appendChild(el('p','consequence-competing','Another reading: '+concern.competing_reading));
    if((concern.counterevidence||[]).length){
      var counter=el('ul','consequence-counter');
      concern.counterevidence.forEach(function(text){counter.appendChild(el('li',null,'Counterevidence: '+text));});
      item.appendChild(counter);
    }
    item.appendChild(evidenceDisclosure(packet,concern.evidence,'Evidence for “'+concern.title+'”'));
    return item;
  }

  function prospectBlock(list,items,packet){
    items.forEach(function(entry){
      var row=el('li','consequence-prospect consequence-prospect-'+entry.kind);
      row.appendChild(el('p',null,entry.text));
      row.appendChild(el('span','consequence-chip',entry.kind==='recorded_relationship'
        ?'Recorded relationship':'Possibility to examine'));
      if((entry.evidence||[]).length)row.appendChild(evidenceDisclosure(packet,entry.evidence,'Evidence for this'));
      list.appendChild(row);
    });
  }

  function alternativeBlock(alternative,packet,canInvestigate,onInvestigate,busy){
    var item=el('li','consequence-alternative');
    item.appendChild(el('span','consequence-chip',approachWords(alternative.approach)));
    item.appendChild(el('p','consequence-alternative-title',alternative.title));
    item.appendChild(el('p',null,alternative.summary));
    var names=el('ul','consequence-questions');
    alternative.questions.forEach(function(identifier){
      names.appendChild(el('li',null,'Question: '+questionWording(packet,identifier)));
    });
    item.appendChild(names);
    item.appendChild(el('p','consequence-gains','Gains: '+alternative.gains));
    item.appendChild(el('p','consequence-costs','Costs: '+alternative.costs));
    if(canInvestigate){
      var button=el('button','consequence-investigate','Investigate this alternative');
      button.type='button';
      button.setAttribute('aria-label','Investigate this alternative: '+alternative.title);
      button.setAttribute('data-key','consequence-investigate:'+alternative.id);
      if(busy)button.setAttribute('aria-disabled','true');
      button.addEventListener('click',function(){onInvestigate(alternative);});
      item.appendChild(button);
    }
    return item;
  }

  function resultBlocks(root,result,standing,projection,handlers,busy){
    var packet=result.evidence||{};
    root.appendChild(sectionHead('What the proposal does'));
    root.appendChild(el('p','consequence-reading','Reading (agent interpretation): '+result.reading));

    root.appendChild(sectionHead('Creative concerns'));
    if(result.concerns&&result.concerns.length){
      var concerns=el('ul','consequence-concerns');
      result.concerns.forEach(function(c){concerns.appendChild(concernBlock(c,packet));});
      root.appendChild(concerns);
    }else{
      root.appendChild(el('p','consequence-note',result.no_concern_reason||'No concern was judged consequential.'));
    }

    var recorded=(result.prospective||[]).filter(function(p){return p.kind==='recorded_relationship';});
    var possible=(result.prospective||[]).filter(function(p){return p.kind!=='recorded_relationship';});
    if(recorded.length){
      root.appendChild(sectionHead('Recorded relationships (what the Books record)'));
      var r=el('ul','consequence-prospects');prospectBlock(r,recorded,packet);root.appendChild(r);
    }
    if(possible.length){
      root.appendChild(sectionHead('Possibilities for later Books (proposed, not recorded)'));
      var p=el('ul','consequence-prospects');prospectBlock(p,possible,packet);root.appendChild(p);
    }

    // Only the latest analysis of the proposal on screen may be investigated from here. The owner refuses the rest.
    var canInvestigate=standing==='current';
    if(result.alternatives&&result.alternatives.length){
      root.appendChild(sectionHead('Developable alternatives'));
      root.appendChild(el('p','consequence-note','Each alternative is one way to develop the opportunity. Investigate prepares the request for your coding agent with this alternative’s questions and the analysis’s suggested wording, which the creative panel shows as the suggestion. Nothing is sent to a provider, and the Architecture is unchanged.'));
      var alts=el('ul','consequence-alternatives');
      result.alternatives.forEach(function(a){
        alts.appendChild(alternativeBlock(a,packet,canInvestigate,function(alt){
          handlers.investigate(alt,projection.request_sha256);
        },busy));
      });
      root.appendChild(alts);
    }

    if(result.not_established&&result.not_established.length){
      root.appendChild(sectionHead('Not established by the record'));
      var ne=el('ul','consequence-not-established');
      result.not_established.forEach(function(text){ne.appendChild(el('li',null,text));});
      root.appendChild(ne);
    }

    var examined=el('details','consequence-examined');
    examined.appendChild(el('summary',null,'What this analysis examined'));
    var coverage=packet.coverage||{};
    examined.appendChild(el('p',null,'Working Books whose decisions were read: '+((coverage.books_with_decisions_on_examined_questions||[]).join(', ')||'none')+'.'));
    examined.appendChild(el('p',null,'Working Books listed by title only: '+((coverage.books_listed_by_title_only||[]).join(', ')||'none')+'. '+(coverage.note||'')));
    var limits=packet.limits||{};
    if(limits.questions_omitted)examined.appendChild(el('p',null,limits.questions_omitted+' further question(s) the proposal touches were not examined.'));
    examined.appendChild(evidenceDisclosure(packet,(packet.evidence||[]).map(function(e){return e.id;}),'All evidence in this request'));
    root.appendChild(examined);
  }

  function renderPanel(root,projection,handlers,ui){
    root.replaceChildren();
    if(ui.notice)root.appendChild(el('p','consequence-notice',ui.notice));
    if(ui.error)root.appendChild(el('p','consequence-error',ui.error));
    if(ui.loadError){
      root.appendChild(el('p','consequence-error','The analysis could not be read: '+ui.loadError));
      var retry=el('button','consequence-retry','Try reading the analysis again');
      retry.type='button';retry.setAttribute('data-key','consequence-retry');
      if(ui.busy)retry.setAttribute('aria-disabled','true');
      retry.addEventListener('click',function(){handlers.retry();});
      root.appendChild(retry);
      return;
    }
    if(!projection){root.appendChild(el('p','consequence-note','Reading the analysis…'));return;}

    var standing=projection.standing;
    var result=projection.result;
    var current=standing==='current';
    var pending=!!projection.pending_revision_request_sha256;
    var actions=el('div','consequence-actions');

    if(result){
      root.appendChild(standingLine(standing));
      resultBlocks(root,result,standing,projection,handlers,ui.busy);
    }

    if(projection.request&&current){
      // An analysis of the proposal on screen is awaiting the coding agent's answer.
      root.appendChild(standingLine('current'));
      root.appendChild(el('p','consequence-note','Copy this request to your coding agent. It asks about the proposal on screen only; nothing is sent to a provider.'));
      var box=el('textarea','consequence-request');
      box.readOnly=true;box.rows=6;box.value=JSON.stringify(projection.request,null,2);
      box.setAttribute('aria-label','Consequence analysis request for your coding agent');
      root.appendChild(box);
      var label=el('label','consequence-response-label','Paste the coding agent’s response (HostAgentResponse JSON)');
      label.htmlFor='consequence-response';
      root.appendChild(label);
      // The unsent response is the author's text: it survives every redraw and refusal until an analysis is accepted.
      var response=el('textarea','consequence-response');
      response.id='consequence-response';response.rows=4;response.value=ui.draft||'';
      response.setAttribute('data-key','consequence-response');
      response.addEventListener('input',function(){ui.draft=response.value;});
      root.appendChild(response);
      var submit=el('button','consequence-submit','Submit the analysis response');
      submit.type='button';submit.setAttribute('data-key','consequence-submit');
      if(ui.busy)submit.setAttribute('aria-disabled','true');
      submit.addEventListener('click',function(){handlers.submit();});
      actions.appendChild(submit);
    }else if(pending&&!(result&&current)){
      // The proposal on screen has no analysis of its own yet (none, or only an earlier one). Asking is always the author's choice.
      var prepare=el('button','consequence-prepare',result?'Ask about the proposal on screen':'Ask about consequences');
      prepare.type='button';prepare.setAttribute('data-key','consequence-prepare');
      if(ui.busy)prepare.setAttribute('aria-disabled','true');
      prepare.addEventListener('click',function(){handlers.prepare();});
      actions.appendChild(prepare);
      root.appendChild(el('p','consequence-note','Asking changes nothing: it reads this proposal, its baseline and the recorded history, and writes only its own record. Apply is not affected by it.'));
    }

    if(result&&current){
      var again=el('button','consequence-ask-again','Ask again about this proposal');
      again.type='button';again.setAttribute('data-key','consequence-ask-again');
      if(ui.busy)again.setAttribute('aria-disabled','true');
      again.addEventListener('click',function(){handlers.prepare();});
      actions.appendChild(again);
    }
    if(actions.childNodes.length)root.appendChild(actions);

    if(projection.history&&projection.history.length){
      var past=el('details','consequence-history');
      past.appendChild(el('summary',null,'Earlier analyses on this canvas ('+projection.history.length+')'));
      var list=el('ul',null);
      projection.history.forEach(function(row){
        list.appendChild(el('li',null,standingWords(row.standing).label+' '+row.concern_count+' concern(s).'));
      });
      past.appendChild(list);
      root.appendChild(past);
    }
  }

  function defaultFetch(url,body,method){
    var init={method:method||'GET',headers:{'Content-Type':'application/json'}};
    if(body!=null&&method!=='GET')init.body=JSON.stringify(body);
    return fetch(url,init).then(function(response){
      return response.json().then(function(data){
        if(!response.ok)throw Error(data.error||'The analysis request was refused.');
        return data;
      });
    });
  }

  // The panel: loads the owner's projection, asks and submits through the owner, and hands investigations to the caller.
  // Every result is tied to the canvas it was asked on: a result that arrives after the canvas changed is dropped.
  // options.live.status and options.live.alert are persistent live regions outside the panel, so announcements are read.
  function createConsequencePanel(options){
    var root=options.root,canvasId=options.canvasId,onInvestigate=options.onInvestigate;
    var live=options.live||{};
    var fetchJson=options.fetchJson||defaultFetch;
    var base=function(){return '/api/beginner/studio/canvases/'+encodeURIComponent(canvasId())+'/architecture/consequence';};
    var projection=null,ui={notice:null,error:null,loadError:null,busy:false,draft:''},generation=0;

    function say(text){if(live.status)live.status.textContent=text||'';}
    function alertUser(text){if(live.alert)live.alert.textContent=text||'';}
    // Keyboard focus stays on the control the author used when it survives; otherwise it moves to the new message or heading.
    function keyInside(){var a=document.activeElement;return a&&root.contains(a)&&a.getAttribute?(a.getAttribute('data-key')||'#inside'):null;}
    function draw(keep){
      renderPanel(root,projection,handlers,ui);
      if(keep==null)return;
      var target=keep!=='#inside'?root.querySelector('[data-key="'+keep.replace(/"/g,'')+'"]'):null;
      if(!target||target.getAttribute('aria-disabled')==='true')target=root.querySelector(FOCUS_FALLBACK)||root.querySelector('h4');
      if(!target)return;
      if(!target.hasAttribute('tabindex')&&!/^(BUTTON|TEXTAREA|INPUT|SUMMARY|A)$/.test(target.tagName))target.setAttribute('tabindex','-1');
      target.focus();
    }
    function begin(){ui.busy=true;ui.error=null;ui.loadError=null;ui.notice=null;root.setAttribute('aria-busy','true');}
    function end(){ui.busy=false;root.removeAttribute('aria-busy');}
    // After a refused action the owner's current state is read again, so a label never describes a request that no longer applies.
    function reloadAfterError(message,keep,canvas){
      var token=++generation;
      return fetchJson(base(),null,'GET').then(function(next){
        if(token!==generation||canvas!==canvasId())return null;
        projection=next;ui.error=message;alertUser(message);draw(keep);return null;
      },function(){
        if(token!==generation||canvas!==canvasId())return null;
        ui.error=message;alertUser(message);draw(keep);return null;
      });
    }
    function run(promise,doneText){
      var token=++generation,canvas=canvasId(),keep=keyInside();
      begin();draw(keep);
      return promise.then(function(next){
        if(token!==generation||canvas!==canvasId())return next;
        end();projection=next;if(next&&next.result)ui.draft='';
        say(doneText);draw(keep);return next;
      },function(error){
        if(token!==generation||canvas!==canvasId())return null;
        end();
        return reloadAfterError((error&&error.message)||'The analysis could not be completed.',keep,canvas);
      });
    }
    var handlers={
      prepare:function(){if(ui.busy)return Promise.resolve(null);return run(fetchJson(base()+'/prepare',{},'POST'),'Analysis requested.');},
      retry:function(){if(ui.busy)return Promise.resolve(null);return handlers.load();},
      load:function(){
        var canvas=canvasId(),keep=keyInside();
        return fetchJson(base(),null,'GET').then(function(next){
          if(canvas!==canvasId())return next;
          projection=next;ui.loadError=null;draw(keep);return next;
        },function(error){
          if(canvas!==canvasId())return null;
          ui.loadError=(error&&error.message)||'The analysis could not be read.';draw(keep);return null;
        });
      },
      submit:function(){
        if(ui.busy)return Promise.resolve(null);
        var payload;
        try{payload=JSON.parse(ui.draft||'');}
        catch(error){
          ui.error='The response must be valid HostAgentResponse JSON.';alertUser(ui.error);draw(keyInside());
          return Promise.resolve(null);
        }
        return run(fetchJson(base()+'/host-agent-response',payload,'POST'),'Analysis accepted.');
      },
      investigate:function(alternative,requestSha){
        if(ui.busy)return Promise.resolve(null);
        var canvas=canvasId(),keep=keyInside();
        begin();draw(keep);
        return Promise.resolve().then(function(){return onInvestigate(alternative,requestSha);}).then(function(){
          if(canvas!==canvasId())return null;
          end();ui.notice='Investigation prepared in the creative panel. Nothing in the Architecture has changed.';
          say(ui.notice);draw(keep);return null;
        },function(error){
          if(canvas!==canvasId())return null;
          end();ui.error=(error&&error.message)||'The investigation could not be prepared.';alertUser(ui.error);draw(keep);
          return null;
        });
      }
    };
    return{
      load:handlers.load,
      reset:function(){
        generation+=1;projection=null;ui={notice:null,error:null,loadError:null,busy:false,draft:''};
        root.replaceChildren();say('');alertUser('');
      },
      show:function(){return projection;}
    };
  }

  global.AuteurStudioConsequence={
    createConsequencePanel:createConsequencePanel,
    statusWords:statusWords,standingWords:standingWords,approachWords:approachWords,intentWords:intentWords,
    evidenceLine:evidenceLine,questionWording:questionWording,
    STATUS:STATUS,APPROACH:APPROACH,STANDING:STANDING
  };
})(window);
