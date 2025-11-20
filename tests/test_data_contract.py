from pathlib import Path
import json

from dq_docker.data_contract import suite_to_contract


class FakeSuite:
    def __init__(self):
        self.expectation_suite_name = "fake_suite"
        self.expectations = [
            {"expectation_type": "ExpectColumnValuesToNotBeNull", "kwargs": {"column": "id"}, "meta": {}},
        ]


def test_suite_to_contract_writes_file(tmp_path):
    suite = FakeSuite()
    out = tmp_path / "out.contract.json"
    data = suite_to_contract(suite, name="fake_suite", output_path=out)
    assert data["name"] == "fake_suite"
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert isinstance(loaded.get("expectations"), list)
