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
    return stage === "discover" ? "Discover" :
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

  function renderInspector(projection) {
    var inspector = projection.guidance_inspector;
    var body = $("inspector-body");
    if (!inspector) {
      body.innerHTML = '<p class="muted">Guidance is unavailable for this view.</p>';
      return;
    }
    var parts = [];
    parts.push(detailsRow("Why does Auteur recommend this?", "<p>" + escapeHtml(inspector.recommendation_rationale) + "</p>"));
    parts.push(detailsRow("Teach me", listHtml(inspector.craft_principles)));
    parts.push(detailsRow("Compare trade-offs", listHtml(inspector.tradeoffs)));
    parts.push(detailsRow("What this choice changes", inspectorValue(inspector["narrative_" + "consequences"])));
    parts.push(detailsRow("Alternatives", listHtml(inspector.alternatives)));
    parts.push(detailsRow("Evidence / story context", listHtml(inspector.evidence)));
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
    if (card && card.warnings_or_tensions) {
      warnings = warnings.concat(card.warnings_or_tensions);
    }
    // Card warnings are the source for card-local guidance. The combined
    // projection no longer repeats them with a card-id prefix.
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
    if (entries.length === 0) {
      list.innerHTML = "<li class=\"muted\">No stages yet.</li>";
      return;
    }
    list.innerHTML = entries
      .map(function (entry) {
        var classes = ["navigator-entry", "lifecycle-" + entry.lifecycle];
        if (entry.current_card_id) {
          classes.push("is-current");
        }
        if (entry.stale) {
          classes.push("is-stale");
        }
        var bits = [];
        bits.push("<span class=\"nav-stage\">" + escapeHtml(stageLabel(entry.stage)) + "</span>");
        bits.push(
          '<span class="nav-progress">' +
            escapeHtml(String(entry.answered_cards)) +
            "/" +
            escapeHtml(String(entry.total_cards)) +
            " answered</span>"
        );
        var acceptedIds = (projection.canonical_refs || []).map(function (ref) { return ref.milestone_id; });
        var milestoneId = entry.stage === "discover" ? "story_direction" :
          (entry.stage === "story_identity" ? "story_identity" : "whole_story_structure");
        var lifecycleLabel = acceptedIds.indexOf(milestoneId) >= 0 ? "Accepted" :
          (entry.review_available ? "Ready for review" :
            (entry.availability !== "available" ? "Later" :
              (entry.lifecycle === "blocked" ? "Needs attention" : "In progress")));
        bits.push('<span class="nav-lifecycle">' + escapeHtml(lifecycleLabel) + "</span>");
        if (entry.review_available && acceptedIds.indexOf(milestoneId) < 0) {
          bits.push('<span class="nav-canonical-state">Not yet accepted</span>');
        }
        if (entry.availability && entry.availability !== "available") {
          bits.push('<span class="nav-locked">' + escapeHtml(entry.availability) + "</span>");
        }
        if (entry.stale) {
          bits.push('<span class="nav-stale">stale</span>');
        }
        return '<li class="' + classes.join(" ") + '">' + bits.join(" ") + "</li>";
      })
      .join("");
  }

  function renderStoryMap(projection) {
    var refs = projection.canonical_refs || [];
    var revision = projection.revision || {};
    var html = [];
    html.push("<h4>Accepted milestones</h4>");
    if (refs.length === 0) {
      html.push("<p class=\"muted\">None accepted yet.</p>");
    } else {
      html.push(
        "<ul>" +
          refs
            .map(function (ref) {
              return "<li>" + escapeHtml(milestoneLabel(ref.milestone_id)) + "</li>";
            })
            .join("") +
          "</ul>"
      );
    }
    html.push("<h4>Revision</h4>");
    if (revision.active_revision_id) {
      html.push(
        "<p>Exploring a revision workspace" +
          (revision.target_stage ? " · target: " + escapeHtml(stageLabel(revision.target_stage)) : "") +
          (revision.at_risk_stages && revision.at_risk_stages.length
            ? " — at risk: " + escapeHtml(revision.at_risk_stages.map(stageLabel).join(", "))
            : "") +
          "</p>"
      );
    } else {
      html.push("<p class=\"muted\">No active revision.</p>");
    }
    // Read-only: plain text, no inputs or command buttons.
    $("story-map-body").innerHTML = html.join("");
  }

  function renderDecisionCard(projection) {
    var card = projection.decision_card;
    var question = $("card-question");
    var optionsBox = $("card-options");
    var acceptedIds = (projection.canonical_refs || []).map(function (ref) { return ref.milestone_id; });
    var foundationAccepted = !((projection.revision || {}).active_revision_id) &&
      acceptedIds.indexOf("whole_story_structure") >= 0;
    if (foundationAccepted) {
      state.currentCardId = null;
      question.textContent = "Story foundation accepted";
      optionsBox.innerHTML = '<p class="completion-state">Discover, Story Identity, and Whole-Story Structure are canonical.</p>';
      $("card-why-now").textContent = "";
      $("card-recommendation").textContent = "";
      $("card-consequence").textContent = "";
      $("inspector-body").innerHTML = "";
      $("card-warnings").innerHTML = "";
      $("save-feedback").textContent = "Accepted story foundation.";
      $("continue-button").disabled = true;
      $("continue-button").textContent = "Story foundation complete";
      $("continue-button").dataset.reviewStage = "";
      return;
    }
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
      body.innerHTML = '<p class="completion-summary"><strong>Story foundation complete.</strong> Your accepted direction, identity, and whole-story structure are ready for the next stage of work.</p>';
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
              (summary.card_id || "card") + " — " + alignmentLabel,
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
    renderDecisionCard(projection);
    renderInspector(projection);
    syncInspector();
    renderReviews(projection);
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
    $("continue-button").addEventListener("click", function () {
      var stage = $("continue-button").dataset.reviewStage;
      if (stage) {
        sendAction("open-review", { stage: stage }, $("continue-button").textContent.trim());
      } else {
        sendContinue();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
