import importlib
import os
import sys


def test_gx_config_allows_import_when_data_source_missing(monkeypatch):
    # Ensure env var is not set
    monkeypatch.delenv("DQ_DATA_SOURCE", raising=False)

    # Removing the module from sys.modules to force a fresh import
    sys.modules.pop("dq_docker.config.gx_config", None)

    # Importing should succeed but DATA_SOURCE_NAME should be None
    import dq_docker.config.gx_config as cfg  # noqa: F401
    assert cfg.DATA_SOURCE_NAME is None


def test_gx_config_raises_when_data_source_not_found(monkeypatch):
    # Set an unknown data source
    monkeypatch.setenv("DQ_DATA_SOURCE", "ds_nonexistent")
    sys.modules.pop("dq_docker.config.gx_config", None)

    try:
        import dq_docker.config.gx_config as cfg  # noqa: F401
        assert False, "gx_config import should have raised when DQ_DATA_SOURCE points to an unknown source"
    except RuntimeError:
        # Expected
        pass
