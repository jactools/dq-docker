from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json


ALLOWED_TYPES = {"string", "integer", "number", "boolean"}
ALLOWED_FORMATS = {"date", "date-time"}


def validate_contract(contract_path: str | Path) -> Dict[str, Any]:
    """Validate a minimal ODCS contract file and return its parsed JSON.

    Raises ValueError with a helpful message if validation fails.
    This validator is intentionally small and dependency-free so it can run
    in CI runners without extra packages.
    """
    p = Path(contract_path)
    if not p.exists():
        raise ValueError(f"Contract file not found: {p}")

    try:
        data = json.loads(p.read_text())
    except Exception as exc:
        raise ValueError(f"Invalid JSON in contract file {p}: {exc}")

    errors: List[str] = []

    # Top-level checks
    if not isinstance(data.get("contract_version"), str):
        errors.append("'contract_version' must be a string")
    if not isinstance(data.get("name"), str):
        errors.append("'name' must be a string")
    if not isinstance(data.get("issued_at"), str):
        errors.append("'issued_at' must be an ISO datetime string")

    # Columns
    cols = data.get("columns")
    if cols is None:
        errors.append("'columns' is required and must be a list of column definitions")
    elif not isinstance(cols, list):
        errors.append("'columns' must be a list")
    else:
        for i, c in enumerate(cols):
            if not isinstance(c, dict):
                errors.append(f"columns[{i}] must be an object")
                continue
            name = c.get("name")
            ctype = c.get("type")
            if not isinstance(name, str) or not name:
                errors.append(f"columns[{i}].name must be a non-empty string")
            if ctype not in ALLOWED_TYPES:
                errors.append(f"columns[{i}].type must be one of {sorted(ALLOWED_TYPES)}")
            fmt = c.get("format")
            if fmt is not None:
                if not isinstance(fmt, str) or fmt not in ALLOWED_FORMATS:
                    errors.append(f"columns[{i}].format must be one of {sorted(ALLOWED_FORMATS)} when provided")
            if "nullable" in c and not isinstance(c.get("nullable"), bool):
                errors.append(f"columns[{i}].nullable must be a boolean if present")

    # Expectations
    exps = data.get("expectations")
    if exps is None:
        errors.append("'expectations' is required and must be a list of expectation objects")
    elif not isinstance(exps, list):
        errors.append("'expectations' must be a list")
    else:
        for i, e in enumerate(exps):
            if not isinstance(e, dict):
                errors.append(f"expectations[{i}] must be an object")
                continue
            if not isinstance(e.get("expectation_type"), str):
                errors.append(f"expectations[{i}].expectation_type must be a string")
            if not isinstance(e.get("kwargs"), dict):
                errors.append(f"expectations[{i}].kwargs must be an object/dict")

    if errors:
        raise ValueError("Contract validation errors:\n" + "\n".join(errors))

    return data
