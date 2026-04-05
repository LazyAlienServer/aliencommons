from django.utils import timezone

import uuid


class RequestMetaMiddleware:
    """
    Add Meta Information to the Request object.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4().hex)
        timestamp = timezone.now()

        request.request_id = request_id
        request.timestamp = timestamp

        response = self.get_response(request)

        return response
