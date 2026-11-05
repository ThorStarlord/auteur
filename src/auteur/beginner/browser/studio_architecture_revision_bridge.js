/* Optional, read-only Studio review bridge. Never requests an agent or writes story state. */
(function (global) {
  'use strict';
  function create({disclosure, root, getCanvasId, loadModules} = {}) {
    if (!disclosure || !root || typeof getCanvasId !== 'function') {
      throw new Error('Revision bridge requires review disclosure, root and canvas identity');
    }
    const load = loadModules || (async () => {
      const [compare, view] = await Promise.all([
        import('/studio_architecture_revision_compare.mjs'),
        import('/studio_architecture_revision_view.mjs'),
      ]);
      return {compareArchitectureRevision:compare.compareArchitectureRevision,
        mountRevisionReview:view.mountRevisionReview};
    });
    let snapshot=null, viewer=null, generation=0;
    function dispose() {
      generation += 1;
      if (viewer) {viewer.destroy();viewer=null;}
      root.replaceChildren();
    }
    function valid(projection) {
      return !!(projection && projection.status==='review_ready'
        && projection.candidate?.schema_version===2
        && projection.candidate_request_sha256
        && projection.review?.candidate?.schema_version===2
        && projection.review.request_sha256
        && projection.review.prior_request_sha256===projection.candidate_request_sha256);
    }
    function update(projection, canvasId) {
      dispose();
      snapshot=valid(projection)?{projection,canvasId}:null;
      disclosure.hidden=!snapshot;
      disclosure.open=false;
    }
    async function open() {
      const current=snapshot;
      if (!current || !disclosure.open || getCanvasId()!==current.canvasId) return;
      const token=++generation;
      try {
        const modules=await load();
        if (token!==generation || !disclosure.open || snapshot!==current
            || getCanvasId()!==current.canvasId) return;
        const p=current.projection,review=p.review;
        const comparison=modules.compareArchitectureRevision({
          before:p.candidate,after:review.candidate,
          beforeRequestSha:p.candidate_request_sha256,
          afterRequestSha:review.request_sha256,
          expectedPriorSha:review.prior_request_sha256,
          requestedChange:review.requested_change || '',
          acceptedConstraints:review.preserved?.accepted_constraints || [],
        });
        viewer=modules.mountRevisionReview(root,{comparison});
      } catch(error) {
        if (token!==generation) return;
        root.textContent='Visual comparison unavailable: '+error.message+
          '. The existing textual revision review remains available.';
      }
    }
    disclosure.addEventListener('toggle', () => {
      if (disclosure.open) open();
      else dispose();
    });
    return {update,destroy:()=>{dispose();snapshot=null;disclosure.hidden=true;}};
  }
  global.AuteurStudioRevisionBridge={create};
})(window);
