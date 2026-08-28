from dataclasses import dataclass

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from processo_seletivo.shared.observability import log_domain_rejection


@dataclass
class DomainError(Exception):
    code: str
    detail: str
    status: int = 422


def _violations(detail, prefix=""):
    """Achata os erros do serializer preservando o caminho do campo."""
    if isinstance(detail, dict):
        return [
            item
            for chave, valor in detail.items()
            for item in _violations(valor, f"{prefix}{chave}.")
        ]
    if isinstance(detail, list):
        return [item for valor in detail for item in _violations(valor, prefix)]
    return [f"{prefix.rstrip('.')}: {detail}" if prefix else str(detail)]


def problem_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        request = context.get("request")
        correlation_id = getattr(request, "correlation_id", "unknown")
        log_domain_rejection(
            code=exc.code,
            status=exc.status,
            correlation_id=correlation_id,
            actor_subject=getattr(getattr(request, "user", None), "subject", ""),
        )
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
    if isinstance(exc, ValidationError):
        # Corpo bem formado mas semanticamente inválido é 422, como declara o contrato;
        # 400 fica para metadados malformados (header ou query string).
        response.status_code = 422
        code = "invalid_payload"
        detail = "; ".join(_violations(exc.detail)) or "Requisição inválida"
    else:
        code = "request_rejected"
        detail = str(
            response.data.get("detail", "Requisição inválida")
            if isinstance(response.data, dict)
            else "Requisição inválida"
        )
    log_domain_rejection(
        code=code,
        status=response.status_code,
        correlation_id=correlation_id,
        actor_subject=getattr(getattr(request, "user", None), "subject", ""),
    )
    response.data = {
        "type": f"https://processo-seletivo.cefor/errors/{code}",
        "title": "Requisição rejeitada",
        "status": response.status_code,
        "code": code,
        "detail": detail,
        "correlationId": correlation_id,
    }
    response.content_type = "application/problem+json"
    return response
