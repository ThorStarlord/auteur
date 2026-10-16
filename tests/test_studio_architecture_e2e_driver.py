"""Safety and command-boundary tests for the authentic-agent Browser qualification runner."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'scripts' / 'studio_architecture_e2e.py'
spec = importlib.util.spec_from_file_location('studio_architecture_e2e', MODULE)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


def _repo(root):
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    subprocess.run(['git', '-C', str(root), 'config', 'user.email', 'test@example.invalid'], check=True)
    subprocess.run(['git', '-C', str(root), 'config', 'user.name', 'Test'], check=True)
    (root / 'note.txt').write_text('accepted bytes', encoding='utf-8')
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'baseline'], check=True)


def test_requires_exact_clean_code_source_before_proving_e2e(tmp_path):
    _repo(tmp_path)
    head = subprocess.check_output(['git', '-C', str(tmp_path), 'rev-parse', 'HEAD'], text=True).strip()
    assert subject.source_identity(tmp_path) == head
    (tmp_path / 'note.txt').write_text('changed', encoding='utf-8')
    with pytest.raises(RuntimeError, match='BLOCKED.*dirty'):
        subject.source_identity(tmp_path)


def test_does_not_claim_e2e_when_no_live_agent_exists(tmp_path):
    report = tmp_path / 'receipt.json'
    assert subject.main(['--report', str(report)]) == 2
    outcome = json.loads(report.read_text(encoding='utf-8'))
    assert outcome['result'] == 'BLOCKED'
    assert outcome['connected_host_e2e'].startswith('BLOCKED')
    assert outcome['human_usability'] == 'NOT_TESTED'
    assert outcome['steps'] == []


def test_canonical_hashes_exclude_only_known_working_paths(tmp_path):
    (tmp_path / 'chapters').mkdir()
    (tmp_path / 'chapters' / 'final.md').write_text('immutable')
    working = tmp_path / '.auteur' / 'beginner' / 'studio' / 'x'
    working.mkdir(parents=True)
    (working / 'canvas.json').write_text('working')
    before = subject.snapshot(tmp_path)
    (working / 'canvas.json').write_text('new work')
    assert subject.snapshot(tmp_path) == before
    (tmp_path / 'chapters' / 'final.md').write_text('different')
    assert subject.snapshot(tmp_path) != before


def test_agent_is_executable_dependency_not_emulated_model():
    packet = {'role': 'studio_architecture', 'request_sha256': 'a'*64}
    with pytest.raises(RuntimeError, match='BLOCKED'):
        subject.run_agent([], packet, 2)
    with pytest.raises(RuntimeError, match='BLOCKED'):
        subject.run_agent(['no-such-real-agent-tool-543222'], packet, 2)
    with pytest.raises(ValueError, match='single raw JSON object'):
        subject.run_agent([sys.executable, '-c', "print('not json')"], packet, 10)
    with pytest.raises(ValueError, match='raw JSON object'):
        subject.run_agent([sys.executable, '-c', "print('\"still not an object\"')"], packet, 10)


def test_generated_payload_fingerprint_is_stable_across_json_object_order():
    left = {'nodes': [{'id': 'a'}], 'summary': 'A'}
    right = {'summary': 'A', 'nodes': [{'id': 'a'}]}
    assert subject.fingerprint_json(left) == subject.fingerprint_json(right)
    assert len(subject.fingerprint_json(left)) == 64


def test_reentry_requires_candidate_and_working_choice_not_just_vision():
    candidate = {'status': 'stale', 'candidate_request_sha256': 'a'*64,
                 'candidate': {'summary': 'Original abstract architecture'}}
    canvas = {'items': [{'id': 'story-vision'}, {'id': 'working-choice',
              'proposal_origin': {'source_kind': 'host_agent_suggestion'}}]}
    assert subject.reentry_invariants(candidate, canvas, 'a'*64, 'working-choice')
    assert not subject.reentry_invariants({**candidate, 'candidate': None}, canvas, 'a'*64, 'working-choice')
    assert not subject.reentry_invariants(candidate, {'items': canvas['items'][:1]}, 'a'*64, 'working-choice')
    assert not subject.reentry_invariants(candidate, canvas, 'b'*64, 'working-choice')


def test_failed_agent_does_not_expose_stderr_secrets_in_receipt():
    packet = {'role': 'studio_architecture', 'request_sha256': 'a'*64}
    cmd = [sys.executable, '-c',
           "import sys; sys.stderr.write('SECRET_FROM_AGENT_STDERR'); sys.exit(7)"]
    with pytest.raises(RuntimeError) as caught:
        subject.run_agent(cmd, packet, 2)
    assert 'Agent exited with code 7' in str(caught.value)
    assert 'SECRET_FROM_AGENT_STDERR' not in str(caught.value)


def test_waits_for_persisted_mentor_keep_not_an_arbitrary_delay():
    steps = [{'items': []}, {'items': [{'id': 'kept', 'proposal_origin': {'source_kind': 'host_agent_suggestion'}}]}]
    def read():
        return steps.pop(0) if len(steps) > 1 else steps[0]
    saved, kept = subject.wait_for_working_choice(read, timeout=1, interval=0)
    assert saved['items'][0]['id'] == kept['id'] == 'kept'
    assert subject.wait_for_working_choice(read, timeout=1, interval=0)[1]['id'] == 'kept'
    with pytest.raises(TimeoutError):
        subject.wait_for_working_choice(lambda: {'items': []}, timeout=0, interval=0)


def test_uses_local_source_checkout_for_response_validation(tmp_path):
    with pytest.raises(RuntimeError, match='BLOCKED.*local Auteur source'):
        subject.local_source_path(tmp_path)
    source = tmp_path / 'src' / 'auteur'
    source.mkdir(parents=True)
    (source / 'host_agent.py').write_text('')
    assert subject.local_source_path(tmp_path) == str(tmp_path / 'src')


def test_agent_transport_preserves_unicode_with_windows_ansi_locale(monkeypatch):
    packet = {'role': 'studio_architecture', 'request_sha256': 'a'*64,
              'user': 'Generosidade — proteção 🛡️'}
    original = subprocess.run
    def ansi_default(*args, **kwargs):
        kwargs.setdefault('encoding', 'cp1252')
        return original(*args, **kwargs)
    monkeypatch.setattr(subject.subprocess, 'run', ansi_default)
    command = [sys.executable, '-c',
               'import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())']
    assert subject.run_agent(command, packet, 10) == packet


def test_reads_exact_packet_from_collapsed_advanced_handoff():
    packet = {'role': 'studio_mentor', 'request_sha256': 'b'*64, 'user': 'Proteção 🛡️'}
    class CollapsedRequest:
        def inner_text(self):
            return ''  # Chromium's rendered text for the closed details panel.
        def text_content(self):
            return json.dumps(packet, ensure_ascii=False)
    assert subject.read_mentor_request(CollapsedRequest()) == packet


def test_outer_runner_timeout_stops_adapter_descendants(tmp_path):
    marker = tmp_path / 'outer-timeout-child'
    child = 'import time,pathlib; time.sleep(2); pathlib.Path(' + repr(str(marker)) + ').touch()'
    parent = 'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",' + repr(child) + ']); time.sleep(20)'
    with pytest.raises(RuntimeError, match='BLOCKED.*timed out'):
        subject.run_agent([sys.executable, '-c', parent],
                          {'role': 'studio_mentor', 'request_sha256': 'b'*64}, 1)
    time.sleep(2.5)
    assert not marker.exists(), 'Outer timeout left the adapter descendant running'
