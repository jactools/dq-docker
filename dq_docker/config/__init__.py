"""Config subpackage for `dq_docker`.

Expose `gx_config` as `dq_docker.config.gx_config` lazily. Importing
the `dq_docker.config` package will not evaluate `gx_config` at
import-time (which may require runtime environment variables). Access
`dq_docker.config.gx_config` to import the module on demand.

This module used to expose `adls_config`; code should migrate to
`gx_config`.
"""

__all__ = ["gx_config"]


def __getattr__(name: str):
	if name == "gx_config":
		from importlib import import_module

		return import_module(__name__ + ".gx_config")
	raise AttributeError(name)
