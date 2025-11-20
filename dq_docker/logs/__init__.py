"""Simple logging helper for the dq_docker package.

Provides `configure_logging` to set a reasonable default handler and
`get_logger(name)` to obtain a package-scoped logger.

This keeps logging configuration in one place and avoids sprinkling
basicConfig calls across modules.
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Optional

DEFAULT_LEVEL = os.environ.get("DQ_LOG_LEVEL", "INFO")


def configure_logging(level: Optional[str] = None) -> None:
    """Configure the root logger for the package.

    This is idempotent and safe to call multiple times. It configures a
    single StreamHandler with a compact formatter writing to stdout.
    """
    lvl = (level or DEFAULT_LEVEL).upper()
    numeric = getattr(logging, lvl, logging.INFO)

    root = logging.getLogger()
    # Avoid adding duplicate handlers if already configured
    if any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.setLevel(numeric)
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%Y-%m-%dT%H:%M:%S")
    handler.setFormatter(fmt)
    root.addHandler(handler)
    root.setLevel(numeric)


def get_logger(name: str) -> logging.Logger:
    """Return a logger scoped under `dq_docker`.

    The logger will inherit configuration from `configure_logging`.
    """
    return logging.getLogger(f"dq_docker.{name}")
