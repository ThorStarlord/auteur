/* Pure source-bound projection over an existing ArchitectureCandidate v2.
   No writable state, no provider, no inferred relationships. */

export const COMPONENT_GROUP_LABELS = {
  emotion: 'Emotional',
  causality: 'Causal',
  structure: 'Structural',
  genre: 'Genre',
  theme: 'Thematic',
  narrative_device: 'Trope / device',
  aesthetic: 'Aesthetic',
  authority: 'Provenance / authority',
  context: 'Context',
};

const SOURCE_SHA = /^[a-f0-9]{64}$/;
const ANCHOR_KINDS = new Set([
  'node', 'link', 'genre_interaction', 'emotion_target', 'genre_contract', 'phase',
]);
const COLLECTION = {
  node: 'nodes',
  link: 'links',
  genre_interaction: 'genre_interactions',
  emotion_target: 'emotion_targets',
  genre_contract: 'genre_contracts',
  phase: 'phases',
};
const KEY = {
  node: 'id',
  link: 'id',
  genre_interaction: 'id',
  emotion_target: 'id',
  genre_contract: 'genre_node_id',
  phase: 'id',
};
const CATEGORY_GROUP = {
  reader_experience: 'emotion',
  aesthetic: 'aesthetic',
  genre: 'genre',
  trope: 'narrative_device',
  engine: 'causality',
  thread: 'causality',
  structure: 'structure',
  theme: 'theme',
  other: 'context',
};

const asArray = value => Array.isArray(value) ? value : [];
const text = value => typeof value === 'string' ? value : '';
const clip = (value, max = 400) => {
  const source = text(value);
  return source.length > max ? `${source.slice(0, max - 1).trimEnd()}…` : source;
};

function findRecord(candidate, kind, id) {
  if (!candidate || typeof candidate !== 'object') return null;
  if (!ANCHOR_KINDS.has(kind) || typeof id !== 'string' || !id) return null;
  const collection = COLLECTION[kind];
  const key = KEY[kind];
  const list = asArray(candidate[collection]);
  const index = list.findIndex(entry => entry && entry[key] === id);
  if (index < 0) return null;
  return {record: list[index], index, collection};
}

function nodeTitle(candidate, id) {
  const found = findRecord(candidate, 'node', id);
  return found ? (text(found.record.title) || id) : id;
}

function nodeRef(candidate, id) {
  const found = findRecord(candidate, 'node', id);
  return {
    kind: 'node',
    id,
    title: found ? (text(found.record.title) || id) : id,
    sourceRef: found ? `nodes/${found.index}` : null,
  };
}

function recordRef(candidate, kind, id, title) {
  const found = findRecord(candidate, kind, id);
  return {
    kind,
    id,
    title: title || id,
    sourceRef: found ? `${found.collection}/${found.index}` : null,
  };
}

function emotionRef(candidate, id) {
  const found = findRecord(candidate, 'emotion_target', id);
  return recordRef(candidate, 'emotion_target', id,
    found ? `${found.record.emotion} · ${found.record.role}` : id);
}

function complexEmotionRef(candidate, id) {
  const found = findRecord(candidate, 'complex_emotion', id);
  return recordRef(candidate, 'complex_emotion', id,
    found ? (text(found.record.title) || id) : id);
}

function genreContractRef(candidate, genreNodeId) {
  const found = findRecord(candidate, 'genre_contract', genreNodeId);
  return recordRef(candidate, 'genre_contract', genreNodeId,
    found ? `${nodeTitle(candidate, genreNodeId)} contract` : genreNodeId);
}

function phaseRef(candidate, id) {
  const found = findRecord(candidate, 'phase', id);
  return recordRef(candidate, 'phase', id, found ? (text(found.record.title) || id) : id);
}

function linkRef(candidate, id) {
  const found = findRecord(candidate, 'link', id);
  return recordRef(candidate, 'link', id, id);
}

function component(group, field, label, value, sourceRef) {
  return {
    group,
    field,
    label,
    value: clip(value, 700),
    sourceRef,
  };
}

