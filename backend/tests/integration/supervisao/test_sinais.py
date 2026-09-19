"""Os cinco sinais: cada um nasce da sua condição, e some quando ela se desfaz.

A contraprova é metade de cada teste. Um sinal que aparece e nunca some é indistinguível de uma
seção fixa, e é exatamente o que `D-001` recusa.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.interface import supervisao
from tests.conftest import ator_institucional
from tests.fixtures.supervisao import (
    SEGUNDO_SEED,
    etapa_ligada,
    evento_do_periodo,
    evento_simples,
    publicar_no_processo,
    rascunho_com_periodo,
    submeter,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def presidenta():
    """Quem preside — e, para os sinais, também quem alcança as telas donas."""
    return ator_institucional("maria", "recurso:julgar")


def das_especies(sinais, especie):
    return [sinal for sinal in sinais if sinal.especie == especie]


# ---------------------------------------------------------------------------
# `UX-001` — Etapa sem marco no cronograma
# ---------------------------------------------------------------------------


def test_etapa_sem_evento_vinculado_produz_o_sinal(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """`FR-026` e `SC-008`: dito **nesses termos**, e nunca como atraso ou progresso zero.

    A Etapa sem referência a Evento é publicável e legítima — a validação recusa referência a
    Evento inexistente, e **admite ausência de referência**. Transformá-la em impeditivo mudaria o
    que o sistema aceita publicar, o que é decisão normativa e não cabe a um painel.
    """
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_001)

    # A Etapa `Prova didática` do Edital A não declara `scheduleEventId`; a `Análise documental`
    # declara, e não produz sinal.
    assert [sinal.alvo for sinal in achados] == ["Prova didática"]
    unico = achados[0]
    assert unico.edital.id == edital_a.id
    assert "sem marco no cronograma" in unico.mensagem
    for proibido in ("atrasad", "aguardando", "progresso", "0 %", "0%"):
        assert proibido not in unico.mensagem.lower()
    assert unico.medida is None


def test_etapa_com_evento_vinculado_nao_produz_o_sinal(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """A contraprova: o Edital C tem uma Etapa só, e ela aponta o Evento do período."""
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_001)

    assert edital_c.id not in {sinal.edital.id for sinal in achados}


# ---------------------------------------------------------------------------
# `UX-002` — declarado × posição temporal (a tabela-verdade de `T-005`)
# ---------------------------------------------------------------------------

# As três posições, em ids distintos por combinação. Combinação omitida é a que ninguém testa.
COMBINACOES = [
    ("PLANEJADO", "antes", False, 411),
    ("PLANEJADO", "dentro", True, 412),
    ("PLANEJADO", "depois", True, 413),
    ("EM_ANDAMENTO", "antes", True, 414),
    ("EM_ANDAMENTO", "dentro", False, 415),
    ("EM_ANDAMENTO", "depois", True, 416),
    ("CONCLUIDO", "antes", True, 417),
    ("CONCLUIDO", "dentro", True, 418),
    ("CONCLUIDO", "depois", False, 419),
    ("CANCELADO", "depois", False, 420),
]
SEM_TERMINO = 421


def _janela(agora, posicao):
    if posicao == "antes":
        return agora + timedelta(days=10), agora + timedelta(days=11)
    if posicao == "dentro":
        return agora - timedelta(days=1), agora + timedelta(days=1)
    return agora - timedelta(days=11), agora - timedelta(days=10)


@pytest.fixture
def edital_da_tabela_verdade(api_client, manager_headers, processo_a):
    """Um Edital cujo cronograma percorre a tabela-verdade inteira de `T-005`."""
    agora = timezone.now()
    eventos = [
        evento_do_periodo(
            7,
            inicio=agora - timedelta(days=2),
            fim=agora + timedelta(days=2),
            status="EM_ANDAMENTO",
        )
    ]
    for ordem, (declarado, posicao, _, base) in enumerate(COMBINACOES, start=2):
        inicio, fim = _janela(agora, posicao)
        eventos.append(
            evento_simples(
                7,
                base=base,
                descricao=f"{declarado} {posicao}",
                inicio=inicio,
                fim=fim,
                ordem=ordem,
                status=declarado,
            )
        )
    # Sem término declarado: marco instantâneo, forma normal do dado, e por isso nunca divergente.
    eventos.append(
        evento_simples(
            7,
            base=SEM_TERMINO,
            descricao="EM_ANDAMENTO sem término",
            inicio=agora - timedelta(days=3),
            ordem=len(COMBINACOES) + 2,
            status="EM_ANDAMENTO",
        )
    )
    return publicar_no_processo(
        api_client,
        manager_headers,
        processo_a,
        number="07",
        title="Tabela-verdade",
        chave="supervisao-tabela-verdade",
        draft=rascunho_com_periodo(7, eventos=eventos, etapas=[etapa_ligada(7)]),
    )


def test_a_tabela_verdade_inteira_de_ux_002(
    processo_a, edital_a, comissao_de_a, presidenta, edital_da_tabela_verdade
):
    """`FR-027` e `SC-009`: as seis que produzem sinal, as três coerentes e as duas exclusões.

    Nem o `status` nem a posição é corrigido: os dois são apresentados, e a tela não afirma qual
    deles vale.
    """
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_002)

    divergentes = {
        sinal.alvo for sinal in achados if sinal.edital.id == edital_da_tabela_verdade.id
    }
    esperados = {f"{d} {p}" for d, p, produz, _ in COMBINACOES if produz}
    assert divergentes == esperados
    assert "EM_ANDAMENTO sem término" not in divergentes


def test_ux_002_apresenta_as_duas_informacoes_sem_arbitrar(
    processo_a, edital_a, comissao_de_a, presidenta, edital_da_tabela_verdade
):
    """`UX-002`: na forma *declarado X · prazo encerrado em D*."""
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_002)

    encerrado = next(sinal for sinal in achados if sinal.alvo == "PLANEJADO depois")
    assert "declarado planejado" in encerrado.mensagem
    assert "prazo encerrado em" in encerrado.mensagem


# ---------------------------------------------------------------------------
# `UX-003` — cobertura de avaliação insuficiente
# ---------------------------------------------------------------------------


def test_inscricao_sem_avaliador_e_carente_e_permanece_no_denominador(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """`FR-028`, `FR-032` e `FR-033`: numerador e denominador, e a unidade sem ninguém nos dois.

    Retirar do denominador quem não recebeu avaliador nenhum faria a cobertura parecer completa
    justamente onde ela não começou (`SC-006`).
    """
    submeter(edital_c, 4, seed=SEGUNDO_SEED)

    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_003)

    do_c = next(sinal for sinal in achados if sinal.edital.id == edital_c.id)
    assert do_c.medida == supervisao.Medida(numerador=4, denominador=4)
    assert do_c.alvo == "Análise documental"
    assert f"{edital_c.number}/{edital_c.year}" in do_c.mensagem


def test_sem_inscricao_submetida_nao_ha_cobertura_a_cobrar(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """A contraprova: zero carentes sobre zero inscrições não é pendência, é ausência."""
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_003)

    assert achados == []


# ---------------------------------------------------------------------------
# `UX-004` — ato de ordenação vigente obsoleto
# ---------------------------------------------------------------------------


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    """O cenário da `018`: marco emitido e divulgado, com um recurso admitido e sem decisão."""
    from tests.fixtures.recursos_us4 import cenario_julgavel

    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=122, codigo="0221"
    )


def deferir(peca):
    """O deferimento que reabilita quem estava fora — a divergência mais consequente das três."""
    from decimal import Decimal

    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.recursos.models import DecisaoRecurso
    from tests.fixtures.recursos_us4 import julgador

    return julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A prova didática entregue não foi considerada.",
        etapa_id=peca["cenario"]["etapa"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="deferir-na-supervisao",
    )


@pytest.mark.django_db(transaction=True)
def test_o_ato_obsoleto_aparece_sem_que_seja_preciso_abrir_o_marco(peca, presidenta):
    """`FR-029`: a obsolescência só se descobria abrindo o marco, um a um.

    O sinal nasce da **confirmação**, e não do filtro: o filtro barato apenas escolhe quem vale a
    pena confirmar.
    """
    processo = peca["cenario"]["processo"]
    antes = das_especies(supervisao.sinais(processo, presidenta), supervisao.UX_004)
    assert antes == [], "o cenário não pode nascer obsoleto — senão o teste abaixo não prova nada"

    deferir(peca)

    achados = das_especies(supervisao.sinais(processo, presidenta), supervisao.UX_004)
    assert len(achados) == 1
    assert achados[0].alvo == "Classificação final"
    assert achados[0].edital.id == peca["cenario"]["edital"].id


@pytest.mark.django_db(transaction=True)
def test_fato_posterior_que_nao_altera_o_universo_do_marco_nao_produz_sinal(
    peca, presidenta, api_client
):
    """`T-003`: o filtro é conservador, e é a confirmação que decide.

    Uma Retificação alheia ao recorte do marco faz o ato citar uma versão que já não vige — o
    filtro barato o admite como candidato —, e a comparação exata não encontra divergência
    nenhuma. Exibir o candidato como sinal produziria alarme falso, e um painel que erra uma vez
    deixa de ser lido.
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.edital import identificador
    from tests.fixtures.publicacao import retify

    cenario = peca["cenario"]
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": f"/schedule/id={identificador(402, 122)}/description",
                "operation": "REPLACE",
                "newValue": "Período de inscrições (redação ajustada)",
            }
        ],
        suffix="supervisao",
    )

    vigente = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at")
    assert cenario["ato"].versao_id != vigente.id, (
        "sem versão nova o filtro barato não admitiria candidato, e o teste não provaria o descarte"
    )
    assert das_especies(supervisao.sinais(cenario["processo"], presidenta), supervisao.UX_004) == []


