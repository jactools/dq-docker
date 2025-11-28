from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import json

from .odcs_validator import validate_contract
from typing import Any
from types import SimpleNamespace
from uuid import uuid4


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


def _import_gx_for_suite():
    # Import GE lazily to avoid importing the package at module import time
    import importlib

    return importlib.import_module("great_expectations")


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

    # Collect expectation configurations as plain dicts (or
    # ExpectationConfiguration-compatible objects) and construct the
    # ExpectationSuite with them. Constructing the suite this way avoids
    # calling `ExpectationSuite.add_expectation` which can attempt to access
    # a persisted store and a DataContext during runtime.
    expectation_configs = []
    legacy_expectation_configs = []

    def _to_legacy_name(type_str: str | None) -> str | None:
        if not type_str:
            return None
        # convert snake_case to PascalCase Expectation names used in older tests
        parts = type_str.split("_")
        return "".join(p.title() for p in parts)

    def _to_snake_name(type_str: str | None) -> str | None:
        """Convert CamelCase / PascalCase expectation names to snake_case.

        GE's registry uses snake_case expectation_type names (e.g.
        `expect_column_values_to_not_be_null`). Contracts may contain
        legacy PascalCase names (e.g. `ExpectColumnValuesToNotBeNull`).
        Normalize those to snake_case before passing to GE constructors.
        """
        if not type_str:
            return None
        s = type_str
        # If it already looks like snake_case, return as-is
        if "_" in s or s.lower() == s:
            return s
        import re

        s1 = re.sub('(.)([A-Z][a-z]+)', r"\1_\2", s)
        s2 = re.sub('([a-z0-9])([A-Z])', r"\1_\2", s1)
        return s2.replace("-", "_").lower()

    # Helper: build an ExpectationConfiguration-like object from a dict.
    def _make_expectation_config(expectation_dict):
        """Try several import paths for GE's ExpectationConfiguration.

        If none are available, return a minimal object that provides an
        `id` attribute and the usual fields so `ExpectationSuite.add_expectation`
        can operate without raising AttributeError.
        """
        # Try common import locations
        ec_cls = None
        try:
            from great_expectations.core.expectation_configuration import ExpectationConfiguration  # type: ignore
            ec_cls = ExpectationConfiguration
        except Exception:
            try:
                from great_expectations.expectations.expectation import ExpectationConfiguration  # type: ignore
                ec_cls = ExpectationConfiguration
            except Exception:
                ec_cls = getattr(__import__("great_expectations"), "ExpectationConfiguration", None)

        if ec_cls:
            try:
                # Support both 'type' and legacy 'expectation_type' keys.
                etype = expectation_dict.get("type") or expectation_dict.get("expectation_type")
                ec = ec_cls(type=etype, kwargs=expectation_dict.get("kwargs", {}), meta=expectation_dict.get("meta", {}))
                # Ensure the expectation isn't tied to another suite (some GE
                # implementations may set an internal suite/id); clear id so it
                # can be added safely to the target suite.
                try:
                    setattr(ec, "id", None)
                except Exception:
                    pass
                try:
                    if hasattr(ec, "expectation_suite"):
                        setattr(ec, "expectation_suite", None)
                except Exception:
                    pass
                return ec
            except Exception:
                # fall through to minimal object
                pass

        # Minimal fallback object with an `id` attribute
        fallback = SimpleNamespace(
            expectation_type=expectation_dict.get("expectation_type"),
            kwargs=expectation_dict.get("kwargs", {}),
            meta=expectation_dict.get("meta", {}),
            id=f"{expectation_dict.get('expectation_type')}-{uuid4()}",
        )
        return fallback

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
            expectation = {"type": "expect_column_values_to_match_regex", "kwargs": {"column": col_name, "regex": regex}, "meta": {"note": "Column should contain integer values"}}
            expectation_configs.append(expectation)
            legacy_expectation_configs.append({"expectation_type": _to_legacy_name(expectation["type"]), "kwargs": expectation["kwargs"], "meta": expectation["meta"]})
        elif ctype == "number":
            regex = r"^-?\d+(?:\.\d+)?$"
            expectation = {"type": "expect_column_values_to_match_regex", "kwargs": {"column": col_name, "regex": regex}, "meta": {"note": "Column should contain numeric values"}}
            expectation_configs.append(expectation)
            legacy_expectation_configs.append({"expectation_type": _to_legacy_name(expectation["type"]), "kwargs": expectation["kwargs"], "meta": expectation["meta"]})
        elif ctype == "boolean":
            # Allow common boolean representations in CSVs
            regex = r"^(?:TRUE|FALSE|True|False|true|false|0|1)$"
            expectation = {"type": "expect_column_values_to_match_regex", "kwargs": {"column": col_name, "regex": regex}, "meta": {"note": "Column should contain boolean-like values"}}
            expectation_configs.append(expectation)
            legacy_expectation_configs.append({"expectation_type": _to_legacy_name(expectation["type"]), "kwargs": expectation["kwargs"], "meta": expectation["meta"]})
        elif ctype == "string" and fmt == "date":
            # Simple ISO date YYYY-MM-DD; allow empty if nullable
            if nullable:
                regex = r"^(?:\d{4}-\d{2}-\d{2})?$"
            else:
                regex = r"^\d{4}-\d{2}-\d{2}$"
            expectation = {"type": "expect_column_values_to_match_regex", "kwargs": {"column": col_name, "regex": regex}, "meta": {"note": "Column should contain ISO dates (YYYY-MM-DD)"}}
            expectation_configs.append(expectation)
            legacy_expectation_configs.append({"expectation_type": _to_legacy_name(expectation["type"]), "kwargs": expectation["kwargs"], "meta": expectation["meta"]})

    # Then add any explicit expectations declared in the contract
    for e in data.get("expectations", []):
        etype = e.get("expectation_type")
        kwargs = e.get("kwargs", {})
        meta = e.get("meta", {})

        # Build minimal expectation dict accepted by GE and convert to
        # ExpectationConfiguration when available so GE's suite.add_expectation
        # (which may expect an object with an `id` attribute) works reliably.
        expectation = {
            "expectation_type": etype,
            "kwargs": kwargs,
            "meta": meta,
        }
        # Explicit expectations from the contract: map `expectation_type` -> `type`
        # to match GE's constructor signature. Normalize legacy PascalCase
        # expectation names to GE snake_case names so GE can find the
        # registered implementation.
        normalized = _to_snake_name(etype)
        cfg = {"type": (normalized or None), "kwargs": kwargs, "meta": meta}
        expectation_configs.append(cfg)
        legacy_expectation_configs.append({"expectation_type": (etype or None), "kwargs": kwargs, "meta": meta})

    # Construct the ExpectationSuite with the collected expectation configs.
    try:
        # Newer GE versions accept `expectations` in the constructor.
        suite = gx.ExpectationSuite(name=name, expectations=expectation_configs)
    except TypeError:
        # Fallback for lightweight/fake GE modules used in tests: construct
        # an empty suite and append expectations using add_expectation.
        suite = gx.ExpectationSuite(name=name)
        for cfg in legacy_expectation_configs:
            try:
                suite.add_expectation(cfg)
            except Exception:
                # If add_expectation expects an Expectation object, try to
                # construct one via the suite internals or fallback helper.
                try:
                    exp = suite._process_expectation(cfg)
                    suite.add_expectation(exp)
                except Exception:
                    suite.add_expectation(_make_expectation_config(cfg))

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