function componentsFor(candidate, kind, record, sourceRef) {
  const components = [];
  if (kind === 'node') {
    const category = text(record.category) || 'other';
    components.push(component(CATEGORY_GROUP[category] || 'context', 'category', 'Category', category, sourceRef));
    components.push(component('context', 'scope', 'Scope', text(record.scope) || 'whole_story', sourceRef));
    if (record.parent_id) components.push(component('structure', 'parent_id', 'Parent', record.parent_id, sourceRef));
  } else if (kind === 'link') {
    components.push(component('causality', 'source', 'Source node', nodeTitle(candidate, record.source), sourceRef));
    components.push(component('causality', 'target', 'Target node', nodeTitle(candidate, record.target), sourceRef));
    components.push(component('causality', 'function', 'Recorded function', record.function, sourceRef));
  } else if (kind === 'genre_interaction') {
    components.push(component('genre', 'kind', 'Interaction kind', record.kind, sourceRef));
    components.push(component('genre', 'source_genre_id', 'Source genre', nodeTitle(candidate, record.source_genre_id), sourceRef));
    components.push(component('genre', 'target_genre_id', 'Target genre', nodeTitle(candidate, record.target_genre_id), sourceRef));
    components.push(component('causality', 'mechanism', 'Mechanism', record.mechanism, sourceRef));
    if (record.risk) components.push(component('causality', 'risk', 'Risk', record.risk, sourceRef));
  } else if (kind === 'emotion_target') {
    components.push(component('emotion', 'emotion', 'Basic emotion', record.emotion, sourceRef));
    components.push(component('emotion', 'role', 'Role', record.role, sourceRef));
    components.push(component('emotion', 'intended_effect', 'Intended effect', record.intended_effect, sourceRef));
    components.push(component('emotion', 'eliciting_condition', 'Eliciting condition', record.eliciting_condition, sourceRef));
    components.push(component('aesthetic', 'aesthetic_strategy', 'Aesthetic strategy', record.aesthetic_strategy, sourceRef));
    components.push(component('authority', 'provenance', 'Provenance', record.provenance, sourceRef));
  } else if (kind === 'genre_contract') {
    components.push(component('genre', 'role', 'Genre role', record.role, sourceRef));
    components.push(component('causality', 'narrative_engine', 'Narrative engine', record.narrative_engine, sourceRef));
    components.push(component('structure', 'structural_pattern', 'Structural pattern', record.structural_pattern, sourceRef));
    components.push(component('narrative_device', 'trope_functions', 'Trope functions', asArray(record.trope_functions).join('; '), sourceRef));
    components.push(component('structure', 'payoff_expectations', 'Payoff expectations', asArray(record.payoff_expectations).join('; '), sourceRef));
    components.push(component('emotion', 'emotion_target_ids', 'Emotion targets', asArray(record.emotion_target_ids).join('; '), sourceRef));
    if (asArray(record.complex_emotion_ids).length) {
      components.push(component('emotion', 'complex_emotion_ids', 'Complex emotions', asArray(record.complex_emotion_ids).join('; '), sourceRef));
    }
  } else if (kind === 'phase') {
    components.push(component('structure', 'order', 'Abstract order', String(record.order), sourceRef));
    components.push(component('context', 'scope', 'Scope', text(record.scope) || 'whole_story', sourceRef));
    components.push(component('emotion', 'reader_experience', 'Reader experience', record.reader_experience, sourceRef));
    components.push(component('aesthetic', 'aesthetic', 'Aesthetic', record.aesthetic, sourceRef));
    components.push(component('structure', 'transition', 'Transition', record.transition, sourceRef));
    components.push(component('structure', 'parallel_with', 'Parallel phases', asArray(record.parallel_with).join('; '), sourceRef));
    components.push(component('genre', 'genre_activations', 'Activated genre contracts', asArray(record.genre_activations).map(item => item.genre_node_id).join('; '), sourceRef));
  }
  return components.filter(item => item.value !== '');
}

function relation(kind, id, sourceRef, from, to, label, detail, extra = {}) {
  return {
    kind,
    id,
    sourceRef,
    from,
    to,
    label,
    detail: clip(detail, 500),
    authority: 'working_proposal',
    ...extra,
  };
}

function linkRelation(candidate, record, index, direction) {
  return relation(
    'link', record.id, `links/${index}`,
    nodeRef(candidate, record.source),
    nodeRef(candidate, record.target),
    'recorded directed link', record.function,
    direction ? {direction} : {},
  );
}

