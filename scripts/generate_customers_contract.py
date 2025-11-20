#!/usr/bin/env python3
"""Generate an ODCS contract for the sample customers CSV using the
expectation builder in `dq_docker`.

This script is intended to be run from the repository root.
"""
from pathlib import Path
import sys

sys.path.insert(0, ".")

from dq_docker.config.adls_config import SOURCE_FOLDER, BATCH_DEFINITION_NAME, EXPECTATION_SUITE_NAME
from dq_docker.expectations import build_expectation_suite
import logging

from dq_docker.logs import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def main():
    # Build suite and export contract
    name = EXPECTATION_SUITE_NAME or f"suite_{BATCH_DEFINITION_NAME}"
    out_dir = Path("contracts")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{Path(BATCH_DEFINITION_NAME).stem}.contract.json"

    suite = build_expectation_suite(name, export_contract=True, contract_path=out_path)

    logger.info("Wrote contract for '%s' -> %s", BATCH_DEFINITION_NAME, out_path)


if __name__ == "__main__":
    main()
