from typing import Any, Optional
from .logs import get_logger

logger = get_logger(__name__)


def create_or_get_validation_definition(context: Any, name: str, batch_definition: Any, suite: Any) -> Any:
    """Create a ValidationDefinition or reuse an existing one to be idempotent.

    This function imports Great Expectations inside its body so tests that
    monkeypatch `great_expectations` can still work.
    """
    try:
        import great_expectations as gx  # lazy import
    except Exception:
        gx = None

    if gx is None:
        # Construct a minimal ValidationDefinition-like object for environments
        # without GE; callers should be guarded accordingly.
        vd = {"name": name, "data": batch_definition, "suite": suite}
        try:
            # attempt to add if supported by context
            return context.validation_definitions.add(vd)
        except Exception:
            return vd

    validation_definition = gx.ValidationDefinition(name=name, data=batch_definition, suite=suite)
    try:
        vd = context.validation_definitions.add(validation_definition)
        logger.info("✅ Validation Definition '%s' created.", name)
        return vd
    except Exception:
        logger.info("ℹ️ Validation Definition '%s' may already exist; attempting to reuse.", name)
        validation_definition = None
        try:
            vd_manager = getattr(context, "validation_definitions", None)
            get_fn = getattr(vd_manager, "get", None)
            if callable(get_fn):
                try:
                    validation_definition = get_fn(name)
                except Exception:
                    validation_definition = None

            if validation_definition is None:
                list_fn = getattr(vd_manager, "list", None) or getattr(context, "list_validation_definitions", None)
                if callable(list_fn):
                    try:
                        items = list_fn()
                        if isinstance(items, dict) and name in items:
                            validation_definition = items[name]
                        elif isinstance(items, list):
                            for it in items:
                                if isinstance(it, dict) and it.get("name") == name:
                                    validation_definition = it
                                    break
                    except Exception:
                        validation_definition = None

            if validation_definition is None:
                try:
                    items = getattr(context, "validation_definitions", None)
                    if isinstance(items, list):
                        for it in items:
                            try:
                                if getattr(it, "name", None) == name or (isinstance(it, dict) and it.get("name") == name):
                                    validation_definition = it
                                    break
                            except Exception:
                                pass
                except Exception:
                    validation_definition = None
        except Exception:
            validation_definition = None

        if validation_definition is None:
            logger.error("Failed to add or find Validation Definition '%s'.", name)
            raise

        return validation_definition
