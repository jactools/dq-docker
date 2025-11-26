import types


def test_csv_asset_reused(monkeypatch):
    # Install a fake `great_expectations` module so importing the runtime will
    # pick up the fake context. We will create fake context and then import the
    # runtime module so its module-level constants align with the fake config.
    import sys
    import importlib

    # Placeholder classes will be defined after importing the runtime so we can
    # reference `rac.ASSET_NAME` and `rac.DATA_SOURCE_NAME` reliably.

    # Create a fake context and fake GE modules
    fake_ctx = types.SimpleNamespace()

    # We'll construct the FakeDataSource etc after importing rac

    fake_gx = types.ModuleType("great_expectations")
    # Provide get_context that returns our fake context object
    fake_gx.get_context = lambda mode=None, project_root_dir=None: fake_ctx
    sys.modules["great_expectations"] = fake_gx

    fake_checkpoint_mod = types.ModuleType("great_expectations.checkpoint")
    class UpdateDataDocsAction:
        def __init__(self, name=None, site_names=None):
            self.name = name
            self.site_names = site_names

    fake_checkpoint_mod.UpdateDataDocsAction = UpdateDataDocsAction
    sys.modules["great_expectations.checkpoint"] = fake_checkpoint_mod

    # Now import the runtime module (it will import our fake gx)
    rac = importlib.import_module("dq_docker.run_adls_checkpoint")

    # Now define the fake structures that reference rac constants
    class FakeBatch:
        def head(self):
            return "fake-head"

    class FakeBatchDef:
        def get_batch(self):
            return FakeBatch()

    class FakeAsset:
        def add_batch_definition_path(self, name, path):
            return FakeBatchDef()

    class FakeDataSource:
        def __init__(self):
            self.add_csv_asset_called = False

        def get(self, name):
            # Return a fake asset for the requested name to simulate an
            # existing asset (avoid relying on exact name matching of
            # rac.ASSET_NAME across test environments).
            return FakeAsset()

        def add_csv_asset(self, name):
            # Should not be called when the asset already exists
            self.add_csv_asset_called = True
            raise AssertionError("add_csv_asset should not be called when asset exists")

        def list_assets(self):
            return [{"name": rac.ASSET_NAME}]

    class DataSourceManager:
        def __init__(self, ds):
            self._ds = ds

        def get(self, name):
            return self._ds if name == rac.DATA_SOURCE_NAME else None

        def add_pandas_filesystem(self, name, base_directory):
            return self._ds

    class FakeSuites:
        def add(self, suite):
            return None

    class FakeValidationDefs:
        def add(self, vd):
            class FakeVD:
                def run(self):
                    return {"success": True}

            return FakeVD()

    class FakeCheckpoints:
        def add_or_update(self, checkpoint):
            pass

    # Attach context attributes now that fake classes exist
    fake_ctx.data_sources = DataSourceManager(FakeDataSource())
    fake_ctx.suites = FakeSuites()
    fake_ctx.validation_definitions = FakeValidationDefs()
    fake_ctx.checkpoints = FakeCheckpoints()

    fake_ctx.get_site_names = lambda: []
    fake_ctx.add_data_docs_site = lambda site_name, site_config: None
    fake_ctx.list_data_docs_sites = lambda: {}
    fake_ctx.get_docs_sites_urls = lambda: []

    # Monkeypatch build_expectation_suite to a simple fake suite
    monkeypatch.setattr(rac, "build_expectation_suite", lambda name, contract_path: types.SimpleNamespace())

    # Monkeypatch ValidationDefinition so we don't invoke pydantic model parsing
    monkeypatch.setattr(fake_gx, "ValidationDefinition", lambda *args, **kwargs: types.SimpleNamespace(), raising=False)

    # Monkeypatch Checkpoint to a simple object with run() -> success
    monkeypatch.setattr(fake_gx, "Checkpoint", lambda *args, **kwargs: types.SimpleNamespace(run=lambda: {"success": True}), raising=False)

    # Run main - should reuse existing asset and not call add_csv_asset
    rac.main()

    assert not fake_ctx.data_sources._ds.add_csv_asset_called
