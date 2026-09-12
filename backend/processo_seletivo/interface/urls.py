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
    # A supervisão do Processo (022). Pende do Processo, e não do Edital, porque é justamente o
    # nível que não existia: a soma acima do Edital e o tempo acima de todos (FR-001).
    path(
        "processos/<uuid:processo_id>/supervisao",
        views.supervisao,
        name="supervisao",
    ),
    path("editais/<uuid:edital_id>/", views.detalhe, name="detalhe"),
    path("editais/<uuid:edital_id>/compor", views.compor, name="compor"),
    path("editais/<uuid:edital_id>/compor/<slug:etapa>", views.compor_etapa, name="compor-etapa"),
    # Partir de um Edital anterior (023). Fora do POST da etapa porque não é gravação de etapa:
    # é um ato só, sobre um rascunho que precisa estar vazio.
    path("editais/<uuid:edital_id>/reaproveitar", views.reaproveitar, name="reaproveitar"),
    path("editais/<uuid:edital_id>/previa", views.previa, name="previa"),
    path(
        "editais/<uuid:edital_id>/previa/documento",
        views.previa_documento,
        name="previa-documento",
    ),
    path("editais/<uuid:edital_id>/atos/<slug:acao>", views.praticar_ato, name="ato"),
    path("editais/<uuid:edital_id>/retificar", views.retificar, name="retificar"),
    # As cinco operações sobre a coleção de Anexos, e o download do artefato antes da publicação.
    # A coleção não viaja no `replace_draft`, então não passa pelo POST da etapa (020, R-006).
    path("editais/<uuid:edital_id>/anexos", views.anexos_acao, name="anexos"),
    path(
        "editais/<uuid:edital_id>/anexos/<uuid:anexo_id>/arquivo",
        views.anexo_do_rascunho,
        name="anexo-arquivo",
    ),
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
        "fragmentos/perfil/<str:indice>/fato",
        views.fragmento_fato,
        name="fragmento-fato",
    ),
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
    path(
        "fragmentos/retificacao/anexo",
        views.fragmento_retificacao_anexo,
        name="fragmento-retificacao-anexo",
    ),
    # Escopada ao Edital porque os dois campos de escolha da linha — Perfil e lista de
    # concorrência — saem do conteúdo vigente **daquele** Edital, como no fragmento da Etapa.
    path(
        "fragmentos/retificacao/<uuid:edital_id>/linha-do-quadro",
        views.fragmento_retificacao_linha_do_quadro,
        name="fragmento-retificacao-linha-do-quadro",
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
    # O desfecho de quem não foi avaliado (D-1). Página própria, e não um botão a mais na
    # distribuição: o ato tem conteúdo próprio — o motivo constatado —, elimina e não se desfaz.
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/ocorrencia",
        views.registrar_ocorrencia,
        name="registrar-ocorrencia",
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
    # A classificação pende do marco publicado, e não de uma Etapa isolada: o mesmo ato serve
    # tanto ao marco intermediário quanto à combinação final de várias Etapas (015, D-001).
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>",
        views.ordenacao,
        name="ordenacao",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/emitir",
        views.emitir_ordenacao,
        name="emitir-ordenacao",
    ),
    # A leitura de um corte pela identidade dele, sucedido ou vigente (014, UX-024). Pende do
    # Edital, e não do marco: o corte histórico continua legível depois de a Retificação remover o
    # marco da versão vigente, e exigir o marco na rota a tornaria inalcançável justamente aí.
    path(
        "editais/<uuid:edital_id>/cortes/<uuid:corte_id>",
        views.corte_historico,
        name="corte-historico",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/atos/<uuid:ato_id>",
        views.ato_de_ordenacao,
        name="ato-de-ordenacao",
    ),
    # O corte (014). Pende do **marco**, como as da 015 e as do sorteio, e o recorte vem em
    # `?lista=`: um marco de cotas tem três, e cada um tem a sua faixa. O GET calcula e mostra, e
    # não grava nada — abrir a tela não pode mudar quem participa da Etapa seguinte (FR-190).
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/corte",
        views.corte,
        name="corte",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/corte/emitir",
        views.emitir_corte_view,
        name="emitir-corte",
    ),
    # A ocupação (016). Pende do **marco**, como as da 015, do corte e do sorteio, porque é o
    # recorte que ela lista: um marco com cotas tem três recortes, e cada um tem o seu número.
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao",
        views.ocupacao,
        name="ocupacao",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/apurar",
        views.emitir_apuracao_view,
        name="emitir-apuracao",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/faixa-seguinte",
        views.causar_faixa_view,
        name="causar-faixa",
    ),
    # O histórico de um recorte (016, FR-259). O caminho **carrega** o marco, como a leitura, e o
    # recorte vem em `?lista=`: o que se lista é a **série** de um recorte, e é ela que o recorte
    # identifica.
    #
    # **Carregar não é resolver, e é aqui que a distinção importa.** A view não chama
    # `_perfil_do_marco`, que levanta 404 quando o marco não está na versão vigente: uma Retificação
    # que removesse o marco faria desaparecer justamente o histórico que explica os números daquela
    # época. A série é encontrada pelas identidades publicadas que as apurações guardaram. É o
    # mesmo motivo pelo qual `corte-historico` endereça o **corte**, e não o marco.
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/ocupacao/historico",
        views.ocupacao_historico,
        name="ocupacao-historico",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/corte/continuar",
        views.continuar_corte_view,
        name="continuar-corte",
    ),
    # O sorteio (021). A rota pende do **marco**, como as da 015, e é o recorte que ela lista: um
    # marco de sorteio com cotas tem três recortes, e cada um tem o seu estado. O GET não escreve
    # nada e não calcula ordem nenhuma — não há o que calcular antes da semente (D-010).
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio",
        views.sorteio,
        name="sorteio",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio/relacao",
        views.publicar_relacao_do_sorteio,
        name="publicar-relacao-do-sorteio",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio/ocorrencia",
        views.observar_ocorrencia_do_sorteio,
        name="observar-ocorrencia-do-sorteio",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio/realizar",
        views.realizar_sorteio,
        name="realizar-sorteio",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/sorteio/anular",
        views.anular_o_sorteio,
        name="anular-sorteio",
    ),
    # A divulgação (017). A rota pende do **ato**, e não do marco, pelo mesmo motivo que as da 015
    # pendem do marco: é dali que ela é alcançada, e é o ato que a autorização qualifica. O GET
    # compõe a prévia e não grava nada; o POST é o ato.
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/atos/<uuid:ato_id>/publicar",
        views.previa_de_publicacao,
        name="previa-de-publicacao",
    ),
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/atos/<uuid:ato_id>/publicar/confirmar",
        views.publicar_resultado,
        name="publicar-resultado",
    ),
    # Consultar o histórico é de dois — quem publica **ou** quem audita; publicar é de um.
    path(
        "editais/<uuid:edital_id>/marcos/<uuid:marco_id>/publicacoes",
        views.publicacoes_do_marco,
        name="publicacoes-do-marco",
    ),
    path(
        "editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/conclusoes",
        views.conclusoes_preservadas,
        name="conclusoes-preservadas",
    ),
    # Os recursos (018). A lista pende do **Edital** porque é a unidade que o julgador escolhe, e
    # as três rotas da peça pendem do recurso: julgar não é ato de marco nem de Etapa, e endereçá-lo
    # por um deles obrigaria a inventar um caminho para o recurso contra a publicação.
    path("editais/<uuid:edital_id>/recursos", views.recursos_do_edital, name="recursos"),
    path("recursos/<uuid:recurso_id>", views.recurso_recebido, name="recurso"),
    path("recursos/<uuid:recurso_id>/admitir", views.admitir_recurso, name="recurso-admitir"),
    path("recursos/<uuid:recurso_id>/julgar", views.julgar_recurso, name="recurso-julgar"),
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
