"""Truth-boundary checks for the explanatory-design fixtures."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'docs/prototypes/studio-explanations'


def load(name):
    return json.loads((ROOT / 'fixtures' / name).read_text(encoding='utf-8'))


def test_two_story_fixtures_are_reproducible_and_noncanonical():
    for filename, story_id in [('paladin.json', 'paladin'), ('hybrid.json', 'hybrid')]:
        story = load(filename)
        assert story['story_id'] == story_id
        assert story['authority_status'] == 'DERIVED / NOT CANON'
        assert story['illustrative'] is True
        assert len(story['nodes']) >= 4
        ids = [n['id'] for n in story['nodes']]
        assert len(ids) == len(set(ids))
        assert all(node['story_treatment'].startswith('proposed_') or node['story_treatment'] == 'unresolved' for node in story['nodes'])
        assert all(edge['source'] in ids and edge['target'] in ids for edge in story['proposal_edges'])
        assert all(edge.get('source_ref') for edge in story['proposal_edges'])
        assert all(genre['id'] in {g['id'] for g in story['genres']} for genre in story['genres'])


def test_knowledge_coverage_does_not_invent_pack_support():
    evidence = load('genre-evidence.json')
    assert evidence['progression_fantasy']['coverage'] == 'inference_only'
    assert evidence['heroic_fantasy']['coverage'] == 'inference_only'
    assert evidence['progression_fantasy']['pack_version'] is None
    assert evidence['heroic_fantasy']['pack_version'] is None
    assert evidence['epic_fantasy']['coverage'] == 'legacy_contract'
    assert evidence['epic_fantasy']['legacy_rule_field'] == 'required_tropes'
    assert 'src/auteur/genres/data/epic_fantasy.yaml' in evidence['epic_fantasy']['source_ref']
    assert 'pack_backed' not in [e['coverage'] for e in evidence.values()]


def test_each_relation_retains_its_own_epistemic_claim():
    for filename in ('paladin.json', 'hybrid.json'):
        story = load(filename)
        known_nodes = {x['id'] for x in story['nodes']}
        known_genres = {x['id'] for x in story['genres']}
        for link in story['genre_links']:
            assert link['node_id'] in known_nodes
            assert link['genre_id'] in known_genres
            assert link['source_ref'] and link['source_kind']
            assert link['relation'] in {'adapts', 'supports', 'contrasts', 'uses', 'unknown'}
            if link['source_kind'] == 'model_inference':
                assert link['rule_strength'] is None
