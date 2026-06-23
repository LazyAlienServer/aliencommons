from rest_framework import status
from rest_framework.response import Response


ENVELOPE_RESPONSE_ATTR = "_drf_std_response_enveloped"


def build_payload(
    *,
    success,
    message,
    code,
    data=None,
    errors=None,
    request=None,
):
    """
    Build the standard API response payload.
    """
    return {
        "success": success,
        "message": message,
        "code": code,
        "data": data,
        "errors": errors,
        "meta": {
            "request_id": getattr(request, "request_id", None) if request else None,
            "timestamp": getattr(request, "timestamp", None) if request else None,
        },
    }


def format_response(
    *,
    success,
    message,
    code,
    data=None,
    errors=None,
    request=None,
    status_code=status.HTTP_200_OK,
    headers=None,
):
    """
    Return a DRF Response containing the standard API response payload.
    """
    response = Response(
        build_payload(
            success=success,
            message=message,
            code=code,
            data=data,
            errors=errors,
            request=request,
        ),
        status=status_code,
        headers=headers,
    )
    setattr(response, ENVELOPE_RESPONSE_ATTR, True)
    return response
