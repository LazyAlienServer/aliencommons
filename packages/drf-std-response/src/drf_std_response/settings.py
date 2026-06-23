from django.conf import settings
from django.utils.module_loading import import_string


DEFAULTS = {
    "EXCEPTION_HANDLER_CLASS": "drf_std_response.exception_handlers.ExceptionHandler",
    "EXCEPTION_FORMATTER_CLASS": "drf_std_response.formatters.ErrorFormatter",
    "NESTED_FIELD_SEPARATOR": ".",
    "NON_FIELD_ERRORS_KEY": "non_field_errors",
}


def get_setting(name):
    if not settings.configured:
        return DEFAULTS[name]
    package_settings = getattr(settings, "DRF_STD_RESPONSE", {})
    return package_settings.get(name, DEFAULTS[name])


def import_from_setting(name):
    return import_string(get_setting(name))
