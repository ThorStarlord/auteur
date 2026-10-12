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
    function updateWorkingCommand(action,command,{sourceSha=null,focusId=null}={}){
      var s=bridge.state(),remote=bridge.remote(),canvasId=remote.canvasId;
      if(s.unfoldingSaving||!remote.ready||remote.failed)return Promise.resolve(bridge.status('Canvas unavailable; nothing was adopted.'));
      s.unfoldingSaving=true;
      return Promise.resolve(bridge.flush()).then(function(){
        if(remote.failed||remote.canvasId!==canvasId)throw Error('Working canvas changed or cannot save.');
        if(focusId && (!s.unfoldingFocus || s.unfoldingFocus.id!==focusId))
          throw Error('Working focus changed before save.');
        if(sourceSha && s.architectureRequestSha!==sourceSha)
          throw Error('Suggestion source became stale.');
        if(sourceSha && !current().some(x=>x.id===command.ghostId))throw Error('Suggestion is no longer available.');
        return bridge.post(action,command);
      }).then(function(doc){
        if(!doc||remote.canvasId!==canvasId)return;
        s.unfoldingFocus={kind:'working',id:command.payload.item.id};
        s.unfoldingInspected=null;s.unfoldingOffset=0;
        bridge.applySaved(doc);
        bridge.status(action==='adopt-suggestion'?'Adopted into working architecture, not canon.':'Working idea saved, not canon.');
      }).catch(function(e){bridge.status('Working change was not confirmed: '+e.message);})
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
        b.addEventListener('click',function(){s.unfoldingInspected=ghost.id;render();});
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
    }
    function more(){
      var s=bridge.state();if(!focusIsValid(s))return;
      var size=global.innerWidth<=480?2:3,next=helper.projectLocalSuggestions(s.architecture,s.architectureRequestSha,
        s.unfoldingFocus,s.items,dismissed(),size,(s.unfoldingOffset||0)+size);
      if(next.length){s.unfoldingOffset=(s.unfoldingOffset||0)+size;s.unfoldingInspected=null;render();return;}
      var focus=s.unfoldingFocus.kind==='candidate'?(s.architecture.nodes||[]).find(x=>x.id===s.unfoldingFocus.id):
        s.items.find(x=>x.id===s.unfoldingFocus.id);
      if(!focus)return;
      var instruction='Develop up to three additional NONCANONICAL narrative possibilities related to '+focus.title+
        '. Current source request SHA: '+(s.architectureRequestSha||'none')+
        '. Explain proposed relationships. Preserve author working notes. Do not accept story canon.';
      bridge.prepare(instruction.slice(0,4000));
    }
    return {render:render,create:createAnchor,adopt:adopt,more:more};
  }
  global.AuteurStudioUnfoldingController={create:create};
})(window,document);
