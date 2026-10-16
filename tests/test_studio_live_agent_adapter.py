"""Transport fixtures test protocol handling, never authentic creative generation."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/studio_live_agent_adapter.py'


def adapter():
    assert SCRIPT.is_file(), 'The live CLI transport adapter is missing'
    spec = importlib.util.spec_from_file_location('live_adapter', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('role', ['studio_architecture', 'studio_mentor'])
def test_live_agent_adapter_preserves_unicode_and_role(tmp_path, role):
    subject = adapter()
    request = {'role': role, 'request_sha256': 'a'*64,
               'system': 'Return the requested object.', 'user': 'Proteção 🛡️'}
    # Synthetic CLI envelope exercises only stdout extraction and UTF-8 transport.
    cli = tmp_path / 'transport.py'
    cli.write_text('import sys,json\np=json.load(sys.stdin)\n'
                   'print(json.dumps({"type":"item.completed","item":'
                   '{"type":"agent_message","text":json.dumps(p,ensure_ascii=False)}},ensure_ascii=False))\n'
                   'print(json.dumps({"type":"turn.completed","usage":{"output_tokens":1}}))\n', encoding='utf-8')
    result = subject.invoke([sys.executable, str(cli)], request, tmp_path / role, 10)
    assert result == request
    assert json.loads((tmp_path / role / 'request.json').read_text(encoding='utf-8')) == request
    assert (tmp_path / role / 'events.jsonl').is_file()


def test_adapter_rejects_wrong_role_before_launch(tmp_path):
    with pytest.raises(ValueError, match='role'):
        adapter().invoke(['not-a-real-executable'], {'role': 'draft'}, tmp_path, 1)


@pytest.mark.parametrize('output', [
    'not json',
    json.dumps({'type': 'turn.completed'}),
    json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{}'}}),
])
def test_adapter_rejects_incomplete_or_invalid_event_stream(tmp_path, output):
    request = {'role': 'studio_architecture', 'request_sha256': 'a'*64}
    with pytest.raises(ValueError):
        adapter().invoke([sys.executable, '-c', 'print(' + repr(output) + ')'],
                         request, tmp_path, 10)


def test_adapter_timeout_is_not_success(tmp_path):
    with pytest.raises(subprocess.TimeoutExpired):
        adapter().invoke([sys.executable, '-c', 'import time; time.sleep(5)'],
                         {'role': 'studio_mentor', 'request_sha256': 'a'*64}, tmp_path, .1)