# ---------------------------------------------------------------------------
# `UX-005` — recurso sem membro desimpedido
# ---------------------------------------------------------------------------


def impedir(inscricao, subject):
    """O `Impedimento` declarado da `012` — a quinta das cinco origens de `T-004`."""
    from processo_seletivo.avaliacoes.models import Impedimento

    return Impedimento.objects.create(
        identity_subject=subject,
        inscricao=inscricao,
        motivo="Parentesco declarado.",
        criado_em=timezone.now(),
        criado_por="carlos",
    )


@pytest.mark.django_db(transaction=True)
def test_com_a_comissao_inteira_impedida_o_sinal_aparece(peca, presidenta):
    """`FR-030` e `SC-010`: a condição verificável, e não a quantidade pendente isolada.

    João concluiu a Avaliação que fundamentou o Resultado atacado; Maria recebe impedimento
    declarado quanto àquela inscrição. Com os dois membros ativos impedidos, o conjunto de
    desimpedidos é vazio.
    """
    impedir(peca["inscricao"], "maria")

    achados = das_especies(
        supervisao.sinais(peca["cenario"]["processo"], presidenta), supervisao.UX_005
    )

    assert len(achados) == 1
    assert achados[0].edital.id == peca["cenario"]["edital"].id
    assert achados[0].medida is None


