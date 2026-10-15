/** Book-level read-only Full/Review mode over Studio's existing CanvasStore ownership. */
(function(global){
 'use strict';
 function create(binding){
   if(!binding||typeof binding.getState!=='function'||typeof binding.getRemote!=='function')
     throw Error('Studio state/read-only canvas bridge required');
   function render(){
     var state=binding.getState(),remote=binding.getRemote(),mode=state.fullArchitectureDisplay||'focus';
     var eligible=state.workspace==='architecture'&&state.view==='architecture'&&state.architectureFacet==='overview';
     binding.nav.hidden=!eligible;
     binding.root.hidden=!eligible||mode!=='full';
     binding.reviewRoot.hidden=!eligible||mode!=='review';
     binding.focusButton.setAttribute('aria-pressed',String(mode==='focus'));
     binding.fullButton.setAttribute('aria-pressed',String(mode!=='focus'));
     if(!eligible||mode==='focus')return false;
     var api=global.AuteurStudioFullArchitecture;
     if(!api){binding.root.hidden=false;binding.root.textContent='Full Architecture sources are unavailable. Working story remains unchanged.';return true;}
     // The current Studio candidate is noncanonical, and no verified Pack or accepted
     // Identity/Structure read source is delivered by this browser API.
     // Null deliberately means unavailable source, never "not accepted" or "noncompliant".
     var evidence=state.fullArchitectureEvidence;
     var current=!!(evidence && evidence.canvasId===remote.canvasId &&
       evidence.requestSha && evidence.requestSha===state.architectureRequestSha);
     var projection=api.project({candidate:state.architecture,requestSha:state.architectureRequestSha,
       workingItems:state.items,workingConnections:state.connections||[],canvasRevision:remote.revision,
       genreEvidence:[],legacyEvidence:current?evidence.legacyEvidence:[],
       acceptedIdentity:null,acceptedStructure:null});
     var focus=function(ref){binding.onFocus(ref);};
     if(mode==='review'){
       api.renderReview(binding.reviewRoot,api.review(projection),{
         onFocusRef:focus,onReturn:function(){binding.onMode('full');}});
     }else{
       api.renderFull(binding.root,projection,{
         expandedGenre:state.fullArchitectureGenre||null,
         onToggleGenre:function(genre){binding.onGenre(genre);},
         onFocusRef:focus,onReview:function(){binding.onMode('review');}});
     }
     return true;
   }
   return {render:render};
 }
 global.AuteurStudioFullArchitectureController={create:create};
})(window);
