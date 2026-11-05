/* Review a completed agent interaction in the original source context. */
(function(global){'use strict';
 function createCreativeFeedbackController({getCandidate,getCanvasId,selectGraphFocus,openHybridReview,renderInquiry}={}){
  if(!getCandidate||!selectGraphFocus||!openHybridReview)throw Error('Creative feedback requires source and UI callbacks');
  let destroyed=false;
  const exists=target=>{const c=getCandidate();if(!c)return false;
    const collections={node:['nodes','id'],link:['links','id'],genre_interaction:['genre_interactions','id'],
       emotion_target:['emotion_targets','id'],complex_emotion:['complex_emotions','id'],
       genre_contract:['genre_contracts','genre_node_id'],phase:['phases','id']};
    const cfg=collections[target.kind];return !!cfg&&(c[cfg[0]]||[]).some(x=>x[cfg[1]]===target.id);
  };
  const valid=(receipt,sha)=>!!receipt&&receipt.expected_candidate_request_sha256===sha&&
    (!getCanvasId||receipt.canvas_id===getCanvasId())&&Array.isArray(receipt.anchors)&&receipt.anchors.length>0;
  function onInquiry(projection,activeSha){if(destroyed)return false;
    if(projection?.status!=='ready'||!projection.result)return false;
    const receipt=projection.result.intent;if(!valid(receipt,activeSha))return false;
    const first=receipt.anchors[0];if(exists(first))selectGraphFocus({kind:first.kind,id:first.id,field:first.field||null,reference:first.reference||null});
    if(renderInquiry)renderInquiry(projection.result);return true;
  }
  function onReviewReady(projection){if(destroyed||projection?.status!=='review_ready')return false;
    const review=projection.review;if(!review||review.prior_request_sha256!==projection.candidate_request_sha256)return false;
    const receipt=review.graph_intent_receipt;if(!valid(receipt,projection.candidate_request_sha256))return false;
    const first=receipt.anchors[0];
    const target={kind:first.kind,id:first.id};
    if(first.field)target.field=first.field;
    if(first.reference)target.reference=first.reference;
    openHybridReview(target);return true;
  }
  return{onInquiry,onReviewReady,onSourceChanged:()=>false,destroy:()=>{destroyed=true}};
 }
 global.AuteurStudioCreativeFeedback={createCreativeFeedbackController};
})(window);
