import importlib
import os


def test_data_sources_yaml_keys_and_gx_config(monkeypatch):
    """Ensure the YAML mapping provides required keys and `gx_config`
    derives values correctly for the selected data source.
    """
    # Ensure selection is explicit for the test
    monkeypatch.setenv("DQ_DATA_SOURCE", "ds_sample_data")

    ds_mod = importlib.import_module("dq_docker.data_sources")
    importlib.reload(ds_mod)

    assert "ds_sample_data" in ds_mod.DATA_SOURCES

    required = [
        "source_folder",
        "asset_name",
        "batch_definition_name",
        "batch_definition_path",
        "expectation_suite_name",
        "definition_name",
    ]
    for k in required:
        assert k in ds_mod.DATA_SOURCES["ds_sample_data"], f"missing key {k} in data_sources"

    # Reload gx_config after setting env var so it picks up the selected source
    cfg = importlib.import_module("dq_docker.config.gx_config")
    importlib.reload(cfg)

    assert cfg.DATA_SOURCE_NAME == "ds_sample_data"

    # The `source_folder` in the YAML is relative to `PROJECT_ROOT` in our design
    expected_source = os.path.join(cfg.PROJECT_ROOT, ds_mod.DATA_SOURCES["ds_sample_data"]["source_folder"])
    assert cfg.SOURCE_FOLDER == expected_source

    assert cfg.ASSET_NAME == ds_mod.DATA_SOURCES["ds_sample_data"]["asset_name"]
    assert cfg.BATCH_DEFINITION_NAME == ds_mod.DATA_SOURCES["ds_sample_data"]["batch_definition_name"]
    assert cfg.EXPECTATION_SUITE_NAME == ds_mod.DATA_SOURCES["ds_sample_data"]["expectation_suite_name"]
    assert cfg.DEFINITION_NAME == ds_mod.DATA_SOURCES["ds_sample_data"]["definition_name"]
