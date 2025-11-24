import types
import importlib

import dq_docker.data_source as ds_mod


class FakeDatasource:
    def __init__(self, name, base_directory):
        self.name = name
        self.base_directory = base_directory


class FakeDataSourcesManager:
    def __init__(self, existing_ds: FakeDatasource = None):
        self._existing = existing_ds
        self.deleted = False
        self.added_with = None

    def get(self, name):
        if self._existing and self._existing.name == name:
            return self._existing
        return None

    def delete(self, name):
        if self._existing and self._existing.name == name:
            self.deleted = True
            self._existing = None

    def add_pandas_filesystem(self, name: str, base_directory: str):
        # Record args and return a new FakeDatasource
        self.added_with = (name, base_directory)
        self._existing = FakeDatasource(name, base_directory)
        return self._existing


class FakeContext:
    def __init__(self, ds_manager: FakeDataSourcesManager):
        self.data_sources = ds_manager


def test_ensure_pandas_filesystem_recreates_when_base_dir_differs():
    # Existing datasource points at a container path
    existing = FakeDatasource("ds_sample_data", "/usr/src/app/dq_great_expectations/sample_data/customers")
    mgr = FakeDataSourcesManager(existing_ds=existing)
    ctx = FakeContext(mgr)

    # Call the function under test with a local path that differs
    result = ds_mod.ensure_pandas_filesystem(ctx, "ds_sample_data", "/home/runner/work/repo/dq_great_expectations/sample_data/customers")

    # Manager should have deleted the old datasource and added a new one
    assert mgr.deleted or mgr.added_with is not None
    assert mgr.added_with[0] == "ds_sample_data"
    assert mgr.added_with[1].endswith("dq_great_expectations/sample_data/customers")
    assert result is not None
