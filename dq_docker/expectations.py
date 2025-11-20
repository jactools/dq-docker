import great_expectations as gx
from pathlib import Path
from typing import Optional, Union, Any
from .data_contract import suite_to_contract, contract_to_suite


def build_expectation_suite(
    name: str,
    *,
    contract_path: Optional[Union[str, Path]] = None,
    export_contract: bool = False,
    contract_out_path: Optional[Union[str, Path]] = None,
) -> Any:
    """Return an ExpectationSuite loaded from an ODCS contract.

    This project requires expectation suites to be expressed as Open Data
    Contract (ODCS) JSON files. If `contract_path` is not provided a
    `ValueError` is raised to make the requirement explicit.
    """
    if not contract_path:
        raise ValueError("contract_path is required: provide a path to an ODCS contract JSON file")

    suite = contract_to_suite(contract_path)
    # Ensure the suite has the requested name (optional override)
    if getattr(suite, "expectation_suite_name", None) != name:
        try:
            suite.expectation_suite_name = name
        except Exception:
            suite.meta = suite.meta or {}
            suite.meta.setdefault("name_override", name)

    # Optionally re-export the loaded suite as a normalized contract
    if export_contract:
        out = contract_out_path or (Path("contracts") / f"{name}.contract.json")
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        suite_to_contract(suite, name=name, description="Exported expectation contract", issuer=None, output_path=out)

    return suite