@pytest.mark.django_db(transaction=True)
def test_bastando_um_membro_desimpedido_o_sinal_some(peca, presidenta):
    """A contraprova de `SC-010`: Maria não tem impedimento, e a condição não se verifica."""
    achados = das_especies(
        supervisao.sinais(peca["cenario"]["processo"], presidenta), supervisao.UX_005
    )

    assert achados == []


@pytest.mark.django_db(transaction=True)
def test_dobrar_os_recursos_pendentes_nao_dobra_as_consultas(
    peca, presidenta, django_assert_num_queries
):
    """`FR-031` e `D-008`: a pergunta é agregada, e não `recurso × membro`.

    Iterar o guardião individual custaria cinco leituras por par, que é exatamente o custo por
    linha que a `018` já recusou uma vez.

    **O orçamento não é um teto escrito: é a invariância** (`038`, `T021`). Ele é medido com uma
    peça e cobrado com quatro, e o que ele prova é que o custo não acompanha a fila. Ajustar um
    número até passar seria perder a guarda sem removê-la — aqui não há número a ajustar, e é essa
    a razão da forma.

    **O que as espécies da `038` fizeram com ele, medido espécie a espécie**, de 21 para 22
    consultas neste cenário:

    - `UX-063` — **nenhuma**. Lê `completas` e `sem_conclusao` do mesmo `resumo_da_etapa` que o
      `UX-003` já busca, por `sinais_da_etapa`.
    - `UX-064` — **nenhuma**. Sai do mesmo `recursos_do_edital` e do mesmo `impedidos_por_recurso`
      que o `UX-005` já chama, partidos em dois desfechos por `sinais_do_recurso`.
    - `UX-065` — **uma por recorte com ato**, e só ela: `apuracao_vigente`, que a Supervisão não
      lia. O `ato_vigente` é o mesmo que o `UX-004` busca. Este cenário tem um recorte com ato, e
      é dele que vem a única consulta a mais.
    - `UX-066` — **uma por marco**, e **nenhuma aqui**: a `presidenta` deste cenário não tem
      `resultado:publicar`, e o sinal que ela não alcança não chega a ser calculado (`FR-004`). O
      custo dele é medido onde ele existe, por
      `test_a_divulgacao_e_lida_uma_vez_por_marco_e_nao_por_recorte` — e é **por marco**, porque a
      cadeia de publicações é do marco e o recorte é filtro sobre as linhas dela.

    **E nenhuma das quatro escala com a fila**, que é o que este teste cobra: triplicar os recursos
    pendentes não acrescenta Etapa, recorte nem marco.
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    from tests.fixtures.recursos import admitir, interpor

    processo = peca["cenario"]["processo"]
    impedir(peca["inscricao"], "maria")
    with CaptureQueriesContext(connection) as com_um:
        supervisao.sinais(processo, presidenta)
    orcamento = len(com_um.captured_queries)

    # Inscrições distintas: `uq_recurso_por_publicacao` admite uma peça por par inscrição ×
    # publicação, e é a constraint que impede o cenário de existir de outro jeito.
    from tests.fixtures.supervisao import submeter

    outras = submeter(peca["cenario"]["edital"], 3, primeiro=9000, seed=122)
    for numero, inscricao in enumerate(outras):
        admitir(
            interpor(
                inscricao=inscricao,
                versao=peca["recurso"].versao,
                resultado=None,
                publicacao=peca["publicacao"],
                protocolo=f"REC-2026-EXTRA{numero:03d}",
            )
        )

    with django_assert_num_queries(orcamento):
        supervisao.sinais(processo, presidenta)


# ---------------------------------------------------------------------------
# `UX-004` — o ato **sorteado**, e os recortes que não são a ampla concorrência
# ---------------------------------------------------------------------------


@pytest.fixture
def certame_sorteado(gestor, api_client, manager_headers, process_payload):
    """Um marco de sorteio com cotas: ampla concorrência, PPI e PcD sobre o mesmo marco."""
    from tests.fixtures.sorteio import certame_com_cotas

    return certame_com_cotas(gestor, api_client, manager_headers, process_payload)


def ato_sorteado(cenario, relacao_publicada, *, lista_id=None):
    """O ato que um sorteio grava, com a relação que o originou citada no universo."""
    from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.sorteio import MARCO, universo_de_sorteio

    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at")
    return AtoDeOrdenacao.objects.create(
        edital=cenario["edital"],
        perfil_id=cenario["perfil"],
        marco_id=MARCO,
        lista_id=lista_id,
        origem=OrigemDaOrdem.SORTEIO,
        versao=versao,
        universo=universo_de_sorteio(
            cenario["edital"],
            versao=versao,
            perfil_id=cenario["perfil"],
            relacao=relacao_publicada,
        ),
        emitido_por="maria",
        emitido_em=timezone.now(),
    )


def relacao_do_recorte(cenario, *, lista_id=None, anterior=None, inscricoes=()):
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.sorteio import MARCO, relacao

    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at")
    return relacao(
        cenario["edital"],
        versao=versao,
        perfil_id=cenario["perfil"],
        marco_id=MARCO,
        lista_id=lista_id,
        inscricoes=inscricoes,
        anterior=anterior,
        motivo="Habilitação revista." if anterior is not None else "",
    )


@pytest.mark.django_db(transaction=True)
def test_o_ato_sorteado_fica_obsoleto_pela_relacao_e_o_sinal_o_alcanca(
    certame_sorteado, presidenta
):
    """`FR-029` com a `021`: a obsolescência de um sorteio não passa por versão nem por Resultado.

    Um ato sorteado envelhece quando a **relação de habilitados** que o originou ganha sucessora —
    e uma relação nova não altera a versão do Edital nem produz `ResultadoEtapa`. As duas condições
    do filtro barato passavam ao largo disso, e a confirmação exata nunca era chamada: o sinal
    ficava cego, em silêncio, que é o modo de falha que `T-003` diz custar caro.
    """
    inscricoes = certame_sorteado["inscricoes"]
    original = relacao_do_recorte(certame_sorteado, inscricoes=inscricoes)
    ato_sorteado(certame_sorteado, original)

    antes = das_especies(
        supervisao.sinais(certame_sorteado["processo"], presidenta), supervisao.UX_004
    )
    assert antes == [], "sem relação sucessora o ato reflete o fato que o originou"

    relacao_do_recorte(certame_sorteado, anterior=original, inscricoes=inscricoes[:2])

    achados = das_especies(
        supervisao.sinais(certame_sorteado["processo"], presidenta), supervisao.UX_004
    )
    assert len(achados) == 1
    assert achados[0].destino is not None
    # A dona é o sorteio, e não a ordenação: uma ordem sorteada não se refaz recalculando, e a tela
    # da 015 ofereceria justamente o recálculo que só uma semente nova produz.
    assert achados[0].destino.url.endswith("/sorteio")


@pytest.mark.django_db(transaction=True)
def test_o_ato_de_uma_lista_de_reserva_tambem_e_alcancado(certame_sorteado, presidenta):
    """`021`, `D-006`: um marco de cotas tem três atos raiz, e "o ato do marco" não é pergunta.

    Consultar o vigente sem dizer de qual lista devolve o da ampla concorrência, e os de PPI e PcD
    ficam invisíveis — a supervisão diria que está tudo em ordem enquanto duas das três ordens
    publicadas já não correspondem ao universo comprometido.
    """
    from tests.fixtures.sorteio import LISTA_PPI

    cotista = certame_sorteado["cotista_ppi"]
    original = relacao_do_recorte(certame_sorteado, lista_id=LISTA_PPI, inscricoes=[cotista])
    ato_sorteado(certame_sorteado, original, lista_id=LISTA_PPI)
    relacao_do_recorte(
        certame_sorteado, lista_id=LISTA_PPI, anterior=original, inscricoes=[cotista]
    )

    achados = das_especies(
        supervisao.sinais(certame_sorteado["processo"], presidenta), supervisao.UX_004
    )

    assert len(achados) == 1
    # O recorte é nomeado: sem ele os três sinais do mesmo marco sairiam com a mesma frase.
    assert "Pretos, pardos e indígenas" in achados[0].alvo
    assert "Pretos, pardos e indígenas" in achados[0].mensagem


# ---------------------------------------------------------------------------
# `UX-063` — avaliação distribuída e não concluída (038)
#
# **A fronteira com o `UX-003` é a razão de esta seção existir.** Os dois falam da mesma Etapa e
# dizem coisas diferentes: aquele pergunta se há avaliador, este se o trabalho andou. A contraprova
# de `test_a_etapa_sem_distribuicao_e_cobertura_e_nao_trabalho_parado` é o que impede a condição
# nova de ficar frouxa e os dois dispararem pelo mesmo fato.
# ---------------------------------------------------------------------------


@pytest.fixture
def banca(gestor, api_client, manager_headers):
    """Uma Etapa que declara duas avaliações, com dois avaliadores alocados e ninguém distribuído.

    É o ponto de partida das duas perguntas: sem distribuição, a Etapa é **cobertura**; distribuída
    e sem conclusão, ela é **trabalho parado**.
    """
    from tests.fixtures.mesa import inscricoes_de, montar_banca

    cenario = montar_banca(gestor, api_client, manager_headers, seed=140, codigo="0380")
    cenario["inscricoes"] = inscricoes_de(cenario, 3, primeiro=7100)
    return cenario


@pytest.fixture
def presidenta_da_banca():
    """Quem preside a banca — e, por isso, alcança a distribuição da Etapa."""
    return ator_institucional("maria", "recurso:julgar")


@pytest.mark.django_db(transaction=True)
def test_avaliacao_distribuida_e_nao_concluida_produz_o_sinal(banca, gestor, presidenta_da_banca):
    """`FR-560` e `SC-198`: o que parou depois da distribuição passa a ser dito.

    Antes desta feature a cauda era cega: uma Etapa com avaliador para todo mundo e nenhuma
    avaliação concluída não produzia sinal nenhum, porque o `UX-003` já estava satisfeito.
    """
    from tests.fixtures.mesa import distribuir_para

    distribuir_para(banca, gestor, ["joao", "ana"], banca["inscricoes"])

    achados = das_especies(
        supervisao.sinais(banca["processo"], presidenta_da_banca), supervisao.UX_063
    )

    assert len(achados) == 1
    unico = achados[0]
    assert unico.edital.id == banca["edital"].id
    # A Etapa e o Edital são nomeados (`FR-560`): sem os dois, quem lê não sabe onde ir.
    assert unico.alvo
    assert f"{banca['edital'].number}/{banca['edital'].year}" in unico.mensagem
    assert "distribuída e não concluída" in unico.mensagem
    # A medida é **paradas sobre distribuídas** — as três receberam avaliador, nenhuma concluiu.
    assert unico.medida == supervisao.Medida(numerador=3, denominador=3)


@pytest.mark.django_db(transaction=True)
def test_concluidas_as_avaliacoes_o_sinal_some(banca, gestor, presidenta_da_banca):
    """A contraprova: o trabalho andou, e o sinal não sobrevive ao fato que o produziu."""
    from tests.fixtures.mesa import concluir_como, distribuir_para

    distribuir_para(banca, gestor, ["joao", "ana"], banca["inscricoes"])
    for inscricao in banca["inscricoes"]:
        for avaliador in ("joao", "ana"):
            concluir_como(banca, avaliador, inscricao)

    achados = das_especies(
        supervisao.sinais(banca["processo"], presidenta_da_banca), supervisao.UX_063
    )

    assert achados == []


def daquela_etapa(sinais, especie, etapa_id):
    """Os sinais de **uma** Etapa, identificada pelo destino que o sinal oferece.

    A fronteira entre o `UX-003` e o `UX-063` é por Etapa, e o Edital da banca tem duas: varrer o
    Processo inteiro misturaria a Etapa distribuída com a que ninguém tocou, e o teste passaria a
    falar de outra coisa.
    """
    return [
        sinal
        for sinal in das_especies(sinais, especie)
        if sinal.destino is not None and str(etapa_id) in sinal.destino.url
    ]


@pytest.mark.django_db(transaction=True)
def test_a_etapa_sem_distribuicao_e_cobertura_e_nao_trabalho_parado(banca, presidenta_da_banca):
    """**CONTRAPROVA OBRIGATÓRIA** — a fronteira com o `UX-003` (`T009`).

    Etapa sem distribuição nenhuma: quem responde é a **cobertura**, e não o trabalho parado. Se as
    duas dispararem pelo mesmo Edital e pela mesma Etapa, a condição da espécie nova está frouxa —
    é o que aconteceria ao lê-la pela mensagem em vez da condição.
    """
    sinais = supervisao.sinais(banca["processo"], presidenta_da_banca)
    etapa = banca["etapa"]

    assert len(daquela_etapa(sinais, supervisao.UX_003, etapa)) == 1, (
        "sem avaliador atribuído, a cobertura é a pergunta"
    )
    assert daquela_etapa(sinais, supervisao.UX_063, etapa) == [], (
        "nada foi distribuído: não há trabalho parado a apontar"
    )


@pytest.mark.django_db(transaction=True)
def test_distribuida_e_parada_a_etapa_deixa_de_ser_cobertura(banca, gestor, presidenta_da_banca):
    """O outro lado da mesma fronteira: distribuída, a cobertura se satisfaz e a parada aparece.

    **Um fato, um sinal.** As três inscrições passam a ter os dois avaliadores previstos naquela
    Etapa, de modo que `carentes` zera nela; nenhuma foi concluída, de modo que a parada é total.

    **A outra Etapa do Edital não se move**, e ela está no teste de propósito: é a prova de que a
    fronteira é por Etapa, e não por Edital.
    """
    from tests.fixtures.mesa import distribuir_para

    distribuir_para(banca, gestor, ["joao", "ana"], banca["inscricoes"])

    sinais = supervisao.sinais(banca["processo"], presidenta_da_banca)
    etapa = banca["etapa"]

    assert daquela_etapa(sinais, supervisao.UX_003, etapa) == []
    assert len(daquela_etapa(sinais, supervisao.UX_063, etapa)) == 1
    # A Etapa que ninguém distribuiu continua sendo cobertura, e não vira trabalho parado.
    assert len(das_especies(sinais, supervisao.UX_003)) == 1
    assert len(das_especies(sinais, supervisao.UX_063)) == 1


# ---------------------------------------------------------------------------
# `UX-064` — recurso aguardando julgamento com julgador disponível (038)
#
# **É a negação da condição do `UX-005`, e os dois nascem do mesmo cálculo.** A contraprova de
# `test_a_mesma_peca_nunca_dispara_os_dois_sinais` é obrigatória: separados, uma mudança na regra
# de impedimento moveria um e deixaria o outro para trás.
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_recurso_com_julgador_disponivel_produz_o_sinal(peca, presidenta):
    """`FR-561` e `SC-198`: hoje não havia sinal nenhum para a peça que alguém pode julgar.

    O `UX-005` exige a comissão **inteira** impedida, e a peça deste cenário tem Maria livre: antes
    desta feature ela esperava julgamento sem que a Atenção dissesse uma palavra.
    """
    achados = das_especies(
        supervisao.sinais(peca["cenario"]["processo"], presidenta), supervisao.UX_064
    )

    assert len(achados) == 1
    unico = achados[0]
    assert unico.edital.id == peca["cenario"]["edital"].id
    assert "aguardando julgamento" in unico.mensagem
    assert "desimpedido" in unico.mensagem
    # Uma peça pendente, e ela tem julgador.
    assert unico.medida == supervisao.Medida(numerador=1, denominador=1)


@pytest.mark.django_db(transaction=True)
def test_a_mesma_peca_nunca_dispara_os_dois_sinais(peca, presidenta):
    """**CONTRAPROVA OBRIGATÓRIA** — um fato, um sinal (`T010`).

    A **mesma** peça, nos dois estados. Com Maria livre é o `UX-064`; impedindo-a, a comissão
    inteira fica impedida e a peça vira `UX-005`. **Nunca as duas**: se ambas aparecerem, os dois
    cálculos se separaram, que é exatamente o que o contrato proíbe.
    """
    processo = peca["cenario"]["processo"]

    com_julgador = supervisao.sinais(processo, presidenta)
    assert len(das_especies(com_julgador, supervisao.UX_064)) == 1
    assert das_especies(com_julgador, supervisao.UX_005) == []

    impedir(peca["inscricao"], "maria")

    sem_julgador = supervisao.sinais(processo, presidenta)
    assert len(das_especies(sem_julgador, supervisao.UX_005)) == 1
    assert das_especies(sem_julgador, supervisao.UX_064) == []


@pytest.mark.django_db(transaction=True)
def test_sem_peca_pendente_nenhum_dos_dois_aparece(peca, presidenta):
    """A contraprova da ausência: julgada a peça, a fila esvazia e os dois somem juntos."""
    deferir(peca)

    sinais = supervisao.sinais(peca["cenario"]["processo"], presidenta)

    assert das_especies(sinais, supervisao.UX_064) == []
    assert das_especies(sinais, supervisao.UX_005) == []


# ---------------------------------------------------------------------------
# `UX-065` — recorte com ordem vigente e ocupação não apurada (038)
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_ordem_emitida_sem_ocupacao_apurada_produz_o_sinal(peca, presidenta):
    """`FR-563` e `SC-198`: a ordem existe, e ninguém apurou quem ela acomoda.

    O cenário da `018` emite o ato de ordenação e **não** apura ocupação — que é o estado em que
    todo marco fica no instante seguinte à emissão, e que até aqui não produzia sinal nenhum.
    """
    achados = das_especies(
        supervisao.sinais(peca["cenario"]["processo"], presidenta), supervisao.UX_065
    )

    assert len(achados) == 1
    unico = achados[0]
    assert unico.edital.id == peca["cenario"]["edital"].id
    assert "ordem vigente" in unico.mensagem
    assert "nenhuma apuração de ocupação" in unico.mensagem
    # O marco é nomeado, e o destino leva à ocupação dele.
    assert unico.alvo
    assert unico.destino is not None
    assert "ocupacao" in unico.destino.url


@pytest.mark.django_db(transaction=True)
def test_sem_ato_de_ordenacao_o_recorte_nao_sinaliza(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """A contraprova: sem ordem emitida não há ocupação a apurar — o recorte não chegou lá.

    **Não é o mesmo que "apurado"**, e é por isso que a condição exige o ato: sinalizar um marco
    que ninguém ordenou mandaria apurar o que não existe.
    """
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_065)

    assert achados == []


# ---------------------------------------------------------------------------
# `UX-066` — ato de ordenação vigente sem divulgação vigente (038)
#
# **A derivação é a mesma que a tela do ato usa**, extraída de `interface/views.py` para
# `divulgacao.application.selectors`. Reescrevê-la aqui daria duas respostas para a mesma pergunta,
# e a tela mandaria divulgar enquanto o painel diria que está tudo publicado.
# ---------------------------------------------------------------------------


@pytest.fixture
def quem_divulga():
    """A divulgação tem porta própria, e ela não decorre de presidir.

    Na configuração segregada que a `033` nomeou, quem conduz o certame **não** é quem divulga — e
    é por isso que este ator existe separado da `presidenta`.
    """
    return ator_institucional("maria", "recurso:julgar", "resultado:publicar")


@pytest.mark.django_db(transaction=True)
def test_ato_emitido_e_nao_divulgado_produz_o_sinal(certame_sorteado, quem_divulga):
    """`FR-562` e `SC-198`: emitir não é divulgar, e o intervalo entre os dois era invisível.

    O ato existe e o público não o lê. Até aqui isso só se descobria abrindo o marco — ou, pior,
    pela página do candidato, que seguia afirmando o resultado anterior.
    """
    from tests.fixtures.sorteio import LISTA_PPI

    cotista = certame_sorteado["cotista_ppi"]
    relacao = relacao_do_recorte(certame_sorteado, lista_id=LISTA_PPI, inscricoes=[cotista])
    ato_sorteado(certame_sorteado, relacao, lista_id=LISTA_PPI)

    achados = das_especies(
        supervisao.sinais(certame_sorteado["processo"], quem_divulga), supervisao.UX_066
    )

    assert len(achados) == 1
    unico = achados[0]
    assert "não foi divulgado" in unico.mensagem
    # O marco e o recorte são nomeados, e o destino é a publicação **daquele ato**.
    assert "Pretos, pardos e indígenas" in unico.alvo
    assert unico.destino is not None
    assert "publicar" in unico.destino.url


@pytest.mark.django_db(transaction=True)
def test_divulgado_o_ato_o_sinal_some(peca, quem_divulga):
    """A contraprova: o cenário da `018` emite **e divulga**, e nada fica a sinalizar.

    É a prova de que a condição lê a divulgação, e não a mera existência do ato — sem ela, todo
    marco ordenado do sistema produziria sinal para sempre.
    """
    achados = das_especies(
        supervisao.sinais(peca["cenario"]["processo"], quem_divulga), supervisao.UX_066
    )

    assert achados == []


@pytest.mark.django_db(transaction=True)
def test_sem_a_porta_da_divulgacao_o_sinal_nao_e_montado(certame_sorteado, presidenta):
    """`FR-004` e `FR-558`: quem não divulga não recebe o sinal que leva à divulgação.

    A `presidenta` conduz o certame e **não** tem `resultado:publicar`. A supressão é silenciosa:
    anunciar que há um sinal suprimido diria a quem não pode vê-lo que há algo para ver.
    """
    from tests.fixtures.sorteio import LISTA_PPI

    cotista = certame_sorteado["cotista_ppi"]
    relacao = relacao_do_recorte(certame_sorteado, lista_id=LISTA_PPI, inscricoes=[cotista])
    ato_sorteado(certame_sorteado, relacao, lista_id=LISTA_PPI)

    achados = das_especies(
        supervisao.sinais(certame_sorteado["processo"], presidenta), supervisao.UX_066
    )

    assert achados == []


@pytest.mark.django_db(transaction=True)
def test_a_divulgacao_e_lida_uma_vez_por_marco_e_nao_por_recorte(certame_sorteado, quem_divulga):
    """`T021`: o custo do `UX-066` é **por marco**, e acrescentar recorte não o move.

    A cadeia de publicações é do marco; o recorte é filtro sobre as linhas dela. Lê-la dentro do
    laço dos recortes devolveria as mesmas linhas uma vez por lista, e um marco de cotas pagaria
    três vezes pela mesma resposta — o custo por linha que a `018` recusou, reintroduzido pela
    porta dos sinais.

    **A medição é o acréscimo da espécie, e não o total da página**: a diferença entre o mesmo
    Processo lido por quem divulga e por quem não divulga. Comparar totais faria este teste variar
    com o custo das outras nove.
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI

    cotista = certame_sorteado["cotista_ppi"]
    processo = certame_sorteado["processo"]
    sem_a_porta = ator_institucional("maria", "recurso:julgar")

    def acrescimo():
        with CaptureQueriesContext(connection) as sem:
            supervisao.sinais(processo, sem_a_porta)
        with CaptureQueriesContext(connection) as com:
            supervisao.sinais(processo, quem_divulga)
        return len(com.captured_queries) - len(sem.captured_queries)

    ato_sorteado(
        certame_sorteado,
        relacao_do_recorte(certame_sorteado, lista_id=LISTA_PPI, inscricoes=[cotista]),
        lista_id=LISTA_PPI,
    )
    com_um_recorte = acrescimo()

    # Um **segundo recorte do mesmo marco** ganha ato. A cadeia continua sendo uma só.
    ato_sorteado(
        certame_sorteado,
        relacao_do_recorte(certame_sorteado, lista_id=LISTA_PCD, inscricoes=[cotista]),
        lista_id=LISTA_PCD,
    )

    assert com_um_recorte == 1, "a cadeia do marco é uma leitura, e não zero nem duas"
    assert acrescimo() == com_um_recorte, "o segundo recorte releu a cadeia do marco"


