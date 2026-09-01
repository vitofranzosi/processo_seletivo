from django.urls import include, path

from processo_seletivo.shared.api.operacional import (
    HealthView,
    IndexView,
    MetricsView,
    ReadinessView,
)

urlpatterns = [
    # Endpoints operacionais ficam fora de /api/v1: não são contrato institucional.
    path("", IndexView.as_view(), name="index"),
    path("gestao/", include("processo_seletivo.interface.urls")),
    # O canal do candidato (009). Fora de `gestao/` porque é outro ator, com outra sessão e
    # nenhuma capacidade de gestão — e fora de `api/` porque é página, não contrato.
    path("selecoes/", include("processo_seletivo.portal.urls")),
    path("health", HealthView.as_view(), name="health"),
    path("readiness", ReadinessView.as_view(), name="readiness"),
    path("metrics", MetricsView.as_view(), name="metrics"),
    path("api/v1/admin/", include("processo_seletivo.processos.api.urls")),
    path("api/v1/admin/", include("processo_seletivo.editais.api.urls")),
    path("api/v1/admin/", include("processo_seletivo.publicacoes.api.urls")),
    path("api/v1/admin/", include("processo_seletivo.auditoria.urls")),
    path("api/v1/public/", include("processo_seletivo.publicacoes.api.public_urls")),
]
