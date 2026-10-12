/* Dedicated explanatory heroes for one working architecture proposal. Pure display only. */
(function(global,document){
  'use strict';
  var api=global.AuteurStudioExplanations;
  function el(tag,cls,content){var e=document.createElement(tag);if(cls)e.className=cls;if(content!==undefined)e.textContent=String(content);return e;}
  function section(parent,caption,value,cls){
    if(!value)return;
    var block=el('section',cls||'studio-explanation-card');
    block.append(el('div','studio-explanation-label',caption),el('p','',value));parent.append(block);
  }
  function semanticButton(parent,link,projection,onNavigate){
    var target=api.resolve(projection,link.targetFacet,link.targetKey,projection.requestSha);
    if(!target)return;
    var button=el('button','studio-semantic-link','Explore '+target.title+' · '+link.relationVerb);
    button.type='button';button.setAttribute('data-semantic-link',link.id);
    button.addEventListener('click',function(){onNavigate(link);});
    parent.append(button);
  }
  function inspector(root,entry,onInspect){
    var button=el('button','studio-explanation-inspect','Inspect source · '+entry.sourceRef);
    button.type='button';button.addEventListener('click',function(){onInspect(entry);});root.append(button);
  }
  function hero(root,title,sub){
    root.replaceChildren();
    root.append(el('div','studio-explanation-label','EXPLAIN THIS WORKING STORY'),el('h2','studio-explanation-title',title),el('p','studio-explanation-note',sub));
  }
  function chosen(packet,facet,key){return api.resolve(packet,facet,key,packet.requestSha)||packet[facet][0]||null;}
  function relations(root,packet,entry,facet,onNavigate){
    var links=api.linksFor(packet,{facet:facet,key:entry.key});
    var group=el('section','studio-explanation-related');
    group.append(el('h3','','Follow documented relationships'));
    if(!links.length)group.append(el('p','studio-explanation-note','No declared connections. Missing links do not imply incompatible ideas.'));
    links.forEach(function(link){semanticButton(group,link,packet,onNavigate);});
    root.append(group);
  }
  function renderGenre(root,packet,genreKey,onNavigate,onInspect){
    var e=chosen(packet,'genres',genreKey);
    hero(root,e?e.title:'Genre anatomy','What this proposed genre is intended to contribute. A story proposal is not a universal genre rule.');
    if(!e){section(root,'NO GENRE','No genre proposal available.');return;}
    section(root,'SOURCE COVERAGE',e.coverageMessage,'studio-explanation-warning');
    var contract=e.contract;
    if(contract){
      section(root,'PROPOSED NARRATIVE ENGINE',contract.narrative_engine,'studio-explanation-feature');
      section(root,'PROPOSED STRUCTURAL PATTERN',contract.structural_pattern);
      section(root,'PROPOSED READER PAYOFFS',(contract.payoff_expectations||[]).join(' · '));
      section(root,'AESTHETIC STRATEGIES',(contract.aesthetic_strategies||[]).join(' · '));
    }else section(root,'STORY PROPOSAL',e.detail);
    relations(root,packet,e,'genres',onNavigate);inspector(root,e,onInspect);
  }
  function renderTrope(root,packet,tropeKey,onNavigate,onInspect){
    var e=chosen(packet,'tropes',tropeKey);
    hero(root,e?e.title:'Trope functions','Distinguish the recorded story-specific use from uncertain genre knowledge.');
    if(!e){section(root,'NO TROPE','No trope proposal available.');return;}
    var columns=el('div','studio-explanation-comparison');
    var left=el('section','studio-explanation-card');
    left.append(el('div','studio-explanation-label','GENRE EVIDENCE'));
    if(e.ownerGenreId){
      var genre=packet.genres.find(function(x){return x.nodeId===e.ownerGenreId;});
      left.append(el('h3','',genre?genre.title:e.ownerGenreId));
      left.append(el('p','',genre?genre.coverageMessage:'No verified pack attached.'));
    }else left.append(el('p','','No attributed Genre Pack relation is established by this trope node.'));
    columns.append(left);
    var right=el('section','studio-explanation-card');
    right.append(el('div','studio-explanation-label','THIS STORY PROPOSES'),el('h3','',e.title),
      el('p','',e.detail||'A proposed narrative role, not accepted canon.'),
      el('small','studio-explanation-note',e.sourceRef));
    columns.append(right);root.append(columns);
    relations(root,packet,e,'tropes',onNavigate);inspector(root,e,onInspect);
  }
  function renderStructure(root,packet,structureKey,onNavigate,onInspect){
    var e=chosen(packet,'structure',structureKey);
    hero(root,e?e.title:'Narrative structure','How proposed functions relate. A source-backed proposal is not a guaranteed reader effect.');
    if(!e){section(root,'NO STRUCTURE','No structural proposal available.');return;}
    section(root,'PROPOSED FUNCTION',e.detail,'studio-explanation-feature');
    section(root,'SOURCE',e.sourceRef);
    var links=api.linksFor(packet,{facet:'structure',key:e.key}),group=el('section','studio-explanation-related');
    group.append(el('h3','','Recorded relationships'));
    if(!links.length)group.append(el('p','studio-explanation-note','No supported relationship is recorded; no causal arrow is implied.'));
    links.forEach(function(link){
      var destination=api.resolve(packet,link.targetFacet,link.targetKey,packet.requestSha);
      if(!destination)return;
      var row=el('div','studio-explanation-mechanism');
      row.append(el('strong','',e.title),el('span','',link.relationVerb+' → '+destination.title),
        el('small','studio-explanation-note','Source-backed proposal / NOT ACCEPTED · '+link.sourceRef));
      semanticButton(row,link,packet,onNavigate);group.append(row);
    });root.append(group);inspector(root,e,onInspect);
  }
  global.AuteurStudioExplanationViews={renderGenre:renderGenre,renderTrope:renderTrope,renderStructure:renderStructure};
})(window,document);
