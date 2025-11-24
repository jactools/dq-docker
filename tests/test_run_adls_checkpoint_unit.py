import importlib
import types
import pytest


def _reload_module():
    import dq_docker.run_adls_checkpoint as mod
    importlib.reload(mod)
    return mod


def test_main_orchestration_calls_helpers(monkeypatch, caplog):
    mod = _reload_module()

    calls = []

    # Stub get_context to return a fake context
    def fake_get_context(root):
        calls.append("get_context")
        return object()

    monkeypatch.setattr(mod, "get_context", fake_get_context, raising=False)

    # Data docs
    def fake_ensure_data_docs_site(context, site_name, site_config):
        calls.append("ensure_data_docs_site")

    monkeypatch.setattr(mod, "ensure_data_docs_site", fake_ensure_data_docs_site, raising=False)

    # Datasource / asset
    def fake_ensure_pandas_filesystem(context, name, base):
        calls.append("ensure_pandas_filesystem")
        return object()

    def fake_ensure_csv_asset(ds, name):
        calls.append("ensure_csv_asset")
        return object()

    monkeypatch.setattr(mod, "ensure_pandas_filesystem", fake_ensure_pandas_filesystem, raising=False)
    monkeypatch.setattr(mod, "ensure_csv_asset", fake_ensure_csv_asset, raising=False)

    # Batch def and preview
    def fake_ensure_batch_definition(asset, name, path):
        calls.append("ensure_batch_definition")
        return types.SimpleNamespace(get_batch=lambda: types.SimpleNamespace(head=lambda: "h"))

    def fake_get_batch_and_preview(bd):
        calls.append("get_batch_and_preview")
        return types.SimpleNamespace()

    monkeypatch.setattr(mod, "ensure_batch_definition", fake_ensure_batch_definition, raising=False)
    monkeypatch.setattr(mod, "get_batch_and_preview", fake_get_batch_and_preview, raising=False)

    # Expectation suite builder
    def fake_build_expectation_suite(name, contract_path=None):
        calls.append("build_expectation_suite")
        return types.SimpleNamespace()

    monkeypatch.setattr(mod, "build_expectation_suite", fake_build_expectation_suite, raising=False)

    def fake_add_suite_to_context(context, suite, name):
        calls.append("add_suite_to_context")

    monkeypatch.setattr(mod, "add_suite_to_context", fake_add_suite_to_context, raising=False)

    # Validation definition
    class FakeVD:
        def run(self):
            calls.append("validation_run")
            return {"success": True}

    def fake_create_or_get_validation_definition(ctx, name, bd, suite):
        calls.append("create_or_get_validation_definition")
        return FakeVD()

    monkeypatch.setattr(mod, "create_or_get_validation_definition", fake_create_or_get_validation_definition, raising=False)

    # Checkpoint
    def fake_create_and_run_checkpoint(context, name, validation_definition, actions, result_format):
        calls.append("create_and_run_checkpoint")
        return {"success": True}

    monkeypatch.setattr(mod, "create_and_run_checkpoint", fake_create_and_run_checkpoint, raising=False)

    # Data docs urls
    def fake_get_data_docs_urls(context):
        calls.append("get_data_docs_urls")
        return {"local_site": ["http://fake"]}

    monkeypatch.setattr(mod, "get_data_docs_urls", fake_get_data_docs_urls, raising=False)

    # prevent os.listdir surprises
    monkeypatch.setattr("os.listdir", lambda p: ["customers_2019.csv", "contracts"], raising=False)

    # Run
    caplog.set_level("INFO")
    mod.main()

    # Ensure key helpers were called in the orchestration
    expected = [
        "get_context",
        "ensure_data_docs_site",
        "ensure_pandas_filesystem",
        "ensure_csv_asset",
        "ensure_batch_definition",
        "get_batch_and_preview",
        "build_expectation_suite",
        "add_suite_to_context",
        "create_or_get_validation_definition",
        "validation_run",
        "create_and_run_checkpoint",
        "get_data_docs_urls",
    ]

    for e in expected:
        assert e in calls


def test_main_early_exit_no_context(monkeypatch, caplog):
    mod = _reload_module()

    # get_context returns None => main should exit early and not call data docs
    monkeypatch.setattr(mod, "get_context", lambda root: None, raising=False)

    called = []

    def fake_ensure_data_docs_site(context, site_name, site_config):
        called.append("data_docs_called")

    monkeypatch.setattr(mod, "ensure_data_docs_site", fake_ensure_data_docs_site, raising=False)

    caplog.set_level("INFO")
    mod.main()

    # ensure we didn't call ensure_data_docs_site
    assert called == []
