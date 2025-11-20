import importlib
import json
import sys
import types
from pathlib import Path

from dq_docker import data_contract as dc


def test_contract_to_suite_synthesizes_datatypes(tmp_path):
    # Create a minimal contract with columns that require synthesized checks
    contract = {
        "contract_version": "1.0",
        "name": "test_contract",
        "issued_at": "2025-11-20T00:00:00Z",
        "columns": [
            {"name": "id", "type": "integer"},
            {"name": "value", "type": "number"},
            {"name": "flag", "type": "boolean"},
            {"name": "event_date", "type": "string", "format": "date"},
        ],
        "expectations": [
            {"expectation_type": "ExpectColumnValuesToNotBeNull", "kwargs": {"column": "id"}, "meta": {}}
        ],
    }

    p = tmp_path / "c.json"
    p.write_text(json.dumps(contract))

    # Inject a fake great_expectations module so contract_to_suite can run without GE
    fake_gx = types.ModuleType("great_expectations")

    class ExpectationSuite:
        def __init__(self, name=None):
            self.expectation_suite_name = name
            self.expectations = []
            self.meta = {}

        def add_expectation(self, expectation):
            self.expectations.append(expectation)

    fake_gx.ExpectationSuite = ExpectationSuite

    sys.modules["great_expectations"] = fake_gx

    # reload module to ensure it imports the fake GE in contract_to_suite
    importlib.reload(dc)

    suite = dc.contract_to_suite(p)

    # Expect 4 synthesized datatype expectations + 1 explicit = 5
    assert len(suite.expectations) == 5

    # Clean up
    del sys.modules["great_expectations"]
    importlib.reload(dc)
