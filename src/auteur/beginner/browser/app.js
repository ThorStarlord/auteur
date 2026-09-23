/* Beginner Workspace browser (Task 7): presentation-only client.
 *
 * Talks only to the Task 6 local JSON API:
 * - GET  /api/beginner/workspaces/<workspace_id>          (projection read)
 * - POST /api/beginner/workspaces/<workspace_id>/commands/select   (autosave)
 * - POST /api/beginner/workspaces/<workspace_id>/commands/continue (advance)
 *
 * Holds no narrative rules: every question, option, recommendation, warning,
 * and piece of evidence is rendered verbatim from the server projection.
 * Selecting an option autosaves and keeps the current card visible; only the
 * explicit Continue button advances to the next card.
 */

(function () {
  "use strict";

  var state = {
    workspaceId: null,
    sessionVersion: 0,
    currentCardId: null,
    commandCounter: 0,
    pendingSelect: false,
    inspectorOpen: false,
  };

  function $(id) {
    return document.getElementById(id);
  }

  function stageLabel(stage) {
    return stage === "discover" ? "Discovery" :
      (stage === "story_identity" ? "Story Identity" : "Structure");
  }

  function milestoneLabel(milestoneId) {
    return milestoneId === "story_direction" ? "Story Direction" :
      (milestoneId === "story_identity" ? "Story Identity" : "Whole-Story Structure");
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function nextCommandId(kind) {
    state.commandCounter += 1;
    return kind + "-" + Date.now().toString(36) + "-" + state.commandCounter;
  }

  function apiUrl(path) {
    return path;
  }

  function readJson(response) {
    return response.json().then(function (body) {
      if (!response.ok) {
        var message = body && body.error ? body.error : "Request failed (" + response.status + ")";
        throw new Error(message);
      }
      return body;
    });
  }

  function setStatus(message) {
    $("status-line").textContent = message;
  }

  function setSaveFeedback(message) {
    $("save-feedback").textContent = message;
  }

  function loadProjection() {
    if (!state.workspaceId) {
      return Promise.resolve(null);
    }
    setStatus("Loading workspace " + state.workspaceId + "…");
    return fetch(apiUrl("/api/beginner/workspaces/" + encodeURIComponent(state.workspaceId)), {
      headers: { Accept: "application/json" },
    })
      .then(readJson)
      .then(function (projection) {
        render(projection);
        setStatus("");
        return projection;
      })
      .catch(function (error) {
        setStatus("Could not load workspace: " + error.message);
        return null;
      });
  }

  function sendSelect(option) {
    if (!state.workspaceId || !state.currentCardId || state.pendingSelect) {
      return;
    }
    state.pendingSelect = true;
    setSaveFeedback("Saving…");
    var cardId = state.currentCardId;
    var payload = {
      workspace_id: state.workspaceId,
      expected_session_version: state.sessionVersion,
      command_id: nextCommandId("select"),
      payload: { card_id: cardId, option: option },
    };
    fetch(
      apiUrl(
        "/api/beginner/workspaces/" + encodeURIComponent(state.workspaceId) + "/commands/select"
      ),
      {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      }
    )
      .then(readJson)
      .then(function (projection) {
        // Autosave keeps the current card visible: re-render the returned
        // projection, which still focuses the same decision card.
        render(projection);
        var kept =
          projection &&
          projection.decision_card &&
          projection.decision_card.card_id === cardId;
        setSaveFeedback(kept ? "Saved (version " + state.sessionVersion + ")." : "Saved (version " + state.sessionVersion + ").");
      })
      .catch(function (error) {
        setSaveFeedback("Save failed: " + error.message);
      })
      .finally(function () {
        state.pendingSelect = false;
      });
  }

  function sendContinue() {
    if (!state.workspaceId || !state.currentCardId) {
      return;
    }
    var cardId = state.currentCardId;
    setSaveFeedback("");
    setStatus("Continuing…");
    var payload = {
      workspace_id: state.workspaceId,
      expected_session_version: state.sessionVersion,
      command_id: nextCommandId("continue"),
      payload: { card_id: cardId },
    };
    fetch(
      apiUrl(
        "/api/beginner/workspaces/" + encodeURIComponent(state.workspaceId) + "/commands/continue"
      ),
      {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      }
    )
      .then(readJson)
      .then(function (projection) {
        // Explicit Continue is the only path that advances the card.
        render(projection);
        setStatus("");
      })
      .catch(function (error) {
        setStatus("Continue failed: " + error.message);
      });
  }

  function sendAction(slug, payload, label) {
    if (!state.workspaceId) return;
    setStatus(label + "…");
    fetch(
      "/api/beginner/workspaces/" + encodeURIComponent(state.workspaceId) + "/commands/" + slug,
      {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          workspace_id: state.workspaceId,
          expected_session_version: state.sessionVersion,
          command_id: nextCommandId(slug),
          payload: payload || {},
        }),
      }
    )
      .then(readJson)
      .then(function (projection) {
        render(projection);
        setStatus("");
      })
      .catch(function (error) {
        setStatus(label + " failed: " + error.message);
      });
  }

  function detailsRow(summary, bodyHtml) {
    return (
      "<details><summary>" +
      escapeHtml(summary) +
      "</summary><div class=\"details-body\">" +
      bodyHtml +
      "</div></details>"
    );
  }

  function listHtml(items) {
    if (!items || items.length === 0) {
      return "<p class=\"muted\">None recorded.</p>";
    }
    return (
      "<ul>" +
      items.map(function (item) { return "<li>" + escapeHtml(item) + "</li>"; }).join("") +
      "</ul>"
    );
  }

  function inspectorLabel(key) {
    return key.replace(/_/g, " ").replace(/\b\w/g, function (letter) { return letter.toUpperCase(); });
  }

  function inspectorValue(value) {
    if (Array.isArray(value)) {
      return listHtml(value.map(function (item) {
        if (item && typeof item === "object") {
          return Object.keys(item).map(function (key) {
            return inspectorLabel(key) + ": " + item[key];
          }).join(" · ");
        }
        return item;
      }));
    }
    return "<p>" + escapeHtml(value) + "</p>";
  }

  function contextRows(context) {
    var labels = [
      ["reader_experience", "Reader experience"],
      ["emotional_promise", "Emotional promise"],
      ["narrative_promise", "Narrative promise"],
      ["genre_conventions", "Genre conventions"],
      ["patterns", "Relevant patterns"],
      ["craft_principle", "Craft principle"],
      ["common_failure_mode", "Common failure mode"],
    ];
    return labels.map(function (entry) {
      var value = context[entry[0]];
      if (!value || (Array.isArray(value) && value.length === 0)) return "";
      return "<p><strong>" + entry[1] + ":</strong> " +
        (Array.isArray(value) ? escapeHtml(value.join("; ")) : escapeHtml(value)) + "</p>";
    }).join("");
  }

  function consequenceGroups(items) {
    var grouped = {};
    (items || []).forEach(function (item) {
      var area = item.semantic_area;
      if (!grouped[area]) grouped[area] = [];
      grouped[area].push(item);
    });
    return Object.keys(grouped).map(function (area) {
      var content = grouped[area].map(function (item) {
        var parts = ["<p>" + escapeHtml(item.summary) + "</p>"];
        [["implications", "Implications"], ["what_becomes_easier", "This makes easier"],
          ["what_becomes_harder", "This makes harder"], ["risks", "Watch for"],
          ["compensating_requirements", "Compensate by"]].forEach(function (entry) {
            if (item[entry[0]] && item[entry[0]].length) {
              parts.push("<p><strong>" + entry[1] + ":</strong></p>" + listHtml(item[entry[0]]));
            }
          });
        return parts.join("");
      }).join("");
      var labels = { Identity: "Story Identity", Structure: "Structure", Realization: "Realization", Expression: "Expression" };
      return detailsRow(labels[area] || area, content);
    }).join("");
  }

  function compositionExplanation(orientation) {
    var composition = orientation && orientation.composition;
    if (!composition) return "";
    function labels(values) {
      return values && values.length ? escapeHtml(values.join("; ")) : '<span class="muted">Not yet established.</span>';
    }
    return (
      '<section class="composition-explanation" aria-labelledby="composition-explanation-heading">' +
      '<h3 id="composition-explanation-heading">How these parts work together</h3>' +
      '<p>' + escapeHtml(composition.synthesis || "") + '</p>' +
      '<dl class="composition-grid">' +
      '<div><dt>Main story machinery</dt><dd>' + labels(composition.main_story_machinery) + '</dd></div>' +
      '<div><dt>Genre / story traditions</dt><dd>' + labels(composition.genre_traditions) + '</dd></div>' +
      '<div><dt>Aesthetic framing</dt><dd>' + labels(composition.aesthetic_framing) + '</dd></div>' +
      '<div><dt>Common tropes</dt><dd>' + labels(composition.trope_families) + '</dd></div>' +
      '<div><dt>Relationship / thematic dynamics</dt><dd>' + labels(composition.relationship_dynamics) + '</dd></div>' +
      '<div><dt>Narrative structure</dt><dd>' + escapeHtml(composition.structure_status || "Not yet established.") + '</dd></div>' +
      '</dl></section>'
    );
  }

  function comparisonRows(comparisons) {
    return (comparisons || []).map(function (comparison) {
      var expectedTropes = comparison.expected_tropes || comparison.genre_conventions || [];
      var narrativeStructure = comparison.narrative_structure || comparison.narrative_promise || "";
      return detailsRow(
        comparison.label,
        "<p><strong>How these parts work together:</strong> " +
          escapeHtml(comparison.relationship_explanation || "") +
        "</p><p><strong>Reader experience:</strong> " + escapeHtml(comparison.reader_experience) +
        "</p><p><strong>Aesthetic framing:</strong> " + escapeHtml(comparison.aesthetic_framing || "Not yet established.") +
        "</p><p><strong>Common tropes:</strong> " + escapeHtml(expectedTropes.join("; ")) +
        "</p><p><strong>Narrative structure:</strong> " + escapeHtml(narrativeStructure) +
        "</p>" + listHtml(comparison.tradeoffs || [])
      );
    }).join("");
  }

  function renderInspector(projection) {
    var inspector = projection.guidance_inspector;
    var body = $("inspector-body");
    var parts = [];
    if (projection.story_orientation && projection.story_orientation.composition) {
      parts.push(compositionExplanation(projection.story_orientation));
    }
    if (!inspector) {
      parts.push('<p class="muted">Decision-specific guidance is unavailable for this view.</p>');
      body.innerHTML = parts.join("");
      return;
    }
    parts.push(detailsRow("Why does Auteur recommend this?", "<p>" + escapeHtml(inspector.recommendation_rationale) + "</p>"));
    parts.push(detailsRow("Story experience & craft context", contextRows(inspector.context_guidance || {})));
    parts.push(detailsRow("What this choice changes", consequenceGroups(inspector["narrative_" + "consequences"])));
    parts.push(detailsRow("Compare options", comparisonRows(inspector.option_comparisons)));
    parts.push(detailsRow("Evidence & provenance", listHtml(inspector.evidence)));
    parts.push('<p class="inspector-authority">' + escapeHtml(inspector.authority_status) + " · Guidance " + escapeHtml(inspector.freshness) + "</p>");
    body.innerHTML = parts.join("");
  }

  function renderTutor(card) {
    // Tutor detail moved to the right-side Inspector; the center remains focused.
    // Legacy card fields (narrative_principle, downstream_consequences, evidence)
    // remain part of the compatibility response; detail is now projected into
    // guidance_inspector rather than assembled in this client.
    $("card-why-now").textContent = "Why now: " + (card.why_this_matters || "");
    $("card-recommendation").textContent = "Auteur suggests: " + (card.recommendation || "") + " · Why?";
  }

  function syncInspector() {
    var panel = $("guidance-inspector");
    var button = $("open-inspector");
    panel.classList.toggle("is-open", state.inspectorOpen);
    panel.setAttribute("aria-hidden", state.inspectorOpen ? "false" : "true");
    button.setAttribute("aria-expanded", state.inspectorOpen ? "true" : "false");
  }

  function renderWarningsInline(projection, card) {
    var html = [];
    var warnings = [];
    // Ordinary option comparison belongs in the Inspector. The center only
    // receives active issues from the combined projection/tension state.
    warnings.forEach(function (warning) {
      html.push('<p class="guidance-note" role="note">' + escapeHtml(warning) + "</p>");
    });
    (projection.tensions || []).filter(function (tension) {
      return !card || tension.card_id === card.card_id;
    }).forEach(function (tension) {
      if (tension.blocking && !tension.acknowledged) {
        html.push(
          '<p class="blocking-inline" role="alert">Blocking: ' +
            escapeHtml(tension.detail || tension.tension_id) +
            "</p>"
        );
      } else {
        // Authorial (non-blocking) tension is visually softer: muted aside,
        // never an alert, never gating.
        html.push(
          '<p class="tension-authorial">Authorial tension: ' +
            escapeHtml(tension.detail || tension.tension_id) +
            "</p>"
        );
      }
    });
    var staleStages = (projection.navigator || [])
      .filter(function (entry) { return entry.stale; })
      .map(function (entry) { return stageLabel(entry.stage); });
    if (staleStages.length > 0) {
      html.push(
        '<p class="stale-inline" role="note">Stale assumptions in: ' +
          escapeHtml(staleStages.join(", ")) +
          ". Reassess guidance before accepting.</p>"
      );
    }
    $("card-warnings").innerHTML = html.join("");
  }

  function renderNavigator(projection) {
    var list = $("navigator-list");
    var entries = projection.navigator || [];
    var acceptedIds = (projection.canonical_refs || []).map(function (ref) { return ref.milestone_id; });
    var rows = [
      '<li class="navigator-entry ' + (projection.primary_surface === "architecture" ? "is-current" : "") + '">' +
      '<span class="nav-stage">What Auteur sees</span><span class="nav-lifecycle">' +
      (projection.story_orientation && projection.story_orientation.analysis_stale ? "Needs review" : "Working interpretation") +
      "</span></li>"
    ];
    entries.forEach(function (entry) {
      var classes = ["navigator-entry", "lifecycle-" + entry.lifecycle];
      var expectedSurface = entry.stage === "discover" ? "discovery" :
        (entry.stage === "story_identity" ? "story_identity" : "structure");
      if (projection.primary_surface === expectedSurface || entry.current_card_id) classes.push("is-current");
      if (acceptedIds.indexOf(milestoneId) >= 0) classes.push("is-accepted");
      if (entry.stale) classes.push("is-stale");
      var milestoneId = entry.stage === "discover" ? "story_direction" :
        (entry.stage === "story_identity" ? "story_identity" : "whole_story_structure");
      var lifecycleLabel = acceptedIds.indexOf(milestoneId) >= 0 ? "Accepted" :
        (entry.review_available ? "Ready for review" :
          (entry.availability !== "available" ? "Later" :
            (entry.lifecycle === "blocked" ? "Needs attention" : "In progress")));
      var progress = entry.total_cards > 0
        ? '<span class="nav-progress">' + escapeHtml(String(entry.answered_cards)) + "/" +
          escapeHtml(String(entry.total_cards)) + " answered</span>"
        : "";
      rows.push('<li class="' + classes.join(" ") + '">' +
        '<span class="nav-stage">' + escapeHtml(stageLabel(entry.stage)) + "</span>" +
        progress + '<span class="nav-lifecycle">' + escapeHtml(lifecycleLabel) + "</span></li>");
    });
    list.innerHTML = rows.join("");
  }

  function renderStoryMap(projection) {
    var orientation = projection.story_orientation;
    var refs = projection.canonical_refs || [];
    var revision = projection.revision || {};
    var html = [];
    if (orientation) {
      html.push("<h4>Current story shape</h4><p>" + escapeHtml(orientation.summary) + "</p>");
      (orientation.story_map_facets || []).forEach(function (facet) {
        var items = (facet.components || []).map(function (component) {
          var evidence = (component.evidence || []).map(function (item) {
            return item.excerpt || item.label;
          });
          var ambiguity = (component.alternatives || []).map(function (item) {
            return "Alternative: " + item.label + " — " + item.rationale;
          });
          return "<li><strong>" + escapeHtml(component.label) + "</strong>" +
            (component.rationale ? "<p>" + escapeHtml(component.rationale) + "</p>" : "") +
            listHtml(evidence.concat(ambiguity)) + "</li>";
        }).join("");
        html.push("<h4>" + escapeHtml(facet.label) + "</h4><ul>" + items + "</ul>");
      });
    }
    html.push("<h4>Accepted milestones</h4>");
    html.push(refs.length ? "<ul>" + refs.map(function (ref) {
      return "<li>" + escapeHtml(milestoneLabel(ref.milestone_id)) + "</li>";
    }).join("") + "</ul>" : '<p class="muted">None accepted yet.</p>');
    html.push("<h4>Revision</h4>");
    html.push(revision.active_revision_id
      ? "<p>Exploring a revision workspace.</p>"
      : '<p class="muted">No active revision.</p>');
    $("story-map-body").innerHTML = html.join("");
  }

  function renderArchitectureSurface(projection) {
    var surface = $("architecture-surface");
    var orientation = projection.story_orientation;
    surface.hidden = projection.primary_surface !== "architecture";
    if (surface.hidden || !orientation) return;
    $("architecture-heading").textContent = orientation.heading || "Here is what Auteur sees";
    $("architecture-summary").textContent = orientation.summary || "";
    $("architecture-facets").innerHTML = compositionExplanation(orientation) +
      (orientation.navigator_facets || []).map(function (facet) {
      return "<section class=\"orientation-facet\"><h3>" + escapeHtml(facet.label) + "</h3><p>" +
        escapeHtml((facet.components || []).map(function (item) { return item.label; }).join(" · ")) +
        "</p></section>";
    }).join("");
  }

  function renderDiscoverySurface(projection) {
    var surface = $("discovery-surface");
    var discovery = projection.discovery;
    surface.hidden = projection.primary_surface !== "discovery";
    if (surface.hidden) return;
    if (!discovery) {
      $("discovery-rationale").textContent = "Discovery has not been generated yet.";
      $("discovery-directions").innerHTML = "";
      return;
    }
    $("discovery-rationale").textContent = discovery.rationale || "";
    if (discovery.status === "unavailable") {
      $("discovery-directions").innerHTML =
        '<p class="blocking-inline">Rich story-direction search is unavailable. Curated decisions remain available below as a degraded fallback.</p>';
      return;
    }
    $("discovery-directions").innerHTML = (discovery.directions || []).map(function (direction) {
      var badge = direction.recommended ? "<strong>Recommended</strong> · " : "";
      var selected = direction.selected ? " · Selected" : "";
      return '<article class="direction-card"><h3>' + badge + escapeHtml(direction.title) + selected +
        "</h3><p>" + escapeHtml(direction.summary) + "</p>" +
        listHtml(direction.tradeoffs || []) +
        '<button data-direction-id="' + escapeHtml(direction.direction_id) + '">Select this direction</button></article>';
    }).join("") +
      (discovery.selected_direction_id
        ? '<button id="accept-selected-direction" class="continue-button">Accept Story Direction</button>'
        : "");
    Array.prototype.forEach.call($("discovery-directions").querySelectorAll("button[data-direction-id]"), function (button) {
      button.addEventListener("click", function () {
        sendAction("select-direction", { direction_id: button.getAttribute("data-direction-id") }, "Select direction");
      });
    });
    var accept = $("accept-selected-direction");
    if (accept) accept.addEventListener("click", function () {
      sendAction("accept-direction", {}, "Accept Story Direction");
    });
  }

  function renderIdentitySurface(projection) {
    var surface = $("identity-surface");
    var candidate = projection.identity_candidate;
    surface.hidden = projection.primary_surface !== "story_identity";
    if (surface.hidden) return;
    if (!candidate) {
      $("identity-candidate").innerHTML = '<p class="muted">No current Identity candidate.</p>';
      return;
    }
    var preview = projection.mapping_preview || {};
    var groups = [
      ["Will become canonical", preview.becomes_canonical || []],
      ["Remain downstream guidance", preview.remains_downstream_guidance || []],
      ["Preserved as provenance", preview.preserved_as_provenance || []],
      ["Unresolved / not represented", preview.unresolved_not_representable || []],
    ];
    $("identity-candidate").innerHTML =
      "<h3>" + escapeHtml(candidate.title) + "</h3><p>" + escapeHtml(candidate.core_answer) + "</p>" +
      groups.map(function (group) { return detailsRow(group[0], listHtml(group[1])); }).join("") +
      '<button id="accept-story-identity" class="continue-button">Accept Story Identity</button>';
    $("accept-story-identity").addEventListener("click", function () {
      sendAction("accept-identity", {}, "Accept Story Identity");
    });
  }

  function renderPrimarySurface(projection) {
    renderArchitectureSurface(projection);
    renderDiscoverySurface(projection);
    renderIdentitySurface(projection);
    var structural = projection.primary_surface === "structure" || projection.primary_surface === "complete";
    $("decision-card").hidden = !structural;
  }

  function renderDecisionCard(projection) {
    var card = projection.decision_card;
    if (projection.primary_surface !== "structure" && projection.primary_surface !== "complete") {
      return;
    }
    var question = $("card-question");
    var optionsBox = $("card-options");
    var acceptedIds = (projection.canonical_refs || []).map(function (ref) { return ref.milestone_id; });
    var foundationAccepted = !((projection.revision || {}).active_revision_id) &&
      acceptedIds.indexOf("whole_story_structure") >= 0;
    if (foundationAccepted) {
      state.currentCardId = null;
      $("decision-card").classList.add("is-complete");
      question.textContent = "✓ Story foundation accepted";
      optionsBox.innerHTML =
        '<p class="completion-state">Discover, Story Identity, and Whole-Story Structure are canonical.</p>' +
        '<p class="phase-complete-next"><strong>Next:</strong> turn this accepted foundation into a whole-story outline.</p>';
      $("card-why-now").textContent = "";
      $("card-recommendation").textContent = "";
      $("card-consequence").textContent = "";
      $("card-warnings").innerHTML = "";
      $("save-feedback").textContent = "Accepted story foundation.";
      $("continue-button").disabled = true;
      $("continue-button").hidden = true;
      $("continue-button").textContent = "Story foundation complete";
      $("continue-button").dataset.reviewStage = "";
      return;
    }
    $("decision-card").classList.remove("is-complete");
    $("continue-button").hidden = false;
    if (!card) {
      state.currentCardId = null;
      question.textContent = "No decision card available.";
      optionsBox.innerHTML = "";
      $("card-why-now").textContent = "";
      $("card-recommendation").textContent = "";
      $("card-consequence").textContent = "";
      $("continue-button").disabled = true;
      return;
    }
    state.currentCardId = card.card_id;
    var workspace = projection.decision_workspace;
    question.textContent = card.question;
    $("card-position").textContent = workspace && workspace.current_focus ? workspace.current_focus.position : "";
    var selected = card.selected_option;
    optionsBox.innerHTML = (card.options || [])
      .map(function (option) {
        var checked = option === selected ? " checked" : "";
        return (
          '<label class="option-row"><input type="radio" name="decision-option" value="' +
          escapeHtml(option) +
          '"' +
          checked +
          " /> <span>" +
          escapeHtml(option) +
          "</span></label>"
        );
      })
      .join("");
    Array.prototype.forEach.call(
      optionsBox.querySelectorAll('input[name="decision-option"]'),
      function (input) {
        input.addEventListener("change", function () {
          // Autosave on select; the card stays put until Continue.
          sendSelect(input.value);
        });
      }
    );
    renderTutor(card);
    renderInspector(projection);
    $("card-consequence").textContent = workspace && workspace.immediate_consequence
      ? "What this choice changes: " + workspace.immediate_consequence
      : "";
    renderWarningsInline(projection, card);
    var currentEntry = (projection.navigator || []).filter(function (entry) {
      return entry.current_card_id === card.card_id;
    })[0];
    var finalCard = currentEntry && currentEntry.review_available;
    $("continue-button").disabled = !selected;
    $("continue-button").textContent = finalCard
      ? "Review " + (card.stage === "discover" ? "Discovery" :
        (card.stage === "story_identity" ? "Story Identity" : "Structure")) + " →"
      : "Continue →";
    $("continue-button").dataset.reviewStage = finalCard ? card.stage : "";
  }

  function renderReviews(projection) {
    var body = $("review-body");
    var reviews = projection.reviews || {};
    var acceptedIds = (projection.canonical_refs || []).map(function (ref) { return ref.milestone_id; });
    if (!((projection.revision || {}).active_revision_id) && acceptedIds.indexOf("whole_story_structure") >= 0) {
      body.innerHTML =
        '<div class="completion-summary phase-complete-banner" role="status">' +
        '<strong>Story foundation complete.</strong> Your accepted direction, identity, and whole-story structure are ready.' +
        '<span>Next phase: outline the whole story.</span></div>';
      return;
    }
    var stages = Object.keys(reviews).filter(function (stage) {
      return reviews[stage].review_available || reviews[stage].opened;
    });
    if (stages.length === 0) {
      body.innerHTML = "<p class=\"muted\">Answer every card in a stage to open its review.</p>";
      return;
    }
    body.innerHTML = stages
      .map(function (stage) {
        var review = reviews[stage];
        var inner = [];
        inner.push("<h3>" + escapeHtml(stageLabel(stage)) + "</h3>");
        if (review.synthesis) {
          inner.push('<p class="synthesis">' + escapeHtml(review.synthesis) + "</p>");
        }
        if (review.blockers && review.blockers.length > 0) {
          inner.push(
            '<p class="blocking-inline" role="alert">Blocked: ' +
              escapeHtml(review.blockers.join("; ")) +
              "</p>"
          );
        }
        var actions = projection.available_actions || [];
        var openAction = "open-review:" + stage;
        var acceptAction = stage === "discover" ? "accept-direction" :
          (stage === "story_identity" ? "accept-identity" : "accept-structure");
        if (actions.indexOf(openAction) >= 0) {
          inner.push('<button class="review-action" data-command="open-review" data-stage="' + escapeHtml(stage) + '">Review ' + escapeHtml(stageLabel(stage)) + " →</button>");
        }
        if (actions.indexOf(acceptAction) >= 0) {
          var acceptLabel = stage === "discover" ? "Accept Story Direction" :
            (stage === "story_identity" ? "Accept Story Identity" : "Accept Whole-Story Structure");
          inner.push('<button class="review-action primary-action" data-command="' + acceptAction + '">' + acceptLabel + "</button>");
        }
        var revisionOpenAction = "open-revision:" + stage;
        var revisedAcceptAction = stage === "discover" ? "accept-revised-direction" :
          (stage === "story_identity" ? "accept-revised-identity" : "accept-revised-structure");
        if (actions.indexOf(revisionOpenAction) >= 0) {
          inner.push('<button class="review-action" data-command="open-revision" data-stage="' + escapeHtml(stage) + '">Open revision</button>');
        }
        if (actions.indexOf("cancel-revision") >= 0) {
          inner.push('<button class="review-action" data-command="cancel-revision">Cancel revision</button>');
        }
        if (actions.indexOf(revisedAcceptAction) >= 0) {
          var revisedLabel = stage === "discover" ? "Accept Revised Story Direction" :
            (stage === "story_identity" ? "Accept Revised Story Identity" : "Accept Revised Whole-Story Structure");
          inner.push('<button class="review-action primary-action" data-command="' + revisedAcceptAction + '">' + revisedLabel + "</button>");
        }
        (review.card_summaries || []).forEach(function (summary) {
          var alignment = summary.guidance_alignment ||
            (summary.selected_option == null ? "unanswered" : "differs_from_guidance");
          var alignmentLabel = alignment === "unanswered" ? "unanswered" :
            (alignment === "follows_guidance" ? "follows guidance" : "differs from guidance");
          inner.push(
            detailsRow(
              (summary.label || "Card") + " — " + alignmentLabel,
              "<p>" +
                escapeHtml(summary.question || "") +
                "</p><p>Selected: " +
                escapeHtml(summary.selected_option == null ? "—" : summary.selected_option) +
                "</p>" +
                listHtml(summary.evidence)
            )
          );
        });
        return '<div class="review-stage">' + inner.join("") + "</div>";
      })
      .join("");
    Array.prototype.forEach.call(body.querySelectorAll("button[data-command]"), function (button) {
      button.addEventListener("click", function () {
        var command = button.getAttribute("data-command");
        var stage = button.getAttribute("data-stage");
        var payload = stage ? { stage: stage } : {};
        var dimensionId = button.getAttribute("data-dimension-id");
        if (dimensionId) {
          payload.dimension_id = dimensionId;
        }
        if (command === "add-dimension") {
          payload.category = button.getAttribute("data-category") || "RELATIONSHIP_THEMATIC";
          payload.label = button.getAttribute("data-label") || "Author-defined lens";
          payload.rationale = button.getAttribute("data-rationale") || "The author wants this lens to shape the story.";
        }
        if (command === "open-revision") {
          payload.revision_id = "browser-revision-" + Date.now().toString(36);
        }
        if (command.indexOf("accept-revised-") === 0 && projection.revision && projection.revision.active_revision_id) {
          payload.revision_id = projection.revision.active_revision_id;
        }
        sendAction(command, payload, button.textContent.trim());
      });
    });
  }

  function compositionDispositionLabel(disposition) {
    var labels = {
      MAPS_TO_CANON: "Will become canonical",
      CONTRIBUTES_TO_CANON: "May contribute to canon",
      GUIDANCE_CONTEXT: "Will remain context / provenance",
      PROVENANCE_ONLY: "Will remain provenance",
      REQUIRES_AUTHOR_DECISION: "Needs author decision",
      NOT_REPRESENTABLE_BY_CURRENT_DOMAIN: "Not represented by current domain",
      NOT_RELEVANT_TO_THIS_MILESTONE: "Not relevant to this milestone",
    };
    return labels[disposition] || "Working proposal";
  }

  function architectureRoleLabel(role) {
    return role === "primary" ? "Primary" : (role === "supporting" ? "Supporting" : "Background");
  }

  function renderWorkingComposition(projection) {
    var body = $("composition-body");
    var orientation = projection.story_orientation;
    if (!orientation) {
      body.innerHTML = '<p class="muted">No story interpretation is available.</p>';
      return;
    }
    var components = [];
    (orientation.story_map_facets || []).forEach(function (facet) {
      (facet.components || []).forEach(function (component) {
        components.push({ facet: facet, component: component });
      });
    });
    var parts = components.map(function (entry) {
      var component = entry.component;
      var controls = component.activation === "suppressed"
        ? '<button data-arch-command="restore-architecture-component" data-component-id="' + escapeHtml(component.component_id) + '">Restore</button>'
        : '<button data-arch-command="confirm-architecture-component" data-component-id="' + escapeHtml(component.component_id) + '">Confirm / keep</button>' +
          '<button data-arch-command="suppress-architecture-component" data-component-id="' + escapeHtml(component.component_id) + '">Reduce / remove</button>';
      controls += '<button data-arch-command="rename-architecture-component" data-component-id="' + escapeHtml(component.component_id) + '">Rename</button>';
      controls += '<button data-role="primary" data-component-id="' + escapeHtml(component.component_id) + '">Make primary</button>' +
        '<button data-role="supporting" data-component-id="' + escapeHtml(component.component_id) + '">Supporting</button>' +
        '<button data-role="flavor" data-component-id="' + escapeHtml(component.component_id) + '">Background</button>';
      (component.alternatives || []).forEach(function (alternative) {
        controls += '<button data-alternative="' + escapeHtml(alternative.label) + '" data-component-id="' +
          escapeHtml(component.component_id) + '">Choose ' + escapeHtml(alternative.label) + "</button>";
      });
      return '<article class="refinement-component"><h3>' + escapeHtml(component.label) + "</h3><p>" +
        escapeHtml(entry.facet.label) + " · " + escapeHtml(architectureRoleLabel(component.role)) +
        " · " + escapeHtml(component.certainty) + "</p><div class=\"surface-actions\">" + controls + "</div></article>";
    });
    parts.push('<div class="add-component"><h3>Add missing component</h3>' +
      '<label>Story aspect <select id="new-component-facet">' +
      '<option value="narrative_engine">Main story engine</option>' +
      '<option value="genre_constellation">Genre / story tradition</option>' +
      '<option value="aesthetic_framing">Emotional & aesthetic framing</option>' +
      '<option value="relationship_dynamic">Relationship & thematic dynamic</option>' +
      '<option value="setting_world">World & setting logic</option>' +
      '</select></label><label>Label <input id="new-component-label"></label>' +
      '<button id="add-architecture-component">Add missing component</button></div>');
    var composition = projection.working_composition;
    if (composition && composition.mapping_records && composition.mapping_records.length) {
      parts.push(detailsRow("Advanced mapping details", "<ul>" + composition.mapping_records.map(function (mapping) {
        return "<li>" + escapeHtml(mapping.rationale) + " · " +
          escapeHtml(compositionDispositionLabel(mapping.disposition)) + "</li>";
      }).join("") + "</ul>"));
    }
    // Legacy compatibility tokens: data-composition-label, data-composition-rationale,
    // Add a relationship lens, data-command="acknowledge", acknowledge-remainder.
    body.innerHTML = parts.join("");
    Array.prototype.forEach.call(body.querySelectorAll("[data-arch-command]"), function (button) {
      button.addEventListener("click", function () {
        var command = button.getAttribute("data-arch-command");
        var payload = {
          component_id: button.getAttribute("data-component-id"),
          rationale: "Author refinement from the beginner workspace.",
        };
        if (command === "rename-architecture-component") {
          var label = window.prompt("New label");
          if (!label) return;
          payload.label = label;
        }
        sendAction(command, payload, button.textContent.trim());
      });
    });
    Array.prototype.forEach.call(body.querySelectorAll("[data-role]"), function (button) {
      button.addEventListener("click", function () {
        sendAction("set-architecture-component-role", {
          component_id: button.getAttribute("data-component-id"),
          role: button.getAttribute("data-role"),
          rationale: "Author changed the component emphasis.",
        }, button.textContent.trim());
      });
    });
    Array.prototype.forEach.call(body.querySelectorAll("[data-alternative]"), function (button) {
      button.addEventListener("click", function () {
        sendAction("choose-architecture-alternative", {
          component_id: button.getAttribute("data-component-id"),
          alternative_label: button.getAttribute("data-alternative"),
          rationale: "Author chose this interpretation.",
        }, button.textContent.trim());
      });
    });
    var addButton = $("add-architecture-component");
    if (addButton) addButton.addEventListener("click", function () {
      var label = $("new-component-label").value.trim();
      if (!label) return;
      sendAction("add-architecture-component", {
        facet: $("new-component-facet").value,
        label: label,
        role: "supporting",
        rationale: "Author added a missing story component.",
      }, "Add missing component");
    });
  }

  function renderContinuation(projection) {
    var body = $("continuation-body");
    var state = projection.continuation;
    var acceptedIds = (projection.canonical_refs || []).map(function (ref) { return ref.milestone_id; });
    var foundationAccepted = !((projection.revision || {}).active_revision_id) &&
      acceptedIds.indexOf("whole_story_structure") >= 0;
    var actionLabels = {
      "propose-outline": "Create outline proposal",
      "accept-outline": "Continue with this outline",
      "propose-chapter-plan": "Plan Chapter 1",
      "accept-chapter-plan": "Continue with this chapter plan",
      "propose-scene-plans": "Plan scenes",
      "accept-scene-plans": "Continue with these scene plans",
      "prepare-draft-handoff": "Prepare Chapter 1 draft",
      "review-chapter-1": "Review Chapter 1",
      "review-stale-continuation": "Review stale continuation"
    };
    var action = (projection.available_actions || []).filter(function (item) {
      return Object.prototype.hasOwnProperty.call(actionLabels, item);
    })[0];
    if (!state && !foundationAccepted) {
      body.innerHTML = '<p class="muted">Accept the whole-story structure to continue into outlining.</p>';
      return;
    }
    var html = [];
    if (foundationAccepted) {
      html.push(
        '<section class="phase-transition" role="status" aria-label="Next story-development phase">' +
        '<p class="phase-transition-kicker">Foundation complete</p>' +
        '<h3>Next: outline your story</h3>' +
        '<p>Turn the accepted foundation into a derived whole-story outline. You can review it before accepting it.</p>' +
        '</section>'
      );
    }
    if (state && state.stale) {
      html.push('<p class="blocking-inline" role="alert">' + escapeHtml(state.stale_reason || "The accepted upstream inputs changed; review these derived plans before drafting.") + "</p>");
    }
    if (state && state.outline_proposal) {
      html.push("<h3>Whole-story outline</h3><p>" + escapeHtml(state.outline_proposal.title) + " · derived proposal</p>");
      html.push(listHtml((state.outline_proposal.chapters || []).map(function (chapter) {
        return "Chapter " + chapter.chapter_index + ": " + chapter.purpose;
      })));
    }
    if (state && state.chapter_plan) {
      html.push("<h3>Chapter 1 plan</h3><p>" + escapeHtml(state.chapter_plan.what_changes) + "</p>");
    }
    if (state && state.scene_plans && state.scene_plans.length) {
      html.push("<h3>Scene plan</h3>" + listHtml(state.scene_plans.map(function (scene) {
        return scene.scene_id + ": " + scene.purpose;
      })));
    }
    if (state && state.draft_handoff) {
      html.push("<h3>Ready to write Chapter 1</h3><p>Use the accepted identity, structure, outline, chapter plan, and scene plan.</p><code>" + escapeHtml(state.draft_handoff.command) + "</code>");
      if (state.draft_status === "drafted") {
        html.push("<p><strong>Chapter 1 is drafted.</strong> Review it before planning Chapter 2.</p>");
      }
    }
    if (action) {
      html.push('<p class="next-action-label">Next step</p>');
      html.push('<button type="button" class="continue-button primary-next-action" data-continuation-action="' + escapeHtml(action) + '">' + escapeHtml(actionLabels[action]) + " →</button>");
    } else if (foundationAccepted) {
      html.push('<p class="muted">The foundation is accepted, but no continuation action is currently available.</p>');
    }
    body.innerHTML = html.join("");
    var button = body.querySelector("[data-continuation-action]");
    if (button) button.addEventListener("click", function () {
      sendAction(button.getAttribute("data-continuation-action"), {}, button.textContent.trim());
    });
  }

  function render(projection) {
    if (!projection) {
      return;
    }
    if (typeof projection.session_version === "number") {
      state.sessionVersion = projection.session_version;
    } else if (projection.workspace && typeof projection.workspace.session_version === "number") {
      state.sessionVersion = projection.workspace.session_version;
    }
    $("workspace-meta").textContent =
      "Workspace " + state.workspaceId + " · version " + state.sessionVersion;
    renderNavigator(projection);
    renderStoryMap(projection);
    renderPrimarySurface(projection);
    renderDecisionCard(projection);
    renderInspector(projection);
    syncInspector();
    renderReviews(projection);
    renderWorkingComposition(projection);
    renderContinuation(projection);
  }

  function renderBookProgress(progress) {
    $("book-progress-summary").textContent =
      progress.accepted_chapters + " accepted chapter(s) · " +
      progress.planned_chapters + " planned chapter(s).";
    $("book-expression-status").textContent = progress.book_expression || "missing";
    $("book-reconciliation-status").textContent = progress.reconciliation_status || "not started";
    $("book-next-command").textContent = progress.next_command || "No owning command is currently required.";
    $("book-authority-status").textContent = progress.authority_status || "DERIVED / NOT CANON";

    if (progress.publication_ready) {
      $("book-publication-status").innerHTML =
        "<p><strong>Publication handoff ready.</strong> The accepted Book passed the existing publishing preflight.</p>" +
        listHtml(progress.publish_commands || []);
    } else {
      $("book-publication-status").innerHTML =
        '<p class="muted"><strong>Publication not ready:</strong> ' +
        escapeHtml(progress.publication_blocker || "An accepted Book is required.") +
        "</p>";
    }
  }

  function loadBookProgress() {
    return fetch("/api/beginner/book/progress", {
      headers: { Accept: "application/json" },
    })
      .then(readJson)
      .then(function (progress) {
        renderBookProgress(progress);
        return progress;
      })
      .catch(function (error) {
        $("book-progress-summary").textContent =
          "Unable to load whole-book progress: " + error.message;
        return null;
      });
  }

  function currentChapterFromQuery() {
    try {
      var params = new URLSearchParams(window.location.search);
      var value = params.get("chapter");
      if (!value) return null;
      var parsed = Number(value);
      return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
    } catch (error) {
      return null;
    }
  }

  function renderPostDraftReview(chapter, review) {
    var panel = $("post-draft-review");
    if (!panel) return;
    panel.hidden = false;
    $("post-draft-status").textContent =
      "Chapter " + chapter + " · " + String(review.production_status || "unknown").replace(/_/g, " ");
    $("post-draft-next-action").textContent = review.recommended_next_action || "Review the current chapter state.";

    var evidence = [];
    if (review.blocking_findings && review.blocking_findings.length) {
      evidence.push("<h4>Blocking findings</h4>" + listHtml(review.blocking_findings));
    }
    if (review.warnings && review.warnings.length) {
      evidence.push("<h4>Warnings</h4>" + listHtml(review.warnings));
    }
    if (review.plan_alignment) {
      evidence.push(
        "<h4>Plan alignment</h4><pre>" +
        escapeHtml(JSON.stringify(review.plan_alignment, null, 2)) +
        "</pre>"
      );
    }
    $("post-draft-evidence").innerHTML = evidence.join("") || '<p class="muted">No review evidence recorded yet.</p>';

    var accept = $("post-draft-accept");
    var revise = $("post-draft-revise");
    var planNext = $("post-draft-plan-next");
    accept.hidden = review.accepted || !review.source_draft || review.stale || (review.blocking_findings || []).length > 0;
    revise.hidden = review.accepted || !review.source_draft;
    planNext.hidden = !review.accepted;
    planNext.textContent = "Plan Chapter " + (chapter + 1);
  }

  function loadPostDraftReview() {
    var chapter = currentChapterFromQuery();
    if (!chapter) return Promise.resolve(null);
    return fetch("/api/beginner/chapters/" + chapter + "/review", {
      headers: { Accept: "application/json" },
    })
      .then(readJson)
      .then(function (review) {
        renderPostDraftReview(chapter, review);
        return review;
      })
      .catch(function (error) {
        var panel = $("post-draft-review");
        if (panel) {
          panel.hidden = false;
          $("post-draft-status").textContent = "Unable to load post-draft review: " + error.message;
        }
        return null;
      });
  }

  function acceptLatestDraft() {
    var chapter = currentChapterFromQuery();
    if (!chapter) return;
    if (!window.confirm("Accept the latest Chapter " + chapter + " draft through Auteur's existing chapter authority?")) {
      return;
    }
    setStatus("Accepting Chapter " + chapter + "…");
    fetch("/api/beginner/chapters/" + chapter + "/accept-latest-draft", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ command_id: nextCommandId("accept-draft") }),
    })
      .then(readJson)
      .then(function () {
        setStatus("");
        loadBookProgress();
        return loadPostDraftReview();
      })
      .catch(function (error) {
        setStatus("Chapter acceptance failed: " + error.message);
      });
  }

  function preparePostDraftRevision() {
    var chapter = currentChapterFromQuery();
    if (!chapter) return;
    setStatus("Preparing revision handoff…");
    fetch("/api/beginner/chapters/" + chapter + "/revision-handoff", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        command_id: nextCommandId("revision-handoff"),
        decision: "revise current candidate from post-draft review",
        route: "retry",
      }),
    })
      .then(readJson)
      .then(function () {
        setStatus("Revision handoff prepared.");
      })
      .catch(function (error) {
        setStatus("Revision handoff failed: " + error.message);
      });
  }

  function loadNextChapterPlan() {
    var chapter = currentChapterFromQuery();
    if (!chapter) return;
    var next = chapter + 1;
    setStatus("Planning Chapter " + next + "…");
    fetch("/api/beginner/chapters/" + next + "/plan", {
      headers: { Accept: "application/json" },
    })
      .then(readJson)
      .then(function (payload) {
        var evidence = $("post-draft-evidence");
        evidence.innerHTML =
          "<h4>Chapter " + next + " context</h4><pre>" +
          escapeHtml(JSON.stringify(payload.plan, null, 2)) +
          "</pre>";
        setStatus("");
      })
      .catch(function (error) {
        setStatus("Next-chapter planning failed: " + error.message);
      });
  }

  function currentWorkspaceFromQuery() {
    try {
      var params = new URLSearchParams(window.location.search);
      return params.get("workspace");
    } catch (error) {
      return null;
    }
  }

  function initDrawer() {
    var toggle = $("nav-toggle");
    var nav = $("story-navigator");
    function syncAria() {
      toggle.setAttribute("aria-expanded", document.body.classList.contains("nav-open") ? "true" : "false");
    }
    toggle.addEventListener("click", function () {
      document.body.classList.toggle("nav-open");
      syncAria();
    });
    nav.addEventListener("click", function (event) {
      // On narrow screens the navigator is a drawer: dismiss after choosing.
      if (window.innerWidth <= 800 && event.target.closest("li")) {
        document.body.classList.remove("nav-open");
        syncAria();
      }
    });
    syncAria();
  }

  function init() {
    initDrawer();
    $("open-inspector").addEventListener("click", function () {
      state.inspectorOpen = true;
      syncInspector();
      $("close-inspector").focus();
    });
    $("close-inspector").addEventListener("click", function () {
      state.inspectorOpen = false;
      syncInspector();
      $("open-inspector").focus();
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && state.inspectorOpen) {
        state.inspectorOpen = false;
        syncInspector();
        $("open-inspector").focus();
      }
    });
    loadPostDraftReview();
    loadBookProgress();
    var fromQuery = currentWorkspaceFromQuery();
    if (fromQuery) {
      state.workspaceId = fromQuery;
      $("workspace-id").value = fromQuery;
      loadProjection();
    }
    $("workspace-form").addEventListener("submit", function (event) {
      event.preventDefault();
      var value = $("workspace-id").value.trim();
      if (!value) {
        setStatus("Enter a workspace ID to open.");
        return;
      }
      state.workspaceId = value;
      setSaveFeedback("");
      loadProjection();
    });
    $("continue-architecture").addEventListener("click", function () {
      sendAction("continue-architecture", {}, "Continue with this interpretation");
    });
    $("refine-architecture").addEventListener("click", function () {
      $("refinement-panel").open = true;
      $("refinement-panel").scrollIntoView({ behavior: "smooth", block: "start" });
    });
    $("explain-architecture").addEventListener("click", function () {
      $("story-map-body").scrollIntoView({ behavior: "smooth", block: "start" });
    });
    $("continue-button").addEventListener("click", function () {
      var stage = $("continue-button").dataset.reviewStage;
      if (stage) {
        sendAction("open-review", { stage: stage }, $("continue-button").textContent.trim());
      } else {
        sendContinue();
      }
    });
    $("post-draft-accept").addEventListener("click", acceptLatestDraft);
    $("post-draft-revise").addEventListener("click", preparePostDraftRevision);
    $("post-draft-plan-next").addEventListener("click", loadNextChapterPlan);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
