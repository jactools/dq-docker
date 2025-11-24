import shutil
import os
import textwrap
from pathlib import Path

import dq_docker.run_adls_checkpoint as runner


def _write_gx_config(gx_path: Path, base_directory: str):
    gx_path.parent.mkdir(parents=True, exist_ok=True)
    content = textwrap.dedent(f"""
    config_version: 4.0
    config_variables_file_path: uncommitted/config_variables.yml
    plugins_directory: plugins/

    stores:
      expectations_store:
        class_name: ExpectationsStore
        store_backend:
          class_name: TupleFilesystemStoreBackend
          base_directory: expectations/

      validation_results_store:
        class_name: ValidationResultsStore
        store_backend:
          class_name: TupleFilesystemStoreBackend
          base_directory: uncommitted/validations/

      checkpoint_store:
        class_name: CheckpointStore
        store_backend:
          class_name: TupleFilesystemStoreBackend
          suppress_store_backend_id: true
          base_directory: checkpoints/

      validation_definition_store:
        class_name: ValidationDefinitionStore
        store_backend:
          class_name: TupleFilesystemStoreBackend
          base_directory: validation_definitions/

    expectations_store_name: expectations_store
    validation_results_store_name: validation_results_store
    checkpoint_store_name: checkpoint_store

    data_docs_sites:
      local_site:
        class_name: SiteBuilder
        store_backend:
          class_name: TupleFilesystemStoreBackend
          base_directory: uncommitted/data_docs/local_site/
        site_index_builder:
          class_name: DefaultSiteIndexBuilder

    fluent_datasources:
      ds_sample_data:
        type: pandas_filesystem
        assets:
          sample_customers:
            type: csv
        base_directory: {base_directory}

    analytics_enabled: false
    """)
    gx_path.write_text(content)


def test_end_to_end_checkpoint_smoke(tmp_path, caplog):
  # Ensure a real Great Expectations installation is available; if tests
  # earlier in the suite installed a fake `great_expectations` module,
  # skip this integration-style test since it requires the real package.
  try:
    import importlib

    if "great_expectations" in importlib.sys.modules:
      # Try to import the checkpoint action to validate a real install
      try:
        from great_expectations.checkpoint import UpdateDataDocsAction  # type: ignore
      except Exception:
        import pytest

        pytest.skip("Real great_expectations package not available in test environment; skipping end-to-end smoke test")
    else:
      # Attempt a normal import
      from great_expectations.checkpoint import UpdateDataDocsAction  # type: ignore
  except Exception:
    import pytest

    pytest.skip("Great Expectations not installed; skipping end-to-end smoke test")

    # Prepare a temporary project root with a minimal GX project, sample data and contract
    project_root = tmp_path / "proj"
    sample_dir = project_root / "sample_data" / "customers"
    gx_dir = project_root / "gx"
    contracts_dir = project_root / "contracts"

    sample_dir.mkdir(parents=True)
    contracts_dir.mkdir(parents=True)

    # Copy sample CSV from repo into temp sample dir
    repo_csv = Path.cwd() / "gx" / "sample_data" / "customers" / "customers_2019.csv"
    assert repo_csv.exists(), f"Expected sample CSV at {repo_csv}"
    shutil.copy(repo_csv, sample_dir / "customers_2019.csv")

    # Copy contract file
    repo_contract = Path.cwd() / "contracts" / "customers.contract.json"
    assert repo_contract.exists(), f"Expected contract at {repo_contract}"
    shutil.copy(repo_contract, contracts_dir / "customers.contract.json")

    # Write minimal gx config pointing at our temp sample dir
    gx_config_path = gx_dir / "great_expectations.yml"
    _write_gx_config(gx_config_path, str(sample_dir))

    # Monkeypatch runner module-level config values to use temp project
    runner.PROJECT_ROOT = str(project_root)
    runner.SOURCE_FOLDER = str(sample_dir)
    runner.DATA_SOURCE_NAME = "ds_sample_data"
    runner.ASSET_NAME = "sample_customers"
    runner.BATCH_DEFINITION_NAME = "customers_2019.csv"
    runner.BATCH_DEFINITION_PATH = "customers_2019.csv"
    runner.EXPECTATION_SUITE_NAME = "adls_data_quality_suite"
    runner.DEFINITION_NAME = "adls_checkpoint"
    runner.DATA_DOCS_SITE_NAMES = ["local_site"]

    # Run the orchestration; this will create datasources, run validation and build Data Docs
    runner.main()

    # Ensure data docs index exists in the temp project
    index_path = gx_dir / "uncommitted" / "data_docs" / "local_site" / "index.html"
    assert index_path.exists(), f"Data Docs index not found at {index_path}"
