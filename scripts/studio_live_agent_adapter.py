"""Operator-only Codex CLI transport for studio_architecture_e2e.py.

Not a Browser executor. Uses existing CLI authentication; never changes providers.
Private request, event and stderr evidence is written outside the checkout.
Synthetic transport tests do not establish live model execution.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid


def run_command(argv, *, input, timeout, **options):
    """Bound a launcher and its descendants, including outer-runner cancellation."""
    with subprocess.Popen(argv, stdin=subprocess.PIPE, text=True, encoding='utf-8',
                          start_new_session=os.name != 'nt', **options) as process:
        try:
            stdout, stderr = process.communicate(input=input, timeout=timeout)
        except BaseException:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               timeout=10, check=False)
            else:
                import signal
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # The process group already exited.
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            raise
        return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)


def invoke(argv: list[str], request: dict, evidence: Path, timeout: float) -> dict:
    if request.get('role') not in {'studio_architecture', 'studio_mentor'}:
        raise ValueError('Unsupported or missing request role')
    if not request.get('request_sha256'):
        raise ValueError('Missing request fingerprint')
    evidence.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(request, ensure_ascii=False)
    (evidence / 'request.json').write_text(payload + '\n', encoding='utf-8')
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    started = time.monotonic()
    invocation = {'argv': argv, 'request_sha256': request['request_sha256'],
                  'returncode': None, 'timed_out': False}
    receipt = evidence / 'invocation.json'
    receipt.write_text(json.dumps(invocation, indent=2), encoding='utf-8')
    # Keep raw diagnostics private, even if the process fails or times out.
    with (evidence / 'events.jsonl').open('w', encoding='utf-8') as events_file, \
         (evidence / 'private-stderr.log').open('w', encoding='utf-8') as stderr_file:
        try:
            result = run_command(argv, input=payload, stdout=events_file,
                                 stderr=stderr_file, timeout=timeout, env=env, shell=False)
            invocation['returncode'] = result.returncode
        except subprocess.TimeoutExpired:
            invocation.update(timed_out=True, returncode=-1)
            raise
        finally:
            invocation['elapsed_seconds'] = time.monotonic() - started
            receipt.write_text(json.dumps(invocation, indent=2), encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Coding agent failed; inspect private local evidence')
    events = [json.loads(line) for line in
              (evidence / 'events.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    if not any(event.get('type') == 'turn.completed' for event in events) or any(
        event.get('type') in {'turn.failed', 'error'} for event in events
    ):
        raise ValueError('Coding agent did not complete a successful turn')
    messages = [event['item']['text'] for event in events
                if event.get('type') == 'item.completed'
                and event.get('item', {}).get('type') == 'agent_message']
    if len(messages) != 1:
        raise ValueError('Expected exactly one structured agent response')
    response = json.loads(messages[0])
    if not isinstance(response, dict):
        raise ValueError('Agent response must be a JSON object')
    (evidence / 'response.json').write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding='utf-8')
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-js', required=True, help='Installed @openai/codex/bin/codex.js')
    parser.add_argument('--node', default='node')
    parser.add_argument('--model', required=True, help='An available model on the existing CLI account')
    parser.add_argument('--evidence', type=Path, required=True, help='Private directory outside the checkout')
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    request = json.loads(sys.stdin.buffer.read().decode('utf-8'))
    argv = [args.node, args.codex_js, 'exec', '--json', '--color', 'never',
            '--ephemeral', '-s', 'read-only', '-m', args.model,
            'Fulfill the exact HostAgentRequest in stdin. Its system and user fields '
            'define the task and schema. Return only the raw requested payload JSON object, '
            'not a response envelope or Markdown. Do not use tools or modify files.']
    evidence = args.evidence.resolve() / uuid.uuid4().hex
    response = invoke(argv, request, evidence, args.timeout)
    sys.stdout.buffer.write((json.dumps(response, ensure_ascii=False) + '\n').encode('utf-8'))


if __name__ == '__main__':
    main()
