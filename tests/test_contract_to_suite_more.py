import importlib
import json
import sys
import types
from pathlib import Path

from dq_docker import data_contract as dc


def _install_fake_gx():
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
    return fake_gx


def _teardown_fake_gx():
    try:
        del sys.modules["great_expectations"]
    except KeyError:
        pass
    importlib.reload(dc)


def test_nullable_date_synthesized_and_meta(tmp_path):
    contract = {
        "contract_version": "1.0",
        "name": "nullable_dates",
        "issued_at": "2025-11-20T00:00:00Z",
        "columns": [
            {"name": "event_date", "type": "string", "format": "date", "nullable": True}
        ],
        "expectations": [],
    }

    p = tmp_path / "c.json"
    p.write_text(json.dumps(contract))

    _install_fake_gx()
    importlib.reload(dc)

    suite = dc.contract_to_suite(p)

    # find regex expectation for event_date
    regex_ex = None
    for e in suite.expectations:
        if e.get("kwargs", {}).get("column") == "event_date":
            if e.get("expectation_type") == "ExpectColumnValuesToMatchRegex":
                regex_ex = e
                break

    assert regex_ex is not None
    regex = regex_ex["kwargs"]["regex"]
    # nullable date regex includes optional quantifier
    assert "?" in regex

    # meta should include provenance
    meta = getattr(suite, "meta", {}) or {}
    assert meta.get("contract_version") == "1.0"
    # contract_source should reference the contract file we wrote
    assert p.name in str(meta.get("contract_source", ""))

    _teardown_fake_gx()


def test_explicit_expectations_appended(tmp_path):
    contract = {
        "contract_version": "1.0",
        "name": "explicit_append",
        "issued_at": "2025-11-20T00:00:00Z",
        "columns": [{"name": "id", "type": "integer"}],
        "expectations": [
            {
                "expectation_type": "ExpectColumnValuesToBeBetween",
                "kwargs": {"column": "id", "min_value": 0, "max_value": 100},
                "meta": {"note": "range check"},
            }
        ],
    }

    p = tmp_path / "c2.json"
    p.write_text(json.dumps(contract))

    _install_fake_gx()
    importlib.reload(dc)

    suite = dc.contract_to_suite(p)

    # synthesized integer regex expectation should exist
    synth = [e for e in suite.expectations if e.get("expectation_type") == "ExpectColumnValuesToMatchRegex"]
    assert len(synth) == 1

    # explicit expectation should be appended as the last expectation
    last = suite.expectations[-1]
    assert last["expectation_type"] == "ExpectColumnValuesToBeBetween"
    assert last["kwargs"]["min_value"] == 0
    assert last["meta"]["note"] == "range check"

    _teardown_fake_gx()
