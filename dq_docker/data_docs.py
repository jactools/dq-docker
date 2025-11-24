from typing import Any, Dict
from .logs import get_logger

logger = get_logger(__name__)


def ensure_data_docs_site(context: Any, site_name: str, site_config: Dict) -> None:
    """Ensure a data docs site exists in the context, creating it if missing."""
    try:
        if site_name not in context.get_site_names():
            context.add_data_docs_site(site_name=site_name, site_config=site_config)
            logger.info("✅ Data Docs site '%s' added to the context.", site_name)
        else:
            logger.info("✅ Data Docs site '%s' already exists in the context.", site_name)
    except Exception as exc:
        logger.error("Failed to ensure Data Docs site '%s': %s", site_name, exc)
        raise


def get_data_docs_urls(context: Any) -> Dict:
    try:
        return context.get_docs_sites_urls()
    except Exception:
        return {}
