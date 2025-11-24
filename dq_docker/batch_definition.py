from typing import Any, Optional
from .logs import get_logger

logger = get_logger(__name__)


def find_batch_definition(asset: Any, name: str, path: str) -> Optional[Any]:
    if asset is None:
        return None

    try:
        get_fn = getattr(asset, "get_batch_definition", None) or getattr(asset, "get", None)
        if callable(get_fn):
            try:
                bd = get_fn(name)
                if bd:
                    return bd
            except Exception:
                pass
    except Exception:
        pass

    try:
        list_fn = getattr(asset, "list_batch_definitions", None) or getattr(asset, "list", None)
        items = None
        if callable(list_fn):
            try:
                items = list_fn()
            except Exception:
                items = None
        else:
            items = getattr(asset, "batch_definitions", None)

        if isinstance(items, dict):
            if name in items:
                return items[name]
            for v in items.values():
                try:
                    if getattr(v, "path", None) == path:
                        return v
                except Exception:
                    pass
        elif isinstance(items, list):
            for it in items:
                if isinstance(it, dict) and it.get("name") == name:
                    return it
                try:
                    if getattr(it, "name", None) == name:
                        return it
                    if getattr(it, "path", None) == path:
                        return it
                except Exception:
                    pass
    except Exception:
        pass

    return None


def ensure_batch_definition(asset: Any, name: str, path: str) -> Any:
    bd = find_batch_definition(asset, name, path)
    if bd:
        logger.info("✅ Batch definition '%s' already exists.", name)
        return bd
    logger.info("Adding batch definition '%s' (path=%s)", name, path)
    return asset.add_batch_definition_path(name=name, path=path)


def get_batch_and_preview(batch_definition: Any):
    """Get a batch from a batch definition and return it.

    This helper will attempt to call `get_batch()` on the batch definition and
    log a short preview (first rows) if available.
    """
    if batch_definition is None:
        return None

    try:
        batch = batch_definition.get_batch()
        try:
            preview = getattr(batch, "head", None)
            if callable(preview):
                logger.info(preview())
            else:
                # sometimes batch behaves like a dataframe
                try:
                    logger.info(batch.head())
                except Exception:
                    pass
        except Exception:
            pass
        return batch
    except Exception:
        return None
