import json
import pytest

from dq_docker.data_contract import contract_to_suite


def test_contract_to_suite_returns_expectation_configurations(tmp_path):
    # Skip test if Great Expectations is not installed in the environment
    pytest.importorskip("great_expectations")
    try:
        from great_expectations.core.expectation_configuration import ExpectationConfiguration
    except Exception:
        from great_expectations.expectations.expectation_configuration import ExpectationConfiguration

    contract = {
        "contract_version": "1.0",
        "name": "test_contract",
        "issued_at": "2020-01-01T00:00:00Z",
        "issuer": "tester",
        "columns": [
            {"name": "col1", "type": "integer", "nullable": False}
        ],
        "expectations": [
            {"expectation_type": "expect_column_values_to_not_be_null", "kwargs": {"column": "col1"}, "meta": {}}
        ],
    }

    p = tmp_path / "test.contract.json"
    p.write_text(json.dumps(contract))

    suite = contract_to_suite(str(p))

    assert hasattr(suite, "expectations")
    assert len(suite.expectations) >= 1

    for e in suite.expectations:
        assert isinstance(e, ExpectationConfiguration)
