"""Config package for dq_docker.

Expose the adls_config module for namespaced imports like `config.adls_config`.
"""

from . import adls_config

__all__ = ["adls_config"]
