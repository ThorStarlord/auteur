/* Beginner Workspace browser (Task 7): presentation-only client.
 *
 * Talks only to the Task 6 local JSON API:
 * - GET  /api/beginner/workspaces/<workspace_id>          (projection read)
 * - POST /api/beginner/workspaces/<workspace_id>/commands/select   (autosave)
 * - POST /api/beginner/workspaces/<workspace_id>/commands/continue (advance)
 *
 * Holds no narrative rules: every question, option, recommendation, warning,
 * and piece of evidence is rendered verbatim from the server projection.
 * Selecting an option autosaves and keeps the current card visible. The
 * step-by-step path still advances through explicit Continue actions, while
 * the default Beginner path may bundle reversible planning steps behind one
 * clearly labelled author action.
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
    activeLensId: null,
    currentProjection: null,
    structureCustomize: false,
    continuationCustomize: false,
    quickDraftSessionId: null,
    quickDraftPremise: "",
    quickDraftFirstScene: "",
    quickDraftDiscoveries: [],
    quickDraftDiscoveriesVisible: false,
    quickDraftDirty: false,
    quickDraftPending: false,
    quickDraftPollTimer: null,
    quickDraftPollAttempts: 0,
  };

  function $(id) {
    return document.getElementById(id);
  }

  function stageLabel(stage) {
    return stage === "discover" ? "Direction" :
      (stage === "story_identity" ? "Story core" : "Story shape");
  }

  function milestoneLabel(milestoneId) {
    return milestoneId === "story_direction" ? "Direction" :
      (milestoneId === "story_identity" ? "Story core" : "Story shape");
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

  function showHome() {
    $("home-surface").hidden = false;
    $("app-shell").hidden = true;
    $("nav-toggle").hidden = true;
    $("home-button").hidden = true;
    $("workspace-meta").textContent = "";
    state.currentProjection = null;
    state.activeLensId = null;
    state.structureCustomize = false;
    state.continuationCustomize = false;
    if (!currentQuickDraftFromQuery()) {
      clearQuickDraftPoll();
      state.quickDraftPending = false;
      $("quick-draft-result").hidden = true;
      state.quickDraftSessionId = null;
      state.quickDraftDiscoveries = [];
      state.quickDraftDiscoveriesVisible = false;
      state.quickDraftDirty = false;
    }
  }

  function showWorkspace() {
    clearQuickDraftPoll();
    state.quickDraftPending = false;
    $("home-surface").hidden = true;
    $("app-shell").hidden = false;
    $("nav-toggle").hidden = false;
    $("home-button").hidden = false;
  }

  function updateWorkspaceUrl(workspaceId) {
    var url = new URL(window.location.href);
    if (workspaceId) {
      url.searchParams.set("workspace", workspaceId);
      url.searchParams.delete("quick_draft");
    } else {
      url.searchParams.delete("workspace");
    }
    window.history.pushState({}, "", url.pathname + url.search);
  }

  function updateQuickDraftUrl(sessionId) {
    var url = new URL(window.location.href);
    url.searchParams.delete("workspace");
    if (sessionId) url.searchParams.set("quick_draft", sessionId);
    else url.searchParams.delete("quick_draft");
    window.history.pushState({}, "", url.pathname + url.search);
  }

  function openWorkspace(workspaceId, updateUrl) {
    if (!workspaceId) return;
    state.workspaceId = workspaceId;
    state.activeLensId = null;
    state.structureCustomize = false;
    state.continuationCustomize = false;
    $("workspace-id").value = workspaceId;
    if (updateUrl !== false) updateWorkspaceUrl(workspaceId);
    return loadProjection();
  }

  function renderRecentStories(payload) {
    var container = $("recent-stories-list");
    var workspaces = (payload && payload.workspaces) || [];
    if (!workspaces.length) {
      container.innerHTML = '<p class="muted">No stories yet. Start with an idea above.</p>';
      return;
    }
    container.innerHTML = workspaces.map(function (item) {
      var milestones = (item.accepted_milestones || []).length;
      return '<article class="recent-story-card">' +
        '<div><h3>' + escapeHtml(item.title) + '</h3>' +
        '<p>' + escapeHtml(item.premise_preview) + '</p>' +
        '<p class="hint">' + escapeHtml(String(milestones)) + ' accepted milestone(s)</p></div>' +
        '<button type="button" data-open-workspace="' + escapeHtml(item.workspace_id) + '">Continue →</button>' +
        '</article>';
    }).join("");
    Array.prototype.forEach.call(container.querySelectorAll("[data-open-workspace]"), function (button) {
      button.addEventListener("click", function () {
        openWorkspace(button.getAttribute("data-open-workspace"));
      });
    });
  }

  function loadRecentStories() {
    $("home-status").textContent = "Loading your stories…";
    return fetch("/api/beginner/workspaces", { headers: { Accept: "application/json" } })
      .then(readJson)
      .then(function (payload) {
        renderRecentStories(payload);
        $("home-status").textContent = "";
        return payload;
      })
      .catch(function (error) {
        $("home-status").textContent = "Could not load recent stories: " + error.message;
        return null;
      });
  }

  function renderQuickDraftDiscoveries(items) {
    var container = $("quick-draft-discoveries");
    var discoveries = items || [];
    state.quickDraftDiscoveries = discoveries;
    if (!discoveries.length) {
      container.innerHTML = '<p class="muted">No obvious new elements yet. Keep writing.</p>';
      return;
    }
    container.innerHTML =
      '<h4>What should Auteur remember when you shape the story?</h4>' +
      discoveries.map(function (item, index) {
        return '<article class="discovery-chip"><strong>' +
          escapeHtml(item.label || "New story element") +
          '</strong><p>' + escapeHtml(item.value || "") + "</p>" +
          '<label><input type="checkbox" data-remember-discovery="' + String(index) +
          '"> Carry this idea into story shaping</label></article>';
      }).join("") +
      '<p class="hint">Nothing is selected automatically. These are working observations, not accepted story facts.</p>';
  }

  function clearQuickDraftPoll() {
    if (state.quickDraftPollTimer !== null) {
      window.clearTimeout(state.quickDraftPollTimer);
      state.quickDraftPollTimer = null;
    }
  }

  function quickDraftHostInstructions(sessionId) {
    var requestPath = ".auteur/quick_draft/" + sessionId + "/host_agent_request.json";
    return "In the currently open Auteur project, complete the existing host-agent " +
      "Quick Draft request at " + requestPath + ".\\n\\n" +
      "1. Read that exact request using auteur.host_agent.load_host_agent_request. " +
      "Do not prepare a new session or silently switch to a paid provider.\\n" +
      "2. Using your current coding-agent model, write one scene that follows the " +
      "request's system and user instructions.\\n" +
      "3. Build a bound response with auteur.host_agent.build_host_agent_response(" +
      "request, scene_text, runtime=<actual runtime>, model=<actual model or UNAVAILABLE>) " +
      "and complete it via auteur.quick_draft.complete_quick_draft_host_agent_response(" +
      "Path('.'), '" + sessionId + "', response).\\n" +
      "4. Leave everything provisional/Working. Do not accept story setup or change canon.\\n" +
      "The author can then use 'Check for scene' in the browser.";
  }

  function scheduleQuickDraftPoll() {
    if (!state.quickDraftPending || !state.quickDraftSessionId ||
        state.quickDraftPollTimer !== null || state.quickDraftPollAttempts >= 12 ||
        document.hidden || $("home-surface").hidden) return;
    var sessionId = state.quickDraftSessionId;
    state.quickDraftPollTimer = window.setTimeout(function () {
      state.quickDraftPollTimer = null;
      if (!state.quickDraftPending || state.quickDraftSessionId !== sessionId ||
          $("home-surface").hidden) return;
      state.quickDraftPollAttempts += 1;
      fetch("/api/beginner/quick-draft/" + encodeURIComponent(sessionId), {
        headers: { Accept: "application/json" }
      }).then(readJson).then(function (projection) {
        if (state.quickDraftSessionId !== sessionId) return;
        if ((projection.draft || {}).status === "awaiting_host_agent") {
          if (state.quickDraftPollAttempts >= 12) {
            $("quick-draft-handoff-status").textContent =
              "Still waiting. Ask your coding agent to finish the request, then choose 'Check for scene'.";
          } else {
            scheduleQuickDraftPoll();
          }
        } else {
          $("home-status").textContent = "";
          renderQuickDraftProjection(projection);
        }
      }).catch(function (error) {
        if (state.quickDraftSessionId !== sessionId) return;
        $("quick-draft-handoff-status").textContent =
          "Could not check the scene: " + error.message + ". You can check again.";
        scheduleQuickDraftPoll();
      });
    }, 5000);
  }

  function copyQuickDraftHandoff() {
    if (!state.quickDraftSessionId || !state.quickDraftPending) return;
    var text = quickDraftHostInstructions(state.quickDraftSessionId);
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      $("quick-draft-handoff-status").textContent =
        "Clipboard access is unavailable. Select the instructions above and copy them.";
      return;
    }
    return navigator.clipboard.writeText(text).then(function () {
      $("quick-draft-handoff-status").textContent =
        "Instructions copied. Give them to the coding agent working in this project.";
    }).catch(function () {
      $("quick-draft-handoff-status").textContent =
        "Clipboard access is unavailable. Select the instructions above and copy them.";
    });
  }

  function checkQuickDraftResult() {
    if (!state.quickDraftSessionId) return Promise.resolve(null);
    clearQuickDraftPoll();
    state.quickDraftPollAttempts = 0;
    return loadQuickDraftSession(state.quickDraftSessionId);
  }

  function renderQuickDraftProjection(projection) {
    if (!projection) return;
    if (state.quickDraftSessionId !== projection.session_id) {
      clearQuickDraftPoll();
      state.quickDraftPollAttempts = 0;
    }
    state.quickDraftSessionId = projection.session_id;
    var inputs = (projection.scaffold || {}).inputs || {};
    state.quickDraftPremise = inputs.premise || state.quickDraftPremise;
    state.quickDraftFirstScene = inputs.first_scene_intent || state.quickDraftFirstScene;
    if (state.quickDraftPremise) $("new-story-premise").value = state.quickDraftPremise;
    if (state.quickDraftFirstScene) $("quick-draft-first-scene").value = state.quickDraftFirstScene;
    state.quickDraftDirty = false;
    $("quick-draft-result").hidden = false;
    $("quick-draft-editor").value = projection.draft_text || "";
    var draft = projection.draft || {};
    var pending = draft.status === "awaiting_host_agent" || draft.status === "generating";
    state.quickDraftPending = draft.status === "awaiting_host_agent";
    $("quick-draft-host-handoff").hidden = !state.quickDraftPending;
    if (state.quickDraftPending) {
      $("quick-draft-agent-instructions").textContent =
        quickDraftHostInstructions(state.quickDraftSessionId);
      scheduleQuickDraftPoll();
    } else {
      clearQuickDraftPoll();
      $("quick-draft-handoff-status").textContent = "";
    }
    $("quick-draft-editor").disabled = pending;
    $("quick-draft-save").disabled = pending;
    $("quick-draft-discover").disabled = pending;
    $("quick-draft-shape").disabled = pending;
    var elapsed = typeof draft.elapsed_seconds === "number"
      ? " · " + draft.elapsed_seconds.toFixed(1) + "s to first draft"
      : "";
    if (pending) {
      $("quick-draft-meta").textContent =
        "Waiting for the active coding agent to return the working scene…";
    } else if (draft.status === "generation_failed") {
      $("quick-draft-meta").textContent =
        "Draft generation failed: " + String(draft.error || "unknown generation error");
    } else {
      $("quick-draft-meta").textContent =
        "Working scene" + elapsed + " · " + String(draft.edit_count || 0) + " edit(s)";
    }
    if (state.quickDraftDiscoveriesVisible) {
      renderQuickDraftDiscoveries(projection.discoveries || []);
    } else {
      $("quick-draft-discoveries").innerHTML =
        '<p class="muted">When you are ready, choose “What did we discover?” to see possible story material from the draft.</p>';
    }
    $("quick-draft-result").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function startQuickDraft() {
    var premise = $("new-story-premise").value.trim();
    var firstScene = $("quick-draft-first-scene").value.trim();
    if (!premise) {
      $("home-status").textContent = "Add a story idea first.";
      return;
    }
    if (!firstScene) {
      $("home-status").textContent = "Tell Auteur what you want to happen in the first scene.";
      $("quick-draft-first-scene").focus();
      return;
    }
    state.quickDraftDiscoveriesVisible = false;
    state.quickDraftDiscoveries = [];
    state.quickDraftPremise = premise;
    state.quickDraftFirstScene = firstScene;
    $("home-status").textContent = "Writing your first scene…";
    return fetch("/api/beginner/quick-draft", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ premise: premise, first_scene: firstScene }),
    })
      .then(readJson)
      .then(function (projection) {
        $("home-status").textContent = "";
        updateQuickDraftUrl(projection.session_id);
        renderQuickDraftProjection(projection);
        return projection;
      })
      .catch(function (error) {
        $("home-status").textContent = "Quick Draft could not start: " + error.message;
        return null;
      });
  }

  function loadQuickDraftSession(sessionId) {
    if (!sessionId) return Promise.resolve(null);
    $("home-status").textContent = "Loading your working scene…";
    return fetch(
      "/api/beginner/quick-draft/" + encodeURIComponent(sessionId),
      { headers: { Accept: "application/json" } }
    )
      .then(readJson)
      .then(function (projection) {
        state.quickDraftDiscoveriesVisible = false;
        $("home-status").textContent = "";
        renderQuickDraftProjection(projection);
        return projection;
      })
      .catch(function (error) {
        $("home-status").textContent = "Could not reopen Quick Draft: " + error.message;
        return null;
      });
  }

  function saveQuickDraft() {
    if (!state.quickDraftSessionId) return Promise.resolve(null);
    var prose = $("quick-draft-editor").value;
    $("home-status").textContent = "Saving your scene…";
    return fetch(
      "/api/beginner/quick-draft/" + encodeURIComponent(state.quickDraftSessionId) + "/save",
      {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ draft_text: prose }),
      }
    )
      .then(readJson)
      .then(function (projection) {
        state.quickDraftDiscoveriesVisible = false;
        state.quickDraftDiscoveries = [];
        $("home-status").textContent = "Saved.";
        renderQuickDraftProjection(projection);
        return projection;
      })
      .catch(function (error) {
        $("home-status").textContent = "Could not save Quick Draft: " + error.message;
        return null;
      });
  }

  function discoverQuickDraftElements() {
    if (!state.quickDraftSessionId) return Promise.resolve(null);
    return fetch(
      "/api/beginner/quick-draft/" + encodeURIComponent(state.quickDraftSessionId) + "/discoveries",
      { headers: { Accept: "application/json" } }
    )
      .then(readJson)
      .then(function (projection) {
        state.quickDraftDiscoveriesVisible = true;
        renderQuickDraftDiscoveries(projection.discoveries || []);
        return projection;
      })
      .catch(function (error) {
        $("quick-draft-discoveries").innerHTML =
          '<p class="blocking-inline">Could not inspect this draft: ' + escapeHtml(error.message) + "</p>";
        return null;
      });
  }

  function selectedQuickDraftDiscoveries() {
    var selected = [];
    Array.prototype.forEach.call(
      $("quick-draft-discoveries").querySelectorAll("[data-remember-discovery]:checked"),
      function (input) {
        var index = Number(input.getAttribute("data-remember-discovery"));
        if (Number.isInteger(index) && state.quickDraftDiscoveries[index]) {
          selected.push(state.quickDraftDiscoveries[index]);
        }
      }
    );
    return selected;
  }

  function shapingPremise(selected) {
    var parts = [state.quickDraftPremise];
    if (state.quickDraftFirstScene) {
      parts.push("First scene I want: " + state.quickDraftFirstScene);
    }
    if (selected.length) {
      parts.push(
        "Ideas I discovered while drafting and explicitly want to carry forward:\n- " +
        selected.map(function (item) { return item.value; }).join("\n- ")
      );
    }
    return parts.filter(Boolean).join("\n\n");
  }

  function createStoryFromPremise(premise, extra) {
    if (!premise) return Promise.resolve(null);
    $("home-status").textContent = "Creating your story…";
    var payload = {
      command_id: nextCommandId("create"),
      premise: premise
    };
    Object.keys(extra || {}).forEach(function (key) {
      payload[key] = extra[key];
    });
    return fetch("/api/beginner/workspaces", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    })
      .then(readJson)
      .then(function (projection) {
        state.workspaceId = projection.workspace.workspace_id;
        updateWorkspaceUrl(state.workspaceId);
        showWorkspace();
        render(projection);
        loadPostDraftReview();
        loadBookProgress();
        $("home-status").textContent = "";
        return projection;
      })
      .catch(function (error) {
        $("home-status").textContent = "Could not create story: " + error.message;
        return null;
      });
  }

  function shapeQuickDraftStory() {
    if (!state.quickDraftSessionId) return Promise.resolve(null);
    function continueAfterDiscovery(projection) {
      if (!projection) return null;
      if (!(projection.discoveries || []).length) {
        return createStoryFromPremise(
          shapingPremise([]),
          {
            quick_draft_session_id: state.quickDraftSessionId,
            quick_draft_discoveries: [],
          }
        );
      }
      $("home-status").textContent =
        "Choose anything you want Auteur to remember, then choose “Shape this story” again.";
      return null;
    }
    if (state.quickDraftDirty) {
      return saveQuickDraft().then(function (saved) {
        if (!saved) return null;
        return discoverQuickDraftElements().then(continueAfterDiscovery);
      });
    }
    if (!state.quickDraftDiscoveriesVisible) {
      return discoverQuickDraftElements().then(continueAfterDiscovery);
    }
    var selected = selectedQuickDraftDiscoveries();
    return createStoryFromPremise(
      shapingPremise(selected),
      {
        quick_draft_session_id: state.quickDraftSessionId,
        quick_draft_discoveries: selected,
      }
    );
  }

  function createStoryFromHome() {
    var premise = $("new-story-premise").value.trim();
    return createStoryFromPremise(premise, {});
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
        showWorkspace();
        render(projection);
        loadPostDraftReview();
        loadBookProgress();
        setStatus("");
        return projection;
      })
      .catch(function (error) {
        var message = "Could not load workspace: " + error.message;
        setStatus(message);
        if (!$("home-surface").hidden) {
          $("home-status").textContent = message;
        } else {
          showHome();
          $("home-status").textContent = message;
        }
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

  function rememberProjection(projection) {
    if (!projection) return;
    state.currentProjection = projection;
    if (typeof projection.session_version === "number") {
      state.sessionVersion = projection.session_version;
    } else if (projection.workspace && typeof projection.workspace.session_version === "number") {
      state.sessionVersion = projection.workspace.session_version;
    }
    $("workspace-meta").textContent =
      "Workspace " + state.workspaceId + " · version " + state.sessionVersion;
  }

  function sendAction(slug, payload, label, options) {
    if (!state.workspaceId) return Promise.resolve(null);
    var settings = options || {};
    setStatus(label + "…");
    return fetch(
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
        if (settings.render === false) {
          rememberProjection(projection);
        } else {
          render(projection);
        }
        if (!settings.keepStatus) setStatus("");
        return projection;
      })
      .catch(function (error) {
        setStatus(label + " failed: " + error.message);
        return null;
      });
  }

  function useStoryDirection(directionId) {
    if (!directionId) return Promise.resolve(null);
    return sendAction(
      "select-direction",
      { direction_id: directionId },
      "Choosing this direction",
      { render: false, keepStatus: true }
    ).then(function (projection) {
      if (!projection) return null;
      return sendAction("accept-direction", {}, "Using this direction");
    });
  }

  function structureNavigatorEntry(projection) {
    return (projection.navigator || []).filter(function (entry) {
      return entry.stage === "story_structure";
    })[0] || null;
  }

  function useRecommendedStoryShape() {
    var guard = 0;
    state.structureCustomize = false;
    setStatus("Applying Auteur's recommended story shape…");

    function advance(projection) {
      if (!projection || guard >= 12) return Promise.resolve(projection);
      guard += 1;

      var accepted = (projection.canonical_refs || []).some(function (ref) {
        return ref.milestone_id === "whole_story_structure";
      });
      if (accepted) return Promise.resolve(projection);

      var card = projection.decision_card;
      if (card && card.stage === "story_structure") {
        var recommendation = card.recommendation || (card.options || [])[0];
        if (!recommendation) return Promise.resolve(projection);
        return sendAction(
          "select",
          { card_id: card.card_id, option: recommendation },
          "Applying recommended story shape",
          { render: false, keepStatus: true }
        ).then(function (selected) {
          if (!selected) return null;
          var entry = structureNavigatorEntry(selected);
          if (entry && entry.review_available) {
            return sendAction(
              "open-review",
              { stage: "story_structure" },
              "Checking recommended story shape",
              { render: false, keepStatus: true }
            ).then(function (reviewed) {
              if (!reviewed) return null;
              return sendAction("accept-structure", {}, "Using recommended story shape");
            });
          }
          return sendAction(
            "continue",
            { card_id: card.card_id },
            "Applying recommended story shape",
            { render: false, keepStatus: true }
          ).then(advance);
        });
      }

      var actions = projection.available_actions || [];
      if (actions.indexOf("open-review:story_structure") >= 0) {
        return sendAction(
          "open-review",
          { stage: "story_structure" },
          "Checking recommended story shape",
          { render: false, keepStatus: true }
        ).then(advance);
      }
      if (actions.indexOf("accept-structure") >= 0) {
        return sendAction("accept-structure", {}, "Using recommended story shape");
      }
      return Promise.resolve(projection);
    }

    return advance(state.currentProjection).then(function (projection) {
      setStatus("");
      return projection;
    });
  }

  function prepareChapterLaunch() {
    var sequence = [
      "propose-outline",
      "accept-outline",
      "propose-chapter-plan",
      "accept-chapter-plan",
      "propose-scene-plans",
      "accept-scene-plans",
      "prepare-draft-handoff",
    ];
    var guard = 0;
    state.continuationCustomize = false;
    setStatus("Planning Chapter 1…");

    function advance(projection) {
      if (!projection || guard >= 10) return Promise.resolve(projection);
      guard += 1;
      var actions = projection.available_actions || [];
      if (actions.indexOf("draft-chapter-1") >= 0) {
        return Promise.resolve(projection);
      }
      var next = sequence.filter(function (action) {
        return actions.indexOf(action) >= 0;
      })[0];
      if (!next) return Promise.resolve(projection);
      var finalPlanningStep = next === "prepare-draft-handoff";
      return sendAction(
        next,
        {},
        "Planning Chapter 1",
        finalPlanningStep ? {} : { render: false, keepStatus: true }
      ).then(advance);
    }

    return advance(state.currentProjection).then(function (projection) {
      setStatus("");
      return projection;
    });
  }

  function draftAndShowChapterOne() {
    return sendAction("draft-chapter-1", {}, "Drafting Chapter 1").then(function (projection) {
      if (!projection) return null;
      return openChapterReview(1).then(function (review) {
        var panel = $("post-draft-review");
        if (panel) panel.scrollIntoView({ behavior: "smooth", block: "start" });
        return review;
      });
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

  function storyLensLayoutKey() {
    return "auteur.beginner.story-lenses.v1:" + (state.workspaceId || "unknown");
  }

  function defaultStoryLensOrder(lenses) {
    return (lenses || []).map(function (lens) { return lens.lens_id; });
  }

  function loadStoryLensOrder(lenses) {
    var fallback = defaultStoryLensOrder(lenses);
    try {
      var raw = window.localStorage.getItem(storyLensLayoutKey());
      if (!raw) return fallback;
      var parsed = JSON.parse(raw);
      if (!parsed || parsed.schema_version !== 1 || !Array.isArray(parsed.order)) {
        return fallback;
      }
      var valid = {};
      fallback.forEach(function (id) { valid[id] = true; });
      var seen = {};
      var order = parsed.order.filter(function (id) {
        if (!valid[id] || seen[id]) return false;
        seen[id] = true;
        return true;
      });
      fallback.forEach(function (id) {
        if (!seen[id]) order.push(id);
      });
      return order;
    } catch (error) {
      return fallback;
    }
  }

  function saveStoryLensOrder(order) {
    try {
      window.localStorage.setItem(
        storyLensLayoutKey(),
        JSON.stringify({ schema_version: 1, order: order })
      );
    } catch (error) {
      // Layout preference failure is non-punitive and never affects story state.
    }
  }

  function orderedStoryLenses(lenses) {
    var source = lenses || [];
    var byId = {};
    source.forEach(function (lens) { byId[lens.lens_id] = lens; });
    return loadStoryLensOrder(source).map(function (id) { return byId[id]; }).filter(Boolean);
  }

  function storyLensById(orientation, lensId) {
    if (!orientation || !lensId) return null;
    return (orientation.story_lenses || []).filter(function (lens) {
      return lens.lens_id === lensId;
    })[0] || null;
  }

  function storyLensStateLabel(value) {
    var labels = {
      inferred: "Inferred",
      author_confirmed: "Author-confirmed",
      author_modified: "Author-modified",
      unestablished: "Not established",
      stale: "Needs review",
    };
    return labels[value] || value || "Working";
  }

  function setActiveStoryLens(lensId) {
    state.activeLensId = lensId;
    state.inspectorOpen = true;
    if (state.currentProjection) renderInspector(state.currentProjection);
    syncInspector();
  }

  function moveStoryLens(lensId, delta) {
    if (!state.currentProjection || !state.currentProjection.story_orientation) return;
    var lenses = state.currentProjection.story_orientation.story_lenses || [];
    var order = loadStoryLensOrder(lenses);
    var index = order.indexOf(lensId);
    var target = index + delta;
    if (index < 0 || target < 0 || target >= order.length) return;
    var swap = order[target];
    order[target] = order[index];
    order[index] = swap;
    saveStoryLensOrder(order);
    renderArchitectureSurface(state.currentProjection);
  }

  function storyLensItemHtml(item) {
    var evidence = (item.evidence || []).map(function (entry) {
      return entry.excerpt || entry.label;
    });
    var alternatives = (item.alternatives || []).map(function (entry) {
      return entry.label + " — " + entry.rationale;
    });
    var controls = [];
    if (item.activation === "suppressed") {
      controls.push('<button data-lens-command="restore-architecture-component" data-component-id="' +
        escapeHtml(item.component_id) + '">Restore</button>');
    } else {
      controls.push('<button data-lens-command="confirm-architecture-component" data-component-id="' +
        escapeHtml(item.component_id) + '">Keep / confirm</button>');
      controls.push('<button data-lens-command="suppress-architecture-component" data-component-id="' +
        escapeHtml(item.component_id) + '">Reduce / remove</button>');
      controls.push('<button data-lens-command="rename-architecture-component" data-component-id="' +
        escapeHtml(item.component_id) + '">Rename</button>');
    }
    (item.alternatives || []).forEach(function (alternative) {
      controls.push('<button data-lens-command="choose-architecture-alternative" data-component-id="' +
        escapeHtml(item.component_id) + '" data-alternative="' + escapeHtml(alternative.label) +
        '">Use ' + escapeHtml(alternative.label) + "</button>");
    });
    return '<article class="story-lens-item"><h3>' + escapeHtml(item.label) + "</h3>" +
      '<p class="lens-meta">' + escapeHtml(item.role) + " · " + escapeHtml(item.certainty) +
      " · " + escapeHtml(storyLensStateLabel(item.review_state === "unreviewed" ? "inferred" :
        (item.review_state === "author_confirmed" ? "author_confirmed" : "author_modified"))) + "</p>" +
      "<p>" + escapeHtml(item.rationale) + "</p>" +
      (evidence.length ? detailsRow("Evidence", listHtml(evidence)) : "") +
      (alternatives.length ? detailsRow("Alternatives", listHtml(alternatives)) : "") +
      (controls.length ? '<div class="surface-actions">' + controls.join("") + "</div>" : "") +
      "</article>";
  }

  function renderStoryLensInspector(projection, lens) {
    var body = $("inspector-body");
    $("inspector-title").textContent = lens.title;
    var parts = [
      '<p class="lens-eyebrow">' + escapeHtml(lens.eyebrow) + "</p>",
      '<p><strong>' + escapeHtml(lens.summary) + "</strong></p>",
      "<p>" + escapeHtml(lens.detail) + "</p>",
      '<p class="inspector-authority">' + escapeHtml(storyLensStateLabel(lens.state)) +
        " · " + escapeHtml(lens.authority_status) + "</p>",
    ];
    if (lens.items && lens.items.length) {
      parts.push(lens.items.map(storyLensItemHtml).join(""));
    } else if (lens.refinement_mode === "through_sources") {
      parts.push('<p class="muted">This lens is synthesized from other Story Lenses. Refine its source lenses rather than editing a parallel copy.</p>');
    }
    var orientation = projection.story_orientation || {};
    var related = (lens.related_lens_ids || []).map(function (id) {
      return storyLensById(orientation, id);
    }).filter(Boolean);
    if (related.length) {
      parts.push('<div class="related-lenses"><h3>Related Story Lenses</h3>' +
        related.map(function (item) {
          return '<button data-related-lens="' + escapeHtml(item.lens_id) + '">' +
            escapeHtml(item.title) + "</button>";
        }).join("") + "</div>");
    }
    body.innerHTML = parts.join("");

    Array.prototype.forEach.call(body.querySelectorAll("[data-lens-command]"), function (button) {
      button.addEventListener("click", function () {
        var command = button.getAttribute("data-lens-command");
        var payload = {
          component_id: button.getAttribute("data-component-id"),
          rationale: "Author refinement from the Story Lens inspector.",
        };
        if (command === "rename-architecture-component") {
          var label = window.prompt("New label");
          if (!label) return;
          payload.label = label;
        }
        if (command === "choose-architecture-alternative") {
          payload.alternative_label = button.getAttribute("data-alternative");
        }
        sendAction(command, payload, button.textContent.trim());
      });
    });
    Array.prototype.forEach.call(body.querySelectorAll("[data-related-lens]"), function (button) {
      button.addEventListener("click", function () {
        setActiveStoryLens(button.getAttribute("data-related-lens"));
      });
    });
  }

  function renderStoryLensCards(projection) {
    var orientation = projection.story_orientation;
    var container = $("architecture-facets");
    if (!orientation) {
      container.innerHTML = '<p class="muted">No story interpretation is available.</p>';
      return;
    }
    var lenses = orderedStoryLenses(orientation.story_lenses || []);
    var ids = lenses.map(function (lens) { return lens.lens_id; });
    if (state.activeLensId && ids.indexOf(state.activeLensId) < 0) {
      state.activeLensId = null;
    }
    container.innerHTML = lenses.map(function (lens, index) {
      var heroClass = lens.lens_id === "story_engine" ? " story-lens-card--anchor" : "";
      var controls =
        '<button data-story-lens-open="' + escapeHtml(lens.lens_id) + '">Open details</button>' +
        '<button data-story-lens-move="-1" data-lens-id="' + escapeHtml(lens.lens_id) +
          '"' + (index === 0 ? " disabled" : "") + ' aria-label="Move ' + escapeHtml(lens.title) + ' left">←</button>' +
        '<button data-story-lens-move="1" data-lens-id="' + escapeHtml(lens.lens_id) +
          '"' + (index === lenses.length - 1 ? " disabled" : "") + ' aria-label="Move ' + escapeHtml(lens.title) + ' right">→</button>';
      return '<article class="story-lens-card' + heroClass + '" data-lens-card="' +
        escapeHtml(lens.lens_id) + '">' +
        '<p class="lens-eyebrow">' + escapeHtml(lens.eyebrow) + "</p>" +
        "<h3>" + escapeHtml(lens.title) + "</h3>" +
        '<span class="lens-state lens-state--' + escapeHtml(lens.state) + '">' +
          escapeHtml(storyLensStateLabel(lens.state)) + "</span>" +
        '<p class="lens-summary">' + escapeHtml(lens.summary) + "</p>" +
        '<div class="story-lens-card-actions">' + controls + "</div></article>";
    }).join("");
    if (orientation.availability_note) {
      container.innerHTML += '<p class="story-lens-availability hint">' +
        escapeHtml(orientation.availability_note) + "</p>";
    }
    Array.prototype.forEach.call(container.querySelectorAll("[data-story-lens-open]"), function (button) {
      button.addEventListener("click", function () {
        setActiveStoryLens(button.getAttribute("data-story-lens-open"));
      });
    });
    Array.prototype.forEach.call(container.querySelectorAll("[data-story-lens-move]"), function (button) {
      button.addEventListener("click", function () {
        moveStoryLens(
          button.getAttribute("data-lens-id"),
          Number(button.getAttribute("data-story-lens-move"))
        );
      });
    });
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
    var orientation = projection.story_orientation;
    var activeLens = storyLensById(orientation, state.activeLensId);
    if (projection.primary_surface === "architecture" && activeLens) {
      renderStoryLensInspector(projection, activeLens);
      return;
    }
    $("inspector-title").textContent = projection.primary_surface === "architecture"
      ? "Story Architecture Overview"
      : "Explore guidance";
    var inspector = projection.guidance_inspector;
    var body = $("inspector-body");
    var parts = [];
    if (orientation && orientation.composition) {
      parts.push(compositionExplanation(orientation));
    }
    if (!inspector) {
      parts.push('<p class="muted">Choose a Story Lens for detailed evidence and refinement.</p>');
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
      var milestoneId = entry.stage === "discover" ? "story_direction" :
        (entry.stage === "story_identity" ? "story_identity" : "whole_story_structure");
      var classes = ["navigator-entry", "lifecycle-" + entry.lifecycle];
      var expectedSurface = entry.stage === "discover" ? "discovery" :
        (entry.stage === "story_identity" ? "story_identity" : "structure");
      if (projection.primary_surface === expectedSurface || entry.current_card_id) classes.push("is-current");
      if (acceptedIds.indexOf(milestoneId) >= 0) classes.push("is-accepted");
      if (entry.stale) classes.push("is-stale");
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
      if (orientation.lens_diagnostics) {
        var diagnostics = orientation.lens_diagnostics;
        var lensTitles = {};
        (orientation.story_lenses || []).forEach(function (lens) {
          lensTitles[lens.lens_id] = lens.title;
        });
        var unresolved = (diagnostics.unestablished_lens_ids || []).map(function (id) {
          return lensTitles[id] || id;
        });
        var needsAttention = (diagnostics.needs_attention_lens_ids || []).map(function (id) {
          return lensTitles[id] || id;
        });
        html.push(detailsRow(
          "Interpretation diagnostics",
          "<p><strong>Analysis source:</strong> " + escapeHtml(diagnostics.source_mode) + "</p>" +
          "<p><strong>Freshness:</strong> " + escapeHtml(diagnostics.stale ? "needs review" : "current") + "</p>" +
          "<p><strong>Active / suppressed components:</strong> " +
            escapeHtml(String(diagnostics.active_component_count)) + " / " +
            escapeHtml(String(diagnostics.suppressed_component_count)) + "</p>" +
          "<p><strong>Author adjustments:</strong> " +
            escapeHtml(String(diagnostics.author_adjustment_count)) + "</p>" +
          "<p><strong>Unestablished lenses:</strong></p>" + listHtml(unresolved) +
          "<p><strong>Needs attention:</strong></p>" + listHtml(needsAttention)
        ));
      }
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
    renderStoryLensCards(projection);
  }

  function renderDiscoverySurface(projection) {
    var surface = $("discovery-surface");
    var discovery = projection.discovery;
    surface.hidden = projection.primary_surface !== "discovery";
    if (surface.hidden) return;
    if (!discovery) {
      $("discovery-rationale").textContent = "Auteur is still preparing possible directions.";
      $("discovery-directions").innerHTML = "";
      return;
    }
    $("discovery-rationale").textContent = discovery.rationale || "";
    if (discovery.status === "unavailable") {
      $("discovery-directions").innerHTML =
        '<p class="blocking-inline">Rich direction search is unavailable. The simpler curated choices are still available below.</p>';
      return;
    }
    $("discovery-directions").innerHTML = (discovery.directions || []).map(function (direction) {
      var badge = direction.recommended ? "<strong>Recommended</strong> · " : "";
      return '<article class="direction-card"><h3>' + badge + escapeHtml(direction.title) +
        "</h3><p>" + escapeHtml(direction.summary) + "</p>" +
        listHtml(direction.tradeoffs || []) +
        '<button class="continue-button" data-direction-id="' + escapeHtml(direction.direction_id) +
        '">Use this direction</button></article>';
    }).join("");
    Array.prototype.forEach.call($("discovery-directions").querySelectorAll("button[data-direction-id]"), function (button) {
      button.addEventListener("click", function () {
        useStoryDirection(button.getAttribute("data-direction-id"));
      });
    });
  }

  function renderIdentitySurface(projection) {
    var surface = $("identity-surface");
    var candidate = projection.identity_candidate;
    surface.hidden = projection.primary_surface !== "story_identity";
    if (surface.hidden) return;
    if (!candidate) {
      $("identity-candidate").innerHTML = '<p class="muted">Auteur is still assembling the story core.</p>';
      return;
    }
    var preview = projection.mapping_preview || {};
    var advanced = [
      ["What Auteur will carry forward", preview.becomes_canonical || []],
      ["Useful context kept for later", preview.remains_downstream_guidance || []],
      ["Source details preserved", preview.preserved_as_provenance || []],
      ["Still unresolved", preview.unresolved_not_representable || []],
    ];
    $("identity-candidate").innerHTML =
      "<h3>" + escapeHtml(candidate.title) + "</h3>" +
      '<p class="story-core-answer">' + escapeHtml(candidate.core_answer) + "</p>" +
      detailsRow(
        "Advanced: what Auteur records",
        advanced.map(function (group) {
          return "<h4>" + escapeHtml(group[0]) + "</h4>" + listHtml(group[1]);
        }).join("")
      ) +
      '<button id="accept-story-identity" class="continue-button">Yes, keep going</button>';
    $("accept-story-identity").addEventListener("click", function () {
      sendAction("accept-identity", {}, "Keeping this story core");
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
      state.structureCustomize = false;
      question.textContent = "✓ Story foundation ready";
      optionsBox.innerHTML =
        '<p class="completion-state">Your direction, story core, and story shape are set.</p>' +
        '<p class="phase-complete-next"><strong>Next:</strong> let Auteur prepare Chapter 1.</p>';
      $("card-why-now").textContent = "";
      $("card-recommendation").textContent = "";
      $("card-consequence").textContent = "";
      $("card-warnings").innerHTML = "";
      $("save-feedback").textContent = "Accepted story foundation.";
      $("continue-button").disabled = true;
      $("continue-button").hidden = true;
      $("continue-button").textContent = "Story foundation ready";
      $("continue-button").dataset.reviewStage = "";
      return;
    }
    $("decision-card").classList.remove("is-complete");
    $("continue-button").hidden = false;

    var structureEntry = structureNavigatorEntry(projection);
    var freshRecommendedShape =
      card &&
      card.stage === "story_structure" &&
      structureEntry &&
      structureEntry.answered_cards === 0 &&
      !(projection.revision || {}).active_revision_id &&
      !state.structureCustomize;
    if (freshRecommendedShape) {
      state.currentCardId = null;
      question.textContent = "Recommended story shape";
      $("card-position").textContent = "Auteur can choose sensible mystery defaults for you";
      optionsBox.innerHTML =
        '<div class="recommended-shape">' +
        '<p><strong>Start with Auteur\'s recommended pacing, clue distribution, and revelation style.</strong></p>' +
        '<p>You can customize each craft decision instead if you already know what you want.</p>' +
        '<div class="surface-actions">' +
        '<button id="use-recommended-story-shape" type="button" class="continue-button">Use recommended story shape</button>' +
        '<button id="customize-story-shape" type="button">Customize story shape</button>' +
        "</div></div>";
      $("card-why-now").textContent =
        "This keeps the beginner path moving while preserving the full craft controls on demand.";
      $("card-recommendation").textContent = "";
      $("card-consequence").textContent =
        "You can revise the story shape later; this chooses Auteur's current recommendations as the starting point.";
      $("card-warnings").innerHTML = "";
      $("save-feedback").textContent = "";
      $("continue-button").hidden = true;
      $("continue-button").dataset.reviewStage = "";
      $("use-recommended-story-shape").addEventListener("click", useRecommendedStoryShape);
      $("customize-story-shape").addEventListener("click", function () {
        state.structureCustomize = true;
        renderDecisionCard(projection);
      });
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
      body.innerHTML =
        '<div class="completion-summary phase-complete-banner" role="status">' +
        '<strong>Story foundation ready.</strong> Your direction, story core, and story shape are set.' +
        '<span>Next: prepare Chapter 1.</span></div>';
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
          var openClass = projection.primary_action && projection.primary_action.action_id === openAction
            ? "review-action primary-action"
            : "review-action";
          inner.push('<button class="' + openClass + '" data-command="open-review" data-stage="' + escapeHtml(stage) + '">Review ' + escapeHtml(stageLabel(stage)) + " →</button>");
        }
        if (actions.indexOf(acceptAction) >= 0) {
          var acceptLabel = stage === "discover" ? "Use this direction" :
            (stage === "story_identity" ? "Keep this story core" : "Use this story shape");
          var acceptClass = projection.primary_action && projection.primary_action.action_id === acceptAction
            ? "review-action primary-action"
            : "review-action";
          inner.push('<button class="' + acceptClass + '" data-command="' + acceptAction + '">' + acceptLabel + "</button>");
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
          var revisedClass = projection.primary_action && projection.primary_action.action_id === revisedAcceptAction
            ? "review-action primary-action"
            : "review-action";
          inner.push('<button class="' + revisedClass + '" data-command="' + revisedAcceptAction + '">' + revisedLabel + "</button>");
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
      MAPS_TO_CANON: "Will become part of the accepted story",
      CONTRIBUTES_TO_CANON: "May shape the accepted story",
      GUIDANCE_CONTEXT: "Will remain supporting context",
      PROVENANCE_ONLY: "Will remain source history",
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
    var continuation = projection.continuation;
    var acceptedIds = (projection.canonical_refs || []).map(function (ref) { return ref.milestone_id; });
    var foundationAccepted = !((projection.revision || {}).active_revision_id) &&
      acceptedIds.indexOf("whole_story_structure") >= 0;
    var stepByStepLabels = {
      "propose-outline": "Create outline proposal",
      "accept-outline": "Continue with this outline",
      "propose-chapter-plan": "Plan Chapter 1",
      "accept-chapter-plan": "Continue with this chapter plan",
      "propose-scene-plans": "Plan scenes",
      "accept-scene-plans": "Continue with these scene plans",
      "prepare-draft-handoff": "Prepare Chapter 1 draft",
    };
    var projectedPrimary = projection.primary_action || null;
    var available = projection.available_actions || [];

    if (!continuation && !foundationAccepted) {
      body.innerHTML = '<p class="muted">Finish the story shape to start Chapter 1.</p>';
      return;
    }

    var html = [];
    if (continuation && continuation.stale) {
      html.push(
        '<p class="blocking-inline" role="alert">' +
        escapeHtml(continuation.stale_reason || "The story changed; review the Chapter 1 plan before drafting.") +
        "</p>"
      );
    }

    var planningReady = continuation && continuation.draft_handoff &&
      continuation.draft_handoff.status === "ready";
    var drafted = continuation && continuation.draft_status === "drafted";
    var accepted = continuation && continuation.draft_status === "accepted";

    if (foundationAccepted && !planningReady && !drafted && !accepted) {
      html.push(
        '<section class="phase-transition chapter-launch" role="status" aria-label="Chapter 1 planning">' +
        '<p class="phase-transition-kicker">Story foundation ready</p>' +
        '<h3>Ready for Chapter 1</h3>' +
        '<p>Auteur can build the working outline, Chapter 1 plan, and scene plan as one planning step. ' +
        'Auteur keeps those planning details separate so you can inspect them if you want.</p>' +
        "</section>"
      );

      if (state.continuationCustomize) {
        if (continuation && continuation.outline_proposal) {
          html.push("<h3>Whole-story outline</h3><p>" + escapeHtml(continuation.outline_proposal.title) + "</p>");
          html.push(listHtml((continuation.outline_proposal.chapters || []).map(function (chapter) {
            return "Chapter " + chapter.chapter_index + ": " + chapter.purpose;
          })));
        }
        if (continuation && continuation.chapter_plan) {
          html.push("<h3>Chapter 1 plan</h3><p>" + escapeHtml(continuation.chapter_plan.what_changes) + "</p>");
        }
        if (continuation && continuation.scene_plans && continuation.scene_plans.length) {
          html.push("<h3>Scene plan</h3>" + listHtml(continuation.scene_plans.map(function (scene) {
            return scene.scene_id + ": " + scene.purpose;
          })));
        }
        var stepAction = projectedPrimary && stepByStepLabels[projectedPrimary.action_id]
          ? projectedPrimary.action_id
          : available.filter(function (action) { return stepByStepLabels[action]; })[0];
        if (stepAction) {
          html.push(
            '<button type="button" class="continue-button primary-next-action" data-continuation-action="' +
            escapeHtml(stepAction) + '">' + escapeHtml(stepByStepLabels[stepAction]) + " →</button>"
          );
        }
        html.push('<button type="button" data-streamlined-planning>Use streamlined planning</button>');
      } else {
        html.push(
          '<div class="surface-actions">' +
          '<button type="button" class="continue-button primary-next-action" data-chapter-launch="prepare">Plan Chapter 1 →</button>' +
          '<button type="button" data-continuation-customize>Plan step by step</button>' +
          "</div>"
        );
        if (projectedPrimary && projectedPrimary.reason) {
          html.push('<p class="muted primary-action-reason">' + escapeHtml(projectedPrimary.reason) + "</p>");
        }
      }
    }

    if (planningReady && !drafted && !accepted) {
      html.push(
        '<section class="chapter-launch-summary">' +
        '<p class="phase-transition-kicker">Chapter 1 launch</p>' +
        '<h3>Here is how Auteur will approach Chapter 1</h3>'
      );
      if (continuation.outline_proposal) {
        html.push("<p><strong>Story direction:</strong> " + escapeHtml(continuation.outline_proposal.title) + "</p>");
      }
      if (continuation.chapter_plan) {
        html.push("<p><strong>What Chapter 1 changes:</strong> " + escapeHtml(continuation.chapter_plan.what_changes) + "</p>");
      }
      if (continuation.scene_plans && continuation.scene_plans.length) {
        html.push(
          "<p><strong>Likely movement:</strong></p>" +
          listHtml(continuation.scene_plans.map(function (scene) { return scene.purpose; }))
        );
      }
      html.push(
        detailsRow(
          "Planning details",
          (continuation.outline_proposal
            ? "<h4>Whole-story outline</h4>" +
              listHtml((continuation.outline_proposal.chapters || []).map(function (chapter) {
                return "Chapter " + chapter.chapter_index + ": " + chapter.purpose;
              }))
            : "") +
          (continuation.scene_plans && continuation.scene_plans.length
            ? "<h4>Scene plan</h4>" +
              listHtml(continuation.scene_plans.map(function (scene) {
                return scene.scene_id + ": " + scene.purpose;
              }))
            : "")
        ) +
        '<button type="button" class="continue-button primary-next-action" data-chapter-launch="draft">Draft Chapter 1 →</button>' +
        "</section>"
      );
    }

    if (drafted) {
      html.push(
        '<section class="chapter-launch-summary">' +
        '<h3>Chapter 1 is ready</h3>' +
        '<p>Read the generated draft below. It is still a working draft until you explicitly keep it.</p>' +
        '<button type="button" class="continue-button primary-next-action" data-chapter-launch="read">Read Chapter 1 →</button>' +
        "</section>"
      );
    } else if (accepted) {
      html.push(
        '<section class="chapter-launch-summary"><h3>Chapter 1 is kept</h3>' +
        '<p>The accepted chapter is now part of the story.</p></section>'
      );
    }

    body.innerHTML = html.join("");

    var planButton = body.querySelector('[data-chapter-launch="prepare"]');
    if (planButton) planButton.addEventListener("click", prepareChapterLaunch);
    var draftButton = body.querySelector('[data-chapter-launch="draft"]');
    if (draftButton) draftButton.addEventListener("click", draftAndShowChapterOne);
    var readButton = body.querySelector('[data-chapter-launch="read"]');
    if (readButton) readButton.addEventListener("click", function () { openChapterReview(1); });

    var customize = body.querySelector("[data-continuation-customize]");
    if (customize) customize.addEventListener("click", function () {
      state.continuationCustomize = true;
      renderContinuation(projection);
    });
    var streamline = body.querySelector("[data-streamlined-planning]");
    if (streamline) streamline.addEventListener("click", function () {
      state.continuationCustomize = false;
      renderContinuation(projection);
    });

    var stepButton = body.querySelector("[data-continuation-action]");
    if (stepButton) stepButton.addEventListener("click", function () {
      var action = stepButton.getAttribute("data-continuation-action");
      sendAction(action, {}, stepButton.textContent.trim());
    });
  }

  function render(projection) {
    if (!projection) {
      return;
    }
    rememberProjection(projection);
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

  function bookUpdateStatusLabel(status) {
    var labels = {
      not_started: "not started",
      reconciled: "up to date",
      partially_reconciled: "partly updated",
      divergent: "needs review",
      abandoned: "stopped",
      superseded: "replaced by a newer update",
    };
    return labels[status] || String(status || "not started").replace(/_/g, " ");
  }

  function bookAuthorityLabel(status) {
    if (!status || status === "DERIVED / NOT CANON") return "WORKING / NOT ACCEPTED";
    return String(status).replace(/DERIVED/g, "WORKING").replace(/NOT CANON/g, "NOT ACCEPTED");
  }

  function renderBookNoticeList(items, emptyText) {
    var notices = items || [];
    if (!notices.length) return '<p class="muted">' + escapeHtml(emptyText) + "</p>";
    return '<ul class="book-orientation-list">' + notices.map(function (item) {
      var chapter = item.chapter_index ? "Chapter " + item.chapter_index + " · " : "";
      return "<li><strong>" + escapeHtml(chapter + (item.state || "")) +
        "</strong><br>" + escapeHtml(item.summary || "") + "</li>";
    }).join("") + "</ul>";
  }

  function renderBookProgress(progress) {
    var chapter = Number(progress.current_chapter || 1);
    var chapterState = progress.current_chapter_state || "Working";
    $("book-current-position").textContent = "Chapter " + chapter + " · " + chapterState;
    $("book-orientation-reason").textContent =
      progress.orientation_reason || "Auteur is orienting this Book from kept and working Chapter state.";
    $("book-recent-changes").innerHTML = renderBookNoticeList(
      progress.recent_changes,
      "No kept story changes yet."
    );
    $("book-pending-updates").innerHTML = renderBookNoticeList(
      progress.pending_updates,
      "Nothing unresolved is currently blocking your writing."
    );
    $("book-needs-attention").innerHTML = renderBookNoticeList(
      progress.needs_attention,
      "Nothing needs attention."
    );
    $("book-next-story-action").textContent =
      progress.next_story_action || "Continue writing";
    var openChapter = $("book-open-current-chapter");
    var actionChapter = Number(progress.next_action_chapter);
    if (Number.isInteger(actionChapter) && actionChapter > 0) {
      openChapter.hidden = false;
      openChapter.dataset.chapter = String(actionChapter);
      openChapter.textContent = "Open Chapter " + actionChapter;
    } else {
      openChapter.hidden = true;
      openChapter.dataset.chapter = "";
    }

    $("book-progress-summary").textContent =
      progress.accepted_chapters + " accepted chapter(s) · " +
      progress.planned_chapters + " planned chapter(s).";
    $("book-expression-status").textContent = progress.book_expression || "missing";
    $("book-reconciliation-status").textContent = bookUpdateStatusLabel(progress.reconciliation_status);
    $("book-next-command").textContent = progress.next_command || "No owning command is currently required.";
    $("book-authority-status").textContent = bookAuthorityLabel(progress.authority_status);

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

  function openChapterReview(chapter) {
    var url = new URL(window.location.href);
    url.searchParams.set("chapter", String(chapter));
    window.history.pushState({}, "", url.pathname + url.search);
    return loadPostDraftReview();
  }

  function renderPostDraftReview(chapter, review) {
    var panel = $("post-draft-review");
    if (!panel) return;
    panel.hidden = false;
    $("post-draft-heading").textContent = "Chapter " + chapter;
    $("post-draft-status").textContent =
      "Chapter " + chapter + " · " + String(review.production_status || "unknown").replace(/_/g, " ");
    $("post-draft-next-action").textContent = review.recommended_next_action || "Review the current chapter state.";

    var evidence = [];
    if (typeof review.draft_text === "string") {
      evidence.push(
        '<article class="chapter-draft"><h4>Chapter ' + chapter + ' draft</h4>' +
        '<div class="draft-prose" aria-label="Chapter draft prose">' +
        escapeHtml(review.draft_text) +
        "</div></article>"
      );
    }
    var reviewNotes = [];
    if (review.blocking_findings && review.blocking_findings.length) {
      reviewNotes.push("<h4>Needs attention</h4>" + listHtml(review.blocking_findings));
    }
    if (review.warnings && review.warnings.length) {
      reviewNotes.push("<h4>Auteur noticed</h4>" + listHtml(review.warnings));
    }
    if (review.plan_alignment) {
      reviewNotes.push(
        "<h4>Planning comparison</h4><pre>" +
        escapeHtml(JSON.stringify(review.plan_alignment, null, 2)) +
        "</pre>"
      );
    }
    if (reviewNotes.length) {
      evidence.push(detailsRow("Auteur review", reviewNotes.join("")));
    }
    $("post-draft-evidence").innerHTML = evidence.join("") ||
      '<p class="muted">No Chapter ' + chapter + ' draft exists yet.</p>';

    var accept = $("post-draft-accept");
    var revise = $("post-draft-revise");
    var planNext = $("post-draft-plan-next");
    var reconcile = $("post-draft-reconcile");
    var needsReconciliation =
      !!review.reconciliation_available &&
      !review.accepted &&
      !!review.source_draft &&
      !review.stale;

    reconcile.hidden = !needsReconciliation;
    if (needsReconciliation) {
      var discoveries = review.creative_discoveries || [];
      $("post-draft-discoveries").innerHTML = discoveries.length
        ? discoveries.map(function (item) {
            return '<article class="discovery-chip"><strong>' +
              escapeHtml(item.label || "Story change") +
              '</strong><p>' + escapeHtml(item.value || "") + "</p></article>";
          }).join("")
        : '<p>Auteur noticed that the draft changed after its previous review.</p>';
    }

    accept.hidden =
      review.accepted ||
      !review.source_draft ||
      review.stale ||
      !!review.review_stale ||
      needsReconciliation ||
      (review.blocking_findings || []).length > 0;
    revise.hidden = review.accepted || !review.source_draft || needsReconciliation;
    planNext.hidden = !review.accepted;
    accept.textContent = "Keep this draft";
    revise.textContent = "Revise";
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
    if (!window.confirm("Keep this Chapter " + chapter + " draft as the accepted version?")) {
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
        return loadProjection().then(function () {
          return loadPostDraftReview();
        });
      })
      .catch(function (error) {
        setStatus("Chapter acceptance failed: " + error.message);
      });
  }

  function resolveCreativeDivergence(decision) {
    var chapter = currentChapterFromQuery();
    if (!chapter) return Promise.resolve(null);
    var label = decision === "keep_and_reconcile"
      ? "Keeping the draft and preparing story updates…"
      : (decision === "keep_intentional_divergence"
        ? "Keeping the draft as an intentional divergence…"
        : "Preparing a revision toward the plan…");
    setStatus(label);
    return fetch("/api/beginner/chapters/" + chapter + "/reconcile-new-elements", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        command_id: nextCommandId("reconcile-new-elements"),
        decision: decision,
      }),
    })
      .then(readJson)
      .then(function (result) {
        if (decision === "revise_to_plan") {
          return sendAction("draft-chapter-1", {}, "Revising Chapter " + chapter)
            .then(function () { return loadPostDraftReview(); });
        }
        setStatus(
          decision === "keep_and_reconcile"
            ? "Draft kept. Auteur prepared " + String(result.proposal_count || 0) + " suggested story update(s)."
            : "Draft kept. The difference from the current plan remains intentional."
        );
        loadBookProgress();
        return loadProjection().then(function () { return loadPostDraftReview(); });
      })
      .catch(function (error) {
        setStatus("Could not resolve the story change: " + error.message);
        return null;
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
        return sendAction("draft-chapter-1", {}, "Revising Chapter " + chapter);
      })
      .then(function () {
        return loadPostDraftReview();
      })
      .catch(function (error) {
        setStatus("Chapter revision failed: " + error.message);
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

  function currentQuickDraftFromQuery() {
    try {
      var params = new URLSearchParams(window.location.search);
      return params.get("quick_draft");
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
      if (
        state.currentProjection &&
        state.currentProjection.primary_surface === "architecture" &&
        !state.activeLensId
      ) {
        var lenses = orderedStoryLenses(
          (state.currentProjection.story_orientation || {}).story_lenses || []
        );
        if (lenses.length) state.activeLensId = lenses[0].lens_id;
        renderInspector(state.currentProjection);
      }
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
    var quickDraftFromQuery = currentQuickDraftFromQuery();
    if (fromQuery) {
      state.workspaceId = fromQuery;
      $("workspace-id").value = fromQuery;
      loadProjection();
      loadPostDraftReview();
      loadBookProgress();
    } else {
      showHome();
      loadRecentStories();
      if (quickDraftFromQuery) {
        state.quickDraftSessionId = quickDraftFromQuery;
        loadQuickDraftSession(quickDraftFromQuery);
      }
    }
    $("new-story-form").addEventListener("submit", function (event) {
      event.preventDefault();
      createStoryFromHome();
    });
    $("quick-draft-start").addEventListener("click", startQuickDraft);
    $("quick-draft-copy-handoff").addEventListener("click", copyQuickDraftHandoff);
    $("quick-draft-check-result").addEventListener("click", checkQuickDraftResult);
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) scheduleQuickDraftPoll();
    });
    $("quick-draft-editor").addEventListener("input", function () {
      state.quickDraftDirty = true;
      state.quickDraftDiscoveriesVisible = false;
      state.quickDraftDiscoveries = [];
      $("quick-draft-discoveries").innerHTML =
        '<p class="muted">Draft changed. Save it before reviewing discoveries.</p>';
    });
    $("quick-draft-save").addEventListener("click", saveQuickDraft);
    $("quick-draft-discover").addEventListener("click", discoverQuickDraftElements);
    $("quick-draft-shape").addEventListener("click", shapeQuickDraftStory);
    $("refresh-stories").addEventListener("click", loadRecentStories);
    $("home-button").addEventListener("click", function () {
      state.workspaceId = null;
      updateWorkspaceUrl(null);
      showHome();
      loadRecentStories();
    });
    $("workspace-form").addEventListener("submit", function (event) {
      event.preventDefault();
      var value = $("workspace-id").value.trim();
      if (!value) {
        $("home-status").textContent = "Enter a workspace ID to open.";
        return;
      }
      setSaveFeedback("");
      openWorkspace(value);
    });
    window.addEventListener("popstate", function () {
      var workspace = currentWorkspaceFromQuery();
      var quickDraft = currentQuickDraftFromQuery();
      if (workspace) {
        openWorkspace(workspace, false);
      } else {
        state.workspaceId = null;
        showHome();
        loadRecentStories();
        if (quickDraft) {
          state.quickDraftSessionId = quickDraft;
          loadQuickDraftSession(quickDraft);
        }
      }
    });
    $("continue-architecture").addEventListener("click", function () {
      sendAction("continue-architecture", {}, "Continue with this interpretation");
    });
    $("refine-architecture").addEventListener("click", function () {
      $("refinement-panel").open = true;
      $("refinement-panel").scrollIntoView({ behavior: "smooth", block: "start" });
    });
    $("explain-architecture").addEventListener("click", function () {
      if (state.currentProjection && state.currentProjection.story_orientation) {
        var lenses = orderedStoryLenses(state.currentProjection.story_orientation.story_lenses || []);
        if (lenses.length) setActiveStoryLens(lenses[0].lens_id);
      }
    });
    $("reset-lens-layout").addEventListener("click", function () {
      try {
        window.localStorage.removeItem(storyLensLayoutKey());
      } catch (error) {
        // Layout storage is optional and never blocks story work.
      }
      if (state.currentProjection) renderArchitectureSurface(state.currentProjection);
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
    $("post-draft-keep-reconcile").addEventListener("click", function () {
      resolveCreativeDivergence("keep_and_reconcile");
    });
    $("post-draft-keep-divergence").addEventListener("click", function () {
      resolveCreativeDivergence("keep_intentional_divergence");
    });
    $("post-draft-revise-plan").addEventListener("click", function () {
      resolveCreativeDivergence("revise_to_plan");
    });
    $("post-draft-plan-next").addEventListener("click", loadNextChapterPlan);
    $("book-open-current-chapter").addEventListener("click", function () {
      var chapter = Number($("book-open-current-chapter").dataset.chapter);
      if (Number.isInteger(chapter) && chapter > 0) openChapterReview(chapter);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
