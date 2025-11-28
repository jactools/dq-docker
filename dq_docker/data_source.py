from typing import Any, Optional
import os
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
        # If an existing datasource points at a different base_directory
        # (for example when great_expectations.yml contains container paths),
        # recreate it so the runtime uses the provided `base_directory`.
        try:
            existing_base = getattr(ds, "base_directory", None)
        except Exception:
            existing_base = None
        if existing_base:
            try:
                # Normalize paths for comparison
                if os.path.abspath(str(existing_base)) != os.path.abspath(str(base_directory)):
                    logger.info("Data source '%s' exists but base_directory differs; recreating with %s", name, base_directory)
                    try:
                        # Attempt to delete and recreate via the DataSourceManager
                        if hasattr(ctx, "data_sources") and callable(getattr(ctx.data_sources, "delete", None)):
                            try:
                                ctx.data_sources.delete(name)
                            except Exception:
                                pass
                            return ctx.data_sources.add_pandas_filesystem(name=name, base_directory=base_directory)
                    except Exception:
                        # Fallthrough to returning the existing datasource
                        pass
            except Exception:
                # If anything goes wrong inspecting the existing datasource, ignore
                pass
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
