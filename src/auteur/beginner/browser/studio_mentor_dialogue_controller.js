/* Explicit host-agent conversation in the existing Focused Unfolding surface.
 * Passive render never issues HTTP requests or author-story writes. */
(function(global,document){
  'use strict';
  function create(bridge){
    function $(id){return document.getElementById(id);}
    var active=null,drafts=Object.create(null),packet=null,busy=false,notice='',chosen=null;
    function current(){
      var state=bridge.state(),focus=state.unfoldingFocus;
      return state.workspace==='architecture'&&state.view==='architecture'&&
        state.architectureFacet==='overview'&&state.fullArchitectureDisplay!=='full'&&
        state.fullArchitectureDisplay!=='review'&&!!focus;
    }
    function key(info){return info.canvasId+':'+info.kind+':'+info.id+':'+(info.sourceSha||'none');}
    function sourceShaOf(state){
      return state.architectureSourceStatus&&state.architectureSourceStatus!=='ready'
        ?null:(state.architectureRequestSha||null);
    }
    function stillCurrent(){
      if(!active||!current())return false;
      var state=bridge.state(),remote=bridge.remote(),focus=state.unfoldingFocus;
      return remote.canvasId===active.canvasId&&focus.kind===active.kind&&
        focus.id===active.id&&sourceShaOf(state)===active.sourceSha;
    }
    function saveDraft(){
      if(active)drafts[key(active)]=$('mentor-author-reply').value;
    }
    function base(){
      return '/api/beginner/studio/canvases/'+encodeURIComponent(bridge.remote().canvasId)+'/mentor';
    }
    function line(tag,value,parent){
      var element=document.createElement(tag);element.textContent=value;parent.appendChild(element);
      return element;
    }
    function previewEdited(){
      return !!chosen&&(
        $('mentor-working-title').value!==chosen.seedTitle||
        $('mentor-working-content').value!==chosen.seedContent);
    }
    function choose(title,content,sourceRef){
      if(!stillCurrent()||!packet||packet.status!=='ready')return;
      if(previewEdited()){
        $('mentor-keep-status').textContent=
          'Keep or explicitly discard your edited working preview before choosing another.';
        return;
      }
      var remote=bridge.remote();
      if(packet.canvas_revision!==remote.revision||
          (packet.candidate_request_sha256||null)!==active.sourceSha){
        notice='Mentor advice is stale; no working change can be prepared.';render();return;
      }
      var seedTitle=title.slice(0,120),seedContent=content.slice(0,20000);
      chosen={sourceRef:sourceRef,seedTitle:seedTitle,seedContent:seedContent};
      $('mentor-working-title').value=seedTitle;
      $('mentor-working-content').value=seedContent;
      $('mentor-keep-status').textContent='Review or edit before choosing to save; nothing is accepted automatically.';
      render();
    }
    async function keep(){
      if(!chosen||!stillCurrent()||busy||!packet||packet.status!=='ready')return;
      if(!bridge.canNavigate()){
        $('mentor-keep-status').textContent='Save your working-idea edits before keeping mentor advice.';
        return;
      }
      var choice={
        title:$('mentor-working-title').value,content:$('mentor-working-content').value,
        sourceRef:chosen.sourceRef,mentorRequestSha:packet.mentor_request_sha256,
        canvasRevision:packet.canvas_revision,
        candidateSha:packet.candidate_request_sha256,focusId:active.id
      };
      if(!bridge.saveWorking){
        $('mentor-keep-status').textContent='Working save unavailable; nothing changed.';return;
      }
      busy=true;render();
      try{
        var saved=await bridge.saveWorking(choice);
        $('mentor-keep-status').textContent=saved?
          'Confirmed as working architecture, NOT canon.':
          'Working save not confirmed. Your preview is still editable.';
        if(saved)chosen=null;
      }catch(e){$('mentor-keep-status').textContent='Working save failed: '+e.message;}
      finally{busy=false;render();}
    }
    function drawAdvice(result){
      var host=$('mentor-advice');host.replaceChildren();
      if(!result||result.status!=='ready'||!result.advice)return;
      var advice=result.advice;
      var title=line('strong','Mentor interpretation · Noncanonical',host);
      if(advice.summary)line('p',advice.summary,host);
      if(advice.explanation)line('p',advice.explanation,host);
      if(advice.author_reply_interpretation)
        line('p','Your reply interpreted as: '+advice.author_reply_interpretation,host);
      if(advice.question)line('p','Question: '+advice.question,host);
      if(advice.challenge){
        line('p','Constructive challenge: '+advice.challenge,host);
        line('small',advice.challenge_basis==='proposed_tension'?
          'Attributable proposed tension, not an accepted contradiction.':
          'Conditional creative hypothesis, not an established defect.',host);
      }
      (advice.directions||[]).forEach(function(item){
        var box=line('div','',host);box.className='mentor-direction';
        line('strong',item.title+' · '+item.divergence_axis.replaceAll('_',' '),box);
        if(item.distinguishing_factor)
          line('p','What makes this different: '+item.distinguishing_factor,box);
        line('p','Mechanism: '+item.mechanism,box);
        line('p','Consequence: '+item.consequence,box);
        line('p','Tradeoff: '+item.tradeoff,box);
        line('small',item.source_status==='source_bound_proposal'?
          'Source-linked proposal · '+item.source_refs.join(', '):
          'Model hypothesis · not accepted story',box);
        var action=line('button','Review as working idea',box);
        action.type='button';action.addEventListener('click',function(){
          var content='AI PROPOSAL — not accepted story\n\nMechanism: '+item.mechanism+
            '\nConsequence: '+item.consequence+'\nTradeoff: '+item.tradeoff+
            '\n\nAuthor\'s original answer (if any): '+(result.author_reply||'')+
            '\n\nReview and rewrite this proposal in your own words.';
          choose(item.title,content,'directions/'+item.id);
        });
      });
      if(advice.author_reply_interpretation){
        var interpret=line('button','Review interpretation as working idea',host);
        interpret.type='button';interpret.addEventListener('click',function(){
          choose('Interpretation of '+(active?.id||'story'),
            'AUTHOR ANSWER (verbatim): '+(result.author_reply||'')+
            '\n\nAI INTERPRETATION — noncanonical:\n'+advice.author_reply_interpretation,
            'interpretation');
        });
      }
      if(advice.limitation)line('small','Limitations: '+advice.limitation,host);
      line('small','Nothing here changes working or accepted story by itself.',host);
    }
    function render(){
      var host=$('unfolding-mentor-dialogue');if(!host)return;
      host.hidden=!stillCurrent();
      if(host.hidden)return;
      // Displaying old advice as current is itself a provenance failure, even
      // if the eventual Keep action would reject it.
      if(packet && (
          (Number.isInteger(packet.canvas_revision) &&
            packet.canvas_revision!==bridge.remote().revision) ||
          (Object.prototype.hasOwnProperty.call(packet,'candidate_request_sha256') &&
            (packet.candidate_request_sha256||null)!==active.sourceSha))){
        if(!previewEdited())chosen=null;
        packet={status:'stale'};
        notice='The working canvas or proposal changed. Mentor advice is stale; request fresh guidance.';
      }
      $('mentor-author-reply').disabled=busy;
      $('mentor-send').disabled=busy;
      $('mentor-complete').disabled=busy||!packet||packet.status!=='awaiting_host_agent';
      $('mentor-handoff').hidden=!packet||packet.status!=='awaiting_host_agent';
      $('mentor-status').textContent=notice;
      $('mentor-working-preview').hidden=!chosen||!packet||
        (packet.status!=='ready'&&!previewEdited());
      $('mentor-keep').disabled=busy||!packet||packet.status!=='ready';
      $('mentor-discard-preview').disabled=busy;
      $('mentor-request').textContent=packet&&packet.request?
        JSON.stringify(packet.request,null,2):'';
      drawAdvice(packet);
    }
    function show(info){
      var remote=bridge.remote(),state=bridge.state();
      if(!remote.ready||remote.failed||!current()||!info||!info.focusId){
        bridge.status('Save the working canvas and select an architecture idea first.');return false;
      }
      var incoming={id:info.focusId,kind:state.unfoldingFocus.kind,
        sourceSha:sourceShaOf(state),canvasId:remote.canvasId};
      if(state.unfoldingFocus.id!==incoming.id||info.sourceSha!==incoming.sourceSha||
          incoming.kind!=='candidate'&&incoming.kind!=='working'){
        bridge.status('Mentor focus has changed. Select the idea again.');return false;
      }
      var changed=!active||key(active)!==key(incoming);
      if(changed&&previewEdited()){
        bridge.status('An edited mentor preview is unsaved. Return to the prior focus to keep or discard it.');
        return false;
      }
      if(active)saveDraft();
      active=incoming;if(changed){packet=null;chosen=null;notice='Working advice only. The author decides what to keep.';}
      $('mentor-author-reply').value=drafts[key(active)]||'';
      render();return true;
    }
    async function prepare(purpose){
      if(!active||!stillCurrent()||busy)return;
      if(!['learn','explore','question','challenge','followup'].includes(purpose))return;
      if(previewEdited()){
        notice='Keep or discard your edited working preview before requesting fresh advice.';
        render();return;
      }
      saveDraft();var selected={...active},reply=$('mentor-author-reply').value;
      if(!bridge.canNavigate()){
        notice='Save working-idea edits before requesting mentorship.';render();return;
      }
      if(reply.length>2000){notice='Reply exceeds 2,000 characters.';render();return;}
      busy=true;chosen=null;notice='Saving author edits before preparing the host-agent request…';render();
      try{
        await bridge.flush();
        if(!stillCurrent()||bridge.remote().canvasId!==selected.canvasId)throw Error('Mentor focus changed.');
        if(bridge.remote().failed)throw Error('Working canvas could not be saved.');
        var response=await bridge.fetch(base()+'/prepare',{
          method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({focus_id:selected.id,focus_kind:selected.kind,
            purpose:purpose,author_reply:reply})
        }).then(bridge.apiJson);
        if(!stillCurrent())throw Error('Mentor focus changed while request was prepared.');
        packet=response;
        notice='Host-agent request prepared. Use your coding agent to fulfill it; no provider was called automatically.';
      }catch(error){notice='Mentor request not prepared: '+error.message;}
      finally{busy=false;render();}
    }
    async function complete(){
      if(!stillCurrent()||busy||!packet||packet.status!=='awaiting_host_agent')return;
      var payload;
      try{payload=JSON.parse($('mentor-response').value);}catch(error){
        notice='Paste a complete HostAgentResponse JSON envelope, or fulfill through the CLI.';
        render();return;
      }
      busy=true;render();
      try{
        var response=await bridge.fetch(base()+'/host-agent-response',{
          method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify(payload)
        }).then(bridge.apiJson);
        if(!stillCurrent())throw Error('Mentor focus changed; result was not applied to this view.');
        packet=response;chosen=null;notice=response.status==='ready'?
          'Advice is ready to inspect. No story meaning has been accepted.':
          'Mentor source changed; refresh before using advice.';
      }catch(error){notice='Mentor response rejected: '+error.message;}
      finally{busy=false;render();}
    }
    async function open(projection,purpose){
      if(!show(projection))return;
      return prepare(purpose||'explore');
    }
    async function resume(projection){
      if(!show(projection))return;
      if(previewEdited()){
        notice='Keep or discard your edited working preview before replacing this advice.';
        render();return;
      }
      busy=true;render();
      try{
        var response=await bridge.fetch(base()).then(bridge.apiJson);
        if(!stillCurrent())throw Error('Focus changed.');
        if(response.focus_id===active.id&&response.focus_kind===active.kind){
          packet=response;chosen=null;
        }else{
          packet=null;chosen=null;
        }
        notice=packet?.status==='stale'?
          'The saved mentor response is stale; no advice or working choice is available.':
          packet?.status==='ready'?'Previous mentor advice restored as read-only.':
          'No current advice for this focus. Choose a question or exploration.';
      }catch(error){notice='Could not read mentor advice: '+error.message;}
      finally{busy=false;render();}
    }
    $('mentor-author-reply').addEventListener('input',saveDraft);
    $('mentor-refresh').addEventListener('click',function(){
      return active?resume({focusId:active.id,sourceSha:active.sourceSha}):null;
    });
    $('mentor-send').addEventListener('click',function(){return prepare('followup');});
    $('mentor-complete').addEventListener('click',complete);
    $('mentor-keep').addEventListener('click',keep);
    $('mentor-discard-preview').addEventListener('click',function(){
      chosen=null;
      $('mentor-working-title').value='';$('mentor-working-content').value='';
      $('mentor-keep-status').textContent='The editable preview was discarded without saving.';
      render();
    });
    $('mentor-dismiss').addEventListener('click',function(){
      if(previewEdited()){
        notice='Keep or discard your edited working preview before closing.';
        render();return;
      }
      saveDraft();active=null;packet=null;chosen=null;render();
    });
    return {render,open,resume,prepare,complete};
  }
  global.AuteurStudioMentorDialogueController={create};
})(window,document);
