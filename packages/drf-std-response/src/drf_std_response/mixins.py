from rest_framework import status
from rest_framework.response import Response

from .responses import ENVELOPE_RESPONSE_ATTR, build_payload, format_response


class EnvelopeMixin:
    """
    Wrap successful DRF responses in the standard response envelope.
    """

    envelope_message = "ok"
    envelope_code = "ok"
    action_messages = {
        "list": "listed",
        "retrieve": "retrieved",
        "create": "created",
        "update": "updated",
        "partial_update": "updated",
        "destroy": "deleted",
    }
    action_codes = {
        "list": "listed",
        "retrieve": "retrieved",
        "create": "created",
        "update": "updated",
        "partial_update": "updated",
        "destroy": "deleted",
    }

    def get_envelope_message(self, response):
        action = getattr(self, "action", None)
        return self.action_messages.get(action, self.envelope_message)

    def get_envelope_code(self, response):
        action = getattr(self, "action", None)
        return self.action_codes.get(action, self.envelope_code)

    def should_wrap_response(self, response):
        if not isinstance(response, Response):
            return False
        if getattr(response, ENVELOPE_RESPONSE_ATTR, False):
            return False
        if response.exception:
            return False
        if status.is_client_error(response.status_code) or status.is_server_error(
            response.status_code
        ):
            return False
        return True

    def format_success_response(
        self,
        *,
        message="ok",
        code="ok",
        data=None,
        status_code=status.HTTP_200_OK,
        headers=None,
    ):
        request = getattr(self, "request", None)
        return format_response(
            success=True,
            message=message,
            code=code,
            data=data,
            errors=None,
            status_code=status_code,
            request=request,
            headers=headers,
        )

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)

        if not self.should_wrap_response(response):
            return response

        if response.status_code == status.HTTP_204_NO_CONTENT:
            response.status_code = status.HTTP_200_OK

        response.data = build_payload(
            success=True,
            message=self.get_envelope_message(response),
            code=self.get_envelope_code(response),
            data=response.data,
            errors=None,
            request=request,
        )
        setattr(response, ENVELOPE_RESPONSE_ATTR, True)
        return response
