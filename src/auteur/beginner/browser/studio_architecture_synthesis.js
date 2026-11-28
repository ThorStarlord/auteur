/* Long-horizon synthesis of selected developments, as the owner recorded it. Presentation only: every word here states what the
   owner read or what the agent returned and the owner accepted. Nothing here applies, accepts, adopts or canonises a synthesis, and
   nothing judges it. Built with text nodes only. Trajectory first; relations, culmination, alternatives, opportunities and open
   decisions follow; the evidence each claim cites is disclosed on demand. */
(function(global){'use strict';

  var MAX_DEVELOPMENTS=3;
  var BASIS={recorded:'Recorded',inferred:'Inferred (agent reading)',proposed:'Proposed, conditional'};
  var HORIZON={existing_book:'In an existing Book',proposed_book:'Beyond the existing Books'};
  var RELATION={prerequisite:'Necessary: cannot occur without',preparation:'Helpful preparation',enables:'Enables',
    complicates:'Complicates',reinforces:'Reinforces',independent:'Independent',incompatible:'Incompatible'};
  var DEPENDENCE={causal:'Causal dependence',thematic:'Thematic resonance',sequential_only:'Sequence only, no dependence',
    none:'No dependence stated'};
  var VIABILITY={viable:'Still viable',weakened:'Weakened',closed:'Closed by this ordering',unresolved:'Unresolved'};
  var STANDING={
    current:{label:'Current: the Architecture and Working Book it read are unchanged, and this is the latest synthesis.',tone:'ok'},
    superseded:{label:'Earlier: a later synthesis of the canvas exists. It is kept as an earlier reading.',tone:'warn'},
    stale:{label:'Stale: the Architecture, the Working Book, the vision or a handoff it read has changed since it was prepared.',
      tone:'warn'}
  };
  var VERDICT={accepted:'Accepted',partly_accepted:'Partly accepted',rejected:'Rejected',unresolved:'Unresolved'};
  var EVIDENCE_KIND={development:'Developing material',author_vision:'Story Vision',author_culmination:'Named culmination',
    book_element:'Working Book element',coverage:'Coverage of the Working Book',link:'Recorded link',handoff:'Accepted reconsideration'};
  var JUDGMENT={supported:'Supported by the evidence',defensible_inference:'Defensible inference',
    creative_speculation:'Creative proposal, not a record',overreaching:'Goes beyond the evidence',
    temporal_misreading:'Reads a time the evidence does not give',modal_misreading:'Reads a condition or possibility as achieved',
    attribution_error:'Attributes the claim to the wrong source',standing_confusion:'Confuses the standing of the source',
    unsupported_relation:'The relation is not stated in the evidence',contradicted:'Contradicted by the evidence',
    insufficient_evidence:'The evidence does not settle it'};
  var REGISTER={established:'Established by the record',inferred_from_established:'Inferred from the record',
    agent_proposed:'Agent-proposed in the record',author_stated:'Stated by the author',not_established:'Not established by the record',
    mixed:'Mixed in the record'};
  var CLAIM_KIND={stage:'Stage',relation:'Relation',alternative_path:'Alternative path',opportunity:'Opportunity',
    necessary_condition:'Necessary condition',enrichment_condition:'Optional enrichment'};

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.appendChild(document.createTextNode(String(text)));
    return node;
  }
  function labelled(tag, text, forId) {
    var node = el(tag, 'synthesis-label', text);
    if (forId) node.htmlFor = forId;
    return node;
  }
  function chip(text, tone) { return el('span', 'synthesis-chip' + (tone ? ' synthesis-chip-' + tone : ''), text); }
  function words(map, key, fallback) { return (map && map[key]) || fallback || key || ''; }

  function createSynthesisPanel(options) {
    var root = options.root;
    var live = options.live || {};
    var view = {projection: null, selected: [], question: '', culmination: '', handoffs: [], criticism: '',
      followUp: false, busy: false, error: null, handoffChoices: [], responseText: '',
      verification: null, carried: [], carriedLabel: {}, claimDrafts: {}};
    var loadToken = 0;

    function say(text, alert) {
      var target = alert ? live.alert : live.status;
      if (target) target.textContent = text || '';
    }
    function canvasPath(suffix) {
      return '/api/beginner/studio/canvases/' + encodeURIComponent(options.canvasId()) + '/architecture/' + suffix;
    }
    function request(path, method, body) {
      var init = {method: method || 'GET', headers: {'Content-Type': 'application/json'}};
      if (body !== undefined) init.body = JSON.stringify(body);
      return fetch(path, init).then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (payload) {
          if (!response.ok) throw new Error(payload.error || payload.message || ('The owner refused this (' + response.status + ').'));
          return payload;
        });
      });
    }

    function candidate() { return options.candidate ? options.candidate() : null; }

    // The developments a synthesis may read: the persistent questions and the mechanism nodes of the current Architecture.
    function developmentChoices() {
      var c = candidate();
      if (!c) return [];
      var choices = [];
      (c.open_question_ids || []).forEach(function (identifier, index) {
        var text = (c.open_questions || [])[index] || identifier;
        choices.push({kind: 'question', ref: identifier, label: text, group: 'question'});
      });
      (c.nodes || []).forEach(function (node) {
        choices.push({kind: 'mechanism', ref: node.id, label: node.title || node.id, group: 'mechanism'});
      });
      return choices;
    }

    function reset() {
      view.projection = null; view.selected = []; view.question = ''; view.culmination = ''; view.handoffs = [];
      view.criticism = ''; view.followUp = false; view.busy = false; view.error = null; view.handoffChoices = [];
      view.responseText = ''; view.verification = null; view.carried = []; view.carriedLabel = {}; view.claimDrafts = {};
      loadToken += 1;
      if (root) root.textContent = '';
    }

    function load() {
      var token = ++loadToken;
      if (!options.canvasId()) return Promise.resolve(null);
      return request(canvasPath('synthesis')).then(function (projection) {
        if (token !== loadToken) return null;
        view.projection = projection;
        return loadHandoffChoices(token).then(function () {
          return loadVerifications(token, projection);
        }).then(function () {
          if (token === loadToken) render();
          return projection;
        });
      });
    }

    // Accepted reconsiderations of the latest consequence analysis, offered as handoffs when they are ready.
    function loadHandoffChoices(token) {
      return request(canvasPath('consequence')).then(function (consequence) {
        if (!consequence.request_sha256) return null;
        return request(canvasPath('consequence/' + consequence.request_sha256 + '/reconsiderations')).then(function (reply) {
          if (token !== loadToken) return null;
          view.handoffChoices = (reply.reconsiderations || []).filter(function (row) {
            return row.status === 'ready' && row.answer;
          }).map(function (row) {
            return {requestSha256: row.request_sha256, disposition: row.answer.disposition,
              judgement: row.answer.reconsidered_judgment, standing: row.standing,
              claim: (row.claim && row.claim.kind) || 'claim'};
          });
          return null;
        });
      }).catch(function () { view.handoffChoices = []; });
    }

    function render() {
      if (!root) return;
      root.textContent = '';
      var projection = view.projection;
      if (!projection) return;
      root.appendChild(renderCompose(projection));
      if (projection.result || (projection.request && projection.status === 'awaiting_host_agent')) {
        root.appendChild(renderCurrent(projection));
      }
      if (projection.history && projection.history.length > 1) root.appendChild(renderHistory(projection));
    }

    function renderCompose(projection) {
      var section = el('section', 'synthesis-compose');
      var heading = el('h3', 'synthesis-subtitle', view.followUp ? 'Continue from this synthesis' : 'Ask about these developments');
      section.appendChild(heading);
      if (view.followUp) {
        section.appendChild(el('p', 'synthesis-note', 'The follow-up keeps the same developments. The earlier judgement is given to the agent as text only, not as evidence.'));
      }
      if (!view.followUp) {
        var choices = developmentChoices();
        var fieldset = el('fieldset', 'synthesis-developments');
        fieldset.appendChild(el('legend', 'synthesis-label', 'Choose up to three developments'));
        if (!choices.length) fieldset.appendChild(el('p', 'synthesis-note', 'The Architecture has no questions or mechanisms yet.'));
        choices.forEach(function (choice, index) {
          var id = 'synthesis-dev-' + index;
          var row = el('label', 'synthesis-choice');
          var box = el('input');
          box.type = 'checkbox'; box.id = id; box.value = choice.kind + ':' + choice.ref;
          box.checked = view.selected.some(function (picked) { return picked.kind === choice.kind && picked.ref === choice.ref; });
          box.disabled = !box.checked && view.selected.length >= MAX_DEVELOPMENTS;
          box.setAttribute('data-development', choice.kind + ':' + choice.ref);
          box.addEventListener('change', function () {
            if (box.checked) view.selected.push({kind: choice.kind, ref: choice.ref});
            else view.selected = view.selected.filter(function (picked) { return !(picked.kind === choice.kind && picked.ref === choice.ref); });
            render();
          });
          row.appendChild(box);
          row.appendChild(el('span', 'synthesis-choice-text', (choice.group === 'question' ? 'Question: ' : 'Mechanism: ') + choice.label));
          fieldset.appendChild(row);
        });
        section.appendChild(fieldset);
      } else {
        section.appendChild(el('p', 'synthesis-developments-note', 'Developments: ' + view.selected.map(function (picked) {
          return picked.kind + ' ' + picked.ref;
        }).join(', ')));
      }
      var question = el('textarea', 'synthesis-question');
      question.id = 'synthesis-question-input';
      question.rows = 3; question.maxLength = 1200; question.value = view.question;
      question.setAttribute('data-synthesis', 'question');
      question.addEventListener('input', function () { view.question = question.value; });
      section.appendChild(labelled('label', 'What do you want to understand about these developments?', question.id));
      section.appendChild(question);
      if (!view.followUp) {
        var culmination = el('textarea', 'synthesis-culmination');
        culmination.id = 'synthesis-culmination-input';
        culmination.rows = 2; culmination.maxLength = 600; culmination.value = view.culmination;
        culmination.setAttribute('data-synthesis', 'culmination');
        culmination.addEventListener('input', function () { view.culmination = culmination.value; });
        section.appendChild(labelled('label', 'A possible culmination you have in mind (optional)', culmination.id));
        section.appendChild(culmination);
        if (view.handoffChoices.length) {
          var handoffs = el('fieldset', 'synthesis-handoffs');
          handoffs.appendChild(el('legend', 'synthesis-label', 'Use an accepted reconsideration as a handoff (optional, up to two)'));
          view.handoffChoices.forEach(function (choice, index) {
            var row = el('label', 'synthesis-choice');
            var box = el('input');
            box.type = 'checkbox'; box.id = 'synthesis-handoff-' + index; box.value = choice.requestSha256;
            box.checked = view.handoffs.indexOf(choice.requestSha256) >= 0;
            box.setAttribute('data-handoff', choice.requestSha256);
            box.addEventListener('change', function () {
              if (box.checked && view.handoffs.length < 2) view.handoffs.push(choice.requestSha256);
              else view.handoffs = view.handoffs.filter(function (sha) { return sha !== choice.requestSha256; });
              render();
            });
            row.appendChild(box);
            row.appendChild(el('span', 'synthesis-choice-text', (choice.claim + ': ' + choice.disposition + '. ' +
              (choice.judgement || '') + ' (' + (choice.standing === 'current' ? 'current' : 'historical') + ')')));
            handoffs.appendChild(row);
          });
          section.appendChild(handoffs);
        }
      } else {
        var criticism = el('textarea', 'synthesis-criticism');
        criticism.id = 'synthesis-criticism-input';
        criticism.rows = 3; criticism.value = view.criticism;
        criticism.setAttribute('data-synthesis', 'criticism');
        criticism.addEventListener('input', function () { view.criticism = criticism.value; });
        section.appendChild(labelled('label', 'Criticism to weigh (optional, one per line)', criticism.id));
        section.appendChild(criticism);
        if (view.carried.length) {
          var carried = el('ul', 'synthesis-list synthesis-carried');
          view.carried.forEach(function (sha) {
            carried.appendChild(el('li', 'synthesis-carried-item', 'Verifier judgement carried in as criticism: ' + view.carriedLabel[sha]));
          });
          section.appendChild(carried);
        }
      }
      var actions = el('div', 'synthesis-actions');
      var submit = el('button', 'synthesis-prepare', view.followUp ? 'Prepare follow-up' : 'Prepare synthesis');
      submit.type = 'button';
      submit.setAttribute('data-synthesis', 'prepare');
      submit.disabled = view.busy;
      submit.addEventListener('click', prepare);
      actions.appendChild(submit);
      if (view.followUp) {
        var back = el('button', 'synthesis-cancel', 'Back to the synthesis');
        back.type = 'button';
        back.addEventListener('click', function () { view.followUp = false; render(); });
        actions.appendChild(back);
      }
      section.appendChild(actions);
      if (view.error) section.appendChild(el('p', 'synthesis-error', view.error));
      return section;
    }

    function prepare() {
      if (view.busy) return;
      var projection = view.projection || {};
      var question = (view.question || '').trim();
      if (!question) { view.error = 'Say what you want to understand first.'; render(); return; }
      var developments = view.followUp && projection.developments
        ? projection.developments.map(function (row) { return {kind: row.kind, ref: row.ref}; })
        : view.selected.slice();
      if (!developments.length) { view.error = 'Choose at least one development.'; render(); return; }
      var body = {question: question, developments: developments, culmination: view.followUp ? null : (view.culmination || null),
        handoffs: view.followUp ? [] : view.handoffs.slice(),
        criticism: view.followUp ? view.criticism.split('\n').map(function (line) { return line.trim(); }).filter(Boolean) : [],
        prior_request_sha256: view.followUp ? projection.request_sha256 : null,
        verifications: view.followUp ? view.carried.slice() : []};
      view.busy = true; view.error = null; render();
      say('Preparing the synthesis for your coding agent…');
      request(canvasPath('synthesis/prepare'), 'POST', body).then(function (prepared) {
        view.busy = false; view.followUp = false; view.error = null; view.carried = []; view.carriedLabel = {};
        view.projection = {schema: prepared.synthesis.schema, authority: prepared.synthesis.authority, status: 'awaiting_host_agent',
          standing: prepared.synthesis.standing, request_sha256: prepared.request.request_sha256, request: prepared.request,
          result: null, history: (view.projection && view.projection.history) || [], developments: prepared.synthesis.developments,
          inputs: prepared.synthesis.inputs, evidence: prepared.synthesis.evidence, coverage: prepared.synthesis.coverage,
          handoffs: prepared.synthesis.handoffs, criticism: prepared.synthesis.criticism};
        say('Synthesis prepared. Your coding agent answers the request below; nothing is applied.');
        return load();
      }).catch(function (error) {
        view.busy = false; view.error = error.message;
        say('The synthesis was not prepared: ' + error.message, true);
        render();
      });
    }

    function renderCurrent(projection) {
      var section = el('section', 'synthesis-current');
      var standing = STANDING[projection.standing] || {label: 'Standing not read.', tone: 'note'};
      section.appendChild(el('p', 'synthesis-standing synthesis-standing-' + standing.tone, standing.label));
      if (projection.status === 'awaiting_host_agent' && projection.request) {
        section.appendChild(renderAwaiting(projection));
        return section;
      }
      var result = projection.result;
      if (!result) return section;
      section.appendChild(renderTrajectory(result));
      section.appendChild(renderRelations(result));
      if (result.culmination) section.appendChild(renderCulmination(result.culmination));
      section.appendChild(renderAlternatives(result));
      if (result.opportunities && result.opportunities.length) section.appendChild(renderOpportunities(result));
      section.appendChild(renderOpenWork(result));
      var derived = renderDerivedChanges(projection);
      if (derived) section.appendChild(derived);
      section.appendChild(renderBasisChecks(projection));
      section.appendChild(renderEvidence(projection));
      section.appendChild(renderFollowUp(projection));
      return section;
    }

    function renderAwaiting(projection) {
      var box = el('div', 'synthesis-awaiting');
      box.appendChild(el('p', 'synthesis-note', 'Awaiting your coding agent. Its request fingerprint is ' +
        projection.request_sha256.slice(0, 16) + '…'));
      var text = el('textarea', 'synthesis-request');
      text.readOnly = true; text.rows = 6; text.value = JSON.stringify(projection.request, null, 2);
      text.setAttribute('aria-label', 'Synthesis request for the coding agent');
      box.appendChild(text);
      var response = el('textarea', 'synthesis-response');
      response.rows = 4;
      // The author's pasted response is kept in the panel's state, so a refusal leaves it in place to correct.
      response.value = view.responseText;
      response.addEventListener('input', function () { view.responseText = response.value; });
      response.setAttribute('aria-label', 'Coding agent response to paste');
      response.placeholder = 'Paste the response object here';
      box.appendChild(labelled('label', 'Response from your coding agent', response.id));
      box.appendChild(response);
      var submit = el('button', 'synthesis-submit', 'Check agent response');
      submit.type = 'button';
      submit.setAttribute('data-synthesis', 'submit');
      submit.addEventListener('click', function () {
        if (!response.value.trim()) { view.error = 'Paste the agent response first.'; render(); return; }
        var payload;
        try { payload = JSON.parse(response.value); } catch (error) { view.error = 'The response is not valid JSON.'; render(); return; }
        view.busy = true; render();
        request(canvasPath('synthesis/host-agent-response'), 'POST', payload).then(function () {
          view.busy = false; view.error = null; view.responseText = ''; say('The synthesis is stored beside its request. Nothing is applied.');
          return load();
        }).catch(function (error) {
          view.busy = false; view.error = error.message; say('The owner refused this response: ' + error.message, true); render();
        });
      });
      box.appendChild(submit);
      return box;
    }

    function renderTrajectory(result) {
      var block = el('section', 'synthesis-trajectory');
      block.appendChild(el('h4', 'synthesis-heading', 'The trajectory'));
      block.appendChild(el('p', 'synthesis-note', 'Stages follow developmental dependency. A Book number places a stage; it does not claim chronology unless the record states it.'));
      var list = el('ol', 'synthesis-stages');
      result.trajectory.forEach(function (stage, index) {
        var item = el('li', 'synthesis-stage');
        item.id = 'synthesis-stage-' + (index + 1);
        var head = el('p', 'synthesis-stage-head');
        head.appendChild(el('span', 'synthesis-stage-ref', 's' + (index + 1)));
        head.appendChild(document.createTextNode(' '));
        head.appendChild(el('span', 'synthesis-stage-place',
          stage.horizon === 'existing_book' ? 'Book ' + stage.book : 'Beyond the existing Books'));
        head.appendChild(document.createTextNode(' · '));
        head.appendChild(chip(BASIS[stage.basis] || stage.basis, stage.basis === 'recorded' ? 'ok' : 'note'));
        item.appendChild(head);
        item.appendChild(el('p', 'synthesis-stage-development', stage.development));
        item.appendChild(labelledLine('Becomes available', stage.becomes_available));
        item.appendChild(labelledLine('What it changes', stage.changes));
        if (stage.quote) item.appendChild(labelledLine('Quoted basis', '“' + stage.quote + '”'));
        item.appendChild(el('p', 'synthesis-stage-horizon', HORIZON[stage.horizon] || stage.horizon));
        list.appendChild(item);
      });
      block.appendChild(list);
      return block;
    }

    function labelledLine(label, text) {
      var p = el('p', 'synthesis-line');
      p.appendChild(el('span', 'synthesis-line-label', label + ': '));
      p.appendChild(document.createTextNode(text));
      return p;
    }

    function renderRelations(result) {
      var block = el('section', 'synthesis-relations');
      block.appendChild(el('h4', 'synthesis-heading', 'Relations among them'));
      if (!result.relations || !result.relations.length) {
        block.appendChild(el('p', 'synthesis-note', 'The synthesis states no relation between them.'));
        return block;
      }
      var list = el('ul', 'synthesis-list');
      result.relations.forEach(function (relation) {
        var item = el('li', 'synthesis-relation');
        item.appendChild(chip(words(RELATION, relation.kind), relation.kind === 'prerequisite' ? 'warn' : 'note'));
        item.appendChild(document.createTextNode(' '));
        item.appendChild(el('span', 'synthesis-between', relation.between.join(' with ')));
        item.appendChild(document.createTextNode(' — ' + words(DEPENDENCE, relation.dependence) + '. ' + relation.reason));
        if (relation.quote) item.appendChild(el('p', 'synthesis-quote', '“' + relation.quote + '”'));
        list.appendChild(item);
      });
      block.appendChild(list);
      return block;
    }

    function renderCulmination(culmination) {
      var block = el('section', 'synthesis-culmination-block');
      block.appendChild(el('h4', 'synthesis-heading', 'Culmination'));
      block.appendChild(el('p', 'synthesis-stage-development', culmination.statement));
      [['Necessary preparation', culmination.necessary], ['Optional enrichment', culmination.enrichment]].forEach(function (pair) {
        if (!pair[1] || !pair[1].length) return;
        block.appendChild(el('p', 'synthesis-line-label', pair[0]));
        var list = el('ul', 'synthesis-list');
        pair[1].forEach(function (condition) { list.appendChild(el('li', 'synthesis-condition', condition.text)); });
        block.appendChild(list);
      });
      block.appendChild(labelledLine('If it never arrives', culmination.standalone_value));
      return block;
    }

    function renderAlternatives(result) {
      var block = el('section', 'synthesis-alternatives');
      block.appendChild(el('h4', 'synthesis-heading', 'If the order or the condition changes'));
      var list = el('ul', 'synthesis-list');
      result.alternative_paths.forEach(function (path) {
        var item = el('li', 'synthesis-alternative');
        item.appendChild(chip(words(VIABILITY, path.viability), path.viability === 'closed' ? 'warn' : 'note'));
        item.appendChild(document.createTextNode(' '));
        item.appendChild(el('span', 'synthesis-ordering', path.ordering));
        item.appendChild(el('p', 'synthesis-effect', path.effect));
        list.appendChild(item);
      });
      block.appendChild(list);
      return block;
    }

    function renderOpportunities(result) {
      var block = el('section', 'synthesis-opportunities');
      block.appendChild(el('h4', 'synthesis-heading', 'What their interaction makes possible'));
      var list = el('ul', 'synthesis-list');
      result.opportunities.forEach(function (opportunity) {
        list.appendChild(el('li', 'synthesis-opportunity', opportunity.between.join(' with ') + ': ' + opportunity.text));
      });
      block.appendChild(list);
      return block;
    }

    function renderOpenWork(result) {
      var block = el('section', 'synthesis-open');
      block.appendChild(labelledLine('The reader’s experience', result.reader_experience));
      if (result.open_decisions && result.open_decisions.length) {
        block.appendChild(el('p', 'synthesis-line-label', 'Left open for the author'));
        var open = el('ul', 'synthesis-list');
        result.open_decisions.forEach(function (text) { open.appendChild(el('li', 'synthesis-open-item', text)); });
        block.appendChild(open);
      }
      if (result.uncertainty && result.uncertainty.length) {
        block.appendChild(el('p', 'synthesis-line-label', 'Not established by the record'));
        var doubt = el('ul', 'synthesis-list');
        result.uncertainty.forEach(function (text) { doubt.appendChild(el('li', 'synthesis-uncertainty', text)); });
        block.appendChild(doubt);
      }
      if (result.criticism_assessments && result.criticism_assessments.length) {
        block.appendChild(el('p', 'synthesis-line-label', 'Criticism weighed'));
        var verdicts = el('ul', 'synthesis-list');
        result.criticism_assessments.forEach(function (row) {
          verdicts.appendChild(el('li', 'synthesis-verdict', row.criticism + ': ' + words(VERDICT, row.verdict) + '. ' + row.reason));
        });
        block.appendChild(verdicts);
      }
      if (result.changes_from_prior && result.changes_from_prior.length) {
        block.appendChild(el('p', 'synthesis-line-label', 'Changed from the earlier judgement'));
        var changes = el('ul', 'synthesis-list');
        result.changes_from_prior.forEach(function (text) { changes.appendChild(el('li', 'synthesis-change', text)); });
        block.appendChild(changes);
      }
      return block;
    }

    function renderEvidence(projection) {
      var details = el('details', 'synthesis-evidence');
      details.appendChild(el('summary', 'synthesis-summary', 'Evidence this synthesis read'));
      var coverage = projection.coverage;
      if (coverage) {
        var counts = coverage.elements_read + ' Working Book elements read in ' + (coverage.books_read || []).length + ' Books.';
        details.appendChild(el('p', 'synthesis-note', counts));
      }
      var list = el('ul', 'synthesis-evidence-list');
      (projection.evidence || []).forEach(function (item) {
        if (item.kind === 'coverage') return;
        var row = el('li', 'synthesis-evidence-item');
        row.appendChild(el('span', 'synthesis-evidence-id', item.id));
        row.appendChild(document.createTextNode(' '));
        row.appendChild(el('span', 'synthesis-evidence-kind', words(EVIDENCE_KIND, item.kind, item.kind)));
        row.appendChild(document.createTextNode(' · ' + item.owner + ' · ' + item.freshness.replace(/_/g, ' ')
          + (item.truncated ? ' · excerpt' : '')));
        row.appendChild(el('p', 'synthesis-evidence-text', item.text));
        list.appendChild(row);
      });
      details.appendChild(list);
      return details;
    }

    function renderFollowUp(projection) {
      var block = el('section', 'synthesis-follow');
      var button = el('button', 'synthesis-continue', 'Criticise or continue from this synthesis');
      button.type = 'button';
      button.setAttribute('data-synthesis', 'continue');
      button.addEventListener('click', function () {
        view.followUp = true; view.question = ''; view.criticism = ''; render();
      });
      block.appendChild(button);
      return block;
    }

    function renderHistory(projection) {
      var details = el('details', 'synthesis-history');
      details.appendChild(el('summary', 'synthesis-summary', 'Earlier syntheses'));
      var list = el('ul', 'synthesis-list');
      projection.history.slice(1).forEach(function (row) {
        var standing = STANDING[row.standing] || {label: row.standing};
        list.appendChild(el('li', 'synthesis-history-item', (row.inputs && row.inputs.question ? row.inputs.question : row.request_sha256.slice(0, 12))
          + ' — ' + (row.standing || 'unread') + '. ' + standing.label));
      });
      details.appendChild(list);
      return details;
    }

    // Derived changes: what the owner finds different between this answer and the one it follows (a follow-up only).
    function renderDerivedChanges(projection) {
      var derived = projection.changes_derived;
      if (!derived) return null;
      var details = el('details', 'synthesis-derived');
      details.appendChild(el('summary', 'synthesis-summary', 'What changed between the two answers, derived by the owner (' +
        derived.changes.length + ' items)'));
      details.appendChild(el('p', 'synthesis-note', derived.note));
      var list = el('ul', 'synthesis-list');
      derived.changes.forEach(function (change) {
        var kind = change.kind.replace(/_/g, ' ');
        var text = kind.charAt(0).toUpperCase() + kind.slice(1) + (change.ref ? ' · ' + change.ref : '') +
          (change.detail ? ' — ' + change.detail : '');
        list.appendChild(el('li', 'synthesis-derived-item', text));
      });
      details.appendChild(list);
      return details;
    }

    // Claim-basis checks: a fresh agent judges one claim of this synthesis against the evidence it read. Advisory; nothing is applied.
    function claimText(item) {
      var w = item.wording || {};
      return w.development || w.text || w.reason || w.ordering || w.statement || '';
    }
    function loadVerifications(token, projection) {
      if (!projection || !projection.request_sha256) { view.verification = null; return Promise.resolve(null); }
      return request(canvasPath('synthesis/' + projection.request_sha256 + '/verifications')).then(function (reply) {
        if (token !== loadToken) return null;
        view.verification = reply;
        // A carried judgement is offered only while its check is current; a check that has gone stale is dropped here.
        view.carried = view.carried.filter(function (sha) {
          return Object.keys(reply.claims || {}).some(function (claim) {
            var latest = reply.claims[claim].latest;
            return latest && latest.request_sha256 === sha && latest.standing === 'current';
          });
        });
        return null;
      }).catch(function () { if (token === loadToken) view.verification = null; });
    }
    function latestCheck(claim) {
      var entry = view.verification && view.verification.claims ? view.verification.claims[claim] : null;
      return entry ? entry.latest : null;
    }
    function renderBasisChecks(projection) {
      var block = el('section', 'synthesis-basis');
      block.appendChild(el('h4', 'synthesis-heading', 'Check a claim’s basis'));
      block.appendChild(el('p', 'synthesis-note', 'A fresh agent judges one claim against the exact evidence this synthesis read. ' +
        'The judgement is advisory: nothing is applied, and you may disagree with it.'));
      var inventory = view.verification && view.verification.inventory ? view.verification.inventory : [];
      if (!inventory.length) { block.appendChild(el('p', 'synthesis-note', 'No claims to check.')); return block; }
      var list = el('ol', 'synthesis-basis-list');
      inventory.forEach(function (claim) { list.appendChild(renderClaimCheck(projection, claim)); });
      block.appendChild(list);
      return block;
    }
    function renderClaimCheck(projection, claim) {
      var item = el('li', 'synthesis-claim-check');
      item.setAttribute('data-claim', claim.claim);
      var head = el('p', 'synthesis-claim-head');
      head.appendChild(el('span', 'synthesis-stage-ref', claim.claim));
      head.appendChild(document.createTextNode(' '));
      head.appendChild(el('span', 'synthesis-claim-kind', CLAIM_KIND[claim.kind] || claim.kind));
      if (claim.basis) {
        head.appendChild(document.createTextNode(' · '));
        head.appendChild(chip(BASIS[claim.basis] || claim.basis, claim.basis === 'recorded' ? 'ok' : 'note'));
      }
      if (claim.load_bearing) {
        head.appendChild(document.createTextNode(' '));
        head.appendChild(chip('Others depend on it', 'warn'));
      }
      item.appendChild(head);
      item.appendChild(el('p', 'synthesis-claim-text', claimText(claim)));
      var latest = latestCheck(claim.claim);
      if (latest && latest.status === 'ready' && latest.result) item.appendChild(renderVerdict(claim, latest));
      else if (latest && latest.status === 'awaiting_host_agent' && latest.request) item.appendChild(renderClaimAwaiting(claim, latest));
      else {
        var button = el('button', 'synthesis-check', latest ? 'Check this claim again' : 'Check this claim');
        button.type = 'button';
        button.setAttribute('data-claim-check', claim.claim);
        button.addEventListener('click', function () { prepareClaim(projection, claim.claim); });
        item.appendChild(button);
      }
      return item;
    }
    function prepareClaim(projection, claim) {
      if (view.busy) return;
      view.busy = true; view.error = null; render();
      say('Preparing the claim check for your coding agent…');
      request(canvasPath('synthesis/' + projection.request_sha256 + '/verifications/prepare'), 'POST', {claim: claim})
        .then(function (prepared) {
          view.busy = false;
          view.verification = view.verification || {claims: {}, inventory: []};
          view.verification.claims = view.verification.claims || {};
          view.verification.claims[claim] = {latest: prepared.verification, earlier: 0};
          say('Claim ' + claim + ' is prepared. Your coding agent answers the request below; nothing is applied.');
          render();
        }).catch(function (error) {
          view.busy = false; view.error = error.message; say('The claim was not prepared: ' + error.message, true); render();
        });
    }
    function renderClaimAwaiting(claim, latest) {
      var key = claim.claim;
      // Drafts belong to the request they answer, so a pasted response cannot land under another synthesis's claim of the same name.
      var draftKey = latest.request_sha256;
      var box = el('div', 'synthesis-claim-awaiting');
      box.appendChild(el('p', 'synthesis-note', 'Awaiting your coding agent for ' + key + '. Request fingerprint ' +
        latest.request_sha256.slice(0, 16) + '…'));
      var text = el('textarea', 'synthesis-request');
      text.readOnly = true; text.rows = 4; text.value = JSON.stringify(latest.request, null, 2);
      text.setAttribute('aria-label', 'Verification request for claim ' + key);
      box.appendChild(text);
      var response = el('textarea', 'synthesis-response synthesis-claim-response');
      response.rows = 3;
      // Kept in the panel's state, so a refusal leaves the pasted response in place to correct.
      response.value = view.claimDrafts[draftKey] || '';
      response.addEventListener('input', function () { view.claimDrafts[draftKey] = response.value; });
      response.setAttribute('aria-label', 'Response for claim ' + key);
      response.placeholder = 'Paste the verifier response object here';
      box.appendChild(response);
      var submit = el('button', 'synthesis-submit', 'Check agent response');
      submit.type = 'button';
      submit.setAttribute('data-claim-submit', key);
      submit.addEventListener('click', function () {
        if (!response.value.trim()) { view.error = 'Paste the agent response first.'; render(); return; }
        var payload;
        try { payload = JSON.parse(response.value); } catch (error) { view.error = 'The response is not valid JSON.'; render(); return; }
        view.busy = true; render();
        request(canvasPath('verification/host-agent-response'), 'POST', payload).then(function () {
          view.busy = false; view.error = null; delete view.claimDrafts[draftKey];
          say('The check of claim ' + key + ' is stored beside its request. Nothing is applied.');
          return load();
        }).catch(function (error) {
          view.busy = false; view.error = error.message; say('The owner refused this response: ' + error.message, true); render();
        });
      });
      box.appendChild(submit);
      return box;
    }
    function renderVerdict(claim, latest) {
      var v = latest.result;
      var box = el('div', 'synthesis-verdict-box');
      var tone = v.judgment === 'supported' || v.judgment === 'defensible_inference' ? 'ok'
        : (v.judgment === 'creative_speculation' ? 'note' : 'warn');
      box.appendChild(chip(words(JUDGMENT, v.judgment), tone));
      box.appendChild(document.createTextNode(' '));
      box.appendChild(chip(words(REGISTER, v.evidence_register), 'note'));
      if (latest.standing !== 'current') {
        box.appendChild(document.createTextNode(' '));
        box.appendChild(chip('Stale: the evidence has changed since this check', 'warn'));
      }
      box.appendChild(el('p', 'synthesis-verdict-reasoning', v.reasoning));
      if (v.alternative_reading) box.appendChild(labelledLine('What the evidence does support', v.alternative_reading));
      if (v.would_settle) box.appendChild(labelledLine('What would settle it', v.would_settle));
      box.appendChild(labelledLine('What stays creatively open', v.creative_room));
      if (v.quote) box.appendChild(el('p', 'synthesis-quote', '“' + v.quote + '”'));
      if (v.evidence && v.evidence.length) box.appendChild(el('p', 'synthesis-note', 'Evidence the check cites: ' + v.evidence.join(', ') + '.'));
      var carry = el('label', 'synthesis-carry');
      var choose = el('input');
      choose.type = 'checkbox';
      choose.checked = view.carried.indexOf(latest.request_sha256) >= 0;
      choose.disabled = latest.standing !== 'current';
      choose.setAttribute('data-carry', claim.claim);
      choose.addEventListener('change', function () {
        var sha = latest.request_sha256;
        if (choose.checked) {
          if (view.carried.indexOf(sha) < 0) view.carried.push(sha);
          view.carriedLabel[sha] = claim.claim + ': ' + words(JUDGMENT, v.judgment);
        } else {
          view.carried = view.carried.filter(function (item) { return item !== sha; });
        }
        say(choose.checked ? 'The check is offered as criticism for a follow-up.' : 'The check is no longer offered for a follow-up.');
      });
      carry.appendChild(choose);
      carry.appendChild(document.createTextNode(' Offer this judgement as criticism for a follow-up'));
      box.appendChild(carry);
      return box;
    }

    return {load: load, reset: reset, render: render};
  }

  global.AuteurStudioSynthesis = {createSynthesisPanel: createSynthesisPanel};
})(window);
