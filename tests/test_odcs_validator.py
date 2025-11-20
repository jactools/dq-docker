import json
from pathlib import Path

import pytest

from dq_docker.odcs_validator import validate_contract


def test_validate_existing_contract():
    data = validate_contract(Path("contracts") / "customers_2019.contract.json")
    assert data["name"] == "customers_2019"


def test_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{ this is not json }")
    with pytest.raises(ValueError):
        validate_contract(p)


def test_missing_columns(tmp_path):
    p = tmp_path / "no_columns.json"
    p.write_text(json.dumps({"contract_version": "1.0", "name": "x", "issued_at": "2025-11-20T00:00:00Z", "expectations": []}))
    with pytest.raises(ValueError):
        validate_contract(p)
