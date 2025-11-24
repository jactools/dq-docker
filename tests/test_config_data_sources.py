import importlib
import os


def test_data_sources_mapping_keys():
    mod = importlib.import_module("dq_docker.config.data_sources")
    ds = mod.DATA_SOURCES
    assert isinstance(ds, dict)
    assert "ds_sample_data" in ds
    required = {
        "source_folder",
        "asset_name",
        "batch_definition_name",
        "batch_definition_path",
        "expectation_suite_name",
        "definition_name",
    }
    for name, cfg in ds.items():
        assert isinstance(cfg, dict)
        assert required.issubset(set(cfg.keys()))


def test_adls_config_derives_from_selected(monkeypatch):
    # Ensure adls_config picks up values based on DQ_DATA_SOURCE.
    # We require the variable be set (no implicit defaults), so set it here.
    monkeypatch.setenv("DQ_DATA_SOURCE", "ds_sample_data")
    import importlib

    cfg = importlib.import_module("dq_docker.config.adls_config")
    importlib.reload(cfg)
    assert cfg.DATA_SOURCE_NAME == "ds_sample_data"
    assert cfg.ASSET_NAME is not None
    assert cfg.SOURCE_FOLDER is not None
