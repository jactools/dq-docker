import great_expectations as gx
import logging

from dq_docker.logs import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

logger.info(gx.__version__)
