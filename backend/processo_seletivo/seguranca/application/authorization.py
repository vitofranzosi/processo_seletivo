from processo_seletivo.shared.api.problems import DomainError


def require_permission(actor, permission: str, *, institution_scope: str | None = None) -> None:
    if not actor or not actor.is_authenticated or not actor.can(permission):
        raise DomainError("forbidden", "A operação não é permitida.", 403)
    if institution_scope is not None and actor.institution_scope != institution_scope:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
