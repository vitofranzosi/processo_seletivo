from django.urls import path

from processo_seletivo.interface import views

app_name = "interface"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("identificar", views.identificar, name="identificar"),
    path("sair", views.sair, name="sair"),
    path("processos/criar", views.criar_processo, name="processo-criar"),
    path("processos/<uuid:processo_id>/", views.processo_detalhe, name="processo-detalhe"),
    path(
        "processos/<uuid:processo_id>/atos/<slug:acao>",
        views.praticar_ato_processo,
        name="processo-ato",
    ),
    path("editais/<uuid:edital_id>/", views.detalhe, name="detalhe"),
    path("editais/<uuid:edital_id>/compor", views.compor, name="compor"),
    path("editais/<uuid:edital_id>/compor/<slug:etapa>", views.compor_etapa, name="compor-etapa"),
    path("editais/<uuid:edital_id>/previa", views.previa, name="previa"),
    path("editais/<uuid:edital_id>/atos/<slug:acao>", views.praticar_ato, name="ato"),
    path("editais/<uuid:edital_id>/retificar", views.retificar, name="retificar"),
    path("editais/<uuid:edital_id>/auditoria", views.auditoria, name="auditoria"),
    path(
        "retificacoes/<uuid:retificacao_id>/",
        views.retificacao_detalhe,
        name="retificacao-detalhe",
    ),
    path(
        "retificacoes/<uuid:retificacao_id>/atos/<slug:acao>",
        views.praticar_ato_retificacao,
        name="retificacao-ato",
    ),
    # Escopado ao Edital: a linha de Etapa precisa dos Eventos daquele Cronograma para oferecer
    # o vínculo. Os demais fragmentos não dependem de conteúdo e continuam sem escopo.
    path(
        "editais/<uuid:edital_id>/fragmentos/etapa",
        views.fragmento_etapa,
        name="fragmento-etapa",
    ),
    path("fragmentos/perfil", views.fragmento_perfil, name="fragmento-perfil"),
    path("fragmentos/evento", views.fragmento_evento, name="fragmento-evento"),
    path(
        "fragmentos/retificacao/perfil",
        views.fragmento_retificacao_perfil,
        name="fragmento-retificacao-perfil",
    ),
    path(
        "fragmentos/retificacao/evento",
        views.fragmento_retificacao_evento,
        name="fragmento-retificacao-evento",
    ),
    path("fragmentos/remover", views.fragmento_remover, name="fragmento-remover"),
]
