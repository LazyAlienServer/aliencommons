from rest_framework.response import Response
from rest_framework import status


def format_api_response(
        *,
        success, message, code, data=None, errors=None, request=None,
        status_code=status.HTTP_200_OK, headers=None
):
    """
    Return a formatted api response.
    This function should always be called in api views and in the custom api exception handler.
    """

    payload = {
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

    return Response(payload, status=status_code, headers=headers)
