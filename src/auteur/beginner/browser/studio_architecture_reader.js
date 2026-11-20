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

  function project(candidate, status) {
    if (!candidate || typeof candidate !== 'object' || !hasCandidateContent(candidate)) {
      return emptyProjection();
    }
    var nodes = asArray(candidate.nodes).filter(function (node) {
      return node && typeof node === 'object' && nonempty(node.id);
    });
    var titles = {};
    nodes.forEach(function (node) { titles[node.id] = nonempty(node.title) ? node.title : node.id; });

    var emotionNaming = {};
    asArray(status && status.authorEmotionGrounding).forEach(function (row) {
      if (row && nonempty(row.id)) emotionNaming[row.id] = row.emotion_named_by_author === true;
    });
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
        groundingKnown: Object.prototype.hasOwnProperty.call(emotionNaming, target.id),
        emotionNamedByAuthor: emotionNaming[target.id] === true,
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
      opportunities: asArray(candidate.opportunities).filter(function (item) {
        return item && typeof item === 'object' && nonempty(item.title);
      }).map(function (item) {
        return {
          id: text(item.id),
          title: text(item.title),
          whyItMatters: text(item.why_it_matters),
          scope: text(item.scope) || 'other',
          relationship: text(item.relationship) || 'unclear',
          requiresAuthorDecision: item.requires_author_decision === true,
          provisionalPrimary: item.provisional_primary === true,
        };
      }),
      governingObjective: (status && status.governingObjective) || null,
      interpretations: asArray(candidate.interpretations).filter(function (item) {
        return item && typeof item === 'object' && nonempty(item.interpretation);
      }).map(function (item) {
        return {
          id: text(item.id),
          interpretation: text(item.interpretation),
          consequences: text(item.consequences),
          alternative: text(item.alternative),
          requiresDecision: item.author_decision_required === true,
        };
      }),
      interpretationAffects: (function () {
        var ids = {};
        asArray(candidate.interpretations).forEach(function (item) {
          asArray(item && item.affects).forEach(function (id) {
            if (nonempty(id)) ids[id] = true;
          });
        });
        return ids;
      })(),
      premiseStatus: (status && status.premiseStatus) || null,
    };
  }

  function excerpt(value, limit) {
    var valueText = text(value);
    if (valueText.length <= limit) return valueText;
    return valueText.slice(0, limit - 1) + '\u2026';
  }

  function describeStatus(projection) {
    var lines = [];
    var objective = projection.governingObjective;
    if (objective && objective.story_vision) {
      lines.push('Author objective: ' + excerpt(objective.story_vision, 240));
    }
    if (objective && objective.instruction) {
      lines.push('Requested change: ' + excerpt(objective.instruction, 240));
    }
    var status = projection.premiseStatus;
    if (!status) return lines;
    var authorNamed = (status.author_expressed || {}).emotion_targets || [];
    lines.push('Author-named: ' + (authorNamed.length ? authorNamed.join(', ') : 'nothing yet'));
    var provisional = status.provisional_agent_interpretation || {};
    lines.push('Agent interpretation: ' + (provisional.nodes || []).length + ' mechanisms, '
      + (provisional.links || []).length + ' relationships, and the summary above');
    var accepted = status.accepted || {};
    lines.push('Accepted commitments: ' + (accepted.source
      ? 'drawn from accepted Story Identity' : 'none yet'));
    var unresolved = (status.unresolved || {}).open_questions || [];
    if (unresolved.length) {
      lines.push('Unresolved: ' + unresolved.length + ' open question(s)');
    }
    return lines;
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

  function joinLimited(items, limit, separator) {
    var between = separator || ' · ';
    var shown = items.slice(0, limit).join(between);
    return items.length > limit ? shown + between + '+' + (items.length - limit) + ' more' : shown;
  }

  // One line per narrative system, so the author grasps the design before any long section.
  function glanceLines(projection) {
    var lines = [];
    if (projection.emotions.length) {
      lines.push('Emotional promise: ' + joinLimited(projection.emotions.map(function (emotion) {
        return emotion.label + ' (' + emotion.role + ')';
      }), 6));
    }
    var engines = projection.mechanisms.filter(function (item) { return item.category === 'engine'; });
    if (engines.length) {
      lines.push('Narrative engines: ' + joinLimited(engines.map(function (item) { return item.title; }), 4));
    }
    if (projection.genres.length) {
      lines.push('Genres: ' + joinLimited(projection.genres.map(function (genre) {
        return genre.title + (genre.role ? ' (' + genre.role + ')' : '');
      }), 5));
    }
    var interactions = projection.relationships.filter(function (item) { return item.kind === 'genre_interaction'; });
    if (interactions.length) {
      var verbs = {creates_tension: 'creates tension with', contrasts: 'contrasts with', converges: 'converges with'};
      lines.push('How genres interact: ' + joinLimited(interactions.map(function (item) {
        return item.from + ' ' + (verbs[item.function] || item.function.replace(/_/g, ' ')) + ' ' + item.to;
      }), 3));
    }
    if (projection.structure.length) {
      lines.push('Development: ' + projection.structure.length + ' phase'
        + (projection.structure.length === 1 ? '' : 's') + ' — '
        + joinLimited(projection.structure.map(function (phase) { return phase.title; }), 6, ' → '));
    }
    var decisions = projection.interpretations.filter(function (item) { return item.requiresDecision; }).length
      + projection.opportunities.filter(function (item) { return item.requiresAuthorDecision; }).length;
    if (decisions) lines.push('Needs your decision: ' + decisions + ' (see the full architecture)');
    if (projection.uncertainties.length) {
      lines.push('Open questions: ' + projection.uncertainties.length);
    }
    return lines;
  }

  function render(root, projection, doc) {
    if (!root || typeof root.replaceChildren !== 'function') {
      throw new Error('Architecture reader requires a render root');
    }
    var documentRef = doc || (typeof document !== 'undefined' ? document : null);
    if (!documentRef || typeof documentRef.createElement !== 'function') {
      throw new Error('Architecture reader requires a document');
    }
    var wasOpen = typeof root.querySelector === 'function'
      && !!root.querySelector('.architecture-reader-full[open]');
    root.replaceChildren();
    root.appendChild(make(documentRef, 'h2', 'architecture-reader-title', 'Your narrative architecture'));
    root.appendChild(make(documentRef, 'p', 'architecture-reader-authority',
      projection.authorityLabel || 'Working proposal — not accepted story'));
    root.appendChild(make(documentRef, 'p', 'architecture-reader-default-authority',
      'Unmarked material below is an agent proposal, not an author-established commitment.'));
    root.appendChild(make(documentRef, 'p', 'architecture-reader-summary',
      projection.summary || 'No architecture summary is available.'));
    if (projection.status === 'empty') return;

    addSection(documentRef, root, 'At a glance', glanceLines(projection));
    addSection(documentRef, root, 'What this proposal is', describeStatus(projection));

    // The complete linear text stays available (and is the non-visual equivalent of the graph),
    // but it no longer pushes the graph and perspectives below the first screen.
    var full = make(documentRef, 'details', 'architecture-reader-full');
    full.open = wasOpen;
    full.appendChild(make(documentRef, 'summary', 'architecture-reader-full-toggle', 'Read the full architecture'));
    root.appendChild(full);
    root = full;

    addSection(documentRef, root, 'Emotional promise', projection.emotions.map(function (emotion) {
      var line = emotion.label + ' · ' + emotion.role + ' — ' + emotion.intendedEffect;
      if (emotion.elicitingCondition) line += ' (Elicited by: ' + emotion.elicitingCondition + ')';
      if (emotion.provenance === 'author_declared' && emotion.groundingKnown
          && !emotion.emotionNamedByAuthor) {
        line += ' [experience described by the author; emotion label assigned by the agent]';
      } else if (emotion.provenance !== 'unknown') {
        line += ' [' + emotion.provenance.replace(/_/g, ' ') + ']';
      }
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
      var line = mechanism.title + ' (' + mechanism.category + '): ' + mechanism.summary;
      if (projection.interpretationAffects[mechanism.id]) {
        line += ' [depends on a proposed reading]';
      }
      return line;
    }));

    addSection(documentRef, root, 'Relationships', projection.relationships.map(function (relationship) {
      var line = relationship.from + ' → ' + relationship.function + ' → ' + relationship.to;
      if (relationship.mechanism) line += ' — ' + relationship.mechanism;
      return line;
    }));

    addSection(documentRef, root, 'Readings the agent is using (not your commitments)',
      projection.interpretations.map(function (item) {
        var line = item.interpretation + ' -> ' + item.consequences;
        if (item.alternative) line += ' | Alternative: ' + item.alternative;
        if (item.requiresDecision) line += ' [your decision required]';
        return line;
      }));

    addSection(documentRef, root, 'Optional opportunities (not accepted)',
      projection.opportunities.map(function (item) {
        var line = item.title + ' (' + item.scope + ', ' + item.relationship + ')';
        if (item.provisionalPrimary) {
          line += ' - the agent provisional primary under your delegated goal discovery';
        }
        if (item.requiresAuthorDecision) {
          line += ' - would replace your purpose: your decision required';
        }
        return line + ': ' + item.whyItMatters;
      }));

    addSection(documentRef, root, 'Open questions', projection.uncertainties);
  }

  global.AuteurStudioArchitectureReader = {project: project, render: render};
})(window);
