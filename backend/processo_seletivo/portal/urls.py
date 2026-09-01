from django.urls import path

from processo_seletivo.portal import views

app_name = "portal"

urlpatterns = [
    path("", views.vitrine, name="vitrine"),
    # Acesso sem senha (010). Três telas curtas e nenhuma delas carrega dado pessoal no endereço.
    path("acesso", views.acesso, name="acesso"),
    path("acesso/codigo", views.acesso_codigo, name="acesso-codigo"),
    path("acesso/reconciliar", views.acesso_reconciliar, name="acesso-reconciliar"),
    path("acesso/reconciliar/retomar", views.acesso_retomar, name="acesso-retomar"),
    path("meus-dados", views.meus_dados, name="meus-dados"),
    path("conta", views.conta, name="conta"),
    path("conta/emails", views.conta_adicionar, name="conta-adicionar"),
    path(
        "conta/emails/<uuid:credencial_id>/principal",
        views.conta_principal,
        name="conta-principal",
    ),
    path(
        "conta/emails/<uuid:credencial_id>/remover",
        views.conta_remover,
        name="conta-remover",
    ),
    path("inscricoes/", views.inscricoes, name="inscricoes"),
    path("sair", views.sair, name="sair"),
    # A Inscrição fora do caminho do Edital: ela pertence a quem a abriu, e o endereço não carrega
    # nada sobre a pessoa — nem CPF, nem nome (FR-073).
    path("inscricoes/<uuid:inscricao_id>/", views.inscricao, name="inscricao"),
    path("inscricoes/<uuid:inscricao_id>/revisao", views.revisao, name="revisao"),
    path(
        "inscricoes/<uuid:inscricao_id>/acompanhamento",
        views.acompanhamento,
        name="acompanhamento",
    ),
    path("inscricoes/<uuid:inscricao_id>/comprovante", views.comprovante, name="comprovante"),
    # O mesmo documento, como arquivo. `.pdf` no endereço porque é o que ele devolve, e porque um
    # endereço que termina em `.pdf` é o que uma pessoa reconhece como arquivo para guardar.
    path(
        "inscricoes/<uuid:inscricao_id>/comprovante.pdf",
        views.comprovante_em_pdf,
        name="comprovante-pdf",
    ),
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