# ---------------------------------------------------------------------------
# `FR-564` e `SC-199` — nenhuma das quatro espécies novas nomeia pessoa
#
# **Duas varreduras, porque nenhum cenário dispara as quatro.** O da `018` produz o recurso com
# julgador e o recorte sem ocupação; o do sorteio produz o ato sem divulgação; e a banca, a
# avaliação parada. Um teste só, sobre um cenário só, afirmaria as quatro e conferiria duas.
# ---------------------------------------------------------------------------

NOVAS = ("UX-063", "UX-064", "UX-065", "UX-066")

# "Membro da comissão" **como conjunto** é permitido, e é o que o `UX-064` diz: nomear a condição
# não é nomear quem a resolve. O que não pode aparecer é gente.
PALAVRAS_PROIBIDAS = ("responsável", "responsavel", "produtividade", "desempenho")


def sem_nome_de_pessoa(processo, ator, esperadas):
    """Varre as espécies novas de um Processo e devolve o texto lido, conferindo o que disparou.

    **O conferimento do que disparou é metade do teste.** Sem ele, um cenário que deixasse de
    produzir sinal passaria em silêncio — e uma varredura sobre lista vazia aprova qualquer coisa.
    """
    from processo_seletivo.comissoes.application import selectors as comissao_selectors

    sinais = [sinal for sinal in supervisao.sinais(processo, ator) if sinal.especie in NOVAS]
    assert sorted({sinal.especie for sinal in sinais}) == sorted(esperadas), (
        "o cenário deixou de produzir as espécies que esta varredura existe para varrer"
    )

    lido = " ".join(f"{sinal.alvo} {sinal.mensagem}" for sinal in sinais)
    for membro in comissao_selectors.membros(processo):
        assert membro.identity_subject not in lido, f"{membro.identity_subject} foi nomeado"
    for proibido in PALAVRAS_PROIBIDAS:
        assert proibido not in lido.lower(), f"a mensagem afirma {proibido}"
    return lido


