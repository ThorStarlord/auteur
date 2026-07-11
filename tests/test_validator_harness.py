import importlib.util
from pathlib import Path


def _harness():
    path = Path(__file__).parents[1] / "scripts" / "test-validators.py"
    spec = importlib.util.spec_from_file_location("validator_harness", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validator_signature_mapping_uses_cli_contracts():
    harness = _harness()
    root = Path(__file__).parents[1] / "scripts"
    assert harness.detect_validator_signature(root / "validate-output.py") == "two_arg"
    assert harness.detect_validator_signature(root / "validate-plan.py") == "single_arg"
    assert harness.detect_validator_signature(root / "validate-workflow-design.py") == "single_no_repo_root"
