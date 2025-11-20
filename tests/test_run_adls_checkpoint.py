import importlib
import sys
import types
from pathlib import Path


def test_run_adls_checkpoint_monkeypatched(tmp_path, caplog):
    """Run `run_adls_checkpoint.main()` with a fake `great_expectations` so
    we can test the runtime flow without the real GE/ADLS dependencies.
    """
    # Build a minimal fake `great_expectations` module
    fake_gx = types.ModuleType("great_expectations")

    # Helper action class (used by runtime when building action list)
    class UpdateDataDocsAction:
        def __init__(self, name=None, site_names=None):
            self.name = name
            self.site_names = site_names

    # Minimal ValidationDefinition used by the runtime
    class ValidationDefinition:
        def __init__(self, name=None, data=None, suite=None):
            self.name = name
            self.data = data
            self.suite = suite

        def run(self):
            return {"success": True}

    # Minimal Checkpoint used by the runtime
    class Checkpoint:
        def __init__(self, name=None, validation_definitions=None, actions=None, result_format=None):
            self.name = name
            self.validation_definitions = validation_definitions
            self.actions = actions
            self.result_format = result_format

        def run(self):
            return {"success": True}

    # Minimal ExpectationSuite used by contract_to_suite/build_expectation_suite
    class ExpectationSuite:
        def __init__(self, name=None):
            self.expectation_suite_name = name
            self.expectations = []
            self.meta = {}

        def add_expectation(self, expectation):
            self.expectations.append(expectation)

    # Context and helpers
    class Batch:
        def head(self):
            return "head"

    class BatchDefinition:
        def __init__(self, name, path):
            self.name = name
            self.path = path

        def get_batch(self):
            return Batch()

    class FileCustomers:
        def add_batch_definition_path(self, name, path):
            return BatchDefinition(name, path)

    class DataSource:
        def add_csv_asset(self, name):
            return FileCustomers()

    class DataSourcesManager:
        def add_pandas_filesystem(self, name, base_directory):
            return DataSource()

    class Suites:
        def add(self, suite):
            # accept suite silently
            return None

    class ValidationDefs:
        def add(self, vd):
            return vd

    class Checkpoints:
        def add_or_update(self, checkpoint):
            return None

    class Context:
        def __init__(self):
            self._sites = []
            self.data_sources = DataSourcesManager()
            self.suites = Suites()
            self.validation_definitions = ValidationDefs()
            self.checkpoints = Checkpoints()

        def get_site_names(self):
            return list(self._sites)

        def add_data_docs_site(self, site_name, site_config):
            self._sites.append(site_name)

        def list_data_docs_sites(self):
            return self._sites

        def get_docs_sites_urls(self):
            return {"local_site": ["http://fake"]}

    # Expose objects on fake module
    fake_gx.UpdateDataDocsAction = UpdateDataDocsAction
    fake_gx.ValidationDefinition = ValidationDefinition
    fake_gx.Checkpoint = Checkpoint
    fake_gx.ExpectationSuite = ExpectationSuite
    fake_gx.get_context = lambda mode=None, project_root_dir=None: Context()

    # Also create a fake submodule `great_expectations.checkpoint` used by the
    # runtime top-level import.
    fake_checkpoint_mod = types.ModuleType("great_expectations.checkpoint")
    fake_checkpoint_mod.UpdateDataDocsAction = UpdateDataDocsAction

    sys.modules["great_expectations"] = fake_gx
    sys.modules["great_expectations.checkpoint"] = fake_checkpoint_mod

    # Import the runtime module after installing the fake GE
    import importlib as _importlib

    rac = _importlib.import_module("dq_docker.run_adls_checkpoint")

    # Prepare a fake source folder (the runtime does an os.listdir on it)
    (tmp_path / "customers_2019.csv").write_text("id,value\n1,10\n")
    # Point the runtime to the temporary source folder
    rac.SOURCE_FOLDER = str(tmp_path)
    # Also set PROJECT_ROOT so the runtime looks for contracts under tmp_path
    rac.PROJECT_ROOT = str(tmp_path)

    # Write a minimal valid contract at PROJECT_ROOT/contracts/customers_2019.contract.json
    contracts_dir = tmp_path / "contracts"
    contracts_dir.mkdir()
    contract = {
        "contract_version": "1.0",
        "name": "customers_2019",
        "issued_at": "2025-11-20T00:00:00Z",
        "columns": [{"name": "id", "type": "integer"}],
        "expectations": [{"expectation_type": "ExpectColumnValuesToNotBeNull", "kwargs": {"column": "id"}}],
    }
    import json as _json
    (contracts_dir / "customers_2019.contract.json").write_text(_json.dumps(contract))

    # Run main() — it should exercise the flow without raising
    caplog.set_level("INFO")
    rac.main()

    # Basic assertions on log output to ensure expected milestones were reached
    text = "\n".join(r.message for r in caplog.records)
    assert "Great Expectations Data Context is ready" in text
    assert "Validation succeeded" in text or "Checkpoint run success status" in text

    # Clean up fakes
    del sys.modules["great_expectations.checkpoint"]
    del sys.modules["great_expectations"]