@pytest.mark.django_db(transaction=True)
def test_o_recurso_e_o_recorte_nao_nomeiam_pessoa(peca, quem_divulga):
    """`FR-564` e `SC-199`, sobre o `UX-064` e o `UX-065`.

    **O produto não liga identidade a papel** — os papéis vêm da sessão, e não há registro que
    faça essa ligação. O `UX-005` já registra a razão por escrito, e ela vale igual para as quatro
    espécies da `038`: um painel que prometesse responsável afirmaria o que os dados não sustentam,
    e seria a pior espécie de painel — o que parece saber.
    """
    lido = sem_nome_de_pessoa(
        peca["cenario"]["processo"], quem_divulga, [supervisao.UX_064, supervisao.UX_065]
    )

    assert peca["inscricao"].nome not in lido
    assert peca["inscricao"].identity_subject not in lido


@pytest.mark.django_db(transaction=True)
def test_o_ato_sem_divulgacao_nao_nomeia_pessoa(certame_sorteado, quem_divulga):
    """`FR-564` e `SC-199`, sobre o `UX-066` — e o ato **guarda quem o emitiu**.

    É a espécie onde o vazamento seria mais fácil: `AtoDeOrdenacao.emitido_por` está a um atributo
    de distância da mensagem, e dizer "emitido por Maria e não divulgado" pareceria prestativo. O
    painel diz o que está parado e onde se resolve; quem emitiu é do histórico do ato.
    """
    from tests.fixtures.sorteio import LISTA_PPI

    cotista = certame_sorteado["cotista_ppi"]
    ato_sorteado(
        certame_sorteado,
        relacao_do_recorte(certame_sorteado, lista_id=LISTA_PPI, inscricoes=[cotista]),
        lista_id=LISTA_PPI,
    )

    lido = sem_nome_de_pessoa(
        certame_sorteado["processo"], quem_divulga, [supervisao.UX_065, supervisao.UX_066]
    )

    assert "maria" not in lido.lower(), "o ato guarda `emitido_por`, e ele não vai para a mensagem"


