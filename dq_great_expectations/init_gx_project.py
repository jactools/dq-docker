import great_expectations as gx
import os
import logging

# Set the project root to the package directory so this script initializes
# the local `dq_great_expectations` project structure rather than the
# current working directory.
project_root = os.path.abspath(os.path.dirname(__file__))

from dq_docker.logs import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

logger.info("Attempting to initialize/load project in: %s", project_root)

# Use get_context() with mode="file" to ensure a FileDataContext is created or loaded
# This handles the creation logic internally if no context is found.
context = gx.get_context(mode="file", project_root_dir=project_root)

logger.info("✅ Great Expectations Data Context is ready.")
# The local `dq_great_expectations` directory should now contain GE project artifacts
logger.info("%s", context)
