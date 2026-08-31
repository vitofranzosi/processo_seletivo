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
    path("<uuid:edital_id>/", views.selecao, name="selecao"),
    path(
        "<uuid:edital_id>/vagas/<uuid:profile_id>/inscrever",
        views.inscrever,
        name="inscrever",
    ),
]
