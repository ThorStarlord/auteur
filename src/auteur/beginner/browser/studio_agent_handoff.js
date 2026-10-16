/* Presentation-only handoff; does not connect a provider or create story authority. */
(function (global) {
  'use strict';
  function present(projection, hostCapability) {
    var data = projection || {};
    var status = data.status || 'not_started';
    var attached = !!(hostCapability && hostCapability.studio_architecture &&
      hostCapability.studio_architecture.attached === true);
    var previous = !!data.candidate;
    var messages = {
      not_started: 'Describe a creative direction to explore.',
      review_ready: 'A revised working proposal is ready to compare; nothing was accepted.',
      ready: 'Working architecture proposal ready for exploration; no story canon changed.',
      stale: 'Your Story Vision changed. The previous proposal remains available as older evidence.',
      error: 'The request could not be completed. Your working story remains unchanged.'
    };
    if (status === 'awaiting_host_agent') return {
      mode: attached ? 'awaiting_response' : 'manual_required',
      message: attached ? 'Waiting for the attached host agent to answer the request.' :
        'Request prepared, but no coding agent is connected to this browser. Copy the request for your coding agent or complete it with the local CLI.',
      primaryAction: attached ? 'Check response' : 'Copy request for coding agent',
      hasPreviousProposal: previous
    };
    var mode = Object.prototype.hasOwnProperty.call(messages, status) ? status : 'error';
    return { mode: mode, message: messages[mode], primaryAction: 'Explore narrative architecture',
      hasPreviousProposal: previous };
  }
  function defaultDelay(ms) { return new Promise(function (resolve) { setTimeout(resolve, ms); }); }
  async function poll(options) {
    var config = options || {};
    var max = Math.max(1, Math.min(12, config.maxAttempts || 12));
    var delay = config.delay || defaultDelay;
    var key = config.key;
    for (var attempt = 1; attempt <= max; attempt++) {
      if (config.shouldStop && config.shouldStop()) return { reason: 'stopped', attempts: attempt - 1 };
      if (config.getKey() !== key) return { reason: 'context_changed', attempts: attempt - 1 };
      var projection;
      try { projection = await config.read(); }
      catch (error) { return { reason: 'error', attempts: attempt, error: String(error) }; }
      if (config.getKey() !== key) return { reason: 'context_changed', attempts: attempt };
      if (projection.status === 'ready' || projection.status === 'review_ready')
        return { reason: projection.status, attempts: attempt, projection: projection };
      if (projection.status !== 'awaiting_host_agent')
        return { reason: projection.status || 'stopped', attempts: attempt, projection: projection };
      if (attempt < max) await delay(config.delayMs || 5000);
    }
    return { reason: 'exhausted', attempts: max };
  }
  async function dispatch(options) {
    var capability = options.capability;
    if (!capability || !capability.studio_architecture ||
        capability.studio_architecture.attached !== true) return null;
    if (!options.projection.request) return null;
    return options.post(options.url + '/dispatch', {
      request_sha256: options.projection.request.request_sha256
    });
  }
  async function load(options) {
    var values = await Promise.all([options.readProjection(), options.readCapability()]);
    return {projection: values[0], capability: values[1]};
  }
  global.AuteurStudioAgentHandoff = { present: present, poll: poll, dispatch: dispatch, load: load };
})(window);
