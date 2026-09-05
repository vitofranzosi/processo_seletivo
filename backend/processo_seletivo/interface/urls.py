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
    path(
        "editais/<uuid:edital_id>/previa/documento",
        views.previa_documento,
        name="previa-documento",
    ),
    path("editais/<uuid:edital_id>/atos/<slug:acao>", views.praticar_ato, name="ato"),
    path("editais/<uuid:edital_id>/retificar", views.retificar, name="retificar"),
    path("editais/<uuid:edital_id>/auditoria", views.auditoria, name="auditoria"),
    path(
        "editais/<uuid:edital_id>/inscricoes",
        views.inscricoes_recebidas,
        name="inscricoes",
    ),
    path(
        "inscricoes/<uuid:inscricao_id>/",
        views.inscricao_recebida,
        name="inscricao-recebida",
    ),
    path(
        "inscricoes/<uuid:inscricao_id>/documentos/<uuid:requirement_id>",
        views.documento_da_inscricao,
        name="documento-da-inscricao",
    ),
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
    path(
        "editais/<uuid:edital_id>/fragmentos/documento",
        views.fragmento_documento,
        name="fragmento-documento",
    ),
    path("fragmentos/perfil", views.fragmento_perfil, name="fragmento-perfil"),
    # O índice do Perfil vai na rota porque os campos da modalidade são nomeados por ele:
    # `modalidade-<perfil>-<n>-…`. Sem isso a linha nova não saberia a que Perfil pertence.
    path(
        "fragmentos/perfil/<str:indice>/modalidade",
        views.fragmento_modalidade,
        name="fragmento-modalidade",
    ),
    # O marco segue o mesmo esquema da modalidade, e o critério vai um nível mais fundo: os
    # campos dele são `criterio-<perfil>-<marco>-<n>-…`, e sem os dois índices na rota a linha nova
    # não saberia a que marco de que Perfil pertence.
    path(
        "fragmentos/perfil/<str:indice>/marco",
        views.fragmento_marco,
        name="fragmento-marco",
    ),
    path(
        "fragmentos/perfil/<str:indice>/marco/<str:sub>/criterio",
        views.fragmento_criterio,
        name="fragmento-criterio",
    ),
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
    # A organização do trabalho (011). Nenhuma rota usa `etapas/` como segmento: a palavra já
    # significa "passo do compositor" em `editais/<uuid>/compor/<slug:etapa>` (D-009, D-015).
    path(
        "processos/<uuid:processo_id>/comissao",
        views.comissao,
        name="comissao",
    ),
    path(
        "processos/<uuid:processo_id>/alocacoes",
        views.alocacoes,
        name="alocacoes",
    ),
    path(
        "processos/<uuid:processo_id>/auditoria",
        views.auditoria_da_comissao,
        name="auditoria-comissao",
    ),
    # A execução do trabalho (012). O segmento é `distribuicao`, e não `etapas`, pela restrição
    # de vocabulário que a 011 fixou: `etapa` já significa "passo do compositor" em `compor/`.
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>",
        views.distribuicao,
        name="distribuicao",
    ),
    # A consequência do trabalho (013). Pende do mesmo caminho da organização da Etapa, porque é
    # dali que ela é alcançada e porque a autorização é a mesma.
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/consolidar",
        views.consolidar_resultados,
        name="consolidar-resultados",
    ),
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/remover",
        views.remover_atribuicao,
        name="distribuicao-remover",
    ),
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/impedimentos",
        views.impedimentos,
        name="impedimentos",
    ),
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/reabrir",
        views.reabrir_avaliacao,
        name="reabrir-avaliacao",
    ),
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/trilha",
        views.trilha_da_avaliacao,
        name="trilha-da-avaliacao",
    ),
    # A preservação de FR-094 só é preservação se for consultável (FR-091). A porta é a mesma da
    # trilha — presidência ou auditoria —, porque são os dois que respondem a recurso.
    # A consulta do Resultado. Mesma porta das conclusões preservadas — presidência e auditoria —,
    # porque são as duas que respondem a recurso.
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/resultados",
        views.resultados_da_etapa,
        name="resultados-da-etapa",
    ),
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/conclusoes",
        views.conclusoes_preservadas,
        name="conclusoes-preservadas",
    ),
    path("minhas-etapas", views.minhas_etapas, name="minhas-etapas"),
    # A inscrição como instrumento de trabalho, sob a Mesa que a autoriza (012, US3). O caminho
    # pende de `minhas-etapas` porque é dali que ele é alcançado, e porque a autorização é a
    # mesma: a Etapa pela alocação, a inscrição pela Atribuição.
    path(
        "minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>/inscricoes/<uuid:inscricao_id>",
        views.inscricao_da_mesa,
        name="mesa-inscricao",
    ),
    path(
        "minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>/inscricoes/<uuid:inscricao_id>/avaliacao",
        views.avaliacao_gravar,
        name="mesa-avaliacao-gravar",
    ),
    path(
        "minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>/inscricoes/<uuid:inscricao_id>"
        "/avaliacao/concluir",
        views.avaliacao_concluir,
        name="mesa-avaliacao-concluir",
    ),
    path(
        "minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>/inscricoes/<uuid:inscricao_id>"
        "/documentos/<uuid:requirement_id>",
        views.documento_da_mesa,
        name="mesa-documento",
    ),
    path(
        "minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>",
        views.minha_etapa,
        name="minha-etapa",
    ),
]