@pytest.mark.django_db(transaction=True)
def test_a_avaliacao_parada_nao_nomeia_pessoa(banca, gestor, presidenta_da_banca):
    """`FR-564` e `SC-199`, sobre o `UX-063` — e é a espécie que mais convidaria a nomear.

    A avaliação parada **tem** avaliador designado, e dizer quem é seria a carga por pessoa que a
    `FR-034` da `022` já proibia. A mensagem nomeia a Etapa e o Edital; quem avalia está na tela
    da distribuição, que é onde o trabalho se resolve.
    """
    from tests.fixtures.mesa import distribuir_para

    distribuir_para(banca, gestor, ["joao", "ana"], banca["inscricoes"])

    lido = sem_nome_de_pessoa(banca["processo"], presidenta_da_banca, [supervisao.UX_063])

    for avaliador in ("joao", "ana"):
        assert avaliador not in lido.lower(), f"{avaliador} foi nomeado na avaliação parada"


# ---------------------------------------------------------------------------
# O Edital que **parou por ato** — encerrado ou cancelado (038, caso-limite da spec)
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("estado", ["ENCERRADO", "CANCELADO"])
def test_edital_parado_por_ato_nao_aponta_trabalho_pendente(peca, quem_divulga, estado):
    """*"Não produz sinal de trabalho pendente — o que parou, parou por ato."*

    **A primeira implementação não olhava o estado do Edital**, e a revisão a pegou: "publicado"
    ali queria dizer apenas *tem conteúdo vigente*, e um Edital encerrado continua tendo. As quatro
    espécies seguiam montadas, **com destino** — mandando retomar avaliação e apurar ocupação de um
    certame que a instituição decidiu encerrar.
    """
    from processo_seletivo.processos.models import Edital

    processo = peca["cenario"]["processo"]
    assert [
        sinal.especie
        for sinal in supervisao.sinais(processo, quem_divulga)
        if sinal.especie in supervisao.TRABALHO_PENDENTE
    ], "sem trabalho pendente antes, o encerramento não provaria nada"

    Edital.objects.filter(pk=peca["cenario"]["edital"].pk).update(
        status=getattr(Edital.Status, estado)
    )

    depois = supervisao.sinais(processo, quem_divulga)

    assert [s for s in depois if s.especie in supervisao.TRABALHO_PENDENTE] == []


