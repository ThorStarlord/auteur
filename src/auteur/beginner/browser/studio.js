(function () {
  "use strict";
  var state = { items: [], connections: [], positions: {}, selected: null, panX: 0, panY: 0, zoom: 1, serial: 0, undo: null };
  var svgNS = "http://www.w3.org/2000/svg";
  function $(id) { return document.getElementById(id); }
  function status(message) { $("status").textContent = message; }
  function id(prefix) { state.serial += 1; return prefix + "-" + Date.now().toString(36) + "-" + state.serial; }
  function selected() { return state.items.find(function (item) { return item.id === state.selected; }); }
  function fit() { state.panX = 0; state.panY = 0; state.zoom = 1; $("zoom").value = "100"; transform(); }
  function transform() { $("world").style.transform = "translate(" + state.panX + "px," + state.panY + "px) scale(" + state.zoom + ")"; }
  function newItem(kind) {
    var item = { id: id("item"), kind: kind, title: kind === "note" ? "New idea" : "New " + kind, content: "" };
    state.items.push(item);
    state.positions[item.id] = { x: 110 + ((state.items.length - 1) % 4) * 192, y: 95 + Math.floor((state.items.length - 1) / 4) * 112 };
    state.selected = item.id;
    render();
    $("title").focus();
    status("Working item created. Export the canvas to preserve it.");
  }
  function drawEdges() {
    var svg = $("edges");
    svg.replaceChildren();
    state.connections.forEach(function (edge) {
      var from = state.positions[edge.source], to = state.positions[edge.target];
      if (!from || !to) return;
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
  }
  function renderInspector() {
    var item = selected();
    $("inspector-empty").hidden = !!item;
    $("inspector-fields").hidden = !item;
    if (!item) return;
    $("title").value = item.title; $("kind").value = item.kind; $("content").value = item.content;
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
      remove.addEventListener("click", function () { state.connections = state.connections.filter(function (e) { return e.id !== edge.id; }); render(); });
      row.append(summary, remove); list.appendChild(row);
    });
  }
  function choose(itemId) {
    state.selected = itemId;
    Array.prototype.forEach.call(document.querySelectorAll(".node"), function (node) {
      node.setAttribute("aria-pressed", String(node.dataset.itemId === itemId));
    });
    renderInspector();
  }
  function render() {
    var host = $("nodes"); host.replaceChildren();
    $("empty-state").hidden = state.items.length > 0;
    state.items.forEach(function (item) {
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
        node.style.left = pos.x + "px"; node.style.top = pos.y + "px"; drawEdges();
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
        function finish() { node.removeEventListener("pointermove", move); node.removeEventListener("pointerup", finish); node.removeEventListener("pointercancel", finish); }
        node.addEventListener("pointermove", move); node.addEventListener("pointerup", finish); node.addEventListener("pointercancel", finish);
      });
      host.appendChild(node);
    });
    drawEdges(); renderInspector(); transform();
  }
  function saveCurrent() {
    var item = selected(); if (!item) return;
    item.title = $("title").value.trim() || "Untitled";
    item.kind = $("kind").value; item.content = $("content").value;
    render(); status("Working item updated in this browser session. Export to keep it.");
  }
  function connect() {
    var item = selected(), target = $("target").value; if (!item || !target || target === item.id) return;
    var exists = state.connections.some(function (e) { return e.source === item.id && e.target === target && e.label === $("relation").value.trim(); });
    if (!exists) state.connections.push({ id: id("edge"), source: item.id, target: target, label: $("relation").value.trim() });
    $("relation").value = ""; render(); status("Working association created. It does not alter accepted relationships.");
  }
  function sceneOpen() {
    var item = selected(); if (!item) return;
    saveCurrent(); $("scene-heading").textContent = item.title; $("scene-text").value = item.content;
    $("scene-panel").hidden = false; $("scene-text").focus();
  }
  function sceneSave() {
    var item = selected(); if (!item) return;
    item.content = $("scene-text").value; $("content").value = item.content;
    $("scene-panel").hidden = true; render();
    status("Working prose updated. This prototype does not submit generation or acceptance.");
  }
  function exportCanvas() {
    var data = { schema_version: 1, items: state.items, connections: state.connections, positions: state.positions };
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
          !["note", "character", "scene", "place", "question"].includes(item.kind)) throw new Error("Invalid canvas item");
      seen.add(item.id);
      var pos = data.positions[item.id];
      if (!pos || !Number.isFinite(pos.x) || !Number.isFinite(pos.y) || pos.x < 0 || pos.x > 1400 || pos.y < 0 || pos.y > 1040) throw new Error("Invalid canvas layout");
    });
    var ids = new Set();
    data.connections.forEach(function (edge) {
      if (!edge || typeof edge.id !== "string" || !/^[a-z0-9_-]{1,80}$/.test(edge.id) || ids.has(edge.id) ||
          !seen.has(edge.source) || !seen.has(edge.target) || edge.source === edge.target ||
          typeof edge.label !== "string" || edge.label.length > 120) throw new Error("Invalid connection");
      ids.add(edge.id);
    });
  }
  function importCanvas(event) {
    var file = event.target.files[0]; event.target.value = ""; if (!file) return;
    if (file.size > 1024 * 1024) { status("Import rejected: file exceeds 1 MB."); return; }
    file.text().then(function (raw) {
      var data = JSON.parse(raw); validCanvas(data);
      state.items = data.items; state.connections = data.connections; state.positions = data.positions;
      state.selected = data.items.length ? data.items[0].id : null; state.serial += 1;
      fit(); render(); status("Working canvas imported. Export again after changes.");
    }).catch(function (error) { status("Import rejected: " + error.message); });
  }
  function removeCurrent() {
    var item = selected(); if (!item || !window.confirm("Remove this working item? You can undo during this session.")) return;
    state.undo = { item: item, pos: state.positions[item.id], links: state.connections.filter(function (e) { return e.source === item.id || e.target === item.id; }) };
    state.items = state.items.filter(function (entry) { return entry.id !== item.id; });
    state.connections = state.connections.filter(function (e) { return e.source !== item.id && e.target !== item.id; });
    delete state.positions[item.id]; state.selected = null; render();
    status("Working item removed. Press Ctrl+Z to undo; export to retain your changes.");
  }
  document.addEventListener("keydown", function (event) {
    if (event.ctrlKey && event.key.toLowerCase() === "z" && state.undo && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      event.preventDefault(); var old = state.undo; state.undo = null;
      state.items.push(old.item); state.positions[old.item.id] = old.pos;
      state.connections.push.apply(state.connections, old.links); state.selected = old.item.id; render();
    }
  });
  $("add-note").addEventListener("click", function () { newItem("note"); });
  $("add-character").addEventListener("click", function () { newItem("character"); });
  $("add-scene").addEventListener("click", function () { newItem("scene"); });
  $("start").addEventListener("click", function () { newItem("note"); });
  $("fit").addEventListener("click", fit);
  $("zoom").addEventListener("input", function () { state.zoom = Number(this.value) / 100; transform(); });
  $("save").addEventListener("click", saveCurrent);
  $("connect").addEventListener("click", connect);
  $("write").addEventListener("click", sceneOpen);
  $("close-scene").addEventListener("click", function () { $("scene-panel").hidden = true; });
  $("save-scene").addEventListener("click", sceneSave);
  $("download").addEventListener("click", exportCanvas);
  $("import").addEventListener("change", importCanvas);
  $("remove").addEventListener("click", removeCurrent);
  $("viewport").addEventListener("pointerdown", function (event) {
    if (event.target !== this && event.target !== $("nodes") && event.target !== $("world")) return;
    if (event.button !== 0) return;
    var startX = event.clientX, startY = event.clientY, baseX = state.panX, baseY = state.panY;
    this.setPointerCapture(event.pointerId);
    function move(e) { state.panX = baseX + e.clientX - startX; state.panY = baseY + e.clientY - startY; transform(); }
    function finish() { $("viewport").removeEventListener("pointermove", move); $("viewport").removeEventListener("pointerup", finish); $("viewport").removeEventListener("pointercancel", finish); }
    this.addEventListener("pointermove", move); this.addEventListener("pointerup", finish); this.addEventListener("pointercancel", finish);
  });
  render();
}());
