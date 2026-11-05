import {
  resolveAnchor,
  recordedRelations,
  buildIntentDraft,
  listSelectableAnchors,
  COMPONENT_GROUP_LABELS,
} from './model.mjs';

const SHA = /^[a-f0-9]{64}$/;
const ANCHOR_GROUP_LABELS = {
  emotion: 'Emotional',
  causality: 'Causal',
  structure: 'Structure',
  genre: 'Genre',
  narrative_device: 'Trope / device',
  theme: 'Theme',
  aesthetic: 'Aesthetic',
  context: 'Other',
};
const GROUP_ORDER = ['emotion', 'causality', 'structure', 'genre', 'narrative_device', 'theme', 'aesthetic', 'context'];
const OPERATIONS = [
  ['ask_relation', 'Ask how selected elements might relate'],
  ['trace', 'Trace recorded connections'],
  ['challenge', 'Challenge an assumption or link'],
  ['compare', 'Compare alternatives'],
  ['revise', 'Request a holistic revision'],
];

export function mountGraphExperiment(root, options = {}) {
  const doc = options.document || (typeof document !== 'undefined' ? document : null);
  if (!doc) throw new Error('A document is required to mount the graph experiment.');
  if (!options.candidate || typeof options.candidate !== 'object') {
    throw new Error('A captured ArchitectureCandidate v2 is required.');
  }
  if (!SHA.test(options.requestSha || '')) {
    throw new Error('A valid captured source request SHA is required.');
  }
  if (!['B1', 'B2'].includes(options.variant)) {
    throw new Error('Prototype variant must be B1 or B2.');
  }
  let destroyed = false;
  let focusRegistry = new Map();
  const state = {
    candidate: options.candidate,
    requestSha: options.requestSha,
    activeRequestSha: options.requestSha,
    variant: options.variant,
    fixtureLabel: options.fixtureLabel || 'Recorded candidate',
    selection: [],
    focusedRelation: null,
    draft: null,
    operation: '',
    operationTouched: false,
    authorText: '',
    notice: '',
    error: '',
    copyStatus: '',
    filter: '',
  };
  const onVariantChange = options.onVariantChange || null;
  const copy = options.onCopy || (typeof navigator !== 'undefined' && navigator.clipboard
    ? value => navigator.clipboard.writeText(value)
    : null);

  const register = (key, node) => {
    if (key) focusRegistry.set(key, node);
    return node;
  };
  const stale = () => state.activeRequestSha !== state.requestSha;
  const node = (tag, className, value, id) => {
    const result = doc.createElement(tag);
    if (className) result.className = className;
    if (value !== undefined) result.textContent = value;
    if (id) result.id = id;
    return result;
  };
  const button = (label, onClick, {className = '', id = '', dataset = {}, disabled = false,
    ariaLabel = '', focusKey = ''} = {}) => {
    const result = node('button', className, label, id);
    result.type = 'button';
    result.disabled = disabled;
    if (ariaLabel) result.setAttribute('aria-label', ariaLabel);
    Object.assign(result.dataset, dataset);
    result.addEventListener('click', onClick);
    return register(focusKey, result);
  };
  const option = (value, label, disabled) => {
    const result = node('option', '', label);
    result.value = value;
    result.disabled = !!disabled;
    return result;
  };
  const selectedKey = item => `${item.kind}:${item.id}`;
  const selected = item => state.selection.some(entry => entry.kind === item.kind && entry.id === item.id);
  const resolvedSelection = () => state.selection
    .map(item => resolveAnchor(state.candidate, state.requestSha, item))
    .filter(Boolean);

  function normalizeOperation() {
    const valid = OPERATIONS.some(([value]) => value === state.operation);
    if (!valid || !state.operationTouched) {
      state.operation = state.selection.length === 2 ? 'ask_relation' : 'challenge';
    }
    if (state.selection.length !== 2 && state.operation === 'ask_relation') {
      state.operation = 'challenge';
    }
    if (state.selection.length === 0) state.operation = 'challenge';
  }

  function canPrepare() {
    if (stale() || !state.selection.length) return false;
    if (state.operation === 'ask_relation' && state.selection.length !== 2) return false;
    if (state.operation === 'revise' && !state.authorText.trim()) return false;
    return true;
  }

  function toggleAnchor(kind, id) {
    if (stale()) {
      state.notice = 'Source request changed. Refresh the fixture before selecting anchors.';
      render('source-status');
      return;
    }
    const index = state.selection.findIndex(item => item.kind === kind && item.id === id);
    if (index >= 0) {
      state.selection.splice(index, 1);
    } else {
      if (state.selection.length >= 3) {
        state.notice = 'Select at most three anchors for one intention draft.';
        render(`anchor:${kind}:${id}`);
        return;
      }
      state.selection.push({kind, id});
    }
    state.focusedRelation = null;
    state.draft = null;
    state.error = '';
    state.copyStatus = '';
    state.notice = '';
    normalizeOperation();
    render(`anchor:${kind}:${id}`);
  }

  function inspectRelation(relation) {
    if (stale()) {
      state.notice = 'Source request changed. Refresh the fixture before inspecting relations.';
      render('source-status');
      return;
    }
    state.focusedRelation = relation;
    render('back-to-entity');
  }

  function prepareDraft() {
    if (!canPrepare()) {
      state.error = stale()
        ? 'Source request changed; refresh the fixture before preparing a draft.'
        : 'Select a valid source context and intention before preparing a draft.';
      render('prepare-draft');
      return;
    }
    try {
      state.draft = buildIntentDraft({
        candidate: state.candidate,
        requestSha: state.requestSha,
        currentRequestSha: state.activeRequestSha,
        anchors: state.selection,
        operation: state.operation,
        authorText: state.authorText,
      });
      state.error = '';
      state.copyStatus = '';
      render('draft-output');
    } catch (error) {
      state.draft = null;
      state.error = error.message;
      render('prepare-draft');
    }
  }

  function copyDraft() {
    const output = focusRegistry.get('draft-output');
    const value = output ? output.value : (state.draft ? state.draft.draft_instruction : '');
    if (!value) return;
    if (copy) {
      try {
        const result = copy(value);
        if (result && typeof result.then === 'function') {
          result.then(() => {
            state.copyStatus = 'Draft copied.';
            render('copy-draft');
          }).catch(() => {
            state.copyStatus = 'Copy unavailable; select the draft text and copy manually.';
            render('copy-draft');
          });
        } else {
          state.copyStatus = 'Draft copied.';
          render('copy-draft');
        }
      } catch (_error) {
        state.copyStatus = 'Copy unavailable; select the draft text and copy manually.';
        render('copy-draft');
      }
    } else {
      state.copyStatus = 'Copy unavailable; select the draft text and copy manually.';
      render('copy-draft');
    }
  }

  function renderSourceStatus() {
    const section = node('section', 'prototype-source', undefined, 'source-status');
    section.appendChild(node('p', 'eyebrow', 'SOURCE-BOUND PROTOTYPE'));
    section.appendChild(node('p', '', `Captured request SHA-256: ${state.requestSha}`));
    section.appendChild(node('p', '', `Active request SHA-256: ${state.activeRequestSha}`));
    section.appendChild(node('p', '', 'Authority: working proposal · not story canon or accepted ontology'));
    section.appendChild(node('p', '', `Fixture: ${state.fixtureLabel}`, 'fixture-label'));
    if (state.candidate._fixture && state.candidate._fixture.synthetic) {
      section.appendChild(node('p', 'warning', 'SYNTHETIC STRESS FIXTURE — NOT RECORDED EVIDENCE'));
    }
    if (stale()) {
      section.appendChild(node('p', 'error', 'STALE SOURCE — selections and drafts are invalid until the fixture is refreshed.'));
    }
    section.appendChild(node('p', '', state.variant === 'B1'
      ? 'Variant: B1 — Question-First Semantic Inspector'
      : 'Variant: B2 — Component-Aware Intent Workbench', 'variant-label'));
    const switcher = node('div', 'variant-switch');
    switcher.appendChild(button('B1 — Question-first', () => {
      state.variant = 'B1';
      state.focusedRelation = null;
      render();
      if (onVariantChange) onVariantChange(state.variant);
    }, {id: 'variant-b1', className: state.variant === 'B1' ? 'active' : '', focusKey: 'variant-b1'}));
    switcher.appendChild(button('B2 — Component workbench', () => {
      state.variant = 'B2';
      state.focusedRelation = null;
      render();
      if (onVariantChange) onVariantChange(state.variant);
    }, {id: 'variant-b2', className: state.variant === 'B2' ? 'active' : '', focusKey: 'variant-b2'}));
    section.appendChild(switcher);
    section.appendChild(button(stale() ? 'Source is stale' : 'Simulate stale source', () => {
      state.activeRequestSha = stale() ? state.requestSha : 'f'.repeat(64);
      state.draft = null;
      state.error = '';
      state.copyStatus = '';
      state.notice = stale()
        ? 'Source request changed. Selections and drafts are now stale.'
        : 'Source request restored. Re-select or prepare a new draft.';
      render('simulate-stale');
    }, {id: 'simulate-stale', className: 'secondary', focusKey: 'simulate-stale'}));
    if (state.notice) section.appendChild(node('p', 'notice', state.notice));
    return section;
  }

  function renderAnchorIndex() {
    const aside = node('aside', 'anchor-panel', undefined, 'anchor-index');
    aside.appendChild(node('h2', '', 'Entities and relationships'));
    aside.appendChild(node('p', 'muted', 'Select 1–3 anchors. This index mirrors the source candidate; it is not a new graph.'));
    const filter = node('input', 'anchor-filter', undefined, 'anchor-filter');
    filter.type = 'search';
    filter.value = state.filter;
    filter.placeholder = 'Filter by title, kind or ID';
    filter.setAttribute('aria-label', 'Filter source anchors');
    filter.addEventListener('input', () => {
      state.filter = filter.value;
      render('anchor-filter');
    });
    aside.appendChild(filter);
    const anchors = listSelectableAnchors(state.candidate, state.requestSha);
    const needle = state.filter.trim().toLowerCase();
    const visible = anchors.filter(item => !needle
      || `${item.title} ${item.kind} ${item.id}`.toLowerCase().includes(needle));
    aside.appendChild(node('p', 'muted', `${anchors.length} anchors in this fixture; ${visible.length} shown.`, 'anchor-count'));
    for (const group of GROUP_ORDER) {
      const members = visible.filter(item => item.group === group);
      if (!members.length) continue;
      const section = node('section', 'anchor-group');
      section.appendChild(node('h3', '', ANCHOR_GROUP_LABELS[group] || group));
      for (const item of members) {
        const isSelected = selected(item);
        const row = button(
          `${item.title} · ${item.kind}/${item.id} · ${item.sourceRef} · working proposal`,
          () => toggleAnchor(item.kind, item.id),
          {
            className: `anchor-button${isSelected ? ' selected' : ''}`,
            dataset: {
              anchorKind: item.kind,
              anchorId: item.id,
              sourceRef: item.sourceRef,
            },
            disabled: stale(),
            ariaLabel: `${item.title}, ${item.kind} ${item.id}, source ${item.sourceRef}`,
            focusKey: `anchor:${item.kind}:${item.id}`,
          },
        );
        row.setAttribute('aria-pressed', String(isSelected));
        section.appendChild(row);
      }
      aside.appendChild(section);
    }
    if (!visible.length) aside.appendChild(node('p', 'muted', 'No anchor matches the filter.'));
    return aside;
  }

  function renderSelectionTrail() {
    const section = node('section', 'selection-trail', undefined, 'selection-trail');
    section.appendChild(node('h2', '', `Selected anchors (${state.selection.length}/3)`));
    if (!state.selection.length) {
      section.appendChild(node('p', 'muted', 'Select an entity or relationship from the index.'));
      return section;
    }
    const list = node('ul', 'selection-list');
    for (const item of state.selection) {
      const anchor = resolveAnchor(state.candidate, state.requestSha, item);
      const entry = node('li', stale() ? 'selection-entry stale' : 'selection-entry');
      entry.appendChild(node('span', '', anchor
        ? `${anchor.title} · ${anchor.kind}/${anchor.id} · ${anchor.sourceRef}`
        : `${item.kind}/${item.id} · unavailable in source`));
      entry.appendChild(button('Remove', () => {
        state.selection = state.selection.filter(entryItem => entryItem !== item);
        state.focusedRelation = null;
        state.draft = null;
        state.error = '';
        normalizeOperation();
        render();
      }, {
        className: 'link-button',
        ariaLabel: `Remove ${item.kind} ${item.id} from selection`,
        focusKey: `remove:${item.kind}:${item.id}`,
      }));
      list.appendChild(entry);
    }
    section.appendChild(list);
    return section;
  }

  function renderComponents(anchor) {
    const list = node('ul', 'component-list');
    for (const component of anchor.components) {
      const item = node('li', 'component-row');
      item.appendChild(node('strong', '', `${component.label}: `));
      item.appendChild(node('span', '', component.value));
      item.appendChild(node('small', 'source-note', ` ${component.field} · ${component.sourceRef}`));
      list.appendChild(item);
    }
    return list;
  }

  function renderFocusPanel() {
    const section = node('section', 'focus-panel', undefined, 'focus-panel');
    section.appendChild(node('h2', '', 'Inspect the selected meaning'));
    if (!state.selection.length) {
      section.appendChild(node('p', 'muted',
        'Select an entity or relationship to read its role, source reference and recorded components.'));
      return section;
    }
    const anchors = resolvedSelection();
    if (!anchors.length) {
      section.appendChild(node('p', 'error', 'The selected anchors are unavailable in the captured source.'));
      return section;
    }
    if (state.variant === 'B2') {
      section.appendChild(node('p', 'muted',
        'Component-aware workbench: the selected anchors are compared by emotional, causal, structural, genre and thematic components.'));
    }
    const primary = anchors[anchors.length - 1];
    const card = node('article', 'focus-card', undefined, 'focus-card');
    card.appendChild(node('h3', '', primary.title, 'focus-title'));
    card.appendChild(node('p', 'source-note', `Source: ${primary.sourceRef} · ${primary.authority}`, 'focus-source'));
    card.appendChild(node('p', 'focus-meaning', primary.meaning, 'focus-meaning'));
    if (state.variant === 'B2') {
      const grid = node('div', 'component-grid', undefined, 'component-grid');
      for (const anchor of anchors) {
        const anchorCard = node('article', 'component-card');
        anchorCard.appendChild(node('h4', '', `${anchor.title} · ${anchor.kind}/${anchor.id}`));
        anchorCard.appendChild(node('p', 'source-note', `${anchor.sourceRef} · ${anchor.authority}`));
        const groups = new Map();
        for (const component of anchor.components) {
          if (!groups.has(component.group)) groups.set(component.group, []);
          groups.get(component.group).push(component);
        }
        for (const group of GROUP_ORDER) {
          const components = groups.get(group);
          if (!components) continue;
          anchorCard.appendChild(node('h5', '', COMPONENT_GROUP_LABELS[group] || group));
          const list = node('ul', 'component-list');
          for (const component of components) {
            const item = node('li', 'component-row');
            item.appendChild(node('strong', '', `${component.label}: `));
            item.appendChild(node('span', '', component.value));
            item.appendChild(node('small', 'source-note', ` ${component.field} · ${component.sourceRef}`));
            list.appendChild(item);
          }
          anchorCard.appendChild(list);
        }
        grid.appendChild(anchorCard);
      }
      card.appendChild(grid);
      card.appendChild(node('p', 'muted', `${anchors.length} anchor(s) in context; ${anchors.reduce((total, anchor) => total + anchor.components.length, 0)} recorded components.`, 'context-count'));
    } else {
      card.appendChild(node('h4', '', 'Recorded components'));
      card.appendChild(renderComponents(primary));
      if (anchors.length > 1) {
        const context = node('p', 'muted');
        context.textContent = `Question context: ${anchors.slice(0, -1).map(anchor => anchor.title).join('; ')}.`;
        card.appendChild(context);
      }
    }
    section.appendChild(card);
    return section;
  }

  function relationButton(relation) {
    return button(
      `${relation.label} · ${relation.from.title} → ${relation.to.title} · ${relation.sourceRef}`,
      () => inspectRelation(relation),
      {
        className: 'relation-button',
        dataset: {
          relationKind: relation.kind,
          relationId: relation.id,
          sourceRef: relation.sourceRef,
        },
        focusKey: `relation:${relation.kind}:${relation.id}:${relation.sourceRef}`,
      },
    );
  }

  function renderRelationshipPanel() {
    const section = node('section', 'relationship-panel', undefined, 'relationship-panel');
    section.appendChild(node('h2', '', 'Recorded relationships'));
    if (state.focusedRelation) {
      const relation = state.focusedRelation;
      const card = node('article', 'relation-detail', undefined, 'relation-detail');
      card.appendChild(node('h3', '', relation.label));
      card.appendChild(node('p', 'source-note', `${relation.kind}/${relation.id} · ${relation.sourceRef} · ${relation.authority}`));
      card.appendChild(node('p', '', `${relation.from.title} → ${relation.to.title}`));
      if (relation.direction) {
        card.appendChild(node('p', 'muted', `Direction relative to the first selected anchor: ${relation.direction}.`));
      }
      card.appendChild(node('p', 'relation-meaning', relation.detail));
      card.appendChild(node('p', 'muted', 'Recorded relation inspection only; this view does not create or accept an edge.'));
      card.appendChild(button('Back to entity', () => {
        state.focusedRelation = null;
        render();
      }, {id: 'back-to-entity', className: 'secondary', focusKey: 'back-to-entity'}));
      section.appendChild(card);
      return section;
    }
    if (!state.selection.length) {
      section.appendChild(node('p', 'muted', 'Select an anchor to inspect its recorded relationships.'));
      return section;
    }
    const relations = recordedRelations(state.candidate, state.selection);
    if (!relations.length) {
      section.appendChild(node('p', 'unknown', 'No recorded relation between the selected anchors. Absence means not recorded, not impossible.', 'relation-empty'));
      return section;
    }
    const list = node('ul', 'relation-list', undefined, 'relationship-list');
    for (const relation of relations) {
      const item = node('li', '');
      item.appendChild(relationButton(relation));
      list.appendChild(item);
    }
    section.appendChild(list);
    return section;
  }

  function renderIntentPanel() {
    const section = node('section', 'intent-panel', undefined, 'intent-panel');
    section.appendChild(node('h2', '', 'Prepare an editable agent instruction'));
    section.appendChild(node('p', 'muted',
      'This prepares text for the active coding agent. It does not send a request, execute a model, save a relationship or accept story meaning.'));
    if (stale()) {
      section.appendChild(node('p', 'error',
        'Source changed: selections and drafts are stale. Refresh the fixture before preparing a new draft.'));
    }
    const label = node('label', '', 'Intent operation');
    label.setAttribute('for', 'operation-select');
    section.appendChild(label);
    const select = node('select', '', undefined, 'operation-select');
    select.setAttribute('aria-label', 'Graph intent operation');
    for (const [value, text] of OPERATIONS) {
      select.appendChild(option(value, text, value === 'ask_relation' && state.selection.length !== 2));
    }
    select.value = state.operation;
    select.disabled = stale();
    select.addEventListener('change', () => {
      state.operation = select.value;
      state.operationTouched = true;
      state.draft = null;
      state.error = '';
      render('operation-select');
    });
    section.appendChild(select);
    const textLabel = node('label', '', 'Your creative intention');
    textLabel.setAttribute('for', 'author-intention');
    section.appendChild(textLabel);
    const textarea = node('textarea', '', undefined, 'author-intention');
    textarea.rows = 4;
    textarea.maxLength = 4000;
    textarea.value = state.authorText;
    textarea.placeholder = 'Example: Make wonder dominate fear while preserving mystery and the memory cost.';
    textarea.setAttribute('aria-label', 'Your creative intention for the coding agent');
    textarea.disabled = stale();
    textarea.addEventListener('input', () => {
      state.authorText = textarea.value;
      state.draft = null;
      state.error = '';
    });
    section.appendChild(textarea);
    section.appendChild(button('Prepare editable draft', prepareDraft, {
      id: 'prepare-draft',
      disabled: !canPrepare(),
      focusKey: 'prepare-draft',
    }));
    const status = node('p', 'draft-status', state.draft
      ? 'prepared_not_executed · noncanonical_intent_draft · not sent to the coding agent'
      : stale() ? 'Source changed: draft unavailable until the fixture is refreshed.'
      : (state.error ? `Draft not prepared: ${state.error}` : 'No draft prepared.'), 'draft-status');
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    section.appendChild(status);
    if (state.copyStatus) section.appendChild(node('p', 'muted', state.copyStatus, 'copy-status'));
    if (state.draft) {
      const warnings = node('ul', 'draft-warnings', undefined, 'draft-warnings');
      for (const warning of state.draft.warnings) warnings.appendChild(node('li', '', warning));
      section.appendChild(warnings);
      const output = node('textarea', 'draft-output', undefined, 'draft-output');
      output.rows = 16;
      output.value = state.draft.draft_instruction;
      output.setAttribute('aria-label', 'Editable coding-agent instruction draft');
      section.appendChild(output);
      section.appendChild(button('Copy draft', copyDraft, {
        id: 'copy-draft', className: 'secondary', focusKey: 'copy-draft',
      }));
    }
    return section;
  }

  function render(focusKey) {
    if (destroyed) return;
    focusRegistry = new Map();
    root.replaceChildren();
    root.appendChild(renderSourceStatus());
    const layout = node('div', 'prototype-layout');
    layout.appendChild(renderAnchorIndex());
    const workspace = node('div', 'prototype-workspace');
    workspace.appendChild(renderSelectionTrail());
    workspace.appendChild(renderFocusPanel());
    workspace.appendChild(renderRelationshipPanel());
    workspace.appendChild(renderIntentPanel());
    layout.appendChild(workspace);
    root.appendChild(layout);
    root.appendChild(node('p', 'prototype-boundary',
      'Prototype boundary: no model request, no CanvasStore write, no accepted story or ontology change.'));
    if (focusKey) {
      const target = focusRegistry.get(focusKey);
      if (target && typeof target.focus === 'function') target.focus();
    }
  }

  render();
  return {
    destroy() {
      destroyed = true;
      root.replaceChildren();
    },
  };
}
