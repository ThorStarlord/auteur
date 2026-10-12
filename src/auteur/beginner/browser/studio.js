(function () {
  "use strict";
  var state = { items: [], connections: [], positions: {}, selected: null, selectedDerived: null, derived: null, derivedPositions: {}, view: "architecture", focusGroup: "", panX: 0, panY: 0, zoom: 1, serial: 0, undo: null };
  // Local, noncanonical working document: server is the persistence owner.
  var remote = { canvasId: null, revision: 0, ready: false, failed: false, queue: Promise.resolve(), timer: null, savedSnapshot: null };
  state.deleted = {};
  state.architecture = null; state.candidatePositions = {}; state.selectedCandidate = null;
  state.architectureFocus = ""; state.architectureCenter = null;
  state.architectureFacet = "overview"; state.facetSelection = null; state.facetHistory = [];
  state.selectedPhase = null; state.lastWorkingSelection = null;
  state.explanationArrival = null; state.explanationInspectRequested = false;
  state.architectureRequestSha = null; state.architectureReview = null;
  state.workspace = "architecture"; state.lastRealizationView = "create";
  state.realization = null; state.realizationRequestSha = null;
  state.realizationStale = false;
  state.realizationReview = null; state.realizationPositions = {}; state.selectedRealization = null;
  function showRecoveryAction() {
    $("restore-deleted").hidden = !remote.ready || remote.failed || !Object.keys(state.deleted).length;
  }
  function apiJson(response) {
    return response.json().then(function (body) {
      if (!response.ok) throw new Error(body.error || "HTTP " + response.status);
      return body;
    });
  }
  function snapshot() {
    return { items: JSON.parse(JSON.stringify(state.items)),
      connections: JSON.parse(JSON.stringify(state.connections)),
      positions: JSON.parse(JSON.stringify(state.positions)),
      viewport: { pan_x: state.panX, pan_y: state.panY, zoom: state.zoom } };
  }
  function queueSave() {
    if (!remote.ready || remote.failed) return;
    var payload = snapshot(), command = id("save");
    remote.queue = remote.queue.then(function () {
      if (remote.failed) return;
      return fetch("/api/beginner/studio/canvases/" + remote.canvasId + "/commands/replace-working-document", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ expected_revision: remote.revision, command_id: command, payload: payload })
      }).then(apiJson).then(function (doc) {
        remote.revision = doc.revision;
        remote.savedSnapshot = JSON.stringify(payload);
        state.deleted = doc.deleted || {}; showRecoveryAction();
        if (!remote.failed) status("Working canvas saved locally · revision " + remote.revision);
      });
    }).catch(function (error) {
      remote.failed = true;
      $("retry-save").hidden = false;
      status("SAVE FAILED: " + error.message + ". Do not reload; export your work before recovery.");
    });
    return remote.queue;
  }
  function scheduleSave() {
    clearTimeout(remote.timer);
    remote.timer = setTimeout(function () { remote.timer = null; queueSave(); }, 300);
  }
  // Presentation-only local preference: story content stays in CanvasStore.
  function focusKey() { return "auteur:studio:focus:" + remote.canvasId; }
  function rememberFocus() {
    if (!remote.ready || !remote.canvasId) return;
    var open = !$("scene-panel").hidden;
    var field = open ? $("scene-text") : $("content");
    try {
      var previous = JSON.parse(window.localStorage.getItem(focusKey()) || "null");
      window.localStorage.setItem(focusKey(), JSON.stringify({
        selected: state.selected || (previous && previous.selected) || null,
        view: state.view, workspace: state.workspace, group: state.focusGroup,
        candidate: state.selectedCandidate, realization: state.selectedRealization, scope: state.architectureFocus,
        neighborhood: state.architectureCenter,
        facet: state.architectureFacet, facetSelection: state.facetSelection,
        phase: state.selectedPhase, search: $("find-nodes").value,
        editorOpen: open, expanded: open && $("scene-panel").classList.contains("expanded"),
        caret: field.selectionStart || 0
      }));
    } catch (error) { status("Your canvas is saved; this browser cannot remember the current focus: " + error.message); }
  }
  function restoreFocus() {
    var saved;
    try { saved = JSON.parse(window.localStorage.getItem(focusKey()) || "null"); }
    catch (error) { status("Previous focus unavailable; working canvas remains safe: " + error.message); return null; }
    if (!saved) return null;
    state.focusGroup = typeof saved.group === "string" ? saved.group : "";
    state.view = ["create", "realization_candidates", "relationships", "all", "architecture", "genre_timeline"].includes(saved.view) ? saved.view : "create";
    state.selectedCandidate = saved.candidate || null;
    state.selectedRealization = saved.realization || null;
    state.workspace = saved.workspace === "architecture" || ["architecture", "genre_timeline"].includes(state.view)
      ? "architecture" : "realization";
    state.architectureFocus = saved.scope || "";
    state.architectureCenter = saved.neighborhood || null;
    var facets = ["overview", "emotions", "genres", "tropes", "structure", "timeline"];
    state.architectureFacet = facets.includes(saved.facet) ? saved.facet :
      (state.view === "genre_timeline" ? "timeline" : "overview");
    state.facetSelection = typeof saved.facetSelection === "string" ? saved.facetSelection : null;
    state.selectedPhase = typeof saved.phase === "string" ? saved.phase : null;
    $("find-nodes").value = typeof saved.search === "string" ? saved.search : "";
    if (state.workspace === "architecture") state.view = state.architectureFacet === "timeline"
      ? "genre_timeline" : "architecture";
    if (state.items.some(function (item) { return item.id === saved.selected; })) state.selected = saved.selected;
    state.lastWorkingSelection = state.selected;
    if (["create", "relationships", "all"].includes(state.view) && !visibleWorking(selected())) {
      state.view = "create"; state.focusGroup = "";
    }
    $("layer-view").value = state.view;
    return saved;
  }

  function architectureUrl() {
    return "/api/beginner/studio/canvases/" + encodeURIComponent(remote.canvasId) + "/architecture";
  }
  function candidateNode(id) {
    return state.architecture && state.architecture.nodes.find(function (node) { return node.id === id; });
  }
  function candidateVisible(node) {
    if (state.view !== "architecture" || !matches(node)) return false;
    if (state.architectureCenter) {
      var center = state.architectureCenter, origin = candidateNode(center);
      if (!origin) return true;
      return node.id === center || node.parent_id === center || origin.parent_id === node.id ||
        state.architecture.links.some(function (edge) {
          return (edge.source === center && edge.target === node.id) ||
            (edge.target === center && edge.source === node.id);
        });
    }
    return !state.architectureFocus || node.scope === state.architectureFocus || node.scope === "whole_story";
  }
  function updateArchitectureScopes() {
    var picker = $("architecture-scope"), scopes = new Set();
    if (state.architecture) {
      state.architecture.nodes.forEach(function (node) { scopes.add(node.scope || "whole_story"); });
      state.architecture.phases.forEach(function (phase) { scopes.add(phase.scope || "whole_story"); });
    }
    picker.replaceChildren();
    var all = document.createElement("option"); all.value = ""; all.textContent = "Whole architecture"; picker.appendChild(all);
    Array.from(scopes).sort().forEach(function (scope) {
      var opt = document.createElement("option"); opt.value = scope; opt.textContent = scope.replace(/_/g, " ");
      picker.appendChild(opt);
    });
    if (!scopes.has(state.architectureFocus)) state.architectureFocus = "";
    picker.value = state.architectureFocus;
  }
  function applyArchitectureProjection(projection, openGraph) {
    if (state.architectureRequestSha && state.architectureRequestSha !== projection.candidate_request_sha256) {
      state.facetHistory = []; state.explanationArrival = null; state.explanationInspectRequested = false;
      state.facetSelection = null;
    }
    state.architecture = projection.candidate;
    if (state.selectedPhase && (!state.architecture ||
        !state.architecture.phases.some(function (p) { return p.id === state.selectedPhase; })))
      state.selectedPhase = null;
    state.architectureReview = projection.review || null;
    if (state.architectureCenter && !candidateNode(state.architectureCenter)) state.architectureCenter = null;
    if (state.selectedCandidate && !candidateNode(state.selectedCandidate)) state.selectedCandidate = null;
    if (state.facetSelection && !architectureFacetEntries(state.architectureFacet).some(function (e) {
      return e.key === state.facetSelection;
    })) state.facetSelection = null;
    state.facetHistory = state.facetHistory.filter(function (old) {
      return (!old.nodeId || candidateNode(old.nodeId)) &&
        (!old.key || architectureFacetEntries(old.facet).some(function (e) { return e.key === old.key; }));
    });
    state.architectureRequestSha = projection.candidate_request_sha256;
    state.candidatePositions = {};
    if (state.architecture) {
      var categories = ["reader_experience", "aesthetic", "genre", "engine", "trope", "structure", "theme", "thread"];
      state.architecture.nodes.slice().sort(function (a, b) {
        return categories.indexOf(a.category) - categories.indexOf(b.category) ||
          a.title.localeCompare(b.title);
      }).forEach(function (node, i) {
        state.candidatePositions[node.id] = { x: 40 + (i % 7) * 188, y: 40 + Math.floor(i / 7) * 100 };
      });
    }
    $("architecture-handoff").hidden = !projection.request;
    $("architecture-request").value = projection.request ? JSON.stringify(projection.request, null, 2) : "";
    $("architecture-review").hidden = !state.architectureReview;
    $("architecture-diff").replaceChildren();
    if (state.architectureReview) {
      var review = state.architectureReview;
      $("architecture-review-summary").textContent = review.candidate.summary;
      ["nodes", "links", "phases", "emotion_targets", "complex_emotions",
        "genre_contracts", "genre_interactions"].forEach(function (kind) {
        ["added", "removed", "changed"].forEach(function (verb) {
          var ids = (review.changes[kind] || {})[verb] || [];
          if (!ids.length) return;
          var li = document.createElement("li");
          li.textContent = kind + " " + verb + ": " + ids.join(", ");
          $("architecture-diff").appendChild(li);
        });
      });
      if (review.changes.summary_changed) {
        var summary = document.createElement("li");
        summary.textContent = "Governing summary changed"; $("architecture-diff").appendChild(summary);
      }
    }
    $("architecture-status").textContent = projection.status === "review_ready"
      ? "A revised proposal is ready for review. Current working architecture is unchanged."
      : projection.status === "awaiting_host_agent"
      ? "Awaiting the active coding agent. Prior working proposal remains available if present."
      : projection.status === "stale"
      ? "Working architecture is outdated relative to your Story Vision. Regenerate or revise before developing concrete story material."
      : projection.status === "ready" ? "Agent proposal ready · working, not accepted story."
      : "Describe a vision and ask the coding agent to develop the architecture.";
    updateArchitectureScopes();
    if (openGraph && state.architecture) {
      state.view = "architecture"; $("layer-view").value = state.view;
      state.selectedCandidate = null;
    }
    render(); rememberFocus();
  }
  function loadArchitecture() {
    var canvasId = remote.canvasId;
    return fetch(architectureUrl()).then(apiJson).then(function (projection) {
      if (remote.canvasId === canvasId) applyArchitectureProjection(projection, false);
    }).catch(function (error) {
      $("architecture-status").textContent = "Architecture unavailable: " + error.message;
    });
  }
  function requestArchitecture(instruction) {
    if (!remote.ready || remote.failed) { status("Save the working canvas before requesting architecture."); return; }
    if (!$("scene-panel").hidden) captureScene();
    if (remote.timer !== null) { clearTimeout(remote.timer); remote.timer = null; queueSave(); }
    else if (hasUnsavedChanges()) queueSave();
    $("architecture-status").textContent = "Saving creative intent and preparing exact coding-agent request...";
    Promise.resolve(remote.queue).then(function () {
      if (remote.failed) throw new Error("The working canvas did not save; no agent request was created.");
      return fetch(architectureUrl() + "/prepare", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ instruction: instruction || "" })
      }).then(apiJson);
    }).then(function (projection) {
      applyArchitectureProjection(projection, false);
      $("architecture-handoff").open = true;
      status("Host-agent request prepared. Ask your active coding agent to fulfill it; no provider was called automatically.");
    }).catch(function (error) {
      $("architecture-status").textContent = "Cannot request architecture: " + error.message;
    });
  }

  function applyReviewedArchitecture() {
    if (!remote.ready || remote.failed || !state.architectureReview) return;
    var canvasId = remote.canvasId, sha = state.architectureReview.request_sha256;
    if (!$("scene-panel").hidden) captureScene();
    if (remote.timer !== null) { clearTimeout(remote.timer); remote.timer = null; queueSave(); }
    else if (hasUnsavedChanges()) queueSave();
    Promise.resolve(remote.queue).then(function () {
      if (remote.failed) throw new Error("Working canvas has unsaved changes.");
      return fetch("/api/beginner/studio/canvases/" + encodeURIComponent(canvasId) + "/architecture/apply", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({request_sha256:sha})
      }).then(apiJson);
    }).then(function (projection) {
      if (remote.canvasId !== canvasId) return;
      applyArchitectureProjection(projection, true);
      status("Reviewed revision applied to working architecture only. Accepted story remains unchanged.");
    }).catch(function (error) {
      $("architecture-status").textContent = "Working revision not applied: " + error.message;
    });
  }
  function submitArchitecture() {
    var payload;
    try { payload = JSON.parse($("architecture-response").value); }
    catch (error) { $("architecture-status").textContent = "Response must be valid HostAgentResponse JSON."; return; }
    fetch(architectureUrl() + "/host-agent-response", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    }).then(apiJson).then(function (projection) {
      $("architecture-response").value = "";
      $("architecture-handoff").open = false;
      applyArchitectureProjection(projection, true);
      status("Source-bound candidate architecture loaded; no story meaning accepted.");
    }).catch(function (error) {
      $("architecture-status").textContent = "Response rejected: " + error.message;
    });
  }
  function chooseCandidate(id) {
    if (!$("scene-panel").hidden) { captureScene(); concealScene(); scheduleSave(); }
    state.selected = null; state.selectedDerived = null; state.selectedCandidate = id;
    state.facetSelection = null;
    renderFacetList(); renderInspector();
    Array.prototype.forEach.call(document.querySelectorAll(".node"), function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.itemId === id));
    });
    drawEdges(); rememberFocus();
  }

  function focusRelatedArchitecture() {
    if (!candidateNode(state.selectedCandidate)) return;
    state.architectureCenter = state.selectedCandidate;
    state.architectureFocus = ""; $("architecture-scope").value = "";
    render(); fit(); rememberFocus();
    status("Showing the selected narrative idea and directly related proposals. Use Show whole graph to return.");
  }
  function showWholeArchitecture() {
    state.architectureCenter = null; state.architectureFocus = "";
    $("architecture-scope").value = "";
    render(); fit(); rememberFocus();
  }
  function realizationUrl() {
    return "/api/beginner/studio/canvases/" + encodeURIComponent(remote.canvasId) + "/realization";
  }
  function realizationElement(id) {
    return state.realization && state.realization.elements.find(function (element) { return element.id === id; });
  }
  function realizationVisible(element) {
    return state.view === "realization_candidates" && matches({
      title: element.title, content: element.description, group: element.scope
    });
  }
  function applyRealizationProjection(projection, openGraph) {
    state.realization = projection.candidate;
    state.realizationStale = projection.status === "stale";
    state.realizationReview = projection.review || null;
    state.realizationRequestSha = projection.candidate_request_sha256;
    state.realizationPositions = {};
    if (state.realization) state.realization.elements.forEach(function (element, i) {
      state.realizationPositions[element.id] = {x: 40 + i % 7 * 188, y: 40 + Math.floor(i / 7) * 100};
    });
    $("realization-handoff").hidden = !projection.request;
    $("realization-request").value = projection.request ? JSON.stringify(projection.request, null, 2) : "";
    $("realization-review").hidden = !state.realizationReview;
    $("realization-diff").replaceChildren();
    if (state.realizationReview) {
      ["elements", "links", "architecture_feedback"].forEach(function (kind) {
        ["added", "removed", "changed"].forEach(function (action) {
          var ids = state.realizationReview.changes[kind][action];
          if (!ids.length) return;
          var li = document.createElement("li"); li.textContent = kind + " " + action + ": " + ids.join(", ");
          $("realization-diff").appendChild(li);
        });
      });
    }
    $("realization-status").textContent = projection.status === "review_ready"
      ? "Review the revised working realization before applying."
      : projection.status === "awaiting_host_agent"
      ? "Awaiting the coding agent. No concrete story material has been accepted."
      : projection.status === "stale"
      ? "This concrete proposal is stale relative to the current creative sources."
      : projection.status === "ready"
      ? "Working concrete story proposal ready. Not accepted."
      : "Develop concrete characters, locations, plots or events from the architecture.";
    if (openGraph && state.realization) {
      state.workspace = "realization"; state.view = "realization_candidates";
      state.lastRealizationView = "realization_candidates";
      state.selectedRealization = null; $("layer-view").value = state.view;
    }
    render(); rememberFocus();
  }
  function loadRealization() {
    var canvasId = remote.canvasId;
    return fetch(realizationUrl()).then(apiJson).then(function (projection) {
      if (remote.canvasId === canvasId) applyRealizationProjection(projection, false);
    }).catch(function (error) {
      $("realization-status").textContent = "Cannot load Story Realization: " + error.message;
    });
  }
  function requestRealization(instruction) {
    if (!remote.ready || remote.failed) { status("Save your working canvas before generating."); return; }
    if (!$("scene-panel").hidden) captureScene();
    if (remote.timer !== null) { clearTimeout(remote.timer); remote.timer = null; queueSave(); }
    else if (hasUnsavedChanges()) queueSave();
    var focus = candidateNode(state.selectedCandidate) ? [state.selectedCandidate] : [];
    var canvasId = remote.canvasId;
    $("realization-status").textContent = "Preparing exact, source-bound realization request...";
    Promise.resolve(remote.queue).then(function () {
      if (remote.canvasId !== canvasId) throw new Error("The active canvas changed.");
      if (remote.failed) throw new Error("Working changes were not saved.");
      return fetch("/api/beginner/studio/canvases/" + encodeURIComponent(canvasId) + "/realization/prepare", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({focus_ids: focus, instruction: instruction || ""})
      }).then(apiJson);
    }).then(function (projection) {
      if (remote.canvasId !== canvasId) return;
      applyRealizationProjection(projection, false);
      $("realization-handoff").open = true;
    }).catch(function (error) {
      $("realization-status").textContent = "Cannot request concrete story material: " + error.message;
    });
  }
  function submitRealization() {
    var payload;
    try { payload = JSON.parse($("realization-response").value); }
    catch (error) { $("realization-status").textContent = "Paste valid HostAgentResponse JSON."; return; }
    var canvasId = remote.canvasId;
    fetch(realizationUrl() + "/host-agent-response", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    }).then(apiJson).then(function (projection) {
      if (remote.canvasId !== canvasId) return;
      $("realization-response").value = "";
      $("realization-handoff").open = false;
      applyRealizationProjection(projection, projection.status === "ready");
      status("Concrete story proposal validated. Existing accepted fiction unchanged.");
    }).catch(function (error) {
      $("realization-status").textContent = "Realization response rejected: " + error.message;
    });
  }
  function applyRealizationReview() {
    if (!state.realizationReview || !remote.ready || remote.failed) return;
    var sha = state.realizationReview.request_sha256, canvasId = remote.canvasId;
    if (!$("scene-panel").hidden) captureScene();
    if (remote.timer !== null) { clearTimeout(remote.timer); remote.timer = null; queueSave(); }
    else if (hasUnsavedChanges()) queueSave();
    Promise.resolve(remote.queue).then(function () {
      if (remote.failed || remote.canvasId !== canvasId) throw new Error("Working canvas did not save safely.");
      return fetch("/api/beginner/studio/canvases/" + encodeURIComponent(canvasId) + "/realization/apply", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({request_sha256: sha})
      }).then(apiJson);
    }).then(function (projection) {
      if (remote.canvasId === canvasId) applyRealizationProjection(projection, true);
    }).catch(function (error) {
      $("realization-status").textContent = "Working revision blocked: " + error.message;
    });
  }
  function copyCandidate() {
    var original = candidateNode(state.selectedCandidate);
    if (!original || !remote.ready || remote.failed) return;
    if (state.items.length >= 200) { status("Working canvas item limit reached; use a focused proposal."); return; }
    var copy = { id: id("item"), title: original.title, kind: "note",
      group: "Architecture", content: original.summary + "\n\nOrigin: working agent proposal " +
      (state.architectureRequestSha || "unknown") + " / " + original.id + ". Not accepted." };
    state.items.push(copy); state.positions[copy.id] = availablePosition();
    state.selected = copy.id; state.selectedCandidate = null;
    state.workspace = "realization"; state.lastRealizationView = "create";
    state.view = "create"; $("layer-view").value = "create";
    render(); rememberFocus(); queueSave();
    status("Copied as editable working note. Original agent proposal remains available.");
  }
  function loadRemote(doc) {
    state.architecture = null; state.architectureReview = null; state.architectureCenter = null;
    state.selectedPhase = null;
    state.candidatePositions = {}; state.selectedCandidate = null;
    state.realization = null; state.realizationReview = null; state.realizationStale = false;
    state.realizationPositions = {}; state.selectedRealization = null;
    state.items = doc.items; state.connections = doc.connections; state.positions = doc.positions;
    state.view = "architecture"; state.workspace = "architecture"; state.focusGroup = "";
    state.selected = state.items.length ? state.items[0].id : null;
    state.panX = doc.viewport.pan_x; state.panY = doc.viewport.pan_y; state.zoom = doc.viewport.zoom;
    $("zoom").value = String(Math.round(state.zoom * 100));
    remote.revision = doc.revision; remote.ready = true;
    state.deleted = doc.deleted || {}; showRecoveryAction();
    remote.savedSnapshot = JSON.stringify(snapshot());
    var focus = restoreFocus();
    if (!focus) $("layer-view").value = state.view;
    state.lastWorkingSelection = state.selected;
    if (visionItem() && visionItem().content.trim()) $("vision-disclosure").open = false;
    render();
    if (focus && focus.editorOpen && selected() && selected().kind === "scene") {
      displayScene(focus.caret, focus.expanded);
    }
    loadArchitecture();
    loadRealization();
    status("Working canvas loaded · saved locally · revision " + remote.revision);
  }
  function hasUnsavedChanges() {
    return remote.ready &&
      (remote.failed || remote.savedSnapshot !== JSON.stringify(snapshot()));
  }
  function leaveForLegacy(href) {
    if (!$("scene-panel").hidden) captureScene();
    rememberFocus();
    if (!remote.ready) {
      status("Canvas is not loaded. Cannot safely leave for the previous interface yet.");
      return;
    }
    if (remote.failed) {
      status("Save failed. Export your working canvas before leaving.");
      return;
    }
    if (remote.timer !== null) {
      clearTimeout(remote.timer); remote.timer = null;
      queueSave();
    } else if (hasUnsavedChanges()) {
      queueSave();
    }
    status("Preserving working notes before switching interfaces...");
    Promise.resolve(remote.queue).then(function () {
      if (hasUnsavedChanges()) {
        throw new Error("Some working edits remain unsaved. Export your notes before leaving.");
      }
      window.location.assign(href);
    }).catch(function (error) {
      status("Could not switch interfaces safely: " + error.message);
    });
  }
  function canvasUrl(canvasId) {
    var params = new URLSearchParams(window.location.search);
    params.set("canvas", canvasId);
    return "/studio.html?" + params.toString();
  }
  function listCanvasChoices() {
    return fetch("/api/beginner/studio/canvases").then(apiJson).then(function (body) {
      var canvases = body.canvases || [], picker = $("canvas-picker");
      picker.replaceChildren();
      canvases.forEach(function (entry) {
        var option = document.createElement("option");
        option.value = entry.canvas_id;
        option.textContent = entry.title + (entry.state === "ready" ? " · " + entry.item_count + " items" : " · needs recovery");
        option.disabled = entry.state !== "ready";
        picker.appendChild(option);
      });
      picker.disabled = !canvases.some(function (entry) { return entry.state === "ready"; });
      if (remote.canvasId) picker.value = remote.canvasId;
      return canvases;
    });
  }
  function activateCanvas(canvasId) {
    remote.canvasId = canvasId;
    window.history.replaceState({}, "", canvasUrl(canvasId));
    return fetch("/api/beginner/studio/canvases", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ canvas_id: canvasId })
    }).then(apiJson).then(function (doc) {
      loadRemote(doc);
      return listCanvasChoices();
    }).catch(function (error) {
      remote.failed = true; $("retry-save").hidden = false;
      status("Cannot open working canvas: " + error.message + ". Do not overwrite earlier work.");
    });
  }
  function navigateCanvas(canvasId) {
    if (!/^[a-z0-9][a-z0-9_-]{0,79}$/.test(canvasId)) {
      status("Invalid working canvas identifier."); return;
    }
    if (!remote.ready) { window.location.assign(canvasUrl(canvasId)); return; }
    if (remote.failed) { status("Unsaved changes remain. Export a backup before switching canvases."); return; }
    // A pending edit must finish before navigation replaces this document.
    if (remote.timer !== null) {
      clearTimeout(remote.timer); remote.timer = null; queueSave();
    }
    $("canvas-picker").disabled = true;
    Promise.resolve(remote.queue).then(function () {
      if (remote.failed) throw new Error("Working changes were not saved. Export a backup before leaving.");
      window.location.assign(canvasUrl(canvasId));
    }).catch(function (error) {
      $("canvas-picker").disabled = false;
      status("Cannot switch canvases safely: " + error.message);
    });
  }
  function openRemote() {
    var canvas = new URLSearchParams(window.location.search).get("canvas");
    if (canvas) {
      if (!/^[a-z0-9][a-z0-9_-]{0,79}$/.test(canvas)) {
        remote.failed = true;
        status("Invalid canvas link. Return to Studio Home or use New canvas."); return;
      }
      activateCanvas(canvas); return;
    }
    // Bare /studio.html reopens recent work instead of silently making a new
    // empty canvas every time the author returns from Home.
    listCanvasChoices().then(function (canvases) {
      var recent = canvases.find(function (entry) { return entry.state === "ready"; });
      if (recent) activateCanvas(recent.canvas_id);
      else if (canvases.length) {
        remote.failed = true;
        status("Saved canvases need recovery. No new canvas was silently created. Choose New canvas to start fresh.");
      } else activateCanvas(id("canvas"));
    }).catch(function (error) {
      remote.failed = true;
      status("Cannot check existing canvases: " + error.message + ". No new canvas was created.");
    });
  }
  function restoreDeleted() {
    if (!remote.ready || remote.failed) return;
    // Flush a pending debounced edit so the recovery snapshot cannot discard it.
    if (remote.timer !== null) {
      clearTimeout(remote.timer); remote.timer = null; queueSave();
    }
    // Wait for all earlier saves before reading the current recovery journal.
    remote.queue.then(function () {
      if (remote.failed) throw new Error("Earlier save failed. Export your notes before attempting recovery.");
      return fetch("/api/beginner/studio/canvases/" + remote.canvasId).then(apiJson);
    }).then(function (doc) {
      if (doc.revision !== remote.revision) {
        remote.failed = true; $("retry-save").hidden = false; showRecoveryAction();
        throw new Error("Another tab changed this canvas. Export current notes; recovery cannot overwrite the new version.");
      }
      var deletedIds = Object.keys(doc.deleted || {});
      if (!deletedIds.length) { state.deleted = {}; showRecoveryAction(); return; }
      var itemId = deletedIds[deletedIds.length - 1], tombstone = doc.deleted[itemId];
      if (state.items.some(function (item) { return item.id === itemId; })) {
        throw new Error("Working item already exists. No recovery performed.");
      }
      state.items.push(tombstone.item);
      state.positions[itemId] = tombstone.position;
      (tombstone.connections || []).forEach(function (edge) {
        var sourceExists = state.items.some(function (item) { return item.id === edge.source; });
        var targetExists = state.items.some(function (item) { return item.id === edge.target; });
        if (sourceExists && targetExists && !state.connections.some(function (existing) { return existing.id === edge.id; })) {
          state.connections.push(edge);
        }
      });
      state.selected = itemId; state.selectedDerived = null;
      state.view = "create"; $("layer-view").value = "create";
      render(); queueSave();
      status("Removed working idea restored. Saving recovery locally.");
    }).catch(function (error) { status("Recovery unavailable: " + error.message); });
  }
  function retrySave() {
    if (!remote.ready) { window.location.reload(); return; }
    fetch("/api/beginner/studio/canvases/" + remote.canvasId).then(apiJson).then(function (doc) {
      if (doc.revision !== remote.revision) throw new Error("Another tab changed this canvas. Export your notes; do not overwrite newer content.");
      remote.failed = false; $("retry-save").hidden = true; queueSave();
    }).catch(function (error) { status("Cannot retry safely: " + error.message); });
  }
  var svgNS = "http://www.w3.org/2000/svg";
  function $(id) { return document.getElementById(id); }
  function status(message) { $("status").textContent = message; }
  function id(prefix) { state.serial += 1; return prefix + "-" + Date.now().toString(36) + "-" + state.serial; }
  function selected() { return state.items.find(function (item) { return item.id === state.selected; }); }
  function matches(item) {
    var query = $("find-nodes").value.trim().toLowerCase();
    return !query || ((item.title || "") + " " + (item.content || item.detail || "") + " " + (item.group || "")).toLowerCase().includes(query);
  }
  function visibleWorking(item) {
    var related = state.view === "relationships" && (item.kind === "character" ||
      state.connections.some(function (edge) { return edge.source === item.id || edge.target === item.id; }));
    return (state.view === "create" || state.view === "all" || related) &&
      (!state.focusGroup || item.group === state.focusGroup) && matches(item);
  }
  function renderGroups() {
    var picker = $("group-filter"), groups = Array.from(new Set(state.items.map(function (item) {
      return item.group || "";
    }).filter(Boolean))).sort();
    if (state.focusGroup && !groups.includes(state.focusGroup)) state.focusGroup = "";
    picker.replaceChildren();
    var all = document.createElement("option"); all.value = ""; all.textContent = "All groups"; picker.appendChild(all);
    groups.forEach(function (group) {
      var option = document.createElement("option"); option.value = group; option.textContent = group;
      picker.appendChild(option);
    });
    picker.value = state.focusGroup;
  }
  function renderOutline() {
    var list = $("outline-list"); list.replaceChildren();
    var displayed = state.items.filter(visibleWorking).map(function (item) { return { item: item, derived: false }; });
    if (state.derived) state.derived.nodes.filter(function (item) { return visibleDerived(item) && matches(item); })
      .forEach(function (item) { displayed.push({ item: item, derived: true }); });
    if (state.architecture) state.architecture.nodes.filter(candidateVisible).forEach(function (item) {
      displayed.push({ item: item, candidate: true });
    });
    if (state.realization) state.realization.elements.filter(realizationVisible).forEach(function (item) {
      displayed.push({item: {id:item.id,title:item.title,group:item.scope}, realization:true});
    });
    displayed.sort(function (a, b) {
      return ((a.item.group || "") + a.item.title).localeCompare((b.item.group || "") + b.item.title);
    });
    if (!displayed.length) {
      var empty = document.createElement("li"); empty.textContent = "No visible matches"; list.appendChild(empty); return;
    }
    displayed.forEach(function (row) {
      var li = document.createElement("li"), button = document.createElement("button");
      button.type = "button"; button.textContent = (row.item.group ? row.item.group + " / " : "") + row.item.title;
      button.addEventListener("click", function () {
        if (row.derived) chooseDerived(row.item.id);
        else if (row.candidate) chooseCandidate(row.item.id);
        else if (row.realization) chooseRealization(row.item.id);
        else choose(row.item.id);
        var pos = row.derived ? state.derivedPositions[row.item.id] :
          row.candidate ? state.candidatePositions[row.item.id] :
          row.realization ? state.realizationPositions[row.item.id] : state.positions[row.item.id];
        if (pos) {
          state.panX = Math.max(-1400, Math.min(700, $("viewport").clientWidth / 2 - (pos.x + 80) * state.zoom));
          state.panY = Math.max(-1040, Math.min(700, $("viewport").clientHeight / 2 - (pos.y + 32) * state.zoom));
          transform(); scheduleSave();
        }
      });
      li.appendChild(button); list.appendChild(li);
    });
  }
  function fit() {
    var points = state.items.filter(visibleWorking).map(function (item) { return state.positions[item.id]; });
    if (state.derived) state.derived.nodes.filter(function (item) { return visibleDerived(item) && matches(item); })
      .forEach(function (item) { if (state.derivedPositions[item.id]) points.push(state.derivedPositions[item.id]); });
    if (state.architecture) state.architecture.nodes.filter(candidateVisible).forEach(function (item) {
      if (state.candidatePositions[item.id]) points.push(state.candidatePositions[item.id]);
    });
    if (state.realization) state.realization.elements.filter(realizationVisible).forEach(function (item) {
      if (state.realizationPositions[item.id]) points.push(state.realizationPositions[item.id]);
    });
    if (!points.length) { state.zoom = 1; state.panX = 0; state.panY = 0; }
    else {
      var minX = Math.min.apply(null, points.map(function (p) { return p.x; }));
      var minY = Math.min.apply(null, points.map(function (p) { return p.y; }));
      var maxX = Math.max.apply(null, points.map(function (p) { return p.x + 165; }));
      var maxY = Math.max.apply(null, points.map(function (p) { return p.y + 75; }));
      var viewport = $("viewport");
      state.zoom = Math.max(.5, Math.min(1.5, (viewport.clientWidth - 48) / (maxX - minX),
        (viewport.clientHeight - 48) / (maxY - minY)));
      state.panX = Math.max(-5000, Math.min(5000, Math.round(viewport.clientWidth / 2 - (minX + maxX) / 2 * state.zoom)));
      state.panY = Math.max(-5000, Math.min(5000, Math.round(viewport.clientHeight / 2 - (minY + maxY) / 2 * state.zoom)));
    }
    $("zoom").value = String(Math.round(state.zoom * 100));
    transform(); scheduleSave();
  }
  function gridPosition(index) {
    return { x: 45 + (index % 8) * 175, y: 30 + (Math.floor(index / 8) % 14) * 75 };
  }
  function availablePosition() {
    var occupied = new Set(Object.values(state.positions).map(function (p) { return p.x + ":" + p.y; }));
    for (var n = 0; n < 112; n++) {
      var p = gridPosition(n);
      if (!occupied.has(p.x + ":" + p.y)) return p;
    }
    return gridPosition(state.items.length % 112);
  }
  function arrangeVisible() {
    if (remote.failed || !remote.ready) { status("Cannot arrange while the canvas is unavailable."); return; }
    if (!$("scene-panel").hidden) captureScene();
    var items = state.items.filter(visibleWorking).sort(function (a, b) {
      return ((a.group || "") + "/" + a.title).localeCompare((b.group || "") + "/" + b.title);
    });
    if (!items.length) { status("No working items in this view to arrange."); return; }
    var moving = new Set(items.map(function (item) { return item.id; }));
    var occupied = new Set(Object.keys(state.positions).filter(function (id) { return !moving.has(id); })
      .map(function (id) { var p = state.positions[id]; return p.x + ":" + p.y; }));
    var free = [];
    for (var n = 0; n < 112; n++) {
      var p = gridPosition(n);
      if (!occupied.has(p.x + ":" + p.y)) free.push(p);
    }
    if (items.length > free.length) { status("Not enough free layout cells; focus a smaller group."); return; }
    items.forEach(function (item, i) { state.positions[item.id] = free[i]; });
    render(); fit();
    status("Working items arranged by group. Arrangement changes layout only.");
  }
  function transform() { $("world").style.transform = "translate(" + state.panX + "px," + state.panY + "px) scale(" + state.zoom + ")"; }
  // A stable, author-editable working item; never a fabricated StoryIdentity premise.
  function visionItem() { return state.items.find(function (item) { return item.id === "story-vision"; }); }
  function showVision() {
    var item = visionItem();
    if (document.activeElement !== $("vision-text")) $("vision-text").value = item ? item.content : "";
    $("vision-status").textContent = item ? "Working vision saved with canvas" : "Start with any creative intent. A premise is optional.";
    var preview = item && item.content.trim() ? item.content.trim().replace(/\s+/g, " ") :
      "Optional: emotional promises, genres, tropes or a premise";
    $("vision-preview").textContent = "· " + preview;
    $("vision-preview").title = preview;
  }
  function updateVision() {
    if (!remote.ready || remote.failed) { status("Vision cannot be saved while the canvas is unavailable."); return; }
    var text = $("vision-text").value;
    var item = visionItem();
    if (!item && !text.trim()) return;
    if (!item) {
      if (state.items.length >= 200) { status("This canvas reached its working-item limit."); return; }
      item = { id: "story-vision", kind: "note", title: "Story Vision", group: "Story Vision", content: text };
      state.items.push(item);
      state.positions[item.id] = availablePosition();
      if (!state.selected) state.selected = item.id;
      render();
    } else {
      item.content = text;
      if (state.selected === item.id) $("content").value = text;
    }
    scheduleSave();
    $("vision-status").textContent = "Saving working vision locally...";
  }
  function newItem(kind) {
    if (!remote.ready || remote.failed) { status("Cannot edit while local canvas is unavailable. Export your notes if needed."); return; }
    if (state.items.length >= 200) { status("The working canvas has reached its 200-item safety bound."); return; }
    if (!$("scene-panel").hidden) { captureScene(); concealScene(); scheduleSave(); }
    var pos = availablePosition();
    var item = { id: id("item"), kind: kind, title: kind === "note" ? "New idea" : "New " + kind,
      content: "", group: state.focusGroup };
    state.items.push(item);
    state.positions[item.id] = pos;
    state.selected = item.id; state.selectedDerived = null;
    state.workspace = "realization"; state.lastRealizationView = "create";
    state.view = "create"; $("layer-view").value = "create";
    render();
    $("title").focus();
    rememberFocus();
    queueSave(); status(remote.failed ? "SAVE FAILED: export your working notes." : "Working item created. Saving locally...");
  }
  function changedRelationVisible(edge) {
    var chapter = $("relationship-chapter").value;
    if (!chapter || !edge.id.startsWith("relation:")) return true;
    var ids = state.derived && state.derived.relationship_changes && state.derived.relationship_changes[chapter];
    return Array.isArray(ids) && ids.includes(edge.id.slice("relation:".length));
  }
  function updateRelationChapters(graph) {
    var select = $("relationship-chapter"); select.replaceChildren();
    var all = document.createElement("option"); all.value = ""; all.textContent = "All declared relations"; select.appendChild(all);
    Object.keys(graph.relationship_changes || {}).sort().forEach(function (key) {
      var opt = document.createElement("option"); opt.value = key;
      opt.textContent = "Changed in " + key.replace("_", " "); select.appendChild(opt);
    });
    select.disabled = select.options.length <= 1;
  }
  function visibleDerived(node) {
    return state.view === "all" || (state.view === "relationships" && node.kind === "character") ||
      (state.view === "lenses" && node.kind === "lens") ||
      (state.view === "impact" && node.kind === "artifact") ||
      (state.view === "book" && node.kind === "chapter");
  }
  function loadEvidence() {
    var workspace = $("evidence-workspace").value.trim();
    var params = new URLSearchParams(window.location.search);
    if (workspace) params.set("workspace", workspace);
    else params.delete("workspace");
    window.history.replaceState({}, "", window.location.pathname + "?" + params.toString());
    status("Loading source-bound story evidence...");
    fetch("/api/beginner/studio/graph" + (workspace ? "?workspace=" + encodeURIComponent(workspace) : ""))
      .then(apiJson).then(function (graph) {
        state.derived = graph; state.derivedPositions = {}; state.selectedDerived = null;
        updateRelationChapters(graph);
        graph.nodes.forEach(function (node, i) {
          var baseX = node.kind === "lens" ? 520 : 380;
          var index = graph.nodes.slice(0, i).filter(function (n) { return n.kind === node.kind; }).length;
          state.derivedPositions[node.id] = { x: baseX + (index % 3) * 188, y: 90 + Math.floor(index / 3) * 115 };
        });
        if (!$("scene-panel").hidden) { captureScene(); concealScene(); queueSave(); }
        state.selected = null;
        state.view = graph.nodes.some(function (n) { return n.kind === "character"; }) ? "relationships" : "lenses";
        $("layer-view").value = state.view;
        render();
        status(graph.warnings.length ? graph.warnings.join(" ") :
          "Read-only story evidence loaded. Select a node to see meaning and source.");
      }).catch(function (error) {
        status("Story evidence unavailable: " + error.message + ". Working notes are unchanged.");
      });
  }
  function fillBookList(id, notices, emptyText) {
    var host = $(id); host.replaceChildren();
    if (!notices || !notices.length) {
      var empty = document.createElement("li"); empty.textContent = emptyText; host.appendChild(empty); return;
    }
    notices.forEach(function (notice) {
      var line = document.createElement("li");
      line.textContent = (notice.chapter_index ? "Chapter " + notice.chapter_index + " · " : "") + notice.summary;
      host.appendChild(line);
    });
  }
  function loadBook() {
    status("Reading accepted Book orientation...");
    fetch("/api/beginner/book/progress").then(apiJson).then(function (book) {
      if (!state.derived) state.derived = { nodes: [], edges: [], warnings: [] };
      state.derived.nodes = state.derived.nodes.filter(function (node) { return node.kind !== "chapter"; });
      state.derived.edges = state.derived.edges.filter(function (edge) { return !edge.id.startsWith("chapter-order:"); });
      Object.keys(state.derivedPositions).forEach(function (id) { if (id.startsWith("book:chapter:")) delete state.derivedPositions[id]; });
      var total = Math.max(book.current_chapter || 1, book.planned_chapters || 0, book.accepted_chapters || 0);
      var visible = Math.min(total, 24);
      for (var i = 1; i <= visible; i++) {
        var id = "book:chapter:" + i;
        var current = i === book.current_chapter;
        state.derived.nodes.push({ id: id, kind: "chapter", title: "Chapter " + i,
          detail: current ? book.orientation_reason : "Chapter-order orientation only; inspect accepted history before making changes.",
          authority: "DERIVED / NOT CANON", source_ref: "book progress, Chapter " + i,
          status: current ? book.current_chapter_state + " · current" : "position only",
          impact_role: current ? "source" : "affected" });
        state.derivedPositions[id] = { x: 115 + ((i - 1) % 4) * 195, y: 90 + Math.floor((i - 1) / 4) * 120 };
        if (i > 1) state.derived.edges.push({ id: "chapter-order:" + (i - 1) + ":" + i,
          source: "book:chapter:" + (i - 1), target: id, label: "chapter order",
          authority: "DERIVED / NOT CANON", source_ref: "book progress" });
      }
      $("book-heading").textContent = "Chapter " + book.current_chapter + " · " + book.current_chapter_state;
      $("book-next-action").textContent = "Next: " + (book.next_story_action || "Continue writing");
      fillBookList("book-recent", book.recent_changes, "Nothing established yet.");
      fillBookList("book-pending", book.pending_updates, "No pending updates.");
      fillBookList("book-attention", book.needs_attention, "Nothing needs attention.");
      $("book-orientation").hidden = false;
      if (!$("scene-panel").hidden) { captureScene(); concealScene(); queueSave(); }
      state.view = "book"; state.selected = null; state.selectedDerived = null;
      $("layer-view").value = "book";
      render();
      status(total > visible ? "Book view shows the first " + visible + " chapters; later chapters are not displayed yet." :
        "Book orientation loaded from current project state. It is read-only.");
    }).catch(function (error) { status("Book orientation unavailable: " + error.message); });
  }
  function previewImpact() {
    var artifact = $("impact-artifact").value.trim();
    if (!artifact) { status("Choose an existing provenance artifact id."); return; }
    status("Reading registered downstream dependency paths...");
    fetch("/api/beginner/studio/impact?artifact=" + encodeURIComponent(artifact))
      .then(apiJson).then(function (preview) {
        if (!state.derived) state.derived = { nodes: [], edges: [], warnings: [] };
        // An impact preview is a *separate read-only graph view*, not working notes.
        state.derived.nodes = state.derived.nodes.filter(function (n) { return n.kind !== "artifact"; });
        state.derived.edges = state.derived.edges.filter(function (e) { return !e.id.startsWith("impact:"); });
        Object.keys(state.derivedPositions).forEach(function (id) { if (id.startsWith("artifact:")) delete state.derivedPositions[id]; });
        var all = [{ artifact_id: preview.source.artifact_id, artifact_type: preview.source.artifact_type,
          accepted: preview.source.accepted, authority: preview.source.authority,
          source_ref: preview.source.file_path, explanation: preview.warning }].concat(preview.affected);
        all.forEach(function (entry, i) {
          var nodeId = "artifact:" + entry.artifact_id;
          state.derived.nodes.push({
            id: nodeId, kind: "artifact", title: entry.artifact_id,
            detail: entry.explanation || "Registered provenance source; possible downstream dependencies.",
            status: entry.accepted ? "accepted source" : "registered source",
            authority: entry.authority || "PROVENANCE",
            source_ref: entry.source_ref || entry.artifact_id,
            impact_role: i === 0 ? "source" : "affected"
          });
          state.derivedPositions[nodeId] = { x: 260 + (i % 3) * 196, y: 80 + Math.floor(i / 3) * 120 };
        });
        var seen = new Set();
        preview.affected.forEach(function (entry) {
          entry.hops.forEach(function (hop) {
            var edgeId = "impact:" + hop.source + ":" + hop.target;
            if (seen.has(edgeId)) return; seen.add(edgeId);
            state.derived.edges.push({ id: edgeId, source: "artifact:" + hop.source,
              target: "artifact:" + hop.target, label: hop.kind,
              source_ref: "provenance", authority: "HYPOTHETICAL / READ ONLY" });
          });
        });
        if (!$("scene-panel").hidden) { captureScene(); concealScene(); queueSave(); }
        state.view = "impact"; $("layer-view").value = "impact"; state.selected = null; state.selectedDerived = null;
        render();
        status("Hypothetical dependency paths only. Nothing has been revised or accepted.");
      }).catch(function (error) { status("Impact preview unavailable: " + error.message); });
  }
  function chooseDerived(nodeId) {
    if (!$("scene-panel").hidden) { captureScene(); concealScene(); scheduleSave(); }
    state.selected = null; state.selectedDerived = nodeId; state.selectedCandidate = null;
    Array.prototype.forEach.call(document.querySelectorAll(".node"), function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.itemId === nodeId));
    });
    renderInspector();
    rememberFocus();
  }
  function drawEdges() {
    var svg = $("edges");
    svg.replaceChildren();
    state.connections.forEach(function (edge) {
      if (!["create", "all", "relationships"].includes(state.view)) return;
      var from = state.positions[edge.source], to = state.positions[edge.target];
      if (!from || !to || !visibleWorking(state.items.find(function (i) { return i.id === edge.source; }) || {}) ||
          !visibleWorking(state.items.find(function (i) { return i.id === edge.target; }) || {})) return;
      var line = document.createElementNS(svgNS, "line");
      line.setAttribute("x1", String(from.x + 82)); line.setAttribute("y1", String(from.y + 33));
      line.setAttribute("x2", String(to.x + 82)); line.setAttribute("y2", String(to.y + 33));
      line.setAttribute("stroke", "#879b91"); line.setAttribute("stroke-width", "2");
      if (!edge.label) line.setAttribute("stroke-dasharray", "5 4");
      svg.appendChild(line);
      if (edge.label) {
        var text = document.createElementNS(svgNS, "text");
        text.setAttribute("x", String((from.x + to.x) / 2 + 82));
        text.setAttribute("y", String((from.y + to.y) / 2 + 23));
        text.setAttribute("text-anchor", "middle"); text.setAttribute("fill", "#45594f");
        text.setAttribute("font-size", "12"); text.textContent = edge.label;
        svg.appendChild(text);
      }
    });
    if (state.architecture && state.view === "architecture") {
      state.architecture.links.forEach(function (edge) {
        var fromNode = candidateNode(edge.source), toNode = candidateNode(edge.target);
        if (!fromNode || !toNode || !candidateVisible(fromNode) || !candidateVisible(toNode)) return;
        var from = state.candidatePositions[edge.source], to = state.candidatePositions[edge.target];
        if (!from || !to) return;
        var line = document.createElementNS(svgNS, "line");
        line.setAttribute("x1", String(from.x + 82)); line.setAttribute("y1", String(from.y + 34));
        line.setAttribute("x2", String(to.x + 82)); line.setAttribute("y2", String(to.y + 34));
        line.setAttribute("stroke", "#846ca1"); line.setAttribute("stroke-width", "2");
        line.setAttribute("stroke-dasharray", "6 4");
        var highlighted = edge.source === state.selectedCandidate || edge.target === state.selectedCandidate;
        line.setAttribute("opacity", state.selectedCandidate && !highlighted ? ".22" : ".8");
        var title = document.createElementNS(svgNS, "title");
        title.textContent = (edge.function || "Related") + ": " + fromNode.title + " → " + toNode.title;
        line.appendChild(title); svg.appendChild(line);
        if (highlighted && edge.function) {
          var verb = document.createElementNS(svgNS, "text");
          verb.setAttribute("x", String((from.x + to.x) / 2 + 82));
          verb.setAttribute("y", String((from.y + to.y) / 2 + 20));
          verb.setAttribute("text-anchor", "middle"); verb.setAttribute("fill", "#584773");
          verb.setAttribute("font-size", "12"); verb.textContent = edge.function.slice(0, 46);
          svg.appendChild(verb);
        }
      });
    }
    if (state.architecture && state.view === "architecture") {
      (state.architecture.genre_interactions || []).forEach(function (edge) {
        var a = candidateNode(edge.source_genre_id), b = candidateNode(edge.target_genre_id);
        if (!a || !b || !candidateVisible(a) || !candidateVisible(b)) return;
        var from = state.candidatePositions[a.id], to = state.candidatePositions[b.id];
        if (!from || !to) return;
        var line = document.createElementNS(svgNS, "line");
        line.setAttribute("x1", String(from.x + 82)); line.setAttribute("y1", String(from.y + 34));
        line.setAttribute("x2", String(to.x + 82)); line.setAttribute("y2", String(to.y + 34));
        line.setAttribute("stroke", "#855a8b"); line.setAttribute("stroke-width", "3");
        line.setAttribute("stroke-dasharray", "3 6");
        var highlighted = edge.source_genre_id === state.selectedCandidate ||
          edge.target_genre_id === state.selectedCandidate;
        line.setAttribute("opacity", state.selectedCandidate && !highlighted ? ".2" : ".9");
        var label = document.createElementNS(svgNS, "title");
        label.textContent = edge.kind.replace(/_/g, " ") + ": " + edge.mechanism; line.appendChild(label);
        svg.appendChild(line);
        if (highlighted) {
          var text = document.createElementNS(svgNS, "text");
          text.setAttribute("x", String((from.x + to.x) / 2 + 82));
          text.setAttribute("y", String((from.y + to.y) / 2 + 26));
          text.setAttribute("text-anchor", "middle"); text.setAttribute("fill", "#75487b");
          text.setAttribute("font-size", "12"); text.textContent = edge.kind.replace(/_/g, " ");
          svg.appendChild(text);
        }
      });
    }
    if (state.realization && state.view === "realization_candidates") {
      state.realization.links.forEach(function (edge) {
        var a = realizationElement(edge.source), b = realizationElement(edge.target);
        if (!a || !b || !realizationVisible(a) || !realizationVisible(b)) return;
        var from = state.realizationPositions[a.id], to = state.realizationPositions[b.id];
        var line = document.createElementNS(svgNS, "line");
        line.setAttribute("x1", String(from.x+82)); line.setAttribute("y1", String(from.y+34));
        line.setAttribute("x2", String(to.x+82)); line.setAttribute("y2", String(to.y+34));
        line.setAttribute("stroke", "#4f897e"); line.setAttribute("stroke-width", "2");
        svg.appendChild(line);
      });
    }
    if (state.derived) state.derived.edges.forEach(function (edge) {
      var from = state.derivedPositions[edge.source], to = state.derivedPositions[edge.target];
      var fromNode = state.derived.nodes.find(function (n) { return n.id === edge.source; });
      var toNode = state.derived.nodes.find(function (n) { return n.id === edge.target; });
      if (!from || !to || !fromNode || !toNode || !visibleDerived(fromNode) || !visibleDerived(toNode) || !matches(fromNode) || !matches(toNode) || !changedRelationVisible(edge)) return;
      var line = document.createElementNS(svgNS, "line");
      line.setAttribute("x1", String(from.x + 82)); line.setAttribute("y1", String(from.y + 33));
      line.setAttribute("x2", String(to.x + 82)); line.setAttribute("y2", String(to.y + 33));
      line.setAttribute("stroke", "#8d9ab9"); line.setAttribute("stroke-width", "2");
      svg.appendChild(line);
    });
  }
  function renderInspector() {
    var source = state.workspace === "realization" && state.derived &&
      state.derived.nodes.find(function (n) { return n.id === state.selectedDerived; });
    if (source && (!visibleDerived(source) || !matches(source))) source = null;
    var proposal = state.workspace === "architecture" && state.view === "architecture"
      ? candidateNode(state.selectedCandidate) : null;
    if (proposal && !candidateVisible(proposal)) proposal = null;
    var concrete = state.workspace === "realization" && state.view === "realization_candidates"
      ? realizationElement(state.selectedRealization) : null;
    if (concrete && !realizationVisible(concrete)) concrete = null;
    var facetEntry = state.workspace === "architecture" ? currentFacetEntry() : null;
    var phase = state.workspace === "architecture" && state.view === "genre_timeline" && state.architecture
      ? state.architecture.phases.find(function (p) { return p.id === state.selectedPhase; }) : null;
    $("source-detail").hidden = !source && !proposal && !concrete && !facetEntry && !phase;
    $("realization-copy").hidden = !concrete;
    $("realization-inspect").hidden = !concrete;
    $("realization-feedback").hidden = !concrete || state.realizationStale || !(state.realization.architecture_feedback || []).some(function (e) {
      return concrete.architecture_refs.includes(e.architecture_node_id);
    });
    $("candidate-copy").hidden = !proposal;
    $("candidate-focus").hidden = !proposal;
    $("genre-contract-detail").replaceChildren();
    $("genre-contract-detail").hidden = true;
    $("book-orientation").hidden = state.workspace !== "realization" || state.view !== "book";
    if (phase) { renderPhaseInspector(phase); return; }
    if (facetEntry) { renderFacetInspector(facetEntry); return; }
    if (concrete) {
      $("inspector-empty").hidden = true; $("inspector-fields").hidden = true;
      $("genre-contract-detail").hidden = true;
      $("source-title").textContent = concrete.title;
      $("source-state").textContent = concrete.kind + " · STORY REALIZATION PROPOSAL / NOT ACCEPTED";
      $("source-description").textContent = concrete.description;
      $("source-ref").textContent = "Architecture references: " + concrete.architecture_refs.map(function (id) {
        var node = candidateNode(id); return node ? node.title : id;
      }).join(" · ") + " | Response " + (state.realizationRequestSha || "unavailable");
      var links = $("source-links"); links.replaceChildren();
      state.realization.links.filter(function (edge) {
        return edge.source === concrete.id || edge.target === concrete.id;
      }).forEach(function (edge) {
        var other = realizationElement(edge.source === concrete.id ? edge.target : edge.source);
        if (!other) return;
        var p = document.createElement("p"); p.textContent = edge.function + " → " + other.title; links.appendChild(p);
      });
      (state.realization.architecture_feedback || []).filter(function (feedback) {
        return concrete.architecture_refs.includes(feedback.architecture_node_id);
      }).forEach(function (feedback) {
        var p = document.createElement("p");
        p.textContent = "Potential architecture refinement: " + feedback.observation +
          " → " + feedback.proposed_change; links.appendChild(p);
      });
      return;
    }
    if (proposal) {
      $("inspector-empty").hidden = true; $("inspector-fields").hidden = true;
      $("source-title").textContent = proposal.title;
      $("source-state").textContent = proposal.category + " · AGENT CANDIDATE / NOT ACCEPTED";
      $("source-description").textContent = proposal.summary;
      $("source-ref").textContent = "Working scope: " + proposal.scope +
        " · Agent response " + (state.architectureRequestSha || "unavailable");
      var related = $("source-links"); related.replaceChildren();
      state.architecture.links.filter(function (edge) {
        return edge.source === proposal.id || edge.target === proposal.id;
      }).forEach(function (edge) {
        var other = candidateNode(edge.source === proposal.id ? edge.target : edge.source);
        if (!other) return;
        var button = document.createElement("button"); button.type = "button"; button.className = "facet-link";
        button.textContent = (edge.function || "Related") + " → " + other.title;
        button.addEventListener("click", function () { visitFacet("overview", null, other.id); });
        related.appendChild(button);
      });
      var contract = (state.architecture.genre_contracts || []).find(function (genre) {
        return genre.genre_node_id === proposal.id;
      });
      if (contract) {
        var detail = $("genre-contract-detail"); detail.hidden = false;
        function section(title, content) {
          if (!content) return;
          var h = document.createElement("h4"); h.textContent = title; detail.appendChild(h);
          var p = document.createElement("p"); p.textContent = content; detail.appendChild(p);
        }
        function jump(label, facet, key, nodeId) {
          var button = document.createElement("button"); button.type = "button";
          button.className = "facet-link"; button.textContent = label;
          button.addEventListener("click", function () { visitFacet(facet, key, nodeId); });
          detail.appendChild(button);
        }
        section("Role", contract.role);
        contract.emotion_target_ids.forEach(function (id) {
          var target = (state.architecture.emotion_targets || []).find(function (e) { return e.id === id; });
          if (target) {
            section("Basic emotion · " + target.emotion,
              target.intended_effect + " (" + target.role + ", " + target.provenance + "). " +
              "Narrative condition: " + target.eliciting_condition +
              ". Aesthetic strategy: " + target.aesthetic_strategy);
            jump("Explore emotion: " + target.emotion, "emotions", "emotion:" + id, null);
          }
        });
        contract.complex_emotion_ids.forEach(function (id) {
          var emotion = (state.architecture.complex_emotions || []).find(function (e) { return e.id === id; });
          if (emotion) {
            section("Complex emotion · " + emotion.title,
              emotion.basic_emotions.join(" + ") + ": " + emotion.context);
            jump("Explore composition: " + emotion.title, "emotions", "complex:" + id, null);
          }
        });
        section("Trope functions", contract.trope_functions.join(" · "));
        contract.trope_functions.forEach(function (trope, index) {
          jump("Explore trope function: " + trope, "tropes",
            "trope:" + proposal.id + ":" + index, null);
        });
        section("Narrative engine", contract.narrative_engine);
        if (contract.narrative_engine) jump("Explore narrative engine", "structure",
          "structure:" + proposal.id + ":0", null);
        section("Structural pattern", contract.structural_pattern);
        if (contract.structural_pattern) jump("Explore structural pattern", "structure",
          "structure:" + proposal.id + ":1", null);
        section("Aesthetic strategies", contract.aesthetic_strategies.join(" · "));
        section("Payoff expectations", contract.payoff_expectations.join(" · "));
        (state.architecture.genre_interactions || []).filter(function (link) {
          return link.source_genre_id === proposal.id || link.target_genre_id === proposal.id;
        }).forEach(function (link) {
          var other = candidateNode(link.source_genre_id === proposal.id ? link.target_genre_id : link.source_genre_id);
          section("Genre interaction · " + link.kind.replace(/_/g, " "),
            (other ? other.title : "Other genre") + ": " + link.mechanism +
            (link.risk ? " Risk: " + link.risk : ""));
          if (other) {
            var button = document.createElement("button"); button.type = "button";
            button.className = "facet-link"; button.textContent = "Inspect interacting genre: " + other.title;
            button.addEventListener("click", function () { visitFacet("genres", null, other.id); });
            related.appendChild(button);
          }
        });
      }
      return;
    }
    if (source) {
      $("inspector-empty").hidden = true; $("inspector-fields").hidden = true;
      $("source-title").textContent = source.title;
      $("source-state").textContent = source.status + " · " + source.authority;
      $("source-description").textContent = source.detail || "No further detail established";
      $("source-ref").textContent = "Source: " + source.source_ref;
      var links = $("source-links"); links.replaceChildren();
      state.derived.edges.filter(function (e) { return (e.source === source.id || e.target === source.id) && changedRelationVisible(e); }).forEach(function (edge) {
        var otherId = edge.source === source.id ? edge.target : edge.source;
        var other = state.derived.nodes.find(function (n) { return n.id === otherId; });
        if (!other) return;
        var text = document.createElement("p"); text.textContent = (edge.label || "Related") + " → " + other.title;
        links.appendChild(text);
      });
      return;
    }
    var item = state.workspace === "realization" ? selected() : null;
    if (item && !visibleWorking(item)) item = null;
    $("inspector-empty").hidden = !!item;
    $("inspector-fields").hidden = !item;
    $("inspector-empty").textContent = state.workspace === "architecture"
      ? (state.view === "genre_timeline" ? "Explore a phase in the timeline." :
        "Choose a visible architecture component to inspect its meaning and relationships.")
      : "Choose a visible working or source item to inspect it.";
    if (!item) return;
    $("title").value = item.title; $("group").value = item.group || ""; $("kind").value = item.kind; $("content").value = item.content;
    $("write").hidden = item.kind !== "scene";
    var target = $("target"); target.replaceChildren();
    state.items.filter(function (entry) { return entry.id !== item.id; }).forEach(function (entry) {
      var opt = document.createElement("option"); opt.value = entry.id; opt.textContent = entry.title; target.appendChild(opt);
    });
    $("connect").disabled = !target.options.length;
    var list = $("connections"); list.replaceChildren();
    state.connections.filter(function (edge) { return edge.source === item.id || edge.target === item.id; }).forEach(function (edge) {
      var otherId = edge.source === item.id ? edge.target : edge.source;
      var other = state.items.find(function (entry) { return entry.id === otherId; });
      var row = document.createElement("div"); row.className = "connection";
      var summary = document.createElement("span"); summary.textContent = (edge.label || "Associated with") + " · " + (other ? other.title : "Unknown");
      var remove = document.createElement("button"); remove.type = "button"; remove.textContent = "Unlink";
      remove.setAttribute("aria-label", "Remove connection with " + (other ? other.title : "unknown"));
      remove.addEventListener("click", function () { state.connections = state.connections.filter(function (e) { return e.id !== edge.id; }); render(); queueSave(); });
      row.append(summary, remove); list.appendChild(row);
    });
  }
  function choose(itemId) {
    var writing = !$("scene-panel").hidden;
    if (writing) { captureScene(); scheduleSave(); }
    state.selected = itemId; state.selectedDerived = null; state.selectedCandidate = null;
    Array.prototype.forEach.call(document.querySelectorAll(".node"), function (node) {
      node.setAttribute("aria-pressed", String(node.dataset.itemId === itemId));
    });
    renderInspector();
    if (writing) {
      if (selected() && selected().kind === "scene") displayScene();
      else concealScene();
    }
    rememberFocus();
  }

  function copyRealization() {
    var source = realizationElement(state.selectedRealization);
    if (!source || !remote.ready || remote.failed) return;
    if (state.items.length >= 200) { status("Working canvas item limit reached."); return; }
    var kind = source.kind === "location" ? "place" :
      ["character", "scene"].includes(source.kind) ? source.kind : "note";
    var item = {id:id("item"), kind:kind, title:source.title,
      group:"Story Realization", content:source.description +
      "\n\nArchitecture refs: " + source.architecture_refs.join(", ") +
      "\nOrigin: working realization " + (state.realizationRequestSha || "unknown") +
      "/" + source.id + ". Not accepted story."};
    state.items.push(item); state.positions[item.id] = availablePosition();
    state.selected = item.id; state.selectedRealization = null;
    state.view = "create"; state.lastRealizationView = "create";
    $("layer-view").value = state.view;
    render(); queueSave(); rememberFocus();
    status("Copied to editable working ideas without accepting any story facts.");
  }
  function inspectRealizationPurpose() {
    var element = realizationElement(state.selectedRealization);
    if (!element) return;
    var node = element.architecture_refs.map(candidateNode).find(Boolean);
    if (!node) { status("Referenced architecture is unavailable or stale."); return; }
    switchWorkspace("architecture"); state.selectedCandidate = node.id;
    state.architectureCenter = null; state.architectureFocus = "";
    $("architecture-scope").value = ""; render(); rememberFocus();
    status("Inspecting the abstract narrative purpose of this concrete proposal.");
  }
  function proposeArchitectureFromRealization() {
    var element = realizationElement(state.selectedRealization);
    if (!element || !state.realization) return;
    if (state.realizationStale) {
      status("Concrete proposal is stale. Regenerate it against the current architecture first."); return;
    }
    var feedback = (state.realization.architecture_feedback || []).find(function (f) {
      return element.architecture_refs.includes(f.architecture_node_id);
    });
    if (!feedback) { status("No specific architecture refinement proposed for this element."); return; }
    switchWorkspace("architecture"); state.selectedCandidate = feedback.architecture_node_id;
    var instruction = "Review this NONCANONICAL finding from Story Realization as a potential " +
      "abstract architecture change. Do not instantiate story details: " +
      feedback.observation + " | Suggested change: " + feedback.proposed_change;
    $("architecture-instruction").value = instruction.slice(0,4000);
    requestArchitecture($("architecture-instruction").value);
  }
  function chooseRealization(id) {
    if (!$("scene-panel").hidden) { captureScene(); concealScene(); scheduleSave(); }
    state.selectedRealization = id; state.selected = null; state.selectedDerived = null;
    renderInspector(); rememberFocus();
  }
  function switchWorkspace(next) {
    if (next === state.workspace) return;
    if (next === "architecture") {
      if (!$("scene-panel").hidden) { captureScene(); concealScene(); scheduleSave(); }
      if (state.workspace === "realization") {
        state.lastRealizationView = state.view;
        if (state.selected) state.lastWorkingSelection = state.selected;
      }
      state.view = state.architectureFacet === "timeline" ? "genre_timeline" : "architecture";
    } else {
      state.view = state.lastRealizationView || "create";
      if (!state.selected && state.items.some(function (item) {
        return item.id === state.lastWorkingSelection;
      })) state.selected = state.lastWorkingSelection;
    }
    state.workspace = next;
    $("layer-view").value = state.view;
    render(); rememberFocus();
  }

  // Read-only, source-scoped projections. No new trope/structure identity is created.
  function explanationActive() {
    return state.workspace === "architecture" && ["genres", "tropes", "structure"].includes(state.architectureFacet);
  }
  function architectureFacetEntries(facet) {
    var a = state.architecture;
    if (!a) return [];
    var entries = [], contracts = a.genre_contracts || [];
    function genreName(id) {
      var n = candidateNode(id); return n ? n.title : id;
    }
    function add(entry) { entries.push(entry); }
    if (facet === "overview") {
      add({key:"summary", title:"Working architecture", kind:"Overview",
        detail:a.summary || "No overarching summary provided.", origin:"Architecture proposal summary"});
    }
    if (facet === "emotions") {
      (a.emotion_targets || []).forEach(function (t) {
        add({key:"emotion:" + t.id, title:t.emotion, kind:"Basic emotion · " + t.role,
          detail:t.intended_effect + " · Eliciting condition: " + t.eliciting_condition +
            " · Aesthetic strategy: " + t.aesthetic_strategy,
          origin:"emotion_targets/" + t.id + " (" + t.provenance + ")", targetId:t.id});
      });
      (a.complex_emotions || []).forEach(function (e) {
        add({key:"complex:" + e.id, title:e.title, kind:"Complex emotional composition",
          detail:e.basic_emotions.join(" + ") + " · " + e.context +
            " · Narrative approximation, not an emotion equation.",
          origin:"complex_emotions/" + e.id});
      });
    }
    if (facet === "genres") {
      contracts.forEach(function (c) {
        add({key:"genre:" + c.genre_node_id, title:genreName(c.genre_node_id),
          kind:"Genre contract · " + c.role,
          detail:"Narrative engine: " + c.narrative_engine + " · Structural pattern: " + c.structural_pattern,
          origin:"genre_contracts/" + c.genre_node_id, nodeId:c.genre_node_id});
      });
      (a.nodes || []).filter(function (n) { return n.category === "genre" &&
        !contracts.some(function (c) { return c.genre_node_id === n.id; }); }).forEach(function (n) {
        add({key:"genre-node:" + n.id, title:n.title, kind:"Proposed genre node",
          detail:n.summary, origin:"nodes/" + n.id, nodeId:n.id});
      });
    }
    if (facet === "tropes") {
      (a.nodes || []).filter(function (n) { return n.category === "trope"; }).forEach(function (n) {
        add({key:"trope-node:" + n.id, title:n.title, kind:"Proposed trope node",
          detail:n.summary, origin:"nodes/" + n.id, nodeId:n.id});
      });
      contracts.forEach(function (c) {
        (c.trope_functions || []).forEach(function (t, i) {
          add({key:"trope:" + c.genre_node_id + ":" + i, title:t,
            kind:"Trope function · " + genreName(c.genre_node_id),
            detail:t, origin:"genre_contracts/" + c.genre_node_id + "/trope_functions/" + i,
            ownerGenreId:c.genre_node_id});
        });
      });
      (a.phases || []).forEach(function (p) {
        (p.genre_activations || []).forEach(function (active) {
          (active.trope_functions || []).forEach(function (t, i) {
            add({key:"phase-trope:" + p.id + ":" + active.genre_node_id + ":" + i,
              title:t, kind:"Phase trope · " + p.title, detail:t,
              origin:"phases/" + p.id + "/genre_activations/" + active.genre_node_id + "/trope_functions/" + i,
              ownerGenreId:active.genre_node_id, phaseId:p.id});
          });
        });
      });
    }
    if (facet === "structure") {
      (a.nodes || []).filter(function (n) { return ["structure", "engine"].includes(n.category); })
        .forEach(function (n) {
          add({key:"structure-node:" + n.id, title:n.title, kind:"Proposed structural node",
            detail:n.summary, origin:"nodes/" + n.id, nodeId:n.id});
        });
      contracts.forEach(function (c) {
        [["Narrative engine", c.narrative_engine], ["Structural pattern", c.structural_pattern]]
          .forEach(function (part, i) {
            if (!part[1]) return;
            add({key:"structure:" + c.genre_node_id + ":" + i,
              title:part[1], kind:part[0] + " · " + genreName(c.genre_node_id),
              detail:part[1], origin:"genre_contracts/" + c.genre_node_id + "/" +
                (i === 0 ? "narrative_engine" : "structural_pattern"), ownerGenreId:c.genre_node_id});
          });
      });
      (a.phases || []).forEach(function (p) {
        (p.genre_activations || []).forEach(function (active) {
          if (!active.structural_function) return;
          add({key:"phase-structure:" + p.id + ":" + active.genre_node_id,
            title:active.structural_function, kind:"Phase structure · " + p.title,
            detail:active.structural_function,
            origin:"phases/" + p.id + "/genre_activations/" + active.genre_node_id + "/structural_function",
            ownerGenreId:active.genre_node_id, phaseId:p.id});
        });
      });
    }
    if (facet === "timeline") {
      (a.phases || []).slice().sort(function (x, y) { return x.order - y.order; })
        .forEach(function (p) {
          add({key:"phase:" + p.id, title:p.title, kind:"Working phase",
            detail:p.narrative_function, origin:"phases/" + p.id, phaseId:p.id});
        });
    }
    return entries;
  }
  function currentFacetEntry() {
    return architectureFacetEntries(state.architectureFacet).find(function (e) {
      return e.key === state.facetSelection;
    }) || null;
  }
  function renderFacetList() {
    var panel = $("architecture-facet-panel");
    panel.hidden = state.workspace !== "architecture";
    Array.prototype.forEach.call(document.querySelectorAll("[data-architecture-facet]"), function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.architectureFacet === state.architectureFacet));
    });
    $("architecture-facet-back").hidden = explanationActive() || !state.facetHistory.length;
    var list = $("architecture-facet-list"); list.replaceChildren();
    var entries = architectureFacetEntries(state.architectureFacet);
    $("architecture-facet-hint").textContent = state.architectureFacet === "overview"
      ? "The graph is the primary map. Select nodes for their proposed meaning and links."
      : state.architectureFacet === "timeline" ? "Select an interval for its local role."
      : "Source-scoped entries; selecting a field never accepts story canon.";
    if (!entries.length) {
      var empty = document.createElement("p"); empty.className = "muted";
      empty.textContent = "No " + state.architectureFacet + " proposed yet."; list.appendChild(empty); return;
    }
    entries.forEach(function (entry) {
      var b = document.createElement("button"); b.type = "button"; b.className = "facet-entry";
      b.setAttribute("aria-pressed", String(entry.key === state.facetSelection ||
        (!!entry.nodeId && entry.nodeId === state.selectedCandidate)));
      var name = document.createElement("strong"); name.textContent = entry.title;
      var kind = document.createElement("small"); kind.textContent = entry.kind;
      b.append(name, kind);
      b.addEventListener("click", function () {
        if (explanationActive()) {
          state.facetSelection = entry.key; state.selectedCandidate = null;
          state.explanationArrival = null; state.explanationInspectRequested = false;
          render(); rememberFocus(); return;
        }
        if (state.architectureFacet === "timeline" && entry.phaseId) state.selectedPhase = entry.phaseId;
        if (entry.nodeId) {
          state.facetSelection = null;
          state.architectureCenter = null; state.architectureFocus = ""; $("architecture-scope").value = "";
          chooseCandidate(entry.nodeId); render();
        } else {
          state.facetSelection = entry.key; state.selectedCandidate = null;
          renderFacetList(); renderTimeline(); renderInspector(); rememberFocus();
        }
      });
      list.appendChild(b);
    });
  }
  function visitFacet(facet, key, nodeId, semanticLink) {
    state.facetHistory.push({facet:state.architectureFacet, key:state.facetSelection,
      nodeId:state.selectedCandidate, search:$("find-nodes").value,
      scope:state.architectureFocus, center:state.architectureCenter, phase:state.selectedPhase,
      arrival:state.explanationArrival, inspected:state.explanationInspectRequested,
      returnLinkId:semanticLink ? semanticLink.id : null});
    state.explanationArrival = null; state.explanationInspectRequested = false;
    if (semanticLink) {
      var projector = window.AuteurStudioExplanations;
      var sourceProjection = projector.project(state.architecture,state.architectureRequestSha,null);
      var source = projector.resolve(sourceProjection,semanticLink.fromFacet,semanticLink.fromKey,state.architectureRequestSha);
      var destination = projector.resolve(sourceProjection,semanticLink.targetFacet,semanticLink.targetKey,state.architectureRequestSha);
      if (source && destination) state.explanationArrival = {from:source.title,to:destination.title,
        verb:semanticLink.relationVerb,sourceRef:semanticLink.sourceRef,status:semanticLink.supportStatus};
    }
    if (state.facetHistory.length > 12) state.facetHistory.shift();
    state.architectureFacet = facet; state.facetSelection = key || null;
    if (facet === "timeline" && key && key.startsWith("phase:")) state.selectedPhase = key.slice(6);
    state.selectedCandidate = nodeId || null; state.architectureCenter = null;
    state.architectureFocus = ""; $("architecture-scope").value = "";
    if (nodeId && candidateNode(nodeId) && !matches(candidateNode(nodeId))) $("find-nodes").value = "";
    state.view = facet === "timeline" ? "genre_timeline" : "architecture";
    $("layer-view").value = state.view; render(); rememberFocus();
  }
  function renderFacetInspector(entry) {
    $("source-detail").hidden = false; $("inspector-empty").hidden = true; $("inspector-fields").hidden = true;
    $("source-title").textContent = entry.title;
    $("source-state").textContent = entry.kind + " · SOURCE-LINKED PROPOSAL / NOT ACCEPTED";
    $("source-description").textContent = entry.detail;
    $("source-ref").textContent = entry.origin + " · Response " +
      (state.architectureRequestSha || "unavailable") + " · locally scoped";
    var links = $("source-links"); links.replaceChildren();
    function action(label, onClick) {
      var b = document.createElement("button"); b.type = "button"; b.className = "facet-link";
      b.textContent = label; b.addEventListener("click", onClick); links.appendChild(b);
    }
    if (entry.ownerGenreId) {
      var genre = candidateNode(entry.ownerGenreId);
      action("Inspect owning genre: " + (genre ? genre.title : entry.ownerGenreId), function () {
        visitFacet("genres", null, entry.ownerGenreId);
      });
      var contract = (state.architecture.genre_contracts || []).find(function (c) {
        return c.genre_node_id === entry.ownerGenreId;
      });
      if (contract && contract.emotion_target_ids.length) {
        var note = document.createElement("p");
        note.textContent = "Genre-level emotional targets (not a claim that this individual trope or phrase evokes them):";
        links.appendChild(note);
        contract.emotion_target_ids.forEach(function (id) {
          var emotion = (state.architecture.emotion_targets || []).find(function (t) { return t.id === id; });
          if (emotion) action("Genre target: " + emotion.emotion, function () {
            visitFacet("emotions", "emotion:" + id, null);
          });
        });
      }
    }
    if (entry.targetId) {
      (state.architecture.genre_contracts || []).filter(function (c) {
        return (c.emotion_target_ids || []).includes(entry.targetId);
      }).forEach(function (c) {
        var node = candidateNode(c.genre_node_id);
        action("Targeted by genre: " + (node ? node.title : c.genre_node_id), function () {
          visitFacet("genres", null, c.genre_node_id);
        });
      });
    }
    if (entry.phaseId) {
      action("View temporal context", function () { visitFacet("timeline", "phase:" + entry.phaseId, null); });
    }
  }
  function renderEmotionalOverview() {
    var host = $("emotional-targets"); host.replaceChildren();
    if (!state.architecture) return;
    (state.architecture.emotion_targets || []).forEach(function (target) {
      var p = document.createElement("p");
      p.textContent = target.emotion.toUpperCase() + " (" + target.role + ", " + target.provenance +
        "): " + target.intended_effect + " | Elicited by: " + target.eliciting_condition +
        " | Aesthetic strategy: " + target.aesthetic_strategy;
      host.appendChild(p);
    });
    (state.architecture.complex_emotions || []).forEach(function (emotion) {
      var p = document.createElement("p");
      p.textContent = emotion.title + " (" + emotion.basic_emotions.join(" + ") + "): " +
        emotion.context + " · Narrative approximation, not an emotion equation.";
      host.appendChild(p);
    });
  }
  function renderPhaseInspector(phase) {
    $("source-detail").hidden = false; $("inspector-empty").hidden = true; $("inspector-fields").hidden = true;
    $("source-title").textContent = phase.title;
    $("source-state").textContent = "Temporal function · AGENT PROPOSAL / NOT ACCEPTED";
    $("source-description").textContent = phase.narrative_function || "No local narrative function specified.";
    $("source-ref").textContent = "phases/" + phase.id + " · Response " +
      (state.architectureRequestSha || "unavailable") + " · No fixed chapter length implied";
    var links = $("source-links"); links.replaceChildren();
    function detail(label, value) {
      if (!value) return;
      var p = document.createElement("p"); p.textContent = label + ": " + value; links.appendChild(p);
    }
    function jump(label, facet, key, id) {
      var b = document.createElement("button"); b.type = "button"; b.className = "facet-link";
      b.textContent = label; b.addEventListener("click", function () { visitFacet(facet, key, id); });
      links.appendChild(b);
    }
    detail("Scope", phase.scope);
    detail("Reader experience", phase.reader_experience);
    detail("Aesthetic strategy", phase.aesthetic);
    detail("Transition", phase.transition);
    detail("Local genre roles", (phase.genres || []).map(function (g) {
      return g.genre + " (" + g.role.replace(/_/g, " ") + ")";
    }).join(" · "));
    var phaseNames = {};
    (state.architecture.phases || []).forEach(function (p) { phaseNames[p.id] = p.title; });
    detail("Parallel with", (phase.parallel_with || []).map(function (id) { return phaseNames[id] || id; }).join(" · "));
    var activeIds = (phase.genre_activations || []).map(function (a) { return a.genre_node_id; });
    (phase.genre_activations || []).forEach(function (a) {
      var node = candidateNode(a.genre_node_id);
      var name = node ? node.title : a.genre_node_id;
      detail("Genre activation · " + name, (a.basic_emotions || []).join(" + ") +
        " · Structural function: " + a.structural_function);
      jump("Inspect genre contract: " + name, "genres", null, a.genre_node_id);
      (a.trope_functions || []).forEach(function (t, i) {
        jump("Inspect phase trope function: " + t, "tropes",
          "phase-trope:" + phase.id + ":" + a.genre_node_id + ":" + i, null);
      });
      if (a.structural_function) jump("Inspect phase structural function", "structure",
        "phase-structure:" + phase.id + ":" + a.genre_node_id, null);
    });
    (state.architecture.genre_interactions || []).filter(function (edge) {
      return activeIds.includes(edge.source_genre_id) && activeIds.includes(edge.target_genre_id);
    }).forEach(function (edge) {
      detail("Genre interaction · " + edge.kind.replace(/_/g, " "), edge.mechanism +
        (edge.risk ? " · Risk: " + edge.risk : ""));
    });
  }
  function renderTimeline() {
    var host = $("timeline-phases"); host.replaceChildren();
    if (!state.architecture || !state.architecture.phases.length) {
      var empty = document.createElement("li"); empty.textContent = "No working narrative phases proposed yet.";
      host.appendChild(empty); return;
    }
    var names = {};
    state.architecture.phases.forEach(function (p) { names[p.id] = p.title; });
    state.architecture.phases.slice().sort(function (a, b) { return a.order - b.order || a.id.localeCompare(b.id); })
      .filter(function (phase) { return !state.architectureFocus || phase.scope === state.architectureFocus ||
        phase.scope === "whole_story"; })
      .forEach(function (phase) {
        var li = document.createElement("li"); li.className = "timeline-phase";
        li.setAttribute("aria-current", phase.id === state.selectedPhase ? "step" : "false");
        var pick = document.createElement("button"); pick.type = "button"; pick.className = "timeline-select";
        pick.textContent = phase.title; pick.setAttribute("aria-pressed", String(phase.id === state.selectedPhase));
        pick.addEventListener("click", function () {
          state.selectedPhase = phase.id; state.facetSelection = "phase:" + phase.id;
          renderTimeline(); renderFacetList(); renderInspector(); rememberFocus();
        });
        li.appendChild(pick);
        var roles = (phase.genres || []).map(function (g) {
          return g.genre + " · " + g.role.replace(/_/g, " ");
        });
        var activations = phase.genre_activations || [];
        var emotions = [];
        activations.forEach(function (a) {
          (a.basic_emotions || []).forEach(function (e) { if (!emotions.includes(e)) emotions.push(e); });
        });
        var firstTrope = activations.map(function (a) { return (a.trope_functions || [])[0]; }).find(Boolean);
        var firstFunction = activations.map(function (a) { return a.structural_function; }).find(Boolean);
        function line(kind, value) {
          if (!value) return;
          var p = document.createElement("p"); p.className = "timeline-" + kind;
          p.textContent = value; li.appendChild(p);
        }
        line("roles", roles.join(" · "));
        line("emotions", emotions.join(" · "));
        line("purpose", "Purpose: " + (phase.narrative_function || firstFunction || "open"));
        if (firstTrope) line("trope", "Trope: " + firstTrope);
        if (phase.parallel_with && phase.parallel_with.length)
          line("parallel", "Parallel: " + phase.parallel_with.map(function (id) {
            return names[id] || id;
          }).join(" · "));
        host.appendChild(li);
      });
  }
  function restoreFacetHistory(index) {
    var old = state.facetHistory[index]; if (!old) return;
    state.facetHistory = state.facetHistory.slice(0,index);
    state.architectureFacet = old.facet; state.facetSelection = old.key;
    state.selectedCandidate = old.nodeId;
    state.architectureFocus = old.scope || ""; $("architecture-scope").value = state.architectureFocus;
    state.architectureCenter = old.center || null; state.selectedPhase = old.phase || null;
    $("find-nodes").value = old.search || "";
    state.explanationArrival = old.arrival || null;
    state.explanationInspectRequested = !!old.inspected;
    state.view = state.architectureFacet === "timeline" ? "genre_timeline" : "architecture";
    $("layer-view").value = state.view; render(); rememberFocus();
    if (old.returnLinkId) {
      var links = document.querySelectorAll("[data-semantic-link]");
      Array.prototype.forEach.call(links,function(button) {
        if (button.getAttribute("data-semantic-link") === old.returnLinkId) button.focus();
      });
    }
  }
  function renderStudioExplanation() {
    var host = $("studio-explanatory-hero"), trail = $("studio-semantic-trail");
    var arrival = $("studio-semantic-arrival");
    var active = explanationActive();
    host.hidden = !active; trail.hidden = !active || !state.facetHistory.length;
    arrival.hidden = !active || !state.explanationArrival;
    $("inspector").hidden = active && !state.explanationInspectRequested;
    document.querySelector(".studio").classList.toggle("studio-explanation-full", active && !state.explanationInspectRequested);
    if (!active) return;
    host.replaceChildren(); trail.replaceChildren(); arrival.replaceChildren();
    var projector = window.AuteurStudioExplanations, views = window.AuteurStudioExplanationViews;
    if (!state.architecture || !projector || !views) {
      var noData = document.createElement("p"); noData.className = "muted";
      noData.textContent = "Develop a working architecture proposal to explore its narrative meaning.";
      host.appendChild(noData); return;
    }
    var projection = projector.project(state.architecture,state.architectureRequestSha,null);
    var facet = state.architectureFacet, list = projection[facet] || [];
    var key = state.facetSelection && projector.resolve(projection,facet,state.facetSelection,state.architectureRequestSha)
      ? state.facetSelection : (list.length ? list[0].key : null);
    if (state.facetSelection && state.facetSelection !== key) {
      state.facetSelection = null; state.explanationArrival = null;
      state.explanationInspectRequested = false;
    }
    function onNavigate(link) {
      if (link.requestSha !== state.architectureRequestSha ||
          !projector.resolve(projection,link.targetFacet,link.targetKey,state.architectureRequestSha) ||
          !projector.linksFor(projection,{facet:facet,key:key}).some(function(l) { return l.id === link.id; })) {
        status("Semantic source changed or is unavailable. Refresh the working architecture.");
        return;
      }
      visitFacet(link.targetFacet,link.targetKey,null,link);
    }
    function onInspect(entry) {
      if (!entry || !projector.resolve(projection,facet,entry.key,state.architectureRequestSha)) return;
      state.facetSelection = entry.key; state.explanationInspectRequested = true;
      $("inspector").hidden = false;
      document.querySelector(".studio").classList.remove("studio-explanation-full");
      renderInspector(); rememberFocus();
      $("inspector").scrollIntoView({block:"nearest"});
    }
    var presenter = {genres:views.renderGenre,tropes:views.renderTrope,structure:views.renderStructure}[facet];
    if (presenter) presenter(host,projection,key,onNavigate,onInspect);
    var len = state.facetHistory.length, show = state.facetHistory.slice(-3);
    if (len) {
      var back = document.createElement("button"); back.type = "button";
      back.textContent = "← Previous context"; back.addEventListener("click",function(){restoreFacetHistory(state.facetHistory.length-1);});
      trail.appendChild(back);
      if (len > 3) {
        var earlier = document.createElement("details"), summary = document.createElement("summary");
        summary.textContent = "Earlier ("+(len-3)+")"; earlier.appendChild(summary);
        state.facetHistory.slice(0,-3).forEach(function(old,i) {
          var b = document.createElement("button"); b.type = "button";
          b.textContent = old.facet + (old.key ? " · "+old.key : "");
          b.addEventListener("click",function(){restoreFacetHistory(i);});earlier.appendChild(b);
        });trail.appendChild(earlier);
      }
      show.forEach(function(old,i) {
        var b = document.createElement("button"); b.type = "button";
        var oldProjectionEntry = projector.resolve(projection,old.facet,old.key,state.architectureRequestSha);
        b.textContent = oldProjectionEntry ? oldProjectionEntry.title : old.facet;
        b.addEventListener("click",function(){restoreFacetHistory(len-show.length+i);});trail.appendChild(b);
      });
    }
    if (state.explanationArrival) {
      var context = document.createElement("p");
      context.textContent = "From “"+state.explanationArrival.from+"” → "+state.explanationArrival.verb+
        " → “"+state.explanationArrival.to+"” · Source-backed proposal, not accepted story.";
      var source = document.createElement("small"); source.className = "muted";
      source.textContent = "Source: "+state.explanationArrival.sourceRef;
      arrival.append(context,source);
    }
  }
  function render() {
    var designing = state.workspace === "architecture";
    $("architecture-context").hidden = !designing;
    $("architecture-work-area").classList.toggle("is-architecture", designing);
    $("architecture-legend").hidden = !designing || state.view !== "architecture";
    var context = state.architecture && state.architecture.summary ? state.architecture.summary :
      "Explore the provisional architecture; select a node to inspect its connections.";
    $("architecture-context-summary").textContent = context;
    $("architecture-context-summary").title = context;
    $("working-group-control").hidden = designing;
    $("inspector").setAttribute("aria-label", designing ? "Architecture component inspector" : "Story item inspector");
    $("viewport").setAttribute("aria-label", designing ? "Interactive proposed narrative architecture graph" :
      "Story canvas. Use Add controls to create notes; arrow keys move focused nodes.");
    ["add-note", "add-character", "add-scene", "connect-shortcut", "write-shortcut"].forEach(function (id) {
      $(id).hidden = designing;
    });
    $("architecture-tools").hidden = !designing;
    $("realization-tools").hidden = designing;
    $("realization-focus-label").textContent = candidateNode(state.selectedCandidate)
      ? "Architecture focus: " + candidateNode(state.selectedCandidate).title
      : "Architecture focus: whole story";
    $("emotional-design").hidden = !designing || !state.architecture ||
      !(state.architecture.emotion_targets || []).length;
    ["workspace-architecture", "workspace-realization"].forEach(function (id) {
      $(id).setAttribute("aria-pressed", String(id === "workspace-" + state.workspace));
    });
    Array.prototype.forEach.call($("layer-view").options, function (opt) {
      opt.hidden = designing ? !["architecture", "genre_timeline"].includes(opt.value)
        : ["architecture", "genre_timeline"].includes(opt.value);
    });
    renderEmotionalOverview();
    renderFacetList();
    $("architecture-clear-focus").hidden = state.view !== "architecture" || !state.architectureCenter;
    $("viewport").hidden = state.view === "genre_timeline" || explanationActive();
    $("genre-timeline").hidden = state.view !== "genre_timeline";
    renderTimeline();
    renderGroups();
    $("canvas-legend").textContent = state.view === "realization_candidates"
      ? "Working concrete story proposals link back to Narrative Architecture; none is accepted fiction."
      : state.view === "relationships"
      ? "Working associations are distinct from accepted, read-only relationship evidence."
      : state.view === "architecture" ? "Agent-generated structure is a proposal, not accepted story meaning. Copy an element to edit working notes."
      : state.view === "genre_timeline" ? "Genre prominence and emotional phases are provisional; no chapter lengths or accepted contracts are implied."
      : state.view === "create" ? "Working ideas and connections are not accepted story facts."
      : "Source-backed elements are read-only; canvas layout never changes story authority.";
    var host = $("nodes"); host.replaceChildren();
    var awaitingArchitecture = state.view === "architecture" &&
      (!state.architecture || !state.architecture.nodes.length);
    $("empty-state").hidden = state.view === "architecture" ? !awaitingArchitecture :
      state.items.length > 0 || (state.view === "realization_candidates" && !!state.realization);
    $("empty-state").querySelector("h1").textContent = designing
      ? "Explore your narrative architecture" : "What story do you want to tell?";
    $("empty-state").querySelector("p").textContent = designing
      ? "Describe an optional Story Vision above, then ask the coding agent to develop a provisional architecture graph."
      : "Start anywhere. Create an idea, character or scene. Nothing becomes accepted story material here.";
    $("start").textContent = designing ? "Develop architecture" : "Add your first idea";
    state.items.forEach(function (item) {
      if (!visibleWorking(item)) return;
      var pos = state.positions[item.id];
      var node = document.createElement("button"); node.type = "button"; node.className = "node";
      node.dataset.itemId = item.id; node.dataset.kind = item.kind;
      node.style.left = pos.x + "px"; node.style.top = pos.y + "px";
      node.setAttribute("aria-pressed", String(item.id === state.selected));
      node.setAttribute("aria-label", item.kind + ": " + item.title + ". Arrow keys move this item.");
      var title = document.createElement("span"); title.className = "label"; title.textContent = item.title;
      var type = document.createElement("span"); type.className = "type"; type.textContent = item.kind + " · Working";
      node.append(title, type);
      node.addEventListener("click", function () { choose(item.id); });
      node.addEventListener("keydown", function (event) {
        var arrows = { ArrowLeft: [-12, 0], ArrowRight: [12, 0], ArrowUp: [0, -12], ArrowDown: [0, 12] };
        if (!arrows[event.key]) return;
        event.preventDefault(); var delta = arrows[event.key];
        pos.x = Math.max(0, Math.min(1400, pos.x + delta[0]));
        pos.y = Math.max(0, Math.min(1040, pos.y + delta[1]));
        node.style.left = pos.x + "px"; node.style.top = pos.y + "px"; drawEdges(); scheduleSave();
      });
      node.addEventListener("pointerdown", function (event) {
        if (event.button !== 0) return;
        var originX = event.clientX, originY = event.clientY, startX = pos.x, startY = pos.y;
        node.setPointerCapture(event.pointerId);
        function move(e) {
          pos.x = Math.max(0, Math.min(1400, startX + (e.clientX - originX) / state.zoom));
          pos.y = Math.max(0, Math.min(1040, startY + (e.clientY - originY) / state.zoom));
          node.style.left = pos.x + "px"; node.style.top = pos.y + "px"; drawEdges();
        }
        function finish() { node.removeEventListener("pointermove", move); node.removeEventListener("pointerup", finish); node.removeEventListener("pointercancel", finish); scheduleSave(); }
        node.addEventListener("pointermove", move); node.addEventListener("pointerup", finish); node.addEventListener("pointercancel", finish);
      });
      host.appendChild(node);
    });
        if (state.derived) state.derived.nodes.filter(function (n) { return visibleDerived(n) && matches(n); }).forEach(function (item) {
      var pos = state.derivedPositions[item.id]; if (!pos) return;
      var node = document.createElement("button"); node.type = "button";
      node.className = "node derived"; node.dataset.itemId = item.id; node.dataset.kind = item.kind;
      if (item.impact_role) node.dataset.impact = item.impact_role;
      node.style.left = pos.x + "px"; node.style.top = pos.y + "px";
      node.setAttribute("aria-pressed", String(item.id === state.selectedDerived));
      node.setAttribute("aria-label", "Read only " + item.kind + ": " + item.title + ". " + item.status);
      var title = document.createElement("span"); title.className = "label"; title.textContent = item.title;
      var type = document.createElement("span"); type.className = "type"; type.textContent = item.status + " · Read-only";
      node.append(title, type); node.addEventListener("click", function () { chooseDerived(item.id); });
      host.appendChild(node);
    });
    if (state.realization && state.view === "realization_candidates") {
      state.realization.elements.filter(realizationVisible).forEach(function (item) {
        var pos = state.realizationPositions[item.id];
        var button = document.createElement("button"); button.type = "button";
        button.className = "node realization"; button.dataset.itemId = item.id;
        button.style.left = pos.x + "px"; button.style.top = pos.y + "px";
        button.setAttribute("aria-pressed", String(item.id === state.selectedRealization));
        button.setAttribute("aria-label", "Working story realization: " + item.kind + " " + item.title);
        var label = document.createElement("span"); label.className = "label"; label.textContent = item.title;
        var type = document.createElement("span"); type.className = "type";
        type.textContent = item.kind + " · Proposed";
        button.append(label, type);
        button.addEventListener("click", function () { chooseRealization(item.id); });
        host.appendChild(button);
      });
    }
    if (state.architecture && state.view === "architecture") {
      state.architecture.nodes.filter(candidateVisible).forEach(function (item) {
        var pos = state.candidatePositions[item.id]; if (!pos) return;
        var button = document.createElement("button"); button.type = "button";
        button.className = "node candidate"; button.dataset.itemId = item.id;
        button.dataset.kind = item.category;
        var focusKinds = {emotions:["reader_experience"], genres:["genre"], tropes:["trope"],
          structure:["engine", "structure"]}[state.architectureFacet];
        if (focusKinds && state.architecture.nodes.some(function (n) { return focusKinds.includes(n.category); }) &&
            !focusKinds.includes(item.category) && item.id !== state.selectedCandidate)
          button.classList.add("facet-context");
        button.style.left = pos.x + "px"; button.style.top = pos.y + "px";
        button.setAttribute("aria-pressed", String(item.id === state.selectedCandidate));
        button.setAttribute("aria-label", "Working architecture proposal: " + item.category + ", " + item.title);
        var label = document.createElement("span"); label.className = "label"; label.textContent = item.title;
        var type = document.createElement("span"); type.className = "type"; type.textContent = item.category + " · Proposed";
        button.append(label, type); button.addEventListener("click", function () { chooseCandidate(item.id); });
        host.appendChild(button);
      });
    }
    drawEdges(); renderStudioExplanation(); renderInspector(); renderOutline(); showVision(); transform();
  }
  // Keep the inspector and the working-document model in sync before focus changes.
  // This is working author material only; it cannot accept story canon.
  function captureInspectorFields() {
    var item = selected(); if (!item || !remote.ready) return;
    item.title = $("title").value.trim() || "Untitled";
    item.kind = $("kind").value;
    item.content = $("content").value;
    item.group = $("group").value.trim();
    if (item.id === "story-vision") $("vision-text").value = item.content;
    $("write").hidden = item.kind !== "scene";
    Array.prototype.forEach.call(document.querySelectorAll(".node"), function (node) {
      if (node.dataset.itemId !== item.id) return;
      var label = node.querySelector(".label");
      if (label) label.textContent = item.title;
      node.dataset.kind = item.kind;
      node.setAttribute("aria-label", item.kind + ": " + item.title + ". Arrow keys move this item.");
    });
    scheduleSave();
    status(remote.failed ? "SAVE FAILED: export your working notes before leaving." :
      "Working note changed. Saving locally...");
  }
  function saveCurrent() {
    var item = selected(); if (!item) return;
    item.title = $("title").value.trim() || "Untitled";
    item.kind = $("kind").value; item.content = $("content").value; item.group = $("group").value.trim();
    render(); queueSave(); status(remote.failed ? "SAVE FAILED: export your working notes before reopening." : "Working item updated. Saving locally...");
  }
  function connect() {
    var item = selected(), target = $("target").value; if (!item || !target || target === item.id) return;
    var exists = state.connections.some(function (e) { return e.source === item.id && e.target === target && e.label === $("relation").value.trim(); });
    if (!exists) state.connections.push({ id: id("edge"), source: item.id, target: target, label: $("relation").value.trim() });
    $("relation").value = ""; render(); queueSave(); status("Working association created. It does not alter accepted relationships.");
  }
  function captureScene() {
    var item = selected(); if (!item || item.kind !== "scene") return;
    item.content = $("scene-text").value;
    item.scene_premise = $("scene-premise").value;
    item.scene_intent = $("scene-intent").value;
  }
  function draftStatus(projection) {
    var draft = projection.draft || {};
    var stateName = draft.status || "unknown";
    $("refresh-draft").hidden = false;
    $("generation-status").textContent =
      stateName === "awaiting_host_agent" ? "Request staged for the active coding agent. Check again after it fulfills the request." :
      stateName === "generating" ? "Generation is in progress." :
      stateName === "generation_failed" ? "Generation failed: " + (draft.error || "unknown error") :
      "Quick Draft status: " + stateName;
    if (projection.draft_text) {
      $("generation-result").hidden = false;
      $("generated-prose").value = projection.draft_text;
      $("open-quick-draft").href = "/beginner.html?quick_draft=" + encodeURIComponent(projection.session_id);
    } else {
      $("generation-result").hidden = true;
      $("generated-prose").value = "";
    }
  }
  function refreshDraft() {
    var item = selected();
    if (!item || !item.quick_draft_session_id) return;
    fetch("/api/beginner/quick-draft/" + encodeURIComponent(item.quick_draft_session_id))
      .then(apiJson).then(function (projection) {
        if (selected() && selected().id === item.id) draftStatus(projection);
      })
      .catch(function (error) {
        if (selected() && selected().id === item.id)
          $("generation-status").textContent = "Could not check Quick Draft: " + error.message;
      });
  }
  function generateScene() {
    var item = selected();
    if (!item || item.kind !== "scene" || remote.failed || !remote.ready) return;
    captureScene();
    var premise = item.scene_premise.trim(), intent = item.scene_intent.trim();
    if (!premise || !intent) {
      $("generation-status").textContent = "Enter both a working story premise and a scene intent before generation.";
      return;
    }
    $("generate-scene").disabled = true;
    $("generation-status").textContent = "Preserving scene intent before staging host-agent request...";
    Promise.resolve(queueSave()).then(function () {
      if (remote.failed) throw new Error("The working canvas was not saved.");
      return fetch("/api/beginner/quick-draft", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ premise: premise, first_scene: intent })
      }).then(apiJson);
    }).then(function (projection) {
      if (!state.items.includes(item)) return;
      item.quick_draft_session_id = projection.session_id;
      queueSave();
      if (selected() && selected().id === item.id) draftStatus(projection);
      status("Host-agent Quick Draft session linked to " + item.title + ". No story acceptance.");
    }).catch(function (error) {
      if (selected() && selected().id === item.id)
        $("generation-status").textContent = "Quick Draft request failed: " + error.message;
      status("Quick Draft request failed: " + error.message);
    }).finally(function () { $("generate-scene").disabled = false; });
  }
  function useGenerated() {
    var item = selected(); if (!item) return;
    var prose = $("generated-prose").value;
    if (!prose) return;
    item.content = prose; $("scene-text").value = prose;
    queueSave(); status("Working candidate copied into scene. Nothing accepted.");
  }
  function concealScene() {
    $("scene-panel").hidden = true;
    $("scene-panel").classList.remove("expanded");
    document.body.classList.remove("scene-docked");
  }
  function displayScene(caret, expanded) {
    var item = selected(); if (!item || item.kind !== "scene") return;
    $("scene-heading").textContent = item.title;
    $("scene-text").value = item.content;
    $("scene-premise").value = item.scene_premise || "";
    $("scene-intent").value = item.scene_intent || "";
    $("generation-result").hidden = true;
    $("generation-status").textContent = item.quick_draft_session_id
      ? "A prior Quick Draft request is linked to this scene."
      : "Working prose can be written here without requesting generation.";
    $("refresh-draft").hidden = !item.quick_draft_session_id;
    $("scene-panel").hidden = false;
    document.body.classList.add("scene-docked");
    $("scene-panel").classList.toggle("expanded", !!expanded);
    $("expand-scene").textContent = expanded ? "Split view" : "Focus writing";
    $("expand-scene").setAttribute("aria-pressed", String(!!expanded));
    $("scene-text").focus();
    if (Number.isInteger(caret)) {
      var n = Math.max(0, Math.min(caret, $("scene-text").value.length));
      $("scene-text").setSelectionRange(n, n);
    }
    rememberFocus();
    if (item.quick_draft_session_id) refreshDraft();
  }
  function sceneOpen() {
    var item = selected(); if (!item || item.kind !== "scene") return;
    if (!$("scene-panel").hidden) { $("scene-text").focus(); return; }
    saveCurrent(); displayScene();
  }
  function sceneSave() {
    var item = selected(); if (!item || item.kind !== "scene") return;
    captureScene(); $("content").value = item.content;
    concealScene(); render(); queueSave(); rememberFocus();
    status("Working prose updated. This editor does not submit generation or acceptance.");
  }
  function exportCanvas() {
    var data = { schema_version: 1, items: state.items, connections: state.connections, positions: state.positions,
      viewport: { pan_x: state.panX, pan_y: state.panY, zoom: state.zoom } };
    var objectUrl = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
    var link = document.createElement("a"); link.href = objectUrl; link.download = "auteur-working-canvas.json";
    document.body.appendChild(link); link.click(); link.remove();
    setTimeout(function () { URL.revokeObjectURL(objectUrl); }, 1000);
    status("Export requested. Retain the JSON file to recover this prototype canvas.");
  }
  function validCanvas(data) {
    if (!data || data.schema_version !== 1 || !Array.isArray(data.items) || !Array.isArray(data.connections) || !data.positions || typeof data.positions !== "object" || data.items.length > 200 || data.connections.length > 500) throw new Error("Unsupported canvas file");
    var seen = new Set();
    data.items.forEach(function (item) {
      if (!item || typeof item.id !== "string" || !/^[a-z0-9_-]{1,80}$/.test(item.id) || seen.has(item.id) ||
          typeof item.title !== "string" || item.title.length > 120 || typeof item.content !== "string" || item.content.length > 20000 ||
          !["note", "character", "scene", "place", "question"].includes(item.kind) ||
          (item.group != null && (typeof item.group !== "string" || item.group.length > 80)) ||
          ["scene_premise", "scene_intent"].some(function (field) {
            return item[field] != null && (typeof item[field] !== "string" || item[field].length > 4000);
          }) || (item.quick_draft_session_id != null &&
            (typeof item.quick_draft_session_id !== "string" || item.quick_draft_session_id.length > 120))
      ) throw new Error("Invalid canvas item");
      seen.add(item.id);
      var pos = data.positions[item.id];
      if (!pos || !Number.isFinite(pos.x) || !Number.isFinite(pos.y) || pos.x < 0 || pos.x > 1400 || pos.y < 0 || pos.y > 1040) throw new Error("Invalid canvas layout");
    });
    var ids = new Set();
    if (data.viewport && (!Number.isFinite(data.viewport.pan_x) || !Number.isFinite(data.viewport.pan_y) ||
        !Number.isFinite(data.viewport.zoom) || Math.abs(data.viewport.pan_x) > 5000 || Math.abs(data.viewport.pan_y) > 5000 ||
        data.viewport.zoom < 0.5 || data.viewport.zoom > 1.5)) throw new Error("Invalid viewport");
    data.connections.forEach(function (edge) {
      if (!edge || typeof edge.id !== "string" || !/^[a-z0-9_-]{1,80}$/.test(edge.id) || ids.has(edge.id) ||
          !seen.has(edge.source) || !seen.has(edge.target) || edge.source === edge.target ||
          typeof edge.label !== "string" || edge.label.length > 120) throw new Error("Invalid connection");
      ids.add(edge.id);
    });
  }
  function importCanvas(event) {
    var file = event.target.files[0]; event.target.value = ""; if (!file) return;
    if (!remote.ready || remote.failed) { status("Canvas is not safely available yet. Import is disabled to prevent losing your file."); return; }
    if (file.size > 1024 * 1024) { status("Import rejected: file exceeds 1 MB."); return; }
    file.text().then(function (raw) {
      var data = JSON.parse(raw); validCanvas(data);
      if (!$("scene-panel").hidden) { captureScene(); concealScene(); queueSave(); }
      state.items = data.items; state.connections = data.connections; state.positions = data.positions;
      state.selected = data.items.length ? data.items[0].id : null; state.serial += 1;
      if (data.viewport && Number.isFinite(data.viewport.zoom)) { state.panX = data.viewport.pan_x; state.panY = data.viewport.pan_y; state.zoom = data.viewport.zoom; }
      else { state.panX = 0; state.panY = 0; state.zoom = 1; }
      render(); queueSave(); status(remote.failed ? "SAVE FAILED: export your working notes." : "Working canvas imported. Saving locally...");
    }).catch(function (error) { status("Import rejected: " + error.message); });
  }
  function removeCurrent() {
    var item = selected(); if (!item || !window.confirm("Remove this working item? You can undo during this session.")) return;
    if (!$("scene-panel").hidden) { captureScene(); concealScene(); }
    state.undo = { item: item, pos: state.positions[item.id], links: state.connections.filter(function (e) { return e.source === item.id || e.target === item.id; }) };
    state.items = state.items.filter(function (entry) { return entry.id !== item.id; });
    state.connections = state.connections.filter(function (e) { return e.source !== item.id && e.target !== item.id; });
    delete state.positions[item.id]; state.selected = null; render();
    queueSave(); status("Working item removed. Press Ctrl+Z to undo; saving locally.");
  }
  document.addEventListener("keydown", function (event) {
    if (event.ctrlKey && event.key.toLowerCase() === "z" && state.undo && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      event.preventDefault(); var old = state.undo; state.undo = null;
      state.items.push(old.item); state.positions[old.item.id] = old.pos;
      state.connections.push.apply(state.connections, old.links); state.selected = old.item.id; render(); queueSave();
    }
  });
  window.addEventListener("beforeunload", function (event) {
    if (!hasUnsavedChanges()) return;
    event.preventDefault();
    event.returnValue = "";
  });
  ["legacy-home", "open-quick-draft"].forEach(function (id) {
    $(id).addEventListener("click", function (event) {
      event.preventDefault();
      leaveForLegacy(this.href);
    });
  });
  $("new-canvas").addEventListener("click", function () { navigateCanvas(id("canvas")); });
  $("canvas-picker").addEventListener("change", function () {
    if (this.value && this.value !== remote.canvasId) navigateCanvas(this.value);
  });
  $("add-note").addEventListener("click", function () { newItem("note"); });
  $("add-character").addEventListener("click", function () { newItem("character"); });
  $("add-scene").addEventListener("click", function () { newItem("scene"); });
  $("start").addEventListener("click", function () {
    if (state.workspace === "architecture") requestArchitecture("");
    else newItem("note");
  });
  $("vision-text").addEventListener("input", updateVision);
  $("vision-save").addEventListener("click", function () {
    var savedText = $("vision-text").value;
    updateVision();
    if (remote.timer !== null) { clearTimeout(remote.timer); remote.timer = null; queueSave(); }
    // Do not collapse unsaved text if persistence failed or new edits arrived.
    Promise.resolve(remote.queue).then(function () {
      if (!remote.ready || remote.failed || !visionItem() ||
          !visionItem().content.trim() || visionItem().content !== savedText) return;
      showVision();
      $("vision-disclosure").open = false;
    });
  });
  $("vision-write").addEventListener("click", function () {
    switchWorkspace("realization"); $("write-shortcut").click();
  });
  $("workspace-architecture").addEventListener("click", function () { switchWorkspace("architecture"); });
  $("workspace-realization").addEventListener("click", function () { switchWorkspace("realization"); });
  Array.prototype.forEach.call(document.querySelectorAll("[data-architecture-facet]"), function (button) {
    button.addEventListener("click", function () {
      state.facetHistory = []; state.facetSelection = null; state.selectedCandidate = null;
      state.explanationArrival = null; state.explanationInspectRequested = false;
      state.architectureFacet = button.dataset.architectureFacet;
      state.view = state.architectureFacet === "timeline" ? "genre_timeline" : "architecture";
      $("layer-view").value = state.view; render(); rememberFocus();
    });
  });
  $("architecture-facet-back").addEventListener("click", function () { restoreFacetHistory(state.facetHistory.length-1); });
  $("architecture-develop").addEventListener("click", function () { requestArchitecture(""); });
  $("architecture-refresh").addEventListener("click", loadArchitecture);
  $("architecture-revise").addEventListener("click", function () {
    var intent = $("architecture-instruction").value.trim();
    if (!intent) { $("architecture-status").textContent = "Describe the desired revision first."; return; }
    requestArchitecture(intent);
  });
  $("architecture-complete").addEventListener("click", submitArchitecture);
  $("realization-develop").addEventListener("click", function () { requestRealization(""); });
  $("realization-refresh").addEventListener("click", loadRealization);
  $("realization-revise").addEventListener("click", function () {
    var instruction = $("realization-instruction").value.trim();
    if (!instruction) { $("realization-status").textContent = "Describe the desired change first."; return; }
    requestRealization(instruction);
  });
  $("realization-complete").addEventListener("click", submitRealization);
  $("realization-apply").addEventListener("click", applyRealizationReview);
  $("realization-copy").addEventListener("click", copyRealization);
  $("realization-inspect").addEventListener("click", inspectRealizationPurpose);
  $("realization-feedback").addEventListener("click", proposeArchitectureFromRealization);
  $("architecture-apply").addEventListener("click", applyReviewedArchitecture);
  $("candidate-copy").addEventListener("click", copyCandidate);
  $("candidate-focus").addEventListener("click", focusRelatedArchitecture);
  $("architecture-clear-focus").addEventListener("click", showWholeArchitecture);
  $("architecture-scope").addEventListener("change", function () {
    state.architectureFocus = this.value; state.architectureCenter = null;
    if (candidateNode(state.selectedCandidate) && !candidateVisible(candidateNode(state.selectedCandidate)))
      state.selectedCandidate = null;
    render(); rememberFocus();
  });
  $("fit").addEventListener("click", fit);
  $("connect-shortcut").addEventListener("click", function () {
    if (!selected()) { status("Select a working idea to connect first."); return; }
    if (!$("scene-panel").hidden) sceneSave();
    $("target").focus();
    if ($("connect").disabled) status("Create another working item before connecting ideas.");
  });
  $("write-shortcut").addEventListener("click", function () {
    if (!remote.ready || remote.failed) { status("Working canvas is unavailable; cannot open a new scene."); return; }
    if (!$("scene-panel").hidden) { $("scene-text").focus(); return; }
    if (!selected() || selected().kind !== "scene") newItem("scene");
    sceneOpen();
  });
  $("arrange-group").addEventListener("click", arrangeVisible);
  $("group-filter").addEventListener("change", function () {
    if (!$("scene-panel").hidden) { captureScene(); concealScene(); scheduleSave(); }
    state.focusGroup = this.value;
    if (selected() && !visibleWorking(selected())) state.selected = null;
    render(); rememberFocus();
  });
  $("find-nodes").addEventListener("input", render);
  $("show-evidence").addEventListener("click", loadEvidence);
  $("relationship-chapter").addEventListener("change", function () { render(); status(this.value ? "Showing relationships with recorded changes in " + this.value + ". Current relation values are not historical snapshots." : "Showing all declared relationships."); });
  $("show-book").addEventListener("click", loadBook);
  $("preview-impact").addEventListener("click", previewImpact);
  $("layer-view").addEventListener("change", function () {
    state.view = this.value;
    state.workspace = ["architecture", "genre_timeline"].includes(state.view) ? "architecture" : "realization";
    if (state.workspace === "realization") state.lastRealizationView = state.view;
    else { state.architectureFacet = state.view === "genre_timeline" ? "timeline" : "overview"; state.facetSelection = null; }
    if (this.value === "book" && !$("book-heading").textContent.startsWith("Chapter")) loadBook();
    else render();
    rememberFocus();
  });
  $("zoom").addEventListener("input", function () { state.zoom = Number(this.value) / 100; transform(); scheduleSave(); });
  $("save").addEventListener("click", saveCurrent);
  ["title", "kind", "content", "group"].forEach(function (id) {
    $(id).addEventListener("input", captureInspectorFields);
    $(id).addEventListener("change", captureInspectorFields);
  });
  $("connect").addEventListener("click", connect);
  $("write").addEventListener("click", sceneOpen);
  $("close-scene").addEventListener("click", sceneSave);
  $("expand-scene").addEventListener("click", function () {
    var expanded = !$("scene-panel").classList.contains("expanded");
    $("scene-panel").classList.toggle("expanded", expanded);
    $("expand-scene").textContent = expanded ? "Split view" : "Focus writing";
    $("expand-scene").setAttribute("aria-pressed", String(expanded));
    rememberFocus();
  });
  $("use-scene-as-intent").addEventListener("click", function () {
    var item = selected();
    if (!item || item.kind !== "scene" || !$("scene-text").value.trim()) {
      $("generation-status").textContent = "Write some scene notes first, then use them as editable intent."; return;
    }
    $("scene-intent").value = $("scene-text").value.trim().slice(0, 4000);
    captureScene(); scheduleSave(); rememberFocus();
    $("generation-status").textContent = "Copied working scene notes as editable generation intent. Review before requesting.";
  });
  $("save-scene").addEventListener("click", sceneSave);
  $("generate-scene").addEventListener("click", generateScene);
  $("refresh-draft").addEventListener("click", refreshDraft);
  $("use-generated").addEventListener("click", useGenerated);
  ["scene-premise", "scene-intent", "scene-text"].forEach(function (id) {
    $(id).addEventListener("input", function () { captureScene(); scheduleSave(); rememberFocus(); });
  });
  ["scene-text", "content"].forEach(function (id) {
    $(id).addEventListener("keyup", rememberFocus);
    $(id).addEventListener("click", rememberFocus);
  });
  $("download").addEventListener("click", exportCanvas);
  $("import").addEventListener("change", importCanvas);
  $("remove").addEventListener("click", removeCurrent);
  $("retry-save").addEventListener("click", retrySave);
  $("restore-deleted").addEventListener("click", restoreDeleted);
  $("viewport").addEventListener("keydown", function (event) {
    if (event.target !== this) return;
    var moves = { ArrowLeft: [50, 0], ArrowRight: [-50, 0], ArrowUp: [0, 50], ArrowDown: [0, -50] };
    if (!moves[event.key]) return;
    event.preventDefault(); state.panX += moves[event.key][0]; state.panY += moves[event.key][1];
    transform(); scheduleSave();
  });
  $("viewport").addEventListener("pointerdown", function (event) {
    if (event.target !== this && event.target !== $("nodes") && event.target !== $("world")) return;
    if (event.button !== 0) return;
    var startX = event.clientX, startY = event.clientY, baseX = state.panX, baseY = state.panY;
    this.setPointerCapture(event.pointerId);
    function move(e) { state.panX = baseX + e.clientX - startX; state.panY = baseY + e.clientY - startY; transform(); }
    function finish() { $("viewport").removeEventListener("pointermove", move); $("viewport").removeEventListener("pointerup", finish); $("viewport").removeEventListener("pointercancel", finish); scheduleSave(); }
    this.addEventListener("pointermove", move); this.addEventListener("pointerup", finish); this.addEventListener("pointercancel", finish);
  });
  $("layer-view").value = state.view;
  render();
  $("evidence-workspace").value = new URLSearchParams(window.location.search).get("workspace") || "";
  openRemote();
}());
