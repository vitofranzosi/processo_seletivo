from django.urls import include, path

urlpatterns = [
    path("api/v1/admin/", include("processo_seletivo.processos.api.urls")),
    path("api/v1/admin/", include("processo_seletivo.editais.api.urls")),
    path("api/v1/admin/", include("processo_seletivo.publicacoes.api.urls")),
    path("api/v1/admin/", include("processo_seletivo.auditoria.urls")),
    path("api/v1/public/", include("processo_seletivo.publicacoes.api.public_urls")),
]
