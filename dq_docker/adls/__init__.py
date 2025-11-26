"""ADLS Gen2 helpers package for dq_docker.

Expose a small ADLS client wrapper that uses fsspec/adlfs when available.
"""
from .client import ADLSClient
from .utils import build_abfs_uri, env_var_names

__all__ = ["ADLSClient", "build_abfs_uri", "env_var_names"]