function interactionRelation(candidate, record, index, direction) {
  const detail = record.risk
    ? `${record.mechanism} Risk: ${record.risk}`
    : record.mechanism;
  return relation(
    'genre_interaction', record.id, `genre_interactions/${index}`,
    nodeRef(candidate, record.source_genre_id),
    nodeRef(candidate, record.target_genre_id),
    `genre interaction: ${record.kind}`, detail,
    direction ? {direction} : {},
  );
}

function contractReference(candidate, genreNodeId, index) {
  const contract = candidate.genre_contracts[index];
  return relation(
    'genre_contract', genreNodeId, `genre_contracts/${index}`,
    nodeRef(candidate, genreNodeId),
    genreContractRef(candidate, genreNodeId),
    'has recorded genre contract', contract.narrative_engine,
  );
}

function emotionTargetReference(candidate, contract, index, targetId) {
  const target = findRecord(candidate, 'emotion_target', targetId);
  return relation(
    'emotion_target_reference', contract.genre_node_id, `genre_contracts/${index}`,
    genreContractRef(candidate, contract.genre_node_id),
    emotionRef(candidate, targetId),
    'references emotion target',
    target ? target.record.intended_effect : 'Referenced emotion target is unavailable.',
  );
}

function complexEmotionReference(candidate, contract, index, targetId) {
  return relation(
    'complex_emotion_reference', contract.genre_node_id, `genre_contracts/${index}`,
    genreContractRef(candidate, contract.genre_node_id),
    complexEmotionRef(candidate, targetId),
    'references complex emotion',
    'Recorded complex-emotion reference.',
  );
}

function phaseActivation(candidate, phase, index, genreNodeId) {
  const activation = asArray(phase.genre_activations)
    .find(item => item && item.genre_node_id === genreNodeId);
  return relation(
    'phase_activation', phase.id, `phases/${index}`,
    phaseRef(candidate, phase.id),
    genreContractRef(candidate, genreNodeId),
    'genre activation in phase',
    activation ? activation.structural_function : 'Recorded genre activation.',
  );
}

function phaseParallel(candidate, phase, index, otherPhaseId) {
  return relation(
    'phase_parallel', phase.id, `phases/${index}`,
    phaseRef(candidate, phase.id),
    phaseRef(candidate, otherPhaseId),
    'parallel phase',
    'Recorded parallel_with reference.',
  );
}

function nodeHierarchy(candidate, parentId, child, index) {
  return relation(
    'node_hierarchy', child.id, `nodes/${index}`,
    nodeRef(candidate, parentId),
    nodeRef(candidate, child.id),
    'node hierarchy',
    'Recorded parent_id containment.',
  );
}

