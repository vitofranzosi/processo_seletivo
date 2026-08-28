from dataclasses import dataclass

from rest_framework.response import Response
from rest_framework.views import exception_handler


@dataclass
class DomainError(Exception):
    code: str
    detail: str
    status: int = 422


def problem_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        request = context.get("request")
        correlation_id = getattr(request, "correlation_id", "unknown")
        return Response(
            {
                "type": f"https://processo-seletivo.cefor/errors/{exc.code}",
                "title": "Operação rejeitada",
                "status": exc.status,
                "code": exc.code,
                "detail": exc.detail,
                "correlationId": correlation_id,
            },
            status=exc.status,
            content_type="application/problem+json",
        )
    response = exception_handler(exc, context)
    if response is None:
        return None
    request = context.get("request")
    correlation_id = getattr(request, "correlation_id", "unknown")
    detail = (
        response.data.get("detail", "Requisição inválida")
        if isinstance(response.data, dict)
        else "Requisição inválida"
    )
    response.data = {
        "type": "about:blank",
        "title": "Requisição rejeitada",
        "status": response.status_code,
        "code": "request_rejected",
        "detail": str(detail),
        "correlationId": correlation_id,
    }
    response.content_type = "application/problem+json"
    return response
