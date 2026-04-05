from .services.sessions import update_last_accessed_at


class UserSessionTrackingMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        update_last_accessed_at(request)

        response = self.get_response(request)
        return response
