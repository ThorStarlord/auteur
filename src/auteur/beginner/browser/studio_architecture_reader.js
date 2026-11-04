/* Text-first, read-only overview of a noncanonical Narrative Architecture candidate.
   No provider calls, no story acceptance, no ontology writes. */
(function (global) {
  'use strict';

  var asArray = function (value) { return Array.isArray(value) ? value : []; };
  var text = function (value) { return typeof value === 'string' ? value : ''; };
  var nonempty = function (value) { return text(value).trim().length > 0; };
  var basicEmotions = ['joy', 'sadness', 'fear', 'anger', 'disgust', 'surprise'];

  function nodeTitle(id, titles) {
    return titles[id] || id;
  }

  function emptyProjection() {
    return {
      status: 'empty',
      authority: 'working_proposal',
      authorityLabel: 'Working proposal — not accepted story',
      summary: 'No working architecture has been generated yet.',
      schemaVersion: null,
      emotions: [],
      complexEmotions: [],
      genres: [],
      tropes: [],
      structure: [],
      mechanisms: [],
      relationships: [],
      uncertainties: [],
    };
  }

  function hasCandidateContent(candidate) {
    return ['nodes', 'links', 'phases', 'emotion_targets', 'complex_emotions',
      'genre_contracts', 'genre_interactions'].some(function (field) {
        return asArray(candidate[field]).some(function (entry) {
          return entry && typeof entry === 'object';
        });
      });
  }

  function project(candidate) {
    if (!candidate || typeof candidate !== 'object' || !hasCandidateContent(candidate)) {
      return emptyProjection();
    }
    var nodes = asArray(candidate.nodes).filter(function (node) {
      return node && typeof node === 'object' && nonempty(node.id);
    });
    var titles = {};
    nodes.forEach(function (node) { titles[node.id] = nonempty(node.title) ? node.title : node.id; });

    var emotions = asArray(candidate.emotion_targets).filter(function (target) {
      return target && typeof target === 'object' && nonempty(target.id);
    }).map(function (target) {
      return {
        id: target.id,
        label: basicEmotions.indexOf(target.emotion) >= 0 ? target.emotion : 'unspecified',
        role: text(target.role) || 'unspecified',
        intendedEffect: text(target.intended_effect),
        elicitingCondition: text(target.eliciting_condition),
        aestheticStrategy: text(target.aesthetic_strategy),
        provenance: text(target.provenance) || 'unknown',
      };
    });

    var complexEmotions = asArray(candidate.complex_emotions).filter(function (emotion) {
      return emotion && typeof emotion === 'object' && nonempty(emotion.title);
    }).map(function (emotion) {
      return {
        id: text(emotion.id) || emotion.title,
        title: emotion.title,
        basicEmotions: asArray(emotion.basic_emotions).filter(function (value) {
          return typeof value === 'string';
        }),
        context: text(emotion.context),
      };
    });

    var genres = [];
    var genreById = {};
    function ensureGenre(id) {
      if (!nonempty(id) || genreById[id]) return genreById[id] || null;
      genreById[id] = {
        id: id,
        title: nodeTitle(id, titles),
        role: 'unassigned',
        narrativeEngine: '',
        structuralPattern: '',
        tropeFunctions: [],
        payoffExpectations: [],
        emotionRoles: [],
      };
      genres.push(genreById[id]);
      return genreById[id];
    }
    nodes.filter(function (node) { return node.category === 'genre'; })
      .forEach(function (node) { ensureGenre(node.id); });
    asArray(candidate.genre_contracts).forEach(function (contract) {
      if (!contract || typeof contract !== 'object') return;
      var genre = ensureGenre(contract.genre_node_id);
      if (!genre) return;
      genre.role = text(contract.role) || 'unassigned';
      genre.narrativeEngine = text(contract.narrative_engine);
      genre.structuralPattern = text(contract.structural_pattern);
      genre.tropeFunctions = asArray(contract.trope_functions).filter(nonempty);
      genre.payoffExpectations = asArray(contract.payoff_expectations).filter(nonempty);
      genre.emotionRoles = asArray(contract.emotion_target_ids).map(function (id) {
        var target = emotions.filter(function (item) { return item.id === id; })[0];
        return target ? target.label + ' · ' + target.role : id;
      });
    });

    var tropes = [];
    var tropeKeys = {};
    function addTrope(value, genreId, source) {
      if (!nonempty(value)) return;
      var key = genreId + ':' + value;
      if (tropeKeys[key]) return;
      tropeKeys[key] = true;
      tropes.push({
        id: genreId + ':trope:' + tropes.length,
        text: value,
        genreId: genreId,
        genreTitle: nodeTitle(genreId, titles),
        source: source,
      });
    }
    asArray(candidate.genre_contracts).forEach(function (contract) {
      if (!contract || typeof contract !== 'object') return;
      asArray(contract.trope_functions).forEach(function (value) {
        addTrope(value, text(contract.genre_node_id), 'genre_contract');
      });
    });
    asArray(candidate.phases).forEach(function (phase) {
      asArray(phase && phase.genre_activations).forEach(function (activation) {
        asArray(activation && activation.trope_functions).forEach(function (value) {
          addTrope(value, text(activation.genre_node_id), 'phase_activation');
        });
      });
    });

    var structure = asArray(candidate.phases).filter(function (phase) {
      return phase && typeof phase === 'object' && nonempty(phase.id);
    }).map(function (phase) {
      return {
        id: phase.id,
        title: nonempty(phase.title) ? phase.title : phase.id,
        order: typeof phase.order === 'number' && isFinite(phase.order) ? phase.order : 0,
        narrativeFunction: text(phase.narrative_function),
        readerExperience: text(phase.reader_experience),
        transition: text(phase.transition),
        parallelWith: asArray(phase.parallel_with).filter(nonempty),
        genres: asArray(phase.genres).filter(function (item) {
          return item && typeof item === 'object' && nonempty(item.genre);
        }).map(function (item) {
          return {genre: item.genre, role: text(item.role)};
        }),
      };
    }).sort(function (a, b) {
      return a.order - b.order || a.title.localeCompare(b.title);
    });

    var mechanisms = nodes.filter(function (node) {
      return ['engine', 'thread', 'structure', 'theme'].indexOf(node.category) >= 0;
    }).map(function (node) {
      return {
        id: node.id,
        title: nodeTitle(node.id, titles),
        category: text(node.category),
        summary: text(node.summary),
      };
    });

    var relationships = [];
    asArray(candidate.links).filter(function (link) {
      return link && typeof link === 'object' && nonempty(link.id)
        && nonempty(link.source) && nonempty(link.target);
    }).forEach(function (link) {
      relationships.push({
        id: link.id,
        kind: 'link',
        from: nodeTitle(link.source, titles),
        to: nodeTitle(link.target, titles),
        function: text(link.function),
      });
    });
    asArray(candidate.genre_interactions).filter(function (edge) {
      return edge && typeof edge === 'object' && nonempty(edge.id);
    }).forEach(function (edge) {
      relationships.push({
        id: edge.id,
        kind: 'genre_interaction',
        from: nodeTitle(text(edge.source_genre_id), titles),
        to: nodeTitle(text(edge.target_genre_id), titles),
        function: text(edge.kind),
        mechanism: text(edge.mechanism),
        risk: text(edge.risk),
      });
    });

    return {
      status: 'ready',
      authority: 'working_proposal',
      authorityLabel: 'Working proposal — not accepted story',
      summary: text(candidate.summary),
      schemaVersion: typeof candidate.schema_version === 'number' ? candidate.schema_version : null,
      emotions: emotions,
      complexEmotions: complexEmotions,
      genres: genres,
      tropes: tropes,
      structure: structure,
      mechanisms: mechanisms,
      relationships: relationships,
      uncertainties: asArray(candidate.open_questions).filter(nonempty),
    };
  }

  function make(doc, tag, className, value) {
    var node = doc.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  }

  function addSection(doc, root, title, lines) {
    if (!lines.length) return;
    root.appendChild(make(doc, 'h3', 'architecture-reader-heading', title));
    var list = make(doc, 'ul', 'architecture-reader-list');
    lines.forEach(function (line) {
      list.appendChild(make(doc, 'li', '', line));
    });
    root.appendChild(list);
  }

  function render(root, projection, doc) {
    if (!root || typeof root.replaceChildren !== 'function') {
      throw new Error('Architecture reader requires a render root');
    }
    var documentRef = doc || (typeof document !== 'undefined' ? document : null);
    if (!documentRef || typeof documentRef.createElement !== 'function') {
      throw new Error('Architecture reader requires a document');
    }
    root.replaceChildren();
    root.appendChild(make(documentRef, 'h2', 'architecture-reader-title', 'Your narrative architecture'));
    root.appendChild(make(documentRef, 'p', 'architecture-reader-authority',
      projection.authorityLabel || 'Working proposal — not accepted story'));
    root.appendChild(make(documentRef, 'p', 'architecture-reader-summary',
      projection.summary || 'No architecture summary is available.'));
    if (projection.status === 'empty') return;

    addSection(documentRef, root, 'Emotional promise', projection.emotions.map(function (emotion) {
      var line = emotion.label + ' · ' + emotion.role + ' — ' + emotion.intendedEffect;
      if (emotion.elicitingCondition) line += ' (Elicited by: ' + emotion.elicitingCondition + ')';
      if (emotion.provenance !== 'unknown') line += ' [' + emotion.provenance.replace(/_/g, ' ') + ']';
      return line;
    }).concat(projection.complexEmotions.map(function (emotion) {
      return emotion.title + ' — ' + emotion.context + ' (' + emotion.basicEmotions.join(', ') + ')';
    })));

    addSection(documentRef, root, 'Genres and their work', projection.genres.map(function (genre) {
      var line = genre.title + ' · ' + genre.role;
      if (genre.narrativeEngine) line += ' — Engine: ' + genre.narrativeEngine;
      if (genre.structuralPattern) line += '; Structure: ' + genre.structuralPattern;
      if (genre.payoffExpectations.length) line += '; Payoff: ' + genre.payoffExpectations.join('; ');
      return line;
    }));

    addSection(documentRef, root, 'Functional tropes', projection.tropes.map(function (trope) {
      return trope.text + ' — ' + trope.genreTitle + ' (' + trope.source.replace(/_/g, ' ') + ')';
    }));

    addSection(documentRef, root, 'Structure', projection.structure.map(function (phase) {
      var line = phase.title + ' (order ' + phase.order + '): ' + phase.narrativeFunction;
      if (phase.readerExperience) line += ' Reader experience: ' + phase.readerExperience;
      if (phase.transition) line += ' Transition: ' + phase.transition;
      return line;
    }));

    addSection(documentRef, root, 'Narrative mechanisms', projection.mechanisms.map(function (mechanism) {
      return mechanism.title + ' (' + mechanism.category + '): ' + mechanism.summary;
    }));

    addSection(documentRef, root, 'Relationships', projection.relationships.map(function (relationship) {
      var line = relationship.from + ' → ' + relationship.function + ' → ' + relationship.to;
      if (relationship.mechanism) line += ' — ' + relationship.mechanism;
      return line;
    }));

    addSection(documentRef, root, 'Open questions', projection.uncertainties);
  }

  global.AuteurStudioArchitectureReader = {project: project, render: render};
})(window);
