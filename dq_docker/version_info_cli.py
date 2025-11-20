"""CLI entrypoint that prints package and Great Expectations versions.
"""
import great_expectations as gx
from . import __version__ as package_version


def main() -> None:
    print(f"dq-docker package version: {package_version}")
    print(f"great_expectations version: {gx.__version__}")


if __name__ == "__main__":
    main()
