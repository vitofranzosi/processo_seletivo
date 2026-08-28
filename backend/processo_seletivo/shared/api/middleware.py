import uuid


class CorrelationIdMiddleware:
    header = "HTTP_X_CORRELATION_ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.correlation_id = request.META.get(self.header) or str(uuid.uuid4())
        response = self.get_response(request)
        response["X-Correlation-ID"] = request.correlation_id
        return response
