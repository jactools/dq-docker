"""Top-level package for the `dq_docker` project.

Expose configuration and package version.
"""

from . import config
from ._version import __version__

__all__ = ["config", "__version__"]
