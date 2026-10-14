/* Focused unfolding presentation and explicit CanvasStore commands; no agent execution on render. */
(function(global,document){
  'use strict';
  function create(bridge){
    var helper=global.AuteurStudioUnfolding;
    function $(id){return document.getElementById(id);}
    function dismissKey(){var s=bridge.state(),r=bridge.remote();
      return 'auteur:studio:unfold:dismissed:'+r.canvasId+':'+(s.architectureRequestSha||'none');}
    function dismissed(){
      try {var found=JSON.parse(global.localStorage.getItem(dismissKey())||'[]');
        return Array.isArray(found)?found.filter(x=>typeof x==='string').slice(-100):[];
      }catch(_){return [];}
    }
    function focusIsValid(s){
      if(!s.unfoldingFocus)return false;
      if(s.unfoldingFocus.kind==='candidate')return !!(s.architecture?.nodes||[]).find(x=>x.id===s.unfoldingFocus.id);
      return s.unfoldingFocus.kind==='working'&&s.items.some(x=>x.id===s.unfoldingFocus.id);
    }
    function current(){var s=bridge.state();if(!focusIsValid(s))return [];
      return helper.projectLocalSuggestions(s.architecture,s.architectureRequestSha,s.unfoldingFocus,
        s.items,dismissed(),global.innerWidth<=480?2:3,s.unfoldingOffset||0);
    }
    function updateWorkingCommand(action,command,{sourceSha=null,focusId=null,expectedCanvasRevision=null}={}){
      var s=bridge.state(),remote=bridge.remote(),canvasId=remote.canvasId;
      if(s.unfoldingSaving||!remote.ready||remote.failed)return Promise.resolve(bridge.status('Canvas unavailable; nothing was adopted.'));
      s.unfoldingSaving=true;
      return Promise.resolve(bridge.flush()).then(function(){
        if(remote.failed||remote.canvasId!==canvasId)throw Error('Working canvas changed or cannot save.');
        if(expectedCanvasRevision!==null && remote.revision!==expectedCanvasRevision)
          throw Error('Mentor advice is stale relative to the working canvas.');
        if(focusId && (!s.unfoldingFocus || s.unfoldingFocus.id!==focusId))
          throw Error('Working focus changed before save.');
        if(sourceSha && s.architectureRequestSha!==sourceSha)
          throw Error('Suggestion source became stale.');
        if(sourceSha && !current().some(x=>x.id===command.ghostId))throw Error('Suggestion is no longer available.');
        return bridge.post(action,command);
      }).then(function(doc){
        if(!doc||remote.canvasId!==canvasId)return false;
        s.unfoldingFocus={kind:'working',id:command.payload.item.id};
        s.unfoldingInspected=null;s.unfoldingOffset=0;
        bridge.applySaved(doc);
        bridge.status(action==='adopt-suggestion'?'Adopted into working architecture, not canon.':'Working idea saved, not canon.');
        return true;
      }).catch(function(e){bridge.status('Working change was not confirmed: '+e.message);return false;})
        .finally(function(){s.unfoldingSaving=false;render();});
    }
    function createAnchor(){
      var command;
      try {command=helper.buildManualAnchorCommand($('unfolding-role').value,$('unfolding-title').value,
        bridge.newItemId(),bridge.position());}
      catch(e){bridge.status('Invalid working idea: '+e.message);return Promise.resolve();}
      return updateWorkingCommand('create-item',command);
    }
    function editWorking(item,title,content){
      var s=bridge.state();
      var current=s.items.find(x=>x.id===item.id);
      if(!current || !s.unfoldingFocus || s.unfoldingFocus.id!==item.id ||
          typeof title!=='string'||!title.trim()||title.trim().length>120||
          typeof content!=='string'||content.length>20000){
        bridge.status('Working idea cannot be saved: title, length or focus is invalid.');return Promise.resolve();
      }
      var command={commandId:'edit-'+bridge.newItemId(),payload:{item:{...current,title:title.trim(),content:content}}};
      return updateWorkingCommand('update-item',command,{focusId:item.id});
    }
    function adopt(ghost){
      var s=bridge.state(),cmd;
      if(!s.unfoldingFocus||!ghost||ghost.requestSha!==s.architectureRequestSha){
        bridge.status('Suggestion source is stale. Nothing was adopted.');return Promise.resolve();}
      try {cmd=helper.buildAdoptionCommand(ghost,bridge.position());}
      catch(e){bridge.status('Invalid suggestion: '+e.message);return Promise.resolve();}
      cmd.ghostId=ghost.id;
      return updateWorkingCommand('adopt-suggestion',cmd,{sourceSha:ghost.requestSha,focusId:s.unfoldingFocus.id});
    }
    function keepMentorIdea(choice){
      var s=bridge.state(),remote=bridge.remote();
      if(!choice||!s.unfoldingFocus||s.unfoldingFocus.id!==choice.focusId||
          (s.architectureRequestSha||null)!==(choice.candidateSha||null)||
          !Number.isInteger(choice.canvasRevision)||choice.canvasRevision!==remote.revision||
          !/^[a-f0-9]{64}$/.test(choice.mentorRequestSha||'')||
          !/^(directions\/[a-z][a-z0-9_-]{0,39}|interpretation|question)$/.test(choice.sourceRef||'')||
          typeof choice.title!=='string'||!choice.title.trim()||choice.title.trim().length>120||
          typeof choice.content!=='string'||choice.content.length>20000){
        bridge.status('Mentor suggestion is invalid or stale; no working change saved.');
        return Promise.resolve(false);
      }
      var command;
      try{
        command=helper.buildManualAnchorCommand('other',choice.title,bridge.newItemId(),bridge.position());
        command.payload.item.content=choice.content;
        command.payload.item.proposal_origin={
          request_sha:choice.mentorRequestSha,source_ref:choice.sourceRef,
          source_kind:'host_agent_suggestion',focus_id:choice.focusId
        };
      }catch(e){bridge.status('Invalid working mentorship idea: '+e.message);return Promise.resolve(false);}
      return updateWorkingCommand('create-item',command,{
        focusId:choice.focusId,expectedCanvasRevision:choice.canvasRevision
      });
    }
    function positionLocalFocus(host,focus){
      // Align the local explanation with its actual transformed canvas node.
      host.style.left='';host.style.top='';host.style.right='';host.style.bottom='';
      if(global.innerWidth<=700 || !focus)return;
      var viewport=$('viewport'),bounds=viewport&&viewport.getBoundingClientRect&&viewport.getBoundingClientRect();
      if(!bounds || !bounds.width || !bounds.height)return;
      var nodes=document.querySelectorAll('#nodes .node');
      var chosen=Array.prototype.find.call(nodes,function(el){return el.dataset&&el.dataset.itemId===focus.id;});
      if(!chosen || !chosen.getBoundingClientRect)return;
      var point=chosen.getBoundingClientRect(),width=Math.min(275,Math.max(180,bounds.width-20));
      var roomRight=bounds.right-point.right,roomLeft=point.left-bounds.left;
      var x=roomRight>=width+16?point.right-bounds.left+12:
        roomLeft>=width+16?point.left-bounds.left-width-12:
        Math.max(8,Math.min(bounds.width-width-8,point.left-bounds.left));
      var y=Math.max(8,Math.min(bounds.height-230,point.top-bounds.top));
      host.style.left=Math.round(x)+'px';host.style.top=Math.round(y)+'px';
      host.style.right='auto';host.style.bottom='auto';
    }
    function mentorProjection(target,suggestions){
      if(!global.AuteurStudioMentorship||!target)return null;
      var s=bridge.state();
      var context=global.AuteurStudioMentorContext?
        global.AuteurStudioMentorContext.project(s,target,s.unfoldingFocus?.kind):null;
      return global.AuteurStudioMentorship.project({
        focus:target,focusKind:s.unfoldingFocus?.kind,candidate:s.architecture,
        requestSha:s.architectureRequestSha,suggestions:suggestions,authorContext:context
      });
    }
    function renderMentor(target,suggestions){
      var host=$('unfolding-mentor'),s=bridge.state(),projection=mentorProjection(target,suggestions);
      if(!host)return;
      host.hidden=!projection;host.replaceChildren();
      if(!projection)return;
      var key=s.unfoldingFocus.kind+':'+projection.focusId+':'+projection.sourceSha;
      if(s.mentorFocusKey!==key){
        s.mentorFocusKey=key;s.mentorMode=projection.recommended;
      }
      var mode=s.mentorMode||'explore';
      function add(tag,value,parent){
        var el=document.createElement(tag);el.textContent=value;(parent||host).appendChild(el);return el;
      }
      var tabs=add('nav','');tabs.className='mentor-tabs';tabs.setAttribute('aria-label','Contextual narrative mentorship');
      ['learn','explore','question','challenge'].forEach(function(name,index){
        var b=add('button',name[0].toUpperCase()+name.slice(1),tabs);
        b.type='button';b.setAttribute('aria-pressed',String(mode===name));
        b.addEventListener('click',function(){
          s.mentorMode=name;renderMentor(target,suggestions); // Do not rebuild the working editor.
          var active=$('unfolding-mentor').children[0].children[index];
          if(active && typeof active.focus==='function')active.focus();
        });
      });
      var body=add('div','');body.className='mentor-body';
      if(mode==='learn'){
        add('strong','Why this matters',body);
        add('p',projection.definition,body);
        if(projection.inStory)add('p','In this story: '+projection.inStory,body);
        var context=projection.authorContext;
        if(context){
          var details=add('details','',body);
          var summary=add('summary','What Auteur knows and does not know',details);
          if(context.storyVision.text)add('p','Author working Story Vision: '+context.storyVision.text,details);
          else add('p','No author Story Vision supplied yet.',details);
          if(context.declaredEdges.length)add('p',context.declaredEdges.length+
            ' linked candidate relation(s) available. These are proposals, not accepted facts.',details);
          add('small',context.acceptedIdentity.note,details);
          add('small',context.genreEvidence.note,details);
        }
        add('small',projection.evidenceNote,body);
        var perspective={genre:'genres',trope:'tropes',structure:'structure',engine:'structure',
          emotion:'emotions',reader_experience:'emotions'}[projection.role];
        if(perspective){
          var learnMore=add('button','See related architecture perspective',body);
          learnMore.type='button';learnMore.addEventListener('click',function(){
            var focused=s.unfoldingFocus?.kind==='working'?
              s.items.find(x=>x.id===s.unfoldingFocus.id):null;
            if(focused){
              var editor=$('unfolding-author-edit');
              var title=Array.prototype.find.call(editor.children,x=>x.id==='unfolding-edit-title');
              var detail=Array.prototype.find.call(editor.children,x=>x.id==='unfolding-edit-content');
              if((title&&title.value!==focused.title)||(detail&&detail.value!==focused.content)){
                bridge.status('Save your working-idea edits before opening another perspective.');return;
              }
            }
            var route=document.querySelector('[data-architecture-facet="'+perspective+'"]');
            if(route)route.click();
          });
        }
      }else if(mode==='explore'){
        add('strong','Different directions',body);
        add('p',projection.options.length?
          'Explore the source-linked possibilities below. They are proposals, not story commitments.':
          'No attributed local alternatives. Ask the host agent to develop genuinely different possibilities.',body);
        projection.options.forEach(function(opt){
          add('small',opt.title+' · '+opt.dimension.replace(':',' / '),body);
        });
        if(projection.options.length<2){
          var explore=add('button','Develop divergent options with coding agent',body);
          explore.type='button';explore.addEventListener('click',function(){requestMentor(projection,'explore');});
        }
      }else if(mode==='question'){
        add('strong','A question for your story',body);
        add('p',projection.question,body);
        var keep=add('button','Keep question as an editable working idea',body);
        keep.type='button';keep.disabled=s.unfoldingSaving;
        keep.addEventListener('click',function(){return keepMentorQuestion(projection);});
        var follow=add('button','Develop follow-up with coding agent',body);
        follow.type='button';follow.addEventListener('click',function(){requestMentor(projection,'question');});
        var resume=add('button','Resume prior mentor exchange',body);
        resume.type='button';resume.addEventListener('click',function(){
          if(bridge.resumeMentor)bridge.resumeMentor(projection);
        });
      }else{
        add('strong','An assumption worth examining',body);
        add('p',projection.challenge,body);
        add('small',projection.challengeSourceRef?
          'Source: proposed '+projection.challengeSourceRef+'. Not an accepted contradiction.':
          'Conditional creative hypothesis, not evidence of a defect.',body);
        var develop=add('button','Explore this tension with coding agent',body);
        develop.type='button';develop.addEventListener('click',function(){requestMentor(projection,'challenge');});
      }
      var visible=mode==='explore';
      $('unfolding-ghosts').hidden=!visible;
      $('unfolding-more').hidden=!visible;
      $('unfolding-explanation').hidden=!visible||!suggestions.some(x=>x.id===s.unfoldingInspected);
    }
    function stillFocused(p){
      var s=bridge.state();
      return !!focusIsValid(s)&&s.unfoldingFocus.id===p.focusId&&
        (s.architectureRequestSha||null)===p.sourceSha;
    }
    function requestMentor(p,purpose){
      if(!stillFocused(p))return bridge.status('Mentor source changed. Select this idea again.');
      if(!bridge.prepareMentor)return bridge.status('Mentor handoff unavailable; no architecture was rewritten.');
      return bridge.prepareMentor(p,purpose||'explore');
    }
    function keepMentorQuestion(p){
      if(!stillFocused(p))return Promise.resolve(bridge.status('Question source changed; nothing saved.'));
      var command;
      try {
        command=helper.buildManualAnchorCommand('other',
          ('Question about '+p.title).slice(0,120),bridge.newItemId(),bridge.position());
        command.payload.item.kind='question';
        command.payload.item.content=p.question;
      }catch(e){return Promise.resolve(bridge.status('Cannot keep this question: '+e.message));}
      return updateWorkingCommand('create-item',command,{focusId:p.focusId});
    }
    function render(){
      var s=bridge.state(),start=$('unfolding-start'),host=$('unfolding-local');
      var ghosts=$('unfolding-ghosts'),explain=$('unfolding-explanation'),edit=$('unfolding-author-edit');
      edit.hidden=true;edit.replaceChildren();
      var active=s.workspace==='architecture'&&s.view==='architecture'&&s.architectureFacet==='overview';
      start.hidden=!active;host.hidden=true;explain.hidden=true;
      if(!active)return;
      if(!focusIsValid(s)){start.hidden=false;return;}
      start.hidden=true;host.hidden=false;positionLocalFocus(host,s.unfoldingFocus);
      ghosts.replaceChildren();explain.replaceChildren();
      var target=s.unfoldingFocus.kind==='candidate'?(s.architecture.nodes||[]).find(n=>n.id===s.unfoldingFocus.id):
        s.items.find(n=>n.id===s.unfoldingFocus.id);
      $('unfolding-evidence-status').textContent=target?.title||'Selected working idea';
      if(s.unfoldingFocus.kind==='working' && target){
        edit.hidden=false;
        var h=document.createElement('strong');h.textContent='Edit your working idea · Not canon';
        var name=document.createElement('input');name.id='unfolding-edit-title';
        name.setAttribute('aria-label','Working idea title');name.maxLength=120;name.value=target.title;
        var content=document.createElement('textarea');content.id='unfolding-edit-content';
        content.setAttribute('aria-label','Working idea details');content.maxLength=20000;content.value=target.content||'';
        var save=document.createElement('button');save.type='button';save.textContent='Save working idea';
        save.disabled=s.unfoldingSaving;
        save.addEventListener('click',function(){return editWorking(target,name.value,content.value);});
        edit.append(h,name,content,save);
      }
      var all=current();
      var mentor=mentorProjection(target,all);
      if(mentor){var allowed=new Set(mentor.options.map(x=>x.id));all=all.filter(x=>allowed.has(x.id));}
      if(!all.length){var p=document.createElement('p');p.className='muted';
        p.textContent='No declared nearby proposals for this focus. Choose another concept or explicitly develop more possibilities.';
        ghosts.appendChild(p);
      }
      all.forEach(function(ghost){
        var b=document.createElement('button');b.type='button';b.className='unfolding-ghost';
        b.setAttribute('aria-pressed',String(s.unfoldingInspected===ghost.id));
        b.textContent=ghost.title+' · Provisional';
        var provenance=document.createElement('small');provenance.textContent=ghost.relationshipVerb+' · Source-backed proposal, not canon';
        b.appendChild(provenance);
        b.addEventListener('click',function(){
          s.unfoldingInspected=ghost.id;render();
          var current=Array.prototype.find.call($('unfolding-ghosts').children,function(e){
            return e.getAttribute && e.getAttribute('aria-pressed')==='true';
          });
          if(current)current.focus();
        });
        ghosts.appendChild(b);
      });
      var selected=all.find(g=>g.id===s.unfoldingInspected);
      if(selected){
        explain.hidden=false;
        function line(tag,body){var node=document.createElement(tag);node.textContent=body;explain.appendChild(node);return node;}
        line('strong',selected.title+' · proposed '+selected.targetRole);
        line('p','Proposed relation: '+selected.relationshipVerb+' · '+(selected.description||'No additional mechanism established.'));
        line('p','Source: '+selected.sourceRef+' · Request '+selected.requestSha.slice(0,12)+' · Noncanonical.');
        var save=line('button','Adopt into working architecture');save.type='button';save.disabled=s.unfoldingSaving;
        save.addEventListener('click',()=>adopt(selected));
        var hide=line('button','Dismiss suggestion');hide.type='button';
        hide.addEventListener('click',function(){
          var list=dismissed();if(!list.includes(selected.id))list.push(selected.id);
          try{global.localStorage.setItem(dismissKey(),JSON.stringify(list.slice(-100)));}
          catch(e){bridge.status('Dismissal could not be saved: '+e.message);}
          s.unfoldingInspected=null;s.unfoldingOffset=0;render();
        });
      }
      var next=helper.projectLocalSuggestions(s.architecture,s.architectureRequestSha,s.unfoldingFocus,
        s.items,dismissed(),global.innerWidth<=480?2:3,(s.unfoldingOffset||0)+(global.innerWidth<=480?2:3));
      $('unfolding-more').textContent=next.length?'Explore further nearby options':'Develop more possibilities (host-agent handoff)';
      renderMentor(target,all);
    }
    function more(){
      var s=bridge.state();if(!focusIsValid(s))return;
      var size=global.innerWidth<=480?2:3,next=helper.projectLocalSuggestions(s.architecture,s.architectureRequestSha,
        s.unfoldingFocus,s.items,dismissed(),size,(s.unfoldingOffset||0)+size);
      if(next.length){s.unfoldingOffset=(s.unfoldingOffset||0)+size;s.unfoldingInspected=null;render();return;}
      var focus=s.unfoldingFocus.kind==='candidate'?(s.architecture.nodes||[]).find(x=>x.id===s.unfoldingFocus.id):
        s.items.find(x=>x.id===s.unfoldingFocus.id);
      if(!focus)return;
      var projection=mentorProjection(focus,current());
      if(projection)requestMentor(projection);
    }
    return {render:render,create:createAnchor,adopt:adopt,more:more,keepMentorIdea:keepMentorIdea};
  }
  global.AuteurStudioUnfoldingController={create:create};
})(window,document);
