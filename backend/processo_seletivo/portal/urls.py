from django.urls import path

from processo_seletivo.portal import views

app_name = "portal"

urlpatterns = [
    path("", views.vitrine, name="vitrine"),
    path("identificar", views.identificar, name="identificar"),
    path("sair", views.sair, name="sair"),
    # A Inscrição fora do caminho do Edital: ela pertence a quem a abriu, e o endereço não carrega
    # nada sobre a pessoa — nem CPF, nem nome (FR-073).
    path("inscricoes/<uuid:inscricao_id>/", views.inscricao, name="inscricao"),
    path(
        "inscricoes/<uuid:inscricao_id>/documentos/<uuid:requirement_id>",
        views.enviar_documento,
        name="enviar-documento",
    ),
    path(
        "inscricoes/<uuid:inscricao_id>/documentos/<uuid:requirement_id>/remover",
        views.remover_documento_enviado,
        name="remover-documento",
    ),
    path(
        "inscricoes/<uuid:inscricao_id>/documentos/<uuid:requirement_id>/arquivo",
        views.documento_do_candidato,
        name="documento-do-candidato",
    ),
    path("<uuid:edital_id>/", views.selecao, name="selecao"),
    path(
        "<uuid:edital_id>/vagas/<uuid:profile_id>/inscrever",
        views.inscrever,
        name="inscrever",
    ),
]
