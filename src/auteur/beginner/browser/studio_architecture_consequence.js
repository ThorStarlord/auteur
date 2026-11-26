/* Consequences of a pending working revision, as the owner recorded them. Presentation only: every word here states what
   the owner read, and nothing here judges the proposal, accepts it, or applies it. Built with text nodes only.
   Version 2 analyses add recorded mechanisms, Working Book inheritance and hypothetical trajectories. Their labels and
   definitions come from the owner's vocabulary in the projection, so the page and the owner cannot drift apart. */
(function(global){'use strict';
  var STATUS={preserved:'Still represented',transformed:'Transformed',possibly_displaced:'May be displaced',introduced:'New concern'};
  var APPROACH={keep_baseline:'Keep the baseline concern',accept_proposal:'Accept the proposal as written',replace:'Replace',
    integrate:'Integrate',separate:'Separate',defer:'Defer',reframe:'Reframe',
    retain:'Retain (version 1 wording; its meaning is not fixed)'};
  var PROVENANCE={preserved:'Preserved in the proposal',transformed:'Transformed by the proposal',removed:'Removed by the proposal',
    introduced:'Introduced by the proposal',historical:'Historical: no longer current'};
  var ROUTE={changed_by_proposal:'the proposal changes it',referenced_by_working_book:'a Working Book references it',
    historical_in_revision:'an earlier applied version recorded it',adjacent_to:'one recorded link away from a seed'};
  var REACH={local:'Local to this change',conditional_inheritance:'May reach later Books through a conditional inheritance',
    long_horizon:'May reach a long-horizon development',not_established:'Not established by the record'};
  var INHERITANCE_KIND={recorded_inheritance:'Recorded inheritance',plausible_inheritance:'Plausible inheritance',
    proposed_inheritance:'Proposed inheritance',unknown_inheritance:'Unknown inheritance'};
  var STAGE={local_decision:'Local decision',mechanism_transformation:'Mechanism transformed',tension:'Tension',
    opportunity:'Opportunity',inheritance:'Possible inheritance',long_horizon:'Long-horizon development'};
  var BASIS={recorded:'Cites the record',interpreted:'Agent interpretation',speculative:'Speculative'};
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
    recorded_phase:'Narrative phase',working_book:'Working Book (title)',named_gap:'Missing or unreadable',
    mechanism:'Recorded mechanism',book_element:'Working Book element'
  };
  var FOCUS_FALLBACK='.consequence-error,.consequence-notice,.consequence-standing,.consequence-heading';
  var VOCAB={};

  function statusWords(status){return STATUS[status]||status;}
  function standingWords(standing){return STANDING[standing]||{label:'Standing not read.',tone:'note'};}
  function approachWords(approach){return APPROACH[approach]||approach;}
  function intentWords(intent){return INTENT[intent]||null;}
  function kindWords(kind){return KIND[kind]||kind;}
  function provenanceWords(p){return PROVENANCE[p]||p;}
  function reachWords(r){return REACH[r]||r;}
  function inheritanceWords(k){return INHERITANCE_KIND[k]||k;}
  function stageWords(s){return STAGE[s]||s;}
  function basisWords(b){return BASIS[b]||b;}
  // The owner's own definition of an approach, reach value, inheritance kind or provenance, read from the projection.
  function meaningOf(group,key){return ((VOCAB[group]||{})[key])||null;}

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
    // The status describes the question under the proposal. A Book decision's own record is not changed by it.
    var label=(item.kind==='book_decision'||item.kind==='baseline_wording'||item.kind==='recorded_history')?'question in proposal: ':'proposal: ';
    var status=item.proposal_status?' · '+label+item.proposal_status.replace(/_/g,' '):'';
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

  // A recorded mechanism: its provenance and what the record says are the owner's; the reading is the agent's interpretation.
  // The summary line is always shown; everything else opens on request, so a long analysis stays readable.
  function mechanismBlock(row,packet){
    var record=row.record||{};
    var map=evidenceMap(packet);
    var source=map[row.evidence]||{};
    var item=el('li','consequence-mechanism consequence-provenance-'+record.provenance);
    var details=el('details','consequence-mechanism-details');
    details.appendChild(el('summary',null,(record.record_kind||'record')+' '+(record.record_id||'')+' · '+provenanceWords(record.provenance)));
    var meaning=meaningOf('provenance',record.provenance);
    if(meaning)details.appendChild(el('p','consequence-note',meaning));
    if(source.provenance==='transformed'){
      details.appendChild(el('p','consequence-recorded','Recorded before: '+(source.baseline_text||'(none)')));
      details.appendChild(el('p','consequence-recorded','Recorded in the proposal: '+(source.proposed_text||'(none)')));
    }else{
      details.appendChild(el('p','consequence-recorded','Recorded: '+(source.proposed_text||source.baseline_text||'(none)')));
    }
    if((record.changed_fields||[]).length)details.appendChild(el('p','consequence-note','Changed fields: '+record.changed_fields.join(', ')+'.'));
    var routes=(source.routes||[]).map(function(route){
      var name=route.split(':')[0];
      return (ROUTE[name]||name)+(route.indexOf(':')>=0?' ('+route.split(':').slice(1).join(':')+')':'');
    });
    if(routes.length)details.appendChild(el('p','consequence-note','Why it is here: '+routes.join('; ')+'.'));
    details.appendChild(el('p','consequence-reading','Reading (agent interpretation): '+row.reading));
    if(row.transformation)details.appendChild(el('p','consequence-transformation','Change to its operation (agent interpretation): '+row.transformation));
    if(row.conditional_consequence)details.appendChild(el('p','consequence-conditional','If adopted (conditional, not established): '+row.conditional_consequence));
    if((row.counterevidence||[]).length){
      var counter=el('ul','consequence-counter');
      row.counterevidence.forEach(function(c){
        counter.appendChild(el('li',null,'Counterevidence: '+c.text));
      });
      details.appendChild(counter);
    }
    if((row.unresolved||[]).length){
      var open=el('ul','consequence-unresolved');
      row.unresolved.forEach(function(text){open.appendChild(el('li',null,'Unresolved: '+text));});
      details.appendChild(open);
    }
    details.appendChild(evidenceDisclosure(packet,[row.evidence],'Recorded item'));
    item.appendChild(details);
    return item;
  }

  function inheritanceBlock(link,packet){
    var item=el('li','consequence-inheritance consequence-inheritance-'+link.kind);
    item.appendChild(el('span','consequence-chip',inheritanceWords(link.kind)));
    item.appendChild(el('p','consequence-from','From: '+(link.from_view?link.from_view.label:link.from)));
    item.appendChild(el('p','consequence-to','To: '+(link.to_view?link.to_view.label:link.to)));
    var meaning=meaningOf('inheritance_kinds',link.kind);
    if(meaning)item.appendChild(el('p','consequence-note',meaning));
    item.appendChild(el('p','consequence-reading','Reading (agent interpretation): '+link.text));
    if((link.evidence||[]).length)item.appendChild(evidenceDisclosure(packet,link.evidence,'Evidence for this inheritance'));
    return item;
  }

  // A trajectory is a hypothetical developmental sequence. Its badge is shown on every one; no step reads as an event.
  function trajectoryBlock(trajectory,packet){
    var item=el('li','consequence-trajectory');
    item.appendChild(el('span','consequence-chip consequence-hypothetical','Hypothetical'));
    item.appendChild(el('p','consequence-trajectory-title',trajectory.title));
    var steps=el('ol','consequence-steps');
    (trajectory.steps||[]).forEach(function(step){
      var row=el('li','consequence-step consequence-basis-'+step.basis);
      row.appendChild(el('span','consequence-chip',stageWords(step.stage)+' · '+basisWords(step.basis)));
      row.appendChild(el('p',null,step.text));
      if((step.evidence||[]).length)row.appendChild(evidenceDisclosure(packet,step.evidence,'Evidence for this step'));
      steps.appendChild(row);
    });
    item.appendChild(steps);
    if((trajectory.assumptions||[]).length){
      var assumptions=el('ul','consequence-assumptions');
      trajectory.assumptions.forEach(function(text){assumptions.appendChild(el('li',null,'Assumes: '+text));});
      item.appendChild(assumptions);
    }
    var comparison=trajectory.comparison||{};
    var labels={creative_gain:'Creative gain',narrative_cost:'Narrative cost',contrivance_risk:'Risk of contrivance',
      future_commitment:'Future commitment',flexibility:'Flexibility for later development'};
    var rows=Object.keys(labels).filter(function(key){return comparison[key];});
    if(rows.length){
      var list=el('ul','consequence-comparison');
      rows.forEach(function(key){list.appendChild(el('li',null,labels[key]+': '+comparison[key]));});
      item.appendChild(list);
    }
    return item;
  }

  function alternativeBlock(alternative,packet,canInvestigate,onInvestigate,busy){
    var item=el('li','consequence-alternative');
    item.appendChild(el('span','consequence-chip',approachWords(alternative.approach)));
    item.appendChild(el('p','consequence-alternative-title',alternative.title));
    var meaning=alternative.approach_meaning||meaningOf('approaches',alternative.approach);
    if(meaning)item.appendChild(el('p','consequence-note',meaning));
    if(alternative.approach==='retain'&&VOCAB.retain_legacy)item.appendChild(el('p','consequence-note',VOCAB.retain_legacy));
    item.appendChild(el('p',null,alternative.summary));
    var names=el('ul','consequence-questions');
    alternative.questions.forEach(function(identifier){
      names.appendChild(el('li',null,'Question: '+questionWording(packet,identifier)));
    });
    item.appendChild(names);
    if((alternative.keeps_views||[]).length){
      item.appendChild(el('p','consequence-keeps','Keeps: '+alternative.keeps_views.map(function(v){return v.label;}).join('; ')+'.'));
    }
    if((alternative.mechanism_views||[]).length){
      item.appendChild(el('p','consequence-keeps','Mechanisms to examine: '+alternative.mechanism_views.map(function(v){return v.label;}).join('; ')+'.'));
    }
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
    var version2=result.schema==='studio-revision-consequence/2';
    root.appendChild(sectionHead('What the proposal does'));
    root.appendChild(el('p','consequence-reading','Reading (agent interpretation): '+result.reading));
    if(version2){
      root.appendChild(el('p','consequence-reach','Reach: '+reachWords(result.reach)+'. '+(result.reach_meaning||'')));
    }

    root.appendChild(sectionHead('Creative concerns'));
    if(result.concerns&&result.concerns.length){
      var concerns=el('ul','consequence-concerns');
      result.concerns.forEach(function(c){concerns.appendChild(concernBlock(c,packet));});
      root.appendChild(concerns);
    }else{
      root.appendChild(el('p','consequence-note',result.no_concern_reason||'No concern was judged consequential.'));
    }

    if(version2){
      if((result.mechanisms||[]).length){
        root.appendChild(sectionHead('Recorded mechanisms this reading rests on'));
        root.appendChild(el('p','consequence-note','Each is a record the Architecture holds, with its provenance against the baseline and the proposal. The reading beneath it is the agent’s interpretation.'));
        var mechs=el('ul','consequence-mechanisms');
        result.mechanisms.forEach(function(m){mechs.appendChild(mechanismBlock(m,packet));});
        root.appendChild(mechs);
      }
      if((result.inheritance||[]).length){
        root.appendChild(sectionHead('What later Books may inherit'));
        root.appendChild(el('p','consequence-note','Recorded inheritance is a Book’s own declaration. Plausible, proposed and unknown inheritance are not recorded facts.'));
        var inh=el('ul','consequence-inheritances');
        result.inheritance.forEach(function(link){inh.appendChild(inheritanceBlock(link,packet));});
        root.appendChild(inh);
      }
      if((result.trajectories||[]).length){
        root.appendChild(sectionHead('Possible developmental trajectories (hypothetical)'));
        root.appendChild(el('p','consequence-note','Hypothetical: none of these has happened or been accepted. Each step says whether it cites the record, is interpreted, or is speculative.'));
        var traj=el('ul','consequence-trajectories');
        result.trajectories.forEach(function(t){traj.appendChild(trajectoryBlock(t,packet));});
        root.appendChild(traj);
      }
    }else{
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
    if(version2){
      examined.appendChild(el('p',null,'Mechanisms offered: '+(limits.mechanisms_shown||0)+' of '+(limits.mechanisms_considered||0)+
        (limits.mechanisms_omitted?' (' +limits.mechanisms_omitted+' not shown)':'')+'. Working Book elements offered: '+
        (limits.book_elements_shown||0)+' of '+(limits.book_elements_considered||0)+(limits.book_elements_omitted?' (' +limits.book_elements_omitted+' not shown)':'')+'.'));
    }
    examined.appendChild(evidenceDisclosure(packet,(packet.evidence||[]).map(function(e){return e.id;}),'All evidence in this request'));
    root.appendChild(examined);
  }

  function renderPanel(root,projection,handlers,ui){
    root.replaceChildren();
    if(projection&&projection.vocabulary)VOCAB=projection.vocabulary;
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
    provenanceWords:provenanceWords,reachWords:reachWords,inheritanceWords:inheritanceWords,stageWords:stageWords,
    basisWords:basisWords,
    evidenceLine:evidenceLine,questionWording:questionWording,
    STATUS:STATUS,APPROACH:APPROACH,STANDING:STANDING,PROVENANCE:PROVENANCE,REACH:REACH,INHERITANCE_KIND:INHERITANCE_KIND
  };
})(window);
