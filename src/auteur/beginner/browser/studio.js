(function () {
  "use strict";
  var state = { items: [], connections: [], positions: {}, selected: null, selectedDerived: null, derived: null, derivedPositions: {}, view: "create", focusGroup: "", panX: 0, panY: 0, zoom: 1, serial: 0, undo: null };
  // Local, noncanonical working document: server is the persistence owner.
  var remote = { canvasId: null, revision: 0, ready: false, failed: false, queue: Promise.resolve(), timer: null, savedSnapshot: null };
  state.deleted = {};
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
      window.localStorage.setItem(focusKey(), JSON.stringify({
        selected: state.selected, view: state.view, group: state.focusGroup,
        editorOpen: open, expanded: open && $("scene-panel").classList.contains("expanded"),
        caret: field.selectionStart || 0
      }));
    } catch (error) { status("Your canvas is saved; this browser cannot remember the current focus: " + error.message); }
  }
  function restoreFocus() {
    var saved;
    try { saved = JSON.parse(window.localStorage.getItem(focusKey()) || "null"); }
    catch (error) { status("Previous focus unavailable; working canvas remains safe: " + error.message); return null; }
    if (!saved || !state.items.some(function (item) { return item.id === saved.selected; })) return null;
    state.focusGroup = typeof saved.group === "string" ? saved.group : "";
    state.view = ["create", "relationships", "all"].includes(saved.view) ? saved.view : "create";
    state.selected = saved.selected;
    if (!visibleWorking(selected())) { state.view = "create"; state.focusGroup = ""; }
    $("layer-view").value = state.view;
    return saved;
  }
  function loadRemote(doc) {
    state.items = doc.items; state.connections = doc.connections; state.positions = doc.positions;
    state.selected = state.items.length ? state.items[0].id : null;
    state.panX = doc.viewport.pan_x; state.panY = doc.viewport.pan_y; state.zoom = doc.viewport.zoom;
    $("zoom").value = String(Math.round(state.zoom * 100));
    remote.revision = doc.revision; remote.ready = true;
    state.deleted = doc.deleted || {}; showRecoveryAction();
    remote.savedSnapshot = JSON.stringify(snapshot());
    var focus = restoreFocus();
    render();
    if (focus && focus.editorOpen && selected() && selected().kind === "scene") {
      displayScene(focus.caret, focus.expanded);
    }
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
        if (row.derived) chooseDerived(row.item.id); else choose(row.item.id);
        var pos = row.derived ? state.derivedPositions[row.item.id] : state.positions[row.item.id];
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
    var items = state.items.filter(visibleWorking).sort(function (a, b) {
      return ((a.group || "") + "/" + a.title).localeCompare((b.group || "") + "/" + b.title);
    });
    if (!items.length) { status("No working items in this view to arrange."); return; }
    if (items.length > 112) { status("Focus one group before arranging this large canvas."); return; }
    items.forEach(function (item, i) { state.positions[item.id] = gridPosition(i); });
    render(); fit();
    status("Working items arranged by group. Arrangement changes layout only.");
  }
  function transform() { $("world").style.transform = "translate(" + state.panX + "px," + state.panY + "px) scale(" + state.zoom + ")"; }
  function newItem(kind) {
    if (!remote.ready || remote.failed) { status("Cannot edit while local canvas is unavailable. Export your notes if needed."); return; }
    if (state.items.length >= 200) { status("The working canvas has reached its 200-item safety bound."); return; }
    if (!$("scene-panel").hidden) { captureScene(); concealScene(); scheduleSave(); }
    var pos = availablePosition();
    var item = { id: id("item"), kind: kind, title: kind === "note" ? "New idea" : "New " + kind,
      content: "", group: state.focusGroup };
    state.items.push(item);
    state.positions[item.id] = pos;
    state.selected = item.id; state.selectedDerived = null; state.view = "create"; $("layer-view").value = "create";
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
        state.view = "impact"; $("layer-view").value = "impact"; state.selected = null; state.selectedDerived = null;
        render();
        status("Hypothetical dependency paths only. Nothing has been revised or accepted.");
      }).catch(function (error) { status("Impact preview unavailable: " + error.message); });
  }
  function chooseDerived(nodeId) {
    if (!$("scene-panel").hidden) { captureScene(); concealScene(); scheduleSave(); }
    state.selected = null; state.selectedDerived = nodeId;
    Array.prototype.forEach.call(document.querySelectorAll(".node"), function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.itemId === nodeId));
    });
    renderInspector();
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
    var source = state.derived && state.derived.nodes.find(function (n) { return n.id === state.selectedDerived; });
    $("source-detail").hidden = !source;
    $("book-orientation").hidden = state.view !== "book";
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
    var item = selected();
    $("inspector-empty").hidden = !!item;
    $("inspector-fields").hidden = !item;
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
    state.selected = itemId; state.selectedDerived = null;
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
  function render() {
    renderGroups();
    $("canvas-legend").textContent = state.view === "relationships"
      ? "Solid nodes and green lines: working ideas only. Dashed nodes and blue lines: read-only source evidence. Canvas actions do not accept story canon."
      : state.view === "create" ? "Working ideas and connections are not accepted story facts."
      : "Source-backed elements are read-only; canvas layout never changes story authority.";
    var host = $("nodes"); host.replaceChildren();
    $("empty-state").hidden = state.items.length > 0;
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
    drawEdges(); renderInspector(); renderOutline(); transform();
  }
  // Keep the inspector and the working-document model in sync before focus changes.
  // This is working author material only; it cannot accept story canon.
  function captureInspectorFields() {
    var item = selected(); if (!item || !remote.ready) return;
    item.title = $("title").value.trim() || "Untitled";
    item.kind = $("kind").value;
    item.content = $("content").value;
    item.group = $("group").value.trim();
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
      .then(apiJson).then(draftStatus)
      .catch(function (error) { $("generation-status").textContent = "Could not check Quick Draft: " + error.message; });
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
      item.quick_draft_session_id = projection.session_id;
      queueSave(); draftStatus(projection);
      status("Host-agent Quick Draft session linked to working scene. No story acceptance.");
    }).catch(function (error) {
      $("generation-status").textContent = "Quick Draft request failed: " + error.message;
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
      state.items = data.items; state.connections = data.connections; state.positions = data.positions;
      state.selected = data.items.length ? data.items[0].id : null; state.serial += 1;
      if (data.viewport && Number.isFinite(data.viewport.zoom)) { state.panX = data.viewport.pan_x; state.panY = data.viewport.pan_y; state.zoom = data.viewport.zoom; }
      else { state.panX = 0; state.panY = 0; state.zoom = 1; }
      render(); queueSave(); status(remote.failed ? "SAVE FAILED: export your working notes." : "Working canvas imported. Saving locally...");
    }).catch(function (error) { status("Import rejected: " + error.message); });
  }
  function removeCurrent() {
    var item = selected(); if (!item || !window.confirm("Remove this working item? You can undo during this session.")) return;
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
  $("start").addEventListener("click", function () { newItem("note"); });
  $("fit").addEventListener("click", fit);
  $("connect-shortcut").addEventListener("click", function () {
    if (!selected()) { status("Select a working idea to connect first."); return; }
    if (!$("scene-panel").hidden) sceneSave();
    $("target").focus();
    if ($("connect").disabled) status("Create another working item before connecting ideas.");
  });
  $("write-shortcut").addEventListener("click", function () {
    if (!remote.ready || remote.failed) { status("Working canvas is unavailable; cannot open a new scene."); return; }
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
  render();
  $("evidence-workspace").value = new URLSearchParams(window.location.search).get("workspace") || "";
  openRemote();
}());
