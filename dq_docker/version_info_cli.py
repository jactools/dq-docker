"""CLI entrypoint that prints package and Great Expectations versions.
"""
import great_expectations as gx
from . import __version__ as package_version
from .logs import configure_logging, get_logger

configure_logging()
logger = get_logger("version_info_cli")


def main() -> None:
    logger.info("dq-docker package version: %s", package_version)
    logger.info("great_expectations version: %s", gx.__version__)


if __name__ == "__main__":
    main()
