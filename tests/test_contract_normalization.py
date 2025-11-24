import json
import importlib
import sys
import types
import pytest

import dq_docker.data_contract as dc


def _install_fake_gx():
    fake_gx = types.ModuleType("great_expectations")

    class ExpectationSuite:
        def __init__(self, name=None, expectations=None):
            self.expectation_suite_name = name
            self.expectations = expectations or []
            self.meta = {}

        def add_expectation(self, expectation):
            self.expectations.append(expectation)

    fake_gx.ExpectationSuite = ExpectationSuite
    sys.modules["great_expectations"] = fake_gx
    return fake_gx


def _teardown_fake_gx():
    try:
        del sys.modules["great_expectations"]
    except KeyError:
        pass
    importlib.reload(dc)


def test_pascalcase_expectation_names_normalized(tmp_path):
    contract = {
        "contract_version": "1.0",
        "name": "normalize_test",
        "issued_at": "2025-11-24T00:00:00Z",
        "issuer": "tester",
        "columns": [{"name": "col1", "type": "integer"}],
        "expectations": [
            {"expectation_type": "ExpectColumnValuesToNotBeNull", "kwargs": {"column": "col1"}, "meta": {}},
            {"expectation_type": "ExpectColumnValuesToBeBetween", "kwargs": {"column": "col1", "min_value": 0, "max_value": 10}, "meta": {}},
        ],
    }

    p = tmp_path / "normalize.contract.json"
    p.write_text(json.dumps(contract))

    _install_fake_gx()
    importlib.reload(dc)

    suite = dc.contract_to_suite(str(p))

    # synthesized integer regex expectation should exist (from columns)
    synth = [e for e in suite.expectations if isinstance(e, dict) and e.get("type") == "expect_column_values_to_match_regex"]
    assert len(synth) == 1

    # explicit expectations should have been normalized and appended
    # The fake ExpectationSuite constructor receives `expectations` as provided
    # in the call path; those will be dicts with a 'type' key after normalization.
    types_present = {e.get("type") for e in suite.expectations if isinstance(e, dict)}
    assert "expect_column_values_to_not_be_null" in types_present
    assert "expect_column_values_to_be_between" in types_present

    _teardown_fake_gx()