@pytest.mark.django_db(transaction=True)
def test_o_edital_parado_nao_silencia_as_especies_anteriores(peca, quem_divulga):
    """**A assimetria é deliberada**: só as quatro da `038` se calam.

    O `UX-001` e o `UX-002` falam do **conteúdo publicado**, que um Edital encerrado continua tendo
    e continua podendo Retificar; o `UX-004` fala de ordem que envelheceu, e ela envelhece depois
    do encerramento como antes. Silenciá-las mudaria o comportamento de seis sinais que ninguém
    pediu para mudar — e é o defeito que a correção mais facilmente introduziria.
    """
    from processo_seletivo.processos.models import Edital

    processo = peca["cenario"]["processo"]
    antigas = {
        sinal.especie
        for sinal in supervisao.sinais(processo, quem_divulga)
        if sinal.especie not in supervisao.TRABALHO_PENDENTE
    }
    assert antigas, "sem espécie anterior disparando, este teste não provaria a preservação"

    Edital.objects.filter(pk=peca["cenario"]["edital"].pk).update(status=Edital.Status.ENCERRADO)

    depois = {
        sinal.especie
        for sinal in supervisao.sinais(processo, quem_divulga)
        if sinal.especie not in supervisao.TRABALHO_PENDENTE
    }

    assert depois == antigas, "o encerramento moveu uma espécie que não é de trabalho pendente"
