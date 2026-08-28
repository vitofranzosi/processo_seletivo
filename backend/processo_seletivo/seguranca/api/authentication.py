from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from processo_seletivo.seguranca.domain import Actor


class InstitutionalBearerAuthentication(BaseAuthentication):
    """Adaptador provisório: token de desenvolvimento `subject|scope|perm,perm`."""

    keyword = b"bearer"

    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts:
            return None
        if len(parts) != 2 or parts[0].lower() != self.keyword:
            raise AuthenticationFailed("Bearer token inválido")
        try:
            subject, scope, permissions = parts[1].decode().split("|", 2)
        except ValueError as exc:
            raise AuthenticationFailed("Bearer token inválido") from exc
        actor = Actor(subject, scope, frozenset(filter(None, permissions.split(","))))
        return actor, parts[1].decode()

    def authenticate_header(self, request):
        return "Bearer"
