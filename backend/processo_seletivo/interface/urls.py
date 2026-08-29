from django.urls import path

from processo_seletivo.interface import views

app_name = "interface"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("identificar", views.identificar, name="identificar"),
    path("sair", views.sair, name="sair"),
    path("editais/<uuid:edital_id>/", views.detalhe, name="detalhe"),
    path("editais/<uuid:edital_id>/compor", views.compor, name="compor"),
    path("editais/<uuid:edital_id>/compor/<slug:etapa>", views.compor_etapa, name="compor-etapa"),
    path("editais/<uuid:edital_id>/atos/<slug:acao>", views.praticar_ato, name="ato"),
    path("fragmentos/perfil", views.fragmento_perfil, name="fragmento-perfil"),
    path("fragmentos/evento", views.fragmento_evento, name="fragmento-evento"),
    path("fragmentos/remover", views.fragmento_remover, name="fragmento-remover"),
]
