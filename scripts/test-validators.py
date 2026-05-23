import os
import subprocess
import sys
import yaml
import re
import argparse
from datetime import datetime

def parse_frontmatter(file_path):
    """Extracts YAML frontmatter from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.match(r'^---\s*[\r\n]+(.*?)\n---\s*[\r\n]+', content, re.DOTALL)
    if not match:
        match = re.match(r'^---\s*[\r\n]+(.*?)\r\n---\s*[\r\n]+', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return {}
    return {}

def detect_validator_signature(validator_path):
    """Detect validator CLI signature by checking its code."""
    with open(validator_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for validators that take TWO positional arguments
    if 'artifact_id' in content and ('artifact_path' in content or 'add_argument("artifact' in content):
        return 'two_arg'  # artifact_id + artifact_path

    # Check for validators that take NO file arguments (repo-wide)
    if 'def validate_repo' in content or 'validate_mode_coverage' in content:
        return 'no_arg'  # No file argument

    # Default to single-argument validators
    return 'single_arg'  # Standard single-file validator

def extract_artifact_id_from_fixture(fixture_path):
    """Extract artifact_id from fixture YAML metadata."""
    try:
        with open(fixture_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for artifact_id in YAML blocks
        yaml_blocks = re.findall(r'```yaml\s+(.*?)\s+```', content, re.DOTALL)
        for block in yaml_blocks:
            try:
                data = yaml.safe_load(block)
                if isinstance(data, dict) and 'artifact_id' in data:
                    return data['artifact_id']
            except:
                pass

        # Fallback: use default artifact ID based on validator type
        return None
    except:
        return None

def run_validator(validator_path, fixture_path, repo_root=".", extra_args=None):
    """Runs a validator script against a fixture with appropriate arguments."""
    validator_name = os.path.basename(validator_path).replace(".py", "")
    sig = detect_validator_signature(validator_path)

    cmd = [sys.executable, validator_path]

    # Handle different validator signatures
    if sig == 'no_arg':
        # No-argument validators - just run with --repo-root
        cmd.extend(["--repo-root", repo_root])
    elif sig == 'two_arg':
        # Two-argument validators (artifact_id + artifact_path)
        artifact_id = extract_artifact_id_from_fixture(fixture_path)
        if not artifact_id:
            # Fallback: use validator name as artifact ID
            artifact_id = validator_name.replace('validate-', '')
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(artifact_id)
        cmd.append(fixture_path)
        cmd.extend(["--repo-root", repo_root])
    else:
        # Single-argument validators (standard)
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(fixture_path)
        cmd.extend(["--repo-root", repo_root])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
    return result.returncode == 0, result.stdout + result.stderr

def test_fixture(validator_script, fixture_path):
    """Tests a single fixture and returns a result dict."""
    meta = parse_frontmatter(fixture_path)
    
    # Default based on path if not in frontmatter
    path_normalized = fixture_path.replace('\\', '/')
    default_case = 'negative' if '/invalid/' in path_normalized else 'positive'
    validator_case = meta.get('validator_case', default_case)
    expected_error = meta.get('expected_error_contains')
    validator_args = meta.get('validator_args', [])
    
    passed_exec, output = run_validator(validator_script, fixture_path, extra_args=validator_args)
    
    result = {
        "validator": os.path.basename(validator_script),
        "fixture": fixture_path,
        "case": validator_case,
        "expected_pass": (validator_case == 'positive'),
        "actual_pass": passed_exec,
        "matched_error": False,
        "status": "FAIL",
        "detail": ""
    }
    
    if validator_case == 'positive':
        if passed_exec:
            result["status"] = "PASS"
        else:
            result["detail"] = "Unexpected validation failure."
    else:
        # Negative case
        if passed_exec:
            result["detail"] = "Expected failure but validator PASSED."
        else:
            if not expected_error:
                result["detail"] = "Negative fixture missing 'expected_error_contains' assertion."
            elif expected_error in output:
                result["status"] = "PASS"
                result["matched_error"] = True
            else:
                result["detail"] = f"Failed for wrong reason. Expected substring: '{expected_error}'"
                
    result["output_snippet"] = output.strip().replace('\n', ' ')[:100]
    result["full_output"] = output
    return result

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    parser = argparse.ArgumentParser(description="Validator Verification Suite")
    parser.add_argument("--log-dir", help="Directory to save TEST-RUN-LOG.md")
    parser.add_argument("--fixtures-dir", default="tests/fixtures", help="Base directory for fixtures")
    args = parser.parse_args()

    fixtures_base = args.fixtures_dir
    regressions_path = os.path.join(fixtures_base, "REGRESSIONS.yaml")
    
    results = []
    
    # 0. Discover all validators in scripts/
    all_validator_scripts = [f for f in os.listdir("scripts") if f.startswith("validate-") and f.endswith(".py")]
    excluded_validators = []
    
    if os.path.exists(regressions_path):
        with open(regressions_path, 'r') as f:
            reg_data = yaml.safe_load(f) or {}
            excluded_data = reg_data.get('excluded_validators', [])
            excluded_validators = [e['validator'] if isinstance(e, dict) else e for e in excluded_data]

    coverage_failures = []
    for script in all_validator_scripts:
        base_name = script.replace(".py", "")
        if base_name in excluded_validators:
            continue
        
        fixture_dir = os.path.join(fixtures_base, base_name)
        if not os.path.exists(fixture_dir) or not os.path.isdir(fixture_dir):
            coverage_failures.append(script)

    # 1. Discover validators in fixtures dir
    if os.path.exists(fixtures_base):
        for item in os.listdir(fixtures_base):
            validator_dir = os.path.join(fixtures_base, item)
            if os.path.isdir(validator_dir):
                # Map dir name to script path (e.g. validate-brief -> scripts/validate-brief.py)
                script_path = os.path.join("scripts", f"{item}.py")
                if not os.path.exists(script_path):
                    continue
                
                # Scan valid/invalid subdirs
                for subtype in ['valid', 'invalid']:
                    subtype_dir = os.path.join(validator_dir, subtype)
                    if os.path.exists(subtype_dir):
                        for f in os.listdir(subtype_dir):
                            if f.endswith(".md"):
                                path = os.path.join(subtype_dir, f)
                                results.append(test_fixture(script_path, path))

    # 2. Check REGRESSIONS.yaml requirements
    required_missing = []
    if os.path.exists(regressions_path):
        with open(regressions_path, 'r') as f:
            reg_data = yaml.safe_load(f)
            required = reg_data.get('required_cases', [])
            for req in required:
                fix_path = req.get('fixture')
                # Check if this fixture was already run
                if not any(r['fixture'].replace('\\', '/') == fix_path.replace('\\', '/') for r in results):
                    if os.path.exists(fix_path):
                        script_path = os.path.join("scripts", f"{req['validator']}.py")
                        results.append(test_fixture(script_path, fix_path))
                    else:
                        required_missing.append(req)

    # 3. Generate Report
    success_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = len(results) - success_count + len(required_missing) + len(coverage_failures)
    
    report_lines = [
        "# Validator Verification Suite Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        f"- Total Cases: {len(results)}",
        f"- Passed: {success_count} ✅",
        f"- Failed: {fail_count} ❌",
        f"- Missing Required Regressions: {len(required_missing)}",
        f"- Coverage Failures: {len(coverage_failures)}",
        "",
        "## Details",
        "| Validator | Fixture | Case | Result | Detail |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for r in results:
        status_icon = "✅ PASS" if r["status"] == "PASS" else "❌ FAIL"
        report_lines.append(f"| `{r['validator']}` | `{os.path.basename(r['fixture'])}` | {r['case']} | {status_icon} | {r['detail']} |")
    
    for m in required_missing:
        report_lines.append(f"| `{m['validator']}` | `{m['fixture']}` | N/A | ❌ MISSING | REQUIRED REGRESSION NOT FOUND |")
    
    for c in coverage_failures:
        report_lines.append(f"| `{c}` | N/A | N/A | ❌ [CRITICAL] | VALIDATOR HAS NO FIXTURE DIRECTORY |")

    if fail_count > 0:
        report_lines.append("\n## Failure Breakdowns")
        for r in [res for res in results if res["status"] == "FAIL"]:
            report_lines.append(f"\n### {r['validator']} / {os.path.basename(r['fixture'])}")
            report_lines.append(f"- **Expected**: {'Pass' if r['expected_pass'] else 'Fail (containing: ' + r['detail'] + ')'}")
            report_lines.append("- **Actual Output**:")
            report_lines.append("```text")
            report_lines.append(r["full_output"])
            report_lines.append("```")

    report_content = "\n".join(report_lines)
    print(report_content)

    if args.log_dir:
        os.makedirs(args.log_dir, exist_ok=True)
        with open(os.path.join(args.log_dir, "TEST-RUN-LOG.md"), 'w', encoding='utf-8') as f:
            f.write(report_content)

    sys.exit(0 if fail_count == 0 else 1)

if __name__ == "__main__":
    main()
