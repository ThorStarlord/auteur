"""Injected executors test dispatch contracts; only a live run proves generation."""
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import prepare_architecture
from auteur.beginner.studio_store import CanvasStore


def http(base, path, payload=None, headers=None):
    req = Request(base + path, data=None if payload is None else json.dumps(payload).encode(),
                  headers={'Content-Type': 'application/json', **(headers or {})})
    with urlopen(req, timeout=5) as response:
        return response.status, json.load(response)


def canvas(root, name='dispatch-test'):
    store = CanvasStore(root, name)
    store.create()
    store.apply('create-item', expected_revision=0, command_id='vision', payload={
        'item': {'id': 'story-vision', 'kind': 'note', 'title': 'Story Vision',
                 'content': 'A joyful story of courage and generosity.'},
        'position': {'x': 0, 'y': 0}})
    return store


def test_real_executor_is_opt_in_and_dispatch_is_exact_and_source_bound(tmp_path):
    store = canvas(tmp_path)
    packet = prepare_architecture(store)['request']
    calls = []
    class Executor:
        def enqueue(self, project_root, canvas_id, request):
            calls.append((project_root, canvas_id, request.model_dump()))
    server = BeginnerWorkspaceServer(tmp_path, port=0, studio_architecture_executor=Executor())
    thread = server.start_in_thread()
    base = f'http://127.0.0.1:{server.port}'
    route = '/api/beginner/studio/canvases/dispatch-test/architecture/dispatch'
    try:
        assert http(base, '/api/beginner/studio/host-capabilities')[1]['studio_architecture']['attached']
        with pytest.raises(HTTPError) as wrong:
            http(base, route, {'request_sha256': '0'*64})
        assert wrong.value.code == 409 and calls == []
        assert http(base, route, {'request_sha256': packet['request_sha256']}) == (
            202, {'state': 'submitted', 'request_sha256': packet['request_sha256']})
        assert calls == [(tmp_path, store.canvas_id, packet)]
        assert http(base, route, {'request_sha256': packet['request_sha256']})[0] == 202
        assert len(calls) == 1, 'A retried dispatch must not enqueue duplicate model work'
        canvas(tmp_path, 'other')
        with pytest.raises(HTTPError) as cross:
            http(base, route.replace('dispatch-test', 'other'), {'request_sha256': packet['request_sha256']})
        assert cross.value.code == 409 and len(calls) == 1
        doc = store.load().model_dump(mode='json')
        doc['items'][0]['content'] = 'A different author vision.'
        store.apply('replace-working-document', expected_revision=doc['revision'], command_id='changed',
                    payload={key: doc[key] for key in ('items', 'connections', 'positions', 'viewport')})
        with pytest.raises(HTTPError) as stale:
            http(base, route, {'request_sha256': packet['request_sha256']})
        assert stale.value.code == 409 and len(calls) == 1
    finally:
        server.stop()
        thread.join(timeout=3)


def test_missing_executor_never_claims_submission(tmp_path):
    canvas(tmp_path)
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    base = f'http://127.0.0.1:{server.port}'
    try:
        assert http(base, '/api/beginner/studio/host-capabilities')[1] == {'studio_architecture': {'attached': False}}
        with pytest.raises(HTTPError) as missing:
            http(base, '/api/beginner/studio/canvases/dispatch-test/architecture/dispatch', {'request_sha256': '0'*64})
        assert missing.value.code == 503
    finally:
        server.stop()
        thread.join(timeout=3)


def test_failed_submission_preserves_pending_request_and_canvas(tmp_path):
    store = canvas(tmp_path)
    packet = prepare_architecture(store)['request']
    before = store.load().model_dump(mode='json')
    class Unavailable:
        def enqueue(self, *args):
            raise RuntimeError('executor unavailable')
    server = BeginnerWorkspaceServer(tmp_path, port=0, studio_architecture_executor=Unavailable())
    thread = server.start_in_thread()
    base = f'http://127.0.0.1:{server.port}'
    route = '/api/beginner/studio/canvases/dispatch-test/architecture'
    try:
        with pytest.raises(HTTPError) as failed:
            http(base, route + '/dispatch', {'request_sha256': packet['request_sha256']})
        assert failed.value.code == 503
        assert http(base, route)[1]['status'] == 'awaiting_host_agent'
        assert store.load().model_dump(mode='json') == before
    finally:
        server.stop()
        thread.join(timeout=3)


@pytest.mark.parametrize('headers,status', [
    ({'Origin': 'https://untrusted.example'}, 403),
    ({'Content-Type': 'text/plain'}, 415),
    ({'Host': 'untrusted.example'}, 421),
])
def test_privileged_dispatch_refuses_foreign_or_simple_requests(tmp_path, headers, status):
    store = canvas(tmp_path)
    packet = prepare_architecture(store)['request']
    calls = []
    class Executor:
        def enqueue(self, *args): calls.append(args)
    server = BeginnerWorkspaceServer(tmp_path, port=0, studio_architecture_executor=Executor())
    thread = server.start_in_thread()
    base = f'http://127.0.0.1:{server.port}'
    try:
        with pytest.raises(HTTPError) as refused:
            http(base, '/api/beginner/studio/canvases/dispatch-test/architecture/dispatch',
                 {'request_sha256': packet['request_sha256']}, headers=headers)
        assert refused.value.code == status
        assert calls == []
    finally:
        server.stop()
        thread.join(timeout=3)
