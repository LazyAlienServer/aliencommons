from contextvars import ContextVar


_log_context = ContextVar('log_context', default={})


def get_log_context() -> dict:
    """
    Return a copy current logging context, not the context object itself.
    Any changes must be made via:
    - set_log_context()
    - bind_log_context()
    - clear_log_context()
    - unbind_log_context()
    """
    context_copy = dict(_log_context.get())
    return context_copy


def set_log_context(**values) -> None:
    """
    Replace the current logging context with the provided values.
    """
    dict_values = dict(values)
    _log_context.set(dict_values)


def add_log_context(**values) -> None:
    """
    Merge the provided values into the current logging context.
    Accepts only keyword arguments.
    """
    current_context = dict(_log_context.get())
    current_context.update(values)

    _log_context.set(current_context)


def clear_log_context() -> None:
    """
    Clear the current logging context.
    """
    _log_context.set({})


def remove_log_context(*keys: str) -> None:
    """
    Remove specific keys from the current logging context.
    """
    current_context = dict(_log_context.get())
    for key in keys:
        current_context.pop(key, None)

    _log_context.set(current_context)