function dedupe(relations) {
  const seen = new Set();
  return relations.filter(item => {
    const key = [item.kind, item.id, item.sourceRef, item.from.kind, item.from.id,
      item.to.kind, item.to.id, item.direction || ''].join('|');
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function relationsForOne(candidate, anchor) {
  const relations = [];
  const found = findRecord(candidate, anchor.kind, anchor.id);
  if (!found) return relations;
  const record = found.record;
  if (anchor.kind === 'node') {
    asArray(candidate.links).forEach((link, index) => {
      if (!link || (link.source !== anchor.id && link.target !== anchor.id)) return;
      relations.push(linkRelation(candidate, link, index,
        link.source === anchor.id ? 'outgoing' : 'incoming'));
    });
    if (record.parent_id) {
      const parentIndex = asArray(candidate.nodes).findIndex(node => node.id === record.parent_id);
      if (parentIndex >= 0) {
        const parent = candidate.nodes[parentIndex];
        relations.push(nodeHierarchy(candidate, parent.id, record, found.index));
      }
    }
    asArray(candidate.nodes).forEach((child, index) => {
      if (child && child.parent_id === anchor.id) relations.push(nodeHierarchy(candidate, anchor.id, child, index));
    });
    if (record.category === 'genre') {
      const contractIndex = asArray(candidate.genre_contracts)
        .findIndex(contract => contract.genre_node_id === anchor.id);
      if (contractIndex >= 0) relations.push(contractReference(candidate, anchor.id, contractIndex));
      asArray(candidate.genre_interactions).forEach((interaction, index) => {
        if (!interaction) return;
        if (interaction.source_genre_id === anchor.id) relations.push(interactionRelation(candidate, interaction, index, 'outgoing'));
        if (interaction.target_genre_id === anchor.id) relations.push(interactionRelation(candidate, interaction, index, 'incoming'));
      });
      if (contractIndex >= 0) {
        const contract = candidate.genre_contracts[contractIndex];
        asArray(contract.emotion_target_ids).forEach(targetId => {
          relations.push(emotionTargetReference(candidate, contract, contractIndex, targetId));
        });
        asArray(contract.complex_emotion_ids).forEach(targetId => {
          relations.push(complexEmotionReference(candidate, contract, contractIndex, targetId));
        });
        asArray(candidate.phases).forEach((phase, index) => {
          if (asArray(phase.genre_activations).some(item => item.genre_node_id === anchor.id)) {
            relations.push(phaseActivation(candidate, phase, index, anchor.id));
          }
        });
      }
    }
  } else if (anchor.kind === 'link') {
    relations.push(linkRelation(candidate, record, found.index));
  } else if (anchor.kind === 'genre_interaction') {
    relations.push(interactionRelation(candidate, record, found.index));
  } else if (anchor.kind === 'genre_contract') {
    asArray(record.emotion_target_ids).forEach(targetId => {
      relations.push(emotionTargetReference(candidate, record, found.index, targetId));
    });
    asArray(record.complex_emotion_ids).forEach(targetId => {
      relations.push(complexEmotionReference(candidate, record, found.index, targetId));
    });
    asArray(candidate.genre_interactions).forEach((interaction, index) => {
      if (!interaction) return;
      if (interaction.source_genre_id === anchor.id) relations.push(interactionRelation(candidate, interaction, index, 'outgoing'));
      if (interaction.target_genre_id === anchor.id) relations.push(interactionRelation(candidate, interaction, index, 'incoming'));
    });
    asArray(candidate.phases).forEach((phase, index) => {
      if (asArray(phase.genre_activations).some(item => item.genre_node_id === anchor.id)) {
        relations.push(phaseActivation(candidate, phase, index, anchor.id));
      }
    });
  } else if (anchor.kind === 'emotion_target') {
    asArray(candidate.genre_contracts).forEach((contract, index) => {
      if (asArray(contract.emotion_target_ids).includes(anchor.id)) {
        relations.push(emotionTargetReference(candidate, contract, index, anchor.id));
      }
    });
  } else if (anchor.kind === 'phase') {
    asArray(record.genre_activations).forEach(activation => {
      if (activation && activation.genre_node_id) {
        relations.push(phaseActivation(candidate, record, found.index, activation.genre_node_id));
      }
    });
    asArray(record.parallel_with).forEach(otherId => {
      relations.push(phaseParallel(candidate, record, found.index, otherId));
    });
  }
  return dedupe(relations);
}

function isGenreNode(candidate, id) {
  const found = findRecord(candidate, 'node', id);
  return !!found && found.record.category === 'genre';
}

function relationsBetween(candidate, first, second) {
  const relations = [];
  if (first.kind === 'node' && second.kind === 'node') {
    asArray(candidate.links).forEach((link, index) => {
      if (!link) return;
      if ((link.source === first.id && link.target === second.id) ||
          (link.source === second.id && link.target === first.id)) {
        relations.push(linkRelation(candidate, link, index,
          link.source === first.id ? 'outgoing' : 'incoming'));
      }
    });
    if (isGenreNode(candidate, first.id) && isGenreNode(candidate, second.id)) {
      asArray(candidate.genre_interactions).forEach((interaction, index) => {
        if (!interaction) return;
        if ((interaction.source_genre_id === first.id && interaction.target_genre_id === second.id) ||
            (interaction.source_genre_id === second.id && interaction.target_genre_id === first.id)) {
          relations.push(interactionRelation(candidate, interaction, index,
            interaction.source_genre_id === first.id ? 'outgoing' : 'incoming'));
        }
      });
    }
    const firstNode = findRecord(candidate, 'node', first.id).record;
    const secondNode = findRecord(candidate, 'node', second.id).record;
    if (firstNode.parent_id === second.id) {
      relations.push(nodeHierarchy(candidate, second.id, firstNode,
        findRecord(candidate, 'node', first.id).index));
    } else if (secondNode.parent_id === first.id) {
      relations.push(nodeHierarchy(candidate, first.id, secondNode,
        findRecord(candidate, 'node', second.id).index));
    }
  } else if (first.kind === 'link' && second.kind === 'node') {
    const link = findRecord(candidate, 'link', first.id);
    if (link && (link.record.source === second.id || link.record.target === second.id)) {
      relations.push(linkRelation(candidate, link.record, link.index));
    }
  } else if (second.kind === 'link' && first.kind === 'node') {
    const link = findRecord(candidate, 'link', second.id);
    if (link && (link.record.source === first.id || link.record.target === first.id)) {
      relations.push(linkRelation(candidate, link.record, link.index));
    }
  } else if (first.kind === 'genre_contract' && second.kind === 'emotion_target') {
    const contract = findRecord(candidate, 'genre_contract', first.id);
    if (contract && asArray(contract.record.emotion_target_ids).includes(second.id)) {
      relations.push(emotionTargetReference(candidate, contract.record, contract.index, second.id));
    }
  } else if (second.kind === 'genre_contract' && first.kind === 'emotion_target') {
    const contract = findRecord(candidate, 'genre_contract', second.id);
    if (contract && asArray(contract.record.emotion_target_ids).includes(first.id)) {
      relations.push(emotionTargetReference(candidate, contract.record, contract.index, first.id));
    }
  } else if (first.kind === 'genre_contract' && second.kind === 'complex_emotion') {
    const contract = findRecord(candidate, 'genre_contract', first.id);
    if (contract && asArray(contract.record.complex_emotion_ids).includes(second.id)) {
      relations.push(complexEmotionReference(candidate, contract.record, contract.index, second.id));
    }
  } else if (second.kind === 'genre_contract' && first.kind === 'complex_emotion') {
    const contract = findRecord(candidate, 'genre_contract', second.id);
    if (contract && asArray(contract.record.complex_emotion_ids).includes(first.id)) {
      relations.push(complexEmotionReference(candidate, contract.record, contract.index, first.id));
    }
  } else if (first.kind === 'phase' && second.kind === 'genre_contract') {
    const phase = findRecord(candidate, 'phase', first.id);
    if (phase && asArray(phase.record.genre_activations)
      .some(item => item && item.genre_node_id === second.id)) {
      relations.push(phaseActivation(candidate, phase.record, phase.index, second.id));
    }
  } else if (second.kind === 'phase' && first.kind === 'genre_contract') {
    const phase = findRecord(candidate, 'phase', second.id);
    if (phase && asArray(phase.record.genre_activations)
      .some(item => item && item.genre_node_id === first.id)) {
      relations.push(phaseActivation(candidate, phase.record, phase.index, first.id));
    }
  } else if (first.kind === 'phase' && second.kind === 'phase') {
    const phase = findRecord(candidate, 'phase', first.id);
    if (phase && asArray(phase.record.parallel_with).includes(second.id)) {
      relations.push(phaseParallel(candidate, phase.record, phase.index, second.id));
    }
    const reverse = findRecord(candidate, 'phase', second.id);
    if (reverse && asArray(reverse.record.parallel_with).includes(first.id)) {
      relations.push(phaseParallel(candidate, reverse.record, reverse.index, first.id));
    }
  } else if (first.kind === 'genre_interaction' && second.kind === 'node') {
    const interaction = findRecord(candidate, 'genre_interaction', first.id);
    if (interaction && (interaction.record.source_genre_id === second.id ||
        interaction.record.target_genre_id === second.id)) {
      relations.push(interactionRelation(candidate, interaction.record, interaction.index,
        interaction.record.source_genre_id === second.id ? 'incoming' : 'outgoing'));
    }
  } else if (second.kind === 'genre_interaction' && first.kind === 'node') {
    const interaction = findRecord(candidate, 'genre_interaction', second.id);
    if (interaction && (interaction.record.source_genre_id === first.id ||
        interaction.record.target_genre_id === first.id)) {
      relations.push(interactionRelation(candidate, interaction.record, interaction.index,
        interaction.record.source_genre_id === first.id ? 'outgoing' : 'incoming'));
    }
  }
  return dedupe(relations);
}

function resolveCore(candidate, requestSha, anchor) {
  if (!candidate || typeof candidate !== 'object' || !SOURCE_SHA.test(requestSha || '')) return null;
  if (!anchor || typeof anchor !== 'object' || !ANCHOR_KINDS.has(anchor.kind)) return null;
  const found = findRecord(candidate, anchor.kind, anchor.id);
  if (!found) return null;
  const record = found.record;
  const sourceRef = `${found.collection}/${found.index}`;
  let title = anchor.id;
  let meaning = '';
  if (anchor.kind === 'node') {
    title = text(record.title) || anchor.id;
    meaning = text(record.summary);
  } else if (anchor.kind === 'link') {
    title = `${nodeTitle(candidate, record.source)} → ${nodeTitle(candidate, record.target)}`;
    meaning = text(record.function);
  } else if (anchor.kind === 'genre_interaction') {
    title = `${nodeTitle(candidate, record.source_genre_id)} ${record.kind} ${nodeTitle(candidate, record.target_genre_id)}`;
    meaning = text(record.mechanism);
  } else if (anchor.kind === 'emotion_target') {
    title = `${record.emotion} · ${record.role}`;
    meaning = text(record.intended_effect);
  } else if (anchor.kind === 'genre_contract') {
    title = `${nodeTitle(candidate, anchor.id)} contract`;
    meaning = text(record.narrative_engine);
  } else if (anchor.kind === 'phase') {
    title = text(record.title) || anchor.id;
    meaning = text(record.narrative_function);
  }
  return {
    kind: anchor.kind,
    id: anchor.id,
    sourceRef,
    title,
    meaning: clip(meaning, 800),
    authority: 'working_proposal',
    request_sha256: requestSha,
    components: componentsFor(candidate, anchor.kind, record, sourceRef),
    relationships: [],
  };
}

export function resolveAnchor(candidate, requestSha, anchor) {
  const resolved = resolveCore(candidate, requestSha, anchor);
  if (!resolved) return null;
  resolved.relationships = relationsForOne(candidate, resolved);
  return resolved;
}

export function recordedRelations(candidate, anchors) {
  if (!Array.isArray(anchors) || anchors.length === 0) return [];
  const resolved = anchors.map(item => resolveCore(candidate, 'a'.repeat(64), item) || null);
  if (resolved.some(item => item === null)) return [];
  if (resolved.length === 1) return relationsForOne(candidate, resolved[0]);
  if (resolved.length === 2) return relationsBetween(candidate, resolved[0], resolved[1]);
  const relations = [];
  for (let first = 0; first < resolved.length; first += 1) {
    for (let second = first + 1; second < resolved.length; second += 1) {
      relations.push(...relationsBetween(candidate, resolved[first], resolved[second]));
    }
  }
  return dedupe(relations);
}

function selectable(kind, record, sourceRef, requestSha, title, category, group) {
  return {
    kind,
    id: kind === 'genre_contract' ? record.genre_node_id : record.id,
    sourceRef,
    title,
    category,
    group,
    authority: 'working_proposal',
    request_sha256: requestSha || null,
  };
}

export function listSelectableAnchors(candidate, requestSha = null) {
  if (!candidate || typeof candidate !== 'object') return [];
  const result = [];
  asArray(candidate.nodes).forEach((record, index) => {
    if (!record || !record.id) return;
    const category = text(record.category) || 'other';
    result.push(selectable('node', record, `nodes/${index}`, requestSha,
      text(record.title) || record.id, category, CATEGORY_GROUP[category] || 'context'));
  });
  asArray(candidate.links).forEach((record, index) => {
    if (!record || !record.id) return;
    result.push(selectable('link', record, `links/${index}`, requestSha,
      `${nodeTitle(candidate, record.source)} → ${nodeTitle(candidate, record.target)}`,
      'link', 'causality'));
  });
  asArray(candidate.genre_interactions).forEach((record, index) => {
    if (!record || !record.id) return;
    result.push(selectable('genre_interaction', record, `genre_interactions/${index}`, requestSha,
      `${nodeTitle(candidate, record.source_genre_id)} ${record.kind} ${nodeTitle(candidate, record.target_genre_id)}`,
      'genre_interaction', 'genre'));
  });
  asArray(candidate.emotion_targets).forEach((record, index) => {
    if (!record || !record.id) return;
    result.push(selectable('emotion_target', record, `emotion_targets/${index}`, requestSha,
      `${record.emotion} · ${record.role}`, 'emotion_target', 'emotion'));
  });
  asArray(candidate.genre_contracts).forEach((record, index) => {
    if (!record || !record.genre_node_id) return;
    result.push(selectable('genre_contract', record, `genre_contracts/${index}`, requestSha,
      `${nodeTitle(candidate, record.genre_node_id)} contract`, 'genre_contract', 'genre'));
  });
  asArray(candidate.phases).forEach((record, index) => {
    if (!record || !record.id) return;
    result.push(selectable('phase', record, `phases/${index}`, requestSha,
      text(record.title) || record.id, 'phase', 'structure'));
  });
  return result;
}

const OPERATIONS = new Set(['ask_relation', 'trace', 'challenge', 'compare', 'revise']);

function anchorKey(anchor) {
  return `${anchor.kind}:${anchor.id}`;
}

function operationInstruction(operation) {
  if (operation === 'ask_relation') {
    return 'Ask how the selected elements might relate. Use only the recorded support above as evidence. Propose a working hypothesis with explicit uncertainty; do not assert, save or accept a relationship.';
  }
  if (operation === 'trace') {
    return 'Trace only the recorded relationships above. Explain the path and identify exactly where the evidence stops; do not add inferred, transitive or proximity-based edges.';
  }
  if (operation === 'challenge') {
    return 'Challenge the selected proposal. Separate recorded evidence from assumption, name what is unsupported or uncertain, and suggest what evidence would change the judgment.';
  }
  if (operation === 'compare') {
    return 'Propose one or more alternative working designs that address the author intention. Keep the alternatives unselected and unresolved; do not select or accept one.';
  }
  return 'Propose a holistic working revision addressed to the author intention. Reconsider every materially affected emotion, genre, trope function, engine and structural phase; preserve explicit constraints and accepted author commitments; distinguish coordinated changes from optional suggestions. Do not claim that constraints were preserved or that the revision was applied.';
}

function draftAnchorLine(anchor) {
  const lines = [
    `- ${anchor.kind}/${anchor.id} — "${anchor.title}" — source: ${anchor.sourceRef} — ${anchor.authority}`,
  ];
  if (anchor.meaning) lines.push(`  meaning: ${anchor.meaning}`);
  const components = asArray(anchor.components).slice(0, 8);
  if (components.length) {
    lines.push(`  components: ${components.map(item => `${item.field}=${item.value}`).join('; ')}`);
  }
  return lines.join('\n');
}

function draftSupportLine(item) {
  const from = item.from ? `${item.from.kind}/${item.from.id}` : '?';
  const to = item.to ? `${item.to.kind}/${item.to.id}` : '?';
  const direction = item.direction ? ` (${item.direction} relative to the first selected anchor)` : '';
  return `- [${item.kind}/${item.id}] ${item.sourceRef}: ${from} -> ${to}${direction}\n  ${item.label}: ${item.detail}`;
}

export function buildIntentDraft({
  candidate,
  requestSha,
  currentRequestSha,
  anchors,
  operation,
  authorText,
}) {
  if (!SOURCE_SHA.test(requestSha || '') || !SOURCE_SHA.test(currentRequestSha || '')) {
    throw new Error('Source request SHA is invalid or unavailable.');
  }
  if (requestSha !== currentRequestSha) {
    throw new Error(
      `Source request is stale: captured ${requestSha} does not match current ${currentRequestSha}. ` +
      'Refresh the fixture; selections and drafts are not rebound by title.',
    );
  }
  if (!Array.isArray(anchors) || anchors.length < 1 || anchors.length > 3) {
    throw new Error('Select 1 to 3 source anchors before preparing a draft.');
  }
  if (!OPERATIONS.has(operation)) {
    throw new Error(`Unsupported graph intent operation: ${operation}`);
  }
  if (typeof authorText !== 'string') {
    throw new Error('Author intention must be text.');
  }
  if (authorText.length > 4000) {
    throw new Error('Author intention must be 4000 characters or fewer.');
  }
  if (operation === 'revise' && !authorText.trim()) {
    throw new Error('A revise draft requires a nonempty author intention.');
  }
  if (operation === 'ask_relation' && anchors.length !== 2) {
    throw new Error('ask_relation requires exactly two distinct source anchors.');
  }
  const resolved = [];
  const seen = new Set();
  for (const item of anchors) {
    const anchor = resolveCore(candidate, requestSha, item);
    if (!anchor) {
      const kind = item && typeof item === 'object' ? item.kind : 'unknown';
      const id = item && typeof item === 'object' ? item.id : 'unknown';
      throw new Error(`Anchor is unavailable: ${kind}/${id}. It is not present in the captured candidate.`);
    }
    const key = anchorKey(anchor);
    if (seen.has(key)) throw new Error(`Duplicate selected anchor: ${key}.`);
    seen.add(key);
    resolved.push(anchor);
  }
  const support = recordedRelations(candidate, anchors).slice(0, 8);
  const warnings = [
    'This is an editable intent draft; no coding-agent request has been sent or executed.',
    'The selected architecture is a working proposal, not story canon or shared ontology.',
  ];
  if (!support.length) {
    warnings.push(
      'No recorded relation exists between the selected anchors; a proposed relation would be a working hypothesis, not source evidence.',
    );
  }
  if (operation === 'ask_relation') {
    warnings.push('This draft asks a question; it does not assert, save or accept a relationship.');
  }
  if (operation === 'challenge') {
    warnings.push('Challenge the recorded evidence; do not treat inference or visual proximity as evidence.');
  }
  if (resolved.some(anchor => anchor.components.some(
    item => item.field === 'provenance' && item.value === 'author_declared',
  ))) {
    warnings.push(
      'Author-declared emotion targets are author commitments; preserve them unless the author explicitly requests a change.',
    );
  }
  if (resolved.some(anchor => anchor.components.some(
    item => item.field === 'provenance' && item.value === 'agent_proposed',
  ))) {
    warnings.push('Agent-proposed emotion targets are working hypotheses.');
  }
  if (resolved.some(anchor => anchor.kind === 'link' || anchor.kind === 'genre_interaction')) {
    warnings.push(
      'Recorded links and genre interactions are working proposals; their presence is not proof of reader effect or accepted causality.',
    );
  }
  const anchorLines = resolved.map(draftAnchorLine).join('\n');
  const supportLines = support.length
    ? support.map(draftSupportLine).join('\n')
    : 'No recorded relation exists between the selected anchors. An absent relation means not recorded, not impossible.';
  const intention = authorText.trim() ? authorText : '(no free-text intention supplied)';
  const draftInstruction = [
    'AUTEUR GRAPH INTENT DRAFT — PREPARED, NOT EXECUTED',
    'This draft has not been sent or executed.',
    'kind: studio_graph_intent_draft_v1',
    'authority: noncanonical_intent_draft',
    'status: prepared_not_executed',
    `source_candidate_request_sha256: ${requestSha}`,
    `operation: ${operation}`,
    '',
    'Selected source anchors:',
    anchorLines,
    '',
    'Author intention (verbatim, bounded by the prototype):',
    intention,
    '',
    'Recorded support (one-hop only; no inferred or transitive edges):',
    supportLines,
    '',
    'Requested task:',
    operationInstruction(operation),
    '',
    'Draft constraints:',
    '- Use only the selected source identities and recorded support above as evidence.',
    '- Distinguish recorded evidence from creative hypothesis.',
    '- Do not claim that a relationship exists, that the story changed, or that this draft was executed.',
    '- Return a working proposal for author review; do not accept story or ontology meaning.',
    '- Working proposal, not story canon.',
  ].join('\n');
  return {
    kind: 'studio_graph_intent_draft_v1',
    authority: 'noncanonical_intent_draft',
    status: 'prepared_not_executed',
    request_sha256: requestSha,
    operation,
    anchors: resolved.map(anchor => ({
      kind: anchor.kind,
      id: anchor.id,
      sourceRef: anchor.sourceRef,
      title: anchor.title,
      meaning: anchor.meaning,
      authority: anchor.authority,
    })),
    recorded_support: support,
    draft_instruction: draftInstruction,
    warnings,
  };
}
