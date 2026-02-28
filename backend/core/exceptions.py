from rest_framework import status


class ServiceError(Exception):
    """
    The exception class for all service-layer errors.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Request failed"
    default_code = 'service_error'

    def __init__(self, *, detail=None, code=None, status_code=None):
        self.detail = self.default_detail if detail is None else detail
        self.code = self.default_code if code is None else code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(str(self.detail))
