/* Truth-preserving view of author working text beside agent-authored proposals.
 * No interpretation of free text and no story-state write. */
(function (global) {
  'use strict';
  function project(items, architectureProjection) {
    var list = Array.isArray(items) ? items : [];
    var author = list.find(function (item) { return item && item.id === 'story-vision'; });
    var visionText = author && typeof author.content === 'string' ? author.content : '';
    var projection = architectureProjection || {};
    var candidate = projection.candidate;
    var status = typeof projection.status === 'string' ? projection.status : 'not_started';
    var requestSha = typeof projection.candidate_request_sha256 === 'string' ?
      projection.candidate_request_sha256 : null;
    var summary = candidate && typeof candidate.summary === 'string' ? candidate.summary : '';
    return {
      authorVision: visionText.trim() ? {
        text: visionText,
        authority: 'author_working',
        sourceRef: 'canvas/items/story-vision'
      } : null,
      proposal: summary ? {
        text: summary,
        authority: 'agent_proposal',
        sourceRef: requestSha ? 'architecture/requests/' + requestSha : null,
        requestSha: requestSha,
        freshness: status === 'stale' ? 'stale' : (status === 'ready' || status === 'review_ready') ? 'current' : 'unconfirmed'
      } : null,
      sourceStatus: status
    };
  }
  global.AuteurStudioAuthorIntent = { project: project };
})(window);