from typing import Any, Optional
from .logs import get_logger


logger = get_logger(__name__)


def find_datasource(ctx: Any, name: str) -> Optional[Any]:
    """Defensively locate a datasource by name across various GE versions."""
    ds_manager = getattr(ctx, "data_sources", None)

    # 1) manager.get(name)
    try:
        get_fn = getattr(ds_manager, "get", None)
        if callable(get_fn):
            try:
                ds = get_fn(name)
                if ds:
                    return ds
            except Exception:
                pass
    except Exception:
        pass

    # 2) context.list_datasources()
    try:
        list_fn = getattr(ctx, "list_datasources", None)
        if callable(list_fn):
            try:
                items = list_fn()
                if isinstance(items, dict):
                    if name in items:
                        try:
                            if callable(getattr(ds_manager, "get", None)):
                                return ds_manager.get(name)
                        except Exception:
                            return items[name]
                elif isinstance(items, list):
                    for it in items:
                        if isinstance(it, dict) and it.get("name") == name:
                            try:
                                if callable(getattr(ds_manager, "get", None)):
                                    return ds_manager.get(name)
                            except Exception:
                                return it
                        if isinstance(it, str) and it == name:
                            try:
                                if callable(getattr(ds_manager, "get", None)):
                                    return ds_manager.get(name)
                            except Exception:
                                return None
            except Exception:
                pass
    except Exception:
        pass

    # 3) manager.list()
    try:
        list_fn = getattr(ds_manager, "list", None) or getattr(ds_manager, "list_datasources", None)
        if callable(list_fn):
            try:
                items = list_fn()
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, dict) and it.get("name") == name:
                            try:
                                if callable(getattr(ds_manager, "get", None)):
                                    return ds_manager.get(name)
                            except Exception:
                                return it
            except Exception:
                pass
    except Exception:
        pass

    return None


def ensure_pandas_filesystem(ctx: Any, name: str, base_directory: str) -> Any:
    ds = find_datasource(ctx, name)
    if ds:
        logger.info("✅ Data source '%s' already exists.", name)
        return ds

    logger.info("Adding pandas_filesystem datasource '%s' (base: %s)", name, base_directory)
    return ctx.data_sources.add_pandas_filesystem(name=name, base_directory=base_directory)


def find_asset(ds: Any, name: str) -> Optional[Any]:
    if ds is None:
        return None

    try:
        get_fn = getattr(ds, "get", None) or getattr(ds, "get_asset", None)
        if callable(get_fn):
            try:
                asset = get_fn(name)
                if asset:
                    return asset
            except Exception:
                pass
    except Exception:
        pass

    try:
        list_fn = getattr(ds, "list_assets", None)
        items = None
        if callable(list_fn):
            try:
                items = list_fn()
            except Exception:
                items = None
        else:
            items = getattr(ds, "assets", None)

        if isinstance(items, dict):
            if name in items:
                return items[name]
        elif isinstance(items, list):
            for it in items:
                if isinstance(it, dict) and it.get("name") == name:
                    return it
                if isinstance(it, str) and it == name:
                    return it
    except Exception:
        pass

    return None


def ensure_csv_asset(ds: Any, name: str) -> Any:
    asset = find_asset(ds, name)
    if asset:
        logger.info("✅ Asset '%s' already exists on datasource.", name)
        return asset
    return ds.add_csv_asset(name=name)
