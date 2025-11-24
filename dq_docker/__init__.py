"""Top-level package for the `dq_docker` project.

Expose configuration and package version.

Make `dq_docker` safe to import in CI and tooling by avoiding import-time
side-effects. Loading `dq_docker.config` is deferred until the attribute
is accessed so scripts that import the package (for version info, etc.)
don't accidentally trigger configuration code that expects runtime
environment variables like `DQ_DATA_SOURCE`.
"""

from ._version import __version__

__all__ = ["config", "__version__"]


def __getattr__(name: str):
	"""Lazily import submodules on attribute access.

	This makes `import dq_docker` lightweight and avoids running
	configuration code at import time. Accessing ``dq_docker.config``
	will import and cache the `dq_docker.config` module on first use.
	"""
	if name == "config":
		import importlib

		mod = importlib.import_module(f"{__name__}.config")
		globals()["config"] = mod
		return mod
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
	return sorted(list(globals().keys()) + ["config"])
