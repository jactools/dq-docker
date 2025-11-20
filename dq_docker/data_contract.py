from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import json

from .odcs_validator import validate_contract
from typing import Any


CONTRACT_MAJOR = 1
CONTRACT_MINOR = 0


def _expectation_to_dict(expectation: Dict[str, Any]) -> Dict[str, Any]:
    # Extract a compact, stable representation of a GE expectation
    return {
        "expectation_type": expectation.get("expectation_type"),
        "kwargs": expectation.get("kwargs", {}),
        "meta": expectation.get("meta", {}),
    }


def suite_to_contract(suite: Any, *,
                      name: str | None = None,
                      description: str | None = None,
                      issuer: str | None = None,
                      output_path: str | Path | None = None) -> Dict[str, Any]:
    """Serialize a Great Expectations ExpectationSuite into a simple
    Open Data Contract JSON structure.

    The contract format is intentionally small and portable:
    {
      "contract_version": "1.0",
      "name": "...",
      "description": "...",
      "issued_at": "ISO8601",
      "issuer": "...",
      "expectations": [ { expectation_type, kwargs, meta }, ... ]
    }

    If `output_path` is provided the JSON file is written to disk and the
    resulting dict is returned.
    """
    suite_meta = getattr(suite, "meta", {}) or {}
    data: Dict[str, Any] = {
        "contract_version": f"{CONTRACT_MAJOR}.{CONTRACT_MINOR}",
        "name": name or getattr(suite, "expectation_suite_name", None) or "unnamed",
        "description": description or suite_meta.get("notes", ""),
        "issued_at": datetime.utcnow().isoformat() + "Z",
        "issuer": issuer or suite_meta.get("owner", None),
        "expectations": [_expectation_to_dict(e) for e in suite.expectations or []],
    }

    if output_path:
        p = Path(output_path)
        p.write_text(json.dumps(data, indent=2))

    return data


def contract_to_suite(contract_path: str | Path):
    """Load a contract JSON file and convert it to a Great Expectations ExpectationSuite.

    Note: This function imports `great_expectations` at runtime so the module
    does not require GE to be installed for non-runtime operations (tests,
    docs generation, etc.).
    """
    import great_expectations as gx
    """Load a contract JSON file and convert it to a Great Expectations ExpectationSuite.

    This function first validates the contract using the ODCS validator, then
    synthesizes datatype expectations from the `columns` section and finally
    appends any explicit expectations supplied in the contract.
    """
    data = validate_contract(contract_path)

    p = Path(contract_path)
    name = data.get("name") or f"contract-{p.stem}"
    suite = gx.ExpectationSuite(name=name)

    # First, create datatype validation expectations from the `columns` section
    for col in data.get("columns", []):
        col_name = col.get("name")
        ctype = col.get("type")
        fmt = col.get("format")
        nullable = bool(col.get("nullable", False))

        if not col_name or not ctype:
            continue

        # Add type validation expectations using regex or set membership
        if ctype == "integer":
            regex = r"^\d+$"
            expectation = {
                "expectation_type": "ExpectColumnValuesToMatchRegex",
                "kwargs": {"column": col_name, "regex": regex},
                "meta": {"note": "Column should contain integer values"},
            }
            suite.add_expectation(expectation)
        elif ctype == "number":
            regex = r"^-?\d+(?:\.\d+)?$"
            expectation = {
                "expectation_type": "ExpectColumnValuesToMatchRegex",
                "kwargs": {"column": col_name, "regex": regex},
                "meta": {"note": "Column should contain numeric values"},
            }
            suite.add_expectation(expectation)
        elif ctype == "boolean":
            # Allow common boolean representations in CSVs
            regex = r"^(?:TRUE|FALSE|True|False|true|false|0|1)$"
            expectation = {
                "expectation_type": "ExpectColumnValuesToMatchRegex",
                "kwargs": {"column": col_name, "regex": regex},
                "meta": {"note": "Column should contain boolean-like values"},
            }
            suite.add_expectation(expectation)
        elif ctype == "string" and fmt == "date":
            # Simple ISO date YYYY-MM-DD; allow empty if nullable
            if nullable:
                regex = r"^(?:\d{4}-\d{2}-\d{2})?$"
            else:
                regex = r"^\d{4}-\d{2}-\d{2}$"
            expectation = {
                "expectation_type": "ExpectColumnValuesToMatchRegex",
                "kwargs": {"column": col_name, "regex": regex},
                "meta": {"note": "Column should contain ISO dates (YYYY-MM-DD)"},
            }
            suite.add_expectation(expectation)

    # Then add any explicit expectations declared in the contract
    for e in data.get("expectations", []):
        etype = e.get("expectation_type")
        kwargs = e.get("kwargs", {})
        meta = e.get("meta", {})

        # Build minimal expectation dict accepted by GE
        expectation = {
            "expectation_type": etype,
            "kwargs": kwargs,
            "meta": meta,
        }
        suite.add_expectation(expectation)

    # Attach contract metadata into suite.meta for provenance.
    # Use getattr/setattr and try/except so fake or minimal suite objects
    # used in tests (which may not have a `meta` attribute) don't raise.
    try:
        meta = getattr(suite, "meta", None)
        if meta is None:
            setattr(suite, "meta", {})
            meta = getattr(suite, "meta")

        if isinstance(meta, dict):
            meta.setdefault("contract_source", str(p))
            meta.setdefault("contract_version", data.get("contract_version"))
    except Exception:
        # Fallback: attempt to set the attribute directly; if that fails,
        # give up silently since provenance is not critical to suite behavior.
        try:
            setattr(suite, "meta", {"contract_source": str(p), "contract_version": data.get("contract_version")})
        except Exception:
            pass

    return suite
