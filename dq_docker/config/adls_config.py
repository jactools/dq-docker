"""Removed compatibility shim.

This module used to provide `adls_config` and a shim to the newer
`gx_config` module. The shim has been removed; importing
`dq_docker.config.adls_config` will raise to encourage callers to migrate.
"""
raise ImportError(
    "dq_docker.config.adls_config has been removed; import dq_docker.config.gx_config instead"
)
