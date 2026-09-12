import pytest

from auteur.artifact_schema import require_supported_schema


def test_schema_contract_accepts_missing_or_current_version() -> None:
    assert require_supported_schema({}) == 1
    assert require_supported_schema({"schema_version": 1}) == 1


def test_schema_contract_rejects_future_versions() -> None:
    with pytest.raises(ValueError, match="unsupported schema_version"):
        require_supported_schema({"schema_version": 2})
